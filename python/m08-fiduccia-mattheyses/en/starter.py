"""Module 08 · Fiduccia–Mattheyses refinement: exercise starter (Python 3.9+, standard library only).

Base track: a weighted graph of 2-pin edges, each edge treated as a 2-pin net. The same code accepts multi-pin nets (extension).
The gain of moving v from side F to side T:
    + w(e)  if v is e's only pin on F   (FS: after the move e is no longer cut)
    − w(e)  if e has no pin on T        (TE: after the move e becomes cut)
Balance: both sides nonempty and |n0 − n1| ≤ max_diff (counting nodes, not area).
Each pass moves one node at a time and locks it; only the legal candidate with the largest gain is chosen (ties by name),
and negative gains are taken too; at the end of the pass keep the prefix with the largest cumulative gain (the empty
prefix is allowed). Candidates are rescanned at every step here: this is not the paper's O(P) bucket implementation.
"""


def to_nets(graph):
    nets = [{"id": "".join(sorted((u, v))), "pins": sorted((u, v)), "w": w} for u, v, w in graph.get("edges", [])]
    nets += [{"id": n.get("id", f"n{i}"), "pins": sorted(set(n["pins"])), "w": n.get("w", 1)} for i, n in enumerate(graph.get("nets", []))]
    return [n for n in nets if len(n["pins"]) >= 2]


def net_cut(nets, side):
    return sum(n["w"] for n in nets if len({side[p] for p in n["pins"]}) > 1)


def balance_ok(side, max_diff):
    c0 = sum(1 for s in side.values() if s == 0)
    c1 = len(side) - c0
    return c0 > 0 and c1 > 0 and abs(c0 - c1) <= max_diff


def gain(nets, side, v):
    """Task 1: return (gain, FS list, TE list).

    For every net that contains v: if v is its only pin on side F → FS, +w; if it has no pin on side T → TE, −w.
    On the five-node seed AE|BCD, D has FS = [DE] (5), TE = [CD] (2), gain = 3.
    """
    raise NotImplementedError("gain")


def legal_moves(side, locked, max_diff):
    """Task 2: the nodes that are unlocked and still satisfy balance_ok after moving (sorted by name).

    On the seed AE|BCD with max_diff=1, A's gain is 6, but moving A out of side 0 leaves 1 node there and breaks the balance: A is not legal.
    """
    raise NotImplementedError("legal_moves")


def best_prefix(gains):
    best_k, best, total = 0, 0, 0
    for i, g in enumerate(gains, 1):
        total += g
        if total > best:
            best_k, best = i, total
    return best_k, best


def fm_pass(graph, initial, max_diff=1):
    nets = to_nets(graph)
    side, locked, moves = dict(initial), set(), []
    while True:
        legal = legal_moves(side, locked, max_diff)
        if not legal:
            break
        scored = sorted(legal, key=lambda v: (-gain(nets, side, v)[0], v))
        v = scored[0]
        g, fs, te = gain(nets, side, v)
        before = net_cut(nets, side)
        side[v] = 1 - side[v]
        locked.add(v)
        moves.append({"node": v, "gain": g, "fs": fs, "te": te, "cut_before": before, "cut_after": net_cut(nets, side)})
    k, total = best_prefix([m["gain"] for m in moves])
    accepted = dict(initial)
    for m in moves[:k]:
        accepted[m["node"]] = 1 - accepted[m["node"]]
    return {"trial_moves": moves, "best_prefix": k, "best_gain": total, "accepted": accepted, "accepted_cut": net_cut(nets, accepted)}


def fm_refine(graph, initial, max_diff=1, max_passes=10):
    side, passes = dict(initial), []
    for _ in range(max_passes):
        p = fm_pass(graph, side, max_diff)
        passes.append(p)
        side = p["accepted"]
        if p["best_prefix"] == 0:
            return {"assignment": side, "cut": net_cut(to_nets(graph), side), "passes": passes, "stop_reason": "no-positive-prefix"}
    return {"assignment": side, "cut": net_cut(to_nets(graph), side), "passes": passes, "stop_reason": "limit"}


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    seed = {"A": 0, "B": 1, "C": 1, "D": 1, "E": 0}
    r = fm_refine(g, seed, 1)
    for i, p in enumerate(r["passes"], 1):
        print(f"pass {i}: " + ", ".join(f"{m['node']}({m['gain']:+d})→{m['cut_after']}" for m in p["trial_moves"]) + f"; k*={p['best_prefix']}, accepted cut {p['accepted_cut']}")
