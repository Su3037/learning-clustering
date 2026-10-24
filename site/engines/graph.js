/**
 * Learning Clustering · shared undirected-graph utilities.
 * Original code for this course (MIT). Every engine in this folder runs unchanged
 * in the browser and in Node, so the page, the challenge checker, the film data
 * and the regression tests all read the same computation.
 */
import { L } from '../assets/i18n.js';
export const ENGINE_VERSION = '1.0.0';

const NAME = /^[A-Za-z][A-Za-z0-9_]{0,15}$/;

/** Compare two arrays field by field: numbers numerically, strings by code point.
 * This is the comparison the original M03 page needed: JavaScript's `a < b` on two
 * arrays converts both to strings, so [-5,'A'] < [-1,'A'] is false ("-5,A" > "-1,A"): the pair with
 * affinity 1 then beats the pair with affinity 5. */
export function compareKeys(a, b) {
  const n = Math.min(a.length, b.length);
  for (let i = 0; i < n; i++) {
    const x = a[i], y = b[i];
    if (Array.isArray(x) && Array.isArray(y)) { const c = compareKeys(x, y); if (c) return c; continue; }
    if (typeof x === 'number' && typeof y === 'number') { if (x !== y) return x < y ? -1 : 1; continue; }
    const sx = String(x), sy = String(y);
    if (sx !== sy) return sx < sy ? -1 : 1;
  }
  return a.length - b.length;
}

/** Accepts nodes as ids or {id,size}; edges as [u,v,w] or {u,v,w}. Returns {ok, errors, graph}. */
export function normalizeGraph(input, { maxNodes = 40, maxEdges = 400, allowZero = false } = {}) {
  const errors = [];
  if (!input || !Array.isArray(input.nodes) || !Array.isArray(input.edges)) {
    return { ok: false, errors: [L('需要 nodes 与 edges 两个数组', 'needs two arrays, nodes and edges')], graph: null };
  }
  const sizes = input.sizes || input.node_sizes || {};
  const nodes = input.nodes.map(n => typeof n === 'string' ? { id: n, size: sizes[n] ?? 1 } : { id: n.id, size: n.size ?? sizes[n.id] ?? 1 });
  if (nodes.length < 1 || nodes.length > maxNodes) errors.push(L(`节点数须在 1–${maxNodes} 之间`, `the number of nodes must be 1–${maxNodes}`));
  const ids = new Set();
  for (const n of nodes) {
    if (typeof n.id !== 'string' || !NAME.test(n.id)) errors.push(L(`节点名 “${n.id}” 须以字母开头、最多 16 个字母数字或下划线`, `node name “${n.id}” must start with a letter and have at most 16 letters, digits or underscores`));
    if (ids.has(n.id)) errors.push(L(`节点 ${n.id} 重复`, `node ${n.id} appears twice`));
    ids.add(n.id);
    if (!Number.isFinite(n.size) || n.size <= 0) errors.push(L(`节点 ${n.id} 的大小须为正数`, `the size of node ${n.id} must be positive`));
  }
  if (input.edges.length > maxEdges) errors.push(L(`边数不能超过 ${maxEdges}`, `at most ${maxEdges} edges`));
  const seen = new Set(), edges = [];
  for (const e of input.edges) {
    const [u, v, w] = Array.isArray(e) ? e : [e.u, e.v, e.w];
    if (!ids.has(u) || !ids.has(v)) { errors.push(L(`边 ${u}–${v} 引用了不存在的节点`, `edge ${u}–${v} refers to a missing node`)); continue; }
    if (u === v) { errors.push(L(`不支持自环 ${u}–${v}`, `self-loops are not supported: ${u}–${v}`)); continue; }
    if (!Number.isFinite(w) || w < 0 || (!allowZero && w === 0) || w > 1e6) { errors.push(L(`边 ${u}–${v} 的权重须为${allowZero ? '非负' : '正'}有限数`, `the weight of edge ${u}–${v} must be a finite ${allowZero ? 'non-negative' : 'positive'} number`)); continue; }
    const [a, b] = u < v ? [u, v] : [v, u], key = a + '\u0000' + b;
    if (seen.has(key)) { errors.push(L(`重复边 ${a}–${b}：请先合并为一条并相加权重`, `duplicate edge ${a}–${b}: merge them into one and add the weights`)); continue; }
    seen.add(key); edges.push({ u: a, v: b, w });
  }
  edges.sort((p, q) => compareKeys([p.u, p.v], [q.u, q.v]));
  return { ok: errors.length === 0, errors, graph: errors.length ? null : { nodes, edges } };
}

export function requireGraph(input, options) {
  const r = normalizeGraph(input, options);
  if (!r.ok) { const err = new Error(r.errors.join(L('；', '; '))); err.errors = r.errors; throw err; }
  return r.graph;
}

export const nodeIds = graph => graph.nodes.map(n => n.id);
export const totalWeight = graph => graph.edges.reduce((s, e) => s + e.w, 0);

export function weightMap(graph) {
  const m = new Map();
  for (const n of graph.nodes) m.set(n.id, new Map());
  for (const { u, v, w } of graph.edges) { m.get(u).set(v, w); m.get(v).set(u, w); }
  return m;
}

/** assignment: node -> group key (any comparable value). Each undirected edge counted once. */
export function cutEdges(graph, assignment) {
  return graph.edges.filter(e => assignment[e.u] !== assignment[e.v]);
}
export const cutsize = (graph, assignment) => cutEdges(graph, assignment).reduce((s, e) => s + e.w, 0);

/** Groups as sorted member lists, groups sorted: label names and left/right swaps do not matter. */
export function canonicalGroups(assignment) {
  const groups = new Map();
  for (const [node, g] of Object.entries(assignment)) {
    if (!groups.has(g)) groups.set(g, []);
    groups.get(g).push(node);
  }
  return [...groups.values()].map(m => m.sort()).sort(compareKeys);
}
export const groupsKey = assignment => canonicalGroups(assignment).map(g => g.join(',')).join(' | ');
export const sameGrouping = (a, b) => groupsKey(a) === groupsKey(b);

export function groupsToAssignment(groups) {
  const a = {};
  groups.forEach((g, i) => g.forEach(n => { a[n] = i; }));
  return a;
}

/** Number of connected components (isolated nodes count as components). */
export function components(graph) {
  const adj = weightMap(graph), seen = new Set(), comps = [];
  for (const { id } of graph.nodes) {
    if (seen.has(id)) continue;
    const stack = [id], comp = [];
    seen.add(id);
    while (stack.length) {
      const x = stack.pop(); comp.push(x);
      for (const y of adj.get(x).keys()) if (!seen.has(y)) { seen.add(y); stack.push(y); }
    }
    comps.push(comp.sort());
  }
  return comps;
}

/** Small deterministic PRNG for reproducible random graphs in tests and experiments. */
export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function randomGraph(seed, { n = 6, p = 0.45, maxW = 9, sizes = false } = {}) {
  const rnd = mulberry32(seed), nodes = [];
  for (let i = 0; i < n; i++) nodes.push({ id: String.fromCharCode(65 + i), size: sizes ? 1 + Math.floor(rnd() * 3) : 1 });
  const edges = [];
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (rnd() < p) edges.push({ u: nodes[i].id, v: nodes[j].id, w: 1 + Math.floor(rnd() * maxW) });
  return { nodes, edges };
}

/** The course's shared five-node graph G01. */
export const G01 = {
  id: 'G01',
  nodes: ['A', 'B', 'C', 'D', 'E'].map(id => ({ id, size: 1 })),
  edges: [
    { u: 'A', v: 'B', w: 5 }, { u: 'A', v: 'C', w: 1 }, { u: 'B', v: 'C', w: 4 },
    { u: 'C', v: 'D', w: 2 }, { u: 'C', v: 'E', w: 1 }, { u: 'D', v: 'E', w: 5 }
  ],
  positions: { A: [170, 100], B: [390, 85], C: [305, 270], D: [530, 375], E: [280, 440] }
};
