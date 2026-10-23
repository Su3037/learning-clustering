/**
 * Module 06 · spectral bisection with the unnormalised Laplacian L = D − A.
 * The page solves the eigenproblem live (cyclic Jacobi rotations on a small symmetric matrix),
 * reports residuals and orthogonality, then sweeps the Fiedler ordering under an explicit
 * balance window. Nothing here is a physical spring simulation; the spring picture only
 * illustrates the quadratic form xᵀLx = Σ_edges w(u,v)(x_u − x_v)².
 */
import { requireGraph, cutsize, components, compareKeys, ENGINE_VERSION } from './graph.js';
import { L as tl } from '../assets/i18n.js';  // L is the Laplacian here

export function laplacian(input) {
  const g = requireGraph(input), ids = g.nodes.map(n => n.id), idx = Object.fromEntries(ids.map((id, i) => [id, i]));
  const n = ids.length, L = Array.from({ length: n }, () => new Array(n).fill(0));
  const contributions = [];
  for (const { u, v, w } of g.edges) {
    const i = idx[u], j = idx[v];
    L[i][i] += w; L[j][j] += w; L[i][j] -= w; L[j][i] -= w;
    contributions.push({ u, v, w, cells: [[i, i, +w], [j, j, +w], [i, j, -w], [j, i, -w]] });
  }
  return { ids, L, rowSums: L.map(r => r.reduce((s, x) => s + x, 0)), contributions };
}

/** Cyclic Jacobi eigen-decomposition of a real symmetric matrix. Returns ascending eigenpairs. */
export function jacobiEigen(M, { tol = 1e-13, maxSweeps = 100 } = {}) {
  const n = M.length, A = M.map(r => r.slice()), V = Array.from({ length: n }, (_, i) => Array.from({ length: n }, (_, j) => +(i === j)));
  let sweeps = 0;
  for (; sweeps < maxSweeps; sweeps++) {
    let off = 0;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) off += A[p][q] * A[p][q];
    if (Math.sqrt(off) < tol) break;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
      if (Math.abs(A[p][q]) < 1e-300) continue;
      const theta = (A[q][q] - A[p][p]) / (2 * A[p][q]);
      const t = Math.sign(theta || 1) / (Math.abs(theta) + Math.sqrt(theta * theta + 1));
      const c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for (let k = 0; k < n; k++) {
        const akp = A[k][p], akq = A[k][q];
        A[k][p] = c * akp - s * akq; A[k][q] = s * akp + c * akq;
      }
      for (let k = 0; k < n; k++) {
        const apk = A[p][k], aqk = A[q][k];
        A[p][k] = c * apk - s * aqk; A[q][k] = s * apk + c * aqk;
      }
      for (let k = 0; k < n; k++) {
        const vkp = V[k][p], vkq = V[k][q];
        V[k][p] = c * vkp - s * vkq; V[k][q] = s * vkp + c * vkq;
      }
    }
  }
  const pairs = Array.from({ length: n }, (_, i) => ({ value: A[i][i], vector: V.map(r => r[i]) }));
  pairs.sort((a, b) => a.value - b.value);
  return { values: pairs.map(p => p.value), vectors: pairs.map(p => p.vector), sweeps };
}

const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);
const norm = a => Math.sqrt(dot(a, a));
const matvec = (M, x) => M.map(r => dot(r, x));
export function residual(L, value, vector) {
  const Lx = matvec(L, vector), nv = norm(vector) || 1;
  return norm(Lx.map((y, i) => y - value * vector[i])) / nv;
}
export function quadraticForm(input, x) {
  const g = requireGraph(input), ids = g.nodes.map(n => n.id), idx = Object.fromEntries(ids.map((id, i) => [id, i]));
  const terms = g.edges.map(e => ({ u: e.u, v: e.v, w: e.w, term: e.w * (x[idx[e.u]] - x[idx[e.v]]) ** 2 }));
  return { total: terms.reduce((s, t) => s + t.term, 0), terms };
}

/** Number of nonempty, unlabelled two-way splits of n nodes: (2ⁿ − 2) / 2. */
export const unlabelledBipartitions = n => (2 ** n - 2) / 2;

/** Balance window as allowed sizes of the smaller-or-left side, both sides nonempty. */
export function balanceWindow(n, { minFraction = 0.4, maxFraction = 0.6 } = {}) {
  const lo = Math.max(1, Math.ceil(minFraction * n - 1e-9)), hi = Math.min(n - 1, Math.floor(maxFraction * n + 1e-9));
  return { lo, hi, minFraction, maxFraction };
}

export function validate(input, { balance = { minFraction: 0.4, maxFraction: 0.6 } } = {}) {
  try {
    const g = requireGraph(input, { maxNodes: 40 });
    const errors = [];
    if (g.nodes.length < 2) errors.push(tl('至少需要 2 个节点才能二分', 'Bisection needs at least 2 nodes'));
    const w = balanceWindow(g.nodes.length, balance);
    if (w.lo > w.hi) errors.push(tl(`平衡窗口 ${balance.minFraction}–${balance.maxFraction} 在 ${g.nodes.length} 个节点上没有合法大小`, `The balance window ${balance.minFraction}–${balance.maxFraction} allows no legal size on ${g.nodes.length} nodes`));
    return { ok: errors.length === 0, errors };
  } catch (e) { return { ok: false, errors: e.errors || [e.message] }; }
}

/** Fix the overall sign so the first node (by id) has a non-negative entry; report that a flip
 * changes nothing but the side names. */
function orient(ids, vec) {
  const order = ids.map((id, i) => [id, i]).sort((a, b) => compareKeys([a[0]], [b[0]]));
  for (const [, i] of order) if (Math.abs(vec[i]) > 1e-9) return vec[i] < 0 ? vec.map(x => -x) : vec.slice();
  return vec.slice();
}

export function run(input, { balance = { minFraction: 0.4, maxFraction: 0.6 }, vector = null, vectorSource = 'live' } = {}) {
  const v = validate(input, { balance });
  if (!v.ok) return { events: [], result: null, status: 'invalid', metadata: { errors: v.errors } };
  const g = requireGraph(input), { ids, L, rowSums, contributions } = laplacian(g), n = ids.length;
  const eig = jacobiEigen(L), comps = components(g);
  const lambda2 = eig.values[1], lambda3 = eig.values[2] ?? Infinity;
  const gap = lambda3 - lambda2;
  const live = orient(ids, eig.vectors[1]);
  const fiedler = vector ? vector.slice() : live;
  const res = residual(L, lambda2, fiedler);
  const ones = new Array(n).fill(1 / Math.sqrt(n));
  const diagnostics = {
    solver: vector ? tl(`${vectorSource}（外部给定向量）`, `${vectorSource} (a given vector)`) : tl('Jacobi（浏览器实时求解）', 'Jacobi (solved live in the browser)'),
    sweeps: eig.sweeps,
    rowSumMax: Math.max(...rowSums.map(Math.abs)),
    lambda1: eig.values[0], lambda2, lambda3, gap,
    connected: comps.length === 1, components: comps,
    degenerate: Math.abs(gap) < 1e-8,
    residual: res, liveResidual: residual(L, lambda2, live),
    orthogonalityToOnes: Math.abs(dot(fiedler, ones)) / (norm(fiedler) || 1),
    warnings: []
  };
  if (!diagnostics.connected) diagnostics.warnings.push(tl(`图有 ${comps.length} 个连通分量：λ2 = 0，特征向量方向不唯一，排序可能只反映分量而非连接强弱。`, `The graph has ${comps.length} connected components: λ2 = 0, the eigenvector direction is not unique, and the order may only reflect the components, not connection strength.`));
  if (diagnostics.degenerate) diagnostics.warnings.push(tl('λ2 与 λ3 相等（简并）：第二特征向量不唯一，任何该特征空间内的方向都同样合法。', 'λ2 equals λ3 (repeated): the second eigenvector is not unique, and any direction in that eigenspace is equally valid.'));
  // Stable order: ascending entry, ties by id.
  const order = ids.map((id, i) => ({ id, x: fiedler[i] })).sort((a, b) => (a.x - b.x) || compareKeys([a.id], [b.id]));
  const win = balanceWindow(n, balance);
  const events = [{ eventId: 'laplacian', phase: 'matrix', step: 0, kind: 'laplacian', before: null, after: { L, rowSums }, contributions, decision: null, metrics: {}, sourceVersion: ENGINE_VERSION },
    { eventId: 'eigen', phase: 'eigen', step: 1, kind: 'eigen', before: null, after: { values: eig.values, fiedler, order: order.map(o => o.id) }, decision: null, metrics: diagnostics, sourceVersion: ENGINE_VERSION }];
  const sweep = [];
  for (let k = 1; k < n; k++) {
    const left = order.slice(0, k).map(o => o.id), right = order.slice(k).map(o => o.id);
    const a = Object.fromEntries(ids.map(id => [id, left.includes(id) ? 'L' : 'R']));
    const cut = cutsize(g, a), legal = k >= win.lo && k <= win.hi && (n - k) >= win.lo && (n - k) <= win.hi;
    sweep.push({ k, left, right, cut, legal, threshold: (order[k - 1].x + order[k].x) / 2 });
    events.push({ eventId: `sweep-${k}`, phase: 'sweep', step: 1 + k, kind: 'sweep-cut', before: null, after: { left, right }, decision: legal ? 'legal' : 'outside-balance', metrics: { cut, k }, sourceVersion: ENGINE_VERSION });
  }
  const legal = sweep.filter(s => s.legal);
  const best = legal.reduce((b, s) => (!b || s.cut < b.cut) ? s : b, null);
  const signSplit = sweep.find(s => order[s.k - 1].x < 0 && order[s.k].x >= 0) || null;
  const result = {
    ids, L, eigenvalues: eig.values, fiedler, order: order.map(o => o.id), orderValues: order.map(o => o.x), sweep, window: win,
    partition: best ? [best.left, best.right] : null, cut: best ? best.cut : null, bestK: best ? best.k : null,
    signSplit: signSplit ? { k: signSplit.k, cut: signSplit.cut, legal: signSplit.legal } : null,
    diagnostics, bipartitions: unlabelledBipartitions(n)
  };
  events.push({ eventId: 'choose', phase: 'choose', step: n + 1, kind: 'choose', before: null, after: result.partition, decision: best ? `k=${best.k}` : 'no-legal-cut', metrics: { cut: result.cut }, sourceVersion: ENGINE_VERSION });
  return { events, result, status: best ? 'completed' : 'blocked', metadata: { engine: 'spectral', version: ENGINE_VERSION, Lvariant: 'unnormalized L=D-A', precomputed: !!vector } };
}

/** Exhaustive minimum cut among all nonempty unlabelled bipartitions within the window (small n). */
export function exhaustiveBisection(input, balance = { minFraction: 0.4, maxFraction: 0.6 }) {
  const g = requireGraph(input), ids = g.nodes.map(n => n.id), n = ids.length, win = balanceWindow(n, balance);
  let best = null, count = 0, unconstrained = null;
  for (let mask = 1; mask < (1 << n) - 1; mask++) {
    if (mask & 1) continue; // fix node 0 on the right: unlabelled
    count++;
    const a = Object.fromEntries(ids.map((id, i) => [id, (mask >> i) & 1]));
    const k = ids.filter((_, i) => (mask >> i) & 1).length, cut = cutsize(g, a);
    const left = ids.filter((_, i) => (mask >> i) & 1), right = ids.filter((_, i) => !((mask >> i) & 1));
    if (!unconstrained || cut < unconstrained.cut) unconstrained = { cut, left, right };
    if (k >= win.lo && k <= win.hi && n - k >= win.lo && n - k <= win.hi && (!best || cut < best.cut)) best = { cut, left, right };
  }
  return { count, best, unconstrained };
}

/** The student page stored these three-decimal values; kept to compare with the live solve. */
export const STORED_VECTOR = { A: 0.519, B: 0.418, C: 0.106, D: -0.489, E: -0.553 };
export const DISCONNECTED = {
  nodes: ['A', 'B', 'C', 'D', 'E', 'F'],
  edges: [['A', 'B', 3], ['B', 'C', 2], ['A', 'C', 1], ['D', 'E', 3], ['E', 'F', 2], ['D', 'F', 1]],
  positions: { A: [120, 140], B: [260, 90], C: [230, 260], D: [470, 140], E: [610, 90], F: [580, 260] }
};
export const DEGENERATE = { // a 4-cycle: λ2 = λ3 = 2
  nodes: ['A', 'B', 'C', 'D'], edges: [['A', 'B', 1], ['B', 'C', 1], ['C', 'D', 1], ['D', 'A', 1]],
  positions: { A: [180, 120], B: [480, 120], C: [480, 380], D: [180, 380] }
};
