// Module 09 lab: (A) path-delay evaluation on a chain; (B) RW labelling and reconstruction with replicated
// instances on the candidate DAG. Every number comes from engines/rw.js.
import { h } from '../../assets/core.js';
import { GraphView, PALETTE } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as RW from '../../engines/rw.js';
import { challenges, NO_REPLICATION_BEST } from './challenges.js';

function chainLab(root) {
  const ids = RW.CHAIN.nodes, cuts = [false, true, false];
  let D = 3;
  const out = h('div'), info = h('div.status');
  const draw = () => {
    const groups = [[]];
    ids.forEach((n, i) => { groups.at(-1).push(n); if (i < cuts.length && cuts[i]) groups.push([]); });
    const ev = RW.evaluatePartition({ ...RW.CHAIN, D }, groups);
    const W = 760, Hh = 170, x = i => 90 + i * 190;
    const svg = h('svg', { viewBox: `0 0 ${W} ${Hh}`, class: 'gv', role: 'img', 'aria-label': `链 ${groups.map(g => g.join('')).join(' | ')}，延迟 ${ev.ok ? ev.maxDelay : '不合法'}` },
      h('defs', {}, h('marker', { id: 'arr9', viewBox: '0 0 10 10', refX: '9', refY: '5', markerWidth: '7', markerHeight: '7', orient: 'auto' }, h('path', { d: 'M0 0 L10 5 L0 10 z', fill: '#8aa7a6' }))));
    let gi = 0, start = 0;
    ids.forEach((n, i) => { if (i === ids.length - 1 || cuts[i]) { const x0 = x(start) - 52, x1 = x(i) + 52; svg.append(h('rect', { x: x0, y: 30, width: x1 - x0, height: 100, rx: 22, fill: PALETTE[gi % 8], 'fill-opacity': '.14', stroke: PALETTE[gi % 8], 'stroke-dasharray': '6 4' })); gi++; start = i + 1; } });
    ids.forEach((n, i) => {
      if (i < ids.length - 1) svg.append(h('line', { x1: x(i) + 26, y1: 80, x2: x(i + 1) - 30, y2: 80, stroke: cuts[i] ? '#db7b72' : '#9fc9bf', 'stroke-width': 3, 'stroke-dasharray': cuts[i] ? '7 5' : null, 'marker-end': 'url(#arr9)' }),
        h('text', { x: (x(i) + x(i + 1)) / 2, y: 64, 'text-anchor': 'middle', class: 'w' }, cuts[i] ? `+${D}` : '+0'));
      svg.append(h('g', { class: 'node', transform: `translate(${x(i)} 80)` }, h('circle', { r: 24, fill: '#a9bdb8' }), h('text', { 'text-anchor': 'middle', y: 6 }, n)),
        h('text', { x: x(i), y: 158, 'text-anchor': 'middle', class: 'side-label' }, ev.ok ? `到达 ${ev.arrival[n]}` : ''));
    });
    out.replaceChildren(svg);
    info.className = 'status ' + (ev.ok ? '' : 'invalid');
    info.textContent = ev.ok ? `${groups.map(g => `{${g.join(',')}}`).join(' | ')}：4 个节点延迟 + ${ev.crossings} 次跨界 × ${D} = ${ev.maxDelay}` : `不合法：${ev.errors.join('；')}`;
  };
  const toggles = h('div.lab-toolbar', { style: 'align-items:center' }, cuts.map((_, i) => h('button.btn.small', { type: 'button', 'aria-pressed': String(cuts[i]), onclick: ev => { cuts[i] = !cuts[i]; ev.currentTarget.setAttribute('aria-pressed', cuts[i]); ev.currentTarget.textContent = `${ids[i]}→${ids[i + 1]}：${cuts[i] ? '跨簇' : '同簇'}`; draw(); } }, `${ids[i]}→${ids[i + 1]}：${cuts[i] ? '跨簇' : '同簇'}`)),
    select('跨簇延迟 D', [1, 2, 3, 4, 5].map(v => [String(v), String(v)]), '3', v => { D = +v; draw(); }));
  root.replaceChildren(h('h3', { style: 'color:var(--c-gold);margin-top:0' }, 'A · 一条路径的延迟（每个节点 δ = 1，容量 2）'), toggles, out, info);
  draw();
}

function instanceView(result, D, upto) {
  const clusters = result.selected.slice(0, upto);
  const W = 760, colW = W / Math.max(4, Math.ceil(clusters.length / 2)), rowH = 210;
  const svg = h('svg', { viewBox: `0 0 ${W} ${rowH * 2 + 20}`, class: 'gv', role: 'img', 'aria-label': `已恢复 ${clusters.length} 个簇` });
  const pos = {};
  clusters.forEach((root, ci) => {
    const members = result.clusters[root], col = ci % Math.ceil(Math.max(4, clusters.length) / 2), row = Math.floor(ci / Math.ceil(Math.max(4, clusters.length) / 2));
    const x0 = 8 + col * colW, y0 = 14 + row * rowH, cw = colW - 16;
    svg.append(h('rect', { x: x0, y: y0, width: cw, height: rowH - 24, rx: 12, fill: PALETTE[ci % 8], 'fill-opacity': '.1', stroke: PALETTE[ci % 8], 'stroke-dasharray': '5 4' }),
      h('text', { x: x0 + 8, y: y0 + 18, class: 'side-label', style: 'font-size:12px' }, `簇根 ${root}（${members.length}/${RW.CANDIDATE_DAG.capacity}）`));
    members.forEach((m, mi) => { pos[`${m}@${root}`] = [x0 + cw / 2 + (mi % 2 ? 26 : -26), y0 + 44 + mi * 38]; });
  });
  for (const e of result.instanceEdges) {
    const a = pos[e.from], b = pos[e.to];
    if (!a || !b) continue;
    svg.append(h('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], stroke: e.cost ? '#db7b72' : '#9fc9bf', 'stroke-width': e.cost ? 1.6 : 2, 'stroke-dasharray': e.cost ? '5 4' : null, opacity: e.cost ? 0.75 : 1 }));
  }
  for (const [id, [x, y]] of Object.entries(pos)) {
    const [lg] = id.split('@'), copies = result.instances.filter(i => i.logicalId === lg).length;
    svg.append(h('g', { class: 'node', transform: `translate(${x} ${y})` }, h('circle', { r: 14, fill: copies > 1 ? '#d8bb78' : '#a9bdb8', stroke: copies > 1 ? '#fff' : '#0d262c', 'stroke-dasharray': copies > 1 ? '3 2' : null }),
      h('text', { 'text-anchor': 'middle', y: 5, style: 'font-size:13px' }, lg)), h('text', { x: x + 18, y: y + 4, class: 'side-label', style: 'font-size:10px' }, `${result.arrival[id]}`));
  }
  return svg;
}

async function lab(root, { pseudo }) {
  const chainBox = h('div.lab-side', { style: 'border:1px solid var(--c-line);border-radius:10px;margin-bottom:18px' });
  chainLab(chainBox);
  let D = 3, cap = 4, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side'), inst = h('div', { style: 'margin-top:10px' });
  const metricBox = h('div.metrics'), statusBox = h('div.status'), candBox = h('div.decision'), playerBox = h('div');
  const traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar');
  root.replaceChildren(chainBox, h('h3', { style: 'color:var(--c-gold)' }, 'B · RW 标记与恢复（候选 DAG）'),
    h('p.notice', { style: 'color:var(--ink)' }, '候选数据：12 节点 DAG 由原作影片的图与 Δ 表复原；“得分相等时拓扑序靠后者优先”是本课程的假设。它重现了 8 簇、20 实例、输出 8，但原始边表与平票规则尚待原作者确认。'),
    toolbar, h('div.lab', {}, h('div', {}, stage, inst, h('div.legend', {}, h('span', {}, '实例图：金色虚线圈 = 被复制的逻辑节点；红色虚线 = 跨簇连线（+D）；数字 = 到达时间'))), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', '本步的得分与候选簇'), candBox, playerBox);
  const dag = () => ({ ...RW.CANDIDATE_DAG, D, capacity: cap });
  const gv = new GraphView(stage, { graph: { nodes: RW.CANDIDATE_DAG.nodes, edges: RW.CANDIDATE_DAG.edges.map(([u, v]) => [u, v]) }, positions: RW.CANDIDATE_DAG.positions, directed: true, radius: 20, title: '候选 DAG', width: 760, height: 440 });
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: '阶段', get: e => ({ 'pi-labels': '初始化', label: '标记', 'select-cluster': '恢复' })[e.kind] },
    { label: '节点 / 簇根', get: e => e.kind === 'label' ? e.after.node : e.kind === 'select-cluster' ? e.after.root : 'PI' }, { label: 'l1 / l2 / l', get: e => e.kind === 'label' ? `${e.metrics.l1} / ${e.metrics.l2} / ${e.metrics.label}` : '' },
    { label: '簇', get: e => e.kind === 'label' ? e.after.cluster.join('') : e.kind === 'select-cluster' ? e.after.members.join('') : '' }], onPick: i => player.go(i) });
  toolbar.replaceChildren(
    select('跨簇延迟 D', [1, 2, 3, 4, 5].map(v => [String(v), String(v)]), String(D), v => { D = +v; recompute(); }),
    select('簇容量 M', [2, 3, 4, 5, 6].map(v => [String(v), String(v)]), String(cap), v => { cap = +v; recompute(); }),
    h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m09-rajaraman-wong', { options: { D, capacity: cap }, input: dag(), result: run.result, events: run.events, note: 'candidate DAG; tie rule assumed' }) }, '导出运行记录'));
  function recompute() {
    run = RW.run(dag());
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join('；'); return; }
    err.textContent = '';
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const r = run.result, labels = {};
    for (const ev of run.events.slice(0, i + 1)) { if (ev.kind === 'pi-labels') Object.assign(labels, ev.after); if (ev.kind === 'label') labels[ev.after.node] = ev.after.label; }
    const inCluster = e.kind === 'label' ? e.after.cluster : e.kind === 'select-cluster' ? e.after.members : [];
    const focus = e.kind === 'label' ? [e.after.node] : e.kind === 'select-cluster' ? [e.after.root] : [];
    gv.render({ groups: Object.fromEntries(RW.CANDIDATE_DAG.nodes.map(n => [n, inCluster.includes(n) ? 'in' : 'out'])), groupOrder: ['in', 'out'], focus,
      fills: Object.fromEntries(RW.CANDIDATE_DAG.nodes.map(n => [n, inCluster.includes(n) ? '#77cdbb' : RW.CANDIDATE_DAG.PI.includes(n) ? '#8fb1e6' : '#a9bdb8'])),
      tags: Object.fromEntries(Object.entries(labels).map(([n, l]) => [n, `l=${l}`])), summary: e.decision || '初始化' });
    const selected = run.events.slice(0, i + 1).filter(x => x.kind === 'select-cluster').length;
    inst.replaceChildren(selected ? instanceView(r, D, selected) : h('p.lab-note', '标记阶段：簇还没有恢复。'));
    metrics(metricBox, [['标记', `${Object.keys(labels).length}/${RW.CANDIDATE_DAG.nodes.length}`], ['已恢复簇', selected], ['最大延迟', selected === r.selected.length ? r.maxDelay : '—']]);
    if (e.kind === 'pi-labels') status(statusBox, '', `初始化：PI ${RW.CANDIDATE_DAG.PI.join('、')} 的标签 = 自身延迟 1；Δ 表由最长路径算出。`);
    else if (e.kind === 'label') status(statusBox, '', `${e.decision}。候选簇 {${e.after.cluster.join(', ')}}（容量 ${cap}）。`);
    else status(statusBox, selected === r.selected.length ? '' : 'limit', `${e.decision}：成员 ${e.after.members.join('')}${e.after.inputs.length ? `，簇外输入 ${e.after.inputs.join('、')} 成为新的簇根` : ''}。${selected === r.selected.length ? `完成：${r.selected.length} 簇、${r.instanceCount} 个实例，输出 ${Object.entries(r.outputDelays).map(([p, t]) => `${p}=${t}`).join('、')}。不复制时（容量 4、D 3）穷举最好是 ${RW.evaluatePartition(RW.CANDIDATE_DAG, NO_REPLICATION_BEST).maxDelay}。` : ''}`);
    candBox.replaceChildren(e.kind === 'label' ? h('table', {}, h('thead', {}, h('tr', {}, h('th', '祖先 x'), h('th', 'l(x)'), h('th', 'Δ(x,v)'), h('th', '得分'), h('th', ''))),
      h('tbody', {}, e.candidates.map(c => h('tr', { class: c.inCluster ? 'chosen' : '' }, h('td', c.x), h('td', String(c.l)), h('td', String(c.delta)), h('td', String(c.score)), h('td', c.inCluster ? '簇内' : `簇外 → +${D}`))))) : h('p.muted', e.kind === 'select-cluster' ? '恢复阶段：见左下实例图。' : '—'));
    pseudo.rw?.show(e.kind === 'pi-labels' ? [1, 2] : e.kind === 'label' ? [3, 4, 5, 6, 7] : [8, 9], '');
  }
  recompute();
}

bootModule({ moduleId: 'm09-rajaraman-wong', display: 'Module 09', challenges, lab });
