"""Module 07 · Kernighan–Lin refinement: exercise starter (Python 3.9+, standard library only).

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
    """Task 1: among unlocked nodes a on side 0 and b on side 1, find the pair with the largest gain.

    Gain g = D(a) + D(b) − 2·w(a,b). Why subtract 2w? Before the swap the a–b edge is external (counted in both D values);
    after it the two nodes are still on opposite sides, so the edge is still cut. Return {"a","b","gain","Da","Db","w"};
    return None when there is no candidate. Ties: take the least (−gain, a, b). Return it even if the gain is ≤ 0:
    that is a trial, not an acceptance.
    """
    raise NotImplementedError("best_swap")


def best_prefix(gains):
    """Task 2: return (k, cumulative gain). Keep only the first k consecutive steps; k = 0 (the empty prefix) is a valid answer."""
    raise NotImplementedError("best_prefix")


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
