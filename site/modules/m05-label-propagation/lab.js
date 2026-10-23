// Module 05 lab: node-by-node label propagation. Every vote comes from engines/lp.js.
import { h, fetchJSON, L } from '../../assets/core.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as LP from '../../engines/lp.js';
import { G01, requireGraph } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const STATUS = { stable: ['', L('稳定：完整一轮零变化。', 'Stable: a full round with zero changes.')], cycle: ['cycle', L('振荡：标签状态重复出现，不会自己停下。', 'Cycle: a label state repeats, so it will never stop on its own.')], limit: ['limit', L('达到最大轮数：既不是稳定也未检测到重复。', 'Round limit reached: neither stable nor a detected repeat.')], running: ['', L('进行中', 'running')] };

async function lab(root, { pseudo, base }) {
  const film = await fetchJSON(new URL('data/m05-label-propagation/film-graphs.json', base));
  const PRESETS = {
    g01: { name: L('课程公共图 G01', 'Course graph G01'), graph: G01, positions: G01.positions, bridge: true },
    pair: { name: L('两节点（振荡反例）', 'Two nodes (cycle counterexample)'), graph: LP.PRESETS.pair, positions: LP.PRESETS.pair.positions },
    tie: { name: L('一票还是两票（加权）', 'One vote or two (weighted)'), graph: LP.PRESETS.tie, positions: LP.PRESETS.tie.positions },
    island: { name: L('孤点与断开的群体', 'Isolated node and separate groups'), graph: LP.PRESETS.island, positions: LP.PRESETS.island.positions },
    ...(film ? { circuit: { name: L('24 单元虚构电路（原作）', '24-cell fictional circuit (original)'), graph: film.circuit, positions: film.circuit.positions, big: true } } : {})
  };
  let presetId = 'g01', mode = 'async', tie = 'min', order = null, bridge = 2, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), votesBox = h('div.decision'), playerBox = h('div');
  const traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar'), extra = h('div.lab-toolbar', { style: 'margin-top:12px' });
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, h('div.legend', {},
    h('span', {}, L('节点颜色 = 当前标签；节点下方写出标签名', 'Node colour = current label; the label is written under each node')), h('span', {}, h('b', { style: 'background:#d8bb78' }), L('金圈：正在更新的节点', 'Gold ring: the node being updated')),
    h('span', {}, h('i', { style: 'border-color:#db7b72;border-top-style:dashed' }), L('两端标签不同的边（计入 cut）', 'Edges whose ends carry different labels (counted in the cut)')))), side), extra, traceBox, err);
  side.append(metricBox, statusBox, h('h4', L('这一票的明细', 'This vote in detail')), votesBox, playerBox);
  let gv;
  const player = new Player(playerBox, { onIndex: show, speed: 900 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: L('轮', 'Round'), get: e => e.round }, { label: L('节点', 'Node'), get: e => e.node }, { label: L('票数', 'Votes'), get: e => Object.entries(e.votes).map(([l, v]) => `${l}:${v}`).join(' ') || L('（无邻居）', '(no neighbours)') },
    { label: L('旧→新', 'Old→new'), get: e => `${e.old}→${e.label}${e.changed ? ' *' : ''}` }, { label: L('状态', 'Status'), get: e => e.kind === 'update-round-end' ? e.status : '' }], onPick: i => player.go(i) });

  const graph = () => {
    const p = PRESETS[presetId], g = requireGraph(p.graph);
    if (p.bridge) g.edges = g.edges.map(e => (e.u === 'C' && e.v === 'D') ? { ...e, w: bridge } : e);
    return { nodes: g.nodes, edges: g.edges };
  };
  function buildToolbar() {
    const p = PRESETS[presetId], ids = graph().nodes.map(n => n.id);
    const orderIn = h('input', { type: 'text', value: (order || [...ids].sort()).join(' '), 'aria-label': L('访问顺序', 'Visiting order'), style: 'min-width:220px' });
    orderIn.addEventListener('change', () => { order = orderIn.value.trim().split(/[\s,]+/).filter(Boolean); recompute(); });
    toolbar.replaceChildren(
      select(L('例子', 'Example'), Object.entries(PRESETS).map(([k, v]) => [k, v.name]), presetId, v => { presetId = v; order = null; bridge = 2; buildToolbar(); recompute(true); }),
      select(L('更新方式', 'Update mode'), [['async', L('异步（立即写回）', 'Asynchronous (write back now)')], ['sync', L('同步（读旧快照）', 'Synchronous (read the old snapshot)')]], mode, v => { mode = v; recompute(); }),
      select(L('平票规则', 'Tie rule'), [['min', L('min：取字典序最小', 'min: smallest name')], ['max', L('max：取最大', 'max: largest name')], ['keep', L('keep：当前标签优先', 'keep: current label first')]], tie, v => { tie = v; recompute(); }),
      p.big ? '' : h('label', {}, L('访问顺序（空格分隔）', 'Visiting order (space-separated)'), orderIn),
      h('button.btn.small', { type: 'button', onclick: () => { order = [...ids].sort().reverse(); buildToolbar(); recompute(); } }, L('反向顺序', 'Reverse order')),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m05-label-propagation', { preset: presetId, options: { mode, tie, order: run.result?.order, bridge }, input: graph(), result: run.result, events: run.events }) }, L('导出运行记录', 'Export this run')));
    if (p.bridge) {
      const out = h('output', String(bridge));
      const range = h('input', { type: 'range', min: 1, max: 12, step: 1, value: bridge, 'aria-label': L('C–D 的边权', 'Weight of C–D'), oninput: () => { out.textContent = range.value; }, onchange: () => { bridge = +range.value; recompute(); } });
      extra.replaceChildren(h('label', { style: 'flex-direction:row;align-items:center;gap:10px' }, L('C–D 的边权（桥）', 'Weight of C–D (the bridge)'), range, out), h('span.lab-note', L('改动后从初始标签重新运行（新的 runId），不在旧结果上继续。', 'A change restarts from the initial labels (a new run), never continuing from the old result.')));
    } else extra.replaceChildren();
  }
  function recompute(newGraph = false) {
    const g = graph(), p = PRESETS[presetId];
    run = LP.run(g, { mode, tie, order, maxRounds: 50 });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join(L('；', '; ')); return; }
    err.textContent = '';
    if (newGraph || !gv) gv = new GraphView(stage, { graph: g, positions: p.positions, title: L('标签传播实验图', 'Label propagation lab graph'), radius: p.big ? 15 : 24 });
    else gv.setGraph(g, p.positions, 760, 500);
    const init = { eventId: 'init', kind: 'init', round: 0, node: null, after: Object.fromEntries(g.nodes.map(n => [n.id, n.id])), votes: {}, metrics: { cut: g.edges.reduce((s, e) => s + e.w, 0) }, status: 'running' };
    const evs = [init, ...run.events];
    trace.load(evs); player.load(evs);
  }
  function show(i, e, evs) {
    const p = PRESETS[presetId], labels = e.after, order0 = graph().nodes.map(n => n.id).sort();
    gv.render({ groups: labels, groupOrder: order0, cut: true, focus: e.node ? [e.node] : [], tags: p.big ? undefined : Object.fromEntries(Object.entries(labels).map(([n, l]) => [n, L(`标签 ${l}`, `label ${l}`)])),
      summary: e.node ? L(`第 ${e.round} 轮，${e.node} 的标签 ${e.old} → ${e.label}`, `Round ${e.round}: ${e.node}’s label ${e.old} → ${e.label}`) : L('初始：每个节点的标签就是自己的名字', 'Start: every node’s label is its own name') });
    metrics(metricBox, [[L('轮', 'Round'), e.round], [L('组数', 'Groups'), new Set(Object.values(labels)).size], ['cut', e.metrics.cut]]);
    if (!e.node) { status(statusBox, '', L('初始：标签 = 名字。', 'Start: label = name.')); votesBox.replaceChildren(h('p.muted', L('点“下一步”更新第一个节点。', 'Press “Step” to update the first node.'))); pseudo.lp?.show([1], ''); return; }
    const st = e.status && e.status !== 'running' ? STATUS[e.status] : null;
    status(statusBox, st ? st[0] : '', st ? L(`第 ${e.round} 轮结束（本轮改变 ${e.changes} 个）。${st[1]}`, `End of round ${e.round} (${e.changes} changed). ${st[1]}`) : L(`${e.node}：${e.changed ? `${e.old} → ${e.label}` : `保持 ${e.old}`}${mode === 'sync' && !e.committed ? '（同步：先记下，轮末提交）' : ''}${e.kind === 'update-round-end' ? `。第 ${e.round} 轮结束，本轮改变 ${e.changes} 个，继续。` : ''}`, `${e.node}: ${e.changed ? `${e.old} → ${e.label}` : `keeps ${e.old}`}${mode === 'sync' && !e.committed ? ' (synchronous: noted now, committed at the end of the round)' : ''}${e.kind === 'update-round-end' ? `. End of round ${e.round}, ${e.changes} changed, continue.` : ''}`));
    const entries = Object.entries(e.votes).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1));
    const max = Math.max(1, ...entries.map(x => x[1]));
    votesBox.replaceChildren(
      entries.length ? h('table', {}, h('tbody', {}, entries.map(([l, v]) => h('tr', { class: l === e.label ? 'chosen' : '' },
        h('td', L(`标签 ${l}`, `label ${l}`)), h('td', { style: 'width:45%' }, h('span', { style: `display:inline-block;height:9px;border-radius:2px;background:${l === e.label ? 'var(--c-gold)' : 'var(--c-teal)'};width:${100 * v / max}%` })),
        h('td', String(v)), h('td', e.neighbors.filter(nb => nb.label === l).map(nb => `${nb.node}:${nb.weight}`).join('+')))))) : h('p', L('没有邻居：保留原标签。', 'No neighbours: keeps its label.')),
      e.tied.length > 1 ? h('p.lab-note', L(`平票：${e.tied.join('、')}；规则 ${tie} 选 ${e.label}。`, `Tie: ${e.tied.join(', ')}; rule ${tie} picks ${e.label}.`)) : '',
      h('p.lab-note', mode === 'sync' ? L(`同步：${e.node} 读的是本轮开始时的旧快照。`, `Synchronous: ${e.node} reads the old snapshot from the start of the round.`) : L(`异步：${e.node} 读到的是此刻最新的标签。`, `Asynchronous: ${e.node} reads the labels as they are right now.`)));
    pseudo.lp?.show(e.kind === 'update-round-end' ? (mode === 'sync' ? [8, 9, 10] : [9, 10]) : (mode === 'sync' ? [3, 5, 6, 7] : [4, 5, 6, 7]), `${e.node}${L('：', ': ')}${entries.map(([l, v]) => `${l}=${v}`).join(L('，', ', '))}`);
  }
  buildToolbar(); recompute(true);
}

/* ---------- code lab: run the learner's own solve() and compare it with the course engine, step by step ---------- */
function visualize(root, api) {
  const EXAMPLES = {
    g01: { name: L('课程公共图 G01', 'Course graph G01'), graph: G01, positions: G01.positions },
    pair: { name: L('两节点（试试同步）', 'Two nodes (try synchronous)'), graph: LP.PRESETS.pair, positions: LP.PRESETS.pair.positions },
    tie: { name: L('一票还是两票（加权）', 'One vote or two (weighted)'), graph: LP.PRESETS.tie, positions: LP.PRESETS.tie.positions },
    island: { name: L('孤点与断开的群体', 'Isolated node and separate groups'), graph: LP.PRESETS.island, positions: LP.PRESETS.island.positions }
  };
  let ex = 'g01', mode = 'async', tie = 'min';
  const stage = h('div.lab-stage'), side = h('div.lab-side'), metricBox = h('div.metrics'), statusBox = h('div.status'), votesBox = h('div.decision'), playerBox = h('div');
  const match = h('p.match'), toolbar = h('div.lab-toolbar');
  const go = h('button.btn.primary', { type: 'button', onclick: runMine }, L('▶ 用我的 solve() 运行', '▶ Run my solve()'));
  toolbar.append(
    select(L('例子', 'Example'), Object.entries(EXAMPLES).map(([k, v]) => [k, v.name]), ex, v => { ex = v; }),
    select(L('更新方式', 'Update mode'), [['async', 'async'], ['sync', 'sync']], mode, v => { mode = v; }),
    select(L('平票规则', 'Tie rule'), [['min', 'min'], ['max', 'max'], ['keep', 'keep']], tie, v => { tie = v; }), go);
  side.append(metricBox, statusBox, h('h4', L('你的代码算出的这一票', 'This vote, from your code')), votesBox, playerBox);
  root.append(h('h3', L('用你的代码跑一遍', 'Watch your own code run')),
    h('p.muted', L('这里调用的是你在上面写的 solve()，不是课程引擎。每一步的票数和标签都来自你的代码；右边同时告诉你它和课程引擎是否一致。',
      'This calls the solve() you wrote above, not the course engine. Every vote and label below comes from your code, and the panel tells you whether it agrees with the course engine.')),
    toolbar, h('div.lab', {}, h('div', {}, stage), side), match);
  let gv;
  const player = new Player(playerBox, { onIndex: show, speed: 900 });
  stage.append(h('p.muted', { style: 'padding:40px 10px;text-align:center' }, L('写好 count_votes 和停止判定后，按“用我的 solve() 运行”。', 'Once count_votes and the stopping test are written, press “Run my solve()”.')));

  async function runMine() {
    if (api.busy) return;
    const e = EXAMPLES[ex], g = requireGraph(e.graph);
    const nodes = g.nodes.map(n => n.id), edges = g.edges.map(x => [x.u, x.v, x.w]);
    const code = `import json, importlib.util
spec = importlib.util.spec_from_file_location('impl_v', 'impl.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
r = m.solve(${JSON.stringify(nodes)}, [tuple(e) for e in ${JSON.stringify(edges)}], mode=${JSON.stringify(mode)}, tie=${JSON.stringify(tie)})
json.dumps({k: r[k] for k in ('labels', 'rounds', 'status', 'cut', 'events')})`;
    api.setBusy(true); go.disabled = true; match.className = 'match'; match.textContent = L('运行中…', 'Running…');
    try {
      const { value } = await api.run(code);
      const mine = JSON.parse(value), ref = LP.run(g, { mode, tie, maxRounds: 50 });
      // Rebuild what the graph shows after each of the learner's events (sync commits at the end of a round).
      let labels = Object.fromEntries(nodes.map(n => [n, n])), pending = { ...labels };
      const evs = [{ round: 0, node: null, after: { ...labels }, votes: {} }];
      mine.events.forEach((x, i) => {
        pending[x.node] = x.label;
        const roundEnd = i === mine.events.length - 1 || mine.events[i + 1].round !== x.round;
        if (mode === 'async' || roundEnd) labels = { ...pending };
        evs.push({ ...x, after: { ...labels }, roundEnd });
      });
      evs.at(-1).final = true;
      const diff = mine.events.findIndex((x, i) => !ref.events[i] || ref.events[i].node !== x.node || ref.events[i].label !== x.label);
      const same = diff < 0 && mine.events.length === ref.events.length && mine.status === ref.status && mine.rounds === ref.result.rounds && mine.cut === ref.result.cut;
      match.className = 'match ' + (same ? 'ok' : 'no');
      match.textContent = same
        ? L(`✓ 与课程引擎逐步一致：${mine.rounds} 轮，${mine.status}，cut ${mine.cut}。`, `✓ Agrees with the course engine at every step: ${mine.rounds} rounds, ${mine.status}, cut ${mine.cut}.`)
        : diff >= 0
          ? L(`✗ 第 ${diff + 1} 步开始不同：你的代码让 ${mine.events[diff].node} 选 ${mine.events[diff].label}，引擎选 ${ref.events[diff]?.label ?? '（已停止）'}。`, `✗ Differs from step ${diff + 1}: your code has ${mine.events[diff].node} pick ${mine.events[diff].label}; the engine picks ${ref.events[diff]?.label ?? '(already stopped)'}.`)
          : L(`✗ 每一步的选择相同，但结果不同：你的代码 ${mine.rounds} 轮、${mine.status}；引擎 ${ref.result.rounds} 轮、${ref.status}。检查停止判定。`, `✗ Every choice matches, but the outcome differs: your code gives ${mine.rounds} rounds, ${mine.status}; the engine ${ref.result.rounds} rounds, ${ref.status}. Check the stopping test.`);
      gv = new GraphView(stage, { graph: g, positions: e.positions, title: L('你的 solve() 的运行', 'Your solve() run'), radius: 24 });
      player.load(evs);
      show.final = mine;
    } catch (err) {
      match.className = 'match no';
      const msg = String(err.message || err).split('\n').filter(Boolean);
      match.textContent = err.reason ? L('已停止。', 'Stopped.') : L('你的代码运行出错：', 'Your code raised an error: ') + msg.slice(-1)[0];
    } finally { api.setBusy(false); go.disabled = false; }
  }
  function show(i, e) {
    const order0 = Object.keys(e.after).sort();
    gv.render({ groups: e.after, groupOrder: order0, cut: true, focus: e.node ? [e.node] : [], tags: Object.fromEntries(Object.entries(e.after).map(([n, l]) => [n, L(`标签 ${l}`, `label ${l}`)])),
      summary: e.node ? L(`第 ${e.round} 轮，${e.node}：${e.old} → ${e.label}`, `Round ${e.round}, ${e.node}: ${e.old} → ${e.label}`) : L('初始', 'Start') });
    const groups = new Set(Object.values(e.after)).size;
    metrics(metricBox, [[L('轮', 'Round'), e.round], [L('组数', 'Groups'), groups], [L('步', 'Step'), i]]);
    if (!e.node) { status(statusBox, '', L('初始：标签 = 名字。按“下一步”看你的代码怎么投票。', 'Start: label = name. Press “Step” to see how your code votes.')); votesBox.replaceChildren(); return; }
    const fin = e.final && show.final;
    status(statusBox, fin && fin.status !== 'stable' ? 'cycle' : '', fin ? L(`你的 solve() 返回：${fin.status}，${fin.rounds} 轮，cut ${fin.cut}。`, `Your solve() returned: ${fin.status}, ${fin.rounds} rounds, cut ${fin.cut}.`)
      : `${e.node}${L('：', ': ')}${e.old === e.label ? L(`保持 ${e.old}`, `keeps ${e.old}`) : `${e.old} → ${e.label}`}`);
    const entries = Object.entries(e.votes || {}).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1));
    const max = Math.max(1, ...entries.map(x => x[1]));
    votesBox.replaceChildren(entries.length ? h('table', {}, h('tbody', {}, entries.map(([l, v]) => h('tr', { class: l === e.label ? 'chosen' : '' },
      h('td', L(`标签 ${l}`, `label ${l}`)), h('td', { style: 'width:50%' }, h('span', { style: `display:inline-block;height:9px;border-radius:2px;background:${l === e.label ? 'var(--c-gold)' : 'var(--c-teal)'};width:${100 * v / max}%` })), h('td', String(v))))))
      : h('p', L('没有票：保留原标签。', 'No votes: keeps its label.')));
  }
}

bootModule({ moduleId: 'm05-label-propagation', display: 'Module 05', challenges, lab, visualize });
