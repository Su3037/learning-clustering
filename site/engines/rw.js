/**
 * Module 09 · Rajaraman–Wong delay-oriented clustering (IEEE TCAD 1995; DAC 1993 version).
 * Model used here: combinational DAG, node delay δ(v) ≥ 0, node size s(v) > 0, cluster capacity M,
 * zero extra delay on a wire inside a cluster, fixed delay D on every wire between clusters, and
 * logical nodes MAY be replicated. Goal: minimise the maximum PI→PO path delay.
 * The paper's optimality statement holds only inside that model; nothing here proves it.
 *
 * Data model keeps logical nodes and physical instances apart:
 *   instances[{instanceId, logicalId, clusterId}], instanceEdges[{from, to, cost}]
 * A logical node may own several instances (replication); a node→cluster map cannot express that.
 *
 * Tie rule (assumption, recorded as candidate): equal l(x)+Δ(x,v) values are ordered by
 * descending topological index. It reproduces the student example's 8 clusters / 20 instances /
 * output delay 8 from the audit reconstruction; the author has not confirmed it.
 */
import { ENGINE_VERSION } from './graph.js';

const NAME = /^[A-Za-z][A-Za-z0-9_]{0,15}$/;

export function validateDAG(input) {
  const errors = [];
  const nodes = (input?.nodes || []).map(n => typeof n === 'string' ? { id: n } : n);
  const ids = nodes.map(n => n.id);
  if (!ids.length) errors.push('需要 nodes');
  if (new Set(ids).size !== ids.length) errors.push('节点名重复');
  ids.forEach(id => { if (!NAME.test(id)) errors.push(`节点名 ${id} 不合法`); });
  const delay = {}, size = {};
  for (const n of nodes) {
    delay[n.id] = n.delay ?? input.nodeDelay ?? 1;
    size[n.id] = n.size ?? input.nodeSize ?? 1;
    if (!(delay[n.id] >= 0)) errors.push(`节点 ${n.id} 延迟须非负`);
    if (!(size[n.id] > 0)) errors.push(`节点 ${n.id} 大小须为正`);
  }
  const edges = [];
  const seen = new Set();
  for (const e of input?.edges || []) {
    const [u, v] = Array.isArray(e) ? e : [e.from ?? e.u, e.to ?? e.v];
    if (!ids.includes(u) || !ids.includes(v)) { errors.push(`有向边 ${u}→${v} 引用了不存在的节点`); continue; }
    if (u === v) { errors.push(`自环 ${u}→${v}`); continue; }
    if (seen.has(u + '>' + v)) { errors.push(`重复有向边 ${u}→${v}`); continue; }
    seen.add(u + '>' + v); edges.push([u, v]);
  }
  const pred = Object.fromEntries(ids.map(i => [i, []])), succ = Object.fromEntries(ids.map(i => [i, []]));
  edges.forEach(([u, v]) => { pred[v].push(u); succ[u].push(v); });
  // Kahn's algorithm; ties by the given node order so the order is reproducible.
  const indeg = Object.fromEntries(ids.map(i => [i, pred[i].length])), topo = [], ready = ids.filter(i => indeg[i] === 0);
  while (ready.length) {
    const x = ready.shift(); topo.push(x);
    for (const y of succ[x]) if (--indeg[y] === 0) { ready.push(y); ready.sort((a, b) => ids.indexOf(a) - ids.indexOf(b)); }
  }
  let cycle = null;
  if (topo.length !== ids.length) {
    cycle = ids.filter(i => !topo.includes(i));
    errors.push(`输入含有环（涉及 ${cycle.join(', ')}）：RW 只处理组合电路 DAG`);
  }
  const PI = input?.PI || ids.filter(i => pred[i].length === 0);
  const PO = input?.PO || ids.filter(i => succ[i].length === 0);
  PI.forEach(p => { if (pred[p]?.length) errors.push(`PI ${p} 不应有输入边`); });
  const capacity = input?.capacity, D = input?.interClusterDelay ?? input?.D;
  if (!(capacity > 0)) errors.push('容量 capacity 须为正');
  if (!(D >= 0)) errors.push('跨簇延迟 D 须非负');
  if (capacity > 0) ids.forEach(i => { if (size[i] > capacity) errors.push(`节点 ${i} 大小超过容量`); });
  return { ok: errors.length === 0, errors, dag: { ids, edges, pred, succ, topo, PI, PO, delay, size, capacity, D }, cycle };
}

/** Δ(x,v): largest sum of node delays along a path x→v, counting v but not x; null if no path. */
export function longestDelays(dag) {
  const { ids, topo, pred, delay } = dag, delta = {};
  for (const x of ids) {
    const row = Object.fromEntries(ids.map(v => [v, null])); row[x] = 0;
    for (const v of topo) for (const u of pred[v]) if (row[u] !== null) row[v] = Math.max(row[v] ?? -Infinity, row[u] + delay[v]);
    delta[x] = row;
  }
  return delta;
}

/** Delay of every instance in an instance graph: δ(v) + max over incoming (arrival + cost). */
export function evaluateInstances(instances, instanceEdges, delay) {
  const byId = Object.fromEntries(instances.map(i => [i.instanceId, i])), inc = Object.fromEntries(instances.map(i => [i.instanceId, []]));
  instanceEdges.forEach(e => inc[e.to].push(e));
  const memo = {}, visiting = new Set();
  const arr = id => {
    if (id in memo) return memo[id];
    if (visiting.has(id)) throw new Error('实例图含环');
    visiting.add(id);
    const t = delay[byId[id].logicalId] + Math.max(0, ...inc[id].map(e => arr(e.from) + e.cost));
    visiting.delete(id);
    return (memo[id] = t);
  };
  instances.forEach(i => arr(i.instanceId));
  return memo;
}

/** Non-replicating clustering evaluation: clusters is a list of disjoint node lists covering the DAG. */
export function evaluatePartition(input, clusters) {
  const v = validateDAG(input);
  if (!v.ok) return { ok: false, errors: v.errors };
  const { dag } = v, where = {};
  const errors = [];
  clusters.forEach((c, ci) => c.forEach(n => { if (n in where) errors.push(`${n} 出现在多个簇（不复制模型）`); where[n] = ci; }));
  dag.ids.forEach(n => { if (!(n in where)) errors.push(`${n} 未分配`); });
  clusters.forEach((c, ci) => { const s = c.reduce((t, n) => t + dag.size[n], 0); if (s > dag.capacity) errors.push(`簇 ${ci + 1} 大小 ${s} 超过容量 ${dag.capacity}`); });
  if (errors.length) return { ok: false, errors };
  const instances = dag.ids.map(n => ({ instanceId: n, logicalId: n, clusterId: where[n] }));
  const instanceEdges = dag.edges.map(([a, b]) => ({ from: a, to: b, cost: where[a] === where[b] ? 0 : dag.D }));
  const t = evaluateInstances(instances, instanceEdges, dag.delay);
  const crossings = instanceEdges.filter(e => e.cost > 0).length;
  return { ok: true, arrival: t, maxDelay: Math.max(...dag.PO.map(p => t[p])), crossings, instances, instanceEdges };
}

export function validate(input) { const r = validateDAG(input); return { ok: r.ok, errors: r.errors }; }

export function run(input) {
  const v = validateDAG(input);
  if (!v.ok) return { events: [], result: null, status: 'invalid', metadata: { errors: v.errors, cycle: v.cycle } };
  const dag = v.dag, { ids, topo, PI, PO, delay, size, capacity, D, pred } = dag;
  const delta = longestDelays(dag), tIndex = Object.fromEntries(topo.map((x, i) => [x, i]));
  const label = {}, cluster = {}, events = [];
  let step = 0;
  for (const p of PI) { label[p] = delay[p]; cluster[p] = [p]; }
  events.push({ eventId: 'init', phase: 'init', step: step++, kind: 'pi-labels', before: null, after: { ...label }, decision: null, metrics: { delta }, sourceVersion: ENGINE_VERSION });
  for (const v0 of topo) {
    if (PI.includes(v0)) continue;
    const anc = topo.filter(x => x !== v0 && delta[x][v0] !== null);
    const score = Object.fromEntries(anc.map(x => [x, label[x] + delta[x][v0]]));
    const rank = [...anc].sort((a, b) => (score[b] - score[a]) || (tIndex[b] - tIndex[a]));
    const C = [v0];
    let used = size[v0], i = 0;
    for (; i < rank.length; i++) { if (used + size[rank[i]] > capacity) break; C.push(rank[i]); used += size[rank[i]]; }
    const outside = rank.slice(i);
    const piInside = C.filter(x => PI.includes(x));
    const l1 = Math.max(0, ...piInside.map(x => score[x]));
    const l2 = Math.max(0, ...outside.map(x => score[x] + D));
    label[v0] = Math.max(l1, l2); cluster[v0] = C;
    events.push({ eventId: `label-${v0}`, phase: 'label', step: step++, kind: 'label', before: null,
      after: { node: v0, label: label[v0], cluster: C }, decision: `l(${v0}) = max(l1=${l1}, l2=${l2}) = ${label[v0]}`,
      candidates: rank.map(x => ({ x, l: label[x], delta: delta[x][v0], score: score[x], inCluster: C.includes(x) })),
      metrics: { l1, l2, label: label[v0], clusterSize: used }, sourceVersion: ENGINE_VERSION });
  }
  // Recover clusters from the outputs backwards; every input of a chosen cluster roots its own cluster.
  const selected = [], queue = [...PO];
  while (queue.length) {
    const r = queue.shift();
    if (selected.includes(r)) continue;
    selected.push(r);
    const C = new Set(cluster[r]);
    const inputs = [...new Set(cluster[r].flatMap(m => pred[m].filter(u => !C.has(u))))].sort((a, b) => tIndex[a] - tIndex[b]);
    events.push({ eventId: `select-${r}`, phase: 'reconstruct', step: step++, kind: 'select-cluster', before: null,
      after: { root: r, members: cluster[r], inputs }, decision: `选中以 ${r} 为根的簇`, metrics: { selected: selected.length }, sourceVersion: ENGINE_VERSION });
    inputs.forEach(u => { if (!selected.includes(u) && !queue.includes(u)) queue.push(u); });
  }
  const instances = [], instanceEdges = [];
  for (const r of selected) for (const m of topo.filter(x => cluster[r].includes(x))) instances.push({ instanceId: `${m}@${r}`, logicalId: m, clusterId: r });
  for (const inst of instances) {
    const r = inst.clusterId, C = cluster[r];
    for (const u of pred[inst.logicalId]) {
      if (C.includes(u)) instanceEdges.push({ from: `${u}@${r}`, to: inst.instanceId, cost: 0 });
      else instanceEdges.push({ from: `${u}@${u}`, to: inst.instanceId, cost: D });
    }
  }
  const legality = checkInstanceGraph(dag, instances, instanceEdges, selected, cluster);
  const arrival = evaluateInstances(instances, instanceEdges, delay);
  const outputDelays = Object.fromEntries(PO.map(p => [p, arrival[`${p}@${p}`]]));
  const copies = {};
  instances.forEach(i => { copies[i.logicalId] = (copies[i.logicalId] || 0) + 1; });
  const result = {
    labels: label, clusters: Object.fromEntries(selected.map(r => [r, topo.filter(x => cluster[r].includes(x))])), selected,
    instances, instanceEdges, arrival, outputDelays, maxDelay: Math.max(...Object.values(outputDelays)),
    instanceCount: instances.length, logicalCount: ids.length, replicated: Object.entries(copies).filter(([, c]) => c > 1).map(([id, c]) => ({ id, copies: c })),
    totalSize: instances.reduce((s, i) => s + size[i.logicalId], 0), legality, delta, tieRule: 'score desc, then reverse topological index (candidate assumption)'
  };
  return { events, result, status: legality.ok ? 'completed' : 'invalid', metadata: { engine: 'rajaraman-wong', version: ENGINE_VERSION, model: 'DAG, δ(v), size, capacity M, intra 0, inter D, replication allowed' } };
}

/** Every instance's fan-in must be complete, every cross-cluster source must be a cluster root,
 * every PO must have a root instance, and every cluster must fit the capacity. */
export function checkInstanceGraph(dag, instances, instanceEdges, selected, cluster) {
  const errors = [], ids = new Set(instances.map(i => i.instanceId));
  for (const inst of instances) {
    const inc = instanceEdges.filter(e => e.to === inst.instanceId).map(e => instances.find(i => i.instanceId === e.from)?.logicalId).sort();
    const need = [...dag.pred[inst.logicalId]].sort();
    if (JSON.stringify(inc) !== JSON.stringify(need)) errors.push(`实例 ${inst.instanceId} 的输入不完整`);
  }
  instanceEdges.forEach(e => { if (!ids.has(e.from)) errors.push(`边来自不存在的实例 ${e.from}`); });
  dag.PO.forEach(p => { if (!ids.has(`${p}@${p}`)) errors.push(`PO ${p} 没有根实例`); });
  selected.forEach(r => { const s = cluster[r].reduce((t, m) => t + dag.size[m], 0); if (s > dag.capacity) errors.push(`簇 ${r} 超容量`); });
  return { ok: errors.length === 0, errors };
}

/** Teaching chain P→X→Y→O for hand evaluation (not an RW run). */
export const CHAIN = { nodes: ['P', 'X', 'Y', 'O'], edges: [['P', 'X'], ['X', 'Y'], ['Y', 'O']], nodeDelay: 1, capacity: 2, D: 3 };

/** Candidate reconstruction of the student's lecture example (audit, video 405 s and 438 s). */
export const CANDIDATE_DAG = {
  status: 'candidate — reconstructed from the student video; original edge list and tie rule unconfirmed',
  nodes: 'abcdefghijkl'.split(''),
  edges: [['a', 'd'], ['a', 'f'], ['b', 'd'], ['b', 'e'], ['c', 'e'], ['c', 'h'], ['d', 'i'], ['e', 'g'], ['f', 'i'], ['g', 'i'], ['g', 'j'], ['h', 'j'], ['i', 'k'], ['j', 'k'], ['j', 'l']],
  PI: ['a', 'b', 'c'], PO: ['k', 'l'], nodeDelay: 1, nodeSize: 1, capacity: 4, D: 3,
  positions: { a: [80, 90], b: [80, 250], c: [80, 410], d: [240, 140], e: [240, 300], f: [240, 30], h: [240, 450], g: [400, 300], i: [560, 150], j: [560, 370], k: [720, 220], l: [720, 420] }
};
