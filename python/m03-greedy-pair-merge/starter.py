"""Module 03 · 贪心成对合并 —— 练习起始代码（Python 3.9+，仅标准库）。

从单点簇开始，每一步合并“正亲和度最大的合法簇对”。亲和度 = 两簇之间所有边权之和。
选择键 (-affinity, 簇A成员, 簇B成员) 逐字段比较：先比数值，再比成员名字典序。
达到 K、或者没有合法的正亲和度对时停止；绝不为凑 K 强行合并，也不撤销已做的合并。
capacity 按节点大小之和（默认每个节点大小 1）。
"""


def cutsize(parts, weights):
    where = {n: i for i, p in enumerate(parts) for n in p}
    return sum(w for (u, v), w in weights.items() if where[u] != where[v])


def _weights(edges):
    out = {}
    for u, v, w in edges:
        if u == v:
            raise ValueError("不支持自环")
        key = (u, v) if u < v else (v, u)
        if key in out:
            raise ValueError(f"重复边 {key}")
        out[key] = w
    return out


def selection_key(c):
    """任务 1：返回候选 c 的选择键，使 min(...) 选出应合并的那一对。

    c = {"a": ("A","B"), "b": ("C",), "affinity": 5, "size": 3, "legal": True}
    规则：亲和度大者优先；并列时比较 a 的成员，再比较 b 的成员。
    提示：Python 元组逐字段比较，数字按数值比。不要把整个键转成字符串比较——
    原网页的 JS 正是因为 "-10,…" 与 "-2,…" 按字符串比较而选错。
    """
    raise NotImplementedError("selection_key")


def candidates(parts, weights, capacity=None, sizes=None):
    """已给出：所有正亲和度簇对，每项含 legal 标记（未排序）。"""
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
    """任务 2：完成主循环。

    返回 {"parts": ["ABC","DE"], "cutsize": 3, "log": [...], "target_reached": True, "stop_reason": ...}
    log 第 0 项为单点簇，之后每次合并追加 {"step","event":"merge","pair","weight","clusters","cutsize"}。
    stop_reason 取 "target-reached"、"capacity-blocked"（有正亲和度对但都超容量）或 "no-positive-affinity"。
    """
    weights = _weights(edges)
    parts = sorted([[n] for n in nodes])
    log = [{"step": 0, "event": "singletons", "clusters": ["".join(p) for p in parts],
            "cutsize": cutsize(parts, weights)}]
    raise NotImplementedError("greedy_pair_merge 主循环")
