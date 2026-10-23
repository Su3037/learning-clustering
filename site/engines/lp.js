/**
 * Module 05 · label propagation. Adapted from the author's own Lab05 engine
 * (Su3037/clustering-lab5-label-propagation, site/algorithm.js @ 7b4eca7, MIT).
 * Changes here: shared graph format, common event fields, and the course run()/validate() contract.
 * Node names never change; labels do. Async writes immediately; sync reads the round's snapshot
 * and commits at the end. A round with zero changes is `stable`; a repeated labelling is `cycle`;
 * hitting the round limit is `limit`. None of these three is called "converged" unless stable.
 */
import { normalizeGraph, cutsize, groupsKey, ENGINE_VERSION } from './graph.js';
import { L } from '../assets/i18n.js';

export function votesFor(adj, labels, node) {
  const votes = {}, neighbors = [];
  for (const [n, w] of adj.get(node)) {
    const l = labels[n];
    votes[l] = (Object.hasOwn(votes, l) ? votes[l] : 0) + w;
    neighbors.push({ node: n, label: l, weight: w });
  }
  return { votes, neighbors };
}

export function chooseLabel(votes, current, tie = 'min') {
  const entries = Object.entries(votes);
  if (!entries.length) return { label: current, tied: [] };
  const max = Math.max(...entries.map(x => x[1]));
  const tied = entries.filter(x => Math.abs(x[1] - max) < 1e-12).map(x => x[0]).sort();
  if (tie === 'keep' && tied.includes(current)) return { label: current, tied };
  return { label: tie === 'max' ? tied.at(-1) : tied[0], tied };
}

export function validate(input, { mode = 'async', tie = 'min', order = null, maxRounds = 50, maxSize = null } = {}) {
  const r = normalizeGraph(input, { maxNodes: 40, maxEdges: 400 });
  const errors = [...r.errors];
  if (!['async', 'sync'].includes(mode)) errors.push(L('更新方式须为 async 或 sync', 'the update mode must be async or sync'));
  if (!['min', 'max', 'keep'].includes(tie)) errors.push(L('平票规则须为 min、max 或 keep', 'the tie rule must be min, max or keep'));
  if (maxSize != null && (!Number.isInteger(maxSize) || maxSize < 1)) errors.push(L('组大小上限须为正整数', 'the group size limit must be a positive integer'));
  if (maxSize != null && mode !== 'async') errors.push(L('组大小上限只用于异步更新', 'the group size limit applies to asynchronous updates only'));
  if (!Number.isInteger(maxRounds) || maxRounds < 1 || maxRounds > 200) errors.push(L('最大轮数为 1–200', 'the maximum number of rounds is 1–200'));
  if (r.ok && order) {
    const ids = r.graph.nodes.map(n => n.id);
    if (order.length !== ids.length || new Set(order).size !== ids.length || order.some(n => !ids.includes(n))) errors.push(L('访问顺序须恰好包含每个节点一次', 'the visiting order must contain every node exactly once'));
  }
  return { ok: errors.length === 0, errors, graph: r.graph };
}

export function run(input, options = {}) {
  const { mode = 'async', tie = 'min', maxRounds = 50, maxSize = null } = options;
  const v = validate(input, options);
  if (!v.ok) return { events: [], result: null, status: 'invalid', metadata: { errors: v.errors } };
  const g = v.graph, ids = g.nodes.map(n => n.id), order = options.order ?? [...ids].sort();
  const adj = new Map(ids.map(id => [id, new Map()]));
  for (const { u, v: w2, w } of g.edges) { adj.get(u).set(w2, w); adj.get(w2).set(u, w); }
  let labels = Object.fromEntries(ids.map(n => [n, n]));
  // Size-constrained variant (Meyerhenke, Sanders & Schulz 2014): a node may only join a label whose group
  // would stay within maxSize nodes. Async only; sizes are updated as labels change.
  const size = Object.fromEntries(ids.map(n => [n, 1]));
  const signature = l => ids.map(n => l[n]).join('|');
  const seen = new Map([[signature(labels), 0]]);
  const events = [];
  let round = 0, status = 'running', step = 0;
  while (status === 'running') {
    const base = { ...labels }, pending = { ...labels };
    let changes = 0;
    for (let index = 0; index < order.length; index++) {
      const node = order[index], before = { ...labels };
      const source = mode === 'sync' ? base : labels;
      const { votes: allVotes, neighbors } = votesFor(adj, source, node);
      const old = source[node];
      const votes = maxSize ? Object.fromEntries(Object.entries(allVotes).filter(([l]) => l === old || size[l] + 1 <= maxSize)) : allVotes;
      const { label, tied } = chooseLabel(votes, old, tie), changed = label !== old;
      if (changed && maxSize) { size[old]--; size[label] = (size[label] || 0) + 1; }
      pending[node] = label;
      if (mode === 'async') labels[node] = label;
      if (changed) changes++;
      const roundEnd = index === order.length - 1;
      if (roundEnd && mode === 'sync') labels = { ...pending };
      const ev = {
        eventId: `r${round + 1}-${node}`, phase: `round-${round + 1}`, step: step++, kind: roundEnd ? 'update-round-end' : 'update',
        round: round + 1, index, node, old, label, changed, votes, tied, neighbors, before, after: { ...labels },
        pending: { ...pending }, committed: mode === 'async' || roundEnd, mode, tie, ...(maxSize ? { allVotes, maxSize } : {}),
        decision: changed ? `${node}: ${old} → ${label}` : L(`${node} 保持 ${old}`, `${node} keeps ${old}`),
        sourceVersion: ENGINE_VERSION
      };
      if (roundEnd) {
        round++;
        ev.changes = changes;
        const sig = signature(labels);
        if (changes === 0) status = 'stable';
        else if (seen.has(sig)) { status = 'cycle'; ev.cycleStart = seen.get(sig); ev.period = round - seen.get(sig); }
        else if (round >= maxRounds) status = 'limit';
        seen.set(sig, round);
      }
      ev.status = status;
      ev.metrics = { cut: cutsize(g, labels), groups: new Set(Object.values(labels)).size };
      events.push(ev);
    }
  }
  const result = { mode, tie, ...(maxSize ? { maxSize } : {}), order, labels: { ...labels }, rounds: round, status, cut: cutsize(g, labels), grouping: groupsKey(labels) };
  return { events, result, status, metadata: { engine: 'label-propagation', version: ENGINE_VERSION, adaptedFrom: 'Su3037/clustering-lab5-label-propagation@7b4eca7' } };
}

export const PRESETS = {
  pair: { nodes: ['A', 'B'], edges: [['A', 'B', 1]], positions: { A: [200, 240], B: [510, 240] } },
  tie: { nodes: ['A', 'B', 'C', 'D'], edges: [['A', 'B', 1], ['A', 'C', 1], ['A', 'D', 4]], positions: { A: [350, 240], B: [150, 100], C: [150, 380], D: [600, 240] } },
  island: { nodes: ['A', 'B', 'C', 'D', 'E'], edges: [['A', 'B', 3], ['C', 'D', 2]], positions: { A: [150, 130], B: [310, 130], C: [150, 380], D: [310, 380], E: [600, 250] } }
};
