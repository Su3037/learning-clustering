"""Module 02 · 亲和度指标 —— 练习起始代码（Python 3.9+，仅标准库）。

补全三个函数。每个函数返回 [(u, v, score), ...]，要求 u < v，
并按 (分数降序, u, v) 排序。运行 `python3 check.py` 查看结果。
"""


def _norm_edges(edges):
    """已给出：把 [(u, v, w), ...] 规范为 {(min, max): w}，自环或重复边报错。"""
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
    """已给出：稳定排名规则。"""
    return sorted(scores, key=lambda t: (-t[2], t[0], t[1]))


def affinity_edge_weight(edges):
    """任务 1：edge(u,v) = w(u,v)。"""
    raise NotImplementedError("affinity_edge_weight")


def affinity_shared_neighbors(nodes, edges):
    """任务 2：shared(u,v) = w(u,v) + Σ_x min(w(u,x), w(v,x))。

    注意：要检查所有无序节点对，没有直接连线的对也可能有正分。只返回分数 > 0 的对。
    """
    raise NotImplementedError("affinity_shared_neighbors")


def affinity_pin_count(nodes, nets):
    """任务 3：clique 模型 Σ w(e)/(|e|-1)。同一 net 内重复引脚只算一次，少于 2 个引脚的 net 忽略。"""
    raise NotImplementedError("affinity_pin_count")
