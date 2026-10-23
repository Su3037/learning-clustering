/**
 * Modules 03 and 04 · greedy pair merging (agglomerative clustering) with an optional hard capacity.
 * Start from singletons; repeatedly merge the legal cluster pair with the largest positive
 * affinity (= total weight of edges between the two clusters). Never undo a merge, never
 * force an illegal or zero-affinity merge just to reach K.
 */
import { requireGraph, compareKeys, cutsize, ENGINE_VERSION } from './graph.js';
import { L } from '../assets/i18n.js';

/** A cluster's canonical label: its sorted member names. Labels are compared as arrays. */
const label = members => members.join('');

/** Selection key, compared field by field: larger affinity first, then member lists of a, then b. */
export const candidateKey = c => [-c.affinity, c.a, c.b];

/** The original M03 page compared these keys with `cand < best` on arrays (string conversion).
 * Kept only so the regression test can show the bug and its effect; never used by the course. */
export function legacyStringLess(a, b) { return String(a) < String(b); }

export function validate(input, { k = 2, capacity = null } = {}) {
  const errors = [];
  let g = null;
  try { g = requireGraph(input); } catch (e) { return { ok: false, errors: e.errors || [e.message] }; }
  if (!Number.isInteger(k) || k < 1) errors.push(L('目标簇数 K 须为正整数', 'the target K must be a positive integer'));
  if (capacity !== null && capacity !== undefined && !(Number.isFinite(capacity) && capacity > 0)) errors.push(L('容量须为正数或留空', 'the capacity must be a positive number or empty'));
  if (capacity) for (const n of g.nodes) if (n.size > capacity) errors.push(L(`节点 ${n.id} 大小 ${n.size} 已超过容量 ${capacity}：任何分组都不合法`, `node ${n.id} has size ${n.size}, above the capacity ${capacity}: no grouping is legal`));
  return { ok: errors.length === 0, errors };
}

function snapshot(clusters) { return clusters.map(c => ({ label: c.label, members: [...c.members], size: c.size })); }
function assignmentOf(clusters) { const a = {}; clusters.forEach(c => c.members.forEach(m => { a[m] = c.label; })); return a; }

/** All cluster pairs with positive affinity, sorted by selection key; illegal ones flagged. */
export function candidates(graph, clusters, capacity, { compare = compareKeys } = {}) {
  const where = {};
  clusters.forEach((c, i) => c.members.forEach(m => { where[m] = i; }));
  const acc = new Map();
  for (const e of graph.edges) {
    const i = where[e.u], j = where[e.v];
    if (i === j) continue;
    const [x, y] = compareKeys(clusters[i].members, clusters[j].members) < 0 ? [i, j] : [j, i];
    const key = x + ',' + y;
    if (!acc.has(key)) acc.set(key, { i: x, j: y, affinity: 0, edges: [] });
    const c = acc.get(key); c.affinity += e.w; c.edges.push(e);
  }
  const list = [...acc.values()].map(c => {
    const A = clusters[c.i], B = clusters[c.j], size = A.size + B.size;
    return {
      a: A.members, b: B.members, labelA: A.label, labelB: B.label, affinity: c.affinity,
      parts: c.edges.map(e => ({ u: e.u, v: e.v, w: e.w })), size,
      legal: capacity == null || size <= capacity,
      reason: capacity != null && size > capacity ? L(`合并后大小 ${size} > 容量 ${capacity}`, `merged size ${size} > capacity ${capacity}`) : null,
      i: c.i, j: c.j
    };
  });
  list.sort((p, q) => compare(candidateKey(p), candidateKey(q)));
  return list;
}

export function run(input, { k = 2, capacity = null, legacyComparator = false } = {}) {
  const v = validate(input, { k, capacity });
  if (!v.ok) return { events: [], result: null, status: 'invalid', metadata: { errors: v.errors } };
  const g = requireGraph(input);
  let clusters = g.nodes.map(n => ({ members: [n.id], label: n.id, size: n.size }))
    .sort((p, q) => compareKeys(p.members, q.members));
  const events = [];
  const cut0 = cutsize(g, assignmentOf(clusters));
  events.push({ eventId: 'init', phase: 'init', step: 0, kind: 'singletons', before: null, after: snapshot(clusters),
    decision: null, metrics: { cut: cut0, clusters: clusters.length }, sourceVersion: ENGINE_VERSION });
  let stopReason = null, step = 0;
  while (true) {
    if (clusters.length <= k) { stopReason = 'target-reached'; break; }
    const cands = candidates(g, clusters, capacity);
    const chosen = legacyComparator ? legacyPick(cands) : (cands.find(c => c.legal) || null);
    if (!chosen) {
      stopReason = cands.length ? 'capacity-blocked' : 'no-positive-affinity';
      events.push({ eventId: `stop-${step + 1}`, phase: 'stop', step: step + 1, kind: 'stopped', before: snapshot(clusters), after: snapshot(clusters),
        decision: stopReason, candidates: strip(cands), metrics: { cut: cutsize(g, assignmentOf(clusters)), clusters: clusters.length }, sourceVersion: ENGINE_VERSION });
      break;
    }
    step++;
    const before = snapshot(clusters), cutBefore = cutsize(g, assignmentOf(clusters));
    const A = clusters[chosen.i], B = clusters[chosen.j];
    const members = [...A.members, ...B.members].sort();
    const merged = { members, label: label(members), size: A.size + B.size };
    clusters = clusters.filter((_, idx) => idx !== chosen.i && idx !== chosen.j).concat([merged]).sort((p, q) => compareKeys(p.members, q.members));
    const cutAfter = cutsize(g, assignmentOf(clusters));
    events.push({
      eventId: `merge-${step}`, phase: 'merge', step, kind: 'merge', before, after: snapshot(clusters),
      decision: { a: chosen.labelA, b: chosen.labelB, affinity: chosen.affinity, size: chosen.size, merged: merged.label },
      candidates: strip(cands), blocked: strip(cands.filter(c => !c.legal && compareKeys(candidateKey(c), candidateKey(chosen)) < 0)),
      metrics: { cutBefore, cut: cutAfter, drop: cutBefore - cutAfter, clusters: clusters.length }, sourceVersion: ENGINE_VERSION
    });
  }
  const assignment = assignmentOf(clusters), cut = cutsize(g, assignment);
  const result = {
    clusters: clusters.map(c => c.members), labels: clusters.map(c => c.label), sizes: clusters.map(c => c.size),
    count: clusters.length, cut, k, capacity, assignment,
    targetReached: clusters.length <= k,
    capacityCompliant: capacity == null || clusters.every(c => c.size <= capacity),
    stopReason, cutTrajectory: [cut0, ...events.filter(e => e.kind === 'merge').map(e => e.metrics.cut)]
  };
  return { events, result, status: result.targetReached ? 'completed' : 'blocked', metadata: { engine: 'merge', version: ENGINE_VERSION, legacyComparator } };
}

function strip(cands) { return cands.map(({ i, j, ...c }) => ({ ...c, a: c.labelA, b: c.labelB })); }

/** Emulates the original loop: for every ordered cluster pair in array order, the candidate key
 * array is compared to the best with `<`, which JavaScript evaluates on the joined strings. */
function legacyPick(cands) {
  const ordered = [...cands].sort((p, q) => (p.i - q.i) || (p.j - q.j));
  let best = null;
  for (const c of ordered) {
    if (!c.legal) continue;
    const key = [-c.affinity, c.labelA, c.labelB, c.i, c.j];
    if (!best || legacyStringLess(key, best.key)) best = { key, c };
  }
  return best ? best.c : null;
}

/** Exhaustive oracle for small graphs (≤ 10 nodes): every set partition, checked for capacity. */
export function exhaustive(input, { k = 2, capacity = null } = {}) {
  const g = requireGraph(input), ids = g.nodes.map(n => n.id), size = Object.fromEntries(g.nodes.map(n => [n.id, n.size]));
  if (ids.length > 10) throw new Error(L('穷举只用于不超过 10 个节点的教学例子', 'exhaustive search is only for teaching examples of at most 10 nodes'));
  let minParts = Infinity, bestExactK = null, count = 0;
  const groups = [];
  const rec = i => {
    if (i === ids.length) {
      count++;
      if (capacity != null && groups.some(gr => gr.size > capacity)) return;
      minParts = Math.min(minParts, groups.length);
      if (groups.length === k) {
        const a = {}; groups.forEach((gr, gi) => gr.members.forEach(m => { a[m] = gi; }));
        const c = cutsize(g, a);
        if (!bestExactK || c < bestExactK.cut) bestExactK = { cut: c, clusters: groups.map(gr => [...gr.members].sort()) };
      }
      return;
    }
    const id = ids[i];
    for (const gr of groups) {
      if (capacity != null && gr.size + size[id] > capacity) continue;
      gr.members.push(id); gr.size += size[id]; rec(i + 1); gr.members.pop(); gr.size -= size[id];
    }
    groups.push({ members: [id], size: size[id] }); rec(i + 1); groups.pop();
  };
  rec(0);
  const total = g.nodes.reduce((s, n) => s + n.size, 0);
  return {
    legalPartitions: count,
    lowerBoundClusters: capacity ? Math.ceil(total / capacity) : 1,
    minFeasibleClusters: minParts === Infinity ? null : minParts,
    feasibleAtK: bestExactK !== null,
    bestCutAtK: bestExactK
  };
}

/** Module 04 diagnosis: why greedy ended where it did. */
export function diagnose(input, options = {}) {
  const r = run(input, options);
  if (r.status === 'invalid') return { kind: 'invalid-input', run: r };
  const ex = exhaustive(input, options), res = r.result;
  let kind;
  if (!res.targetReached) {
    if (ex.lowerBoundClusters > options.k) kind = 'infeasible-by-bound';
    else if (!ex.bestCutAtK) kind = 'infeasible-by-search';
    else kind = 'greedy-stuck';
  } else if (ex.bestCutAtK && ex.bestCutAtK.cut < res.cut) kind = 'feasible-suboptimal';
  else kind = 'reached-and-optimal-here';
  return { kind, run: r, oracle: ex };
}

export const M04_GRAPHS = {
  greedy_trap: {
    nodes: [{ id: 'A', size: 2 }, { id: 'B', size: 2 }, { id: 'C', size: 1 }, { id: 'D', size: 1 }],
    edges: [['C', 'D', 10], ['A', 'C', 4], ['B', 'D', 4]],
    positions: { A: [140, 160], C: [300, 260], D: [470, 260], B: [630, 160] }
  },
  suboptimal: {
    nodes: ['A', 'B', 'C', 'D'],
    edges: [['A', 'B', 10], ['A', 'C', 9], ['B', 'D', 9], ['C', 'D', 1]],
    positions: { A: [180, 120], B: [520, 120], C: [180, 380], D: [520, 380] }
  }
};
