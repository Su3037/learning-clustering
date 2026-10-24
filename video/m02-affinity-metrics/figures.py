"""Slide figures for Module 02 (drawn with the slide kit, once per language).
Every score is read from site/data/m02-affinity-metrics/traces.json."""
import json
import math
from pathlib import Path

from kit import X, table, code, tag, fit, node, edge, panel, score_box, formula, INK, MUTED, GOLD, TEAL, RED, BLUE, PURPLE

T = json.loads((Path(__file__).resolve().parents[2] / "site/data/m02-affinity-metrics/traces.json").read_text())
E5 = [tuple(e) for e in T["g01"]["edges"]]
POS5 = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (230, 230, 900, 790))
PRPOS = {k: tuple(v) for k, v in T["priority"]["positions"].items()}
PREDGES = [tuple(e) for e in T["priority"]["edges"]]
SHARED = {(p["u"], p["v"]): p for p in T["shared"]}
EDGE_RANK = T["edge"]
PIN = T["pin"]


def g5(cv, states=None, rings=None, alpha=1.0, tags=None, fills=None, pos=None):
    pos = pos or POS5
    st = states or {}
    for u, v, w in E5:
        edge(cv, pos[u], pos[v], w, st.get(f"{u}|{v}", "normal"), alpha)
    for n, p in pos.items():
        node(cv, *p, n, (fills or {}).get(n, "#a9bdb8"), 40, alpha, (rings or {}).get(n))
        if tags and tags.get(n):
            cv.text(p[0], p[1] + 82, tags[n], 26, GOLD, "bold", "center", alpha=alpha)


def priority_graph(cv, box, states=None, rings=None):
    pos = fit(PRPOS, box)
    for u, v, w in PREDGES:
        edge(cv, pos[u], pos[v], w, (states or {}).get(f"{u}|{v}", "normal"), 1.0)
    for n, p in pos.items():
        node(cv, *p, n, TEAL if n in "PQR" else BLUE, 40, 1.0, (rings or {}).get(n))
    return pos


def g01(cv, a):
    with cv.place(800, 40, 1.0):
        g5(cv)
    cv.text(1380, 960, X("课程公共图 G01（总权 18）", "Course graph G01 (total weight 18)"), 30, MUTED, "bold", "center")


def model(cv, a):
    with cv.place(820, 180, 0.58):
        panel(cv, 140, 170, 760, 640, X("普通的边：两端", "An ordinary edge: two ends"), 1.0)
        node(cv, 330, 500, "A", TEAL, 44, 1.0); node(cv, 710, 500, "B", TEAL, 44, 1.0)
        edge(cv, (330, 500), (710, 500), 5, "normal", 1.0)
        panel(cv, 1020, 170, 760, 640, X("一个 net：五个引脚", "One net: five pins"), 1.0)
        hub = (1400, 500)
        pins = {n: (1400 + 230 * math.cos(-math.pi / 2 + i * 2 * math.pi / 5), 500 + 210 * math.sin(-math.pi / 2 + i * 2 * math.pi / 5)) for i, n in enumerate("ABCDE")}
        cv.circle(*hub, 14, fill=GOLD)
        for n, p in pins.items():
            cv.line(hub[0], hub[1], p[0], p[1], GOLD, 4, 1.0)
            node(cv, *p, n, TEAL, 38, 1.0)
        names = list(pins)
        for i in range(5):
            for j in range(i + 1, 5):
                cv.line(*pins[names[i]], *pins[names[j]], "#8fb1e6", 2, 0.55, dash=[8, 8])
        cv.text(1400, 780, X("展开成 10 对“示意贡献”——不是 10 根新导线", "Drawn as 10 illustrative contributions, not 10 new wires"), 28, MUTED, "bold", "center")


def edge_rank(cv, a):
    rows = [[X("名次", "Rank"), X("节点对", "Pair"), X("分数", "Score")]] + [[str(i + 1), f"{x['u']}–{x['v']}", str(x["score"])] for i, x in enumerate(EDGE_RANK)]
    table(cv, 1000, 300, [170, 300, 170], rows, 38, 84, {1: GOLD, 2: GOLD})


def shared_table(cv, a):
    rows = [[X("节点对", "Pair"), X("直接", "Direct"), X("经共同邻居", "Via shared"), X("分数", "Score")]]
    for p in T["shared"]:
        via = " + ".join(f"{v['x']}:{v['min']}" for v in p["parts"]["via"]) or "—"
        rows.append([f"{p['u']}–{p['v']}", str(p["parts"]["direct"]), via, str(p["score"])])
    hl = {i: GOLD for i, r in enumerate(rows) if r[0] in ("A–C", "B–D")}
    table(cv, 980, 250, [170, 120, 330, 120], rows, 32, 66, hl)


def hand(cv, a):
    pair = tuple(a.get("pair", "AC"))
    s = SHARED[pair]
    items = [(X(f"直接边 w({pair[0]},{pair[1]})", f"direct edge w({pair[0]},{pair[1]})"), s["parts"]["direct"], TEAL, 1)] + \
            [(X(f"经 {x['x']}：min({x['wu']}, {x['wv']})", f"via {x['x']}: min({x['wu']}, {x['wv']})"), x["min"], GOLD, 1) for x in s["parts"]["via"]]
    with cv.place(880, 120, 0.62):
        g5(cv, {"|".join(sorted((pair[0], x["x"]))): "hl" for x in s["parts"]["via"]} | {"|".join(sorted((pair[1], x["x"]))): "hl" for x in s["parts"]["via"]}, {pair[0]: GOLD, pair[1]: GOLD})
    score_box(cv, 1440, 260, 400, items, s["score"], 1.0, f"{pair[0]}–{pair[1]}", 28)


def priority(cv, a):
    with cv.place(800, 200, 0.58):
        panel(cv, 130, 160, 800, 700, X("按直接边权", "By direct weight"), 1.0)
        panel(cv, 1010, 160, 800, 700, X("按共同邻居", "By shared neighbours"), 1.0)
        priority_graph(cv, (170, 280, 860, 700), {"X|Y": "hl"}, {"X": GOLD, "Y": GOLD})
        pr = T["priorityShared"]
        pos = priority_graph(cv, (1060, 280, 1750, 700), {"P|Q": "hl", "P|R": "hl", "Q|R": "hl"}, {"P": GOLD, "Q": GOLD})
        tag(cv, pos["R"][0], pos["R"][1] - 70, X("经 R：min(4, 4) = 4", "via R: min(4, 4) = 4"), GOLD, 1.0, 24)
        tag(cv, 530, 820, X("第一对：X–Y @ 5", "first pair: X–Y @ 5"), BLUE, 1.0)
        tag(cv, 1410, 820, X(f"第一对：{pr[0]['u']}–{pr[0]['v']} @ {pr[0]['score']}", f"first pair: {pr[0]['u']}–{pr[0]['v']} @ {pr[0]['score']}"), TEAL, 1.0)


def netlist(cv, pick=None):
    """Nets drawn as hyperedge outlines around their pins (not as extra wires)."""
    pos = {"A": (300, 420), "B": (450, 420), "C": (600, 420), "D": (750, 420), "E": (900, 420), "F": (900, 640)}
    cv.rect(220, 330, 760, 180, stroke=GOLD, width=4, r=60)
    cv.rect(195, 300, 810, 240, stroke=PURPLE, width=4, r=80, dash=[14, 9])
    cv.rect(830, 350, 140, 360, stroke=TEAL, width=5, r=60)
    cv.text(230, 284, X("net enable（5 引脚）", "net enable (5 pins)"), 26, GOLD, "bold")
    cv.text(230, 580, X("net reset（5 引脚）", "net reset (5 pins)"), 26, PURPLE, "bold")
    cv.text(1000, 760, X("net n1（2 引脚，私有）", "net n1 (2 pins, private)"), 26, TEAL, "bold", "right")
    for n, p in pos.items():
        node(cv, *p, n, "#a9bdb8", 38, 1.0, GOLD if pick and n in pick else None)
    return pos


def pin(cv, a):
    with cv.place(760, 60, 0.85):
        netlist(cv, ("E", "F"))
    raw = {(p["u"], p["v"]): p["score"] for p in PIN["raw"]}
    sc = {(p["u"], p["v"]): p["score"] for p in PIN["scores"]}
    rows = [["", X("按 net 计数", "net count"), "pin-count"], ["A–B", str(raw[("A", "B")]), f"{sc[('A', 'B')]:g}"], ["E–F", str(raw[("E", "F")]), f"{sc[('E', 'F')]:g}"]]
    table(cv, 1010, 790, [150, 260, 240], rows, 36, 66, {2: GOLD})


def pseudo(cv, a):
    lines = [X("for 每个无序节点对 (u, v)，u < v:", "for each unordered pair (u, v), u < v:"),
             X("    score ← w(u, v)，没有边则为 0", "    score ← w(u, v), or 0 with no edge"),
             X("    for 每个共同邻居 x:", "    for each shared neighbour x:"),
             "        score ← score + min(w(u,x), w(v,x))",
             X("    if score > 0: 记下 (u, v, score)", "    if score > 0: record (u, v, score)"),
             X("按 (−score, u, v) 排序", "sort by (−score, u, v)"),
             X("返回排名（不是分组）", "return the ranking (not a grouping)")]
    code(cv, 930, 300, lines, (3, 4), 26, 64, w=900)


FIGURES = {"g01": g01, "model": model, "edge_rank": edge_rank, "shared_table": shared_table, "hand": hand, "priority": priority, "pin": pin, "pseudo": pseudo}
