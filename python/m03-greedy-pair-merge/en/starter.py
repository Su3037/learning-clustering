"""Module 03 · Greedy pair merge: starter code (Python 3.9+, standard library only).

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
    """Task 1: return candidate c's selection key, so that min(...) picks the pair to merge.

    c = {"a": ("A","B"), "b": ("C",), "affinity": 5, "size": 3, "legal": True}
    Rule: higher affinity first; on a tie, compare a's members, then b's members.
    Hint: Python tuples compare field by field, and numbers compare as numbers. Never turn the whole key into a
    string: the original page's JS went wrong exactly because "-10,…" and "-2,…" compared as strings.
    """
    raise NotImplementedError("selection_key")


def candidates(parts, weights, capacity=None, sizes=None):
    """Given: every cluster pair with positive affinity, each with a legal flag (unsorted)."""
    sizes = sizes or {}
    where = {n: i for i, p in enumerate(parts) for n in p}
    acc = {}
    for (u, v), w in weights.items():
        i, j = where[u], where[v]
        if i == j:
            continue
        a, b = sorted((tuple(parts[i]), tuple(parts[j])))
        acc[(a, b)] = acc.get((a, b), 0) + w
    return [{"a": a, "b": b, "affinity": aff, "size": sum(sizes.get(n, 1) for n in a + b),
             "legal": capacity is None or sum(sizes.get(n, 1) for n in a + b) <= capacity}
            for (a, b), aff in acc.items()]


def greedy_pair_merge(nodes, edges, k=2, capacity=None, sizes=None):
    """Task 2: write the main loop.

    Return {"parts": ["ABC","DE"], "cutsize": 3, "log": [...], "target_reached": True, "stop_reason": ...}
    log[0] is the singletons; every merge then appends {"step","event":"merge","pair","weight","clusters","cutsize"}.
    stop_reason is "target-reached", "capacity-blocked" (positive pairs remain but all are over capacity)
    or "no-positive-affinity".
    """
    weights = _weights(edges)
    parts = sorted([[n] for n in nodes])
    log = [{"step": 0, "event": "singletons", "clusters": ["".join(p) for p in parts],
            "cutsize": cutsize(parts, weights)}]
    raise NotImplementedError("greedy_pair_merge main loop")
