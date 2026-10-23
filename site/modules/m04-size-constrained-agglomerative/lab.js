// Module 04 lab: greedy merging with a hard capacity, plus a lower-bound and exhaustive diagnosis.
import { h } from '../../assets/core.js';
import { GraphView, PALETTE } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as M from '../../engines/merge.js';
import { G01, requireGraph } from '../../engines/graph.js';
import { challenges } from './challenges.js';


const PRESETS = {
  g01: { name: '课程公共图 G01（大小均为 1）', graph: G01, positions: G01.positions, k: 2, capacity: 2 },
  trap: { name: 'greedy_trap（原作者 GateUltra）', graph: M.M04_GRAPHS.greedy_trap, positions: M.M04_GRAPHS.greedy_trap.positions, k: 2, capacity: 3 },
  sub: { name: 'suboptimal（原作者 GateUltra）', graph: M.M04_GRAPHS.suboptimal, positions: M.M04_GRAPHS.suboptimal.positions, k: 2, capacity: 2 }
};
const KIND = { 'infeasible-by-bound': ['blocked', '目标不可能：下界已超过 K。任何算法都做不到，贪心停下不是错误。'],
  'infeasible-by-search': ['blocked', '目标不可能：穷举也找不到恰好 K 簇的合法划分。'],
  'greedy-stuck': ['cycle', '总体可行，但贪心卡住：存在合法的 K 簇分组，贪心因早期选择而无法到达。'],
  'feasible-suboptimal': ['limit', '达到 K 且合法，但不是最优：穷举找到更小的 cut。'],
  'reached-and-optimal-here': ['', '达到 K 且合法；在这张小图上与穷举最优相同（不代表一般最优）。'] };
const STOP = { 'target-reached': '达到 K', 'capacity-blocked': '剩下的正亲和度对全部超容量', 'no-positive-affinity': '剩下的簇之间没有边' };

async function lab(root, { pseudo }) {
  let presetId = 'g01', k = 2, capacity = 2, sizes = {}, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), decision = h('div.decision'), playerBox = h('div');
  const diagBox = h('div.decision'), traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, h('div.legend', {},
    h('span', {}, h('b', { style: 'background:#db7b72' }), '红圈：超容量被阻止'), h('span', {}, h('b', { style: 'background:#d8bb78' }), '金圈：本步合并'),
    h('span', {}, '节点下方：大小 s(v)'))), side), h('div.lab-side', { style: 'border:1px solid var(--c-line);border-radius:10px;margin-top:14px' }, h('h4', { style: 'margin-top:0' }, '诊断：是不可能、卡住，还是不最优？'), diagBox), traceBox, err);
  side.append(metricBox, statusBox, h('h4', '本步的全部候选'), decision, playerBox);
  let gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: '容量约束实验图' });
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: '步', get: e => e.step }, { label: '动作', get: e => e.kind === 'merge' ? `合并 ${e.decision.a}+${e.decision.b}（大小 ${e.decision.size}）` : e.kind === 'stopped' ? '停止' : '单点簇' },
    { label: '被阻止', get: e => (e.kind === 'stopped' ? e.candidates : e.blocked || []).filter(c => !c.legal).map(c => `${c.a}+${c.b}`).join(' ') }, { label: 'cut', get: e => e.metrics.cut }], onPick: i => player.go(i) });

  const graph = () => { const g = requireGraph(PRESETS[presetId].graph); return { nodes: g.nodes.map(n => ({ id: n.id, size: sizes[n.id] ?? n.size })), edges: g.edges }; };
  function buildToolbar() {
    const g = graph();
    const nodeSel = h('select', { 'aria-label': '选择节点' }, g.nodes.map(n => h('option', { value: n.id }, n.id)));
    const sIn = h('input', { type: 'number', min: 1, max: 9, step: 1, 'aria-label': '节点大小' });
    const sync = () => { sIn.value = graph().nodes.find(n => n.id === nodeSel.value).size; };
    nodeSel.addEventListener('change', sync); sync();
    sIn.addEventListener('change', () => { const v = Number(sIn.value); if (!(Number.isInteger(v) && v >= 1 && v <= 9)) { err.textContent = '节点大小为 1–9 的整数。'; return; } err.textContent = ''; sizes[nodeSel.value] = v; recompute(); });
    toolbar.replaceChildren(
      select('例子', Object.entries(PRESETS).map(([key, p]) => [key, p.name]), presetId, v => { presetId = v; sizes = {}; k = PRESETS[v].k; capacity = PRESETS[v].capacity; buildToolbar(); recompute(true); }),
      select('目标 K', [1, 2, 3, 4].map(x => [String(x), String(x)]), String(k), v => { k = +v; recompute(); }),
      select('容量 C', [['', '不限'], ...[2, 3, 4, 5, 6].map(x => [String(x), String(x)])], capacity ? String(capacity) : '', v => { capacity = v ? +v : null; recompute(); }),
      h('label', {}, '节点', nodeSel), h('label', {}, '大小 s(v)', sIn),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m04-size-constrained-agglomerative', { preset: presetId, options: { k, capacity }, input: graph(), result: run.result, events: run.events, diagnosis: diag }) }, '导出运行记录'));
  }
  let diag = null;
  function recompute(newGraph = false) {
    const g = graph();
    if (newGraph) gv = new GraphView(stage, { graph: g, positions: PRESETS[presetId].positions, title: '容量约束实验图' });
    run = M.run(g, { k, capacity });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join('；'); diagBox.replaceChildren(h('p', '输入不合法：没有任何合法分组。')); trace.load([]); return; }
    err.textContent = '';
    diag = M.diagnose(g, { k, capacity });
    const o = diag.oracle, [cls, text] = KIND[diag.kind];
    diagBox.replaceChildren(h('div', { class: 'status ' + cls }, text), h('table', {}, h('tbody', {},
      h('tr', {}, h('th', '下界 ⌈Σs / C⌉'), h('td', capacity ? `⌈${g.nodes.reduce((s, n) => s + n.size, 0)} / ${capacity}⌉ = ${o.lowerBoundClusters}` : '不限容量：1')),
      h('tr', {}, h('th', '穷举：最少合法簇数'), h('td', String(o.minFeasibleClusters))),
      h('tr', {}, h('th', `穷举：恰好 ${k} 簇的最小 cut`), h('td', o.bestCutAtK ? `${o.bestCutAtK.cut}（${o.bestCutAtK.clusters.map(c => c.join('')).join(' | ')}）` : '不存在')),
      h('tr', {}, h('th', '贪心结果'), h('td', `${run.result.labels.join(' | ')}，cut ${run.result.cut}，${run.result.count} 簇`)))),
      h('p.lab-note', `穷举检查了 ${o.legalPartitions} 个合法划分；只用于 ≤ 10 个节点的教学图。`));
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const g = graph(), size = Object.fromEntries(g.nodes.map(n => [n.id, n.size]));
    const groups = {}, hulls = [];
    e.after.forEach((c, gi) => { c.members.forEach(m => { groups[m] = c.label; }); if (c.members.length > 1) hulls.push({ members: c.members, label: `${c.label} · ${c.size}/${capacity ?? '∞'}`, color: PALETTE[gi % PALETTE.length] }); });
    const inside = g.edges.filter(x => groups[x.u] === groups[x.v]).map(x => [x.u, x.v]);
    const blockedList = (e.kind === 'stopped' ? e.candidates : e.blocked || []).filter(c => !c.legal);
    const focus = e.kind === 'merge' ? [...e.before.find(c => c.label === e.decision.a).members, ...e.before.find(c => c.label === e.decision.b).members] : [];
    gv.render({ groups, cut: true, inside, hulls, focus, blocked: [...new Set(blockedList.flatMap(c => [...c.a, ...c.b]))], tags: Object.fromEntries(Object.entries(size).map(([n, s]) => [n, `s=${s}`])), groupOrder: e.after.map(c => c.label), summary: `第 ${e.step} 步：${e.after.map(c => c.label).join(' | ')}` });
    const r = run.result, last = i === run.events.length - 1;
    metrics(metricBox, [['簇数', e.after.length], ['cut', e.metrics.cut], ['K / C', `${k} / ${capacity ?? '∞'}`]]);
    if (e.kind === 'merge') status(statusBox, '', `合并 ${e.decision.a}+${e.decision.b}：大小 ${e.decision.size}${capacity ? ` ≤ ${capacity}` : ''}，亲和度 ${e.decision.affinity}。${blockedList.length ? `之前的 ${blockedList.map(c => `${c.a}+${c.b}`).join('、')} 因超容量被跳过。` : ''}`);
    else if (e.kind === 'stopped') status(statusBox, 'blocked', `停止：${STOP[e.decision]}。`);
    else status(statusBox, '', '开始：每个节点一个簇。');
    if (last) status(statusBox, r.targetReached ? '' : 'blocked', `报告：${r.count} 簇；容量${r.capacityCompliant ? '满足' : '违反'}；${r.targetReached ? '达到' : '未达到'} K = ${k}；停止原因：${STOP[r.stopReason]}。`);
    const cands = e.candidates || [];
    decision.replaceChildren(cands.length ? h('table', {}, h('thead', {}, h('tr', {}, h('th', '簇对'), h('th', '亲和度'), h('th', '大小'), h('th', ''))),
      h('tbody', {}, cands.map(c => { const chosen = e.kind === 'merge' && c.a === e.decision.a && c.b === e.decision.b;
        return h('tr', { class: chosen ? 'chosen' : !c.legal ? 'blocked' : '' }, h('td', `${c.a}–${c.b}`), h('td', String(c.affinity)), h('td', `${c.size}${capacity ? '/' + capacity : ''}`), h('td', chosen ? '选中' : !c.legal ? '超容量' : '')); }))) : h('p.muted', '初始状态。'));
    pseudo.capacity?.show(e.kind === 'singletons' ? [1] : e.kind === 'stopped' ? [4, 5, 7, 8] : last ? [6, 2, 7, 8] : [3, 4, 6], '');
  }
  buildToolbar(); recompute(true);
}

bootModule({ moduleId: 'm04-size-constrained-agglomerative', display: 'Module 04', challenges, lab });
