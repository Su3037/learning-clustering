"""Slide figures for Module 04 (drawn with the slide kit, once per language).
Every state is read from site/data/m04-size-constrained-agglomerative/traces.json."""
import json
from pathlib import Path

from kit import X, table, code, tag, node, edge, hull, fit, INK, MUTED, GOLD, TEAL, RED, BLUE, PURPLE, MONO

T = json.loads((Path(__file__).resolve().parents[2] / "site/data/m04-size-constrained-agglomerative/traces.json").read_text())
G01P = {k: tuple(v) for k, v in T["g01"]["positions"].items()}
G01E = [tuple(e) for e in T["g01"]["edges"]]
TRAP_G, SUB_G = T["graphs"]["greedy_trap"], T["graphs"]["suboptimal"]
TRAP_SIZE = {n["id"]: n["size"] for n in TRAP_G["nodes"]}
ONES = {n: 1 for n in "ABCDE"}
HC = {"AB": TEAL, "ABC": TEAL, "AC": TEAL, "DE": BLUE, "CDE": BLUE, "BD": BLUE, "CD": GOLD}


def state(cv, pos, edges, clusters, sizes, cap, r=36, blocked=()):
    """Clusters as hulls labelled size/capacity; crossing wires dashed red; blocked nodes ringed red."""
    where = {m: c["label"] for c in clusters for m in c["members"]}
    mean_y = sum(p[1] for p in pos.values()) / len(pos)
    for c in clusters:
        if len(c["members"]) > 1:
            ys = [pos[m][1] for m in c["members"]]
            size = sum(sizes[m] for m in c["members"])
            hull(cv, [pos[m] for m in c["members"]], HC.get(c["label"], PURPLE), 58, 1.0, f"{c['label']} · {size}/{cap}", below=sum(ys) / len(ys) > mean_y)
    for u, v, w in edges:
        edge(cv, pos[u], pos[v], w, "inside" if where[u] == where[v] else "cut", 1.0, r)
    for n, p in pos.items():
        col = HC.get(where[n], PURPLE) if len(where[n]) > 1 else "#a9bdb8"
        node(cv, *p, n, col, r, 1.0, RED if n in blocked else None)
        if sizes[n] != 1:
            cv.text(p[0], p[1] + r + 34, f"s={sizes[n]}", 24, GOLD, "bold", "center")


def clusters_of(labels, sizes):
    return [{"label": l, "members": list(l), "size": sum(sizes[m] for m in l)} for l in labels]


def g01(cv, key, cap, box, title):
    run = T[key]["run"]
    last = run["events"][-1]
    blocked = sorted({m for c in last.get("candidates", []) if not c["legal"] for m in c["a"] + c["b"]}) if last["kind"] == "stopped" else ()
    state(cv, fit(G01P, box), G01E, last["after"], ONES, cap, r=32, blocked=blocked)
    r = run["result"]
    cx = (box[0] + box[2]) / 2
    cv.text(cx, box[1] - 70, title, 30, INK, "bold", "center")
    tag(cv, cx, box[3] + 130, f"{' | '.join(r['labels'])} · cut {r['cut']}", TEAL if r["targetReached"] else GOLD, 1.0, 26)


def report(cv, a):
    rows = [[X("报告项", "Report item"), X("容量 2，K = 2", "Capacity 2, K = 2")], ["count", "3"], ["capacityCompliant", X("是", "yes")],
            ["targetReached", X("否", "no")], ["stopReason", "capacity-blocked"]]
    table(cv, 980, 320, [420, 360], rows, 36, 88, {3: GOLD})


def fork(cv, a):
    g01(cv, "cap3", 3, (960, 330, 1290, 760), X("容量 3：达到 K", "Capacity 3: K reached"))
    g01(cv, "cap2", 2, (1440, 330, 1770, 760), X("容量 2：未达到 K", "Capacity 2: K not reached"))


def bound(cv, a):
    for i in range(5):
        node(cv, 1000 + i * 90, 360, "ABCDE"[i], "#a9bdb8", 32)
    cv.text(1180, 450, X("总大小 5", "total size 5"), 28, MUTED, "bold", "center")
    for j in range(3):
        x = 1520 + (j % 2) * 160
        y = 330 + (j // 2) * 110
        cv.rect(x - 64, y - 30, 128, 64, fill="#0a2126", stroke=RED if j == 2 else TEAL, width=2, r=20)
        cv.text(x, y + 10, X("容量 2", "cap 2"), 24, RED if j == 2 else TEAL, "bold", "center")
    cv.text(1360, 650, "⌈5 ÷ 2⌉ = 3 > K = 2", 52, GOLD, "bold", "center", family=MONO)  # the sans faces lack ⌈⌉
    cv.text(1360, 730, X("至少 3 个簇：K = 2 不可能", "at least 3 clusters: K = 2 is impossible"), 30, INK, "normal", "center")


def trap(cv, a):
    run = T["trap"]["run"]
    pos = fit({k: tuple(v) for k, v in TRAP_G["positions"].items()}, (960, 300, 1780, 520))
    state(cv, pos, [tuple(e) for e in TRAP_G["edges"]], run["events"][-1]["after"], TRAP_SIZE, 3, blocked=("A", "B"))
    tag(cv, 1370, 700, X(f"贪心：{' | '.join(run['result']['labels'])}，3 簇", f"Greedy: {' | '.join(run['result']['labels'])}, 3 clusters"), GOLD, 1.0, 26)
    best = T["trap"]["oracle"]["bestCutAtK"]
    grouping = " | ".join("".join(x) for x in best["clusters"])
    tag(cv, 1370, 800, X(f"穷举：{grouping}，2 簇，cut {best['cut']}", f"Exhaustive: {grouping}, 2 clusters, cut {best['cut']}"), TEAL, 1.0, 26)


def sub(cv, a):
    run, best = T["suboptimal"]["run"], T["suboptimal"]["oracle"]["bestCutAtK"]
    edges = [tuple(e) for e in SUB_G["edges"]]
    raw = {k: tuple(v) for k, v in SUB_G["positions"].items()}
    state(cv, fit(raw, (980, 340, 1300, 680)), edges, run["events"][-1]["after"], ONES, 2)
    state(cv, fit(raw, (1490, 340, 1810, 680)), edges, clusters_of(["".join(x) for x in best["clusters"]], ONES), ONES, 2)
    cv.text(1140, 250, X("贪心", "Greedy"), 30, INK, "bold", "center")
    cv.text(1650, 250, X("穷举最优", "Exhaustive optimum"), 30, INK, "bold", "center")
    tag(cv, 1140, 860, f"cut {run['result']['cut']}", RED, 1.0, 28)
    tag(cv, 1650, 860, f"cut {best['cut']}", TEAL, 1.0, 28)


def uneven(cv, a):
    u = T["uneven"]
    sizes = {n: 2 if n == "A" else 1 for n in "ABCDE"}
    state(cv, fit(G01P, (1000, 280, 1700, 760)), G01E, u["events"][-1]["after"], sizes, 3)
    tag(cv, 1350, 920, X(f"{' | '.join(u['result']['labels'])}，cut {u['result']['cut']}", f"{' | '.join(u['result']['labels'])}, cut {u['result']['cut']}"), GOLD, 1.0, 28)


CODE = [X("clusters ← 单点簇；s(v) > C 则输入不合法", "clusters ← singletons; s(v) > C: invalid input"),
        X("while 簇数 > K:", "while #clusters > K:"),
        X("    cands ← 亲和度 > 0 的簇对", "    cands ← pairs with affinity > 0"),
        X("    legal ← s(P) + s(Q) ≤ C 的候选", "    legal ← cands with s(P) + s(Q) ≤ C"),
        X("    if legal 为空: 停止（两种原因）", "    if legal is empty: stop (two reasons)"),
        X("    合并选择键最小的合法一对", "    merge the legal pair with the least key"),
        X("报告 count、合法、达到 K、停止原因", "report count, legal, K reached, stop reason"),
        X("诊断：下界 ceil(Σs / C) 与小图穷举", "diagnose: bound ceil(Σs / C), small search")]


def pseudo(cv, a):
    code(cv, 930, 300, CODE, (4, 5), 27, 64, w=900)


FIGURES = {"report": report, "fork": fork, "bound": bound, "trap": trap, "sub": sub, "uneven": uneven, "pseudo": pseudo}
