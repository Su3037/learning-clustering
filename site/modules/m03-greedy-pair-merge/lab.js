// Module 03 lab: greedy pair merging on G01 (or edited weights). All states come from engines/merge.js.
import { h } from '../../assets/core.js';
import { L } from '../../assets/i18n.js';
import { GraphView, PALETTE } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as M from '../../engines/merge.js';
import { G01 } from '../../engines/graph.js';
import { challenges } from './challenges.js';


const STOP = { 'target-reached': L('达到目标簇数 K', 'the target K is reached'), 'capacity-blocked': L('还有正亲和度对，但全部超容量', 'positive pairs remain, but all are over capacity'), 'no-positive-affinity': L('剩下的簇之间没有边（亲和度为 0）', 'no wire between the remaining clusters (affinity 0)') };

/** Draw one merge state on a GraphView: hulls around merged clusters, crossing wires as the cut. */
function drawState(gv, graph, after, { focus = [], blocked = [], summary = '' } = {}) {
  const groups = {}, hulls = [];
  after.forEach((c, gi) => { c.members.forEach(m => { groups[m] = c.label; }); if (c.members.length > 1) hulls.push({ members: c.members, label: L(`${c.label} · 大小 ${c.size}`, `${c.label} · size ${c.size}`), color: PALETTE[gi % PALETTE.length] }); });
  const inside = graph.edges.map(x => Array.isArray(x) ? { u: x[0], v: x[1] } : x).filter(x => groups[x.u] === groups[x.v]).map(x => [x.u, x.v]);
  gv.render({ groups, cut: true, inside, hulls, focus, blocked, groupOrder: after.map(c => c.label), summary });
}

async function lab(root, { pseudo }) {
  let k = 2, capacity = null, weights = {}, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), decision = h('div.decision'), playerBox = h('div');
  const legacyBox = h('div.lab-note'), traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, h('div.legend', {},
    h('span', {}, h('i', { style: 'border-color:#db7b72;border-top-style:dashed' }), L('被切断的边', 'Cut wires')),
    h('span', {}, h('i', { style: 'border-color:#9fc9bf' }), L('簇内部的边（不计入 cut）', 'Wires inside a cluster (not in the cut)')),
    h('span', {}, h('b', { style: 'background:#d8bb78' }), L('金圈：本步合并的两个簇', 'Gold rings: the two clusters merging now')))), side), legacyBox, traceBox, err);
  side.append(metricBox, statusBox, h('h4', L('本步的全部候选', 'Every candidate at this step')), decision, playerBox);
  const gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: L('贪心合并实验图', 'Greedy merge lab graph') });
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [
    { label: L('步', 'Step'), get: e => e.step }, { label: L('动作', 'Action'), get: e => e.kind === 'merge' ? L(`合并 ${e.decision.a}+${e.decision.b}`, `merge ${e.decision.a}+${e.decision.b}`) : e.kind === 'stopped' ? L('停止', 'stop') : L('单点簇', 'singletons') },
    { label: L('亲和度', 'Affinity'), get: e => e.decision?.affinity ?? '' }, { label: 'cut', get: e => e.metrics.cut }, { label: L('簇', 'Clusters'), get: e => e.after.map(c => c.label).join(' | ') }], onPick: i => player.go(i) });

  const graph = () => ({ nodes: G01.nodes, edges: G01.edges.map(e => ({ ...e, w: weights[`${e.u}|${e.v}`] ?? e.w })) });
  function buildToolbar() {
    const edgeSel = h('select', { 'aria-label': L('选择要修改的边', 'Choose the edge to change') }, G01.edges.map(e => h('option', { value: `${e.u}|${e.v}` }, `${e.u}–${e.v}`)));
    const wIn = h('input', { type: 'number', min: 1, max: 99, step: 0.5, 'aria-label': L('新权重', 'New weight') });
    const sync = () => { const e = graph().edges.find(x => `${x.u}|${x.v}` === edgeSel.value); wIn.value = e.w; };
    edgeSel.addEventListener('change', sync); sync();
    wIn.addEventListener('change', () => { const w = Number(wIn.value); if (!(w > 0 && w <= 99)) { err.textContent = L('权重须为 0–99 之间的正数。', 'The weight must be a positive number up to 99.'); return; } err.textContent = ''; weights[edgeSel.value] = w; recompute(); });
    toolbar.replaceChildren(
      select(L('目标簇数 K', 'Target K'), [1, 2, 3, 4].map(x => [String(x), String(x)]), String(k), v => { k = +v; recompute(); }),
      select(L('容量 C（节点大小均为 1）', 'Capacity C (every node size 1)'), [['', L('不限', 'none')], ['2', '2'], ['3', '3'], ['4', '4']], capacity ? String(capacity) : '', v => { capacity = v ? +v : null; recompute(); }),
      h('label', {}, L('改一条边', 'Change an edge'), edgeSel), h('label', {}, L('新权重', 'New weight'), wIn),
      h('button.btn.small', { type: 'button', onclick: () => { weights = {}; buildToolbar(); recompute(); } }, L('恢复原权重', 'Restore weights')),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m03-greedy-pair-merge', { options: { k, capacity }, input: graph(), engine: run.metadata, result: run.result, events: run.events }) }, L('导出运行记录', 'Export run')));
  }
  function recompute() {
    run = M.run(graph(), { k, capacity });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join(L('；', '; ')); return; }
    trace.load(run.events); player.load(run.events);
    const legacy = M.run(graph(), { k, capacity, legacyComparator: true });
    const same = legacy.result.cut === run.result.cut && legacy.result.labels.join() === run.result.labels.join();
    legacyBox.replaceChildren(h('strong', L('对照：原网页的字符串比较（已修复的错误，仅用于说明）', 'For comparison: the original page’s string comparison (a fixed bug, shown only to explain it)')), h('br'),
      L(`正确比较器：${run.result.labels.join(' | ')}，cut ${run.result.cut}。字符串比较：${legacy.result.labels.join(' | ')}，cut ${legacy.result.cut}`,
        `Correct comparator: ${run.result.labels.join(' | ')}, cut ${run.result.cut}. String comparison: ${legacy.result.labels.join(' | ')}, cut ${legacy.result.cut}`),
      same ? L('——这组参数下两者碰巧相同。', ': with these settings the two happen to agree.') : L(`——第一步被错误地选成 ${legacy.events[1]?.decision?.a ?? '?'}–${legacy.events[1]?.decision?.b ?? '?'}。`, `: its first step wrongly picks ${legacy.events[1]?.decision?.a ?? '?'}–${legacy.events[1]?.decision?.b ?? '?'}.`));
  }
  function show(i, e) {
    const after = e.after;
    const focus = e.kind === 'merge' ? [...e.before.find(c => c.label === e.decision.a).members, ...e.before.find(c => c.label === e.decision.b).members] : [];
    const blocked = e.kind === 'stopped' ? [...new Set((e.candidates || []).flatMap(c => [...c.a, ...c.b]))] : [];
    drawState(gv, graph(), after, { focus, blocked, summary: L(`第 ${e.step} 步：${after.map(c => c.label).join(' | ')}，cut ${e.metrics.cut}`, `Step ${e.step}: ${after.map(c => c.label).join(' | ')}, cut ${e.metrics.cut}`) });
    metrics(metricBox, [[L('簇数', 'Clusters'), after.length], ['cut', e.metrics.cut], [L('目标 K', 'Target K'), k]]);
    if (e.kind === 'singletons') status(statusBox, '', L(`开始：每个节点一个簇，cut = 全部边权 = ${e.metrics.cut}。`, `Start: one cluster per node; cut = all the weight = ${e.metrics.cut}.`));
    else if (e.kind === 'merge') status(statusBox, '', L(`合并 ${e.decision.a} + ${e.decision.b}（亲和度 ${e.decision.affinity}）：cut ${e.metrics.cutBefore} → ${e.metrics.cut}，下降量 = 亲和度。`, `Merge ${e.decision.a} + ${e.decision.b} (affinity ${e.decision.affinity}): cut ${e.metrics.cutBefore} → ${e.metrics.cut}; the drop equals the affinity.`));
    else status(statusBox, 'blocked', L(`停止：${STOP[e.decision]}。`, `Stopped: ${STOP[e.decision]}.`) + (after.length > k ? L(`得到 ${after.length} 簇，未达到 K = ${k}；不强行合并。`, ` ${after.length} clusters, K = ${k} not reached; no forced merge.`) : ''));
    if (i === run.events.length - 1 && run.result.targetReached) status(statusBox, '', L(`完成：${run.result.labels.join(' | ')}，cut ${run.result.cut}。停止原因：${STOP[run.result.stopReason]}。`, `Done: ${run.result.labels.join(' | ')}, cut ${run.result.cut}. Stop reason: ${STOP[run.result.stopReason]}.`));
    const cands = e.candidates || [];
    decision.replaceChildren(cands.length ? h('table', {}, h('thead', {}, h('tr', {}, h('th', L('簇对', 'Pair')), h('th', L('亲和度', 'Affinity')), h('th', L('合并后大小', 'Merged size')), h('th', ''))),
      h('tbody', {}, cands.map(c => {
        const chosen = e.kind === 'merge' && c.a === e.decision.a && c.b === e.decision.b;
        return h('tr', { class: chosen ? 'chosen' : (!c.legal ? 'blocked' : '') }, h('td', `${c.a}–${c.b}`), h('td', `${c.affinity}${c.parts.length > 1 ? L(`（${c.parts.map(p => p.w).join('+')}）`, ` (${c.parts.map(p => p.w).join('+')})`) : ''}`), h('td', String(c.size)), h('td', chosen ? L('选中', 'chosen') : !c.legal ? L('超容量', 'over capacity') : ''));
      }))) : h('p.muted', L('初始状态：还没有比较候选。', 'Initial state: no candidates compared yet.')));
    const lines = e.kind === 'singletons' ? [1] : e.kind === 'stopped' ? [2, 3, 4, 5] : (i === run.events.length - 1 ? [6, 7, 2, 8] : [3, 4, 6, 7]);
    pseudo.merge?.show(lines, e.kind === 'merge' ? L(`本步：${e.decision.a} + ${e.decision.b}，亲和度 ${e.decision.affinity}`, `This step: ${e.decision.a} + ${e.decision.b}, affinity ${e.decision.affinity}`) : '');
  }
  buildToolbar(); recompute();
}

/* ---------- code lab: run the learner's greedy_pair_merge and compare every step with the course engine ---------- */
const DIGITS = { nodes: ['P', 'Q', 'R', 'S', 'T', 'U'], edges: [['P', 'Q', 10], ['Q', 'R', 2], ['R', 'S', 9], ['S', 'T', 1.5], ['T', 'U', 10], ['P', 'U', 2]],
  positions: { P: [160, 110], Q: [400, 90], R: [560, 230], S: [430, 400], T: [180, 400], U: [70, 250] } };
const FRESH = { nodes: ['K', 'L', 'M', 'N', 'O', 'V'], edges: [['K', 'L', 3], ['L', 'M', 3], ['K', 'M', 1], ['M', 'N', 2.5], ['N', 'O', 4], ['O', 'V', 4], ['N', 'V', 1]],
  positions: { K: [90, 120], L: [300, 80], M: [250, 290], N: [450, 300], O: [620, 170], V: [640, 400] } };
function visualize(root, api) {
  const EXAMPLES = {
    k2: { name: L('G01，K = 2', 'G01, K = 2'), graph: G01, positions: G01.positions, k: 2, capacity: null },
    cap2: { name: L('G01，K = 2，容量 2', 'G01, K = 2, capacity 2'), graph: G01, positions: G01.positions, k: 2, capacity: 2 },
    digits: { name: L('多位数权重（10、9、2、1.5）', 'Multi-digit weights (10, 9, 2, 1.5)'), graph: DIGITS, positions: DIGITS.positions, k: 2, capacity: null },
    fresh: { name: L('一张新图（练习里没出现过），K = 2', 'A new graph (not in the exercise), K = 2'), graph: FRESH, positions: FRESH.positions, k: 2, capacity: null }
  };
  let ex = 'k2';
  const stage = h('div.lab-stage'), side = h('div.lab-side'), metricBox = h('div.metrics'), statusBox = h('div.status'), stepBox = h('div.decision'), playerBox = h('div');
  const match = h('p.match'), toolbar = h('div.lab-toolbar');
  const go = h('button.btn.primary', { type: 'button', onclick: runMine }, L('▶ 用我的代码运行', '▶ Run my code'));
  toolbar.append(select(L('例子', 'Example'), Object.entries(EXAMPLES).map(([key, v]) => [key, v.name]), ex, v => { ex = v; }), go);
  side.append(metricBox, statusBox, h('h4', L('你的每一步 · 引擎的每一步', 'Your steps · the engine’s steps')), stepBox, playerBox);
  root.append(h('h3', L('用你的代码跑一遍', 'Watch your own code run')),
    h('p.muted', L('这里调用的是你在上面写的 greedy_pair_merge()，不是课程引擎。左边的图逐步画出你的合并；右边逐步对照课程引擎的簇和 cut。',
      'This calls the greedy_pair_merge() you wrote above, not the course engine. The graph draws your merges step by step; the table compares your clusters and cut with the course engine at every step.')),
    toolbar, h('div.lab', {}, h('div', {}, stage), side), match);
  let gv, mine = [], ref = [], cur = null, mineRes = null;
  const player = new Player(playerBox, { onIndex: show, speed: 1200 });
  stage.append(h('p.muted', { style: 'padding:40px 10px;text-align:center' }, L('写好函数后，按“用我的代码运行”。', 'Once your functions are written, press “Run my code”.')));
  const norm = list => [...list].map(s => s.split('').sort().join('')).sort().join(' | ');

  async function runMine() {
    if (api.busy) return;
    cur = EXAMPLES[ex];
    const g = cur.graph;
    const edges = g.edges.map(x => Array.isArray(x) ? x : [x.u, x.v, x.w]);
    const code = `import json, importlib.util
spec = importlib.util.spec_from_file_location('impl_v', 'impl.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
r = m.greedy_pair_merge(${JSON.stringify(g.nodes)}, [tuple(x) for x in ${JSON.stringify(edges)}], ${cur.k}, ${cur.capacity ?? 'None'})
json.dumps({"parts": list(r["parts"]), "cutsize": r["cutsize"], "target_reached": r["target_reached"], "stop_reason": r["stop_reason"], "log": [{"clusters": list(e["clusters"]), "cutsize": e["cutsize"], "pair": e.get("pair")} for e in r["log"]]})`;
    api.setBusy(true); go.disabled = true; match.className = 'match'; match.textContent = L('运行中…', 'Running…');
    try {
      const { value } = await api.run(code);
      mineRes = JSON.parse(value);
      mine = mineRes.log;
      const run = M.run(g, { k: cur.k, capacity: cur.capacity });
      ref = run.events.filter(e => e.kind !== 'stopped').map(e => ({ clusters: e.after.map(c => c.label), cutsize: e.metrics.cut, pair: e.decision ? `${e.decision.a}-${e.decision.b}` : null }));
      const same = (a, b) => a && b && norm(a.clusters) === norm(b.clusters) && Math.abs(a.cutsize - b.cutsize) < 1e-9;
      const n = Math.max(mine.length, ref.length);
      const diff = [...Array(n).keys()].find(i => !same(mine[i], ref[i])) ?? -1;
      const endOk = diff < 0 && mineRes.stop_reason === run.result.stopReason && mineRes.target_reached === run.result.targetReached;
      match.className = 'match ' + (endOk ? 'ok' : 'no');
      match.textContent = endOk
        ? L(`✓ 与课程引擎每一步一致：${ref.length - 1} 次合并，cut ${ref.map(r => r.cutsize).join(' → ')}，停止原因 ${run.result.stopReason}。`, `✓ Agrees with the course engine at every step: ${ref.length - 1} merges, cut ${ref.map(r => r.cutsize).join(' → ')}, stop reason ${run.result.stopReason}.`)
        : diff < 0
          ? L(`✗ 每一步都对，但结尾不同：你报告 ${mineRes.stop_reason} / 达到 K = ${mineRes.target_reached}，引擎是 ${run.result.stopReason} / ${run.result.targetReached}。`, `✗ Every step matches, but the ending differs: you report ${mineRes.stop_reason} / K reached = ${mineRes.target_reached}; the engine has ${run.result.stopReason} / ${run.result.targetReached}.`)
          : !mine[diff]
            ? L(`✗ 你在第 ${diff} 步之后就停了；引擎还合并了 ${ref[diff].pair}。`, `✗ You stopped after step ${diff - 1}; the engine also merges ${ref[diff].pair}.`)
            : !ref[diff]
              ? L(`✗ 你多合并了一步（${mine[diff].pair}）：引擎在这里已经停止。是否忘了检查 K 或容量？`, `✗ You merged one step too many (${mine[diff].pair}): the engine has stopped here. Did you forget to check K or the capacity?`)
              : L(`✗ 第 ${diff} 步开始不同：你的是 ${norm(mine[diff].clusters)}（cut ${mine[diff].cutsize}），引擎是 ${norm(ref[diff].clusters)}（cut ${ref[diff].cutsize}）。`, `✗ Differs from step ${diff}: yours is ${norm(mine[diff].clusters)} (cut ${mine[diff].cutsize}), the engine’s ${norm(ref[diff].clusters)} (cut ${ref[diff].cutsize}).`);
      gv = new GraphView(stage, { graph: g, positions: cur.positions, title: L('你的代码的合并过程', 'Your code’s merges'), radius: 24 });
      player.load(mine.length ? mine.map((e, i) => ({ ...e, i })) : [{ clusters: [], cutsize: 0, i: 0 }]);
    } catch (err) {
      match.className = 'match no';
      const msg = String(err.message || err).split('\n').filter(Boolean);
      match.textContent = err.reason ? L('已停止。', 'Stopped.') : L('你的代码运行出错：', 'Your code raised an error: ') + msg.slice(-1)[0];
    } finally { api.setBusy(false); go.disabled = false; }
  }
  function show(i, e) {
    if (!gv || !cur) return;
    const after = e.clusters.map(lab => ({ label: lab, members: lab.split(''), size: lab.length }));
    if (after.length) drawState(gv, cur.graph, after, { summary: i === 0 ? L(`你的第 0 步：单点簇，cut ${e.cutsize}`, `Your step 0: singletons, cut ${e.cutsize}`) : L(`你的第 ${i} 步：合并 ${e.pair}，cut ${e.cutsize}`, `Your step ${i}: merge ${e.pair}, cut ${e.cutsize}`) });
    metrics(metricBox, [[L('你的步数', 'Your steps'), Math.max(0, mine.length - 1)], [L('引擎步数', 'Engine steps'), Math.max(0, ref.length - 1)], ['cut', e.cutsize]]);
    const r = ref[i], ok = r && norm(r.clusters) === norm(e.clusters) && Math.abs(r.cutsize - e.cutsize) < 1e-9;
    status(statusBox, ok ? '' : 'cycle', ok ? L('这一步与引擎一致。', 'This step matches the engine.') : L(`这一步与引擎不同：引擎是 ${r ? `${norm(r.clusters)}，cut ${r.cutsize}` : '（已停止）'}。`, `This step differs: the engine has ${r ? `${norm(r.clusters)}, cut ${r.cutsize}` : '(stopped)'}.`));
    const n = Math.max(mine.length, ref.length);
    stepBox.replaceChildren(h('table', {}, h('thead', {}, h('tr', {}, h('th', '#'), h('th', L('你的', 'Yours')), h('th', L('引擎', 'Engine')))),
      h('tbody', {}, [...Array(n).keys()].map(k => {
        const a = mine[k], b = ref[k], eq = a && b && norm(a.clusters) === norm(b.clusters) && Math.abs(a.cutsize - b.cutsize) < 1e-9;
        return h('tr', { class: k === i ? 'chosen' : '' }, h('td', String(k)), h('td', { style: eq ? '' : 'color:var(--c-red)' }, a ? `${a.pair || '—'} · ${a.cutsize}` : '—'), h('td', b ? `${b.pair || '—'} · ${b.cutsize}` : '—'));
      }))));
  }
}

bootModule({ moduleId: 'm03-greedy-pair-merge', display: 'Module 03', challenges, lab, visualize });
