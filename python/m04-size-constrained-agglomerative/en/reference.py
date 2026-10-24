"""Module 04 · Size-constrained agglomerative clustering: reference implementation (Python 3.9+, standard library only).

Filter for legality first (merged size ≤ capacity), then choose among the legal candidates by (-affinity, members, members).
Report four things separately: the actual number of clusters, whether the capacity holds, whether the target K is reached, and why it stopped.
classify() uses the exhaustive oracle to tell apart: provably impossible / greedy stuck / legal but not optimal.
"""
import math


def _weights(edges):
    out = {}
    for u, v, w in edges:
        key = (u, v) if u < v else (v, u)
        if u == v or key in out:
            raise ValueError("self-loops and duplicate edges are not supported")
        out[key] = w
    return out


def cutsize(parts, weights):
    where = {n: i for i, p in enumerate(parts) for n in p}
    return sum(w for (u, v), w in weights.items() if where[u] != where[v])


def solve(graph, k, capacity):
    nodes, sizes = graph["nodes"], graph.get("sizes", {})
    size = {n: sizes.get(n, 1) for n in nodes}
    weights = _weights(graph["edges"])
    over = [n for n in nodes if capacity is not None and size[n] > capacity]
    if over:
        return {"clusters": [[n] for n in sorted(nodes)], "cutsize": cutsize([[n] for n in nodes], weights),
                "target_reached": False, "capacity_compliant": False,
                "stop_reason": "invalid-input", "steps": [], "detail": f"{over} alone already exceed the capacity"}
    parts = sorted([[n] for n in nodes])
    steps = []
    while True:
        if len(parts) <= k:
            stop = "target-reached"
            break
        where = {n: i for i, p in enumerate(parts) for n in p}
        acc = {}
        for (u, v), w in weights.items():
            i, j = where[u], where[v]
            if i != j:
                a, b = sorted((tuple(parts[i]), tuple(parts[j])))
                acc[(a, b)] = acc.get((a, b), 0) + w
        cands = sorted(acc.items(), key=lambda t: (-t[1], t[0][0], t[0][1]))
        legal = [(ab, aff) for ab, aff in cands if capacity is None or sum(size[n] for n in ab[0] + ab[1]) <= capacity]
        if not legal:
            stop = "capacity-blocked" if cands else "no-positive-affinity"
            break
        (a, b), aff = legal[0]
        blocked = ["".join(x) + "+" + "".join(y) for (x, y), af in cands if (-af, x, y) < (-aff, a, b)]
        parts = sorted([p for p in parts if tuple(p) not in (a, b)] + [sorted(a + b)])
        steps.append({"merge": ("".join(a), "".join(b)), "affinity": aff,
                      "blocked_before": blocked,
                      "cutsize": cutsize(parts, weights)})
    out = {"clusters": parts, "cutsize": cutsize(parts, weights), "steps": steps}
    out.update(report(parts, k, capacity, size, stop))
    return out


def report(parts, k, capacity, size, stop):
    """Report the number of clusters, capacity legality, reaching K and the stop reason separately."""
    return {"count": len(parts),
            "capacity_compliant": capacity is None or all(sum(size[n] for n in p) <= capacity for p in parts),
            "target_reached": len(parts) <= k,
            "stop_reason": stop}


def oracle(graph, k, capacity):
    """Enumerate every set partition (only for teaching graphs of at most 10 nodes)."""
    nodes, sizes = graph["nodes"], graph.get("sizes", {})
    size = {n: sizes.get(n, 1) for n in nodes}
    weights = _weights(graph["edges"])
    best, min_parts = None, None

    def rec(i, groups):
        nonlocal best, min_parts
        if i == len(nodes):
            if min_parts is None or len(groups) < min_parts:
                min_parts = len(groups)
            if len(groups) == k:
                c = cutsize(groups, weights)
                if best is None or c < best[0]:
                    best = (c, [sorted(g) for g in groups])
            return
        n = nodes[i]
        for g in groups:
            if capacity is None or sum(size[x] for x in g) + size[n] <= capacity:
                g.append(n)
                rec(i + 1, groups)
                g.pop()
        if capacity is None or size[n] <= capacity:
            groups.append([n])
            rec(i + 1, groups)
            groups.pop()

    rec(0, [])
    total = sum(size.values())
    return {"lower_bound": math.ceil(total / capacity) if capacity else 1,
            "min_feasible_clusters": min_parts, "best_cut_at_k": best}


def classify(graph, k, capacity):
    """Return 'infeasible-by-bound' / 'infeasible-by-search' / 'greedy-stuck' /
    'feasible-suboptimal' / 'reached-and-optimal-here'。"""
    r, o = solve(graph, k, capacity), oracle(graph, k, capacity)
    if not r["target_reached"]:
        if o["lower_bound"] > k:
            return "infeasible-by-bound"
        return "greedy-stuck" if o["best_cut_at_k"] else "infeasible-by-search"
    if o["best_cut_at_k"] and o["best_cut_at_k"][0] < r["cutsize"]:
        return "feasible-suboptimal"
    return "reached-and-optimal-here"


if __name__ == "__main__":
    import json
    from pathlib import Path
    here = Path(__file__).resolve().parent / "fixtures"
    cases = [("five_node.json", 2, 2), ("five_node.json", 2, 3), ("five_node.json", 3, 2),
             ("greedy_trap.json", 2, 3), ("suboptimal.json", 2, 2)]
    for name, k, cap in cases:
        g = json.loads((here / name).read_text(encoding="utf-8"))
        r = solve(g, k, cap)
        print(f"{name} K={k} C={cap}: {['' .join(p) for p in r['clusters']]} cut={r['cutsize']} "
              f"legal={r['capacity_compliant']} K reached={r['target_reached']} stop={r['stop_reason']} → {classify(g, k, cap)}")
