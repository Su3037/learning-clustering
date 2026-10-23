"""Module 08 · Fiduccia–Mattheyses 改进 —— 参考实现（Python 3.9+，仅标准库）。

基础轨道：带权二端图，每条边当作 2 引脚 net。同一份代码也接受多引脚 net（拓展）。
把 v 从 F 侧移到 T 侧的收益：
    + w(e)  若 e 在 F 侧只剩 v 一个引脚（FS：移动后 e 不再被切）
    − w(e)  若 e 在 T 侧没有引脚         （TE：移动后 e 开始被切）
平衡：两侧非空且 |n0 − n1| ≤ max_diff（按节点个数，不是面积）。
每轮单点移动、锁定；只在合法候选里选收益最大者（平票按名字），负收益也照走；
轮末保留累计收益最大的前缀（允许空前缀）。这里每步重新扫描候选，不是论文的 O(P) 桶实现。
"""


def to_nets(graph):
    nets = [{"id": "".join(sorted((u, v))), "pins": sorted((u, v)), "w": w} for u, v, w in graph.get("edges", [])]
    nets += [{"id": n.get("id", f"n{i}"), "pins": sorted(set(n["pins"])), "w": n.get("w", 1)} for i, n in enumerate(graph.get("nets", []))]
    return [n for n in nets if len(n["pins"]) >= 2]


def net_cut(nets, side):
    return sum(n["w"] for n in nets if len({side[p] for p in n["pins"]}) > 1)


def balance_ok(side, max_diff):
    c0 = sum(1 for s in side.values() if s == 0)
    c1 = len(side) - c0
    return c0 > 0 and c1 > 0 and abs(c0 - c1) <= max_diff


def gain(nets, side, v):
    """返回 (gain, FS 列表, TE 列表)。"""
    F, T = side[v], 1 - side[v]
    g, fs, te = 0, [], []
    for n in nets:
        if v not in n["pins"]:
            continue
        on_f = sum(1 for p in n["pins"] if side[p] == F)
        on_t = len(n["pins"]) - on_f
        if on_f == 1:
            g += n["w"]
            fs.append(n["id"])
        if on_t == 0:
            g -= n["w"]
            te.append(n["id"])
    return g, fs, te


def legal_moves(side, locked, max_diff):
    return [v for v in sorted(side) if v not in locked and balance_ok({**side, v: 1 - side[v]}, max_diff)]


def best_prefix(gains):
    best_k, best, total = 0, 0, 0
    for i, g in enumerate(gains, 1):
        total += g
        if total > best:
            best_k, best = i, total
    return best_k, best


def fm_pass(graph, initial, max_diff=1):
    nets = to_nets(graph)
    side, locked, moves = dict(initial), set(), []
    while True:
        legal = legal_moves(side, locked, max_diff)
        if not legal:
            break
        scored = sorted(legal, key=lambda v: (-gain(nets, side, v)[0], v))
        v = scored[0]
        g, fs, te = gain(nets, side, v)
        before = net_cut(nets, side)
        side[v] = 1 - side[v]
        locked.add(v)
        moves.append({"node": v, "gain": g, "fs": fs, "te": te, "cut_before": before, "cut_after": net_cut(nets, side)})
    k, total = best_prefix([m["gain"] for m in moves])
    accepted = dict(initial)
    for m in moves[:k]:
        accepted[m["node"]] = 1 - accepted[m["node"]]
    return {"trial_moves": moves, "best_prefix": k, "best_gain": total, "accepted": accepted, "accepted_cut": net_cut(nets, accepted)}


def fm_refine(graph, initial, max_diff=1, max_passes=10):
    side, passes = dict(initial), []
    for _ in range(max_passes):
        p = fm_pass(graph, side, max_diff)
        passes.append(p)
        side = p["accepted"]
        if p["best_prefix"] == 0:
            return {"assignment": side, "cut": net_cut(to_nets(graph), side), "passes": passes, "stop_reason": "no-positive-prefix"}
    return {"assignment": side, "cut": net_cut(to_nets(graph), side), "passes": passes, "stop_reason": "limit"}


if __name__ == "__main__":
    import json
    from pathlib import Path
    g = json.loads((Path(__file__).resolve().parent / "fixtures" / "five_node.json").read_text(encoding="utf-8"))
    seed = {"A": 0, "B": 1, "C": 1, "D": 1, "E": 0}
    r = fm_refine(g, seed, 1)
    for i, p in enumerate(r["passes"], 1):
        print(f"pass {i}: " + ", ".join(f"{m['node']}({m['gain']:+d})→{m['cut_after']}" for m in p["trial_moves"]) + f"；k*={p['best_prefix']}，接受 cut {p['accepted_cut']}")
