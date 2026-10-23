// Module 08 lab: white-box FM — legal candidates, FS/TE, gain buckets, cumulative gains (engines/fm.js).
import { h } from '../../assets/core.js';
import { GraphView } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as FM from '../../engines/fm.js';
import { G01 } from '../../engines/graph.js';
import { challenges } from './challenges.js';

const MULTI = { nodes: ['A', 'B', 'C', 'D', 'E', 'F'], nets: [{ id: 'bus', pins: ['A', 'B', 'C', 'D'], w: 2 }], edges: [['A', 'E', 3], ['C', 'F', 2], ['E', 'F', 1], ['B', 'D', 1]],
  seed: { A: 0, B: 0, E: 0, C: 1, D: 1, F: 1 }, maxDiff: 2, positions: { A: [150, 120], B: [150, 300], E: [300, 420], C: [520, 120], D: [520, 300], F: [620, 420] } };
const PRESETS = {
  seed: { name: '课程种子 AE | BCD（maxDiff 1）', graph: G01, positions: G01.positions, seed: FM.SEED, maxDiff: 1 },
  escape: { name: '替换反例：先负后正（maxDiff 2）', graph: FM.NEG_ESCAPE, positions: FM.NEG_ESCAPE.positions, seed: FM.NEG_ESCAPE.seed, maxDiff: 2 },
  seven: { name: '原附件第三例：7 节点普通图', graph: FM.SEVEN_NODE, positions: null, seed: FM.SEVEN_NODE.seed, maxDiff: 1 },
  legacy: { name: '原附件 hillclimb（说明已证伪，仅供审查）', graph: FM.LEGACY_HILLCLIMB, positions: { A: [180, 95], B: [180, 285], C: [380, 95], D: [380, 285], E: [580, 95], F: [580, 285] }, seed: FM.LEGACY_HILLCLIMB.seed, maxDiff: 2 },
  multi: { name: '拓展：含 4 引脚 net', graph: MULTI, positions: MULTI.positions, seed: MULTI.seed, maxDiff: 2 }
};

function cumChart(gains, bestK, shown) {
  const W = 300, H = 140, base = 78, mx = Math.max(1, ...gains.map(Math.abs)), bw = Math.min(36, (W - 30) / gains.length - 6);
  const svg = h('svg', { viewBox: `0 0 ${W} ${H}`, class: 'gv', role: 'img', 'aria-label': `累计收益 ${gains.join('，')}` }, h('line', { x1: 14, y1: base, x2: W - 4, y2: base, stroke: '#5d7c80' }));
  gains.forEach((g, k) => {
    if (k > shown) return;
    const x = 18 + k * (bw + 6), hg = 56 * Math.abs(g) / mx, best = bestK !== null && k === bestK;
    svg.append(h('rect', { x, y: g >= 0 ? base - hg : base, width: bw, height: Math.max(2, hg), rx: 3, fill: best ? '#d8bb78' : g > 0 ? '#77cdbb' : g < 0 ? '#db7b72' : '#bcd2d0' }),
      h('text', { x: x + bw / 2, y: g >= 0 ? base - hg - 4 : base + hg + 12, 'text-anchor': 'middle', class: 'w', style: 'font-size:11px' }, (g > 0 ? '+' : '') + g),
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
    h('span', {}, h('b', { style: 'background:#77cdbb' }), '0 侧'), h('span', {}, h('b', { style: 'background:#8fb1e6' }), '1 侧'),
    h('span', {}, '白色虚线圈：已锁定'), h('span', {}, h('b', { style: 'background:#db7b72' }), '红圈：收益更大但不合法'), h('span', {}, h('b', { style: 'background:#d8bb78' }), '金圈：本步移动'))), side), traceBox, err);
  side.append(metricBox, statusBox, h('h4', '累计收益'), chartBox, h('h4', '所有节点的收益（移动前）'), gainBox, bucketBox, playerBox);
  let gv;
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [{ label: '轮', get: e => e.phase.split('-')[1] }, { label: '事件', get: e => e.kind === 'pass-start' ? '本轮开始' : e.decision },
    { label: '收益', get: e => e.trialGain ?? '' }, { label: 'cut', get: e => e.metrics.cut }, { label: '被挡住的更大收益', get: e => (e.blocked || []).join(' ') }], onPick: i => player.go(i) });

  function buildToolbar() {
    toolbar.replaceChildren(
      select('例子', Object.entries(PRESETS).map(([k, p]) => [k, p.name]), presetId, v => { presetId = v; maxDiff = PRESETS[v].maxDiff; buildToolbar(); recompute(true); }),
      select('平衡 maxDiff', [0, 1, 2, 3].map(x => [String(x), `|n₀ − n₁| ≤ ${x}`]), String(maxDiff), v => { maxDiff = +v; recompute(); }),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m08-fiduccia-mattheyses', { preset: presetId, options: { maxDiff, initial: PRESETS[presetId].seed }, input: PRESETS[presetId].graph, result: run.result, events: run.events }) }, '导出运行记录'));
    note.textContent = presetId === 'legacy' ? '注意：原附件对这个案例的文字说明（初始 cut 9、所有合法收益 ≤ 0、降到 4）与数据不符。这里按数据真实运行，供你自己核验。' : presetId === 'multi' ? '拓展：bus 是一个 4 引脚 net（图上画成虚线示意）。收益按两侧引脚计数，不是把 net 拆成边。' : '';
  }
  function recompute(newGraph = false) {
    const p = PRESETS[presetId];
    run = FM.run(p.graph, { initial: p.seed, maxDiff });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join('；') + '（试试更大的 maxDiff）'; trace.load([]); return; }
    err.textContent = '';
    const display = { nodes: p.graph.nodes, edges: [...(p.graph.edges || []), ...(p.graph.nets || []).flatMap(n => n.pins.slice(1).map(q => [n.pins[0], q, `${n.id}`]))] };
    if (newGraph || !gv) gv = new GraphView(stage, { graph: display, positions: p.positions, title: 'FM 实验图' });
    trace.load(run.events); player.load(run.events);
  }
  function show(i, e) {
    const p = PRESETS[presetId], passNo = +e.phase.split('-')[1], pass = run.result.passes[passNo - 1];
    const moved = e.kind === 'trial-move' ? e.decision.match(/移动 (\S+)（/)[1] : null;
    const before = e.kind === 'trial-move' ? run.events[i - 1] : e;
    const blocked = e.kind === 'trial-move' ? e.blocked : [];
    const dash = Object.fromEntries((p.graph.nets || []).flatMap(n => n.pins.slice(1).map(q => [[n.pins[0], q].sort().join('|'), 'stroke-dasharray:3 5;stroke:#c2a6e6'])));
    gv.render({ groups: e.after, groupOrder: [0, 1], cut: true, locked: e.locks || [], focus: moved ? [moved] : [], blocked, edgeStyle: dash, summary: `${e.phase}：cut ${e.metrics.cut}` });
    const stepIdx = e.kind === 'trial-move' ? pass.moves.findIndex(m => m.node === moved) + 1 : e.kind === 'best-prefix' ? pass.moves.length : 0;
    chartBox.replaceChildren(cumChart(pass.prefixGains, e.kind === 'best-prefix' ? pass.bestK : null, stepIdx));
    const n0 = Object.values(e.after).filter(s => s === 0).length, n1 = Object.values(e.after).length - n0;
    metrics(metricBox, [['轮', passNo], ['cut', e.metrics.cut], ['两侧人数', `${n0} : ${n1}`]]);
    if (e.kind === 'pass-start') status(statusBox, '', `第 ${passNo} 轮开始：全部解锁，cut ${pass.startCut}。`);
    else if (e.kind === 'trial-move') {
      const m = pass.moves[stepIdx - 1];
      status(statusBox, m.gain < 0 ? 'limit' : '', `试探移动 ${moved}：收益 ${m.gain > 0 ? '+' : ''}${m.gain}（FS ${m.fs.map(x => `${x.net}:${x.w}`).join('+') || '0'}，TE ${m.te.map(x => `${x.net}:${x.w}`).join('+') || '0'}），cut ${m.cutBefore} → ${m.cutAfter}。${blocked.length ? `${blocked.join('、')} 收益更大但不合法。` : ''}`);
    } else status(statusBox, pass.bestK ? '' : 'blocked', `${e.decision}：接受 cut ${e.metrics.cut}（试探终点 ${e.metrics.rollbackFromCut}）。${pass.bestK ? '进入下一轮。' : '空前缀 → 停止。'}`);
    const gains = (before.gains || []);
    gainBox.replaceChildren(gains.length ? h('table', {}, h('thead', {}, h('tr', {}, h('th', '节点'), h('th', '侧'), h('th', '收益'), h('th', '状态'))),
      h('tbody', {}, gains.map(g => h('tr', { class: g.node === moved ? 'chosen' : (!g.locked && !g.legal ? 'blocked' : '') }, h('td', g.node), h('td', String(g.side)), h('td', (g.gain > 0 ? '+' : '') + g.gain),
        h('td', g.locked ? '已锁定' : g.legal ? (g.node === moved ? '选中' : '合法') : '不合法'))))) : h('p.muted', '本轮结束。'));
    const buckets = before.buckets || [];
    bucketBox.textContent = buckets.length ? '按收益分组的“桶”（每步扫描生成，不是 O(P) 结构）：' + buckets.map(b => `[${b.gain > 0 ? '+' : ''}${b.gain}] ${b.nodes.join(' ')}`).join('　') : '';
    pseudo.fm?.show(e.kind === 'pass-start' ? [1, 2] : e.kind === 'trial-move' ? [3, 4, 5, 6] : (pass.bestK ? [7, 8] : [7, 8, 9]), '');
  }
  buildToolbar(); recompute(true);
}

bootModule({ moduleId: 'm08-fiduccia-mattheyses', display: 'Module 08', challenges, lab });
