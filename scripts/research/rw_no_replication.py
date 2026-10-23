#!/usr/bin/env python3
"""Exhaustive search over NON-replicating clusterings (set partitions, each block ≤ capacity) of the
candidate DAG, minimising the maximum PI→PO delay under the same model (δ = 1, intra 0, inter D).
Used only to contrast with the replicating RW result; writes site/data/m09-rajaraman-wong/no-replication.json."""
import json, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
dag = json.loads((ROOT / "python/m09-rajaraman-wong/fixtures/candidate_dag.json").read_text())
nodes, edges, cap, D = dag["nodes"], [tuple(e) for e in dag["edges"]], dag["capacity"], dag["D"]
pred = {v: [u for u, w in edges if w == v] for v in nodes}
order = nodes[:]  # already topological
best = [10 ** 9, None]
count = 0
t0 = time.time()
assign = {}
arr = {}
sizes = []


def rec(i):
    global count
    if i == len(order):
        count += 1
        m = max(arr[p] for p in dag["PO"])
        if m < best[0]:
            best[0], best[1] = m, dict(assign)
        return
    v = order[i]
    for c in range(len(sizes) + 1):
        if c < len(sizes) and sizes[c] >= cap:
            continue
        t = 1 + max([arr[u] + (0 if assign[u] == c else D) for u in pred[v]], default=0)
        if t >= best[0]:
            continue  # arrival times only grow along paths: prune
        assign[v] = c; arr[v] = t
        if c == len(sizes):
            sizes.append(1)
        else:
            sizes[c] += 1
        rec(i + 1)
        if sizes[c] == 1 and c == len(sizes) - 1:
            sizes.pop()
        else:
            sizes[c] -= 1
        del assign[v]; del arr[v]


rec(0)
clusters = {}
for v, c in best[1].items():
    clusters.setdefault(c, []).append(v)
out = {"status": "computed by exhaustive search with pruning (scripts/research/rw_no_replication.py)", "model": "same DAG, delta=1, intra 0, inter D=3, capacity 4, NO replication",
       "bestMaxDelay": best[0], "example": sorted(clusters.values()), "leavesVisited": count, "seconds": round(time.time() - t0, 2)}
p = ROOT / "site/data/m09-rajaraman-wong/no-replication.json"
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(out)
