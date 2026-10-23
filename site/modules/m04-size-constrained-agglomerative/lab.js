// Module 04 lab: greedy merging with a hard capacity, plus a lower-bound and exhaustive diagnosis.
import { h } from '../../assets/core.js';
import { L } from '../../assets/i18n.js';
import { GraphView, PALETTE } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as M from '../../engines/merge.js';
import { G01, requireGraph } from '../../engines/graph.js';
import { challenges } from './challenges.js';


/** Three twin-size rooms: the lower bound allows K = 2, but no two fit together (used only in the code-lab check). */
const TRIO = { nodes: [{ id: 'X', size: 2 }, { id: 'Y', size: 2 }, { id: 'Z', size: 2 }], edges: [['X', 'Y', 3], ['Y', 'Z', 2], ['X', 'Z', 1]],
  positions: { X: [180, 150], Y: [420, 300], Z: [660, 150] } };
const PRESETS = {
  g01: { name: L('课程公共图 G01（大小均为 1）', 'Course graph G01 (every size 1)'), graph: G01, positions: G01.positions, k: 2, capacity: 2 },
  trap: { name: L('greedy_trap（原作者 GateUltra）', 'greedy_trap (original author GateUltra)'), graph: M.M04_GRAPHS.greedy_trap, positions: M.M04_GRAPHS.greedy_trap.positions, k: 2, capacity: 3 },
  sub: { name: L('suboptimal（原作者 GateUltra）', 'suboptimal (original author GateUltra)'), graph: M.M04_GRAPHS.suboptimal, positions: M.M04_GRAPHS.suboptimal.positions, k: 2, capacity: 2 }
};
const KIND = { 'infeasible-by-bound': ['blocked', L('目标不可能：下界已超过 K。任何算法都做不到，贪心停下不是错误。', 'The target is impossible: the lower bound already exceeds K. No algorithm can do it, so greedy stopping is not a mistake.')],
  'infeasible-by-search': ['blocked', L('目标不可能：穷举也找不到恰好 K 簇的合法划分。', 'The target is impossible: even exhaustive search finds no legal partition into exactly K clusters.')],
  'greedy-stuck': ['cycle', L('总体可行，但贪心卡住：存在合法的 K 簇分组，贪心因早期选择而无法到达。', 'Feasible, but greedy is stuck: a legal grouping into K clusters exists, and greedy cannot reach it because of an early choice.')],
  'feasible-suboptimal': ['limit', L('达到 K 且合法，但不是最优：穷举找到更小的 cut。', 'K is reached and the result is legal, but not optimal: exhaustive search finds a smaller cut.')],
  'reached-and-optimal-here': ['', L('达到 K 且合法；在这张小图上与穷举最优相同（不代表一般最优）。', 'K is reached and the result is legal; on this small graph it equals the exhaustive optimum (not a general guarantee).')] };
const KIND_SHORT = { 'infeasible-by-bound': L('下界证明不可能', 'impossible by bound'), 'infeasible-by-search': L('穷举证明不可能', 'impossible by search'),
  'greedy-stuck': L('贪心卡住', 'greedy stuck'), 'feasible-suboptimal': L('合法但非最优', 'legal, not optimal'), 'reached-and-optimal-here': L('达到且此处最优', 'reached, optimal here') };
const STOP = { 'target-reached': L('达到 K', 'K is reached'), 'capacity-blocked': L('剩下的正亲和度对全部超容量', 'every remaining positive pair is over capacity'), 'no-positive-affinity': L('剩下的簇之间没有边', 'no wire joins the remaining clusters') };

async function lab(root, { pseudo }) {
  let presetId = 'g01', k = 2, capacity = 2, sizes = {}, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), decision = h('div.decision'), playerBox = h('div');
  const diagBox = h('div.decision'), traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, h('div.legend', {},
    h('span', {}, h('b', { style: 'background:#db7b72' }), L('红圈：超容量被阻止', 'Red rings: blocked by the capacity')), h('span', {}, h('b', { style: 'background:#d8bb78' }), L('金圈：本步合并', 'Gold rings: merging now')),
    h('span', {}, L('节点下方：大小 s(v)', 'Under each node: its size s(v)')))), side), h('div.lab-side.lab-diag', { style: 'border:1px solid var(--c-line);border-radius:10px;margin-top:14px' }, h('h4', { style: 'margin-top:0' }, L('诊断：是不可能、卡住，还是不最优？', 'Diagnosis: impossible, stuck, or not optimal?')), diagBox), traceBox, err);
  side.append(metricBox, statusBox, h('h4', L('本步的全部候选', 'Every candidate at this step')), decision, playerBox);
  let gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: L('容量约束实验图', 'Capacity-constrained lab graph') });
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: L('步', 'Step'), get: e => e.step }, { label: L('动作', 'Action'), get: e => e.kind === 'merge' ? L(`合并 ${e.decision.a}+${e.decision.b}（大小 ${e.decision.size}）`, `merge ${e.decision.a}+${e.decision.b} (size ${e.decision.size})`) : e.kind === 'stopped' ? L('停止', 'stop') : L('单点簇', 'singletons') },
    { label: L('被阻止', 'Blocked'), get: e => (e.kind === 'stopped' ? e.candidates : e.blocked || []).filter(c => !c.legal).map(c => `${c.a}+${c.b}`).join(' ') }, { label: 'cut', get: e => e.metrics.cut }], onPick: i => player.go(i) });

  const graph = () => { const g = requireGraph(PRESETS[presetId].graph); return { nodes: g.nodes.map(n => ({ id: n.id, size: sizes[n.id] ?? n.size })), edges: g.edges }; };
  function buildToolbar() {
    const g = graph();
    const nodeSel = h('select', { 'aria-label': L('选择节点', 'Choose a node') }, g.nodes.map(n => h('option', { value: n.id }, n.id)));
    const sIn = h('input', { type: 'number', min: 1, max: 9, step: 1, 'aria-label': L('节点大小', 'Node size') });
    const sync = () => { sIn.value = graph().nodes.find(n => n.id === nodeSel.value).size; };
    nodeSel.addEventListener('change', sync); sync();
    sIn.addEventListener('change', () => { const v = Number(sIn.value); if (!(Number.isInteger(v) && v >= 1 && v <= 9)) { err.textContent = L('节点大小为 1–9 的整数。', 'A node size is a whole number from 1 to 9.'); return; } err.textContent = ''; sizes[nodeSel.value] = v; recompute(); });
    toolbar.replaceChildren(
      select(L('例子', 'Example'), Object.entries(PRESETS).map(([key, p]) => [key, p.name]), presetId, v => { presetId = v; sizes = {}; k = PRESETS[v].k; capacity = PRESETS[v].capacity; buildToolbar(); recompute(true); }),
      select(L('目标 K', 'Target K'), [1, 2, 3, 4].map(x => [String(x), String(x)]), String(k), v => { k = +v; recompute(); }),
      select(L('容量 C', 'Capacity C'), [['', L('不限', 'none')], ...[2, 3, 4, 5, 6].map(x => [String(x), String(x)])], capacity ? String(capacity) : '', v => { capacity = v ? +v : null; recompute(); }),
      h('label', {}, L('节点', 'Node'), nodeSel), h('label', {}, L('大小 s(v)', 'Size s(v)'), sIn),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m04-size-constrained-agglomerative', { preset: presetId, options: { k, capacity }, input: graph(), result: run.result, events: run.events, diagnosis: diag }) }, L('导出运行记录', 'Export the run')));
  }
  let diag = null;
  function recompute(newGraph = false) {
    const g = graph();
    if (newGraph) gv = new GraphView(stage, { graph: g, positions: PRESETS[presetId].positions, title: L('容量约束实验图', 'Capacity-constrained lab graph') });
    run = M.run(g, { k, capacity });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join(L('；', '; ')); diagBox.replaceChildren(h('p', L('输入不合法：没有任何合法分组。', 'Invalid input: no legal grouping exists.'))); trace.load([]); return; }
    err.textContent = '';
    diag = M.diagnose(g, { k, capacity });
    const o = diag.oracle, [cls, text] = KIND[diag.kind];
    diagBox.replaceChildren(h('div', { class: 'status ' + cls }, text), h('table', {}, h('tbody', {},
      h('tr', {}, h('th', L('下界 ⌈Σs / C⌉', 'Lower bound ⌈Σs / C⌉')), h('td', capacity ? `⌈${g.nodes.reduce((s, n) => s + n.size, 0)} / ${capacity}⌉ = ${o.lowerBoundClusters}` : L('不限容量：1', 'no capacity: 1'))),
      h('tr', {}, h('th', L('穷举：最少合法簇数', 'Exhaustive: fewest legal clusters')), h('td', String(o.minFeasibleClusters))),
      h('tr', {}, h('th', L(`穷举：恰好 ${k} 簇的最小 cut`, `Exhaustive: least cut with exactly ${k} clusters`)), h('td', o.bestCutAtK ? L(`${o.bestCutAtK.cut}（${o.bestCutAtK.clusters.map(c => c.join('')).join(' | ')}）`, `${o.bestCutAtK.cut} (${o.bestCutAtK.clusters.map(c => c.join('')).join(' | ')})`) : L('不存在', 'none'))),
      h('tr', {}, h('th', L('贪心结果', 'Greedy result')), h('td', L(`${run.result.labels.join(' | ')}，cut ${run.result.cut}，${run.result.count} 簇`, `${run.result.labels.join(' | ')}, cut ${run.result.cut}, ${run.result.count} clusters`))))),
      h('p.lab-note', L(`穷举检查了 ${o.legalPartitions} 个合法划分；只用于 ≤ 10 个节点的教学图。`, `Exhaustive search checked ${o.legalPartitions} legal partitions; it is only for teaching graphs of at most 10 nodes.`)));
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const g = graph(), size = Object.fromEntries(g.nodes.map(n => [n.id, n.size]));
    const groups = {}, hulls = [];
    e.after.forEach((c, gi) => { c.members.forEach(m => { groups[m] = c.label; }); if (c.members.length > 1) hulls.push({ members: c.members, label: `${c.label} · ${c.size}/${capacity ?? '∞'}`, color: PALETTE[gi % PALETTE.length] }); });
    const inside = g.edges.filter(x => groups[x.u] === groups[x.v]).map(x => [x.u, x.v]);
    const blockedList = (e.kind === 'stopped' ? e.candidates : e.blocked || []).filter(c => !c.legal);
    const focus = e.kind === 'merge' ? [...e.before.find(c => c.label === e.decision.a).members, ...e.before.find(c => c.label === e.decision.b).members] : [];
    gv.render({ groups, cut: true, inside, hulls, focus, blocked: [...new Set(blockedList.flatMap(c => [...c.a, ...c.b]))], tags: Object.fromEntries(Object.entries(size).map(([n, s]) => [n, `s=${s}`])), groupOrder: e.after.map(c => c.label), summary: L(`第 ${e.step} 步：${e.after.map(c => c.label).join(' | ')}`, `Step ${e.step}: ${e.after.map(c => c.label).join(' | ')}`) });
    const r = run.result, last = i === run.events.length - 1;
    metrics(metricBox, [[L('簇数', 'Clusters'), e.after.length], ['cut', e.metrics.cut], ['K / C', `${k} / ${capacity ?? '∞'}`]]);
    if (e.kind === 'merge') status(statusBox, '', L(`合并 ${e.decision.a}+${e.decision.b}：大小 ${e.decision.size}${capacity ? ` ≤ ${capacity}` : ''}，亲和度 ${e.decision.affinity}。${blockedList.length ? `之前的 ${blockedList.map(c => `${c.a}+${c.b}`).join('、')} 因超容量被跳过。` : ''}`, `Merge ${e.decision.a}+${e.decision.b}: size ${e.decision.size}${capacity ? ` ≤ ${capacity}` : ''}, affinity ${e.decision.affinity}.${blockedList.length ? ` The earlier ${blockedList.map(c => `${c.a}+${c.b}`).join(', ')} ${blockedList.length > 1 ? 'were' : 'was'} skipped as over capacity.` : ''}`));
    else if (e.kind === 'stopped') status(statusBox, 'blocked', L(`停止：${STOP[e.decision]}。`, `Stop: ${STOP[e.decision]}.`));
    else status(statusBox, '', L('开始：每个节点一个簇。', 'Start: one cluster per node.'));
    if (last) status(statusBox, r.targetReached ? '' : 'blocked', L(`报告：${r.count} 簇；容量${r.capacityCompliant ? '满足' : '违反'}；${r.targetReached ? '达到' : '未达到'} K = ${k}；停止原因：${STOP[r.stopReason]}。`, `Report: ${r.count} clusters; capacity ${r.capacityCompliant ? 'respected' : 'violated'}; K = ${k} ${r.targetReached ? 'reached' : 'not reached'}; stop reason: ${STOP[r.stopReason]}.`));
    const cands = e.candidates || [];
    decision.replaceChildren(cands.length ? h('table', {}, h('thead', {}, h('tr', {}, h('th', L('簇对', 'Pair')), h('th', L('亲和度', 'Affinity')), h('th', L('大小', 'Size')), h('th', ''))),
      h('tbody', {}, cands.map(c => { const chosen = e.kind === 'merge' && c.a === e.decision.a && c.b === e.decision.b;
        return h('tr', { class: chosen ? 'chosen' : !c.legal ? 'blocked' : '' }, h('td', `${c.a}–${c.b}`), h('td', String(c.affinity)), h('td', `${c.size}${capacity ? '/' + capacity : ''}`), h('td', chosen ? L('选中', 'chosen') : !c.legal ? L('超容量', 'over capacity') : '')); }))) : h('p.muted', L('初始状态。', 'Initial state.')));
    pseudo.capacity?.show(e.kind === 'singletons' ? [1] : e.kind === 'stopped' ? [4, 5, 7, 8] : last ? [6, 2, 7, 8] : [3, 4, 6], '');
  }
  buildToolbar(); recompute(true);
}

/** Code lab: run the learner's solve()/report()/classify() on eight cases and compare each with the engine. */
function visualize(root, api) {
  const G = { g01: [G01, G01.positions], trap: [M.M04_GRAPHS.greedy_trap, M.M04_GRAPHS.greedy_trap.positions], sub: [M.M04_GRAPHS.suboptimal, M.M04_GRAPHS.suboptimal.positions], trio: [TRIO, TRIO.positions] };
  const CASES = [['g01', 2, 3], ['g01', 2, 2], ['g01', 3, 2], ['trap', 2, 3], ['sub', 2, 2], ['trio', 2, 3], ['trio', 2, 4], ['g01', 1, 4]];
  const NAME = { g01: 'G01', trap: 'greedy_trap', sub: 'suboptimal', trio: L('三间双人房 XYZ（新图）', 'Three twin rooms XYZ (new graph)') };
  const stage = h('div.lab-stage'), side = h('div.lab-side'), statusBox = h('div.status'), detail = h('div.decision'), tableBox = h('div'), match = h('p.match');
  const go = h('button.btn.primary', { type: 'button', onclick: runMine }, L('▶ 用我的代码运行', '▶ Run my code'));
  side.append(statusBox, detail);
  root.append(h('h3', L('用你的代码跑一遍', 'Watch your own code run')),
    h('p.muted', L('这里调用你写的 report() 和 classify()，在 8 个情形上与课程引擎逐项对照：簇数、是否满足容量、是否达到 K、停止原因和诊断类别。点表格的一行，左边画出你的结果。',
      'This calls the report() and classify() you wrote and compares them with the course engine on eight cases, field by field: the number of clusters, whether the capacity holds, whether K is reached, the stop reason and the diagnosis. Click a row to draw your result on the left.')),
    h('div.lab-toolbar', {}, go), tableBox, h('div.lab', {}, h('div', {}, stage), side), match);
  stage.append(h('p.muted', { style: 'padding:40px 10px;text-align:center' }, L('写好两个函数后，按“用我的代码运行”。', 'Once both functions are written, press “Run my code”.')));
  let rows = [], gv = null;
  const graphOf = key => requireGraph(G[key][0]);
  const pyGraph = key => { const g = graphOf(key); return { nodes: g.nodes.map(n => n.id), sizes: Object.fromEntries(g.nodes.map(n => [n.id, n.size])), edges: g.edges.map(e => [e.u, e.v, e.w]) }; };
  const FIELDS = [['count', 'count'], ['capacity_compliant', 'capacityCompliant'], ['target_reached', 'targetReached'], ['stop_reason', 'stopReason']];

  async function runMine() {
    if (api.busy) return;
    const payload = CASES.map(([key, k, cap]) => ({ g: pyGraph(key), k, cap }));
    const code = `import json, importlib.util
spec = importlib.util.spec_from_file_location('impl_v', 'impl.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
out = []
for c in json.loads(${JSON.stringify(JSON.stringify(payload))}):
    try:
        r = m.solve(c["g"], c["k"], c["cap"])
        row = {k: r.get(k) for k in ("count", "capacity_compliant", "target_reached", "stop_reason", "cutsize")}
        row["clusters"] = ["".join(p) for p in r["clusters"]]
        try:
            row["kind"] = m.classify(c["g"], c["k"], c["cap"])
        except Exception as e:
            row["kindError"] = type(e).__name__ + ": " + str(e)
        out.append(row)
    except Exception as e:
        out.append({"error": type(e).__name__ + ": " + str(e)})
json.dumps(out)`;
    api.setBusy(true); go.disabled = true; match.className = 'match'; match.textContent = L('运行中…', 'Running…');
    try {
      const mine = JSON.parse((await api.run(code)).value);
      rows = CASES.map(([key, k, cap], i) => {
        const g = graphOf(key), d = M.diagnose(g, { k, capacity: cap }), ref = d.run.result, me = mine[i];
        const bad = me.error ? ['error'] : FIELDS.filter(([p, j]) => me[p] !== ref[j]).map(([p]) => p);
        if (!me.error && me.kind !== d.kind) bad.push('kind');
        return { key, k, cap, g, d, ref, me, bad };
      });
      const ok = rows.filter(r => !r.bad.length).length;
      match.className = 'match ' + (ok === rows.length ? 'ok' : 'no');
      match.textContent = ok === rows.length
        ? L(`✓ 8 个情形全部与课程引擎一致，五种诊断类别都出现过。`, `✓ All eight cases agree with the course engine, and all five diagnoses appear.`)
        : L(`× ${rows.length - ok} 个情形与引擎不同（红色）。点那一行看差在哪里。`, `× ${rows.length - ok} of the cases differ from the engine (in red). Click a row to see where.`);
      drawTable(); pick(rows.findIndex(r => r.bad.length) >= 0 ? rows.findIndex(r => r.bad.length) : 0);
    } catch (err) {
      match.className = 'match no';
      const msg = String(err.message || err).split('\n').filter(Boolean);
      match.textContent = err.reason ? L('已停止。', 'Stopped.') : L('你的代码运行出错：', 'Your code raised an error: ') + msg.slice(-1)[0];
    } finally { api.setBusy(false); go.disabled = false; }
  }
  function drawTable(sel = -1) {
    const yes = v => v === true ? '✓' : v === false ? '×' : String(v ?? '—');
    tableBox.replaceChildren(h('table.codelab-cases', {}, h('thead', {}, h('tr', {}, h('th', L('情形', 'Case')), h('th', L('簇数', 'Clusters')), h('th', L('容量满足', 'Capacity ok')), h('th', L('达到 K', 'K reached')), h('th', L('停止原因', 'Stop reason')), h('th', L('你的诊断', 'Your diagnosis')), h('th', L('引擎诊断', 'Engine diagnosis')))),
      h('tbody', {}, rows.map((r, i) => {
        const cell = (field, text) => h('td', { style: r.bad.includes(field) || r.bad.includes('error') ? 'color:var(--c-red);font-weight:600' : '' }, text);
        return h('tr', { class: i === sel ? 'chosen' : '', style: 'cursor:pointer', onclick: () => pick(i) },
          h('td', `${NAME[r.key]} · K=${r.k} · C=${r.cap}`),
          ...(r.me.error ? [h('td', { colspan: 5, style: 'color:var(--c-red)' }, r.me.error)] : [cell('count', String(r.me.count ?? '—')), cell('capacity_compliant', yes(r.me.capacity_compliant)), cell('target_reached', yes(r.me.target_reached)), cell('stop_reason', String(r.me.stop_reason ?? '—')), cell('kind', r.me.kindError ? r.me.kindError : KIND_SHORT[r.me.kind] || String(r.me.kind ?? '—'))]),
          h('td', KIND_SHORT[r.d.kind]));
      }))));
  }
  function pick(i) {
    const r = rows[i]; if (!r) return;
    drawTable(i);
    const [, pos] = G[r.key], size = Object.fromEntries(r.g.nodes.map(n => [n.id, n.size]));
    const parts = r.me.clusters || r.ref.labels, groups = {}, hulls = [];
    parts.forEach((p, gi) => { [...p].forEach(m => { groups[m] = p; }); if (p.length > 1) hulls.push({ members: [...p], label: `${p} · ${[...p].reduce((s, m) => s + size[m], 0)}/${r.cap}`, color: PALETTE[gi % PALETTE.length] }); });
    gv = new GraphView(stage, { graph: r.g, positions: pos, title: L('你的代码的结果', 'Your code’s result') });
    gv.render({ groups, cut: true, inside: r.g.edges.filter(x => groups[x.u] === groups[x.v]).map(x => [x.u, x.v]), hulls, tags: Object.fromEntries(Object.entries(size).map(([n, s]) => [n, `s=${s}`])), groupOrder: parts, summary: L(`你的结果：${parts.join(' | ')}`, `Your result: ${parts.join(' | ')}`) });
    const [cls, text] = KIND[r.d.kind];
    status(statusBox, r.bad.length ? 'cycle' : cls, r.bad.length ? L(`这个情形与引擎不同：${r.bad.join('、')}。`, `This case differs from the engine: ${r.bad.join(', ')}.`) : L('这个情形与引擎一致。', 'This case agrees with the engine.'));
    const o = r.d.oracle;
    detail.replaceChildren(h('p', {}, h('b', L('引擎：', 'Engine: ')), text), h('table', {}, h('tbody', {},
      h('tr', {}, h('th', L('贪心结果', 'Greedy result')), h('td', L(`${r.ref.labels.join(' | ')}，cut ${r.ref.cut}`, `${r.ref.labels.join(' | ')}, cut ${r.ref.cut}`))),
      h('tr', {}, h('th', L('下界 ⌈Σs / C⌉', 'Lower bound ⌈Σs / C⌉')), h('td', String(o.lowerBoundClusters))),
      h('tr', {}, h('th', L(`恰好 ${r.k} 簇的最小 cut`, `Least cut with exactly ${r.k} clusters`)), h('td', o.bestCutAtK ? `${o.bestCutAtK.cut} (${o.bestCutAtK.clusters.map(c => c.join('')).join(' | ')})` : L('不存在', 'none'))),
      h('tr', {}, h('th', L('停止原因', 'Stop reason')), h('td', `${r.ref.stopReason}`)))));
  }
}

bootModule({ moduleId: 'm04-size-constrained-agglomerative', display: 'Module 04', challenges, lab, visualize });

