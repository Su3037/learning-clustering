// Module 08 lab: white-box FM — legal candidates, FS/TE, gain buckets, cumulative gains (engines/fm.js).
import { h } from '../../assets/core.js';
import { L } from '../../assets/i18n.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as FM from '../../engines/fm.js';
import { G01 } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const MULTI = { nodes: ['A', 'B', 'C', 'D', 'E', 'F'], nets: [{ id: 'bus', pins: ['A', 'B', 'C', 'D'], w: 2 }], edges: [['A', 'E', 3], ['C', 'F', 2], ['E', 'F', 1], ['B', 'D', 1]],
  seed: { A: 0, B: 0, E: 0, C: 1, D: 1, F: 1 }, maxDiff: 2, positions: { A: [150, 120], B: [150, 300], E: [300, 420], C: [520, 120], D: [520, 300], F: [620, 420] } };
const PRESETS = {
  seed: { name: L('课程种子 AE | BCD（maxDiff 1）', 'Course seed AE | BCD (maxDiff 1)'), graph: G01, positions: G01.positions, seed: FM.SEED, maxDiff: 1 },
  escape: { name: L('替换反例：先负后正（maxDiff 2）', 'Replacement example: negative first, then positive (maxDiff 2)'), graph: FM.NEG_ESCAPE, positions: FM.NEG_ESCAPE.positions, seed: FM.NEG_ESCAPE.seed, maxDiff: 2 },
  seven: { name: L('原附件第三例：7 节点普通图', 'The attachment’s third case: an ordinary 7-node graph'), graph: FM.SEVEN_NODE, positions: null, seed: FM.SEVEN_NODE.seed, maxDiff: 1 },
  legacy: { name: L('原附件 hillclimb（说明已证伪，仅供审查）', 'The attachment’s hillclimb (its claim is disproved; for auditing only)'), graph: FM.LEGACY_HILLCLIMB, positions: { A: [180, 95], B: [180, 285], C: [380, 95], D: [380, 285], E: [580, 95], F: [580, 285] }, seed: FM.LEGACY_HILLCLIMB.seed, maxDiff: 2 },
  multi: { name: L('拓展：含 4 引脚 net', 'Extension: with a 4-pin net'), graph: MULTI, positions: MULTI.positions, seed: MULTI.seed, maxDiff: 2 }
};
const signed = g => (g > 0 ? '+' : '') + g;
const movedOf = e => e.decision.match(/移动 (\S+)（/)[1];  // the engine's event text is data; only the node name is read from it
/** Nets drawn as edges: a multi-pin net becomes a star from its first pin, labelled with the net's name. */
const displayOf = g => ({ nodes: g.nodes, edges: [...(g.edges || []), ...(g.nets || []).flatMap(n => n.pins.slice(1).map(q => [n.pins[0], q, `${n.id}`]))] });
const netDash = g => Object.fromEntries((g.nets || []).flatMap(n => n.pins.slice(1).map(q => [[n.pins[0], q].sort().join('|'), 'stroke-dasharray:3 5;stroke:#c2a6e6'])));
const SIDE_LABELS = [L('青：0 侧', 'teal: side 0'), L('蓝：1 侧', 'blue: side 1')];

function cumChart(gains, bestK, shown) {
  const W = 300, H = 140, base = 78, mx = Math.max(1, ...gains.map(Math.abs)), bw = Math.min(36, (W - 30) / gains.length - 6);
  const svg = h('svg', { viewBox: `0 0 ${W} ${H}`, class: 'gv', role: 'img', 'aria-label': L(`累计收益 ${gains.join('，')}`, `Cumulative gains ${gains.join(', ')}`) }, h('line', { x1: 14, y1: base, x2: W - 4, y2: base, stroke: '#5d7c80' }));
  gains.forEach((g, k) => {
    if (k > shown) return;
    const x = 18 + k * (bw + 6), hg = 56 * Math.abs(g) / mx, best = bestK !== null && k === bestK;
    svg.append(h('rect', { x, y: g >= 0 ? base - hg : base, width: bw, height: Math.max(2, hg), rx: 3, fill: best ? '#d8bb78' : g > 0 ? '#77cdbb' : g < 0 ? '#db7b72' : '#bcd2d0' }),
      h('text', { x: x + bw / 2, y: g >= 0 ? base - hg - 4 : base + hg + 12, 'text-anchor': 'middle', class: 'w', style: 'font-size:11px' }, signed(g)),
      h('text', { x: x + bw / 2, y: H - 4, 'text-anchor': 'middle', class: 'side-label', style: 'font-size:10px' }, `k${k}`));
  });
  return svg;
}

async function lab(root, { pseudo }) {
  let presetId = 'seed', maxDiff = 1, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), gainBox = h('div.decision'), bucketBox = h('div.lab-note'), chartBox = h('div'), playerBox = h('div');
  const traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar'), note = h('p.lab-note');
  root.replaceChildren(toolbar, note, h('div.lab', {}, h('div', {}, stage, h('div.legend', {},
    h('span', {}, h('b', { style: 'background:#77cdbb' }), L('0 侧', 'Side 0')), h('span', {}, h('b', { style: 'background:#8fb1e6' }), L('1 侧', 'Side 1')),
    h('span', {}, L('白色虚线圈：已锁定', 'White dashed ring: locked')), h('span', {}, h('b', { style: 'background:#db7b72' }), L('红圈：收益更大但不合法', 'Red ring: larger gain but not legal')), h('span', {}, h('b', { style: 'background:#d8bb78' }), L('金圈：本步移动', 'Gold ring: moved this step')))), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', L('累计收益', 'Cumulative gain')), chartBox, h('h4', L('所有节点的收益（移动前）', 'Every node’s gain (before the move)')), gainBox, bucketBox, playerBox);
  let gv;
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const eventText = e => e.kind === 'pass-start' ? L('本轮开始', 'pass starts') : e.kind === 'trial-move' ? L(`试探移动 ${movedOf(e)}`, `trial move ${movedOf(e)}`)
    : e.prefix.bestK ? L(`保留前 ${e.prefix.bestK} 步`, `keep the first ${e.prefix.bestK}`) : L('保留空前缀', 'keep the empty prefix');
  const trace = new TraceInspector(traceBox, { columns: [{ label: L('轮', 'Pass'), get: e => e.phase.split('-')[1] }, { label: L('事件', 'Event'), get: eventText },
    { label: L('收益', 'Gain'), get: e => e.trialGain ?? '' }, { label: 'cut', get: e => e.metrics.cut }, { label: L('被挡住的更大收益', 'Larger gains blocked'), get: e => (e.blocked || []).join(' ') }], onPick: i => player.go(i) });

  function buildToolbar() {
    toolbar.replaceChildren(
      select(L('例子', 'Example'), Object.entries(PRESETS).map(([k, p]) => [k, p.name]), presetId, v => { presetId = v; maxDiff = PRESETS[v].maxDiff; buildToolbar(); recompute(true); }),
      select(L('平衡 maxDiff', 'Balance maxDiff'), [0, 1, 2, 3].map(x => [String(x), `|n₀ − n₁| ≤ ${x}`]), String(maxDiff), v => { maxDiff = +v; recompute(); }),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m08-fiduccia-mattheyses', { preset: presetId, options: { maxDiff, initial: PRESETS[presetId].seed }, input: PRESETS[presetId].graph, result: run.result, events: run.events }) }, L('导出运行记录', 'Export the run')));
    note.textContent = presetId === 'legacy' ? L('注意：原附件对这个案例的文字说明（初始 cut 9、所有合法收益 ≤ 0、降到 4）与数据不符。这里按数据真实运行，供你自己核验。', 'Note: the attachment’s text for this case (initial cut 9, every legal gain ≤ 0, down to 4) does not match its data. Here it runs on the data as given, so you can check it yourself.')
      : presetId === 'multi' ? L('拓展：bus 是一个 4 引脚 net（图上画成虚线示意）。收益按两侧引脚计数，不是把 net 拆成边。', 'Extension: bus is a 4-pin net (drawn dashed). Gains count the pins on each side; the net is not split into edges.') : '';
  }
  function recompute(newGraph = false) {
    const p = PRESETS[presetId];
    run = FM.run(p.graph, { initial: p.seed, maxDiff });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join(L('；', '; ')) + L('（试试更大的 maxDiff）', ' (try a larger maxDiff)'); trace.load([]); return; }
    err.textContent = '';
    if (newGraph || !gv) gv = new GraphView(stage, { graph: displayOf(p.graph), positions: p.positions, title: L('FM 实验图', 'FM lab graph') });
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const p = PRESETS[presetId], passNo = +e.phase.split('-')[1], pass = run.result.passes[passNo - 1];
    const moved = e.kind === 'trial-move' ? movedOf(e) : null;
    const before = e.kind === 'trial-move' ? run.events[i - 1] : e;
    const blocked = e.kind === 'trial-move' ? e.blocked : [];
    gv.render({ groups: e.after, groupOrder: [0, 1], cut: true, locked: e.locks || [], focus: moved ? [moved] : [], blocked, edgeStyle: netDash(p.graph), sideLabels: SIDE_LABELS,
      summary: L(`第 ${passNo} 轮：cut ${e.metrics.cut}`, `pass ${passNo}: cut ${e.metrics.cut}`) });
    const stepIdx = e.kind === 'trial-move' ? pass.moves.findIndex(m => m.node === moved) + 1 : e.kind === 'best-prefix' ? pass.moves.length : 0;
    chartBox.replaceChildren(cumChart(pass.prefixGains, e.kind === 'best-prefix' ? pass.bestK : null, stepIdx));
    const n0 = Object.values(e.after).filter(s => s === 0).length, n1 = Object.values(e.after).length - n0;
    metrics(metricBox, [[L('轮', 'Pass'), passNo], ['cut', e.metrics.cut], [L('两侧人数', 'Side sizes'), `${n0} : ${n1}`]]);
    const parts = xs => xs.map(x => `${x.net}:${x.w}`).join('+') || '0';
    if (e.kind === 'pass-start') status(statusBox, '', L(`第 ${passNo} 轮开始：全部解锁，cut ${pass.startCut}。`, `Pass ${passNo} starts: everything unlocked, cut ${pass.startCut}.`));
    else if (e.kind === 'trial-move') {
      const m = pass.moves[stepIdx - 1];
      status(statusBox, m.gain < 0 ? 'limit' : '', L(`试探移动 ${moved}：收益 ${signed(m.gain)}（FS ${parts(m.fs)}，TE ${parts(m.te)}），cut ${m.cutBefore} → ${m.cutAfter}。${blocked.length ? `${blocked.join('、')} 收益更大但不合法。` : ''}`,
        `Trial move ${moved}: gain ${signed(m.gain)} (FS ${parts(m.fs)}, TE ${parts(m.te)}), cut ${m.cutBefore} → ${m.cutAfter}.${blocked.length ? ` ${blocked.join(', ')} ${blocked.length > 1 ? 'have' : 'has'} a larger gain but ${blocked.length > 1 ? 'are' : 'is'} not legal.` : ''}`));
    } else status(statusBox, pass.bestK ? '' : 'blocked', L(`${eventText(e)}：接受 cut ${e.metrics.cut}（试探终点 ${e.metrics.rollbackFromCut}）。${pass.bestK ? '进入下一轮。' : '空前缀 → 停止。'}`,
      `${pass.bestK ? `Keep the first ${pass.bestK}` : 'Keep the empty prefix'}: accept cut ${e.metrics.cut} (the trials ended at ${e.metrics.rollbackFromCut}). ${pass.bestK ? 'On to the next pass.' : 'Empty prefix → stop.'}`));
    const gains = (before.gains || []);
    gainBox.replaceChildren(gains.length ? h('table', {}, h('thead', {}, h('tr', {}, h('th', L('节点', 'Node')), h('th', L('侧', 'Side')), h('th', L('收益', 'Gain')), h('th', L('状态', 'Status')))),
      h('tbody', {}, gains.map(g => h('tr', { class: g.node === moved ? 'chosen' : (!g.locked && !g.legal ? 'blocked' : '') }, h('td', g.node), h('td', String(g.side)), h('td', signed(g.gain)),
        h('td', g.locked ? L('已锁定', 'locked') : g.legal ? (g.node === moved ? L('选中', 'chosen') : L('合法', 'legal')) : L('不合法', 'not legal')))))) : h('p.muted', L('本轮结束。', 'The pass is over.')));
    const buckets = before.buckets || [];
    bucketBox.textContent = buckets.length ? L('按收益分组的“桶”（每步扫描生成，不是 O(P) 结构）：', 'Nodes grouped by gain, the “buckets” (rebuilt by a scan each step, not an O(P) structure): ') + buckets.map(b => `[${signed(b.gain)}] ${b.nodes.join(' ')}`).join('　') : '';
    pseudo.fm?.show(e.kind === 'pass-start' ? [1, 2] : e.kind === 'trial-move' ? [3, 4, 5, 6] : (pass.bestK ? [7, 8] : [7, 8, 9]), '');
  }
  buildToolbar(); recompute(true);
}

/** A new graph for the code lab: a ring of six with one chord. Three passes: a blocked larger gain in pass 1, a −2 step that opens a +4 in pass 2, then the empty prefix. */
const RING = {
  nodes: ['P', 'Q', 'R', 'S', 'T', 'U'],
  edges: [['P', 'Q', 3], ['Q', 'R', 1], ['R', 'S', 3], ['S', 'T', 1], ['T', 'U', 3], ['U', 'P', 1], ['P', 'S', 2]],
  positions: { P: [140, 90], Q: [360, 60], R: [580, 90], S: [580, 330], T: [360, 380], U: [140, 330] }
};
const RING_SEED = { P: 0, R: 0, T: 0, Q: 1, S: 1, U: 1 };

/** Code lab: run the learner's fm_refine() (built on their gain() and legal_moves()) and compare every pass with the engine. */
function visualize(root, api) {
  const CASES = [
    { name: 'G01 · AE|BCD · maxDiff 1', graph: G01, seed: FM.SEED, maxDiff: 1 },
    { name: 'G01 · BD|ACE · maxDiff 1', graph: G01, seed: { A: 1, B: 0, C: 1, D: 0, E: 1 }, maxDiff: 1 },
    { name: 'G01 · AB|CDE · maxDiff 1', graph: G01, seed: { A: 0, B: 0, C: 1, D: 1, E: 1 }, maxDiff: 1 },
    { name: L('替换反例 · maxDiff 2', 'Replacement example · maxDiff 2'), graph: FM.NEG_ESCAPE, seed: FM.NEG_ESCAPE.seed, maxDiff: 2 },
    { name: L('7 节点普通图 · maxDiff 1', 'Ordinary 7-node graph · maxDiff 1'), graph: FM.SEVEN_NODE, seed: FM.SEVEN_NODE.seed, maxDiff: 1 },
    { name: L('六点环（新图）· maxDiff 2', 'Ring of six (new graph) · maxDiff 2'), graph: RING, seed: RING_SEED, maxDiff: 2 },
    { name: L('拓展：4 引脚 net · maxDiff 2', 'Extension: 4-pin net · maxDiff 2'), graph: MULTI, seed: MULTI.seed, maxDiff: 2 }
  ];
  const stage = h('div.lab-stage'), side = h('div.lab-side'), statusBox = h('div.status'), detail = h('div.decision'), tableBox = h('div'), match = h('p.match');
  const go = h('button.btn.primary', { type: 'button', onclick: runMine }, L('▶ 用我的代码运行', '▶ Run my code'));
  side.append(statusBox, detail);
  root.append(h('h3', L('用你的代码跑一遍', 'Watch your own code run')),
    h('p.muted', L('这里调用你写的 gain() 和 legal_moves()（经由已提供的 fm_pass() 和 fm_refine()），在 7 个情形上逐轮对照课程引擎：每一步移动哪个点、收益多少、保留几步、最终 cut。最后一个情形含 4 引脚 net。点表格的一行，左边画出你的结果。',
      'This calls the gain() and legal_moves() you wrote (through the provided fm_pass() and fm_refine()) and compares them pass by pass with the course engine on seven cases: which node each step moves, its gain, how many steps are kept, and the final cut. The last case has a 4-pin net. Click a row to draw your result on the left.')),
    h('div.lab-toolbar', {}, go), tableBox, h('div.lab', {}, h('div', {}, stage), side), match);
  stage.append(h('p.muted', { style: 'padding:40px 10px;text-align:center' }, L('写好两个函数后，按“用我的代码运行”。', 'Once both functions are written, press “Run my code”.')));
  let rows = [];
  const passesText = ps => ps.map(p => `[${p.moves.map(([v, g]) => v + signed(g)).join(' ')}] → ${p.k}`).join('  ');

  async function runMine() {
    if (api.busy) return;
    const payload = CASES.map(c => ({ graph: { nodes: c.graph.nodes.map(n => n.id ?? n), edges: (c.graph.edges || []).map(e => Array.isArray(e) ? e : [e.u, e.v, e.w]), nets: c.graph.nets || [] }, seed: c.seed, maxDiff: c.maxDiff }));
    const code = `import json, importlib.util
spec = importlib.util.spec_from_file_location('impl_v', 'impl.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
out = []
for c in json.loads(${JSON.stringify(JSON.stringify(payload))}):
    try:
        g = c["graph"]
        g["edges"] = [tuple(e) for e in g["edges"]]
        r = m.fm_refine(g, c["seed"], c["maxDiff"])
        out.append({"cut": r["cut"], "assignment": r["assignment"],
                    "passes": [{"moves": [[x["node"], x["gain"]] for x in p["trial_moves"]], "k": p["best_prefix"]} for p in r["passes"]]})
    except Exception as e:
        out.append({"error": type(e).__name__ + ": " + str(e)})
json.dumps(out)`;
    api.setBusy(true); go.disabled = true; match.className = 'match'; match.textContent = L('运行中…', 'Running…');
    try {
      const mine = JSON.parse((await api.run(code)).value);
      rows = CASES.map((c, i) => {
        const ref = FM.run(c.graph, { initial: c.seed, maxDiff: c.maxDiff }).result, me = mine[i];
        const refPasses = ref.passes.map(p => ({ moves: p.moves.map(x => [x.node, x.gain]), k: p.bestK }));
        const same = !me.error && me.cut === ref.cut && JSON.stringify(me.passes) === JSON.stringify(refPasses);
        return { c, ref, refPasses, me, ok: same };
      });
      const ok = rows.filter(r => r.ok).length;
      match.className = 'match ' + (ok === rows.length ? 'ok' : 'no');
      match.textContent = ok === rows.length
        ? L('✓ 7 个情形逐轮与课程引擎一致：同样的移动、同样的收益、同样的最佳前缀。', '✓ All seven cases agree with the course engine pass by pass: the same moves, the same gains, the same best prefixes.')
        : L(`× ${rows.length - ok} 个情形与引擎不同（红色）。点那一行看差在哪里。`, `× ${rows.length - ok} of the cases differ from the engine (in red). Click a row to see where.`);
      drawTable(); pick(rows.findIndex(r => !r.ok) >= 0 ? rows.findIndex(r => !r.ok) : 0);
    } catch (err) {
      match.className = 'match no';
      const msg = String(err.message || err).split('\n').filter(Boolean);
      match.textContent = err.reason ? L('已停止。', 'Stopped.') : L('你的代码运行出错：', 'Your code raised an error: ') + msg.slice(-1)[0];
    } finally { api.setBusy(false); go.disabled = false; }
  }
  function drawTable(sel = -1) {
    tableBox.replaceChildren(h('table.codelab-cases', {}, h('thead', {}, h('tr', {}, h('th', L('情形', 'Case')), h('th', L('你的各轮移动 → 保留步数', 'Your moves per pass → steps kept')), h('th', L('你的 cut', 'Your cut')), h('th', L('引擎', 'Engine')))),
      h('tbody', {}, rows.map((r, i) => h('tr', { class: i === sel ? 'chosen' : '', style: 'cursor:pointer', onclick: () => pick(i) },
        h('td', r.c.name),
        ...(r.me.error ? [h('td', { colspan: 2, style: 'color:var(--c-red)' }, r.me.error)]
          : [h('td', { style: r.ok ? '' : 'color:var(--c-red);font-weight:600' }, passesText(r.me.passes)), h('td', { style: r.me.cut === r.ref.cut ? '' : 'color:var(--c-red);font-weight:600' }, String(r.me.cut))]),
        h('td', `${passesText(r.refPasses)} · cut ${r.ref.cut}`))))));
  }
  function pick(i) {
    const r = rows[i]; if (!r) return;
    drawTable(i);
    const groups = r.me.assignment || r.ref.assignment;
    new GraphView(stage, { graph: displayOf(r.c.graph), positions: r.c.graph.positions || null, title: L('你的代码的结果', 'Your code’s result') })
      .render({ groups, groupOrder: [0, 1], cut: true, edgeStyle: netDash(r.c.graph), sideLabels: SIDE_LABELS, summary: L(`你的结果：cut ${r.me.cut ?? '—'}`, `Your result: cut ${r.me.cut ?? '—'}`) });
    status(statusBox, r.ok ? '' : 'cycle', r.ok ? L('这个情形与引擎一致。', 'This case agrees with the engine.') : L('这个情形与引擎不同：对照右表，找第一处不同的移动或保留步数。', 'This case differs from the engine: compare with the right-hand column and find the first move or kept count that differs.'));
    const p1 = r.ref.passes[0], first = p1.moves[0];
    detail.replaceChildren(h('p', {}, L(`引擎第 1 轮：${p1.moves.map(x => `${x.node} ${signed(x.gain)}`).join('，')}；保留前 ${p1.bestK} 步。`, `Engine pass 1: ${p1.moves.map(x => `${x.node} ${signed(x.gain)}`).join(', ')}; keeps the first ${p1.bestK}.`)),
      first && first.blockedBetter.length ? h('p.muted', L(`第一步：${first.blockedBetter.join('、')} 收益更大，但移动后会破坏平衡，所以选 ${first.node}。`, `First step: ${first.blockedBetter.join(', ')} ${first.blockedBetter.length > 1 ? 'have' : 'has'} a larger gain but would break the balance, so ${first.node} is chosen.`)) : '');
  }
}

bootModule({ moduleId: 'm08-fiduccia-mattheyses', display: 'Module 08', challenges, lab, visualize });
