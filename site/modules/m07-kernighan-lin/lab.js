// Module 07 lab: KL passes with trial swaps, locks, cumulative gains and best-prefix rollback (engines/kl.js).
import { h } from '../../assets/core.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as KL from '../../engines/kl.js';
import { G01 } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const SEEDS = { 'AE|BCD': KL.SEED, 'AB|CDE': { A: 0, B: 0, C: 1, D: 1, E: 1 }, 'BD|ACE': { A: 1, B: 0, C: 1, D: 0, E: 1 }, 'CE|ABD': { A: 1, B: 1, C: 0, D: 1, E: 0 } };

function prefixChart(gains, bestK, shown) {
  const W = 300, H = 140, base = 80, mx = Math.max(1, ...gains.map(Math.abs)), bw = Math.min(46, (W - 40) / gains.length - 8);
  const svg = h('svg', { viewBox: `0 0 ${W} ${H}`, class: 'gv', role: 'img', 'aria-label': `累计收益 ${gains.join('，')}，最佳前缀 k=${bestK}` },
    h('line', { x1: 20, y1: base, x2: W - 6, y2: base, stroke: '#5d7c80' }));
  gains.forEach((g, k) => {
    if (k > shown) return;
    const x = 26 + k * (bw + 10), hgt = 60 * Math.abs(g) / mx, best = bestK !== null && k === bestK;
    svg.append(h('rect', { x, y: g >= 0 ? base - hgt : base, width: bw, height: Math.max(2, hgt), rx: 3, fill: best ? '#d8bb78' : g > 0 ? '#77cdbb' : g < 0 ? '#db7b72' : '#bcd2d0' }),
      h('text', { x: x + bw / 2, y: g >= 0 ? base - hgt - 4 : base + hgt + 13, 'text-anchor': 'middle', class: 'w', style: 'font-size:12px' }, (g > 0 ? '+' : '') + g),
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
    h('span', {}, h('b', { style: 'background:#77cdbb' }), '左侧'), h('span', {}, h('b', { style: 'background:#8fb1e6' }), '右侧'),
    h('span', {}, '白色虚线圈：本轮已锁定'), h('span', {}, h('b', { style: 'background:#d8bb78' }), '金圈：本步交换的一对'))), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', '累计收益（前 k 步）'), chartBox, h('h4', '本步的候选（未锁定的跨侧对）'), candBox, playerBox);
  const gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: 'KL 实验图' });
  const player = new Player(playerBox, { onIndex: show, speed: 1600 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: '阶段', get: e => e.phase.replace('pass-', '第 ') + (e.phase.startsWith('pass') ? ' 轮' : '') },
    { label: '事件', get: e => e.kind === 'pass-start' ? '本轮开始' : e.kind === 'trial-swap' ? `试探 ${e.decision.replace('试探交换 ', '')}` : e.decision },
    { label: '收益', get: e => e.trialGain ?? '' }, { label: 'cut', get: e => e.metrics.cut }, { label: '累计', get: e => e.metrics.cumulative ?? '' }], onPick: i => player.go(i) });

  const graph = () => ({ nodes: G01.nodes, edges: G01.edges.map(e => ({ ...e, w: weights[`${e.u}|${e.v}`] ?? e.w })) });
  function buildToolbar() {
    const edgeSel = h('select', { 'aria-label': '选择要修改的边' }, G01.edges.map(e => h('option', { value: `${e.u}|${e.v}` }, `${e.u}–${e.v}`)));
    const wIn = h('input', { type: 'number', min: 1, max: 20, step: 1, 'aria-label': '新权重' });
    const sync = () => { wIn.value = graph().edges.find(x => `${x.u}|${x.v}` === edgeSel.value).w; };
    edgeSel.addEventListener('change', sync); sync();
    wIn.addEventListener('change', () => { const w = Number(wIn.value); if (!(w > 0 && w <= 20)) { err.textContent = '权重须为 1–20。'; return; } err.textContent = ''; weights[edgeSel.value] = w; recompute(); });
    toolbar.replaceChildren(
      select('初始二分（左 | 右）', Object.keys(SEEDS).map(k => [k, k]), seed, v => { seed = v; recompute(); }),
      h('label', {}, '改一条边', edgeSel), h('label', {}, '新权重', wIn),
      h('button.btn.small', { type: 'button', onclick: () => { weights = {}; buildToolbar(); recompute(); } }, '恢复原权重'),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m07-kernighan-lin', { options: { initial: SEEDS[seed] }, input: graph(), result: run.result, events: run.events }) }, '导出运行记录'));
  }
  function recompute() {
    run = KL.run(graph(), { initial: SEEDS[seed] });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join('；'); return; }
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const passNo = +e.phase.split('-')[1], pass = run.result.passes[passNo - 1];
    const side = e.after, locked = e.locks || [];
    const focus = e.kind === 'trial-swap' ? e.decision.replace('试探交换 ', '').split('↔') : [];
    gv.render({ groups: side, groupOrder: [0, 1], cut: true, focus, locked, sideLabels: ['青：左侧', '蓝：右侧'],
      tags: e.kind === 'trial-swap' ? Object.fromEntries(Object.entries(e.dValues).map(([n, d]) => [n, `D=${d.D > 0 ? '+' : ''}${d.D}`])) : undefined,
      summary: `${e.phase}：cut ${e.metrics.cut}` });
    const stepIdx = e.kind === 'trial-swap' ? pass.swaps.findIndex(s => `${s.a}↔${s.b}` === focus.join('↔')) + 1 : e.kind === 'best-prefix' ? pass.swaps.length : 0;
    chartBox.replaceChildren(prefixChart(pass.prefixGains, e.kind === 'best-prefix' ? pass.bestK : null, stepIdx));
    metrics(metricBox, [['第几轮', passNo], [e.kind === 'best-prefix' ? '接受的 cut' : '试探中的 cut', e.metrics.cut], ['本轮起点 cut', pass.startCut]]);
    if (e.kind === 'pass-start') status(statusBox, '', `第 ${passNo} 轮开始：全部解锁，从 cut ${pass.startCut} 出发。`);
    else if (e.kind === 'trial-swap') status(statusBox, e.trialGain < 0 ? 'limit' : '', `试探交换 ${focus.join('↔')}：收益 ${e.trialGain > 0 ? '+' : ''}${e.trialGain}，cut ${e.metrics.cutBefore} → ${e.metrics.cut}。${e.trialGain < 0 ? '收益为负也照走：这只是试探。' : ''}两点锁定。`);
    else status(statusBox, pass.bestK ? '' : 'blocked', `${e.decision}：从本轮起点回退，接受 cut ${e.metrics.cut}（试探结束时是 ${e.metrics.rollbackFromCut}）。${pass.bestK === 0 ? '空前缀胜出 → 停止。' : '进入下一轮。'}`);
    const c = e.candidates || [];
    candBox.replaceChildren(c.length ? h('table', {}, h('thead', {}, h('tr', {}, h('th', '对'), h('th', 'D(a)+D(b)'), h('th', '−2w'), h('th', 'g'))),
      h('tbody', {}, c.map((x, k) => h('tr', { class: k === 0 ? 'chosen' : '' }, h('td', `${x.a}↔${x.b}`), h('td', String(x.Da + x.Db)), h('td', String(-2 * x.w)), h('td', (x.gain > 0 ? '+' : '') + x.gain)))))
      : h('p.muted', e.kind === 'best-prefix' ? '本轮试探结束。' : '本轮尚未开始交换。'));
    pseudo.kl?.show(e.kind === 'pass-start' ? [1, 2] : e.kind === 'trial-swap' ? [3, 4, 5, 6] : (pass.bestK ? [7, 8] : [7, 8, 9]), '');
  }
  buildToolbar(); recompute();
}

bootModule({ moduleId: 'm07-kernighan-lin', display: 'Module 07', challenges, lab });
