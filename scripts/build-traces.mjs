#!/usr/bin/env node
// Runs the browser engines in Node and writes the traces that films and slides read.
// Films and slides never hard-code an algorithm result: they draw these events.
import fs from 'node:fs';
import path from 'node:path';
import { G01, ENGINE_VERSION, cutsize } from '../site/engines/graph.js';
import * as AF from '../site/engines/affinity.js';
import * as M from '../site/engines/merge.js';
import * as LP from '../site/engines/lp.js';
import * as SP from '../site/engines/spectral.js';
import * as KL from '../site/engines/kl.js';
import * as FM from '../site/engines/fm.js';
import * as RW from '../site/engines/rw.js';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const out = (id, data) => {
  const p = path.join(ROOT, 'site/data', id, 'traces.json');
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify({ moduleId: id, engineVersion: ENGINE_VERSION, generatedBy: 'scripts/build-traces.mjs', ...data }, null, 1));
  console.log('wrote', path.relative(ROOT, p));
};
const g01 = { nodes: G01.nodes.map(n => n.id), edges: G01.edges.map(e => [e.u, e.v, e.w]), positions: G01.positions };

out('m02-affinity-metrics', {
  g01, priority: AF.PRIORITY_GRAPH, netlist: AF.TINY_NETLIST,
  edge: AF.edgeWeight(G01), shared: AF.sharedNeighbors(G01),
  priorityEdge: AF.edgeWeight(AF.PRIORITY_GRAPH), priorityShared: AF.sharedNeighbors(AF.PRIORITY_GRAPH),
  pin: AF.pinCount(AF.TINY_NETLIST)
});

const mergeRuns = {};
for (const [k, capacity] of [[2, null], [3, null], [2, 2], [2, 3], [3, 2]]) mergeRuns[`k${k}-cap${capacity ?? 'none'}`] = M.run(G01, { k, capacity });
const legacy = M.run(G01, { k: 2, legacyComparator: true });
out('m03-greedy-pair-merge', { g01, runs: mergeRuns, legacy: { result: legacy.result, first: legacy.events[1].decision } });

out('m04-size-constrained-agglomerative', {
  g01, graphs: M.M04_GRAPHS,
  cap2: M.diagnose(G01, { k: 2, capacity: 2 }), cap3: M.diagnose(G01, { k: 2, capacity: 3 }), k3cap2: M.diagnose(G01, { k: 3, capacity: 2 }),
  trap: M.diagnose(M.M04_GRAPHS.greedy_trap, { k: 2, capacity: 3 }), suboptimal: M.diagnose(M.M04_GRAPHS.suboptimal, { k: 2, capacity: 2 }),
  uneven: M.run({ nodes: G01.nodes.map(n => ({ id: n.id, size: n.id === 'A' ? 2 : 1 })), edges: G01.edges }, { k: 2, capacity: 3 })
});

const film = JSON.parse(fs.readFileSync(path.join(ROOT, 'site/data/m05-label-propagation/film-graphs.json'), 'utf8'));
const heavy = structuredClone(G01); heavy.edges.find(e => e.u === 'C' && e.v === 'D').w = 10;
out('m05-label-propagation', {
  g01, golden: LP.run(G01), reverse: LP.run(G01, { order: ['E', 'D', 'C', 'B', 'A'] }), sync: LP.run(G01, { mode: 'sync' }),
  pairSync: LP.run(LP.PRESETS.pair, { mode: 'sync', maxRounds: 6 }), pairAsync: LP.run(LP.PRESETS.pair, { mode: 'async' }), pair: LP.PRESETS.pair,
  heavy: LP.run(heavy), syncG01: LP.run(G01, { mode: 'sync', maxRounds: 10 }), tieMax: LP.run(G01, { tie: 'max' }),
  circuit: { graph: film.circuit, run: LP.run(film.circuit), geometric: geometric(film.circuit) },
  contacts: { graph: film.contacts, run: LP.run(film.contacts) }
});
// "Ruler" split of the fictional 24-cell circuit into three columns by drawing position (from the author's Lab05 film).
function geometric(g) {
  const a = Object.fromEntries(g.nodes.map(n => [n, g.positions[n][0] < 700 ? 'L' : g.positions[n][0] < 1200 ? 'M' : 'R']));
  return { labels: a, cut: cutsize({ nodes: g.nodes.map(id => ({ id })), edges: g.edges.map(([u, v, w]) => ({ u, v, w })) }, a) };
}

out('m06-spectral-bisection', {
  g01, run: SP.run(G01), laplacian: SP.laplacian(G01), stored: SP.run(G01, { vector: ['A', 'B', 'C', 'D', 'E'].map(i => SP.STORED_VECTOR[i]), vectorSource: '原作存储' }).result.diagnostics,
  exhaustive: SP.exhaustiveBisection(G01), unconstrained: SP.exhaustiveBisection(G01, { minFraction: 0, maxFraction: 1 }).unconstrained,
  disconnected: { graph: SP.DISCONNECTED, run: SP.run(SP.DISCONNECTED).result }, bipartitions5: SP.unlabelledBipartitions(5)
});

const ab1 = structuredClone(G01); ab1.edges[0].w = 1;
out('m07-kernighan-lin', { g01, seed: KL.SEED, run: KL.run(G01, { initial: KL.SEED }), ab1: KL.run(ab1, { initial: KL.SEED }) });

out('m08-fiduccia-mattheyses', {
  g01, seed: FM.SEED, run: FM.run(G01, { initial: FM.SEED, maxDiff: 1 }),
  legacy: { graph: FM.LEGACY_HILLCLIMB, run: FM.run(FM.LEGACY_HILLCLIMB, { initial: FM.LEGACY_HILLCLIMB.seed, maxDiff: 2, firstPassOnly: true }), optimum: FM.exhaustive(FM.LEGACY_HILLCLIMB, 2) },
  escape: { graph: FM.NEG_ESCAPE, run: FM.run(FM.NEG_ESCAPE, { initial: FM.NEG_ESCAPE.seed, maxDiff: 2 }), optimum: FM.exhaustive(FM.NEG_ESCAPE, 2) },
  seven: { graph: FM.SEVEN_NODE, run: FM.run(FM.SEVEN_NODE, { initial: FM.SEVEN_NODE.seed, maxDiff: 1 }) }
});

out('m09-rajaraman-wong', {
  chain: RW.CHAIN, chainOne: RW.evaluatePartition(RW.CHAIN, [['P', 'X'], ['Y', 'O']]), chainTwo: RW.evaluatePartition(RW.CHAIN, [['P'], ['X', 'Y'], ['O']]),
  dag: RW.CANDIDATE_DAG, run: RW.run(RW.CANDIDATE_DAG)
});
