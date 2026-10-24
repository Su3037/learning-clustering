"""Module 05 · Label propagation — reference solution (Python 3.9+, standard library only).

Adapted from the author's own Lab05 standalone Python reference (Su3037/clustering-lab5-label-propagation,
src/label_propagation.py @ 7b4eca7, MIT); only the layout and returned fields were changed.

A node's name never changes; its label does. Each node adds up the edge weights of its neighbours per label
and takes the label with the largest total.
- async: write back at once, so later nodes in the same round see the new label;
- sync: the whole round reads an old snapshot, and everything is committed at the end of the round;
- ties: min takes the alphabetically smallest, max the largest, keep keeps the current label if it is tied.
Stopping: a full round with zero changes = stable; a label state seen before = cycle; hitting the cap = limit.
The round count includes the final "zero-change" confirmation round.
"""
import math


def build_adjacency(nodes, edges):
    adj = {n: [] for n in nodes}
    seen = set()
    for u, v, w in edges:
        key = tuple(sorted((u, v)))
        if u not in adj or v not in adj or u == v or key in seen:
            raise ValueError(f"invalid or duplicate edge {u}-{v}")
        if not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0:
            raise ValueError("edge weights must be finite and positive")
        adj[u].append((v, w))
        adj[v].append((u, w))
        seen.add(key)
    return adj


def count_votes(adj, labels, vertex):
    """Add up neighbour edge weights per label: {label: votes}."""
    votes = {}
    for neighbor, weight in adj[vertex]:
        votes[labels[neighbor]] = votes.get(labels[neighbor], 0) + weight
    return votes


def choose(votes, previous, tie="min"):
    if not votes:
        return previous
    top = max(votes.values())
    tied = sorted(k for k, v in votes.items() if abs(v - top) < 1e-12)
    if tie == "keep" and previous in tied:
        return previous
    return tied[-1] if tie == "max" else tied[0]


def solve(nodes, edges, mode="async", tie="min", order=None, max_iters=50):
    if not nodes or len(set(nodes)) != len(nodes):
        raise ValueError("nodes must be non-empty and unique")
    if mode not in ("async", "sync") or tie not in ("min", "max", "keep"):
        raise ValueError("unknown update mode or tie rule")
    seq = list(order) if order is not None else sorted(nodes)
    if len(seq) != len(nodes) or set(seq) != set(nodes):
        raise ValueError("the visiting order must contain every node exactly once")
    adj = build_adjacency(nodes, edges)
    labels = {n: n for n in nodes}
    seen = {tuple(labels[n] for n in nodes): 0}
    events, status, rounds = [], "limit", 0
    for rounds in range(1, max_iters + 1):
        snapshot, pending, changes = dict(labels), dict(labels), 0
        for vertex in seq:
            source = snapshot if mode == "sync" else labels
            votes = count_votes(adj, source, vertex)
            previous = source[vertex]
            winner = choose(votes, previous, tie)
            changes += winner != previous
            pending[vertex] = winner
            if mode == "async":
                labels[vertex] = winner
            events.append({"round": rounds, "node": vertex, "old": previous, "label": winner, "votes": votes})
        if mode == "sync":
            labels = pending
        signature = tuple(labels[n] for n in nodes)
        if changes == 0:
            status = "stable"
            break
        if signature in seen:
            status = "cycle"
            break
        seen[signature] = rounds
    cut = sum(w for u, v, w in edges if labels[u] != labels[v])
    return {"labels": labels, "rounds": rounds, "status": status, "cut": cut, "events": events}


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    r = solve(g["nodes"], g["edges"])
    print(r["labels"], r["rounds"], r["status"], "cut", r["cut"])
