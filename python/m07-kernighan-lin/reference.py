"""Module 07 · Kernighan–Lin 改进 —— 参考实现（Python 3.9+，仅标准库）。

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
    D = d_values(adj, side)
    cands = []
    for a in sorted(v for v in adj if side[v] == 0 and v not in locked):
        for b in sorted(v for v in adj if side[v] == 1 and v not in locked):
            cands.append((-(D[a] + D[b] - 2 * adj[a].get(b, 0)), a, b))
    if not cands:
        return None
    g, a, b = min(cands)
    return {"a": a, "b": b, "gain": -g, "Da": D[a], "Db": D[b], "w": adj[a].get(b, 0)}


def best_prefix(gains):
    """gains 为每步收益；返回 (k, 累计收益)。k=0 表示空前缀。只在严格更大时更新。"""
    best_k, best, total = 0, 0, 0
    for i, g in enumerate(gains, 1):
        total += g
        if total > best:
            best_k, best = i, total
    return best_k, best


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
