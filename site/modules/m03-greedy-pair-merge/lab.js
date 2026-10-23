// Module 03 lab: greedy pair merging on G01 (or edited weights). All states come from engines/merge.js.
import { h } from '../../assets/core.js';
import { GraphView, PALETTE } from '../../assets/graphview.js';
import { Player, TraceInspector, exportRun, metrics, status, select } from '../../assets/lab.js';
import { bootModule } from '../../assets/module-page.js';
import * as M from '../../engines/merge.js';
import { G01 } from '../../engines/graph.js';
import { challenges } from './challenges.js';


const STOP = { 'target-reached': '达到目标簇数 K', 'capacity-blocked': '还有正亲和度对，但全部超容量', 'no-positive-affinity': '剩下的簇之间没有边（亲和度为 0）' };

async function lab(root, { pseudo }) {
  let k = 2, capacity = null, weights = {}, run = null;
  const stage = h('div.lab-stage'), side = h('div.lab-side');
  const metricBox = h('div.metrics'), statusBox = h('div.status'), decision = h('div.decision'), playerBox = h('div');
  const legacyBox = h('div.lab-note'), traceBox = h('div'), err = h('p.lab-error'), toolbar = h('div.lab-toolbar');
  root.replaceChildren(toolbar, h('div.lab', {}, h('div', {}, stage, h('div.legend', {},
    h('span', {}, h('i', { style: 'border-color:#db7b72;border-top-style:dashed' }), '被切断的边'),
    h('span', {}, h('i', { style: 'border-color:#9fc9bf' }), '簇内部的边（不计入 cut）'),
    h('span', {}, h('b', { style: 'background:#d8bb78' }), '金圈：本步合并的两个簇'))), side), legacyBox, traceBox, err);
  side.append(metricBox, statusBox, h('h4', '本步的全部候选'), decision, playerBox);
  const gv = new GraphView(stage, { graph: G01, positions: G01.positions, title: '贪心合并实验图' });
  const player = new Player(playerBox, { onIndex: show, speed: 1500 });
  const trace = new TraceInspector(traceBox, { columns: [
    { label: '步', get: e => e.step }, { label: '动作', get: e => e.kind === 'merge' ? `合并 ${e.decision.a}+${e.decision.b}` : e.kind === 'stopped' ? '停止' : '单点簇' },
    { label: '亲和度', get: e => e.decision?.affinity ?? '' }, { label: 'cut', get: e => e.metrics.cut }, { label: '簇', get: e => e.after.map(c => c.label).join(' | ') }], onPick: i => player.go(i) });

  const graph = () => ({ nodes: G01.nodes, edges: G01.edges.map(e => ({ ...e, w: weights[`${e.u}|${e.v}`] ?? e.w })) });
  function buildToolbar() {
    const edgeSel = h('select', { 'aria-label': '选择要修改的边' }, G01.edges.map(e => h('option', { value: `${e.u}|${e.v}` }, `${e.u}–${e.v}`)));
    const wIn = h('input', { type: 'number', min: 1, max: 99, step: 0.5, 'aria-label': '新权重' });
    const sync = () => { const e = graph().edges.find(x => `${x.u}|${x.v}` === edgeSel.value); wIn.value = e.w; };
    edgeSel.addEventListener('change', sync); sync();
    wIn.addEventListener('change', () => { const w = Number(wIn.value); if (!(w > 0 && w <= 99)) { err.textContent = '权重须为 0–99 之间的正数。'; return; } err.textContent = ''; weights[edgeSel.value] = w; recompute(); });
    toolbar.replaceChildren(
      select('目标簇数 K', [1, 2, 3, 4].map(x => [String(x), String(x)]), String(k), v => { k = +v; recompute(); }),
      select('容量 C（节点大小均为 1）', [['', '不限'], ['2', '2'], ['3', '3'], ['4', '4']], capacity ? String(capacity) : '', v => { capacity = v ? +v : null; recompute(); }),
      h('label', {}, '改一条边', edgeSel), h('label', {}, '新权重', wIn),
      h('button.btn.small', { type: 'button', onclick: () => { weights = {}; buildToolbar(); recompute(); } }, '恢复原权重'),
      h('button.btn.small', { type: 'button', onclick: () => run && exportRun('m03-greedy-pair-merge', { options: { k, capacity }, input: graph(), engine: run.metadata, result: run.result, events: run.events }) }, '导出运行记录'));
  }
  function recompute() {
    run = M.run(graph(), { k, capacity });
    if (run.status === 'invalid') { err.textContent = run.metadata.errors.join('；'); return; }
    trace.load(run.events); player.load(run.events);
    const legacy = M.run(graph(), { k, capacity, legacyComparator: true });
    const same = legacy.result.cut === run.result.cut && legacy.result.labels.join() === run.result.labels.join();
    legacyBox.replaceChildren(h('strong', '对照：原网页的字符串比较（已修复的错误，仅用于说明）'), h('br'),
      `正确比较器：${run.result.labels.join(' | ')}，cut ${run.result.cut}。字符串比较：${legacy.result.labels.join(' | ')}，cut ${legacy.result.cut}`,
      same ? '——这组参数下两者碰巧相同。' : `——第一步被错误地选成 ${legacy.events[1]?.decision?.a ?? '?'}–${legacy.events[1]?.decision?.b ?? '?'}。`);
  }
  function show(i, e) {
    const after = e.after, order = run.events[0].after.map(c => c.label);
    const groups = {}, hulls = [];
    after.forEach((c, gi) => { c.members.forEach(m => { groups[m] = c.label; }); if (c.members.length > 1) hulls.push({ members: c.members, label: `${c.label} · 大小 ${c.size}`, color: PALETTE[gi % PALETTE.length] }); });
    const inside = graph().edges.filter(x => groups[x.u] === groups[x.v]).map(x => [x.u, x.v]);
    const focus = e.kind === 'merge' ? [...e.before.find(c => c.label === e.decision.a).members, ...e.before.find(c => c.label === e.decision.b).members] : [];
    const blocked = e.kind === 'stopped' ? [...new Set((e.candidates || []).flatMap(c => [...c.a, ...c.b]))] : [];
    gv.render({ groups, cut: true, inside, hulls, focus, blocked, groupOrder: after.map(c => c.label), summary: `第 ${e.step} 步：${after.map(c => c.label).join(' | ')}，cut ${e.metrics.cut}` });
    metrics(metricBox, [['簇数', after.length], ['cut', e.metrics.cut], ['目标 K', k]]);
    if (e.kind === 'singletons') status(statusBox, '', `开始：每个节点一个簇，cut = 全部边权 = ${e.metrics.cut}。`);
    else if (e.kind === 'merge') status(statusBox, '', `合并 ${e.decision.a} + ${e.decision.b}（亲和度 ${e.decision.affinity}）：cut ${e.metrics.cutBefore} → ${e.metrics.cut}，下降量 = 亲和度。`);
    else status(statusBox, 'blocked', `停止：${STOP[e.decision]}。${after.length > k ? `得到 ${after.length} 簇，未达到 K = ${k}；不强行合并。` : ''}`);
    if (i === run.events.length - 1 && run.result.targetReached) status(statusBox, '', `完成：${run.result.labels.join(' | ')}，cut ${run.result.cut}。停止原因：${STOP[run.result.stopReason]}。`);
    const cands = e.candidates || [];
    decision.replaceChildren(cands.length ? h('table', {}, h('thead', {}, h('tr', {}, h('th', '簇对'), h('th', '亲和度'), h('th', '合并后大小'), h('th', ''))),
      h('tbody', {}, cands.map(c => {
        const chosen = e.kind === 'merge' && c.a === e.decision.a && c.b === e.decision.b;
        return h('tr', { class: chosen ? 'chosen' : (!c.legal ? 'blocked' : '') }, h('td', `${c.a}–${c.b}`), h('td', `${c.affinity}${c.parts.length > 1 ? `（${c.parts.map(p => p.w).join('+')}）` : ''}`), h('td', String(c.size)), h('td', chosen ? '选中' : !c.legal ? '超容量' : ''));
      }))) : h('p.muted', '初始状态：还没有比较候选。'));
    const lines = e.kind === 'singletons' ? [1] : e.kind === 'stopped' ? [2, 3, 4, 5] : (i === run.events.length - 1 ? [6, 7, 2, 8] : [3, 4, 6, 7]);
    pseudo.merge?.show(lines, e.kind === 'merge' ? `本步：${e.decision.a} + ${e.decision.b}，亲和度 ${e.decision.affinity}` : '');
  }
  buildToolbar(); recompute();
}

bootModule({ moduleId: 'm03-greedy-pair-merge', display: 'Module 03', challenges, lab });
