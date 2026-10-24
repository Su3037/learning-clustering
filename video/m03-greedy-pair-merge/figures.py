"""Slide figures for Module 03 (drawn with the slide kit, once per language).
Every state is read from site/data/m03-greedy-pair-merge/traces.json."""
import json
from pathlib import Path

from kit import X, table, code, tag, node, edge, hull, fit, INK, MUTED, GOLD, TEAL, RED, BLUE, PURPLE, MONO

T = json.loads((Path(__file__).resolve().parents[2] / "site/data/m03-greedy-pair-merge/traces.json").read_text())
POS = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (220, 250, 920, 800))
EDGES = [tuple(e) for e in T["g01"]["edges"]]
RUN = T["runs"]["k2-capnone"]
CAP2 = T["runs"]["k2-cap2"]
MERGES = [e for e in RUN["events"] if e["kind"] == "merge"]
HC = {"AB": TEAL, "ABC": TEAL, "DE": BLUE}


def state_graph(cv, clusters, focus=(), alpha=1.0):
    where = {m: c["label"] for c in clusters for m in c["members"]}
    mean_y = sum(p[1] for p in POS.values()) / len(POS)
    for c in clusters:
        if len(c["members"]) > 1:
            ys = [POS[m][1] for m in c["members"]]
            hull(cv, [POS[m] for m in c["members"]], HC.get(c["label"], PURPLE), 66, alpha, X(f"{c['label']} · 大小 {c['size']}", f"{c['label']} · size {c['size']}"),
                 below=sum(ys) / len(ys) > mean_y)
    for u, v, w in EDGES:
        edge(cv, POS[u], POS[v], w, "inside" if where[u] == where[v] else "cut", alpha)
    for n, p in POS.items():
        node(cv, *p, n, HC.get(where[n], "#a9bdb8") if len(where[n]) > 1 else "#a9bdb8", 40, alpha, GOLD if n in focus else None)


def graph(cv, clusters, small=False, **kw):
    with cv.place(760, 40, 1.0) if not small else cv.place(780, 120, 0.8):
        state_graph(cv, clusters, **kw)


def start(cv, a):
    graph(cv, RUN["events"][0]["after"])
    tag(cv, 1350, 960, X("单点簇：cut = 18", "Singletons: cut = 18"), RED)


def step(cv, a):
    ev = MERGES[a.get("i", 0)]
    graph(cv, ev["after"], small=True, focus=[m for c in ev["after"] if c["label"] == ev["decision"]["merged"] for m in c["members"]])
    rows = [[X("候选", "Pair"), X("亲和度", "Affinity")]] + [[f"{c['a']}–{c['b']}", str(c["affinity"])] for c in ev["candidates"][:4]]
    table(cv, 1580, 300, [150, 120], rows, 28, 56, {1: GOLD})
    tag(cv, 1350, 960, f"cut {ev['metrics']['cutBefore']} → {ev['metrics']['cut']}", TEAL)


def trajectory(cv, a):
    rows = [[X("步", "Step"), X("合并", "Merge"), X("亲和度", "Affinity"), "cut"], ["0", "—", "—", "18"]] + \
           [[str(e["step"]), f"{e['decision']['a']} + {e['decision']['b']}", str(e["decision"]["affinity"]), str(e["metrics"]["cut"])] for e in MERGES]
    table(cv, 980, 300, [110, 300, 180, 140], rows, 36, 86, {4: TEAL})


def bug(cv, a):
    cv.text(960, 330, '[−5, "A", "B"]  →  "-5,A,B"', 36, INK, family=MONO)
    cv.text(960, 400, '[−1, "A", "C"]  →  "-1,A,C"', 36, INK, family=MONO)
    cv.text(960, 480, X("字符 1 < 5：亲和度 1 的 A–C 被当成更好", "Character 1 < 5: A–C, affinity 1, looks better"), 30, RED, "bold")
    rows = [[X("配置", "Setting"), X("原网页", "Original"), X("正确", "Correct")], ["K=2", "9", "3"], ["K=3", "16", "8"],
            [X("K=2 容量2", "K=2 cap 2"), "12", "8"], [X("K=2 容量3", "K=2 cap 3"), "16", "3"]]
    table(cv, 980, 590, [300, 180, 180], rows, 32, 66)


def capacity(cv, a):
    stop = [e for e in CAP2["events"] if e["kind"] == "stopped"][0]
    graph(cv, stop["after"])
    tag(cv, 1350, 960, X("容量 2：AB | C | DE，cut 8，未达到 K", "Capacity 2: AB | C | DE, cut 8, K not reached"), GOLD)


CODE = [X("clusters ← 每个节点一个单点簇", "clusters ← one singleton per node"),
        X("while 簇数 > K:", "while #clusters > K:"),
        X("    cands ← 亲和度 > 0 的簇对", "    cands ← pairs with affinity > 0"),
        X("    legal ← 合并后大小 ≤ C 的候选", "    legal ← cands with merged size ≤ C"),
        X("    if legal 为空: 停止（如实报告）", "    if legal is empty: stop (say so)"),
        X("    选 (−亲和度, P, Q) 最小的一对", "    pick the pair with the least (−aff, P, Q)"),
        X("    收缩 P ∪ Q：cut 下降该亲和度", "    contract P ∪ Q: cut drops by its affinity"),
        X("返回 簇、cut、是否达到 K、停止原因", "return clusters, cut, K reached, stop reason")]


def pseudo(cv, a):
    code(cv, 930, 300, CODE, (4, 5, 6), 27, 64, w=900)


FIGURES = {"start": start, "step": step, "trajectory": trajectory, "bug": bug, "capacity": capacity, "pseudo": pseudo}
