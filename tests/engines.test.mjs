// Regression and property tests for every course engine. Run: node --test tests/
import test from 'node:test';
import assert from 'node:assert/strict';
import { G01, compareKeys, cutsize, randomGraph, sameGrouping, groupsKey } from '../site/engines/graph.js';
import * as AF from '../site/engines/affinity.js';
import * as M from '../site/engines/merge.js';
import * as LP from '../site/engines/lp.js';
import * as SP from '../site/engines/spectral.js';
import * as KL from '../site/engines/kl.js';
import * as FM from '../site/engines/fm.js';
import * as RW from '../site/engines/rw.js';

const pair = l => l.map(p => `${p.u}-${p.v}:${p.score}`);
const parts = r => r.clusters.map(c => c.join('')).sort().join('|');

test('graph: compareKeys is numeric-first, the course-wide fix', () => {
  assert.equal(compareKeys([-5, 'A'], [-1, 'A']), -1);
  assert.equal(String([-5, 'A']) < String([-1, 'A']), false, 'string comparison gets it wrong');
  assert.equal(compareKeys([-10, 'A'], [-9, 'A']), -1);
  assert.equal(String([-10, 'A']) < String([-9, 'A']), true, 'right here only by accident of the first digit');
  assert.equal(compareKeys([-2.5, 'B'], [-2, 'A']), -1);
  assert.equal(compareKeys([-5, ['A', 'B']], [-5, ['D']]), -1);
});

test('M02 affinity: edge 6 pairs, shared 10 pairs, priority and pin-count', () => {
  assert.deepEqual(pair(AF.edgeWeight(G01)), ['A-B:5', 'D-E:5', 'B-C:4', 'C-D:2', 'A-C:1', 'C-E:1']);
  const shared = AF.sharedNeighbors(G01);
  assert.deepEqual(pair(shared), ['A-B:6', 'D-E:6', 'A-C:5', 'B-C:5', 'C-D:3', 'C-E:3', 'B-D:2', 'A-D:1', 'A-E:1', 'B-E:1']);
  const bd = shared.find(p => p.u === 'B' && p.v === 'D');
  assert.equal(bd.parts.direct, 0); assert.deepEqual(bd.parts.via.map(v => [v.x, v.min]), [['C', 2]]);
  const ac = shared.find(p => p.u === 'A' && p.v === 'C');
  assert.equal(ac.parts.direct, 1); assert.deepEqual(ac.parts.via.map(v => [v.x, v.min]), [['B', 4]]);
  assert.equal(pair(AF.edgeWeight(AF.PRIORITY_GRAPH))[0], 'X-Y:5');
  assert.equal(pair(AF.sharedNeighbors(AF.PRIORITY_GRAPH))[0], 'P-Q:8');
  const pc = AF.pinCount(AF.TINY_NETLIST);
  assert.equal(pc.scores[0].u + pc.scores[0].v, 'EF'); assert.equal(pc.scores[0].score, 1);
  assert.equal(pc.scores.find(p => p.u === 'A' && p.v === 'B').score, 0.5);
  assert.equal(pc.raw.find(p => p.u === 'A' && p.v === 'B').score, 2);
  // reversed and shuffled input yields the same ranking
  const rev = { nodes: [...G01.nodes].reverse(), edges: [...G01.edges].reverse().map(e => ({ u: e.v, v: e.u, w: e.w })) };
  assert.deepEqual(pair(AF.sharedNeighbors(rev)), pair(shared));
});

test('M03 greedy merge: fixed comparator and the four configurations', () => {
  const cfg = [[2, null, 'ABC|DE', 3, [18, 13, 8, 3], true], [3, null, 'ABC|D|E', 8, [18, 13, 8], true],
    [2, 2, 'AB|C|DE', 8, [18, 13, 8], false], [2, 3, 'ABC|DE', 3, [18, 13, 8, 3], true]];
  for (const [k, cap, p, cut, traj, reached] of cfg) {
    const r = M.run(G01, { k, capacity: cap }).result;
    assert.equal(parts(r), p); assert.equal(r.cut, cut); assert.deepEqual(r.cutTrajectory, traj); assert.equal(r.targetReached, reached);
  }
  assert.equal(M.run(G01, { k: 2, capacity: 2 }).result.stopReason, 'capacity-blocked');
});

test('M03 regression: the original string comparison reproduces cut 9/16/12/16', () => {
  const cuts = [[2, null], [3, null], [2, 2], [2, 3]].map(([k, capacity]) => M.run(G01, { k, capacity, legacyComparator: true }).result.cut);
  assert.deepEqual(cuts, [9, 16, 12, 16]);
  const first = M.run(G01, { k: 2, legacyComparator: true }).events[1].decision;
  assert.equal(`${first.a}-${first.b}@${first.affinity}`, 'A-C@1', 'legacy picks A–C@1 first');
});

test('M03: two-digit and fractional affinities, cut drop equals affinity, every node once', () => {
  const g = { nodes: ['P', 'Q', 'R', 'S'], edges: [['P', 'Q', 2], ['R', 'S', 10], ['Q', 'R', 2.5]] };
  const r = M.run(g, { k: 1 });
  assert.equal(r.events[1].decision.affinity, 10);
  assert.equal(r.events[2].decision.affinity, 2.5);
  for (let seed = 1; seed <= 200; seed++) {
    const rg = randomGraph(seed, { n: 7, p: 0.5, maxW: 12 });
    const run = M.run(rg, { k: 1 + (seed % 3), capacity: seed % 2 ? null : 3 });
    for (const e of run.events.filter(e => e.kind === 'merge')) assert.equal(e.metrics.drop, e.decision.affinity);
    const all = run.result.clusters.flat().sort();
    assert.deepEqual(all, rg.nodes.map(n => n.id).sort());
  }
});

test('M04: infeasible bound, greedy trap and suboptimal are distinguished', () => {
  assert.equal(M.diagnose(G01, { k: 2, capacity: 2 }).kind, 'infeasible-by-bound');
  const trap = M.diagnose(M.M04_GRAPHS.greedy_trap, { k: 2, capacity: 3 });
  assert.equal(trap.kind, 'greedy-stuck'); assert.equal(trap.run.result.count, 3); assert.equal(trap.oracle.bestCutAtK.cut, 10);
  const sub = M.diagnose(M.M04_GRAPHS.suboptimal, { k: 2, capacity: 2 });
  assert.equal(sub.kind, 'feasible-suboptimal'); assert.equal(sub.run.result.cut, 18); assert.equal(sub.oracle.bestCutAtK.cut, 11);
  const k3 = M.run(G01, { k: 3, capacity: 2 }).result;
  assert.equal(parts(k3), 'AB|C|DE'); assert.equal(k3.targetReached, true); assert.equal(k3.capacityCompliant, true);
  assert.equal(M.run({ nodes: [{ id: 'A', size: 3 }, 'B'], edges: [['A', 'B', 1]] }, { k: 1, capacity: 2 }).status, 'invalid');
  assert.equal(M.run({ nodes: ['A', 'B', 'C'], edges: [] }, { k: 1 }).result.stopReason, 'no-positive-affinity');
});

test('M04: greedy never violates capacity and never beats the exhaustive optimum (random)', () => {
  for (let seed = 1; seed <= 150; seed++) {
    const g = randomGraph(seed, { n: 6, p: 0.5, sizes: true });
    const capacity = 3 + (seed % 3), k = 2 + (seed % 2);
    const v = M.validate(g, { k, capacity });
    if (!v.ok) continue;
    const d = M.diagnose(g, { k, capacity }), r = d.run.result;
    assert.ok(r.capacityCompliant);
    if (r.targetReached && d.oracle.bestCutAtK) assert.ok(r.cut >= d.oracle.bestCutAtK.cut);
    if (d.kind === 'greedy-stuck') assert.ok(d.oracle.bestCutAtK);
  }
});

test('M05 label propagation: async cut drop, size cap, trivial fixed point, synchronous star', () => {
  // Each asynchronous change lowers the cut by exactly (votes for the new label − votes for the old one).
  const run = LP.run(G01);
  let prev = G01.edges.reduce((s, e) => s + e.w, 0);
  for (const e of run.events) { assert.equal(prev - e.metrics.cut, e.changed ? e.votes[e.label] - (e.votes[e.old] || 0) : 0); prev = e.metrics.cut; }
  const tri = { nodes: ['A', 'B', 'C', 'D', 'E', 'F'], edges: [['A', 'B', 1], ['A', 'C', 1], ['B', 'C', 1], ['C', 'D', 1], ['D', 'E', 1], ['D', 'F', 1], ['E', 'F', 1]] };
  assert.equal(LP.run(tri).result.grouping, 'A,B,C,D,E,F');
  assert.equal(LP.run(tri, { tie: 'max' }).result.cut, 1);
  const cap = LP.run(tri, { maxSize: 3 }).result;
  assert.equal(cap.grouping, 'A,B,C | D,E,F');
  const sizes = Object.values(cap.labels).reduce((m, l) => ((m[l] = (m[l] || 0) + 1), m), {});
  assert.ok(Object.values(sizes).every(n => n <= 3));
  assert.equal(LP.validate(tri, { mode: 'sync', maxSize: 3 }).ok, false);
  const star = { nodes: ['H', 'a', 'b', 'c', 'd'], edges: [['H', 'a', 1], ['H', 'b', 1], ['H', 'c', 1], ['H', 'd', 1]] };
  const s = LP.run(star, { mode: 'sync' });
  assert.equal(s.result.status, 'cycle'); assert.equal(s.events.at(-1).period, 2);
});

test('M05 label propagation: golden, cycle, bridge, order, film graphs', async () => {
  const r = LP.run(G01).result;
  assert.deepEqual(r.labels, { A: 'B', B: 'B', C: 'B', D: 'E', E: 'E' }); assert.equal(r.rounds, 2); assert.equal(r.status, 'stable'); assert.equal(r.cut, 3);
  assert.equal(LP.run(LP.PRESETS.pair, { mode: 'sync' }).result.status, 'cycle');
  assert.equal(LP.run(LP.PRESETS.pair, { mode: 'async' }).result.status, 'stable');
  const heavy = structuredClone(G01); heavy.edges.find(e => e.u === 'C' && e.v === 'D').w = 10;
  assert.equal(LP.run(heavy).result.cut, 5);
  const rev = LP.run(G01, { order: ['E', 'D', 'C', 'B', 'A'] }).result;
  assert.ok(sameGrouping(rev.labels, r.labels)); assert.equal(rev.rounds, 3);
  const C = LP.run(G01).events.find(e => e.node === 'C' && e.round === 1);
  assert.deepEqual(C.votes, { B: 5, D: 2, E: 1 });
  const fs = await import('node:fs');
  const f = JSON.parse(fs.readFileSync(new URL('../site/data/m05-label-propagation/film-graphs.json', import.meta.url)));
  const c = LP.run(f.circuit).result, p = LP.run(f.contacts).result;
  assert.equal(f.circuit.edges.length, 56); assert.equal(f.circuit.edges.reduce((s, e) => s + e[2], 0), 202);
  assert.equal(c.rounds, 5); assert.equal(c.cut, 2); assert.equal(p.rounds, 3); assert.equal(p.cut, 4);
});

test('M06 spectral: live eigen-solve, sweep 6/3/5/6, 15 bipartitions, flip, disconnected', () => {
  const r = SP.run(G01).result;
  assert.ok(Math.abs(r.eigenvalues[1] - 1.7733143437197119) < 1e-10);
  assert.deepEqual(r.order, ['E', 'D', 'C', 'B', 'A']);
  assert.deepEqual(r.sweep.map(s => s.cut), [6, 3, 5, 6]);
  assert.deepEqual(r.sweep.filter(s => s.legal).map(s => s.k), [2, 3]);
  assert.equal(r.cut, 3); assert.equal(r.bestK, 2);
  assert.ok(r.diagnostics.residual < 1e-10 && r.diagnostics.rowSumMax < 1e-12);
  assert.equal(SP.unlabelledBipartitions(5), 15);
  assert.equal(SP.exhaustiveBisection(G01).count, 15);
  assert.equal(SP.exhaustiveBisection(G01, { minFraction: 0, maxFraction: 1 }).unconstrained.cut, 3, 'unconstrained optimum is not a singleton');
  const stored = SP.run(G01, { vector: ['A', 'B', 'C', 'D', 'E'].map(i => SP.STORED_VECTOR[i]) }).result;
  assert.ok(Math.abs(stored.diagnostics.residual - 0.0044) < 0.0002, 'three-decimal stored vector residual ≈ 0.0044');
  assert.deepEqual(stored.sweep.map(s => s.cut), [6, 3, 5, 6]);
  const flipped = SP.run(G01, { vector: r.fiedler.map(x => -x) }).result;
  assert.deepEqual(flipped.order, [...r.order].reverse()); assert.equal(flipped.cut, r.cut);
  const d = SP.run(SP.DISCONNECTED).result;
  assert.ok(Math.abs(d.eigenvalues[1]) < 1e-9 && !d.diagnostics.connected);
  assert.ok(SP.run(SP.DEGENERATE).result.diagnostics.degenerate);
  for (let seed = 1; seed <= 60; seed++) {
    const g = randomGraph(seed, { n: 8, p: 0.6 });
    const x = SP.run(g).result;
    const comps = x.diagnostics.components.length;
    if (comps === 1) assert.ok(x.diagnostics.residual < 1e-8, `seed ${seed}`);
    for (const s of x.sweep) assert.equal(s.cut, cutsize(g, Object.fromEntries(g.nodes.map(n => [n.id, s.left.includes(n.id) ? 0 : 1]))));
  }
});

test('M07 KL: documented passes, empty prefix, AB=1, random invariants', () => {
  const r = KL.run(G01, { initial: KL.SEED }).result;
  const p1 = r.passes[0], p2 = r.passes[1];
  assert.equal(p1.startCut, 12);
  assert.deepEqual(p1.swaps.map(s => [s.a + s.b, s.gain, s.cutAfter]), [['AD', 9, 3], ['EC', -8, 11]]);
  assert.deepEqual(p1.prefixGains, [0, 9, 1]); assert.equal(p1.bestK, 1); assert.equal(p1.acceptedCut, 3);
  assert.deepEqual(p2.prefixGains, [0, -8, -6]); assert.equal(p2.bestK, 0); assert.equal(r.cut, 3);
  const g = structuredClone(G01); g.edges[0].w = 1;
  const k = KL.run(g, { initial: KL.SEED });
  assert.equal(k.events[0].metrics.cut, 8); assert.equal(k.result.passes[0].swaps[0].gain, 5);
  let cases = 0;
  for (let seed = 1; seed <= 300; seed++) {
    const rg = randomGraph(seed, { n: 4 + (seed % 4), p: 0.55 });
    const ids = rg.nodes.map(n => n.id), init = Object.fromEntries(ids.map((id, i) => [id, i % 2]));
    const res = KL.run(rg, { initial: init });
    for (const pass of res.result.passes) {
      const used = pass.swaps.flatMap(s => [s.a, s.b]);
      assert.equal(new Set(used).size, used.length);
      for (const s of pass.swaps) { assert.equal(s.cutBefore - s.cutAfter, s.gain); cases++; }
      assert.equal(pass.startCut - pass.acceptedCut, pass.bestGain);
    }
    // the selected swap is the true maximum over all unlocked cross pairs (independent enumeration)
    const first = res.events.find(e => e.kind === 'trial-swap');
    if (first) {
      let best = -Infinity;
      for (const a of ids.filter(v => init[v] === 0)) for (const b of ids.filter(v => init[v] === 1)) {
        const t = { ...init, [a]: 1, [b]: 0 };
        best = Math.max(best, cutsize(rg, init) - cutsize(rg, t));
      }
      assert.equal(first.trialGain, best);
    }
    const s0 = ids.filter(v => res.result.assignment[v] === 0).length;
    assert.equal(s0, ids.filter(v => init[v] === 0).length);
  }
  assert.ok(cases > 300);
});

test('M08 FM: documented seed, legality, disproved hillclimb, replacement escape, multi-pin', () => {
  const r = FM.run(G01, { initial: FM.SEED, maxDiff: 1 });
  const g0 = Object.fromEntries(r.events[0].gains.map(x => [x.node, [x.gain, x.legal]]));
  assert.deepEqual(g0, { A: [6, false], B: [1, true], C: [-4, true], D: [3, true], E: [6, false] });
  const p = r.result.passes[0];
  assert.deepEqual(p.moves.map(m => [m.node, m.gain, m.cutAfter]), [['D', 3, 9], ['A', 6, 3], ['C', -2, 5], ['E', -6, 11], ['B', -1, 12]]);
  assert.deepEqual(p.prefixGains, [0, 3, 9, 7, 1, 0]); assert.equal(p.bestK, 2); assert.equal(p.acceptedCut, 3);
  assert.equal(r.result.passes[1].bestK, 0);
  const d = p.moves[0]; assert.deepEqual([d.fs.map(x => x.w), d.te.map(x => x.w)], [[5], [2]]);
  const h = FM.LEGACY_HILLCLIMB, hr = FM.run(h, { initial: h.seed, maxDiff: h.maxDiff, firstPassOnly: true });
  assert.equal(hr.events[0].metrics.cut, 18, 'claimed 9 is wrong');
  assert.equal(hr.events[0].gains.find(x => x.node === 'E').gain, 10);
  assert.ok(hr.events[0].gains.find(x => x.node === 'E').legal, 'a legal positive gain exists');
  assert.equal(hr.result.passes[0].acceptedCut, 8); assert.equal(FM.exhaustive(h, 2).cut, 8);
  const e = FM.NEG_ESCAPE, er = FM.run(e, { initial: e.seed, maxDiff: e.maxDiff });
  assert.ok(er.events[0].gains.filter(x => x.legal).every(x => x.gain <= 0));
  assert.deepEqual(er.result.passes[0].moves.slice(0, 3).map(m => m.gain), [-1, -1, 4]);
  assert.equal(er.result.passes[0].bestK, 3); assert.equal(er.result.cut, 4); assert.equal(FM.exhaustive(e, 2).cut, 4);
  const s = FM.SEVEN_NODE, sr = FM.run(s, { initial: s.seed, maxDiff: 1 });
  assert.equal(sr.result.passes[0].startCut, 22); assert.equal(sr.result.passes[0].bestK, 3); assert.equal(sr.result.cut, 1);
  assert.equal(sr.result.hasMultiPin, false, 'the attachment "hypergraph" case has only 2-pin edges');
  const mp = { nodes: ['A', 'B', 'C', 'D'], nets: [{ id: 'bus', pins: ['A', 'B', 'C'], w: 2 }, { id: 'n2', pins: ['C', 'D'], w: 1 }] };
  const mg = FM.gainsFromScratch(FM.toNets(mp).nets, { A: 0, B: 0, C: 1, D: 1 }, ['A', 'B', 'C', 'D']);
  assert.equal(mg.C.gain, 1); assert.equal(mg.A.gain, 0);
});

test('M08: incremental gains equal from-scratch gains and cut differences (random, multi-pin)', () => {
  let moves = 0;
  for (let seed = 1; seed <= 250; seed++) {
    const rg = randomGraph(seed, { n: 5 + (seed % 4), p: 0.5 });
    const ids = rg.nodes.map(n => n.id);
    if (seed % 3 === 0) rg.nets = [{ id: 'm1', pins: ids.slice(0, 3), w: 2 }, { id: 'm2', pins: ids.slice(-3), w: 3 }];
    const init = Object.fromEntries(ids.map((id, i) => [id, i % 2]));
    const run = FM.run(rg, { initial: init, maxDiff: 1 });
    const { nets } = FM.toNets(rg);
    for (const ev of run.events.filter(e => e.kind === 'trial-move')) {
      const scratch = FM.gainsFromScratch(nets, ev.after, ids);
      for (const g of ev.gains.filter(x => !x.locked)) assert.equal(g.gain, scratch[g.node].gain, `seed ${seed}`);
      assert.equal(ev.metrics.cutBefore - ev.metrics.cut, ev.trialGain); moves++;
    }
    for (const pass of run.result.passes) assert.ok(FM.balanceOk(pass.accepted, ids, 1));
  }
  assert.ok(moves > 500);
});

test('M09 RW: cycle error, chain 7/10, candidate DAG 8 clusters / 20 instances / delay 8', () => {
  assert.equal(RW.run({ ...RW.CHAIN, edges: [...RW.CHAIN.edges, ['O', 'P']] }).status, 'invalid');
  assert.equal(RW.evaluatePartition(RW.CHAIN, [['P', 'X'], ['Y', 'O']]).maxDelay, 7);
  assert.equal(RW.evaluatePartition(RW.CHAIN, [['P'], ['X', 'Y'], ['O']]).maxDelay, 10);
  const r = RW.run(RW.CANDIDATE_DAG).result;
  assert.deepEqual(r.labels, { a: 1, b: 1, c: 1, d: 2, e: 2, f: 2, g: 3, h: 2, i: 7, j: 7, k: 8, l: 8 });
  assert.equal(Object.keys(r.clusters).length, 8); assert.equal(r.instanceCount, 20);
  assert.deepEqual(r.outputDelays, { k: 8, l: 8 });
  assert.ok(r.legality.ok);
  assert.deepEqual(r.clusters.k, ['g', 'i', 'j', 'k']); assert.deepEqual(r.clusters.l, ['e', 'g', 'j', 'l']);
  assert.equal(r.replicated.find(x => x.id === 'b').copies, 3);
  // the same groups cannot be used without replication: they overlap
  assert.equal(RW.evaluatePartition(RW.CANDIDATE_DAG, Object.values(r.clusters)).ok, false);
});

test('M09: RW label ≥ arrival lower bound and reconstruction legal on random DAGs', () => {
  for (let seed = 1; seed <= 120; seed++) {
    const rg = randomGraph(seed, { n: 9, p: 0.35 });
    const ids = rg.nodes.map(n => n.id);
    const edges = rg.edges.map(e => [e.u, e.v]); // u < v alphabetically: acyclic
    if (!edges.length) continue;
    const dag = { nodes: ids, edges, nodeDelay: 1, capacity: 3, D: 2 };
    const r = RW.run(dag);
    assert.equal(r.status, 'completed', `seed ${seed}`);
    assert.ok(r.result.legality.ok);
    const delta = r.result.delta;
    for (const po of Object.keys(r.result.outputDelays)) {
      const longest = Math.max(...ids.filter(x => delta[x][po] !== null).map(x => 1 + delta[x][po]));
      assert.ok(r.result.outputDelays[po] >= longest, 'never faster than the pure node-delay path');
    }
    assert.equal(Math.max(...Object.values(r.result.outputDelays)), Math.max(...Object.keys(r.result.outputDelays).map(p => r.result.labels[p])), `seed ${seed}: output arrival equals label`);
  }
});

test('M09: replication pays for itself on the candidate DAG (8 vs best non-replicating 10)', async () => {
  const fs = await import('node:fs');
  const nr = JSON.parse(fs.readFileSync(new URL('../site/data/m09-rajaraman-wong/no-replication.json', import.meta.url)));
  assert.equal(nr.bestMaxDelay, 10);
  const ev = RW.evaluatePartition(RW.CANDIDATE_DAG, nr.example);
  assert.ok(ev.ok); assert.equal(ev.maxDelay, 10);
  assert.ok(RW.run(RW.CANDIDATE_DAG).result.maxDelay < ev.maxDelay);
  // every non-replicating partition the search could miss would contradict the lower bound: delay ≥ longest path (5) + D
  assert.ok(nr.bestMaxDelay >= 5 + 3);
});
