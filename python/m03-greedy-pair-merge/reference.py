"""Module 03 · 贪心成对合并 —— 参考实现（Python 3.9+，仅标准库）。

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
    """(-亲和度, 簇A成员元组, 簇B成员元组)：逐字段比较，数字按数值。"""
    return (-c["affinity"], c["a"], c["b"])


def candidates(parts, weights, capacity=None, sizes=None):
    """所有正亲和度簇对，按选择键排序；每项含 legal 标记。"""
    sizes = sizes or {}
    where = {n: i for i, p in enumerate(parts) for n in p}
    acc = {}
    for (u, v), w in weights.items():
        i, j = where[u], where[v]
        if i == j:
            continue
        a, b = sorted((tuple(parts[i]), tuple(parts[j])))
        acc[(a, b)] = acc.get((a, b), 0) + w
    out = []
    for (a, b), aff in acc.items():
        size = sum(sizes.get(n, 1) for n in a + b)
        out.append({"a": a, "b": b, "affinity": aff, "size": size,
                    "legal": capacity is None or size <= capacity})
    out.sort(key=selection_key)
    return out


def greedy_pair_merge(nodes, edges, k=2, capacity=None, sizes=None):
    weights = _weights(edges)
    sizes = sizes or {}
    if capacity is not None:
        for n in nodes:
            if sizes.get(n, 1) > capacity:
                raise ValueError(f"节点 {n} 已超过容量")
    parts = sorted([[n] for n in nodes])
    log = [{"step": 0, "event": "singletons", "clusters": ["".join(p) for p in parts],
            "cutsize": cutsize(parts, weights)}]
    stop_reason = None
    while True:
        if len(parts) <= k:
            stop_reason = "target-reached"
            break
        cands = candidates(parts, weights, capacity, sizes)
        legal = [c for c in cands if c["legal"]]
        if not legal:
            stop_reason = "capacity-blocked" if cands else "no-positive-affinity"
            break
        best = legal[0]
        merged = sorted(best["a"] + best["b"])
        parts = sorted([p for p in parts if tuple(p) not in (best["a"], best["b"])] + [merged])
        log.append({"step": len(log), "event": "merge", "pair": "".join(best["a"]) + "-" + "".join(best["b"]),
                    "weight": best["affinity"], "clusters": ["".join(p) for p in parts],
                    "cutsize": cutsize(parts, weights)})
    return {"parts": ["".join(p) for p in parts], "cutsize": cutsize(parts, weights), "log": log,
            "target_reached": len(parts) <= k, "stop_reason": stop_reason}


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    for k, cap in [(2, None), (3, None), (2, 2), (2, 3)]:
        r = greedy_pair_merge(g["nodes"], g["edges"], k, cap)
        print(f"K={k} cap={cap}: {'|'.join(r['parts'])} cut={r['cutsize']} 轨迹={[e['cutsize'] for e in r['log']]} 达到K={r['target_reached']} 停止={r['stop_reason']}")
