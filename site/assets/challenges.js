/**
 * ChallengeEngine: read the task → predict → operate → submit → explanation → retry.
 * Every check calls the module's real engine or an explicit rule; finishing a video or reaching
 * a page never counts as completion. Viewing the answer is recorded separately and never penalised.
 */
import { h, $, recordChallenge, challengeState, resetChallenge, chime, toast, L } from './core.js';
import { GraphView } from './graphview.js';

const DIFF = { Intro: L('入门', 'Intro'), Practice: L('练习', 'Practice'), Stretch: L('挑战', 'Stretch') };

export function mountChallenges(root, moduleId, list) {
  root.replaceChildren(...list.map(c => card(moduleId, c)));
  document.dispatchEvent(new CustomEvent('challenges-ready', { detail: { moduleId, count: list.length } }));
}

function card(moduleId, c) {
  const fb = h('p.fb', { role: 'status', 'aria-live': 'polite' });
  const hints = h('div.hints');
  const answerBox = h('div');
  const stateTag = h('span.state.tag');
  const ui = c.build();
  let hintShown = 0;
  const el = h('article.challenge', { id: `challenge-${c.id}`, 'data-challenge': c.id },
    h('header', {},
      h('span.cat', `[${c.type}]`), h('h3', c.title),
      h('span.tag', DIFF[c.difficulty] || c.difficulty), stateTag),
    h('p.why', {}, h('b', L('这题检查什么：', 'What this checks: ')), c.why),
    h('p.task', c.task),
    h('div.controls', {}, ui.element),
    h('div.btn-row', {},
      h('button.btn.primary', { type: 'button', onclick: submit }, L('提交', 'Submit')),
      h('button.btn', { type: 'button', onclick: hint }, L('提示', 'Hint')),
      h('button.btn.quiet', { type: 'button', onclick: showAnswer }, L('查看答案与解析', 'Show answer and explanation')),
      h('button.btn.quiet', { type: 'button', onclick: retry }, L('重置重试', 'Reset and retry'))),
    fb, hints, answerBox);
  function paint() {
    const s = challengeState(moduleId, c.id);
    const text = !s ? L('未开始', 'Not started') : s.status === 'solved' ? L('独立完成', 'Solved on your own') : s.status === 'solved-after-answer' ? L('看过答案后完成', 'Solved after seeing the answer') : L(`尝试中 · ${s.attempts} 次`, `In progress · ${s.attempts} ${s.attempts === 1 ? 'try' : 'tries'}`);
    stateTag.textContent = text;
    stateTag.className = 'state tag' + (s?.status === 'solved' ? ' ok' : s?.status === 'solved-after-answer' ? ' warn' : '');
    el.classList.toggle('solved', !!s && s.status !== 'attempted');
  }
  function submit() {
    let answer;
    try { answer = ui.getAnswer(); } catch (e) { fb.className = 'fb no'; fb.textContent = e.message; return; }
    const r = c.check(answer);
    const prev = challengeState(moduleId, c.id) || { attempts: 0 };
    fb.className = 'fb ' + (r.ok ? 'ok' : 'no');
    fb.textContent = (r.ok ? '✓ ' : '✗ ') + r.message;
    chime(r.ok);
    if (r.ok) {
      const viewed = !!prev.answerViewed;
      recordChallenge(moduleId, c.id, { status: viewed ? 'solved-after-answer' : 'solved', attempts: (prev.attempts || 0) + 1 });
      answerBox.replaceChildren(h('div.answer', {}, h('b', L('为什么：', 'Why: ')), ' ', c.explanation));
      if (!viewed && allSolved(moduleId)) toast(L('本模块挑战全部独立完成。', 'You solved every challenge in this module on your own.'));
    } else {
      recordChallenge(moduleId, c.id, { status: prev.status && prev.status !== 'attempted' ? prev.status : 'attempted', attempts: (prev.attempts || 0) + 1 });
    }
    paint();
  }
  function hint() {
    if (hintShown >= c.hints.length) { toast(L('两级提示都已显示；仍卡住时可以查看答案，记录会如实标注。', 'Both hints are showing. If you are still stuck, look at the answer; your record will say so honestly.')); return; }
    hints.append(h('div.hint', {}, h('b', L(`提示 ${hintShown + 1}/${c.hints.length}：`, `Hint ${hintShown + 1}/${c.hints.length}: `)), ' ', c.hints[hintShown]));
    hintShown++;
    const prev = challengeState(moduleId, c.id);
    recordChallenge(moduleId, c.id, { status: prev?.status || 'attempted', attempts: prev?.attempts || 0, hintsUsed: hintShown });
    paint();
  }
  function showAnswer() {
    const prev = challengeState(moduleId, c.id);
    recordChallenge(moduleId, c.id, { status: prev?.status || 'attempted', attempts: prev?.attempts || 0, answerViewed: true });
    answerBox.replaceChildren(h('div.answer', {}, h('b', L('答案：', 'Answer: ')), ' ', c.answer, h('br'), h('b', L('解析：', 'Explanation: ')), ' ', c.explanation,
      h('br'), h('span.small.muted', L('已记录为“看过答案”。之后自己再提交一次正确答案，会标为“看过答案后完成”，不扣分。', 'Recorded as “answer seen”. Submit a correct answer yourself later and it will show as “solved after seeing the answer”; nothing is deducted.'))));
    paint();
  }
  function retry() {
    resetChallenge(moduleId, c.id); hintShown = 0;
    hints.replaceChildren(); answerBox.replaceChildren(); fb.textContent = ''; fb.className = 'fb';
    ui.reset?.(); paint();
  }
  paint();
  return el;
}

function allSolved(moduleId) {
  const cards = document.querySelectorAll('[data-challenge]');
  return [...cards].every(c => ['solved'].includes(challengeState(moduleId, c.dataset.challenge)?.status));
}

/* ---------- reusable controls ---------- */
export function choice(options, { multi = false } = {}) {
  let picked = new Set();
  const buttons = options.map(([value, label]) => h('button', { type: 'button', 'aria-pressed': 'false', onclick: () => {
    if (!multi) picked.clear();
    picked.has(value) ? picked.delete(value) : picked.add(value);
    buttons.forEach((b, i) => b.setAttribute('aria-pressed', picked.has(options[i][0])));
  } }, label));
  return {
    element: h('div.choice-row', { role: multi ? 'group' : 'radiogroup' }, buttons),
    getAnswer() { if (!picked.size) throw new Error(L('先选择一项再提交。', 'Pick an option before submitting.')); return multi ? [...picked] : [...picked][0]; },
    reset() { picked = new Set(); buttons.forEach(b => b.setAttribute('aria-pressed', 'false')); }
  };
}
export function fields(specs) {
  const inputs = specs.map(s => h('input', { type: s.type || 'number', step: s.step || 'any', 'aria-label': s.label, placeholder: s.placeholder || '', style: s.wide ? 'min-width:260px' : null }));
  return {
    element: h('div.btn-row', {}, specs.map((s, i) => h('label', {}, s.label, ' ', inputs[i]))),
    getAnswer() {
      return Object.fromEntries(specs.map((s, i) => {
        const v = inputs[i].value.trim();
        if (v === '') throw new Error(L(`请填写“${s.label}”。`, `Please fill in “${s.label}”.`));
        if ((s.type || 'number') === 'number') { const n = Number(v); if (!Number.isFinite(n)) throw new Error(L(`“${s.label}”须为数字。`, `“${s.label}” must be a number.`)); return [s.key, n]; }
        return [s.key, v];
      }));
    },
    reset() { inputs.forEach(i => { i.value = ''; }); }
  };
}
/** Click nodes (or edges) on a small graph to build a set. */
export function graphPick({ graph, positions, mode = 'nodes', state = () => ({}), width = 560, height = 360, label = L('点击选择', 'Click to select') }) {
  const box = h('div.ch-graph');
  const picked = new Set();
  let gv;
  const draw = () => {
    const st = state();
    if (mode === 'nodes') gv.render({ ...st, focus: [...picked], summary: L(`已选 ${[...picked].join('、') || '无'}`, `Selected: ${[...picked].join(', ') || 'none'}`) });
    else {
      const edgeStyle = {};
      gv.render({ ...st, highlight: [...picked].map(k => k.split('|')), summary: L(`已选边 ${[...picked].map(k => k.replace('|', '–')).join('、') || '无'}`, `Selected edges: ${[...picked].map(k => k.replace('|', '–')).join(', ') || 'none'}`), edgeStyle });
    }
  };
  const toggle = k => { picked.has(k) ? picked.delete(k) : picked.add(k); draw(); list.textContent = L('已选：', 'Selected: ') + ([...picked].map(x => x.replace('|', '–')).join(L('、', ', ')) || L('无', 'none')); };
  gv = new GraphView(box, { graph, positions, width, height, radius: 22, onNodeClick: mode === 'nodes' ? toggle : null, title: label });
  const list = h('p.small', L('已选：无', 'Selected: none'));
  let edgeButtons = null;
  if (mode === 'edges') {
    const edges = gv.edges.map(e => [e.u, e.v].sort().join('|'));
    edgeButtons = h('div.choice-row', {}, edges.map(k => {
      const b = h('button', { type: 'button', 'aria-pressed': 'false', onclick: () => { toggle(k); b.setAttribute('aria-pressed', picked.has(k)); } }, k.replace('|', '–'));
      return b;
    }));
  }
  draw();
  return {
    element: h('div', {}, box, edgeButtons, list),
    getAnswer() { return [...picked]; },
    reset() { picked.clear(); draw(); list.textContent = L('已选：无', 'Selected: none'); edgeButtons?.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', 'false')); },
    redraw: draw
  };
}
/** Reorder items with up/down buttons (keyboard friendly), e.g. ranking pairs by hand. */
export function orderList(items) {
  let order = [...items];
  const ol = h('ol.small', { style: 'padding-left:22px;margin:0' });
  const paint = () => ol.replaceChildren(...order.map((it, i) => h('li', { style: 'margin:4px 0' }, h('span', { style: 'display:inline-block;min-width:90px;font-family:var(--mono)' }, it),
    h('button.btn.small', { type: 'button', 'aria-label': L(`${it} 上移`, `Move ${it} up`), disabled: i === 0, onclick: () => { [order[i - 1], order[i]] = [order[i], order[i - 1]]; paint(); ol.children[i - 1]?.querySelector('button')?.focus(); } }, '↑'), ' ',
    h('button.btn.small', { type: 'button', 'aria-label': L(`${it} 下移`, `Move ${it} down`), disabled: i === order.length - 1, onclick: () => { [order[i + 1], order[i]] = [order[i], order[i + 1]]; paint(); ol.children[i + 1]?.querySelectorAll('button')[1]?.focus(); } }, '↓'))));
  paint();
  return { element: ol, getAnswer: () => [...order], reset() { order = [...items]; paint(); } };
}
export function combine(...parts) {
  return {
    element: h('div', { style: 'display:grid;gap:10px' }, parts.map(p => p.element)),
    getAnswer: () => parts.map(p => p.getAnswer()),
    reset: () => parts.forEach(p => p.reset?.())
  };
}
