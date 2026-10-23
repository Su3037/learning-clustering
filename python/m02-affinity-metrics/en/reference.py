"""Module 02 · Affinity metrics: reference solution (Python 3.9+, standard library only).

Three scoring models, each returning [(u, v, score), ...] sorted by (score descending, u, v), with u < v.
A score only ranks pairs: it is not a final grouping, nor a distance or a probability.
"""


def _norm_edges(edges):
    """Normalise [(u, v, w), ...] to {(min, max): w}. Duplicate edges or self-loops raise an error instead of being silently added."""
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
    return sorted(scores, key=lambda t: (-t[2], t[0], t[1]))


def affinity_edge_weight(edges):
    """edge(u,v) = w(u,v): only pairs that share a direct wire get a score."""
    return _rank([(u, v, w) for (u, v), w in _norm_edges(edges).items()])


def affinity_shared_neighbors(nodes, edges):
    """shared(u,v) = w(u,v) + Σ_x min(w(u,x), w(v,x)), x running over shared neighbours.

    Visit every unordered pair (including pairs with no direct wire) and list only pairs with score > 0.
    """
    w = _norm_edges(edges)
    adj = {n: {} for n in nodes}
    for (u, v), x in w.items():
        adj[u][v] = x
        adj[v][u] = x
    ordered = sorted(nodes)
    result = []
    for i, u in enumerate(ordered):
        for v in ordered[i + 1:]:
            score = adj[u].get(v, 0)
            for x, wu in adj[u].items():
                if x != v and x in adj[v]:
                    score += min(wu, adj[v][x])
            if score > 0:
                result.append((u, v, score))
    return _rank(result)


def affinity_pin_count(nodes, nets):
    """The clique model: Σ_{net e ∋ u,v} w(e)/(|e|-1).

    nets: [{"id":..., "pins":[...], "w":1}, ...]. A pin repeated within one net counts once;
    nets with fewer than two distinct pins are ignored.
    """
    acc = {}
    known = set(nodes)
    for net in nets:
        pins = sorted(set(net["pins"]))
        if any(p not in known for p in pins):
            raise ValueError(f"net {net.get('id')} refers to an unknown node")
        if len(pins) < 2:
            continue
        share = net.get("w", 1) / (len(pins) - 1)
        for i, u in enumerate(pins):
            for v in pins[i + 1:]:
                acc[(u, v)] = acc.get((u, v), 0) + share
    return _rank([(u, v, round(s, 9)) for (u, v), s in acc.items()])


if __name__ == "__main__":
    import json
    import sys
    from pathlib import Path

    here = Path(__file__).resolve().parent
    g = json.loads((here / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    print("edge   :", affinity_edge_weight(g["edges"]))
    print("shared :", affinity_shared_neighbors(g["nodes"], g["edges"]))
    sys.exit(0)
