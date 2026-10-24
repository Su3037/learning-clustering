"""Slide figures for Module 08 (drawn with the slide kit, once per language).
Every value is read from site/data/m08-fiduccia-mattheyses/traces.json."""
import json
from pathlib import Path

from kit import X, table, code, tag, panel, node, edge, fit, INK, MUTED, GOLD, TEAL, RED, BLUE, PURPLE

T = json.loads((Path(__file__).resolve().parents[2] / "site/data/m08-fiduccia-mattheyses/traces.json").read_text())
E5 = [tuple(e) if isinstance(e, list) else (e["u"], e["v"], e["w"]) for e in T["g01"]["edges"]]
POS = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (200, 230, 860, 780))
EV = T["run"]["events"]
P1, P2 = T["run"]["result"]["passes"]
SEED = T["seed"]
SIDEC = {0: TEAL, 1: BLUE}


def sg(g):
    return f"{g:+d}" if g else "0"


def graph(cv, pos, edges, side, locked=(), focus=None, blocked=(), hl=None, r=40):
    for u, v, w in edges:
        k = "|".join(sorted((u, v)))
        edge(cv, pos[u], pos[v], w, (hl or {}).get(k) or ("cut" if side[u] != side[v] else "inside"))
    for n, p in pos.items():
        ring = GOLD if n == focus else (RED if n in blocked else None)
        node(cv, *p, n, SIDEC[side[n]], r, 1.0, ring, n in locked)


def g(cv, side, **kw):
    with cv.place(800, 40, 1.0):
        graph(cv, POS, E5, side, **kw)


def gain_table(cv, gains, x, y, chosen=None):
    rows = [[X("节点", "Node"), X("侧", "Side"), X("收益", "Gain"), X("合法", "Legal")]] + \
           [[e["node"], str(e["side"]), sg(e["gain"]), X("已锁定", "locked") if e["locked"] else (X("是", "yes") if e["legal"] else X("否", "no"))] for e in gains]
    hl = {i + 1: (GOLD if e["node"] == chosen else RED) for i, e in enumerate(gains) if e["node"] == chosen or (not e["legal"] and not e["locked"])}
    table(cv, x, y, [120, 90, 130, 150], rows, 32, 62, hl)


def cum_chart(cv, x, y, gains, best, title):
    panel(cv, x, y, 680, 460, title)
    mx = max(1, max(gains)), max(0, -min(gains))
    sc = min(18, 230 / max(1, mx[0] + mx[1]))
    base = y + 120 + mx[0] * sc
    cv.line(x + 40, base, x + 650, base, "#3b5a5e", 2)
    for k, v in enumerate(gains):
        bx, hgt = x + 60 + k * 100, abs(v) * sc
        col = GOLD if k == best else (TEAL if v > 0 else RED if v < 0 else MUTED)
        cv.rect(bx, base - hgt if v >= 0 else base, 70, max(5, hgt), fill=col, r=6)
        cv.text(bx + 35, (base - hgt - 12) if v >= 0 else base + hgt + 36, sg(v), 30, col, "bold", "center")
        cv.text(bx + 35, y + 440, f"k={k}", 24, MUTED, align="center")
        if k == best:
            cv.rect(bx - 10, y + 60, 90, 400, stroke=GOLD, width=3, r=10, dash=[10, 7])


def gains(cv, a):
    with cv.place(800, 150, 0.56):
        graph(cv, POS, E5, SEED, blocked=("A", "E"), focus="D")
    gain_table(cv, EV[0]["gains"], 1320, 300, "D")


def fste(cv, a):
    g(cv, SEED, focus="D", hl={"D|E": "hl", "C|D": "trial"})
    tag(cv, 1350, 960, X("FS D–E +5，TE C–D −2 → 收益 3", "FS D–E +5, TE C–D −2 → gain 3"), GOLD)


def walk(cv, a):
    rows = [[X("步", "Step"), X("移动", "Move"), X("收益", "Gain"), "cut", X("累计", "Cum.")]] + \
           [[str(i + 1), m["node"], sg(m["gain"]), str(m["cutAfter"]), sg(m["cumulative"])] for i, m in enumerate(P1["moves"])]
    table(cv, 980, 300, [100, 140, 140, 140, 140], rows, 34, 76, {2: GOLD})


def prefix(cv, a):
    cum_chart(cv, 1000, 250, P1["prefixGains"], P1["bestK"], X("累计收益（前 k 步）", "Cumulative gain (first k steps)"))
    tag(cv, 1340, 800, X(f"接受前 {P1['bestK']} 步：ABC | DE，cut {P1['acceptedCut']}", f"Accept the first {P1['bestK']}: ABC | DE, cut {P1['acceptedCut']}"), TEAL)


def legacy(cv, a):
    Lg = T["legacy"]
    gE = next(e for e in Lg["run"]["events"][0]["gains"] if e["node"] == "E")
    rows = [["", X("原文", "The text"), X("按数据计算", "From its data")],
            [X("初始 cut", "Initial cut"), "9", str(Lg["run"]["events"][0]["metrics"]["cut"])],
            [X("合法收益", "Legal gains"), X("全部 ≤ 0", "all ≤ 0"), X(f"E 合法 +{gE['gain']}", f"E legal, +{gE['gain']}")],
            [X("最终 cut", "Final cut"), "4", X(f"首轮 {Lg['run']['result']['passes'][0]['acceptedCut']}", f"pass 1: {Lg['run']['result']['passes'][0]['acceptedCut']}")],
            [X("穷举最优", "Exhaustive optimum"), "—", str(Lg["optimum"]["cut"])]]
    table(cv, 960, 320, [280, 240, 340], rows, 32, 90, {i: RED for i in range(1, 5)})


def escape(cv, a):
    E = T["escape"]
    gr = E["graph"]
    p = E["run"]["result"]["passes"][0]
    pos = fit(dict({k: tuple(v) for k, v in gr["positions"].items()}, F=(620, 400)), (960, 250, 1400, 620))
    graph(cv, pos, [tuple(x) for x in gr["edges"]], p["accepted"], r=34)
    rows = [[X("步", "Step"), X("移动", "Move"), X("收益", "Gain"), "cut"]] + [[str(i + 1), m["node"], sg(m["gain"]), str(m["cutAfter"])] for i, m in enumerate(p["moves"][:3])]
    table(cv, 1480, 280, [80, 110, 100, 80], rows, 28, 58, {3: GOLD})
    tag(cv, 1350, 860, X(f"保留 3 步：cut {p['startCut']} → {p['acceptedCut']} = 穷举最优", f"Keep 3 steps: cut {p['startCut']} → {p['acceptedCut']} = the exhaustive optimum"), TEAL)


def multipin(cv, a):
    with cv.place(700, 60, 0.95):
        pins = {"A": (360, 360), "B": (360, 560), "C": (560, 460), "D": (1000, 460)}
        hub = (760, 460)
        for n, p in pins.items():
            cv.line(*hub, *p, PURPLE, 4)
        cv.circle(*hub, 14, fill=PURPLE)
        cv.text(740, 410, X("net（权 3）", "net (weight 3)"), 26, PURPLE, "bold", "center")
        for n, p in pins.items():
            node(cv, *p, n, SIDEC[0 if n != "D" else 1], 40)
        cv.line(860, 260, 860, 700, GOLD, 3, 1.0, dash=[10, 8])
    tag(cv, 1340, 860, X("按引脚计数：A 0，D +3；拆成团：A −1", "Counting pins: A 0, D +3; as a clique: A −1"), GOLD)


CODE = [X("repeat：全部解锁，记下起点", "repeat: unlock all, remember the start"),
        X("  按 net 计数，算出所有收益", "  count pins per net, compute every gain"),
        X("  while 有合法的未锁定节点:", "  while a legal unlocked node exists:"),
        X("    v ← 合法候选中收益最大者", "    v ← the legal candidate with the largest gain"),
        X("    移动 v（试探），锁定 v", "    move v (a trial), lock v"),
        X("    只更新受影响节点的收益", "    update only the affected nodes' gains"),
        X("  k* ← 最佳前缀（允许 0）", "  k* ← the best prefix (0 allowed)"),
        X("  回到起点，只应用前 k* 步", "  back to the start, apply only the first k*"),
        "until k* = 0"]


def pseudo(cv, a):
    code(cv, 930, 290, CODE, (3, 4), 27, 62, w=900)


FIGURES = {"gains": gains, "fste": fste, "walk": walk, "prefix": prefix, "legacy": legacy, "escape": escape, "multipin": multipin, "pseudo": pseudo}
