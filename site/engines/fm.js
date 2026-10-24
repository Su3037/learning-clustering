/**
 * Module 08 · Fiduccia–Mattheyses refinement by single-node moves.
 * Internally every connection is a net (a pin list with a weight); an ordinary weighted edge is a
 * 2-pin net. Gain of moving v from side F to side T:
 *   + w(e) for every net e whose only F-side pin is v   (FS: the move removes e from the cut)
 *   − w(e) for every net e with no pin on T             (TE: the move puts e into the cut)
 * For 2-pin nets this is external − internal. After each move the pin counts are updated and only
 * the gains of nodes on affected nets are recomputed (the FM update rules).
 * Candidate selection scans the unlocked, balance-legal nodes of a gain-indexed Map. That is a
 * teaching implementation: it does NOT reach the O(pins) per pass bound of the 1982 bucket list.
 * Balance (base track): both sides nonempty and |n0 − n1| ≤ maxDiff, counting nodes, not area.
 */
import { compareKeys, ENGINE_VERSION } from './graph.js';
import { L } from '../assets/i18n.js';

const NAME = /^[A-Za-z][A-Za-z0-9_]{0,15}$/;

/** {nodes, edges?, nets?} → {ids, nets:[{id,pins,w}]}. */
export function toNets(input) {
  const errors = [];
  const ids = (input?.nodes || []).map(n => typeof n === 'string' ? n : n.id);
  if (!ids.length) errors.push(L('需要 nodes', 'nodes is required'));
  if (new Set(ids).size !== ids.length) errors.push(L('节点名重复', 'duplicate node names'));
  ids.forEach(id => { if (!NAME.test(id)) errors.push(L(`节点名 ${id} 不合法`, `node name ${id} is not valid`)); });
  const nets = [];
  for (const [i, e] of (input?.edges || []).entries()) {
    const [u, v, w] = Array.isArray(e) ? e : [e.u, e.v, e.w];
    if (!ids.includes(u) || !ids.includes(v) || u === v) { errors.push(L(`边 ${u}–${v} 不合法`, `edge ${u}–${v} is not valid`)); continue; }
    if (!(w > 0)) { errors.push(L(`边 ${u}–${v} 权重须为正`, `edge ${u}–${v} needs a positive weight`)); continue; }
    nets.push({ id: `${u < v ? u + v : v + u}`, pins: [u, v].sort(), w, kind: 'edge' });
  }
  for (const [i, n] of (input?.nets || []).entries()) {
    const pins = [...new Set(n.pins || [])].sort();
    if (pins.some(p => !ids.includes(p))) { errors.push(L(`net ${n.id ?? i} 引用了不存在的节点`, `net ${n.id ?? i} refers to a node that does not exist`)); continue; }
    if (pins.length < 2) continue;
    if (!((n.w ?? 1) > 0)) { errors.push(L(`net ${n.id ?? i} 权重须为正`, `net ${n.id ?? i} needs a positive weight`)); continue; }
    nets.push({ id: n.id ?? `n${i}`, pins, w: n.w ?? 1, kind: pins.length > 2 ? 'multi-pin' : 'edge' });
  }
  return { ok: errors.length === 0, errors, ids: [...ids].sort(), nets };
}

export function netCut(nets, side) {
  return nets.filter(n => new Set(n.pins.map(p => side[p])).size > 1).reduce((s, n) => s + n.w, 0);
}

export function balanceOk(side, ids, maxDiff) {
  const c0 = ids.filter(v => side[v] === 0).length, c1 = ids.length - c0;
  return c0 > 0 && c1 > 0 && Math.abs(c0 - c1) <= maxDiff;
}

/** Gain of every node with its FS/TE breakdown, from scratch (used for checks and the first step). */
export function gainsFromScratch(nets, side, ids) {
  const out = {};
  for (const v of ids) out[v] = { gain: 0, fs: [], te: [] };
  for (const n of nets) {
    const cnt = [0, 0]; n.pins.forEach(p => cnt[side[p]]++);
    for (const v of n.pins) {
      const F = side[v], T = 1 - F;
      if (cnt[F] === 1) { out[v].gain += n.w; out[v].fs.push({ net: n.id, w: n.w }); }
      if (cnt[T] === 0) { out[v].gain -= n.w; out[v].te.push({ net: n.id, w: n.w }); }
    }
  }
  return out;
}

export function validate(input, { initial, maxDiff = 1 } = {}) {
  const r = toNets(input), errors = [...r.errors];
  if (r.ok) {
    if (!initial) errors.push(L('需要初始二分 initial', 'an initial bisection is required'));
    else {
      for (const v of r.ids) if (initial[v] !== 0 && initial[v] !== 1) errors.push(L(`节点 ${v} 的初始侧须为 0 或 1`, `node ${v} must start on side 0 or 1`));
      if (!errors.length && !balanceOk(initial, r.ids, maxDiff)) errors.push(L(`初始二分不满足平衡：|n0−n1| ≤ ${maxDiff} 且两侧非空`, `the initial bisection is not balanced: |n0−n1| ≤ ${maxDiff} with both sides nonempty`));
    }
    if (!Number.isInteger(maxDiff) || maxDiff < 0) errors.push(L('maxDiff 须为非负整数', 'maxDiff must be a nonnegative integer'));
  }
  return { ok: errors.length === 0, errors };
}

export function run(input, { initial, maxDiff = 1, maxPasses = 10, firstPassOnly = false } = {}) {
  const val = validate(input, { initial, maxDiff });
  if (!val.ok) return { events: [], result: null, status: 'invalid', metadata: { errors: val.errors } };
  const { ids, nets } = toNets(input);
  const netsOf = Object.fromEntries(ids.map(v => [v, []]));
  nets.forEach((n, i) => n.pins.forEach(p => netsOf[p].push(i)));
  let side = { ...initial };
  const events = [], passes = [];
  let step = 0, stopReason = 'limit';
  for (let pass = 1; pass <= maxPasses; pass++) {
    const start = { ...side }, startCut = netCut(nets, start), trial = { ...side }, locked = new Set(), moves = [];
    const count = nets.map(n => { const c = [0, 0]; n.pins.forEach(p => c[trial[p]]++); return c; });
    let gains = gainsFromScratch(nets, trial, ids);
    const bucketsOf = () => { const b = new Map(); for (const v of ids) if (!locked.has(v)) { const gv = gains[v].gain; if (!b.has(gv)) b.set(gv, []); b.get(gv).push(v); } return [...b.entries()].sort((x, y) => y[0] - x[0]).map(([gain, nodes]) => ({ gain, nodes: nodes.sort() })); };
    events.push({ eventId: `p${pass}-start`, phase: `pass-${pass}`, step: step++, kind: 'pass-start', before: null, after: { ...start },
      decision: null, gains: snapshotGains(gains, trial, ids, maxDiff), buckets: bucketsOf(), metrics: { cut: startCut }, sourceVersion: ENGINE_VERSION });
    while (true) {
      const legal = ids.filter(v => !locked.has(v) && balanceOk({ ...trial, [v]: 1 - trial[v] }, ids, maxDiff));
      if (!legal.length) break;
      legal.sort((a, b) => compareKeys([-gains[a].gain, a], [-gains[b].gain, b]));
      const v = legal[0], blockedBetter = ids.filter(u => !locked.has(u) && !legal.includes(u) && gains[u].gain > gains[v].gain);
      const F = trial[v], T = 1 - F, cutBefore = netCut(nets, trial), detail = gains[v];
      const before = { ...trial };
      // FM update rules on the nets of v, before and after the move.
      const affected = new Set();
      for (const i of netsOf[v]) {
        const n = nets[i];
        n.pins.forEach(p => { if (p !== v && !locked.has(p)) affected.add(p); });
        count[i][F]--; count[i][T]++;
      }
      trial[v] = T; locked.add(v);
      for (const u of affected) gains[u] = nodeGain(u, nets, netsOf, count, trial);
      const cutAfter = netCut(nets, trial);
      const cumulative = moves.reduce((s, m) => s + m.gain, 0) + detail.gain;
      const mv = { index: moves.length + 1, node: v, from: F, to: T, gain: detail.gain, fs: detail.fs, te: detail.te, cutBefore, cutAfter, cumulative, blockedBetter };
      moves.push(mv);
      events.push({ eventId: `p${pass}-m${mv.index}`, phase: `pass-${pass}`, step: step++, kind: 'trial-move', before, after: { ...trial },
        decision: `试探移动 ${v}（${F}→${T}）`, gains: snapshotGains(gains, trial, ids, maxDiff, locked), buckets: bucketsOf(), locks: [...locked].sort(),
        trialGain: detail.gain, blocked: blockedBetter, metrics: { cutBefore, cut: cutAfter, cumulative }, sourceVersion: ENGINE_VERSION });
    }
    const prefixGains = [0, ...moves.map(m => m.cumulative)];
    let bestK = 0;
    prefixGains.forEach((x, k) => { if (x > prefixGains[bestK]) bestK = k; });
    const accepted = { ...start };
    moves.slice(0, bestK).forEach(m => { accepted[m.node] = m.to; });
    const acceptedCut = netCut(nets, accepted);
    passes.push({ pass, startCut, moves, prefixGains, bestK, bestGain: prefixGains[bestK], acceptedCut, start, accepted: { ...accepted } });
    events.push({ eventId: `p${pass}-prefix`, phase: `pass-${pass}`, step: step++, kind: 'best-prefix', before: { ...trial }, after: { ...accepted },
      decision: bestK ? `保留前 ${bestK} 步` : '保留空前缀', prefix: { gains: prefixGains, bestK }, locks: [],
      metrics: { cut: acceptedCut, rollbackFromCut: netCut(nets, trial) }, sourceVersion: ENGINE_VERSION });
    side = accepted;
    if (bestK === 0) { stopReason = 'no-positive-prefix'; break; }
    if (firstPassOnly) { stopReason = 'first-pass-only'; break; }
  }
  const result = { assignment: side, cut: netCut(nets, side), passes, stopReason, maxDiff,
    hasMultiPin: nets.some(n => n.pins.length > 2) };
  return { events, result, status: stopReason === 'limit' ? 'limit' : 'completed', metadata: { engine: 'fiduccia-mattheyses', version: ENGINE_VERSION, buckets: 'Map scan, not O(P)', balance: `|n0-n1|<=${maxDiff}` } };
}

function nodeGain(v, nets, netsOf, count, side) {
  const r = { gain: 0, fs: [], te: [] }, F = side[v], T = 1 - F;
  for (const i of netsOf[v]) {
    const n = nets[i];
    if (count[i][F] === 1) { r.gain += n.w; r.fs.push({ net: n.id, w: n.w }); }
    if (count[i][T] === 0) { r.gain -= n.w; r.te.push({ net: n.id, w: n.w }); }
  }
  return r;
}
function snapshotGains(gains, side, ids, maxDiff, locked = new Set()) {
  return ids.map(v => ({ node: v, side: side[v], gain: gains[v].gain, locked: locked.has(v),
    legal: !locked.has(v) && balanceOk({ ...side, [v]: 1 - side[v] }, ids, maxDiff) }));
}

/** Exhaustive minimum net cut among balance-legal two-way splits (unlabelled). */
export function exhaustive(input, maxDiff = 1) {
  const { ids, nets } = toNets(input), n = ids.length;
  let best = null;
  for (let mask = 0; mask < (1 << n); mask++) {
    if (mask & 1) continue;
    const s = Object.fromEntries(ids.map((v, i) => [v, (mask >> i) & 1]));
    if (!balanceOk(s, ids, maxDiff)) continue;
    const c = netCut(nets, s);
    if (!best || c < best.cut) best = { cut: c, side: s };
  }
  return best;
}

export const SEED = { A: 0, B: 1, C: 1, D: 1, E: 0 };

/** The attachment's "hillclimb" case, kept only as a disproved regression fixture. */
export const LEGACY_HILLCLIMB = {
  nodes: ['A', 'B', 'C', 'D', 'E', 'F'],
  edges: [['A', 'B', 6], ['A', 'C', 4], ['B', 'D', 4], ['C', 'D', 1], ['C', 'E', 4], ['D', 'F', 4], ['E', 'F', 6]],
  seed: { A: 0, B: 0, C: 1, D: 1, E: 0, F: 1 }, maxDiff: 2,
  claimed: { initialCut: 9, allLegalGainsNonPositive: true, finalCut: 4 }
};
/** The attachment's third example: ordinary 2-pin edges despite its "hypergraph" id. */
export const SEVEN_NODE = {
  nodes: ['A', 'B', 'C', 'D', 'E', 'F', 'G'],
  edges: [['A', 'B', 5], ['A', 'C', 4], ['B', 'C', 4], ['C', 'D', 1], ['D', 'E', 4], ['D', 'F', 4], ['E', 'F', 3], ['F', 'G', 5], ['D', 'G', 3]],
  seed: { A: 0, B: 1, C: 0, D: 0, E: 1, F: 1, G: 0 }, maxDiff: 1
};

/** Replacement negative-gain example (found by seeded search, checked exhaustively in tests):
 * at the start every legal move has gain ≤ 0, so plain hill climbing stops at cut 6;
 * FM moves A (−1) and B (−1), then E (+4), and keeps the 3-step prefix: cut 4 = balanced optimum. */
export const NEG_ESCAPE = {
  nodes: ['A', 'B', 'C', 'D', 'E', 'F'],
  edges: [['A', 'C', 4], ['A', 'E', 5], ['B', 'C', 2], ['B', 'E', 1], ['C', 'F', 3], ['D', 'E', 1], ['E', 'F', 1]],
  seed: { A: 0, D: 0, E: 0, B: 1, C: 1, F: 1 }, maxDiff: 2,
  positions: { A: [160, 120], E: [330, 250], D: [160, 380], C: [500, 120], B: [640, 250], F: [500, 380] },
  origin: 'randomGraph(4198, n=6, p=.5, maxW=6) in site/engines/graph.js'
};
