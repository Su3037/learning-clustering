// Module 05 lab: node-by-node label propagation. Every vote comes from engines/lp.js.
import { h, fetchJSON } from '../../assets/core.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as LP from '../../engines/lp.js';
import { G01, requireGraph } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const STATUS = { stable: ['', '稳定：完整一轮零变化。'], cycle: ['cycle', '振荡：标签状态重复出现，不会自己停下。'], limit: ['limit', '达到最大轮数：既不是稳定也未检测到重复。'], running: ['', '进行中'] };

async function lab(root, { pseudo, base }) {
  const film = await fetchJSON(new URL('data/m05-label-propagation/film-graphs.json', base));
  const PRESETS = {
    g01: { name: '课程公共图 G01', graph: G01, positions: G01.positions, bridge: true },
    pair: { name: '两节点（振荡反例）', graph: LP.PRESETS.pair, positions: LP.PRESETS.pair.positions },
    tie: { name: '一票还是两票（加权）', graph: LP.PRESETS.tie, positions: LP.PRESETS.tie.positions },
    island: { name: '孤点与断开的群体', graph: LP.PRESETS.island, positions: LP.PRESETS.island.positions },
    ...(film ? { circuit: { name: '24 单元虚构电路（原作）', graph: film.circuit, positions: film.circuit.positions, big: true } } : {})
  };
  let presetId = 'g01', mode = 'async', tie = 'min', order = null, bridge = 2, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), votesBox = h('div.decision'), playerBox = h('div');
  const traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar'), extra = h('div.lab-toolbar', { style: 'margin-top:12px' });
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, h('div.legend', {},
    h('span', {}, '节点颜色 = 当前标签；节点下方写出标签名'), h('span', {}, h('b', { style: 'background:#d8bb78' }), '金圈：正在更新的节点'),
    h('span', {}, h('i', { style: 'border-color:#db7b72;border-top-style:dashed' }), '两端标签不同的边（计入 cut）'))), side), extra, traceBox, err);
  side.append(metricBox, statusBox, h('h4', '这一票的明细'), votesBox, playerBox);
  let gv;
  const player = new Player(playerBox, { onIndex: show, speed: 900 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: '轮', get: e => e.round }, { label: '节点', get: e => e.node }, { label: '票数', get: e => Object.entries(e.votes).map(([l, v]) => `${l}:${v}`).join(' ') || '（无邻居）' },
    { label: '旧→新', get: e => `${e.old}→${e.label}${e.changed ? ' *' : ''}` }, { label: '状态', get: e => e.kind === 'update-round-end' ? e.status : '' }], onPick: i => player.go(i) });

  const graph = () => {
    const p = PRESETS[presetId], g = requireGraph(p.graph);
    if (p.bridge) g.edges = g.edges.map(e => (e.u === 'C' && e.v === 'D') ? { ...e, w: bridge } : e);
    return { nodes: g.nodes, edges: g.edges };
  };
  function buildToolbar() {
    const p = PRESETS[presetId], ids = graph().nodes.map(n => n.id);
    const orderIn = h('input', { type: 'text', value: (order || [...ids].sort()).join(' '), 'aria-label': '访问顺序', style: 'min-width:220px' });
    orderIn.addEventListener('change', () => { order = orderIn.value.trim().split(/[\s,]+/).filter(Boolean); recompute(); });
    toolbar.replaceChildren(
      select('例子', Object.entries(PRESETS).map(([k, v]) => [k, v.name]), presetId, v => { presetId = v; order = null; bridge = 2; buildToolbar(); recompute(true); }),
      select('更新方式', [['async', '异步（立即写回）'], ['sync', '同步（读旧快照）']], mode, v => { mode = v; recompute(); }),
      select('平票规则', [['min', 'min：取字典序最小'], ['max', 'max：取最大'], ['keep', 'keep：当前标签优先']], tie, v => { tie = v; recompute(); }),
      p.big ? '' : h('label', {}, '访问顺序（空格分隔）', orderIn),
      h('button.btn.small', { type: 'button', onclick: () => { order = [...ids].sort().reverse(); buildToolbar(); recompute(); } }, '反向顺序'),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m05-label-propagation', { preset: presetId, options: { mode, tie, order: run.result?.order, bridge }, input: graph(), result: run.result, events: run.events }) }, '导出运行记录'));
    if (p.bridge) {
      const out = h('output', String(bridge));
      const range = h('input', { type: 'range', min: 1, max: 12, step: 1, value: bridge, 'aria-label': 'C–D 的边权', oninput: () => { out.textContent = range.value; }, onchange: () => { bridge = +range.value; recompute(); } });
      extra.replaceChildren(h('label', { style: 'flex-direction:row;align-items:center;gap:10px' }, 'C–D 的边权（桥）', range, out), h('span.lab-note', '改动后从初始标签重新运行（新的 runId），不在旧结果上继续。'));
    } else extra.replaceChildren();
  }
  function recompute(newGraph = false) {
    const g = graph(), p = PRESETS[presetId];
    run = LP.run(g, { mode, tie, order, maxRounds: 50 });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join('；'); return; }
    err.textContent = '';
    if (newGraph || !gv) gv = new GraphView(stage, { graph: g, positions: p.positions, title: '标签传播实验图', radius: p.big ? 15 : 24 });
    else gv.setGraph(g, p.positions, 760, 500);
    const init = { eventId: 'init', kind: 'init', round: 0, node: null, after: Object.fromEntries(g.nodes.map(n => [n.id, n.id])), votes: {}, metrics: { cut: g.edges.reduce((s, e) => s + e.w, 0) }, status: 'running' };
    const evs = [init, ...run.events];
    trace.load(evs); player.load(evs);
  }
  function show(i, e, evs) {
    const p = PRESETS[presetId], labels = e.after, order0 = graph().nodes.map(n => n.id).sort();
    gv.render({ groups: labels, groupOrder: order0, cut: true, focus: e.node ? [e.node] : [], tags: p.big ? undefined : Object.fromEntries(Object.entries(labels).map(([n, l]) => [n, `标签 ${l}`])),
      summary: e.node ? `第 ${e.round} 轮，${e.node} 的标签 ${e.old} → ${e.label}` : '初始：每个节点的标签就是自己的名字' });
    metrics(metricBox, [['轮', e.round], ['组数', new Set(Object.values(labels)).size], ['cut', e.metrics.cut]]);
    if (!e.node) { status(statusBox, '', '初始：标签 = 名字。'); votesBox.replaceChildren(h('p.muted', '点“下一步”更新第一个节点。')); pseudo.lp?.show([1], ''); return; }
    const st = e.status && e.status !== 'running' ? STATUS[e.status] : null;
    status(statusBox, st ? st[0] : '', st ? `第 ${e.round} 轮结束（本轮改变 ${e.changes} 个）。${st[1]}` : `${e.node}：${e.changed ? `${e.old} → ${e.label}` : `保持 ${e.old}`}${mode === 'sync' && !e.committed ? '（同步：先记下，轮末提交）' : ''}${e.kind === 'update-round-end' ? `。第 ${e.round} 轮结束，本轮改变 ${e.changes} 个，继续。` : ''}`);
    const entries = Object.entries(e.votes).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1));
    const max = Math.max(1, ...entries.map(x => x[1]));
    votesBox.replaceChildren(
      entries.length ? h('table', {}, h('tbody', {}, entries.map(([l, v]) => h('tr', { class: l === e.label ? 'chosen' : '' },
        h('td', `标签 ${l}`), h('td', { style: 'width:45%' }, h('span', { style: `display:inline-block;height:9px;border-radius:2px;background:${l === e.label ? 'var(--c-gold)' : 'var(--c-teal)'};width:${100 * v / max}%` })),
        h('td', String(v)), h('td', e.neighbors.filter(nb => nb.label === l).map(nb => `${nb.node}:${nb.weight}`).join('+')))))) : h('p', '没有邻居：保留原标签。'),
      e.tied.length > 1 ? h('p.lab-note', `平票：${e.tied.join('、')}；规则 ${tie} 选 ${e.label}。`) : '',
      h('p.lab-note', mode === 'sync' ? `同步：${e.node} 读的是本轮开始时的旧快照。` : `异步：${e.node} 读到的是此刻最新的标签。`));
    pseudo.lp?.show(e.kind === 'update-round-end' ? (mode === 'sync' ? [8, 9, 10] : [9, 10]) : (mode === 'sync' ? [3, 5, 6, 7] : [4, 5, 6, 7]), `${e.node}：${entries.map(([l, v]) => `${l}=${v}`).join('，')}`);
  }
  buildToolbar(); recompute(true);
}

bootModule({ moduleId: 'm05-label-propagation', display: 'Module 05', challenges, lab });
