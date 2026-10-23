/**
 * Module 07 · Kernighan–Lin refinement of a two-way split with fixed side cardinalities.
 * One pass: repeatedly swap the unlocked cross pair with the largest gain
 *   g(a,b) = D(a) + D(b) − 2w(a,b),   D(v) = external(v) − internal(v),
 * even when that gain is ≤ 0 (a trial), lock both, update D. After the pass keep the prefix with
 * the largest positive cumulative gain — the empty prefix (0) is allowed — and apply it from the
 * pass start. Stop when the best prefix of a pass is empty. Node counts per side never change;
 * cell areas are not balanced by this rule.
 */
import { requireGraph, weightMap, cutsize, compareKeys, ENGINE_VERSION } from './graph.js';
import { L } from '../assets/i18n.js';

export function validate(input, { initial } = {}) {
  let g;
  try { g = requireGraph(input); } catch (e) { return { ok: false, errors: e.errors || [e.message] }; }
  const errors = [], ids = g.nodes.map(n => n.id);
  if (!initial) errors.push(L('需要初始二分 initial：{节点: 0 或 1}', 'An initial bisection is required: {node: 0 or 1}'));
  else {
    for (const id of ids) if (initial[id] !== 0 && initial[id] !== 1) errors.push(L(`节点 ${id} 的初始侧须为 0 或 1`, `Node ${id}'s initial side must be 0 or 1`));
    const c0 = ids.filter(id => initial[id] === 0).length;
    if (c0 === 0 || c0 === ids.length) errors.push(L('两侧都须非空', 'Both sides must be non-empty'));
  }
  return { ok: errors.length === 0, errors };
}

function dValues(adj, side, nodes) {
  const D = {};
  for (const v of nodes) {
    let ext = 0, int = 0;
    for (const [u, w] of adj.get(v)) (side[u] === side[v] ? (int += w) : (ext += w));
    D[v] = { ext, int, D: ext - int };
  }
  return D;
}

export function run(input, { initial, maxPasses = 10 } = {}) {
  const val = validate(input, { initial });
  if (!val.ok) return { events: [], result: null, status: 'invalid', metadata: { errors: val.errors } };
  const g = requireGraph(input), adj = weightMap(g), ids = g.nodes.map(n => n.id).sort();
  let side = { ...initial };
  const events = [], passes = [];
  let stopReason = 'limit', step = 0;
  for (let pass = 1; pass <= maxPasses; pass++) {
    const start = { ...side }, startCut = cutsize(g, start), trial = { ...side }, locked = new Set(), swaps = [];
    events.push({ eventId: `p${pass}-start`, phase: `pass-${pass}`, step: step++, kind: 'pass-start', before: null, after: { ...start }, decision: null, metrics: { cut: startCut }, sourceVersion: ENGINE_VERSION });
    while (true) {
      const free0 = ids.filter(v => trial[v] === 0 && !locked.has(v)), free1 = ids.filter(v => trial[v] === 1 && !locked.has(v));
      if (!free0.length || !free1.length) break;
      const D = dValues(adj, trial, ids);
      const cands = [];
      for (const a of free0) for (const b of free1) {
        const w = adj.get(a).get(b) || 0;
        cands.push({ a, b, Da: D[a].D, Db: D[b].D, w, gain: D[a].D + D[b].D - 2 * w });
      }
      cands.sort((p, q) => compareKeys([-p.gain, p.a, p.b], [-q.gain, q.a, q.b]));
      const best = cands[0], cutBefore = cutsize(g, trial);
      const before = { ...trial };
      trial[best.a] = 1; trial[best.b] = 0; locked.add(best.a); locked.add(best.b);
      const cutAfter = cutsize(g, trial);
      const cumulative = swaps.reduce((s, x) => s + x.gain, 0) + best.gain;
      const sw = { index: swaps.length + 1, ...best, cutBefore, cutAfter, cumulative };
      swaps.push(sw);
      events.push({ eventId: `p${pass}-t${sw.index}`, phase: `pass-${pass}`, step: step++, kind: 'trial-swap', before, after: { ...trial },
        decision: `试探交换 ${best.a}↔${best.b}`, candidates: cands, dValues: D, locks: [...locked].sort(), trialGain: best.gain,
        metrics: { cutBefore, cut: cutAfter, cumulative }, sourceVersion: ENGINE_VERSION });
    }
    const prefixGains = [0, ...swaps.map(s => s.cumulative)];
    let bestK = 0;
    prefixGains.forEach((gsum, k) => { if (gsum > prefixGains[bestK]) bestK = k; });
    const accepted = { ...start };
    for (const s of swaps.slice(0, bestK)) { accepted[s.a] = 1 - accepted[s.a]; accepted[s.b] = 1 - accepted[s.b]; }
    const acceptedCut = cutsize(g, accepted);
    passes.push({ pass, startCut, swaps, prefixGains, bestK, bestGain: prefixGains[bestK], acceptedCut, start, accepted: { ...accepted } });
    events.push({ eventId: `p${pass}-prefix`, phase: `pass-${pass}`, step: step++, kind: 'best-prefix', before: { ...trial }, after: { ...accepted },
      decision: bestK ? `保留前 ${bestK} 步` : '保留空前缀（不改变）', prefix: { gains: prefixGains, bestK }, locks: [],
      metrics: { cut: acceptedCut, rollbackFromCut: cutsize(g, trial), bestGain: prefixGains[bestK] }, sourceVersion: ENGINE_VERSION });
    side = accepted;
    if (bestK === 0) { stopReason = 'no-positive-prefix'; break; }
  }
  const result = { assignment: side, cut: cutsize(g, side), passes, stopReason,
    sideSizes: [ids.filter(v => side[v] === 0).length, ids.filter(v => side[v] === 1).length] };
  return { events, result, status: stopReason === 'limit' ? 'limit' : 'completed', metadata: { engine: 'kernighan-lin', version: ENGINE_VERSION, balance: 'node count per side fixed' } };
}

export const SEED = { A: 0, B: 1, C: 1, D: 1, E: 0 };
