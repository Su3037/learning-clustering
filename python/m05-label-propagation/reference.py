"""Module 05 · 标签传播 —— 参考实现（Python 3.9+，仅标准库）。

改写自作者本人 Lab05 的独立 Python 参考（Su3037/clustering-lab5-label-propagation，
src/label_propagation.py @ 7b4eca7，MIT），只调整了排版与返回字段。

节点名字不变，标签会变。每个节点把“同一标签的邻居边权”加起来，取最大的标签。
- async：立即写回，本轮后面的节点马上看到新标签；
- sync：整轮读旧快照，轮末一起提交；
- 平票：min 取字典序最小、max 取最大、keep 若当前标签在并列中则保留。
停止状态：整轮零变化 = stable；出现过的标签状态再次出现 = cycle；到达上限 = limit。
轮数包含最后那一轮“零变化确认轮”。
"""
import math


def build_adjacency(nodes, edges):
    adj = {n: [] for n in nodes}
    seen = set()
    for u, v, w in edges:
        key = tuple(sorted((u, v)))
        if u not in adj or v not in adj or u == v or key in seen:
            raise ValueError(f"非法或重复的边 {u}-{v}")
        if not isinstance(w, (int, float)) or not math.isfinite(w) or w <= 0:
            raise ValueError("边权须为有限正数")
        adj[u].append((v, w))
        adj[v].append((u, w))
        seen.add(key)
    return adj


def count_votes(adj, labels, vertex):
    """按标签累加邻居边权：{标签: 票数}。"""
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
        raise ValueError("nodes 须非空且不重复")
    if mode not in ("async", "sync") or tie not in ("min", "max", "keep"):
        raise ValueError("未知的更新方式或平票规则")
    seq = list(order) if order is not None else sorted(nodes)
    if len(seq) != len(nodes) or set(seq) != set(nodes):
        raise ValueError("访问顺序须恰好包含每个节点一次")
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
