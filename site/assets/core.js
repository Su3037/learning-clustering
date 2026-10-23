/**
 * Course shell: element helper, versioned progress store with export/import,
 * toast, preferences (reduced motion, sound), section highlighting.
 * Every page and every module uses this one implementation.
 */
export const SCHEMA_VERSION = 1;
export const STORE_KEY = 'learning-clustering:v1';
export const MODULE_IDS = ['m02-affinity-metrics', 'm03-greedy-pair-merge', 'm04-size-constrained-agglomerative',
  'm05-label-propagation', 'm06-spectral-bisection', 'm07-kernighan-lin', 'm08-fiduccia-mattheyses', 'm09-rajaraman-wong'];

/** h('div.class#id', {attrs}, ...children). Strings become text nodes (never parsed as HTML). */
export function h(tag, attrs = {}, ...kids) {
  if (attrs === null || typeof attrs !== 'object' || attrs instanceof Node || Array.isArray(attrs)) { kids.unshift(attrs); attrs = {}; }
  const [, name = 'div', rest = ''] = tag.match(/^([a-z0-9-]*)(.*)$/i);
  const el = /^(svg|g|line|circle|rect|text|path|polygon|polyline|ellipse|defs|marker|tspan|title)$/.test(name)
    ? document.createElementNS('http://www.w3.org/2000/svg', name) : document.createElement(name);
  for (const m of rest.matchAll(/([.#])([\w-]+)/g)) m[1] === '.' ? el.classList.add(m[2]) : (el.id = m[2]);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === false || v == null) continue;
    if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
    else if (k === 'html') el.innerHTML = v; // only for trusted, course-authored strings
    else if (k === 'class') el.setAttribute('class', [el.getAttribute('class'), v].filter(Boolean).join(' '));
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const k of kids.flat(Infinity)) if (k != null && k !== false) el.append(k instanceof Node ? k : document.createTextNode(String(k)));
  return el;
}
export const $ = (s, root = document) => root.querySelector(s);
export const $$ = (s, root = document) => [...root.querySelectorAll(s)];

let toastTimer;
export function toast(msg, ms = 3200) {
  let t = $('.toast');
  if (!t) { t = h('div.toast', { role: 'status', 'aria-live': 'polite' }); document.body.append(t); }
  t.textContent = msg; t.hidden = false;
  clearTimeout(toastTimer); toastTimer = setTimeout(() => { t.hidden = true; }, ms);
}

/* ---------- storage that survives a blocked localStorage ---------- */
let memory = null, storageOk = true;
function readRaw() {
  try { const s = localStorage.getItem(STORE_KEY); storageOk = true; return s; } catch { storageOk = false; return null; }
}
function writeRaw(s) {
  try { localStorage.setItem(STORE_KEY, s); storageOk = true; return true; } catch { storageOk = false; return false; }
}
export const storageAvailable = () => { readRaw(); return storageOk; };
function empty() { return { schemaVersion: SCHEMA_VERSION, savedAt: null, prefs: {}, modules: {} }; }
export function loadProgress() {
  if (memory) return memory;
  const raw = readRaw();
  let data = empty();
  if (raw) { try { const p = JSON.parse(raw); const v = validateProgress(p); if (v.ok) data = v.data; } catch { /* keep empty */ } }
  memory = data; return data;
}
export function saveProgress(data = loadProgress()) {
  data.savedAt = new Date().toISOString(); memory = data;
  if (!writeRaw(JSON.stringify(data))) notifyStorage();
  document.dispatchEvent(new CustomEvent('progress-changed'));
}
let warned = false;
function notifyStorage() {
  if (warned) return; warned = true;
  toast('浏览器禁止了本地存储：进度只保留在这次打开的页面中。可以用“学习记录”页导出备份。', 6000);
}
/** status: 'attempted' | 'solved' | 'solved-after-answer' */
export function recordChallenge(moduleId, challengeId, patch) {
  const d = loadProgress();
  const m = d.modules[moduleId] ??= { challenges: {} };
  const c = m.challenges[challengeId] ??= { status: 'attempted', attempts: 0, hintsUsed: 0, answerViewed: false };
  Object.assign(c, patch, { updatedAt: new Date().toISOString() });
  saveProgress(d);
  return c;
}
export function challengeState(moduleId, challengeId) { return loadProgress().modules[moduleId]?.challenges?.[challengeId] || null; }
export function resetChallenge(moduleId, challengeId) {
  const d = loadProgress(); if (d.modules[moduleId]) delete d.modules[moduleId].challenges[challengeId]; saveProgress(d);
}

/** Validate an imported or stored progress object: size, version, known ids, known fields only. */
export function validateProgress(obj, known = null) {
  const errors = [];
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return { ok: false, errors: ['不是 JSON 对象'] };
  if (obj.schemaVersion !== SCHEMA_VERSION) errors.push(`schemaVersion 应为 ${SCHEMA_VERSION}`);
  const out = empty();
  if (obj.prefs && typeof obj.prefs === 'object') {
    if (typeof obj.prefs.reduceMotion === 'boolean') out.prefs.reduceMotion = obj.prefs.reduceMotion;
    if (typeof obj.prefs.sound === 'boolean') out.prefs.sound = obj.prefs.sound;
  }
  for (const [mid, m] of Object.entries(obj.modules || {})) {
    if (!MODULE_IDS.includes(mid)) { errors.push(`未知模块 ${mid}`); continue; }
    const ch = {};
    for (const [cid, c] of Object.entries(m?.challenges || {})) {
      if (known && !known[mid]?.includes(cid)) { errors.push(`${mid} 中没有挑战 ${cid}`); continue; }
      if (!/^[a-z0-9-]{1,40}$/.test(cid)) { errors.push(`挑战 id ${cid} 不合法`); continue; }
      if (!['attempted', 'solved', 'solved-after-answer'].includes(c?.status)) { errors.push(`${cid} 状态不合法`); continue; }
      ch[cid] = { status: c.status, attempts: Math.max(0, Math.min(9999, c.attempts | 0)), hintsUsed: Math.max(0, Math.min(2, c.hintsUsed | 0)),
        answerViewed: !!c.answerViewed, updatedAt: typeof c.updatedAt === 'string' ? c.updatedAt.slice(0, 40) : null };
    }
    out.modules[mid] = { challenges: ch };
  }
  return { ok: errors.length === 0, errors, data: out };
}
export function exportProgress() {
  const blob = new Blob([JSON.stringify(loadProgress(), null, 2)], { type: 'application/json' });
  download(blob, `learning-clustering-progress-${new Date().toISOString().slice(0, 10)}.json`);
}
export function download(blob, name) {
  const a = h('a', { href: URL.createObjectURL(blob), download: name });
  document.body.append(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
}
export async function importProgress(file, known) {
  if (file.size > 200 * 1024) return { ok: false, errors: ['文件超过 200 KB，不像学习记录'] };
  let obj;
  try { obj = JSON.parse(await file.text()); } catch { return { ok: false, errors: ['不是有效的 JSON'] }; }
  const v = validateProgress(obj, known);
  if (!v.ok) return v;
  memory = v.data; saveProgress(v.data);
  return v;
}

/* ---------- preferences ---------- */
export function prefs() { return loadProgress().prefs; }
export function setPref(k, v) { const d = loadProgress(); d.prefs[k] = v; saveProgress(d); applyPrefs(); }
export function reducedMotion() {
  const p = prefs().reduceMotion;
  if (typeof p === 'boolean') return p;
  return typeof matchMedia === 'function' && matchMedia('(prefers-reduced-motion: reduce)').matches;
}
export function applyPrefs() { document.documentElement.classList.toggle('reduce-motion', reducedMotion()); }
let audio;
export function chime(ok = true) {
  if (!prefs().sound) return;
  try {
    audio ??= new (window.AudioContext || window.webkitAudioContext)();
    const o = audio.createOscillator(), g = audio.createGain(), t = audio.currentTime;
    o.frequency.setValueAtTime(ok ? 660 : 220, t); if (ok) o.frequency.setValueAtTime(880, t + 0.09);
    g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(0.08, t + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, t + 0.28);
    o.connect(g).connect(audio.destination); o.start(t); o.stop(t + 0.3);
  } catch { /* sound is optional feedback only */ }
}

/* ---------- page wiring ---------- */
export function initShell() {
  applyPrefs();
  const toggles = $$('[data-pref]');
  for (const b of toggles) {
    const k = b.dataset.pref;
    const sync = () => { const on = k === 'reduceMotion' ? reducedMotion() : !!prefs()[k]; b.setAttribute('aria-pressed', on); b.textContent = (k === 'sound' ? '声音：' : '减少动态：') + (on ? '开' : '关'); };
    b.addEventListener('click', () => { setPref(k, !(b.getAttribute('aria-pressed') === 'true')); sync(); });
    sync();
  }
  // Highlight the in-page section that is on screen.
  const links = $$('.module-nav a[href^="#"]');
  if (links.length && 'IntersectionObserver' in window) {
    const map = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
    const io = new IntersectionObserver(es => {
      for (const e of es) if (e.isIntersecting) { links.forEach(a => a.classList.remove('active')); map.get(e.target.id)?.classList.add('active'); }
    }, { rootMargin: '-45% 0px -50% 0px' });
    map.forEach((_, id) => { const s = document.getElementById(id); if (s) io.observe(s); });
  }
  if (!storageAvailable()) notifyStorage();
}

/** Fetch JSON relative to a module URL; returns null and shows a visible message on failure. */
export async function fetchJSON(url, where) {
  try {
    const r = await fetch(url);
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.json();
  } catch (e) {
    if (where) where.replaceChildren(h('p.lab-error', `资源加载失败（${e.message}）：${decodeURI(String(url).split('/').slice(-2).join('/'))}。可刷新重试；若通过 file:// 直接打开，请改用本地 HTTP 服务（见 README）。`));
    return null;
  }
}
export const fmt = x => Number.isInteger(x) ? String(x) : (Math.abs(x) < 1e-9 ? '0' : (+x.toFixed(4)).toString());
