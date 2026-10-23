/**
 * Module 02 · affinity metrics. A score for every unordered node pair under one stated model.
 * Scores are rankings, not clusters, distances or probabilities.
 */
import { requireGraph, weightMap, compareKeys, ENGINE_VERSION } from './graph.js';
import { L } from '../assets/i18n.js';

const pairKey = (u, v) => u < v ? [u, v] : [v, u];
/** Ranking order: score descending, then u, then v (u < v inside a pair). */
export const rankOrder = (a, b) => compareKeys([-a.score, a.u, a.v], [-b.score, b.u, b.v]);

/** edge(u,v) = w(u,v): only pairs that share a wire get a score. */
export function edgeWeight(input) {
  const g = requireGraph(input);
  return g.edges.map(e => ({ u: e.u, v: e.v, score: e.w, parts: { direct: e.w, via: [] } })).sort(rankOrder);
}

/** shared(u,v) = w(u,v) + Σ_x min(w(u,x), w(v,x)) over common neighbours x.
 * Every unordered pair is examined, including pairs without a direct wire.
 * Pairs whose score is 0 are not listed (stated policy, `includeZero` lists them). */
export function sharedNeighbors(input, { includeZero = false } = {}) {
  const g = requireGraph(input), adj = weightMap(g), ids = g.nodes.map(n => n.id).sort(), out = [];
  for (let i = 0; i < ids.length; i++) for (let j = i + 1; j < ids.length; j++) {
    const u = ids[i], v = ids[j], direct = adj.get(u).get(v) || 0, via = [];
    for (const [x, wu] of adj.get(u)) {
      if (x === v) continue;
      const wv = adj.get(v).get(x);
      if (wv !== undefined) via.push({ x, wu, wv, min: Math.min(wu, wv) });
    }
    via.sort((a, b) => compareKeys([a.x], [b.x]));
    const score = direct + via.reduce((s, c) => s + c.min, 0);
    if (score > 0 || includeZero) out.push({ u, v, score, parts: { direct, via } });
  }
  return out.sort(rankOrder);
}

/** Validates a netlist {nodes, nets|hyperedges:[{id,pins,w}]}. Duplicate pins inside one net
 * are counted once; nets with fewer than two distinct pins are ignored and reported. */
export function validateNetlist(input) {
  const errors = [], ignored = [];
  const nodes = (input?.nodes || []).map(n => typeof n === 'string' ? n : n.id);
  const ids = new Set(nodes);
  if (!nodes.length) errors.push(L('需要 nodes 数组', 'needs a nodes array'));
  const raw = input?.nets || input?.hyperedges;
  if (!Array.isArray(raw)) errors.push(L('需要 nets 数组', 'needs a nets array'));
  const nets = [];
  for (const [i, n] of (raw || []).entries()) {
    const id = n.id ?? `n${i}`, w = n.w ?? 1;
    if (!Array.isArray(n.pins)) { errors.push(L(`net ${id} 缺少 pins`, `net ${id} has no pins`)); continue; }
    if (!Number.isFinite(w) || w <= 0) { errors.push(L(`net ${id} 权重须为正数`, `the weight of net ${id} must be positive`)); continue; }
    const missing = n.pins.filter(p => !ids.has(p));
    if (missing.length) { errors.push(L(`net ${id} 引用了不存在的节点 ${missing.join(',')}`, `net ${id} refers to missing nodes ${missing.join(', ')}`)); continue; }
    const pins = [...new Set(n.pins)].sort();
    if (pins.length < 2) { ignored.push({ id, reason: L('少于两个不同引脚', 'fewer than two distinct pins') }); continue; }
    nets.push({ id, pins, w, duplicatePins: n.pins.length - pins.length });
  }
  return { ok: errors.length === 0, errors, ignored, netlist: { nodes, nets } };
}

/** pin-count (clique model): Σ_{nets e ∋ u,v} w(e)/(|e|−1). `raw` is the plain Σ w(e) for comparison. */
export function pinCount(input) {
  const r = validateNetlist(input);
  if (!r.ok) { const e = new Error(r.errors.join(L('；', '; '))); e.errors = r.errors; throw e; }
  const acc = new Map();
  for (const net of r.netlist.nets) {
    const share = net.w / (net.pins.length - 1);
    for (let i = 0; i < net.pins.length; i++) for (let j = i + 1; j < net.pins.length; j++) {
      const [u, v] = pairKey(net.pins[i], net.pins[j]), k = u + '\u0000' + v;
      if (!acc.has(k)) acc.set(k, { u, v, score: 0, raw: 0, parts: { nets: [] } });
      const p = acc.get(k);
      p.score += share; p.raw += net.w;
      p.parts.nets.push({ id: net.id, size: net.pins.length, w: net.w, share });
    }
  }
  const scores = [...acc.values()].map(p => ({ ...p, score: round(p.score) })).sort(rankOrder);
  const raw = [...acc.values()].map(p => ({ u: p.u, v: p.v, score: p.raw })).sort(rankOrder);
  return { scores, raw, ignored: r.ignored };
}
const round = x => Math.round(x * 1e9) / 1e9;

export function validate(input, { metric = 'shared' } = {}) {
  try { metric === 'pin' ? pinCount(input) : requireGraph(input); return { ok: true, errors: [] }; }
  catch (e) { return { ok: false, errors: e.errors || [e.message] }; }
}

/** One event per scored pair, in ranking order, so a player can reveal the ranking step by step. */
export function run(input, { metric = 'shared' } = {}) {
  const v = validate(input, { metric });
  if (!v.ok) return { events: [], result: null, status: 'invalid', metadata: { errors: v.errors } };
  const list = metric === 'edge' ? edgeWeight(input) : metric === 'pin' ? pinCount(input).scores : sharedNeighbors(input);
  const events = list.map((p, i) => ({
    eventId: `${metric}-${i}`, phase: 'score', step: i, kind: 'pair-scored', before: null,
    after: { u: p.u, v: p.v, score: p.score }, decision: i === 0 ? 'top-pair' : 'ranked',
    metrics: { rank: i + 1 }, parts: p.parts, sourceVersion: ENGINE_VERSION
  }));
  return { events, result: { metric, ranking: list, top: list[0] || null }, status: 'completed', metadata: { engine: 'affinity', version: ENGINE_VERSION } };
}

export const PRIORITY_GRAPH = {
  nodes: ['P', 'Q', 'R', 'X', 'Y'],
  edges: [['P', 'Q', 4], ['P', 'R', 4], ['Q', 'R', 4], ['X', 'Y', 5]],
  positions: { P: [150, 330], Q: [330, 330], R: [240, 160], X: [470, 170], Y: [590, 330] }
};
export const TINY_NETLIST = {
  nodes: ['A', 'B', 'C', 'D', 'E', 'F'],
  nets: [
    { id: 'en', pins: ['A', 'B', 'C', 'D', 'E'], w: 1 },
    { id: 'rst', pins: ['A', 'B', 'C', 'D', 'E'], w: 1 },
    { id: 'n1', pins: ['E', 'F'], w: 1 }
  ]
};
