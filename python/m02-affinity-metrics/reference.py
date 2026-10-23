"""Module 02 · 亲和度指标 —— 参考实现（Python 3.9+，仅标准库）。

三个评分模型，各自返回按 (分数降序, u, v) 排好的 [(u, v, score), ...]，其中 u < v。
评分只给节点对排序，不是最终分组，也不是距离或概率。
"""


def _norm_edges(edges):
    """把 [(u, v, w), ...] 规范为 {(min, max): w}。重复边或自环直接报错，而不是悄悄相加。"""
    out = {}
    for u, v, w in edges:
        if u == v:
            raise ValueError(f"不支持自环 {u}-{v}")
        key = (u, v) if u < v else (v, u)
        if key in out:
            raise ValueError(f"重复边 {key[0]}-{key[1]}")
        out[key] = w
    return out


def _rank(scores):
    return sorted(scores, key=lambda t: (-t[2], t[0], t[1]))


def affinity_edge_weight(edges):
    """edge(u,v) = w(u,v)：只有直接连线的节点对才有分数。"""
    return _rank([(u, v, w) for (u, v), w in _norm_edges(edges).items()])


def affinity_shared_neighbors(nodes, edges):
    """shared(u,v) = w(u,v) + Σ_x min(w(u,x), w(v,x))，x 为共同邻居。

    遍历所有无序节点对（包括没有直接连线的对），只列出分数 > 0 的对。
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
    """clique 模型：Σ_{net e ∋ u,v} w(e)/(|e|-1)。

    nets: [{"id":..., "pins":[...], "w":1}, ...]。同一 net 内重复的引脚只算一次；
    少于两个不同引脚的 net 忽略。
    """
    acc = {}
    known = set(nodes)
    for net in nets:
        pins = sorted(set(net["pins"]))
        if any(p not in known for p in pins):
            raise ValueError(f"net {net.get('id')} 引用了未知节点")
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
