"""Module 03 · Greedy pair merge: reference implementation (Python 3.9+, standard library only).

Start from single-node clusters; at each step merge the legal cluster pair with the highest positive affinity.
Affinity = the total weight of every edge between the two clusters.
The selection key (-affinity, members of A, members of B) compares field by field: the number first, then names.
Stop when K is reached or no legal positive pair remains; never force a merge to reach K, never undo one.
capacity counts the sum of node sizes (every node has size 1 by default).
"""


def cutsize(parts, weights):
    where = {n: i for i, p in enumerate(parts) for n in p}
    return sum(w for (u, v), w in weights.items() if where[u] != where[v])


def _weights(edges):
    out = {}
    for u, v, w in edges:
        if u == v:
            raise ValueError("self-loops are not supported")
        key = (u, v) if u < v else (v, u)
        if key in out:
            raise ValueError(f"duplicate edge {key}")
        out[key] = w
    return out


def selection_key(c):
    """(-affinity, members of A as a tuple, members of B as a tuple): field by field, numbers as numbers."""
    return (-c["affinity"], c["a"], c["b"])


def candidates(parts, weights, capacity=None, sizes=None):
    """Every cluster pair with positive affinity, sorted by the selection key; each carries a legal flag."""
    sizes = sizes or {}
    where = {n: i for i, p in enumerate(parts) for n in p}
    acc = {}
    for (u, v), w in weights.items():
        i, j = where[u], where[v]
        if i == j:
            continue
        a, b = sorted((tuple(parts[i]), tuple(parts[j])))
        acc[(a, b)] = acc.get((a, b), 0) + w
    out = []
    for (a, b), aff in acc.items():
        size = sum(sizes.get(n, 1) for n in a + b)
        out.append({"a": a, "b": b, "affinity": aff, "size": size,
                    "legal": capacity is None or size <= capacity})
    out.sort(key=selection_key)
    return out


def greedy_pair_merge(nodes, edges, k=2, capacity=None, sizes=None):
    weights = _weights(edges)
    sizes = sizes or {}
    if capacity is not None:
        for n in nodes:
            if sizes.get(n, 1) > capacity:
                raise ValueError(f"node {n} is already over capacity")
    parts = sorted([[n] for n in nodes])
    log = [{"step": 0, "event": "singletons", "clusters": ["".join(p) for p in parts],
            "cutsize": cutsize(parts, weights)}]
    stop_reason = None
    while True:
        if len(parts) <= k:
            stop_reason = "target-reached"
            break
        cands = candidates(parts, weights, capacity, sizes)
        legal = [c for c in cands if c["legal"]]
        if not legal:
            stop_reason = "capacity-blocked" if cands else "no-positive-affinity"
            break
        best = legal[0]
        merged = sorted(best["a"] + best["b"])
        parts = sorted([p for p in parts if tuple(p) not in (best["a"], best["b"])] + [merged])
        log.append({"step": len(log), "event": "merge", "pair": "".join(best["a"]) + "-" + "".join(best["b"]),
                    "weight": best["affinity"], "clusters": ["".join(p) for p in parts],
                    "cutsize": cutsize(parts, weights)})
    return {"parts": ["".join(p) for p in parts], "cutsize": cutsize(parts, weights), "log": log,
            "target_reached": len(parts) <= k, "stop_reason": stop_reason}


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    for k, cap in [(2, None), (3, None), (2, 2), (2, 3)]:
        r = greedy_pair_merge(g["nodes"], g["edges"], k, cap)
        print(f"K={k} cap={cap}: {'|'.join(r['parts'])} cut={r['cutsize']} path={[e['cutsize'] for e in r['log']]} K reached={r['target_reached']} stop={r['stop_reason']}")
