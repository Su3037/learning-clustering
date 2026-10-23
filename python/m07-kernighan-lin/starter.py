"""Module 07 · Kernighan–Lin 改进 —— 练习起始代码（Python 3.9+，仅标准库）。

两侧节点数固定。一轮（pass）中反复选“未锁定的跨侧节点对”里收益最大的一对交换：
    g(a, b) = D(a) + D(b) − 2·w(a, b)，   D(v) = 外部边权 − 内部边权
收益 ≤ 0 也照样试探；交换后两点锁定、重算 D。轮末取累计收益最大的前缀（允许空前缀 0），
从本轮起点只应用这几步；最佳前缀为空就停止。平票按 (−收益, a, b) 的字典序。
"""


def _adj(nodes, edges):
    adj = {n: {} for n in nodes}
    for u, v, w in edges:
        adj[u][v] = adj[v][u] = w
    return adj


def cut(edges, side):
    return sum(w for u, v, w in edges if side[u] != side[v])


def d_values(adj, side):
    out = {}
    for v in adj:
        ext = sum(w for u, w in adj[v].items() if side[u] != side[v])
        inn = sum(w for u, w in adj[v].items() if side[u] == side[v])
        out[v] = ext - inn
    return out


def best_swap(adj, side, locked):
    """任务 1：在未锁定的 0 侧节点 a 与 1 侧节点 b 之间，找收益最大的一对。

    收益 g = D(a) + D(b) − 2·w(a,b)。为什么减 2w？a、b 之间那条边交换前是外部边（被算进两个 D），
    交换后两点仍分处两侧，这条边依然被切。返回 {"a","b","gain","Da","Db","w"}；没有候选时返回 None。
    平票：按 (−gain, a, b) 取最小。收益 ≤ 0 也要返回——那是试探，不是接受。
    """
    raise NotImplementedError("best_swap")


def best_prefix(gains):
    """任务 2：返回 (k, 累计收益)。只保留连续的前 k 步；k = 0（空前缀）是合法答案。"""
    raise NotImplementedError("best_prefix")


def kl_pass(nodes, edges, side):
    adj = _adj(nodes, edges)
    trial, locked, swaps = dict(side), set(), []
    while True:
        s = best_swap(adj, trial, locked)
        if s is None:
            break
        before = cut(edges, trial)
        trial[s["a"]], trial[s["b"]] = 1, 0
        locked |= {s["a"], s["b"]}
        s["cut_before"], s["cut_after"] = before, cut(edges, trial)
        swaps.append(s)
    k, g = best_prefix([s["gain"] for s in swaps])
    accepted = dict(side)
    for s in swaps[:k]:
        accepted[s["a"]], accepted[s["b"]] = 1, 0
    return {"swaps": swaps, "best_k": k, "best_gain": g, "accepted": accepted, "accepted_cut": cut(edges, accepted)}


def kernighan_lin(nodes, edges, initial, max_passes=10):
    side, passes = dict(initial), []
    for _ in range(max_passes):
        p = kl_pass(nodes, edges, side)
        passes.append(p)
        side = p["accepted"]
        if p["best_k"] == 0:
            return {"assignment": side, "cut": cut(edges, side), "passes": passes, "stop_reason": "no-positive-prefix"}
    return {"assignment": side, "cut": cut(edges, side), "passes": passes, "stop_reason": "limit"}


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    seed = {"A": 0, "B": 1, "C": 1, "D": 1, "E": 0}
    r = kernighan_lin(g["nodes"], [tuple(e) for e in g["edges"]], seed)
    for i, p in enumerate(r["passes"], 1):
        print(f"pass {i}: " + ", ".join(f"{s['a']}↔{s['b']} g={s['gain']} cut→{s['cut_after']}" for s in p["swaps"]) + f"；最佳前缀 {p['best_k']}，接受 cut {p['accepted_cut']}")
