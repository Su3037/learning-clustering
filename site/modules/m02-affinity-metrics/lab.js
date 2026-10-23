// Module 02 lab: the same graph under three scoring models. Every number comes from engines/affinity.js.
import { h, fmt } from '../../assets/core.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as AF from '../../engines/affinity.js';
import { G01 } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const NET_POS = { A: [120, 120], B: [300, 70], C: [470, 120], D: [470, 330], E: [300, 380], F: [640, 380] };
const PRESETS = {
  g01: { name: '课程公共图 G01', graph: G01, positions: G01.positions, kind: 'graph' },
  priority: { name: 'priority 图（原作者 Capeur）', graph: AF.PRIORITY_GRAPH, positions: AF.PRIORITY_GRAPH.positions, kind: 'graph' },
  netlist: { name: 'tiny netlist：两条宽 net + 一条私有 net', graph: AF.TINY_NETLIST, positions: NET_POS, kind: 'netlist' }
};


async function lab(root, { pseudo }) {
  let presetId = 'priority', metric = 'shared', weights = null, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), decision = h('div.decision'), rankBox = h('div.decision');
  const playerBox = h('div'), traceBox = h('div'), err = h('p.lab-error');
  const toolbar = h('div.lab-toolbar');
  const legend = h('div.legend');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, legend), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', '这一对的分数从哪里来'), decision, h('h4', '当前排名'), rankBox, playerBox);
  const gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: '评分实验图' });
  const player = new Player(playerBox, { onIndex: show, speed: 1300 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: '名次', get: e => e.metrics.rank }, { label: '节点对', get: e => `${e.after.u}–${e.after.v}` }, { label: '分数', get: e => fmt(e.after.score) }, { label: '组成', get: e => explainParts(e) }], onPick: i => player.go(i) });

  function currentGraph() {
    const p = PRESETS[presetId];
    if (p.kind !== 'graph') return p.graph;
    return { nodes: p.graph.nodes, edges: p.graph.edges.map(e => { const [u, v, w] = Array.isArray(e) ? e : [e.u, e.v, e.w]; const k = [u, v].sort().join('|'); return [u, v, weights?.[k] ?? w]; }) };
  }
  function buildToolbar() {
    const p = PRESETS[presetId];
    const metricOpts = p.kind === 'netlist' ? [['pin', 'pin-count（clique 模型）'], ['raw', '按 net 计数（未摊薄，对照用）']] : [['edge', '直接边权 edge'], ['shared', '共同邻居 shared']];
    if (!metricOpts.some(([v]) => v === metric)) metric = metricOpts[0][0];
    const items = [select('例子', Object.entries(PRESETS).map(([k, v]) => [k, v.name]), presetId, v => { presetId = v; weights = null; buildToolbar(); recompute(); }),
      select('评分方式', metricOpts, metric, v => { metric = v; recompute(); })];
    if (p.kind === 'graph') {
      const edges = currentGraph().edges;
      const edgeSel = h('select', { 'aria-label': '选择要修改的边' }, edges.map(([u, v]) => h('option', { value: [u, v].sort().join('|') }, `${u}–${v}`)));
      const wIn = h('input', { type: 'number', min: 1, max: 99, step: 1, 'aria-label': '新权重' });
      const syncW = () => { const [u, v] = edgeSel.value.split('|'); wIn.value = currentGraph().edges.find(e => [e[0], e[1]].sort().join('|') === edgeSel.value)[2]; };
      edgeSel.addEventListener('change', syncW); syncW();
      wIn.addEventListener('change', () => { const w = Number(wIn.value); if (!(w > 0 && w <= 99)) { err.textContent = '权重须为 1–99 的正数。'; return; } err.textContent = ''; weights = { ...(weights || {}), [edgeSel.value]: w }; recompute(); });
      items.push(h('label', {}, '改一条边', edgeSel), h('label', {}, '新权重', wIn));
    }
    items.push(h('button.btn.small', { type: 'button', onclick: () => { weights = null; buildToolbar(); recompute(); } }, '恢复原权重'),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m02-affinity-metrics', { preset: presetId, metric, input: currentGraph(), engine: run.metadata, ranking: run.result.ranking }) }, '导出运行记录'));
    toolbar.replaceChildren(...items);
  }
  function recompute() {
    const p = PRESETS[presetId], g = currentGraph();
    if (metric === 'raw') {
      const pc = AF.pinCount(g);
      const list = pc.raw.map(x => ({ ...x, parts: { nets: pc.scores.find(s => s.u === x.u && s.v === x.v).parts.nets } }));
      run = { events: list.map((pp, i) => ({ eventId: `raw-${i}`, kind: 'pair-scored', after: { u: pp.u, v: pp.v, score: pp.score }, metrics: { rank: i + 1 }, parts: pp.parts })), result: { ranking: list, top: list[0] }, metadata: { engine: 'affinity', note: 'raw net count, comparison only' } };
    } else run = AF.run(g, { metric: p.kind === 'netlist' ? 'pin' : metric });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join('；'); return; }
    gv.setGraph(p.kind === 'netlist' ? cliqueGraph(g) : g, p.positions, 760, 480);
    legend.replaceChildren(...(p.kind === 'netlist'
      ? [h('span', {}, h('i', { style: 'border-color:#5d7c80' }), 'net 展开后的两两“示意贡献”（不是新导线），数字为每对得到的份额')]
      : [h('span', {}, h('i', { style: 'border-color:#d8bb78' }), '金色：参与当前这一对分数的边'), h('span', {}, h('b', { style: 'background:#d8bb78' }), '金圈：当前节点对')]));
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const p = PRESETS[presetId], list = run.result.ranking;
    const hl = [];
    if (e.parts?.direct) hl.push([e.after.u, e.after.v]);
    for (const c of e.parts?.via || []) hl.push([e.after.u, c.x], [e.after.v, c.x]);
    gv.render({ focus: [e.after.u, e.after.v], highlight: p.kind === 'netlist' ? [[e.after.u, e.after.v]] : hl,
      edgeLabels: p.kind === 'netlist' ? cliqueLabels(currentGraph()) : undefined,
      tags: Object.fromEntries((e.parts?.via || []).map(c => [c.x, `共同邻居`])),
      summary: `第 ${i + 1} 名：${e.after.u}–${e.after.v}，分数 ${fmt(e.after.score)}` });
    metrics(metricBox, [['正分节点对', list.length], ['第一名', list[0] ? `${list[0].u}–${list[0].v}` : '—'], ['当前分数', fmt(e.after.score)]]);
    const name = { edge: '直接边权', shared: '共同邻居', pin: 'pin-count', raw: 'net 计数' }[metric] || metric;
    status(statusBox, '', `${name}：第 ${i + 1} 名 ${e.after.u}–${e.after.v} = ${fmt(e.after.score)}${i === 0 ? '（若用于合并，这一对最先合并）' : ''}`);
    decision.replaceChildren(partsTable(e));
    rankBox.replaceChildren(h('table', {}, h('tbody', {}, list.map((x, k) => h('tr', { class: k === i ? 'chosen' : '' }, h('td', String(k + 1)), h('td', `${x.u}–${x.v}`), h('td', fmt(x.score)))))));
    if (metric === 'shared') pseudo.shared?.show(i === list.length - 1 ? [5, 6, 7] : (e.parts.via.length ? [1, 2, 3, 4, 5] : [1, 2, 5]),
      `${e.after.u}–${e.after.v}：直接 ${e.parts.direct}${e.parts.via.map(c => ` + min(${c.wu},${c.wv})`).join('')} = ${e.after.score}`);
  }
  buildToolbar(); recompute();
}

function partsTable(e) {
  const p = e.parts || {};
  if (p.nets) return h('table', {}, h('thead', {}, h('tr', {}, h('th', 'net'), h('th', '引脚数'), h('th', '这一对得到'))),
    h('tbody', {}, p.nets.map(n => h('tr', {}, h('td', n.id), h('td', String(n.size)), h('td', `${n.w}/(${n.size}−1) = ${fmt(n.share)}`))),
      h('tr.chosen', {}, h('td', '合计'), h('td', ''), h('td', fmt(e.after.score)))));
  const rows = [h('tr', {}, h('td', '直接边'), h('td', p.direct ? `w(${e.after.u},${e.after.v}) = ${p.direct}` : '没有直接连线：0'))];
  for (const c of p.via || []) rows.push(h('tr', {}, h('td', `经 ${c.x}`), h('td', `min(${c.wu}, ${c.wv}) = ${c.min}`)));
  rows.push(h('tr.chosen', {}, h('td', '合计'), h('td', fmt(e.after.score))));
  return h('table', {}, h('tbody', {}, rows));
}
function explainParts(e) {
  const p = e.parts || {};
  if (p.nets) return p.nets.map(n => `${n.id}:${fmt(n.share)}`).join(' + ');
  return [p.direct ? `直接${p.direct}` : '', ...(p.via || []).map(c => `经${c.x}:${c.min}`)].filter(Boolean).join(' + ') || '—';
}
function cliqueGraph(net) {
  const pairs = new Map();
  for (const n of net.nets) { const pins = [...new Set(n.pins)].sort(); for (let i = 0; i < pins.length; i++) for (let j = i + 1; j < pins.length; j++) pairs.set(pins[i] + '|' + pins[j], [pins[i], pins[j]]); }
  return { nodes: net.nodes, edges: [...pairs.values()].map(([u, v]) => [u, v, undefined]) };
}
function cliqueLabels(net) {
  const pc = AF.pinCount(net);
  return Object.fromEntries(pc.scores.map(s => [s.u + '|' + s.v, fmt(s.score)]));
}

bootModule({ moduleId: 'm02-affinity-metrics', display: 'Module 02', challenges, lab });
