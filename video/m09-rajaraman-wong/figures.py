"""Slide figures for Module 09 (drawn with the slide kit, once per language).
Every value is read from site/data/m09-rajaraman-wong/traces.json and no-replication.json; the candidate DAG is labelled
as candidate data on every figure that shows it."""
import json
from pathlib import Path

from kit import X, table, code, tag, node, fit, INK, MUTED, GOLD, TEAL, RED, BLUE, PURPLE, GROUP, PANEL2

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m09-rajaraman-wong/traces.json").read_text())
NR = json.loads((ROOT / "site/data/m09-rajaraman-wong/no-replication.json").read_text())
DAG = T["dag"]
R = T["run"]["result"]
LABEL_EV = {e["after"]["node"]: e for e in T["run"]["events"] if e["kind"] == "label"}
PIS, POS_O = DAG["PI"], DAG["PO"]
POS = fit({k: tuple(v) for k, v in DAG["positions"].items()}, (960, 240, 1800, 780))
LABELS = R["labels"]


def candidate_tag(cv, x=1380, y=900):
    tag(cv, x, y, X("候选复原数据 · 平票为假设", "Candidate data, reconstructed · tie rule assumed"), PURPLE, 1.0, 22)


def dag(cv, pos=POS, cluster=(), labels=None, focus=None, r=24):
    for u, v in DAG["edges"]:
        inside = u in cluster and v in cluster
        cv.arrow(*pos[u], *pos[v], "#9fc9bf" if inside else "#5d7c80", 3 if inside else 2.4, 14, 1.0, shorten=r + 4)
    for n, p in pos.items():
        fill = TEAL if n in cluster else (BLUE if n in PIS else ("#e39fb8" if n in POS_O else "#a9bdb8"))
        node(cv, *p, n, fill, r, 1.0, GOLD if n == focus else None, size=24)
        if labels and n in labels:
            cv.text(p[0], p[1] - r - 12, f"l={labels[n]}", 22, GOLD, "bold", "center")


def chain_row(cv, groups, y, label, D=3):
    ids = ["P", "X", "Y", "O"]
    x = lambda i: 1000 + i * 200
    start = 0
    for gi, g in enumerate(groups):
        x0, x1 = x(start) - 60, x(start + len(g) - 1) + 60
        cv.rect(x0, y - 66, x1 - x0, 132, stroke=GROUP[gi], width=3, r=30, dash=[12, 8])
        start += len(g)
    where = {n: gi for gi, g in enumerate(groups) for n in g}
    t = 0
    for i, n in enumerate(ids):
        if i:
            cross = where[ids[i - 1]] != where[n]
            t += D if cross else 0
            cv.arrow(x(i - 1) + 34, y, x(i) - 34, y, RED if cross else "#9fc9bf", 4, 14, 1.0, dash=[10, 7] if cross else None)
            cv.text((x(i - 1) + x(i)) / 2, y - 20, f"+{D}" if cross else "+0", 24, RED if cross else MUTED, "bold", "center")
        t += 1
        node(cv, x(i), y, n, "#a9bdb8", 32, 1.0, size=28)
        cv.text(x(i), y + 62, str(t), 24, GOLD, "bold", "center")
    cv.text(1300, y + 120, label, 30, INK, "bold", "center")


def chain(cv, a):
    one, two = T["chainOne"], T["chainTwo"]
    chain_row(cv, [["P", "X"], ["Y", "O"]], 320, X(f"跨界 {one['crossings']} 次：延迟 {one['maxDelay']}", f"{one['crossings']} crossing: delay {one['maxDelay']}"))
    chain_row(cv, [["P"], ["X", "Y"], ["O"]], 640, X(f"跨界 {two['crossings']} 次：延迟 {two['maxDelay']}", f"{two['crossings']} crossings: delay {two['maxDelay']}"))


def dag_fig(cv, a):
    dag(cv, labels=({p: 1 for p in PIS} | {n: LABELS[n] for n in LABEL_EV}) if a.get("labels") else None,
        cluster=LABEL_EV[a["cluster"]]["after"]["cluster"] if a.get("cluster") else (), focus=a.get("cluster"))
    candidate_tag(cv)


def replica(cv, a):
    # schematic: g feeds i and j, which sit in two clusters; with a copy, both get g from inside
    for bx, col, name in ((1000, TEAL, X("簇 1", "Cluster 1")), (1420, BLUE, X("簇 2", "Cluster 2"))):
        cv.rect(bx, 260, 300, 400, stroke=col, width=3, r=30, dash=[12, 8])
        cv.text(bx + 150, 305, name, 26, col, "bold", "center")
    node(cv, 1150, 580, "i", "#a9bdb8", 36)
    node(cv, 1570, 580, "j", "#a9bdb8", 36)
    for bx in (1150, 1570):
        node(cv, bx, 420, "g", GOLD, 36, 1.0, None, True)
        cv.arrow(bx, 420, bx, 580, "#9fc9bf", 3, 14, 1.0, shorten=40)
    cv.text(1150, 485, "g@1", 22, MUTED, align="center")
    cv.text(1570, 485, "g@2", 22, MUTED, align="center")
    cv.line(1190, 420, 1530, 420, PURPLE, 2, 1.0, dash=[6, 8])
    cv.text(1360, 400, X("同一逻辑节点的两个实例", "two instances of one logic node"), 22, PURPLE, align="center")
    tag(cv, 1360, 760, X("代价：多一个实例，多占一份面积（示意）", "The cost: one more instance, one more unit of area (schematic)"), GOLD, 1.0, 24)


def label_i(cv, a):
    e = LABEL_EV["i"]
    rows = [[X("祖先", "Ancestor"), "l(x)", "Δ", X("得分", "Score"), ""]] + \
           [[x["x"], str(x["l"]), str(x["delta"]), str(x["score"]), X("簇内", "inside") if x["inCluster"] else X("簇外", "outside")] for x in e["candidates"]]
    table(cv, 1000, 270, [150, 110, 90, 120, 140], rows, 32, 66, {i + 1: TEAL for i, x in enumerate(e["candidates"]) if x["inCluster"]})
    tag(cv, 1330, 860, f"l1 = {e['metrics']['l1']}, l2 = {e['metrics']['l2']}, l(i) = {e['metrics']['label']}", GOLD)


def instances(cv, a):
    roots = R["selected"]
    x0, y0, w, hgt = 940, 220, 880, 560
    cols, cw, ch = 4, w / 4, hgt / 2
    pos, copies = {}, {}
    for i in R["instances"]:
        copies[i["logicalId"]] = copies.get(i["logicalId"], 0) + 1
    for ci, root in enumerate(roots):
        col, row = ci % cols, ci // cols
        bx, by = x0 + col * cw + 6, y0 + row * ch + 6
        members = R["clusters"][root]
        cv.rect(bx, by, cw - 12, ch - 12, fill=PANEL2, stroke=GROUP[ci % len(GROUP)], width=2, r=14)
        cv.text(bx + 12, by + 28, X(f"簇根 {root} · {len(members)}/4", f"root {root} · {len(members)}/4"), 20, GROUP[ci % len(GROUP)], "bold")
        for mi, m in enumerate(members):
            pos[f"{m}@{root}"] = (bx + 48 + (mi % 2) * 100, by + 80 + (mi // 2) * 92)
    for e in R["instanceEdges"]:
        if not e["cost"]:
            cv.line(*pos[e["from"]], *pos[e["to"]], "#9fc9bf", 3, 1.0)
    for iid, (px, py) in pos.items():
        lg = iid.split("@")[0]
        node(cv, px, py, lg, GOLD if copies[lg] > 1 else "#a9bdb8", 24, 1.0, None, copies[lg] > 1, size=20)
        cv.text(px + 32, py + 8, str(R["arrival"][iid]), 18, MUTED)
    tag(cv, 1380, 840, X(f"{len(roots)} 簇 · {R['instanceCount']} 实例 · 输出 {R['maxDelay']}", f"{len(roots)} clusters · {R['instanceCount']} instances · output {R['maxDelay']}"), GOLD)


def compare(cv, a):
    rows = [["", X("允许复制（RW）", "Replication (RW)"), X("禁止复制（穷举）", "No replication (exhaustive)")],
            [X("最大延迟", "Largest delay"), str(R["maxDelay"]), str(NR["bestMaxDelay"])],
            [X("实例 / 面积", "Instances / area"), str(R["instanceCount"]), str(R["logicalCount"])]]
    table(cv, 960, 330, [250, 280, 380], rows, 32, 96, {1: TEAL})
    cv.text(960, 660, X("不复制的最好方案之一：", "One best grouping without copies: ") + " | ".join("".join(x) for x in NR["example"]), 28, INK)


CODE1 = [X("检查 DAG；拓扑序；算 Δ(x, v)", "check DAG; topological order; Δ(x, v)"), X("PI：l(p) ← δ(p)", "PIs: l(p) ← δ(p)"),
         X("for 非 PI 节点 v（拓扑序）:", "for each non-PI v (topological order):"), "  score(x) ← l(x) + Δ(x, v)",
         X("  候选簇 ← v + 得分最高的祖先（≤ M）", "  cluster ← v + top-scoring ancestors (≤ M)"), X("  l1 ← 簇内 PI 最大得分", "  l1 ← largest PI score inside"),
         X("  l2 ← 簇外最大得分 + D", "  l2 ← largest score outside + D"), "  l(v) ← max(l1, l2)"]
CODE2 = [X("queue ← 所有 PO", "queue ← every PO"), X("while queue 非空:", "while queue is not empty:"), X("  r ← 取出；选中 r 的候选簇", "  r ← pop; select r's cluster"),
         X("  簇外输入 u → 加入 queue（新簇根）", "  outside input u → queue (new root)"), X("for 每个选中的簇根 r、成员 m:", "for each selected root r, member m:"),
         X("  生成实例 m@r", "  make instance m@r"), X("  簇内输入：u@r → m@r（+0）", "  input inside: u@r → m@r (+0)"), X("  簇外输入：u@u → m@r（+D）", "  input outside: u@u → m@r (+D)")]


def pseudo(cv, a):
    code(cv, 930, 280, CODE1 if a.get("part", 1) == 1 else CODE2, a.get("active", (4, 5)), 26, 60, w=900)


FIGURES = {"chain": chain, "dag": dag_fig, "replica": replica, "label_i": label_i, "instances": instances, "compare": compare, "pseudo": pseudo}
