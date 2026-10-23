// Module 06 lab: Laplacian, live Jacobi eigen-solve, Fiedler number line and sweep. engines/spectral.js only.
import { h, fmt } from '../../assets/core.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as S from '../../engines/spectral.js';
import { G01, requireGraph } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const PRESETS = {
  g01: { name: '课程公共图 G01', graph: G01, positions: G01.positions },
  disc: { name: '两个分量（断开）', graph: S.DISCONNECTED, positions: S.DISCONNECTED.positions },
  ring: { name: '四节点环（λ2 简并）', graph: S.DEGENERATE, positions: S.DEGENERATE.positions }
};
const BAL = { '40': { minFraction: 0.4, maxFraction: 0.6 }, '30': { minFraction: 0.3, maxFraction: 0.7 }, '0': { minFraction: 0, maxFraction: 1 } };

async function lab(root, { pseudo }) {
  let presetId = 'g01', bal = '40', source = 'live', weights = {}, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side'), line = h('div', { style: 'margin-top:8px' });
  const metricBox = h('div.metrics'), statusBox = h('div.status'), matBox = h('div.decision'), diagBox = h('div.decision'), playerBox = h('div');
  const traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, line, h('div.legend', {},
    h('span', {}, '节点颜色 = 当前切点下的左 / 右组'), h('span', {}, h('i', { style: 'border-color:#db7b72;border-top-style:dashed' }), '被切断的边'),
    h('span', {}, h('i', { style: 'border-color:#d8bb78' }), '数轴上的金线：当前切点')), h('div.lab-side', { style: 'border:1px solid var(--c-line);border-radius:10px;margin-top:12px' }, h('h4', { style: 'margin-top:0' }, '拉普拉斯矩阵 L = D − A'), matBox)), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', '数值诊断'), diagBox, playerBox);
  let gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: '谱二分实验图', width: 760, height: 380 });
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: '步骤', get: e => ({ laplacian: '构造 L', eigen: '求特征值与向量', 'sweep-cut': `切点 k=${e.metrics.k}`, choose: '选择' })[e.kind] },
    { label: '左组', get: e => e.kind === 'sweep-cut' ? e.after.left.join('') : '' }, { label: 'cut', get: e => e.metrics?.cut ?? '' }, { label: '窗口内', get: e => e.kind === 'sweep-cut' ? (e.decision === 'legal' ? '是' : '否') : '' }], onPick: i => player.go(i) });

  const graph = () => { const g = requireGraph(PRESETS[presetId].graph); return { nodes: g.nodes, edges: g.edges.map(e => ({ ...e, w: weights[`${e.u}|${e.v}`] ?? e.w })) }; };
  function buildToolbar() {
    const edgeSel = h('select', { 'aria-label': '选择要修改的边' }, graph().edges.map(e => h('option', { value: `${e.u}|${e.v}` }, `${e.u}–${e.v}`)));
    const wIn = h('input', { type: 'number', min: 0.5, max: 50, step: 0.5, 'aria-label': '新权重' });
    const sync = () => { wIn.value = graph().edges.find(x => `${x.u}|${x.v}` === edgeSel.value).w; };
    edgeSel.addEventListener('change', sync); sync();
    wIn.addEventListener('change', () => { const w = Number(wIn.value); if (!(w > 0 && w <= 50)) { err.textContent = '权重须为 0–50 之间的正数。'; return; } err.textContent = ''; weights[edgeSel.value] = w; if (source === 'stored') source = 'live'; buildToolbar(); recompute(); });
    toolbar.replaceChildren(
      select('例子', Object.entries(PRESETS).map(([k, p]) => [k, p.name]), presetId, v => { presetId = v; weights = {}; source = 'live'; buildToolbar(); recompute(true); }),
      select('平衡窗口', [['40', '每组 40%–60%'], ['30', '每组 30%–70%'], ['0', '不限（只要非空）']], bal, v => { bal = v; recompute(); }),
      select('特征向量来源', presetId === 'g01' && !Object.keys(weights).length ? [['live', '浏览器实时求解（Jacobi）'], ['stored', '原作页面存储的三位小数']] : [['live', '浏览器实时求解（Jacobi）']], source, v => { source = v; recompute(); }),
      h('label', {}, '改一条边', edgeSel), h('label', {}, '新权重', wIn),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m06-spectral-bisection', { preset: presetId, options: { balance: BAL[bal], source }, input: graph(), result: run.result }) }, '导出运行记录'));
  }
  function recompute(newGraph = false) {
    const g = graph();
    const opts = { balance: BAL[bal] };
    if (source === 'stored') Object.assign(opts, { vector: g.nodes.map(n => S.STORED_VECTOR[n.id]), vectorSource: '原作存储值' });
    run = S.run(g, opts);
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join('；'); return; }
    err.textContent = '';
    if (newGraph) gv = new GraphView(stage, { graph: g, positions: PRESETS[presetId].positions, title: '谱二分实验图', width: 760, height: 380 });
    else gv.setGraph(g, PRESETS[presetId].positions, 760, 380);
    const r = run.result, L = r.L;
    matBox.replaceChildren(h('table', {}, h('thead', {}, h('tr', {}, h('th', ''), r.ids.map(id => h('th', id)), h('th', '行和'))),
      h('tbody', {}, L.map((row, i) => h('tr', {}, h('th', r.ids[i]), row.map(x => h('td', { style: x > 0 ? 'color:var(--c-gold)' : '' }, fmt(x))), h('td', fmt(row.reduce((s, x) => s + x, 0))))))));
    const d = r.diagnostics;
    diagBox.replaceChildren(h('table', {}, h('tbody', {},
      h('tr', {}, h('th', '求解'), h('td', `${d.solver}${source === 'live' ? `，${d.sweeps} 次扫掠` : ''}`)),
      h('tr', {}, h('th', '特征值'), h('td', r.eigenvalues.map(x => fmt(x)).join('，'))),
      h('tr', {}, h('th', '残差 ‖Lx−λ₂x‖/‖x‖'), h('td', d.residual.toExponential(2))),
      h('tr', {}, h('th', '与全 1 向量的夹角余弦'), h('td', d.orthogonalityToOnes.toExponential(1))),
      h('tr', {}, h('th', '连通'), h('td', d.connected ? '是' : `否（${d.components.length} 个分量）`)),
      h('tr', {}, h('th', 'λ3 − λ2'), h('td', fmt(d.gap))))), ...d.warnings.map(w => h('p.lab-note', { style: 'color:var(--c-gold)' }, '⚠ ' + w)),
      source === 'stored' ? h('p.lab-note', `原作存储的是三位小数，残差约 ${d.residual.toFixed(4)}：这是舍入，不是求解失败；改图时它不会重算。`) : '');
    trace.load(run.events); player.load(run.events);
  }
  function numberLine(r, k) {
    const W = 760, H = 124, pad = 50, vals = r.orderValues, lo = Math.min(...vals), hi = Math.max(...vals), sx = v => pad + (W - 2 * pad) * (v - lo) / ((hi - lo) || 1);
    const svg = h('svg', { viewBox: `0 0 ${W} ${H}`, class: 'gv', role: 'img', 'aria-label': `Fiedler 数轴：${r.order.map((n, i) => `${n} ${fmt(vals[i])}`).join('，')}` },
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
    svg.append(h('text', { x: W - pad + 20, y: 18, class: 'side-label', 'text-anchor': 'end' }, 'Fiedler 值（升序）'));
    return svg;
  }
  function show(i, e) {
    const r = run.result;
    const k = e.kind === 'sweep-cut' ? e.metrics.k : e.kind === 'choose' ? r.bestK : 0;
    const left = k ? r.order.slice(0, k) : null;
    gv.render({ groups: left ? Object.fromEntries(r.ids.map(id => [id, left.includes(id) ? 'L' : 'R'])) : undefined, groupOrder: ['L', 'R'], cut: !!left,
      tags: Object.fromEntries(r.ids.map((id, j) => [id, fmt(+r.fiedler[j].toFixed(3))])), summary: k ? `切点 k=${k}` : '尚未切分' });
    line.replaceChildren(numberLine(r, k));
    const s = k ? r.sweep[k - 1] : null;
    metrics(metricBox, [['λ₂', fmt(+r.eigenvalues[1].toFixed(4))], ['切点 k', k || '—'], ['cut', s ? s.cut : '—']]);
    if (e.kind === 'laplacian') status(statusBox, '', '构造 L：每条边贡献两个对角 +w、两个非对角 −w。每行和为 0。');
    else if (e.kind === 'eigen') status(statusBox, r.diagnostics.warnings.length ? 'limit' : '', `求出特征值；Fiedler 排序：${r.order.join(', ')}。`);
    else if (e.kind === 'sweep-cut') status(statusBox, s.legal ? '' : 'blocked', `k = ${k}：${s.left.join('')} | ${s.right.join('')}，cut ${s.cut}，${s.legal ? '在窗口内' : `不在窗口内（每组需 ${r.window.lo}–${r.window.hi} 个）`}。`);
    else status(statusBox, r.partition ? '' : 'invalid', r.partition ? `选择窗口内 cut 最小的 k = ${r.bestK}：${r.partition.map(p => p.join('')).join(' | ')}，cut ${r.cut}。` : '窗口内没有合法切点。');
    pseudo.spectral?.show(e.kind === 'laplacian' ? [1] : e.kind === 'eigen' ? [2, 3, 4, 5] : e.kind === 'sweep-cut' ? [6] : [7], '');
  }
  buildToolbar(); recompute(true);
}

bootModule({ moduleId: 'm06-spectral-bisection', display: 'Module 06', challenges, lab });
