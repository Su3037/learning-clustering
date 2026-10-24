// Module 06 lab: Laplacian, live Jacobi eigen-solve, Fiedler number line and sweep. engines/spectral.js only.
import { h, fmt } from '../../assets/core.js';
import { L } from '../../assets/i18n.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as S from '../../engines/spectral.js';
import { G01, requireGraph } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const PRESETS = {
  g01: { name: L('课程公共图 G01', 'Course graph G01'), graph: G01, positions: G01.positions },
  disc: { name: L('两个分量（断开）', 'Two components (disconnected)'), graph: S.DISCONNECTED, positions: S.DISCONNECTED.positions },
  ring: { name: L('四节点环（λ2 简并）', 'Four-node ring (λ2 repeated)'), graph: S.DEGENERATE, positions: S.DEGENERATE.positions }
};
const BAL = { '40': { minFraction: 0.4, maxFraction: 0.6 }, '30': { minFraction: 0.3, maxFraction: 0.7 }, '0': { minFraction: 0, maxFraction: 1 } };

/** The Fiedler number line: nodes at their values (ascending), the gold dashed line at cut point k. */
function numberLine(r, k) {
  const W = 760, H = 124, pad = 50, vals = r.orderValues, lo = Math.min(...vals), hi = Math.max(...vals), sx = v => pad + (W - 2 * pad) * (v - lo) / ((hi - lo) || 1);
  const svg = h('svg', { viewBox: `0 0 ${W} ${H}`, class: 'gv', role: 'img', 'aria-label': L(`Fiedler 数轴：${r.order.map((n, i) => `${n} ${fmt(vals[i])}`).join('，')}`, `Fiedler number line: ${r.order.map((n, i) => `${n} ${fmt(vals[i])}`).join(', ')}`) },
    h('line', { x1: pad - 20, y1: 60, x2: W - pad + 20, y2: 60, stroke: '#5d7c80', 'stroke-width': 2 }));
  let lastX = -1e9, up = false;
  r.order.forEach((n, i) => {
    const x = sx(vals[i]);
    up = x - lastX < 34 ? !up : false; lastX = x;
    const cy = up ? 26 : 60;
    if (up) svg.append(h('line', { x1: x, y1: 41, x2: x, y2: 60, stroke: '#5d7c80', 'stroke-width': 1.5 }));
    svg.append(h('circle', { cx: x, cy, r: 15, fill: k && i < k ? '#77cdbb' : '#8fb1e6', stroke: '#0d262c', 'stroke-width': 2 }),
      h('text', { x, y: cy + 6, 'text-anchor': 'middle', style: 'font-size:14px;font-weight:700;fill:#0b1b1f' }, n),
      h('text', { x, y: i % 2 ? 112 : 96, 'text-anchor': 'middle', class: 'w', style: 'font-size:12px' }, fmt(+vals[i].toFixed(3))));
  });
  if (k) { const x = (sx(vals[k - 1]) + sx(vals[k])) / 2; svg.append(h('line', { x1: x, y1: 20, x2: x, y2: 85, stroke: '#d8bb78', 'stroke-width': 3, 'stroke-dasharray': '6 4' })); }
  svg.append(h('text', { x: W - pad + 20, y: 18, class: 'side-label', 'text-anchor': 'end' }, L('Fiedler 值（升序）', 'Fiedler value (ascending)')));
  return svg;
}

async function lab(root, { pseudo }) {
  let presetId = 'g01', bal = '40', source = 'live', weights = {}, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side'), line = h('div', { style: 'margin-top:8px' });
  const metricBox = h('div.metrics'), statusBox = h('div.status'), matBox = h('div.decision'), diagBox = h('div.decision'), playerBox = h('div');
  const traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, line, h('div.legend', {},
    h('span', {}, L('节点颜色 = 当前切点下的左 / 右组', 'Node colour = left / right side at the current cut point')), h('span', {}, h('i', { style: 'border-color:#db7b72;border-top-style:dashed' }), L('被切断的边', 'Cut wires')),
    h('span', {}, h('i', { style: 'border-color:#d8bb78' }), L('数轴上的金线：当前切点', 'Gold line on the number line: the current cut point'))), h('div.lab-side', { style: 'border:1px solid var(--c-line);border-radius:10px;margin-top:12px' }, h('h4', { style: 'margin-top:0' }, L('拉普拉斯矩阵 L = D − A', 'The Laplacian L = D − A')), matBox)), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', L('数值诊断', 'Numerical diagnostics')), diagBox, playerBox);
  let gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: L('谱二分实验图', 'Spectral bisection lab graph'), width: 760, height: 380 });
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: L('步骤', 'Step'), get: e => ({ laplacian: L('构造 L', 'build L'), eigen: L('求特征值与向量', 'eigenvalues and vectors'), 'sweep-cut': L(`切点 k=${e.metrics.k}`, `cut point k=${e.metrics.k}`), choose: L('选择', 'choose') })[e.kind] },
    { label: L('左组', 'Left'), get: e => e.kind === 'sweep-cut' ? e.after.left.join('') : '' }, { label: 'cut', get: e => e.metrics?.cut ?? '' }, { label: L('窗口内', 'In window'), get: e => e.kind === 'sweep-cut' ? (e.decision === 'legal' ? L('是', 'yes') : L('否', 'no')) : '' }], onPick: i => player.go(i) });

  const graph = () => { const g = requireGraph(PRESETS[presetId].graph); return { nodes: g.nodes, edges: g.edges.map(e => ({ ...e, w: weights[`${e.u}|${e.v}`] ?? e.w })) }; };
  function buildToolbar() {
    const edgeSel = h('select', { 'aria-label': L('选择要修改的边', 'Choose an edge to change') }, graph().edges.map(e => h('option', { value: `${e.u}|${e.v}` }, `${e.u}–${e.v}`)));
    const wIn = h('input', { type: 'number', min: 0.5, max: 50, step: 0.5, 'aria-label': L('新权重', 'New weight') });
    const sync = () => { wIn.value = graph().edges.find(x => `${x.u}|${x.v}` === edgeSel.value).w; };
    edgeSel.addEventListener('change', sync); sync();
    wIn.addEventListener('change', () => { const w = Number(wIn.value); if (!(w > 0 && w <= 50)) { err.textContent = L('权重须为 0–50 之间的正数。', 'A weight must be a positive number up to 50.'); return; } err.textContent = ''; weights[edgeSel.value] = w; if (source === 'stored') source = 'live'; buildToolbar(); recompute(); });
    toolbar.replaceChildren(
      select(L('例子', 'Example'), Object.entries(PRESETS).map(([k, p]) => [k, p.name]), presetId, v => { presetId = v; weights = {}; source = 'live'; buildToolbar(); recompute(true); }),
      select(L('平衡窗口', 'Balance window'), [['40', L('每组 40%–60%', '40%–60% per side')], ['30', L('每组 30%–70%', '30%–70% per side')], ['0', L('不限（只要非空）', 'any (non-empty)')]], bal, v => { bal = v; recompute(); }),
      select(L('特征向量来源', 'Eigenvector source'), presetId === 'g01' && !Object.keys(weights).length ? [['live', L('浏览器实时求解（Jacobi）', 'solved live in the browser (Jacobi)')], ['stored', L('原作页面存储的三位小数', 'the original page’s stored 3-decimal values')]] : [['live', L('浏览器实时求解（Jacobi）', 'solved live in the browser (Jacobi)')]], source, v => { source = v; recompute(); }),
      h('label', {}, L('改一条边', 'Change an edge'), edgeSel), h('label', {}, L('新权重', 'New weight'), wIn),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m06-spectral-bisection', { preset: presetId, options: { balance: BAL[bal], source }, input: graph(), result: run.result }) }, L('导出运行记录', 'Export the run')));
  }
  function recompute(newGraph = false) {
    const g = graph();
    const opts = { balance: BAL[bal] };
    if (source === 'stored') Object.assign(opts, { vector: g.nodes.map(n => S.STORED_VECTOR[n.id]), vectorSource: L('原作存储值', 'stored by the original') });
    run = S.run(g, opts);
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join(L('；', '; ')); return; }
    err.textContent = '';
    if (newGraph) gv = new GraphView(stage, { graph: g, positions: PRESETS[presetId].positions, title: L('谱二分实验图', 'Spectral bisection lab graph'), width: 760, height: 380 });
    else gv.setGraph(g, PRESETS[presetId].positions, 760, 380);
    const r = run.result, Lm = r.L;
    matBox.replaceChildren(h('table', {}, h('thead', {}, h('tr', {}, h('th', ''), r.ids.map(id => h('th', id)), h('th', L('行和', 'Row sum')))),
      h('tbody', {}, Lm.map((row, i) => h('tr', {}, h('th', r.ids[i]), row.map(x => h('td', { style: x > 0 ? 'color:var(--c-gold)' : '' }, fmt(x))), h('td', fmt(row.reduce((s, x) => s + x, 0))))))));
    const d = r.diagnostics;
    diagBox.replaceChildren(h('table', {}, h('tbody', {},
      h('tr', {}, h('th', L('求解', 'Solver')), h('td', `${d.solver}${source === 'live' ? L(`，${d.sweeps} 次扫掠`, `, ${d.sweeps} sweeps`) : ''}`)),
      h('tr', {}, h('th', L('特征值', 'Eigenvalues')), h('td', r.eigenvalues.map(x => fmt(x)).join(L('，', ', ')))),
      h('tr', {}, h('th', L('残差 ‖Lx−λ₂x‖/‖x‖', 'Residual ‖Lx−λ₂x‖/‖x‖')), h('td', d.residual.toExponential(2))),
      h('tr', {}, h('th', L('与全 1 向量的夹角余弦', 'Cosine with the all-ones vector')), h('td', d.orthogonalityToOnes.toExponential(1))),
      h('tr', {}, h('th', L('连通', 'Connected')), h('td', d.connected ? L('是', 'yes') : L(`否（${d.components.length} 个分量）`, `no (${d.components.length} components)`))),
      h('tr', {}, h('th', 'λ3 − λ2'), h('td', fmt(d.gap))))), ...d.warnings.map(w => h('p.lab-note', { style: 'color:var(--c-gold)' }, '⚠ ' + w)),
      source === 'stored' ? h('p.lab-note', L(`原作存储的是三位小数，残差约 ${d.residual.toFixed(4)}：这是舍入，不是求解失败；改图时它不会重算。`, `The original stored three decimals, so the residual is about ${d.residual.toFixed(4)}: that is rounding, not a failed solve; it is not recomputed when you change the graph.`)) : '');
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const r = run.result;
    const k = e.kind === 'sweep-cut' ? e.metrics.k : e.kind === 'choose' ? r.bestK : 0;
    const left = k ? r.order.slice(0, k) : null;
    gv.render({ groups: left ? Object.fromEntries(r.ids.map(id => [id, left.includes(id) ? 'L' : 'R'])) : undefined, groupOrder: ['L', 'R'], cut: !!left,
      tags: Object.fromEntries(r.ids.map((id, j) => [id, fmt(+r.fiedler[j].toFixed(3))])), summary: k ? L(`切点 k=${k}`, `cut point k=${k}`) : L('尚未切分', 'not cut yet') });
    line.replaceChildren(numberLine(r, k));
    const s = k ? r.sweep[k - 1] : null;
    metrics(metricBox, [['λ₂', fmt(+r.eigenvalues[1].toFixed(4))], [L('切点 k', 'Cut point k'), k || '—'], ['cut', s ? s.cut : '—']]);
    if (e.kind === 'laplacian') status(statusBox, '', L('构造 L：每条边贡献两个对角 +w、两个非对角 −w。每行和为 0。', 'Build L: each edge adds +w to two diagonal entries and −w to two off-diagonal ones. Every row sums to 0.'));
    else if (e.kind === 'eigen') status(statusBox, r.diagnostics.warnings.length ? 'limit' : '', L(`求出特征值；Fiedler 排序：${r.order.join(', ')}。`, `Eigenvalues found; Fiedler order: ${r.order.join(', ')}.`));
    else if (e.kind === 'sweep-cut') status(statusBox, s.legal ? '' : 'blocked', L(`k = ${k}：${s.left.join('')} | ${s.right.join('')}，cut ${s.cut}，${s.legal ? '在窗口内' : `不在窗口内（每组需 ${r.window.lo}–${r.window.hi} 个）`}。`, `k = ${k}: ${s.left.join('')} | ${s.right.join('')}, cut ${s.cut}, ${s.legal ? 'inside the window' : `outside the window (each side needs ${r.window.lo}–${r.window.hi})`}.`));
    else status(statusBox, r.partition ? '' : 'invalid', r.partition ? L(`选择窗口内 cut 最小的 k = ${r.bestK}：${r.partition.map(p => p.join('')).join(' | ')}，cut ${r.cut}。`, `Choose the least cut inside the window, k = ${r.bestK}: ${r.partition.map(p => p.join('')).join(' | ')}, cut ${r.cut}.`) : L('窗口内没有合法切点。', 'No legal cut point inside the window.'));
    pseudo.spectral?.show(e.kind === 'laplacian' ? [1] : e.kind === 'eigen' ? [2, 3, 4, 5] : e.kind === 'sweep-cut' ? [6] : [7], '');
  }
  buildToolbar(); recompute(true);
}

/** A new graph for the code lab: two four-cell blocks joined by two weak wires. */
const TWIN = {
  nodes: ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W'],
  edges: [['P', 'Q', 4], ['P', 'R', 3], ['Q', 'R', 5], ['Q', 'S', 2], ['R', 'S', 4], ['T', 'U', 5], ['T', 'V', 3], ['U', 'V', 4], ['U', 'W', 2], ['V', 'W', 4], ['S', 'T', 1], ['R', 'V', 1]],
  positions: { P: [70, 90], Q: [190, 40], R: [190, 170], S: [310, 110], T: [450, 110], U: [570, 40], V: [570, 170], W: [690, 90] }
};

/** Code lab: run the learner's laplacian() / sweep() / count_bipartitions() inside spectral_bisection() and compare with the engine. */
function visualize(root, api) {
  const EX = {
    g01: { name: L('G01', 'G01'), graph: G01, positions: G01.positions },
    twin: { name: L('两个四节点块（新图）', 'Two four-node blocks (new graph)'), graph: TWIN, positions: TWIN.positions },
    disc: { name: L('两个分量（断开）', 'Two components (disconnected)'), graph: S.DISCONNECTED, positions: S.DISCONNECTED.positions }
  };
  let ex = 'g01', bal = '40';
  const stage = h('div.lab-stage'), line = h('div', { style: 'margin-top:8px' }), side = h('div.lab-side'), statusBox = h('div.status'), sweepBox = h('div.decision'), match = h('p.match');
  const go = h('button.btn.primary', { type: 'button', onclick: runMine }, L('▶ 用我的代码运行', '▶ Run my code'));
  const toolbar = h('div.lab-toolbar', {}, select(L('例子', 'Example'), Object.entries(EX).map(([k, v]) => [k, v.name]), ex, v => { ex = v; }),
    select(L('平衡窗口', 'Balance window'), [['40', L('每组 40%–60%', '40%–60% per side')], ['0', L('不限（只要非空）', 'any (non-empty)')]], bal, v => { bal = v; }), go);
  side.append(statusBox, h('h4', L('你的扫描 · 引擎的扫描', 'Your sweep · the engine’s sweep')), sweepBox);
  root.append(h('h3', L('用你的代码跑一遍', 'Watch your own code run')),
    h('p.muted', L('这里调用你写的 laplacian()、sweep() 和 count_bipartitions()（特征向量用已提供的 Jacobi）。左边按你的结果画出切分，右边逐个切点对照课程引擎。',
      'This calls the laplacian(), sweep() and count_bipartitions() you wrote (eigenvectors come from the provided Jacobi). The left draws the cut from your result; the right compares every cut point with the course engine.')),
    toolbar, h('div.lab', {}, h('div', {}, stage, line), side), match);
  stage.append(h('p.muted', { style: 'padding:40px 10px;text-align:center' }, L('写好函数后，按“用我的代码运行”。', 'Once your functions are written, press “Run my code”.')));

  async function runMine() {
    if (api.busy) return;
    const cur = EX[ex], g = requireGraph(cur.graph), ids = g.nodes.map(n => n.id), bounds = bal === '40' ? [0.4, 0.6] : [0, 1];
    const code = `import json, importlib.util
spec = importlib.util.spec_from_file_location('impl_v', 'impl.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
nodes = ${JSON.stringify(ids)}
edges = [tuple(e) for e in ${JSON.stringify(g.edges.map(e => [e.u, e.v, e.w]))}]
r = m.spectral_bisection(nodes, edges, (${bounds[0]}, ${bounds[1]}))
json.dumps({"L": m.laplacian(nodes, edges), "eig": r["eigenvalues"], "order": r["order"], "vector": r["vector"],
            "cands": [{"k": c["k"], "left": list(c["left"]), "cut": c["cut"], "legal": c["legal"]} for c in r["candidates"]],
            "partition": [list(p) for p in r["partition"]] if r["partition"] else None, "cut": r["cut"], "count": m.count_bipartitions(len(nodes))})`;
    api.setBusy(true); go.disabled = true; match.className = 'match'; match.textContent = L('运行中…', 'Running…');
    try {
      const mine = JSON.parse((await api.run(code)).value);
      const ref = S.run(g, { balance: bal === '40' ? { minFraction: 0.4, maxFraction: 0.6 } : { minFraction: 0, maxFraction: 1 } }).result;
      const n = ids.length, win = ref.window;
      const lOk = mine.L.every((row, i) => row.every((x, j) => Math.abs(x - ref.L[i][j]) < 1e-9));
      // the expected sweep along YOUR order (the sign of the eigenvector may differ from the engine's; the cuts must not)
      const want = [...Array(n - 1).keys()].map(i => { const k = i + 1, left = new Set(mine.order.slice(0, k));
        return { k, cut: g.edges.reduce((s, e) => s + (left.has(e.u) !== left.has(e.v) ? e.w : 0), 0), legal: k >= win.lo && k <= win.hi && n - k >= win.lo && n - k <= win.hi }; });
      const sweepOk = mine.cands.length === want.length && mine.cands.every((c, i) => Math.abs(c.cut - want[i].cut) < 1e-9 && c.legal === want[i].legal && c.k === want[i].k);
      const countOk = mine.count === S.unlabelledBipartitions(n);
      const cutOk = (mine.cut ?? null) === (ref.cut ?? null);
      const ok = lOk && sweepOk && countOk && cutOk, chosenK = mine.partition ? mine.partition[0].length : '—';
      match.className = 'match ' + (ok ? 'ok' : 'no');
      match.textContent = ok
        ? L(`✓ L、扫描、选择与非空二分数（${mine.count}）都和课程引擎一致：选 k = ${chosenK}，cut ${mine.cut ?? '—'}。`, `✓ L, the sweep, the choice and the bipartition count (${mine.count}) all agree with the course engine: k = ${chosenK}, cut ${mine.cut ?? '—'}.`)
        : L(`× 有不一致：${[!lOk && 'L', !sweepOk && '扫描', !cutOk && '选择的 cut', !countOk && `非空二分数（你的 ${mine.count}，应为 ${S.unlabelledBipartitions(n)}）`].filter(Boolean).join('、')}。`,
            `× Something differs: ${[!lOk && 'L', !sweepOk && 'the sweep', !cutOk && 'the chosen cut', !countOk && `the bipartition count (yours ${mine.count}, expected ${S.unlabelledBipartitions(n)})`].filter(Boolean).join(', ')}.`);
      const gv = new GraphView(stage, { graph: g, positions: cur.positions, title: L('你的代码选出的切分', 'The cut your code chose'), width: 760, height: 300 });
      const left = mine.partition ? new Set(mine.partition[0]) : null;
      gv.render({ groups: left ? Object.fromEntries(ids.map(id => [id, left.has(id) ? 'L' : 'R'])) : undefined, groupOrder: ['L', 'R'], cut: !!left,
        tags: Object.fromEntries(ids.map((id, j) => [id, fmt(+mine.vector[j].toFixed(3))])), summary: left ? L(`你的选择：${mine.partition.map(p => p.join('')).join(' | ')}，cut ${mine.cut}`, `Your choice: ${mine.partition.map(p => p.join('')).join(' | ')}, cut ${mine.cut}`) : L('窗口内没有合法切点', 'no legal cut point inside the window') });
      const vals = mine.order.map(id => mine.vector[ids.indexOf(id)]);
      line.replaceChildren(numberLine({ order: mine.order, orderValues: vals }, left ? left.size : 0));
      status(statusBox, lOk ? '' : 'cycle', lOk ? L(`你的 L 与引擎一致（每行和 0）。λ₂ = ${fmt(+mine.eig[1].toFixed(4))}。`, `Your L matches the engine (every row sums to 0). λ₂ = ${fmt(+mine.eig[1].toFixed(4))}.`)
        : L('你的 L 与引擎不同：检查对角元（度）与非对角元（−w）。', 'Your L differs from the engine: check the diagonal (degrees) and the off-diagonal entries (−w).'));
      sweepBox.replaceChildren(h('table', {}, h('thead', {}, h('tr', {}, h('th', 'k'), h('th', L('左组', 'Left')), h('th', L('你的 cut', 'Your cut')), h('th', L('应为', 'Expected')), h('th', L('窗口内', 'In window')))),
        h('tbody', {}, mine.cands.map((c, i) => { const w = want[i] || {}, eq = Math.abs(c.cut - w.cut) < 1e-9 && c.legal === w.legal;
          const chosen = left && c.left.length === left.size && c.left.every(x => left.has(x));
          return h('tr', { class: chosen ? 'chosen' : !c.legal ? 'blocked' : '' }, h('td', String(c.k)), h('td', c.left.join('')),
            h('td', { style: eq ? '' : 'color:var(--c-red);font-weight:600' }, fmt(c.cut)), h('td', fmt(w.cut)), h('td', c.legal ? '✓' : '×')); }))));
    } catch (err) {
      match.className = 'match no';
      const msg = String(err.message || err).split('\n').filter(Boolean);
      match.textContent = err.reason ? L('已停止。', 'Stopped.') : L('你的代码运行出错：', 'Your code raised an error: ') + msg.slice(-1)[0];
    } finally { api.setBusy(false); go.disabled = false; }
  }
}

bootModule({ moduleId: 'm06-spectral-bisection', display: 'Module 06', challenges, lab, visualize });

