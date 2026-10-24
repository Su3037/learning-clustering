"""Module 07 · Kernighan–Lin refinement: reference implementation (Python 3.9+, standard library only).

The node count on each side is fixed. One pass repeatedly swaps the unlocked cross pair with the largest gain:
    g(a, b) = D(a) + D(b) − 2·w(a, b),   D(v) = external weight − internal weight
Gains ≤ 0 are tried as well; after a swap both nodes lock and D is recomputed. At the end of the pass keep the prefix
with the largest cumulative gain (the empty prefix, 0, is allowed) and apply only those steps from the pass start;
stop when the best prefix is empty. Ties go by the lexicographic order of (−gain, a, b).
"""


def _adj(nodes, edges):
    adj = {n: {} for n in nodes}
    for u, v, w in edges:
        adj[u][v] = adj[v][u] = w
    return adj


def cut(edges, side):
    return sum(w for u, v, w in edges if side[u] != side[v])


def d_values(adj, side):
    out = {}
    for v in adj:
        ext = sum(w for u, w in adj[v].items() if side[u] != side[v])
        inn = sum(w for u, w in adj[v].items() if side[u] == side[v])
        out[v] = ext - inn
    return out


def best_swap(adj, side, locked):
    D = d_values(adj, side)
    cands = []
    for a in sorted(v for v in adj if side[v] == 0 and v not in locked):
        for b in sorted(v for v in adj if side[v] == 1 and v not in locked):
            cands.append((-(D[a] + D[b] - 2 * adj[a].get(b, 0)), a, b))
    if not cands:
        return None
    g, a, b = min(cands)
    return {"a": a, "b": b, "gain": -g, "Da": D[a], "Db": D[b], "w": adj[a].get(b, 0)}


def best_prefix(gains):
    """gains are the per-step gains; return (k, cumulative gain). k = 0 means the empty prefix. Update only when strictly larger."""
    best_k, best, total = 0, 0, 0
    for i, g in enumerate(gains, 1):
        total += g
        if total > best:
            best_k, best = i, total
    return best_k, best


def kl_pass(nodes, edges, side):
    adj = _adj(nodes, edges)
    trial, locked, swaps = dict(side), set(), []
    while True:
        s = best_swap(adj, trial, locked)
        if s is None:
            break
        before = cut(edges, trial)
        trial[s["a"]], trial[s["b"]] = 1, 0
        locked |= {s["a"], s["b"]}
        s["cut_before"], s["cut_after"] = before, cut(edges, trial)
        swaps.append(s)
    k, g = best_prefix([s["gain"] for s in swaps])
    accepted = dict(side)
    for s in swaps[:k]:
        accepted[s["a"]], accepted[s["b"]] = 1, 0
    return {"swaps": swaps, "best_k": k, "best_gain": g, "accepted": accepted, "accepted_cut": cut(edges, accepted)}


def kernighan_lin(nodes, edges, initial, max_passes=10):
    side, passes = dict(initial), []
    for _ in range(max_passes):
        p = kl_pass(nodes, edges, side)
        passes.append(p)
        side = p["accepted"]
        if p["best_k"] == 0:
            return {"assignment": side, "cut": cut(edges, side), "passes": passes, "stop_reason": "no-positive-prefix"}
    return {"assignment": side, "cut": cut(edges, side), "passes": passes, "stop_reason": "limit"}


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    seed = {"A": 0, "B": 1, "C": 1, "D": 1, "E": 0}
    r = kernighan_lin(g["nodes"], [tuple(e) for e in g["edges"]], seed)
    for i, p in enumerate(r["passes"], 1):
        print(f"pass {i}: " + ", ".join(f"{s['a']}↔{s['b']} g={s['gain']} cut→{s['cut_after']}" for s in p["swaps"]) + f"; best prefix {p['best_k']}, accepted cut {p['accepted_cut']}")
