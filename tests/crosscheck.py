#!/usr/bin/env python3
"""Cross-language check: the browser engines (site/engines/*.js, run in Node) against the
independent Python references (python/<module>/reference.py) on seeded random inputs.
Compares step-level data, not just final numbers. Run: python3 tests/crosscheck.py
"""
import importlib.util
import json
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ref(module):
    spec = importlib.util.spec_from_file_location(module, ROOT / "python" / module / "reference.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def graph(rng, n, p=0.5, maxw=9, sizes=False):
    nodes = [chr(65 + i) for i in range(n)]
    edges = [[u, v, rng.randint(1, maxw)] for i, u in enumerate(nodes) for v in nodes[i + 1:] if rng.random() < p]
    g = {"nodes": nodes, "edges": edges}
    if sizes:
        g["sizes"] = {v: rng.randint(1, 3) for v in nodes}
    return g


rng = random.Random(20261023)
cases = {"m02": [], "m03": [], "m05": [], "m06": [], "m07": [], "m08": [], "m09": []}
for _ in range(80):
    cases["m02"].append(graph(rng, rng.randint(2, 8)))
for _ in range(120):
    g = graph(rng, rng.randint(2, 8), sizes=rng.random() < 0.5)
    cases["m03"].append({"g": g, "k": rng.randint(1, 4), "cap": rng.choice([None, 3, 4, 6])})
for _ in range(120):
    g = graph(rng, rng.randint(1, 8), p=0.45)
    order = g["nodes"][:]
    rng.shuffle(order)
    cases["m05"].append({"g": g, "mode": rng.choice(["async", "sync"]), "tie": rng.choice(["min", "max", "keep"]), "order": order})
for _ in range(60):
    g = graph(rng, rng.randint(3, 9), p=0.7)
    cases["m06"].append(g)
for _ in range(120):
    g = graph(rng, rng.randint(2, 8), p=0.55)
    ids = g["nodes"][:]
    rng.shuffle(ids)
    cases["m07"].append({"g": g, "init": {v: (0 if i < len(ids) // 2 else 1) for i, v in enumerate(ids)}})
for _ in range(120):
    g = graph(rng, rng.randint(3, 8), p=0.5)
    if rng.random() < 0.3:
        g["nets"] = [{"id": f"m{i}", "pins": rng.sample(g["nodes"], 3), "w": rng.randint(1, 4)} for i in range(2)]
    ids = g["nodes"][:]
    rng.shuffle(ids)
    cases["m08"].append({"g": g, "init": {v: i % 2 for i, v in enumerate(ids)}, "maxDiff": rng.choice([1, 2])})
for _ in range(80):
    n = rng.randint(3, 10)
    nodes = [chr(97 + i) for i in range(n)]
    edges = [[u, v] for i, u in enumerate(nodes) for v in nodes[i + 1:] if rng.random() < 0.35]
    if edges:
        cases["m09"].append({"nodes": nodes, "edges": edges, "node_delay": 1, "capacity": rng.choice([2, 3, 4]), "D": rng.choice([1, 2, 3])})

js = r"""
import fs from 'node:fs';
import * as AF from './site/engines/affinity.js'; import * as M from './site/engines/merge.js';
import * as LP from './site/engines/lp.js'; import * as SP from './site/engines/spectral.js';
import * as KL from './site/engines/kl.js'; import * as FM from './site/engines/fm.js'; import * as RW from './site/engines/rw.js';
const c = JSON.parse(fs.readFileSync(0, 'utf8'));
const t = p => [p.u, p.v, p.score];
const out = {
  m02: c.m02.map(g => ({ edge: AF.edgeWeight(g).map(t), shared: AF.sharedNeighbors(g).map(t) })),
  m03: c.m03.map(x => { const r = M.run(x.g, { k: x.k, capacity: x.cap }); return r.status === 'invalid' ? 'invalid' : { parts: r.result.labels, traj: r.result.cutTrajectory, reached: r.result.targetReached, stop: r.result.stopReason }; }),
  m05: c.m05.map(x => { const r = LP.run(x.g, { mode: x.mode, tie: x.tie, order: x.order }); return { labels: r.result.labels, rounds: r.result.rounds, status: r.result.status, cut: r.result.cut, votes: r.events.map(e => [e.node, e.label, e.votes]) }; }),
  m06: c.m06.map(g => { const r = SP.run(g, { balance: { minFraction: 0.4, maxFraction: 0.6 } }); return r.status === 'invalid' ? 'invalid' : { values: r.result.eigenvalues, connected: r.result.diagnostics.connected, gap: r.result.diagnostics.gap, order: r.result.order, sweep: r.result.sweep.map(s => s.cut), cut: r.result.cut }; }),
  m07: c.m07.map(x => { const r = KL.run(x.g, { initial: x.init }); return r.status === 'invalid' ? 'invalid' : r.result.passes.map(p => ({ swaps: p.swaps.map(s => [s.a, s.b, s.gain, s.cutAfter]), k: p.bestK, cut: p.acceptedCut })); }),
  m08: c.m08.map(x => { const r = FM.run(x.g, { initial: x.init, maxDiff: x.maxDiff }); return r.status === 'invalid' ? 'invalid' : r.result.passes.map(p => ({ moves: p.moves.map(m => [m.node, m.gain, m.cutAfter]), k: p.bestK, cut: p.acceptedCut })); }),
  m09: c.m09.map(d => { const r = RW.run({ nodes: d.nodes, edges: d.edges, nodeDelay: 1, capacity: d.capacity, D: d.D }); return { labels: r.result.labels, clusters: r.result.clusters, instances: r.result.instanceCount, out: r.result.outputDelays }; })
};
console.log(JSON.stringify(out));
"""
proc = subprocess.run(["node", "--input-type=module", "-e", js], cwd=ROOT, input=json.dumps(cases), text=True, capture_output=True)
if proc.returncode:
    print(proc.stderr)
    sys.exit(1)
J = json.loads(proc.stdout)
fails, checked = [], 0


def same(a, b, where):
    global checked
    checked += 1
    if a != b:
        fails.append(f"{where}\n  JS : {a}\n  PY : {b}")


m02, m03, m04, m05, m06, m07, m08, m09 = (ref(n) for n in [
    "m02-affinity-metrics", "m03-greedy-pair-merge", "m04-size-constrained-agglomerative", "m05-label-propagation",
    "m06-spectral-bisection", "m07-kernighan-lin", "m08-fiduccia-mattheyses", "m09-rajaraman-wong"])

for i, g in enumerate(cases["m02"]):
    same([list(x) for x in J["m02"][i]["edge"]], [list(x) for x in m02.affinity_edge_weight(g["edges"])], f"m02 edge #{i}")
    same([list(x) for x in J["m02"][i]["shared"]], [list(x) for x in m02.affinity_shared_neighbors(g["nodes"], g["edges"])], f"m02 shared #{i}")

for i, x in enumerate(cases["m03"]):
    sizes = x["g"].get("sizes")
    try:
        r = m03.greedy_pair_merge(x["g"]["nodes"], x["g"]["edges"], x["k"], x["cap"], sizes)
    except ValueError:
        same(J["m03"][i], "invalid", f"m03 #{i}")
        continue
    same(J["m03"][i], {"parts": r["parts"], "traj": [e["cutsize"] for e in r["log"]], "reached": r["target_reached"], "stop": r["stop_reason"]}, f"m03 #{i}")
    r4 = m04.solve(x["g"], x["k"], x["cap"])
    same(J["m03"][i]["parts"], ["".join(p) for p in r4["clusters"]], f"m04 solve #{i}")

for i, x in enumerate(cases["m05"]):
    r = m05.solve(x["g"]["nodes"], [tuple(e) for e in x["g"]["edges"]], mode=x["mode"], tie=x["tie"], order=x["order"])
    same({k: J["m05"][i][k] for k in ("labels", "rounds", "status", "cut")}, {k: r[k] for k in ("labels", "rounds", "status", "cut")}, f"m05 #{i}")
    same(J["m05"][i]["votes"], [[e["node"], e["label"], e["votes"]] for e in r["events"]], f"m05 votes #{i}")

for i, g in enumerate(cases["m06"]):
    j = J["m06"][i]
    if j == "invalid":
        continue
    r = m06.spectral_bisection(g["nodes"], [tuple(e) for e in g["edges"]], (0.4, 0.6))
    checked += 1
    if max(abs(a - b) for a, b in zip(j["values"], r["eigenvalues"])) > 1e-8:
        fails.append(f"m06 eigenvalues #{i}")
    if j["connected"] and j["gap"] > 1e-6:  # λ2 simple: order and sweep are well defined
        same(j["sweep"], [c["cut"] for c in r["candidates"]], f"m06 sweep #{i}")
        same(j["cut"], r["cut"], f"m06 cut #{i}")

for i, x in enumerate(cases["m07"]):
    j = J["m07"][i]
    if j == "invalid":
        continue
    r = m07.kernighan_lin(x["g"]["nodes"], [tuple(e) for e in x["g"]["edges"]], x["init"])
    same(j, [{"swaps": [[s["a"], s["b"], s["gain"], s["cut_after"]] for s in p["swaps"]], "k": p["best_k"], "cut": p["accepted_cut"]} for p in r["passes"]], f"m07 #{i}")

for i, x in enumerate(cases["m08"]):
    j = J["m08"][i]
    if not m08.balance_ok(x["init"], x["maxDiff"]):
        same(j, "invalid", f"m08 invalid #{i}")
        continue
    r = m08.fm_refine(x["g"], x["init"], x["maxDiff"])
    same(j, [{"moves": [[m["node"], m["gain"], m["cut_after"]] for m in p["trial_moves"]], "k": p["best_prefix"], "cut": p["accepted_cut"]} for p in r["passes"]], f"m08 #{i}")

for i, d in enumerate(cases["m09"]):
    d2 = dict(d)
    d2["PO"] = [v for v in d["nodes"] if not any(u == v for u, _ in d["edges"])]
    d2["PI"] = [v for v in d["nodes"] if not any(w == v for _, w in d["edges"])]
    r = m09.rajaraman_wong(d2)
    j = J["m09"][i]
    same(j["labels"], r["labels"], f"m09 labels #{i}")
    same({k: sorted(v) for k, v in j["clusters"].items()}, {k: sorted(v) for k, v in r["clusters"].items()}, f"m09 clusters #{i}")
    same(j["instances"], len(r["instances"]), f"m09 instances #{i}")
    same(j["out"], r["output_delay"], f"m09 output #{i}")

if fails:
    print("\n".join(fails[:10]))
    print(f"FAIL: {len(fails)} of {checked} comparisons differ")
    sys.exit(1)
print(f"PASS: {checked} JS/Python comparisons across M02–M09 (step-level for M03, M05, M07, M08)")
