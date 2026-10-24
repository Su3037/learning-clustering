// Module 09 lab: (A) path-delay evaluation on a chain; (B) RW labelling and reconstruction with replicated
// instances on the candidate DAG. Every number comes from engines/rw.js.
import { h } from '../../assets/core.js';
import { L } from '../../assets/i18n.js';
import { GraphView, PALETTE } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as RW from '../../engines/rw.js';
import { challenges, NO_REPLICATION_BEST } from './challenges.js';

function chainLab(root) {
  const ids = RW.CHAIN.nodes, cuts = [false, true, false];
  let D = 3;
  const out = h('div'), info = h('div.status');
  const toggleText = i => `${ids[i]}→${ids[i + 1]}${L('：', ': ')}${cuts[i] ? L('跨簇', 'across') : L('同簇', 'same cluster')}`;
  const draw = () => {
    const groups = [[]];
    ids.forEach((n, i) => { groups.at(-1).push(n); if (i < cuts.length && cuts[i]) groups.push([]); });
    const ev = RW.evaluatePartition({ ...RW.CHAIN, D }, groups);
    const W = 760, Hh = 170, x = i => 90 + i * 190;
    const svg = h('svg', { viewBox: `0 0 ${W} ${Hh}`, class: 'gv', role: 'img', 'aria-label': L(`链 ${groups.map(g => g.join('')).join(' | ')}，延迟 ${ev.ok ? ev.maxDelay : '不合法'}`, `Chain ${groups.map(g => g.join('')).join(' | ')}, delay ${ev.ok ? ev.maxDelay : 'not valid'}`) },
      h('defs', {}, h('marker', { id: 'arr9', viewBox: '0 0 10 10', refX: '9', refY: '5', markerWidth: '7', markerHeight: '7', orient: 'auto' }, h('path', { d: 'M0 0 L10 5 L0 10 z', fill: '#8aa7a6' }))));
    let gi = 0, start = 0;
    ids.forEach((n, i) => { if (i === ids.length - 1 || cuts[i]) { const x0 = x(start) - 52, x1 = x(i) + 52; svg.append(h('rect', { x: x0, y: 30, width: x1 - x0, height: 100, rx: 22, fill: PALETTE[gi % 8], 'fill-opacity': '.14', stroke: PALETTE[gi % 8], 'stroke-dasharray': '6 4' })); gi++; start = i + 1; } });
    ids.forEach((n, i) => {
      if (i < ids.length - 1) svg.append(h('line', { x1: x(i) + 26, y1: 80, x2: x(i + 1) - 30, y2: 80, stroke: cuts[i] ? '#db7b72' : '#9fc9bf', 'stroke-width': 3, 'stroke-dasharray': cuts[i] ? '7 5' : null, 'marker-end': 'url(#arr9)' }),
        h('text', { x: (x(i) + x(i + 1)) / 2, y: 64, 'text-anchor': 'middle', class: 'w' }, cuts[i] ? `+${D}` : '+0'));
      svg.append(h('g', { class: 'node', transform: `translate(${x(i)} 80)` }, h('circle', { r: 24, fill: '#a9bdb8' }), h('text', { 'text-anchor': 'middle', y: 6 }, n)),
        h('text', { x: x(i), y: 158, 'text-anchor': 'middle', class: 'side-label' }, ev.ok ? L(`到达 ${ev.arrival[n]}`, `arrives ${ev.arrival[n]}`) : ''));
    });
    out.replaceChildren(svg);
    info.className = 'status ' + (ev.ok ? '' : 'invalid');
    info.textContent = ev.ok ? L(`${groups.map(g => `{${g.join(',')}}`).join(' | ')}：4 个节点延迟 + ${ev.crossings} 次跨界 × ${D} = ${ev.maxDelay}`, `${groups.map(g => `{${g.join(',')}}`).join(' | ')}: 4 node delays + ${ev.crossings} crossing${ev.crossings === 1 ? '' : 's'} × ${D} = ${ev.maxDelay}`) : L(`不合法：${ev.errors.join('；')}`, `Not valid: ${ev.errors.join('; ')}`);
  };
  const toggles = h('div.lab-toolbar', { style: 'align-items:center' }, cuts.map((_, i) => h('button.btn.small', { type: 'button', 'aria-pressed': String(cuts[i]), onclick: ev => { cuts[i] = !cuts[i]; ev.currentTarget.setAttribute('aria-pressed', cuts[i]); ev.currentTarget.textContent = toggleText(i); draw(); } }, toggleText(i))),
    select(L('跨簇延迟 D', 'Inter-cluster delay D'), [1, 2, 3, 4, 5].map(v => [String(v), String(v)]), '3', v => { D = +v; draw(); }));
  root.replaceChildren(h('h3', { style: 'color:var(--c-gold);margin-top:0' }, L('A · 一条路径的延迟（每个节点 δ = 1，容量 2）', 'A · The delay of one path (each node δ = 1, capacity 2)')), toggles, out, info);
  draw();
}

function instanceView(result, D, upto, cap) {
  const clusters = result.selected.slice(0, upto);
  const W = 760, colW = W / Math.max(4, Math.ceil(clusters.length / 2)), rowH = 210;
  const svg = h('svg', { viewBox: `0 0 ${W} ${rowH * 2 + 20}`, class: 'gv', role: 'img', 'aria-label': L(`已恢复 ${clusters.length} 个簇`, `${clusters.length} clusters recovered`) });
  const pos = {};
  clusters.forEach((root, ci) => {
    const members = result.clusters[root], col = ci % Math.ceil(Math.max(4, clusters.length) / 2), row = Math.floor(ci / Math.ceil(Math.max(4, clusters.length) / 2));
    const x0 = 8 + col * colW, y0 = 14 + row * rowH, cw = colW - 16;
    svg.append(h('rect', { x: x0, y: y0, width: cw, height: rowH - 24, rx: 12, fill: PALETTE[ci % 8], 'fill-opacity': '.1', stroke: PALETTE[ci % 8], 'stroke-dasharray': '5 4' }),
      h('text', { x: x0 + 8, y: y0 + 18, class: 'side-label', style: 'font-size:12px' }, L(`簇根 ${root}（${members.length}/${cap}）`, `root ${root} (${members.length}/${cap})`)));
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
  root.replaceChildren(chainBox, h('h3', { style: 'color:var(--c-gold)' }, L('B · RW 标记与恢复（候选 DAG）', 'B · RW labelling and recovery (candidate DAG)')),
    h('p.notice', { style: 'color:var(--ink)' }, L('候选数据：12 节点 DAG 由原作影片的图与 Δ 表复原；“得分相等时拓扑序靠后者优先”是本课程的假设。它重现了 8 簇、20 实例、输出 8，但原始边表与平票规则尚待原作者确认。', 'Candidate data: the 12-node DAG is reconstructed from the figure and the Δ table in the original video; “on equal scores the later node in topological order goes first” is this course’s assumption. It reproduces 8 clusters, 20 instances and output 8, but the original edge list and tie rule await the original author’s confirmation.')),
    toolbar, h('div.lab', {}, h('div', {}, stage, inst, h('div.legend', {}, h('span', {}, L('实例图：金色虚线圈 = 被复制的逻辑节点；红色虚线 = 跨簇连线（+D）；数字 = 到达时间', 'Instance graph: gold dashed ring = a replicated logic node; red dashed line = a wire between clusters (+D); number = arrival time')))), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', L('本步的得分与候选簇', 'This step’s scores and candidate cluster')), candBox, playerBox);
  const dag = () => ({ ...RW.CANDIDATE_DAG, D, capacity: cap });
  const gv = new GraphView(stage, { graph: { nodes: RW.CANDIDATE_DAG.nodes, edges: RW.CANDIDATE_DAG.edges.map(([u, v]) => [u, v]) }, positions: RW.CANDIDATE_DAG.positions, directed: true, radius: 20, title: L('候选 DAG', 'Candidate DAG'), width: 760, height: 440 });
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: L('阶段', 'Phase'), get: e => ({ 'pi-labels': L('初始化', 'init'), label: L('标记', 'label'), 'select-cluster': L('恢复', 'recover') })[e.kind] },
    { label: L('节点 / 簇根', 'Node / root'), get: e => e.kind === 'label' ? e.after.node : e.kind === 'select-cluster' ? e.after.root : 'PI' }, { label: 'l1 / l2 / l', get: e => e.kind === 'label' ? `${e.metrics.l1} / ${e.metrics.l2} / ${e.metrics.label}` : '' },
    { label: L('簇', 'Cluster'), get: e => e.kind === 'label' ? e.after.cluster.join('') : e.kind === 'select-cluster' ? e.after.members.join('') : '' }], onPick: i => player.go(i) });
  toolbar.replaceChildren(
    select(L('跨簇延迟 D', 'Inter-cluster delay D'), [1, 2, 3, 4, 5].map(v => [String(v), String(v)]), String(D), v => { D = +v; recompute(); }),
    select(L('簇容量 M', 'Cluster capacity M'), [2, 3, 4, 5, 6].map(v => [String(v), String(v)]), String(cap), v => { cap = +v; recompute(); }),
    h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m09-rajaraman-wong', { options: { D, capacity: cap }, input: dag(), result: run.result, events: run.events, note: 'candidate DAG; tie rule assumed' }) }, L('导出运行记录', 'Export the run')));
  function recompute() {
    run = RW.run(dag());
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join(L('；', '; ')); return; }
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
      tags: Object.fromEntries(Object.entries(labels).map(([n, l]) => [n, `l=${l}`])), summary: e.kind === 'label' ? e.decision : e.kind === 'select-cluster' ? L(`选中以 ${e.after.root} 为根的簇`, `cluster rooted at ${e.after.root} selected`) : L('初始化', 'initialisation') });
    const selected = run.events.slice(0, i + 1).filter(x => x.kind === 'select-cluster').length;
    inst.replaceChildren(selected ? instanceView(r, D, selected, cap) : h('p.lab-note', L('标记阶段：簇还没有恢复。', 'Labelling: no cluster has been recovered yet.')));
    metrics(metricBox, [[L('标记', 'Labelled'), `${Object.keys(labels).length}/${RW.CANDIDATE_DAG.nodes.length}`], [L('已恢复簇', 'Clusters'), selected], [L('最大延迟', 'Max delay'), selected === r.selected.length ? r.maxDelay : '—']]);
    if (e.kind === 'pi-labels') status(statusBox, '', L(`初始化：PI ${RW.CANDIDATE_DAG.PI.join('、')} 的标签 = 自身延迟 1；Δ 表由最长路径算出。`, `Initialisation: the PIs ${RW.CANDIDATE_DAG.PI.join(', ')} get label = their own delay, 1; the Δ table comes from longest paths.`));
    else if (e.kind === 'label') status(statusBox, '', L(`${e.decision}。候选簇 {${e.after.cluster.join(', ')}}（容量 ${cap}）。`, `${e.decision}. Candidate cluster {${e.after.cluster.join(', ')}} (capacity ${cap}).`));
    else {
      const done = selected === r.selected.length, nr = RW.evaluatePartition(RW.CANDIDATE_DAG, NO_REPLICATION_BEST).maxDelay, outs = Object.entries(r.outputDelays).map(([p, t]) => `${p}=${t}`);
      status(statusBox, done ? '' : 'limit', L(`选中以 ${e.after.root} 为根的簇：成员 ${e.after.members.join('')}${e.after.inputs.length ? `，簇外输入 ${e.after.inputs.join('、')} 成为新的簇根` : ''}。${done ? `完成：${r.selected.length} 簇、${r.instanceCount} 个实例，输出 ${outs.join('、')}。不复制时（容量 4、D 3）穷举最好是 ${nr}。` : ''}`,
        `Cluster rooted at ${e.after.root} selected: members ${e.after.members.join('')}${e.after.inputs.length ? `; the outside inputs ${e.after.inputs.join(', ')} become new roots` : ''}.${done ? ` Done: ${r.selected.length} clusters, ${r.instanceCount} instances, outputs ${outs.join(', ')}. Without replication (capacity 4, D 3) the exhaustive best is ${nr}.` : ''}`));
    }
    candBox.replaceChildren(e.kind === 'label' ? h('table', {}, h('thead', {}, h('tr', {}, h('th', L('祖先 x', 'Ancestor x')), h('th', 'l(x)'), h('th', 'Δ(x,v)'), h('th', L('得分', 'Score')), h('th', ''))),
      h('tbody', {}, e.candidates.map(c => h('tr', { class: c.inCluster ? 'chosen' : '' }, h('td', c.x), h('td', String(c.l)), h('td', String(c.delta)), h('td', String(c.score)), h('td', c.inCluster ? L('簇内', 'inside') : L(`簇外 → +${D}`, `outside → +${D}`)))))) : h('p.muted', e.kind === 'select-cluster' ? L('恢复阶段：见左下实例图。', 'Recovery: see the instance graph at the lower left.') : '—'));
    pseudo.rw?.show(e.kind === 'pi-labels' ? [1, 2] : e.kind === 'label' ? [3, 4, 5, 6, 7] : [8, 9], '');
  }
  recompute();
}

/** A new DAG for the code lab: two inputs, a diamond and a fork, one output. */
const DIAMOND = { nodes: ['p', 'q', 'r', 's', 't', 'u', 'v'], edges: [['p', 'r'], ['q', 'r'], ['q', 's'], ['r', 't'], ['s', 't'], ['s', 'u'], ['t', 'v'], ['u', 'v']], PI: ['p', 'q'], PO: ['v'], nodeDelay: 1, nodeSize: 1,
  positions: { p: [80, 120], q: [80, 320], r: [260, 120], s: [260, 320], t: [440, 200], u: [440, 400], v: [620, 280] } };

/** Code lab: run the learner's rajaraman_wong() (built on all five tasks) and compare labels, clusters, instances and output delays with the engine. */
function visualize(root, api) {
  const C = RW.CANDIDATE_DAG;
  const CASES = [
    { name: L('候选 DAG · D 3 · M 4', 'Candidate DAG · D 3 · M 4'), dag: C, D: 3, cap: 4 }, { name: L('候选 DAG · D 1 · M 4', 'Candidate DAG · D 1 · M 4'), dag: C, D: 1, cap: 4 },
    { name: L('候选 DAG · D 3 · M 3', 'Candidate DAG · D 3 · M 3'), dag: C, D: 3, cap: 3 }, { name: L('候选 DAG · D 3 · M 2', 'Candidate DAG · D 3 · M 2'), dag: C, D: 3, cap: 2 },
    { name: L('菱形 DAG（新图）· D 2 · M 3', 'Diamond DAG (new graph) · D 2 · M 3'), dag: DIAMOND, D: 2, cap: 3 }, { name: L('菱形 DAG（新图）· D 4 · M 2', 'Diamond DAG (new graph) · D 4 · M 2'), dag: DIAMOND, D: 4, cap: 2 }
  ];
  const stage = h('div.lab-stage'), side = h('div.lab-side'), statusBox = h('div.status'), detail = h('div.decision'), tableBox = h('div'), match = h('p.match');
  const go = h('button.btn.primary', { type: 'button', onclick: runMine }, L('▶ 用我的代码运行', '▶ Run my code'));
  side.append(statusBox, detail);
  root.append(h('h3', L('用你的代码跑一遍', 'Watch your own code run')),
    h('p.muted', L('这里调用你的 rajaraman_wong()（它用到你写的全部五个函数），在 6 个情形上对照课程引擎：每个节点的标签、簇数、实例数和输出延迟。点表格的一行，左边画出你的标签和被复制的节点。',
      'This calls your rajaraman_wong() (which uses all five functions you wrote) and compares it with the course engine on six cases: every node’s label, the number of clusters and instances, and the output delays. Click a row to draw your labels and the replicated nodes on the left.')),
    h('div.lab-toolbar', {}, go), tableBox, h('div.lab', {}, h('div', {}, stage), side), match);
  stage.append(h('p.muted', { style: 'padding:40px 10px;text-align:center' }, L('写好五个函数后，按“用我的代码运行”。', 'Once all five functions are written, press “Run my code”.')));
  let rows = [];
  const summary = x => `${x.clusters} | ${x.instances} | ${Object.entries(x.out).map(([p, t]) => `${p}=${t}`).join(' ')}`;

  async function runMine() {
    if (api.busy) return;
    const payload = CASES.map(c => ({ nodes: c.dag.nodes, edges: c.dag.edges, PI: c.dag.PI, PO: c.dag.PO, node_delay: 1, capacity: c.cap, D: c.D }));
    const code = `import json, importlib.util
spec = importlib.util.spec_from_file_location('impl_v', 'impl.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
out = []
for d in json.loads(${JSON.stringify(JSON.stringify(payload))}):
    try:
        d["edges"] = [tuple(e) for e in d["edges"]]
        r = m.rajaraman_wong(d)
        logical = {}
        for i, lg in r["instances"].items():
            logical[lg] = logical.get(lg, 0) + 1
        out.append({"labels": r["labels"], "clusters": len(r["clusters"]), "instances": len(r["instances"]), "out": r["output_delay"], "copies": logical})
    except Exception as e:
        out.append({"error": type(e).__name__ + ": " + str(e)})
json.dumps(out)`;
    api.setBusy(true); go.disabled = true; match.className = 'match'; match.textContent = L('运行中…', 'Running…');
    try {
      const mine = JSON.parse((await api.run(code)).value);
      rows = CASES.map((c, i) => {
        const r = RW.run({ ...c.dag, D: c.D, capacity: c.cap }).result, me = mine[i];
        const ref = { labels: r.labels, clusters: r.selected.length, instances: r.instanceCount, out: r.outputDelays };
        const same = !me.error && JSON.stringify(me.labels) === JSON.stringify(ref.labels) && me.clusters === ref.clusters && me.instances === ref.instances && JSON.stringify(me.out) === JSON.stringify(ref.out);
        return { c, ref, me, ok: same };
      });
      const ok = rows.filter(r => r.ok).length;
      match.className = 'match ' + (ok === rows.length ? 'ok' : 'no');
      match.textContent = ok === rows.length
        ? L('✓ 6 个情形都与课程引擎一致：同样的标签、簇数、实例数和输出延迟。', '✓ All six cases agree with the course engine: the same labels, clusters, instances and output delays.')
        : L(`× ${rows.length - ok} 个情形与引擎不同（红色）。点那一行看差在哪里。`, `× ${rows.length - ok} of the cases differ from the engine (in red). Click a row to see where.`);
      drawTable(); pick(rows.findIndex(r => !r.ok) >= 0 ? rows.findIndex(r => !r.ok) : 0);
    } catch (err) {
      match.className = 'match no';
      const msg = String(err.message || err).split('\n').filter(Boolean);
      match.textContent = err.reason ? L('已停止。', 'Stopped.') : L('你的代码运行出错：', 'Your code raised an error: ') + msg.slice(-1)[0];
    } finally { api.setBusy(false); go.disabled = false; }
  }
  function drawTable(sel = -1) {
    tableBox.replaceChildren(h('table.codelab-cases', {}, h('thead', {}, h('tr', {}, h('th', L('情形', 'Case')), h('th', L('你的：簇 | 实例 | 输出', 'Yours: clusters | instances | outputs')), h('th', L('标签', 'Labels')), h('th', L('引擎', 'Engine')))),
      h('tbody', {}, rows.map((r, i) => h('tr', { class: i === sel ? 'chosen' : '', style: 'cursor:pointer', onclick: () => pick(i) },
        h('td', r.c.name),
        ...(r.me.error ? [h('td', { colspan: 2, style: 'color:var(--c-red)' }, r.me.error)]
          : [h('td', { style: r.ok ? '' : 'color:var(--c-red);font-weight:600' }, summary(r.me)),
             h('td', { style: JSON.stringify(r.me.labels) === JSON.stringify(r.ref.labels) ? '' : 'color:var(--c-red);font-weight:600' }, JSON.stringify(r.me.labels) === JSON.stringify(r.ref.labels) ? '✓' : '×')]),
        h('td', summary(r.ref)))))));
  }
  function pick(i) {
    const r = rows[i]; if (!r) return;
    drawTable(i);
    const g = r.c.dag, labels = r.me.labels || r.ref.labels, copies = r.me.copies || {};
    new GraphView(stage, { graph: { nodes: g.nodes, edges: g.edges.map(([u, v]) => [u, v]) }, positions: g.positions, directed: true, radius: 20, title: L('你的代码的结果', 'Your code’s result'), width: 760, height: 440 })
      .render({ groups: Object.fromEntries(g.nodes.map(n => [n, (copies[n] || 1) > 1 ? 'rep' : 'one'])), groupOrder: ['rep', 'one'],
        fills: Object.fromEntries(g.nodes.map(n => [n, (copies[n] || 1) > 1 ? '#d8bb78' : g.PI.includes(n) ? '#8fb1e6' : '#a9bdb8'])),
        tags: Object.fromEntries(Object.entries(labels).map(([n, l]) => [n, `l=${l}`])), summary: L(`你的结果：最大延迟 ${r.me.out ? Math.max(...Object.values(r.me.out)) : '—'}`, `Your result: max delay ${r.me.out ? Math.max(...Object.values(r.me.out)) : '—'}`) });
    status(statusBox, r.ok ? '' : 'cycle', r.ok ? L('这个情形与引擎一致。金色节点在你的结果里被复制了。', 'This case agrees with the engine. Gold nodes were replicated in your result.') : L('这个情形与引擎不同：先对照标签，再对照簇和实例的个数。', 'This case differs from the engine: compare the labels first, then the cluster and instance counts.'));
    const rep = Object.entries(copies).filter(([, k]) => k > 1).map(([n, k]) => `${n}×${k}`);
    detail.replaceChildren(h('p', {}, L(`引擎：${r.ref.clusters} 簇、${r.ref.instances} 个实例（逻辑节点 ${g.nodes.length} 个），输出 ${Object.entries(r.ref.out).map(([p, t]) => `${p}=${t}`).join('、')}。`,
      `Engine: ${r.ref.clusters} clusters, ${r.ref.instances} instances (${g.nodes.length} logic nodes), outputs ${Object.entries(r.ref.out).map(([p, t]) => `${p}=${t}`).join(', ')}.`)),
      rep.length ? h('p.muted', L(`你的结果里被复制的：${rep.join('、')}`, `Replicated in your result: ${rep.join(', ')}`)) : '');
  }
}

bootModule({ moduleId: 'm09-rajaraman-wong', display: 'Module 09', challenges, lab, visualize });
