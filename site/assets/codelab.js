/**
 * CodeLab: write and run the module's Python exercise in the browser.
 * - Editor: CodeMirror 6 (vendor/codemirror.js), loaded when the section comes near the screen.
 * - Python: Pyodide in a worker (assets/py-worker.js), loaded on the first Run (about 12 MB, cached by the browser).
 * - Checks: the same check.py as the download, run with --json; results per check, never a pass for unfinished code.
 * - The learner's code is kept per module and language in localStorage (falls back to memory).
 * A module can add a visualiser that runs the learner's own functions and animates the result.
 */
import { h, L, LANG, toast, chime } from './core.js';

/** One Python worker; stop() terminates it (the only way to end an infinite loop) and the next run starts a new one. */
export class PyRunner {
  constructor(onstate = () => {}) { this.onstate = onstate; this.worker = null; this.ready = null; this.seq = 0; this.waiting = new Map(); }
  start() {
    if (this.ready) return this.ready;
    this.onstate('loading');
    const w = this.worker = new Worker(new URL('./py-worker.js', import.meta.url), { type: 'module' });
    this.ready = new Promise((resolve, reject) => {
      w.onmessage = ({ data }) => {
        if (data.type === 'ready') { this.onstate('ready', data.version); resolve(); }
        else if (data.type === 'fatal') { this.onstate('failed', data.text); reject(new Error(data.text)); }
        else this.waiting.get(data.id)?.(data);
      };
      w.onerror = e => { this.onstate('failed', e.message || ''); reject(new Error(e.message || 'worker error')); };
    });
    return this.ready;
  }
  async run(files, code, { onOutput, timeout = 20000 } = {}) {
    await this.start();
    const id = ++this.seq;
    return new Promise((resolve, reject) => {
      let out = '';
      const timer = setTimeout(() => { this.stop('timeout'); }, timeout);
      this.waiting.set(id, d => {
        if (d.type === 'out' || d.type === 'err') { out += d.text + '\n'; onOutput?.(d.type, d.text); return; }
        clearTimeout(timer); this.waiting.delete(id);
        if (d.type === 'done') resolve({ value: d.value, out });
        else reject(Object.assign(new Error(d.text), { out, reason: d.reason }));
      });
      this.worker.postMessage({ id, files, code });
    });
  }
  stop(reason = 'stopped') {
    this.worker?.terminate(); this.worker = null; this.ready = null;
    for (const f of this.waiting.values()) f({ type: 'error', text: reason, reason });
    this.waiting.clear(); this.onstate('stopped', reason);
  }
}

const store = {
  key: id => `learning-clustering:code:${id}:${LANG}`,
  mem: {},
  get(id) { try { return localStorage.getItem(this.key(id)); } catch { return this.mem[id] ?? null; } },
  set(id, v) { try { localStorage.setItem(this.key(id), v); } catch { this.mem[id] = v; } },
  clear(id) { try { localStorage.removeItem(this.key(id)); } catch { delete this.mem[id]; } }
};

const CHECK_CODE = `import runpy, sys
sys.argv = ['check.py', 'impl.py', '--json', '--lang', '${LANG}']
try:
    runpy.run_path('check.py', run_name='__main__')
except SystemExit:
    pass`;
const RUN_CODE = `import runpy
runpy.run_path('impl.py', run_name='__main__')`;

export async function mountCodeLab(root, { moduleId, base, data, visualize }) {
  const starter = data.starter[LANG] ?? data.starter.zh, reference = data.reference[LANG] ?? data.reference.zh;
  let mine = store.get(moduleId) ?? starter, showingReference = false, view = null, busy = false;

  const pill = h('span.cl-pill', { role: 'status', 'aria-live': 'polite' }, L('Python 未加载 · 首次运行时下载约 12 MB', 'Python not loaded · about 12 MB on the first run'));
  const btn = (cls, text, onclick, extra = {}) => h(`button.btn.small${cls}`, { type: 'button', onclick, ...extra }, text);
  const runChecksBtn = btn('.primary', L('▶ 运行检查', '▶ Run checks'), () => runChecks(), { title: 'Ctrl/⌘ + Enter' });
  const runFileBtn = btn('', L('运行文件', 'Run file'), () => runFile());
  const stopBtn = btn('', L('■ 停止', '■ Stop'), () => runner.stop('stopped'), { disabled: true });
  const resetBtn = btn('.quiet', L('恢复起始代码', 'Reset to starter'), () => {
    if (!confirm(L('用起始代码替换编辑器里的内容？你的修改会丢失。', 'Replace the editor contents with the starter code? Your changes will be lost.'))) return;
    mine = starter; store.clear(moduleId); setDoc(starter, false); showingReference = false; refBtn.textContent = refLabel(); banner.hidden = true;
  });
  const refLabel = () => showingReference ? L('回到我的代码', 'Back to my code') : L('查看参考实现', 'Show the reference');
  const refBtn = btn('.quiet', refLabel(), () => {
    showingReference = !showingReference;
    setDoc(showingReference ? reference : mine, showingReference);
    refBtn.textContent = refLabel();
    banner.hidden = !showingReference;
  });
  const banner = h('p.cl-banner', { hidden: true }, L('正在查看参考实现（只读）。运行按钮仍然检查你自己的代码。', 'Viewing the reference (read-only). The Run buttons still check your own code.'));
  const editorBox = h('div.cl-editor', {}, h('p.muted.cl-loading', L('正在载入编辑器…', 'Loading the editor…')));
  const checks = h('ol.cl-checks', {}, data.checks.map(c => h('li', {}, h('span.cl-chip', '—'), h('span.cl-name', c[LANG] ?? c.zh))));
  const summary = h('p.cl-summary', L('还没有运行。', 'Not run yet.'));
  const consoleBox = h('pre.cl-console', { tabindex: '0', 'aria-label': L('输出', 'Output') });
  const vizBox = h('div.cl-viz');
  root.replaceChildren(h('div.codelab', {},
    h('div.cl-bar', {}, h('div.btn-row', {}, runChecksBtn, runFileBtn, stopBtn), h('div.btn-row', {}, refBtn, resetBtn, pill)),
    banner,
    h('div.cl-main', {}, h('div.cl-file', {}, h('div.cl-tab', {}, h('code', 'impl.py'), h('span', L('你的代码 · 自动保存在本浏览器', 'your code · saved in this browser'))), editorBox),
      h('div.cl-side', {}, h('h4', L('检查', 'Checks')), summary, checks, h('h4', L('输出', 'Output')), consoleBox))),
    vizBox);

  const runner = new PyRunner((state, info) => {
    const text = { loading: L('正在下载并启动 Python…', 'Downloading and starting Python…'), ready: `Python · Pyodide ${info || ''} · ${L('已就绪', 'ready')}`,
      failed: L(`Python 启动失败：${info}`, `Python failed to start: ${info}`), stopped: info === 'timeout' ? L('已停止：运行超过 20 秒（可能是死循环）', 'Stopped: ran longer than 20 s (an infinite loop?)') : L('已停止', 'Stopped') }[state];
    pill.textContent = text; pill.dataset.state = state;
  });

  const getCode = () => (showingReference ? mine : view ? view.state.doc.toString() : mine);
  const files = () => ({ ...data.files, 'impl.py': getCode() });
  function setBusy(b) { busy = b; runChecksBtn.disabled = runFileBtn.disabled = b; stopBtn.disabled = !b; }
  const print = (type, text) => { const s = h('span', { class: type === 'err' ? 'err' : '' }, text + '\n'); consoleBox.append(s); consoleBox.scrollTop = consoleBox.scrollHeight; };

  async function runChecks() {
    if (busy) return; setBusy(true); consoleBox.replaceChildren(); summary.textContent = L('运行中…', 'Running…');
    try {
      const { out } = await runner.run(files(), CHECK_CODE, { onOutput: (t, s) => { if (!s.startsWith('@@CHECK@@')) print(t, s); } });
      const line = out.split('\n').find(l => l.startsWith('@@CHECK@@'));
      if (!line) throw Object.assign(new Error(L('检查器没有给出结果（代码在导入时出错？看上方输出）', 'The checker gave no result (did your code fail on import? See the output).')), { out });
      const r = JSON.parse(line.slice(9));
      r.results.forEach((x, i) => {
        const li = checks.children[i]; if (!li) return;
        li.dataset.status = x.status; li.querySelector('.cl-chip').textContent = x.status;
        li.querySelector('.cl-note')?.remove(); if (x.note) li.append(h('span.cl-note', x.note));
      });
      const c = r.counts;
      summary.textContent = r.ok ? L(`全部通过：${c.PASS}/${r.results.length}`, `All passed: ${c.PASS}/${r.results.length}`)
        : L(`通过 ${c.PASS}/${r.results.length}`, `Passed ${c.PASS}/${r.results.length}`) + (c.INCOMPLETE ? L(`，${c.INCOMPLETE} 项尚未实现`, `, ${c.INCOMPLETE} not implemented yet`) : '') + (c.FAIL + c.ERROR ? L(`，${c.FAIL + c.ERROR} 项有错`, `, ${c.FAIL + c.ERROR} wrong`) : '');
      summary.dataset.ok = r.ok;
      if (r.ok) { chime(true); toast(L('全部检查通过。在下方用你的代码跑一遍看看。', 'Every check passed. Watch your code run below.')); }
    } catch (e) { fail(e); }
    finally { setBusy(false); }
  }
  async function runFile() {
    if (busy) return; setBusy(true); consoleBox.replaceChildren();
    try { await runner.run(files(), RUN_CODE, { onOutput: print }); print('out', L('—— 运行结束', '—— finished')); }
    catch (e) { fail(e); }
    finally { setBusy(false); }
  }
  function fail(e) {
    if (e.reason === 'stopped' || e.reason === 'timeout') { summary.textContent = pill.textContent; return; }
    const msg = String(e.message || e);
    // Show the last lines of a Python traceback: that is where the learner's mistake is.
    print('err', msg.split('\n').filter(l => !/File "\/lib\/python|_pyodide|pyodide\.ffi/.test(l)).slice(-8).join('\n'));
    summary.textContent = L('运行出错，见输出。', 'The run failed; see the output.');
  }

  // Public API for module visualisers: run Python against the learner's current code.
  const api = {
    run: (code, opts) => runner.run(files(), code, opts),
    get busy() { return busy; },
    setBusy
  };
  if (visualize) { try { visualize(vizBox, api); } catch (e) { console.error(e); } }

  // The editor itself loads when the section approaches the viewport.
  let setDoc = (text) => { mine = showingReference ? mine : text; };
  const loadEditor = async () => {
    const CM = await import(new URL('../vendor/codemirror.js', import.meta.url).href);
    const editable = new CM.Compartment();
    const theme = CM.EditorView.theme({
      '&': { fontSize: '13.5px', backgroundColor: '#fffdf8', height: '100%' },
      '.cm-scroller': { fontFamily: 'var(--mono)', lineHeight: '1.7' },
      '.cm-gutters': { backgroundColor: '#f4f0e7', borderRight: '1px solid #dcd4c6', color: '#8a938c' },
      '.cm-activeLine': { backgroundColor: '#f1ede2' }, '.cm-activeLineGutter': { backgroundColor: '#ebe6da' },
      '&.cm-focused': { outline: 'none' }, '.cm-content': { caretColor: '#0f6b5c' }
    });
    view = new CM.EditorView({
      parent: editorBox,
      state: CM.EditorState.create({
        doc: mine,
        extensions: [CM.basicSetup, CM.python(), CM.indentUnit.of('    '), theme, editable.of(CM.EditorView.editable.of(true)),
          CM.keymap.of([{ key: 'Mod-Enter', run: () => { runChecks(); return true; } }, CM.indentWithTab]),
          CM.EditorView.updateListener.of(u => { if (u.docChanged && !showingReference) { mine = u.state.doc.toString(); store.set(moduleId, mine); } }),
          CM.EditorView.contentAttributes.of({ 'aria-label': L('Python 代码编辑器', 'Python code editor') })]
      })
    });
    editorBox.querySelector('.cl-loading')?.remove();
    editorBox.editorView = view; // for scripted walkthroughs and tests
    setDoc = (text, readOnly) => {
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: text }, effects: editable.reconfigure(CM.EditorView.editable.of(!readOnly)) });
    };
  };
  const io = 'IntersectionObserver' in window ? new IntersectionObserver(es => { if (es.some(e => e.isIntersecting)) { io.disconnect(); loadEditor().catch(fallback); } }, { rootMargin: '600px 0px' }) : null;
  io ? io.observe(root) : loadEditor().catch(fallback);
  // Without the editor bundle, a plain textarea keeps the exercise usable.
  function fallback(e) {
    console.error(e);
    const ta = h('textarea.cl-fallback', { spellcheck: 'false', 'aria-label': L('Python 代码', 'Python code') }); ta.value = mine;
    ta.addEventListener('input', () => { if (!showingReference) { mine = ta.value; store.set(moduleId, mine); } });
    editorBox.replaceChildren(ta);
    setDoc = (text, readOnly) => { ta.value = text; ta.readOnly = !!readOnly; };
    view = { state: { doc: { toString: () => ta.value } } };
  }
}
