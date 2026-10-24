"""Module 02 · Affinity metrics: starter code (Python 3.9+, standard library only).

Complete the three functions. Each returns [(u, v, score), ...] with u < v,
sorted by (score descending, u, v). Run `python3 check.py --lang en` to see the results.
"""


def _norm_edges(edges):
    """Provided: normalise [(u, v, w), ...] to {(min, max): w}; self-loops and duplicate edges raise an error."""
    out = {}
    for u, v, w in edges:
        if u == v:
            raise ValueError(f"self-loop {u}-{v} is not supported")
        key = (u, v) if u < v else (v, u)
        if key in out:
            raise ValueError(f"duplicate edge {key[0]}-{key[1]}")
        out[key] = w
    return out


def _rank(scores):
    """Provided: the stable ranking rule."""
    return sorted(scores, key=lambda t: (-t[2], t[0], t[1]))


def affinity_edge_weight(edges):
    """Task 1: edge(u,v) = w(u,v)."""
    raise NotImplementedError("affinity_edge_weight")


def affinity_shared_neighbors(nodes, edges):
    """Task 2: shared(u,v) = w(u,v) + Σ_x min(w(u,x), w(v,x)).

    Note: check every unordered pair; a pair with no direct wire can still score. Return only pairs with score > 0.
    """
    raise NotImplementedError("affinity_shared_neighbors")


def affinity_pin_count(nodes, nets):
    """Task 3: the clique model Σ w(e)/(|e|-1). A pin repeated within one net counts once; nets with fewer than 2 pins are ignored."""
    raise NotImplementedError("affinity_pin_count")
