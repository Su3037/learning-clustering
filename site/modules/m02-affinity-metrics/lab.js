// Module 02 lab: the same graph under three scoring models. Every number comes from engines/affinity.js.
import { h, fmt, L } from '../../assets/core.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as AF from '../../engines/affinity.js';
import { G01 } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const NET_POS = { A: [120, 120], B: [300, 70], C: [470, 120], D: [470, 330], E: [300, 380], F: [640, 380] };
const PRESETS = {
  g01: { name: L('课程公共图 G01', 'Course graph G01'), graph: G01, positions: G01.positions, kind: 'graph' },
  priority: { name: L('priority 图（原作者 Capeur）', 'Priority graph (original author Capeur)'), graph: AF.PRIORITY_GRAPH, positions: AF.PRIORITY_GRAPH.positions, kind: 'graph' },
  netlist: { name: L('tiny netlist：两条宽 net + 一条私有 net', 'Tiny netlist: two wide nets + one private net'), graph: AF.TINY_NETLIST, positions: NET_POS, kind: 'netlist' }
};
const METRIC_NAME = { edge: L('直接边权', 'direct weight'), shared: L('共同邻居', 'shared neighbours'), pin: 'pin-count', raw: L('net 计数', 'net count') };

async function lab(root, { pseudo }) {
  let presetId = 'priority', metric = 'shared', weights = null, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), decision = h('div.decision'), rankBox = h('div.decision');
  const playerBox = h('div'), traceBox = h('div'), err = h('p.lab-error');
  const toolbar = h('div.lab-toolbar');
  const legend = h('div.legend');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, legend), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', L('这一对的分数从哪里来', 'Where this pair’s score comes from')), decision, h('h4', L('当前排名', 'Current ranking')), rankBox, playerBox);
  const gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: L('评分实验图', 'Scoring lab graph') });
  const player = new Player(playerBox, { onIndex: show, speed: 1300 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: L('名次', 'Rank'), get: e => e.metrics.rank }, { label: L('节点对', 'Pair'), get: e => `${e.after.u}–${e.after.v}` }, { label: L('分数', 'Score'), get: e => fmt(e.after.score) }, { label: L('组成', 'Parts'), get: e => explainParts(e) }], onPick: i => player.go(i) });

  function currentGraph() {
    const p = PRESETS[presetId];
    if (p.kind !== 'graph') return p.graph;
    return { nodes: p.graph.nodes, edges: p.graph.edges.map(e => { const [u, v, w] = Array.isArray(e) ? e : [e.u, e.v, e.w]; const k = [u, v].sort().join('|'); return [u, v, weights?.[k] ?? w]; }) };
  }
  function buildToolbar() {
    const p = PRESETS[presetId];
    const metricOpts = p.kind === 'netlist' ? [['pin', L('pin-count（clique 模型）', 'pin-count (clique model)')], ['raw', L('按 net 计数（未摊薄，对照用）', 'net count (not shared out; for comparison)')]] : [['edge', L('直接边权 edge', 'direct weight (edge)')], ['shared', L('共同邻居 shared', 'shared neighbours (shared)')]];
    if (!metricOpts.some(([v]) => v === metric)) metric = metricOpts[0][0];
    const items = [select(L('例子', 'Example'), Object.entries(PRESETS).map(([k, v]) => [k, v.name]), presetId, v => { presetId = v; weights = null; buildToolbar(); recompute(); }),
      select(L('评分方式', 'Score'), metricOpts, metric, v => { metric = v; recompute(); })];
    if (p.kind === 'graph') {
      const edges = currentGraph().edges;
      const edgeSel = h('select', { 'aria-label': L('选择要修改的边', 'Choose the edge to change') }, edges.map(([u, v]) => h('option', { value: [u, v].sort().join('|') }, `${u}–${v}`)));
      const wIn = h('input', { type: 'number', min: 1, max: 99, step: 1, 'aria-label': L('新权重', 'New weight') });
      const syncW = () => { wIn.value = currentGraph().edges.find(e => [e[0], e[1]].sort().join('|') === edgeSel.value)[2]; };
      edgeSel.addEventListener('change', syncW); syncW();
      wIn.addEventListener('change', () => { const w = Number(wIn.value); if (!(w > 0 && w <= 99)) { err.textContent = L('权重须为 1–99 的正数。', 'The weight must be a positive number from 1 to 99.'); return; } err.textContent = ''; weights = { ...(weights || {}), [edgeSel.value]: w }; recompute(); });
      items.push(h('label', {}, L('改一条边', 'Change an edge'), edgeSel), h('label', {}, L('新权重', 'New weight'), wIn));
    }
    items.push(h('button.btn.small', { type: 'button', onclick: () => { weights = null; buildToolbar(); recompute(); } }, L('恢复原权重', 'Restore weights')),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m02-affinity-metrics', { preset: presetId, metric, input: currentGraph(), engine: run.metadata, ranking: run.result.ranking }) }, L('导出运行记录', 'Export run')));
    toolbar.replaceChildren(...items);
  }
  function recompute() {
    const p = PRESETS[presetId], g = currentGraph();
    if (metric === 'raw') {
      const pc = AF.pinCount(g);
      const list = pc.raw.map(x => ({ ...x, parts: { nets: pc.scores.find(s => s.u === x.u && s.v === x.v).parts.nets } }));
      run = { events: list.map((pp, i) => ({ eventId: `raw-${i}`, kind: 'pair-scored', after: { u: pp.u, v: pp.v, score: pp.score }, metrics: { rank: i + 1 }, parts: pp.parts })), result: { ranking: list, top: list[0] }, metadata: { engine: 'affinity', note: 'raw net count, comparison only' } };
    } else run = AF.run(g, { metric: p.kind === 'netlist' ? 'pin' : metric });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join(L('；', '; ')); return; }
    gv.setGraph(p.kind === 'netlist' ? cliqueGraph(g) : g, p.positions, 760, 480);
    legend.replaceChildren(...(p.kind === 'netlist'
      ? [h('span', {}, h('i', { style: 'border-color:#5d7c80' }), L('net 展开后的两两“示意贡献”（不是新导线），数字为每对得到的份额', 'A net drawn as pairwise “illustrative contributions” (not new wires); the numbers are each pair’s share'))]
      : [h('span', {}, h('i', { style: 'border-color:#d8bb78' }), L('金色：参与当前这一对分数的边', 'Gold: edges that make up the current pair’s score')), h('span', {}, h('b', { style: 'background:#d8bb78' }), L('金圈：当前节点对', 'Gold rings: the current pair'))]));
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const p = PRESETS[presetId], list = run.result.ranking;
    const hl = [];
    if (e.parts?.direct) hl.push([e.after.u, e.after.v]);
    for (const c of e.parts?.via || []) hl.push([e.after.u, c.x], [e.after.v, c.x]);
    gv.render({ focus: [e.after.u, e.after.v], highlight: p.kind === 'netlist' ? [[e.after.u, e.after.v]] : hl,
      edgeLabels: p.kind === 'netlist' ? cliqueLabels(currentGraph()) : undefined,
      tags: Object.fromEntries((e.parts?.via || []).map(c => [c.x, L('共同邻居', 'shared neighbour')])),
      summary: L(`第 ${i + 1} 名：${e.after.u}–${e.after.v}，分数 ${fmt(e.after.score)}`, `Rank ${i + 1}: ${e.after.u}–${e.after.v}, score ${fmt(e.after.score)}`) });
    metrics(metricBox, [[L('正分节点对', 'Positive pairs'), list.length], [L('第一名', 'First'), list[0] ? `${list[0].u}–${list[0].v}` : '—'], [L('当前分数', 'Current score'), fmt(e.after.score)]]);
    const name = METRIC_NAME[metric] || metric;
    status(statusBox, '', L(`${name}：第 ${i + 1} 名 ${e.after.u}–${e.after.v} = ${fmt(e.after.score)}${i === 0 ? '（若用于合并，这一对最先合并）' : ''}`,
      `${name}: rank ${i + 1}, ${e.after.u}–${e.after.v} = ${fmt(e.after.score)}${i === 0 ? ' (if used for merging, this pair merges first)' : ''}`));
    decision.replaceChildren(partsTable(e));
    rankBox.replaceChildren(h('table', {}, h('tbody', {}, list.map((x, k) => h('tr', { class: k === i ? 'chosen' : '' }, h('td', String(k + 1)), h('td', `${x.u}–${x.v}`), h('td', fmt(x.score)))))));
    if (metric === 'shared') pseudo.shared?.show(i === list.length - 1 ? [5, 6, 7] : (e.parts.via.length ? [1, 2, 3, 4, 5] : [1, 2, 5]),
      `${e.after.u}–${e.after.v}${L('：直接 ', ': direct ')}${e.parts.direct}${e.parts.via.map(c => ` + min(${c.wu},${c.wv})`).join('')} = ${e.after.score}`);
  }
  buildToolbar(); recompute();
}

function partsTable(e) {
  const p = e.parts || {};
  if (p.nets) return h('table', {}, h('thead', {}, h('tr', {}, h('th', 'net'), h('th', L('引脚数', 'Pins')), h('th', L('这一对得到', 'This pair gets')))),
    h('tbody', {}, p.nets.map(n => h('tr', {}, h('td', n.id), h('td', String(n.size)), h('td', `${n.w}/(${n.size}−1) = ${fmt(n.share)}`))),
      h('tr.chosen', {}, h('td', L('合计', 'Total')), h('td', ''), h('td', fmt(e.after.score)))));
  const rows = [h('tr', {}, h('td', L('直接边', 'Direct edge')), h('td', p.direct ? `w(${e.after.u},${e.after.v}) = ${p.direct}` : L('没有直接连线：0', 'No direct wire: 0')))];
  for (const c of p.via || []) rows.push(h('tr', {}, h('td', L(`经 ${c.x}`, `via ${c.x}`)), h('td', `min(${c.wu}, ${c.wv}) = ${c.min}`)));
  rows.push(h('tr.chosen', {}, h('td', L('合计', 'Total')), h('td', fmt(e.after.score))));
  return h('table', {}, h('tbody', {}, rows));
}
function explainParts(e) {
  const p = e.parts || {};
  if (p.nets) return p.nets.map(n => `${n.id}:${fmt(n.share)}`).join(' + ');
  return [p.direct ? L(`直接${p.direct}`, `direct ${p.direct}`) : '', ...(p.via || []).map(c => L(`经${c.x}:${c.min}`, `via ${c.x}: ${c.min}`))].filter(Boolean).join(' + ') || '—';
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

/* ---------- code lab: run the learner's three functions and compare each ranking with the course engine ---------- */
const NEW_GRAPH = { nodes: ['M', 'N', 'O', 'P'], edges: [['M', 'N', 2], ['N', 'O', 10], ['M', 'O', 3], ['O', 'P', 1]],
  positions: { M: [150, 120], N: [420, 90], O: [420, 330], P: [650, 380] } };
function visualize(root, api) {
  const EXAMPLES = {
    g01: { name: L('课程公共图 G01', 'Course graph G01'), graph: G01, positions: G01.positions, kind: 'graph' },
    priority: { name: L('priority 图', 'Priority graph'), graph: AF.PRIORITY_GRAPH, positions: AF.PRIORITY_GRAPH.positions, kind: 'graph' },
    fresh: { name: L('一张新图（练习里没出现过）', 'A new graph (not in the exercise)'), graph: NEW_GRAPH, positions: NEW_GRAPH.positions, kind: 'graph' },
    netlist: { name: 'tiny netlist', graph: AF.TINY_NETLIST, positions: NET_POS, kind: 'netlist' }
  };
  let ex = 'g01', metric = 'shared';
  const stage = h('div.lab-stage'), side = h('div.lab-side'), metricBox = h('div.metrics'), statusBox = h('div.status'), rankBox = h('div.decision'), playerBox = h('div');
  const match = h('p.match'), toolbar = h('div.lab-toolbar');
  const metricSel = h('span');
  const go = h('button.btn.primary', { type: 'button', onclick: runMine }, L('▶ 用我的代码运行', '▶ Run my code'));
  const buildMetric = () => {
    const opts = EXAMPLES[ex].kind === 'netlist' ? [['pin', 'affinity_pin_count']] : [['edge', 'affinity_edge_weight'], ['shared', 'affinity_shared_neighbors']];
    if (!opts.some(([v]) => v === metric)) metric = opts[0][0];
    metricSel.replaceChildren(select(L('函数', 'Function'), opts, metric, v => { metric = v; }));
  };
  toolbar.append(select(L('例子', 'Example'), Object.entries(EXAMPLES).map(([k, v]) => [k, v.name]), ex, v => { ex = v; buildMetric(); }), metricSel, go);
  buildMetric();
  side.append(metricBox, statusBox, h('h4', L('你的排名 · 引擎的排名', 'Your ranking · the engine’s ranking')), rankBox, playerBox);
  root.append(h('h3', L('用你的代码跑一遍', 'Watch your own code run')),
    h('p.muted', L('这里调用的是你在上面写的函数，不是课程引擎。左边的图按你的排名逐对高亮；右边逐行对照课程引擎的结果。',
      'This calls the functions you wrote above, not the course engine. The graph highlights your ranking pair by pair; the table compares it row by row with the course engine.')),
    toolbar, h('div.lab', {}, h('div', {}, stage), side), match);
  let gv, mine = [], ref = [];
  const player = new Player(playerBox, { onIndex: show, speed: 900 });
  stage.append(h('p.muted', { style: 'padding:40px 10px;text-align:center' }, L('写好函数后，按“用我的代码运行”。', 'Once your functions are written, press “Run my code”.')));

  async function runMine() {
    if (api.busy) return;
    const e = EXAMPLES[ex], g = e.graph;
    const nodes = g.nodes.map(n => typeof n === 'string' ? n : n.id);
    const call = metric === 'edge' ? `m.affinity_edge_weight([tuple(x) for x in ${JSON.stringify(g.edges.map(x => Array.isArray(x) ? x : [x.u, x.v, x.w]))}])`
      : metric === 'shared' ? `m.affinity_shared_neighbors(${JSON.stringify(nodes)}, [tuple(x) for x in ${JSON.stringify(g.edges.map(x => Array.isArray(x) ? x : [x.u, x.v, x.w]))}])`
        : `m.affinity_pin_count(${JSON.stringify(nodes)}, json.loads(${JSON.stringify(JSON.stringify(g.nets))}))`;
    const code = `import json, importlib.util
spec = importlib.util.spec_from_file_location('impl_v', 'impl.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
json.dumps([[u, v, s] for u, v, s in ${call}])`;
    api.setBusy(true); go.disabled = true; match.className = 'match'; match.textContent = L('运行中…', 'Running…');
    try {
      const { value } = await api.run(code);
      mine = JSON.parse(value).map(([u, v, score]) => ({ u, v, score }));
      ref = metric === 'edge' ? AF.edgeWeight(g) : metric === 'shared' ? AF.sharedNeighbors(g) : AF.pinCount(g).scores;
      const same = (a, b) => a && b && a.u === b.u && a.v === b.v && Math.abs(a.score - b.score) < 1e-9;
      const diff = Math.max(mine.length, ref.length) === 0 ? -1 : [...Array(Math.max(mine.length, ref.length)).keys()].find(i => !same(mine[i], ref[i])) ?? -1;
      match.className = 'match ' + (diff < 0 ? 'ok' : 'no');
      match.textContent = diff < 0
        ? L(`✓ 与课程引擎逐行一致：${ref.length} 对，第一名 ${ref[0] ? `${ref[0].u}–${ref[0].v}@${fmt(ref[0].score)}` : '—'}。`, `✓ Agrees with the course engine on every row: ${ref.length} pairs, first ${ref[0] ? `${ref[0].u}–${ref[0].v}@${fmt(ref[0].score)}` : '—'}.`)
        : !mine[diff]
          ? L(`✗ 你的列表少了：引擎第 ${diff + 1} 名是 ${ref[diff].u}–${ref[diff].v}@${fmt(ref[diff].score)}。是否漏了没有直接连线的对？`, `✗ Your list is short: the engine’s rank ${diff + 1} is ${ref[diff].u}–${ref[diff].v}@${fmt(ref[diff].score)}. Did you skip pairs with no direct wire?`)
          : !ref[diff]
            ? L(`✗ 你的列表多了 ${mine[diff].u}–${mine[diff].v}：只列分数大于 0 的对。`, `✗ Your list has an extra ${mine[diff].u}–${mine[diff].v}: list only pairs with a score above 0.`)
            : L(`✗ 第 ${diff + 1} 名开始不同：你的是 ${mine[diff].u}–${mine[diff].v}@${fmt(mine[diff].score)}，引擎是 ${ref[diff].u}–${ref[diff].v}@${fmt(ref[diff].score)}。`, `✗ Differs from rank ${diff + 1}: yours is ${mine[diff].u}–${mine[diff].v}@${fmt(mine[diff].score)}, the engine’s ${ref[diff].u}–${ref[diff].v}@${fmt(ref[diff].score)}.`);
      gv = new GraphView(stage, { graph: e.kind === 'netlist' ? cliqueGraph(g) : g, positions: e.positions, title: L('你的代码的排名', 'Your code’s ranking'), radius: 24 });
      player.load(mine.length ? mine.map((p, i) => ({ ...p, i })) : [{ u: null, v: null, score: 0, i: 0 }]);
    } catch (err) {
      match.className = 'match no';
      const msg = String(err.message || err).split('\n').filter(Boolean);
      match.textContent = err.reason ? L('已停止。', 'Stopped.') : L('你的代码运行出错：', 'Your code raised an error: ') + msg.slice(-1)[0];
    } finally { api.setBusy(false); go.disabled = false; }
  }
  function show(i, p) {
    if (!gv) return;
    gv.render({ focus: p.u ? [p.u, p.v] : [], highlight: p.u ? [[p.u, p.v]] : [], summary: p.u ? L(`你的第 ${i + 1} 名：${p.u}–${p.v} = ${fmt(p.score)}`, `Your rank ${i + 1}: ${p.u}–${p.v} = ${fmt(p.score)}`) : L('你的函数返回了空列表', 'Your function returned an empty list') });
    metrics(metricBox, [[L('你的对数', 'Your pairs'), mine.length], [L('引擎对数', 'Engine pairs'), ref.length], [L('名次', 'Rank'), p.u ? i + 1 : '—']]);
    const ok = p.u && ref[i] && ref[i].u === p.u && ref[i].v === p.v && Math.abs(ref[i].score - p.score) < 1e-9;
    status(statusBox, ok ? '' : 'cycle', p.u ? (ok ? L('这一行与引擎一致。', 'This row matches the engine.') : L(`这一行与引擎不同：引擎是 ${ref[i] ? `${ref[i].u}–${ref[i].v} = ${fmt(ref[i].score)}` : '（没有这一行）'}。`, `This row differs: the engine has ${ref[i] ? `${ref[i].u}–${ref[i].v} = ${fmt(ref[i].score)}` : '(no such row)'}.`)) : '');
    const n = Math.max(mine.length, ref.length);
    rankBox.replaceChildren(h('table', {}, h('thead', {}, h('tr', {}, h('th', '#'), h('th', L('你的', 'Yours')), h('th', L('引擎', 'Engine')))),
      h('tbody', {}, [...Array(n).keys()].map(k => {
        const a = mine[k], b = ref[k], eq = a && b && a.u === b.u && a.v === b.v && Math.abs(a.score - b.score) < 1e-9;
        return h('tr', { class: k === i ? 'chosen' : '' }, h('td', String(k + 1)), h('td', { style: eq ? '' : 'color:var(--c-red)' }, a ? `${a.u}–${a.v} ${fmt(a.score)}` : '—'), h('td', b ? `${b.u}–${b.v} ${fmt(b.score)}` : '—'));
      }))));
  }
}

bootModule({ moduleId: 'm02-affinity-metrics', display: 'Module 02', challenges, lab, visualize });
