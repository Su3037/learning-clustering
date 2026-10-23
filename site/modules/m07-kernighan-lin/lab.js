// Module 07 lab: KL passes with trial swaps, locks, cumulative gains and best-prefix rollback (engines/kl.js).
import { h } from '../../assets/core.js';
import { L } from '../../assets/i18n.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as KL from '../../engines/kl.js';
import { G01, requireGraph } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const SEEDS = { 'AE|BCD': KL.SEED, 'AB|CDE': { A: 0, B: 0, C: 1, D: 1, E: 1 }, 'BD|ACE': { A: 1, B: 0, C: 1, D: 0, E: 1 }, 'CE|ABD': { A: 1, B: 1, C: 0, D: 1, E: 0 } };
const pairOf = e => e.decision.replace('试探交换 ', '').split('↔');  // the engine's event text is data; only the pair is read from it
const signed = g => (g > 0 ? '+' : '') + g;

function prefixChart(gains, bestK, shown) {
  const W = 300, H = 140, base = 80, mx = Math.max(1, ...gains.map(Math.abs)), bw = Math.min(46, (W - 40) / gains.length - 8);
  const svg = h('svg', { viewBox: `0 0 ${W} ${H}`, class: 'gv', role: 'img', 'aria-label': L(`累计收益 ${gains.join('，')}，最佳前缀 k=${bestK}`, `Cumulative gains ${gains.join(', ')}, best prefix k=${bestK}`) },
    h('line', { x1: 20, y1: base, x2: W - 6, y2: base, stroke: '#5d7c80' }));
  gains.forEach((g, k) => {
    if (k > shown) return;
    const x = 26 + k * (bw + 10), hgt = 60 * Math.abs(g) / mx, best = bestK !== null && k === bestK;
    svg.append(h('rect', { x, y: g >= 0 ? base - hgt : base, width: bw, height: Math.max(2, hgt), rx: 3, fill: best ? '#d8bb78' : g > 0 ? '#77cdbb' : g < 0 ? '#db7b72' : '#bcd2d0' }),
      h('text', { x: x + bw / 2, y: g >= 0 ? base - hgt - 4 : base + hgt + 13, 'text-anchor': 'middle', class: 'w', style: 'font-size:12px' }, signed(g)),
      h('text', { x: x + bw / 2, y: H - 4, 'text-anchor': 'middle', class: 'side-label', style: 'font-size:11px' }, `k=${k}`));
    if (best) svg.append(h('rect', { x: x - 4, y: 8, width: bw + 8, height: H - 22, fill: 'none', stroke: '#d8bb78', 'stroke-dasharray': '4 3', rx: 4 }));
  });
  return svg;
}

async function lab(root, { pseudo }) {
  let seed = 'AE|BCD', weights = {}, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), candBox = h('div.decision'), chartBox = h('div'), playerBox = h('div');
  const traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, h('div.legend', {},
    h('span', {}, h('b', { style: 'background:#77cdbb' }), L('左侧', 'Left side')), h('span', {}, h('b', { style: 'background:#8fb1e6' }), L('右侧', 'Right side')),
    h('span', {}, L('白色虚线圈：本轮已锁定', 'White dashed ring: locked this pass')), h('span', {}, h('b', { style: 'background:#d8bb78' }), L('金圈：本步交换的一对', 'Gold ring: the pair swapped this step')))), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', L('累计收益（前 k 步）', 'Cumulative gain (first k steps)')), chartBox, h('h4', L('本步的候选（未锁定的跨侧对）', 'This step’s candidates (unlocked cross pairs)')), candBox, playerBox);
  const gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: L('KL 实验图', 'KL lab graph') });
  const player = new Player(playerBox, { onIndex: show, speed: 1600 });
  const passName = e => L(`第 ${e.phase.split('-')[1]} 轮`, `pass ${e.phase.split('-')[1]}`);
  const eventText = e => e.kind === 'pass-start' ? L('本轮开始', 'pass starts') : e.kind === 'trial-swap' ? L(`试探 ${pairOf(e).join('↔')}`, `trial ${pairOf(e).join('↔')}`)
    : e.prefix.bestK ? L(`保留前 ${e.prefix.bestK} 步`, `keep the first ${e.prefix.bestK}`) : L('保留空前缀（不改变）', 'keep the empty prefix (no change)');
  const trace = new TraceInspector(traceBox, { columns: [{ label: L('阶段', 'Phase'), get: passName },
    { label: L('事件', 'Event'), get: eventText },
    { label: L('收益', 'Gain'), get: e => e.trialGain ?? '' }, { label: 'cut', get: e => e.metrics.cut }, { label: L('累计', 'Cumulative'), get: e => e.metrics.cumulative ?? '' }], onPick: i => player.go(i) });

  const graph = () => ({ nodes: G01.nodes, edges: G01.edges.map(e => ({ ...e, w: weights[`${e.u}|${e.v}`] ?? e.w })) });
  function buildToolbar() {
    const edgeSel = h('select', { 'aria-label': L('选择要修改的边', 'Choose an edge to change') }, G01.edges.map(e => h('option', { value: `${e.u}|${e.v}` }, `${e.u}–${e.v}`)));
    const wIn = h('input', { type: 'number', min: 1, max: 20, step: 1, 'aria-label': L('新权重', 'New weight') });
    const sync = () => { wIn.value = graph().edges.find(x => `${x.u}|${x.v}` === edgeSel.value).w; };
    edgeSel.addEventListener('change', sync); sync();
    wIn.addEventListener('change', () => { const w = Number(wIn.value); if (!(w > 0 && w <= 20)) { err.textContent = L('权重须为 1–20。', 'A weight must be 1–20.'); return; } err.textContent = ''; weights[edgeSel.value] = w; recompute(); });
    toolbar.replaceChildren(
      select(L('初始二分（左 | 右）', 'Initial bisection (left | right)'), Object.keys(SEEDS).map(k => [k, k]), seed, v => { seed = v; recompute(); }),
      h('label', {}, L('改一条边', 'Change an edge'), edgeSel), h('label', {}, L('新权重', 'New weight'), wIn),
      h('button.btn.small', { type: 'button', onclick: () => { weights = {}; buildToolbar(); recompute(); } }, L('恢复原权重', 'Restore the weights')),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m07-kernighan-lin', { options: { initial: SEEDS[seed] }, input: graph(), result: run.result, events: run.events }) }, L('导出运行记录', 'Export the run')));
  }
  function recompute() {
    run = KL.run(graph(), { initial: SEEDS[seed] });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join(L('；', '; ')); return; }
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const passNo = +e.phase.split('-')[1], pass = run.result.passes[passNo - 1];
    const side = e.after, locked = e.locks || [];
    const focus = e.kind === 'trial-swap' ? pairOf(e) : [];
    gv.render({ groups: side, groupOrder: [0, 1], cut: true, focus, locked, sideLabels: [L('青：左侧', 'teal: left'), L('蓝：右侧', 'blue: right')],
      tags: e.kind === 'trial-swap' ? Object.fromEntries(Object.entries(e.dValues).map(([n, d]) => [n, `D=${signed(d.D)}`])) : undefined,
      summary: L(`第 ${passNo} 轮：cut ${e.metrics.cut}`, `pass ${passNo}: cut ${e.metrics.cut}`) });
    const stepIdx = e.kind === 'trial-swap' ? pass.swaps.findIndex(s => `${s.a}↔${s.b}` === focus.join('↔')) + 1 : e.kind === 'best-prefix' ? pass.swaps.length : 0;
    chartBox.replaceChildren(prefixChart(pass.prefixGains, e.kind === 'best-prefix' ? pass.bestK : null, stepIdx));
    metrics(metricBox, [[L('第几轮', 'Pass'), passNo], [e.kind === 'best-prefix' ? L('接受的 cut', 'Accepted cut') : L('试探中的 cut', 'Trial cut'), e.metrics.cut], [L('本轮起点 cut', 'Cut at pass start'), pass.startCut]]);
    if (e.kind === 'pass-start') status(statusBox, '', L(`第 ${passNo} 轮开始：全部解锁，从 cut ${pass.startCut} 出发。`, `Pass ${passNo} starts: everything unlocked, from cut ${pass.startCut}.`));
    else if (e.kind === 'trial-swap') status(statusBox, e.trialGain < 0 ? 'limit' : '', L(`试探交换 ${focus.join('↔')}：收益 ${signed(e.trialGain)}，cut ${e.metrics.cutBefore} → ${e.metrics.cut}。${e.trialGain < 0 ? '收益为负也照走：这只是试探。' : ''}两点锁定。`,
      `Trial swap ${focus.join('↔')}: gain ${signed(e.trialGain)}, cut ${e.metrics.cutBefore} → ${e.metrics.cut}. ${e.trialGain < 0 ? 'A negative gain is taken anyway: this is only a trial. ' : ''}Both nodes lock.`));
    else status(statusBox, pass.bestK ? '' : 'blocked', L(`${eventText(e)}：从本轮起点回退，接受 cut ${e.metrics.cut}（试探结束时是 ${e.metrics.rollbackFromCut}）。${pass.bestK === 0 ? '空前缀胜出 → 停止。' : '进入下一轮。'}`,
      `${eventText(e)[0].toUpperCase() + eventText(e).slice(1)}: roll back to the pass start and accept cut ${e.metrics.cut} (the trials ended at ${e.metrics.rollbackFromCut}). ${pass.bestK === 0 ? 'The empty prefix wins → stop.' : 'On to the next pass.'}`));
    const c = e.candidates || [];
    candBox.replaceChildren(c.length ? h('table', {}, h('thead', {}, h('tr', {}, h('th', L('对', 'Pair')), h('th', 'D(a)+D(b)'), h('th', '−2w'), h('th', 'g'))),
      h('tbody', {}, c.map((x, k) => h('tr', { class: k === 0 ? 'chosen' : '' }, h('td', `${x.a}↔${x.b}`), h('td', String(x.Da + x.Db)), h('td', String(-2 * x.w)), h('td', signed(x.gain))))))
      : h('p.muted', e.kind === 'best-prefix' ? L('本轮试探结束。', 'The trials of this pass are over.') : L('本轮尚未开始交换。', 'No swap yet this pass.')));
    pseudo.kl?.show(e.kind === 'pass-start' ? [1, 2] : e.kind === 'trial-swap' ? [3, 4, 5, 6] : (pass.bestK ? [7, 8] : [7, 8, 9]), '');
  }
  buildToolbar(); recompute();
}

/** A new graph for the code lab: two four-node blocks, started from a mixed bisection. Its first trial swap loses 1, the second gains 7. */
const BRIDGE = {
  nodes: ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W'],
  edges: [['P', 'V', 4], ['P', 'W', 2], ['Q', 'S', 4], ['Q', 'T', 2], ['Q', 'U', 1], ['R', 'S', 3], ['R', 'T', 4], ['U', 'W', 2]],
  positions: { P: [80, 70], W: [230, 70], V: [80, 220], U: [230, 220], T: [400, 70], Q: [400, 220], R: [550, 70], S: [550, 220] }
};
const BRIDGE_SEED = { P: 0, Q: 1, R: 0, S: 1, T: 0, U: 1, V: 0, W: 1 };

/** Code lab: run the learner's kernighan_lin() (built on their best_swap() and best_prefix()) and compare every pass with the engine. */
function visualize(root, api) {
  const withAB1 = { nodes: G01.nodes, edges: G01.edges.map(e => ({ ...e, w: e.u === 'A' && e.v === 'B' ? 1 : e.w })), positions: G01.positions };
  const CASES = [
    { name: 'G01 · AE|BCD', graph: G01, seed: SEEDS['AE|BCD'] }, { name: 'G01 · AB|CDE', graph: G01, seed: SEEDS['AB|CDE'] },
    { name: 'G01 · BD|ACE', graph: G01, seed: SEEDS['BD|ACE'] }, { name: 'G01 · CE|ABD', graph: G01, seed: SEEDS['CE|ABD'] },
    { name: L('G01（A–B = 1）· AE|BCD', 'G01 (A–B = 1) · AE|BCD'), graph: withAB1, seed: SEEDS['AE|BCD'] },
    { name: L('两个四节点块（新图）', 'Two four-node blocks (new graph)'), graph: BRIDGE, seed: BRIDGE_SEED }
  ];
  const stage = h('div.lab-stage'), side = h('div.lab-side'), statusBox = h('div.status'), detail = h('div.decision'), tableBox = h('div'), match = h('p.match');
  const go = h('button.btn.primary', { type: 'button', onclick: runMine }, L('▶ 用我的代码运行', '▶ Run my code'));
  side.append(statusBox, detail);
  root.append(h('h3', L('用你的代码跑一遍', 'Watch your own code run')),
    h('p.muted', L('这里调用你写的 best_swap() 和 best_prefix()（经由已提供的 kl_pass() 和 kernighan_lin()），在 6 个情形上逐轮对照课程引擎：每一步交换哪一对、收益多少、保留几步、最终 cut。点表格的一行，左边画出你的结果。',
      'This calls the best_swap() and best_prefix() you wrote (through the provided kl_pass() and kernighan_lin()) and compares them pass by pass with the course engine on six cases: which pair each step swaps, its gain, how many steps are kept, and the final cut. Click a row to draw your result on the left.')),
    h('div.lab-toolbar', {}, go), tableBox, h('div.lab', {}, h('div', {}, stage), side), match);
  stage.append(h('p.muted', { style: 'padding:40px 10px;text-align:center' }, L('写好两个函数后，按“用我的代码运行”。', 'Once both functions are written, press “Run my code”.')));
  let rows = [];
  const passesText = ps => ps.map(p => `[${p.gains.map(signed).join(', ')}] → ${p.k}`).join('  ');

  async function runMine() {
    if (api.busy) return;
    const payload = CASES.map(c => { const g = requireGraph(c.graph); return { nodes: g.nodes.map(n => n.id), edges: g.edges.map(e => [e.u, e.v, e.w]), seed: c.seed }; });
    const code = `import json, importlib.util
spec = importlib.util.spec_from_file_location('impl_v', 'impl.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
out = []
for c in json.loads(${JSON.stringify(JSON.stringify(payload))}):
    try:
        r = m.kernighan_lin(c["nodes"], [tuple(e) for e in c["edges"]], c["seed"])
        out.append({"cut": r["cut"], "assignment": r["assignment"],
                    "passes": [{"pairs": [s["a"] + s["b"] for s in p["swaps"]], "gains": [s["gain"] for s in p["swaps"]], "k": p["best_k"]} for p in r["passes"]]})
    except Exception as e:
        out.append({"error": type(e).__name__ + ": " + str(e)})
json.dumps(out)`;
    api.setBusy(true); go.disabled = true; match.className = 'match'; match.textContent = L('运行中…', 'Running…');
    try {
      const mine = JSON.parse((await api.run(code)).value);
      rows = CASES.map((c, i) => {
        const g = requireGraph(c.graph), ref = KL.run(g, { initial: c.seed }).result, me = mine[i];
        const refPasses = ref.passes.map(p => ({ pairs: p.swaps.map(s => s.a + s.b), gains: p.swaps.map(s => s.gain), k: p.bestK }));
        const same = !me.error && me.cut === ref.cut && JSON.stringify(me.passes) === JSON.stringify(refPasses);
        return { c, g, ref, refPasses, me, ok: same };
      });
      const ok = rows.filter(r => r.ok).length;
      match.className = 'match ' + (ok === rows.length ? 'ok' : 'no');
      match.textContent = ok === rows.length
        ? L('✓ 6 个情形逐轮与课程引擎一致：同样的交换、同样的收益、同样的最佳前缀。', '✓ All six cases agree with the course engine pass by pass: the same swaps, the same gains, the same best prefixes.')
        : L(`× ${rows.length - ok} 个情形与引擎不同（红色）。点那一行看差在哪里。`, `× ${rows.length - ok} of the cases differ from the engine (in red). Click a row to see where.`);
      drawTable(); pick(rows.findIndex(r => !r.ok) >= 0 ? rows.findIndex(r => !r.ok) : 0);
    } catch (err) {
      match.className = 'match no';
      const msg = String(err.message || err).split('\n').filter(Boolean);
      match.textContent = err.reason ? L('已停止。', 'Stopped.') : L('你的代码运行出错：', 'Your code raised an error: ') + msg.slice(-1)[0];
    } finally { api.setBusy(false); go.disabled = false; }
  }
  function drawTable(sel = -1) {
    tableBox.replaceChildren(h('table.codelab-cases', {}, h('thead', {}, h('tr', {}, h('th', L('情形', 'Case')), h('th', L('你的各轮收益 → 保留步数', 'Your gains per pass → steps kept')), h('th', L('你的 cut', 'Your cut')), h('th', L('引擎', 'Engine')))),
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
    new GraphView(stage, { graph: r.g, positions: r.c.graph.positions, title: L('你的代码的结果', 'Your code’s result') })
      .render({ groups, groupOrder: [0, 1], cut: true, sideLabels: [L('青：左侧', 'teal: left'), L('蓝：右侧', 'blue: right')], summary: L(`你的结果：cut ${r.me.cut ?? '—'}`, `Your result: cut ${r.me.cut ?? '—'}`) });
    status(statusBox, r.ok ? '' : 'cycle', r.ok ? L('这个情形与引擎一致。', 'This case agrees with the engine.') : L('这个情形与引擎不同：对照右表，找第一处不同的交换或保留步数。', 'This case differs from the engine: compare with the right-hand column and find the first swap or kept count that differs.'));
    const p1 = r.refPasses[0];
    detail.replaceChildren(h('p', {}, L(`引擎第 1 轮：${p1.pairs.map((x, j) => `${x[0]}↔${x[1]} ${signed(p1.gains[j])}`).join('，')}；保留前 ${p1.k} 步。`, `Engine pass 1: ${p1.pairs.map((x, j) => `${x[0]}↔${x[1]} ${signed(p1.gains[j])}`).join(', ')}; keeps the first ${p1.k}.`)),
      r.c.graph === BRIDGE ? h('p.muted', L('第一步收益 −1：只接受正收益的贪心会在 cut 7 停下；KL 先试探，第二步 +7，保留前两步，cut 1。', 'The first step’s gain is −1: a greedy that only accepts positive gains would stop at cut 7; KL tries it anyway, the second step gains +7, and keeping the first two steps gives cut 1.')) : '');
  }
}

bootModule({ moduleId: 'm07-kernighan-lin', display: 'Module 07', challenges, lab, visualize });
