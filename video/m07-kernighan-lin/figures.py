"""Slide figures for Module 07 (drawn with the slide kit, once per language).
Every value is read from site/data/m07-kernighan-lin/traces.json."""
import json
from pathlib import Path

from kit import X, table, code, formula, panel, tag, node, edge, INK, MUTED, GOLD, TEAL, RED, BLUE

T = json.loads((Path(__file__).resolve().parents[2] / "site/data/m07-kernighan-lin/traces.json").read_text())
EDGES = [tuple(e) if isinstance(e, list) else (e["u"], e["v"], e["w"]) for e in T["g01"]["edges"]]
EV = T["run"]["events"]
PASS1, PASS2 = T["run"]["result"]["passes"]
TRIAL1, TRIAL2 = [e for e in EV if e["kind"] == "trial-swap"][:2]
SEEDSIDE = T["seed"]
SIDE_C = {0: TEAL, 1: BLUE}
SLOTS = {0: [(380, 330), (380, 620)], 1: [(900, 250), (900, 470), (900, 690)]}


def layout(side):
    pos = {}
    for s in (0, 1):
        for n, k in zip(sorted(n for n in side if side[n] == s), range(3)):
            pos[n] = SLOTS[s][k]
    return pos


S1 = dict(SEEDSIDE, A=1, D=0)
S2 = dict(S1, E=1, C=0)


def cut_of(side):
    return sum(w for u, v, w in EDGES if side[u] != side[v])


def stage(cv, side, locked=(), rings=None, hl=()):
    """Two rooms (two places and three) and the graph."""
    for x, label in ((150, X("左侧 · 2 个位置", "left · 2 places")), (670, X("右侧 · 3 个位置", "right · 3 places"))):
        cv.rect(x, 150, 460, 640, stroke="#2b5158", width=2, r=24, dash=[10, 8])
        cv.text(x + 230, 196, label, 26, MUTED, "bold", "center")
    pos = layout(side)
    for u, v, w in EDGES:
        k = "|".join(sorted((u, v)))
        edge(cv, pos[u], pos[v], w, "hl" if k in hl else ("cut" if side[u] != side[v] else "inside"), label_offset=26)
    for n in sorted(pos):
        node(cv, *pos[n], n, SIDE_C[side[n]], 42, 1.0, (rings or {}).get(n), n in locked)


def graph_at(cv, side, **kw):
    with cv.place(738, 77, 0.95):
        stage(cv, side, **kw)


def prefix_chart(cv, x, y, gains, best, title):
    panel(cv, x, y, 640, 460, title)
    pos, neg = max(0, max(gains)), max(0, -min(gains))
    scale = min(18, 230 / max(1, pos + neg))
    base_y = y + 120 + pos * scale
    cv.line(x + 50, base_y, x + 600, base_y, "#3b5a5e", 2)
    cv.text(x + 40, base_y + 10, "0", 24, MUTED, align="right")
    for k, g in enumerate(gains):
        bx, h = x + 90 + k * 160, g * scale
        col = GOLD if k == best else (TEAL if g > 0 else RED if g < 0 else MUTED)
        if g:
            cv.rect(bx, base_y - max(h, 0), 90, abs(h), fill=col, r=6)
        else:
            cv.rect(bx, base_y - 3, 90, 6, fill=col, r=3)
        cv.text(bx + 45, base_y - max(h, 0) - 14 if g >= 0 else base_y - h + 40, f"{g:+d}" if g else "0", 32, col, "bold", "center")
        cv.text(bx + 45, y + 420, f"k = {k}", 26, MUTED, align="center")
        if k == best:
            cv.rect(bx - 14, y + 70, 118, 370, stroke=GOLD, width=3, r=12, dash=[10, 7])


def seed(cv, a):
    graph_at(cv, SEEDSIDE)
    cv.text(1345, 900, X(f"种子 AE | BCD：cut = {cut_of(SEEDSIDE)}", f"Seed AE | BCD: cut = {cut_of(SEEDSIDE)}"), 32, GOLD, "bold", "center")


def dtable(cv, a):
    d = TRIAL1["dValues"]
    rows = [[X("节点", "Node"), X("侧", "Side"), X("外部", "Ext."), X("内部", "Int."), X("D = 外 − 内", "D = ext − int")]] + \
           [[n, X("左", "L") if SEEDSIDE[n] == 0 else X("右", "R"), str(d[n]["ext"]), str(d[n]["int"]), f"{d[n]['D']:+d}"] for n in "ABCDE"]
    table(cv, 960, 300, [130, 110, 150, 150, 240], rows, 38, 82)


def pairs(cv, a):
    formula(cv, 1340, 290, [("g(a,b) = D(a) + D(b) − ", INK), ("2w(a,b)", RED)], 44)
    rows = [[X("左 a", "left a"), X("右 b", "right b"), "D(a)+D(b)", "−2w", "g"]] + \
           [[x["a"], x["b"], str(x["Da"] + x["Db"]), str(-2 * x["w"]), f"{x['gain']:+d}" if x["gain"] else "0"] for x in TRIAL1["candidates"]]
    table(cv, 960, 400, [120, 120, 220, 140, 140], rows, 36, 74, {1: GOLD})


def minus2w(cv, a):
    graph_at(cv, SEEDSIDE, hl={"D|E"}, rings={"E": GOLD, "D": GOLD})
    cv.text(1345, 900, X("E↔D：DE 交换前后都被切 → 扣回 2 × 5", "E↔D: DE is cut before and after → take back 2 × 5"), 30, GOLD, "bold", "center")


def trial1(cv, a):
    graph_at(cv, S1, locked=("A", "D"))
    m = TRIAL1["metrics"]
    cv.text(1345, 900, X(f"试探 A↔D：g = +9，cut {m['cutBefore']} → {m['cut']}", f"Trial A↔D: g = +9, cut {m['cutBefore']} → {m['cut']}"), 32, GOLD, "bold", "center")


def trial2(cv, a):
    graph_at(cv, S2, locked=("A", "D", "E", "C"))
    cv.text(1345, 900, X(f"试探 E↔C：g = −8，cut 暂升到 {TRIAL2['metrics']['cut']}", f"Trial E↔C: g = −8, the cut rises to {TRIAL2['metrics']['cut']} for now"), 32, RED, "bold", "center")


def prefix(cv, a):
    prefix_chart(cv, 1000, 250, PASS1["prefixGains"], PASS1["bestK"], X("累计收益（前 k 步）", "Cumulative gain (first k steps)"))
    tag(cv, 1320, 800, X(f"接受前 {PASS1['bestK']} 步：ABC | DE，cut {PASS1['acceptedCut']}", f"Accept the first {PASS1['bestK']}: ABC | DE, cut {PASS1['acceptedCut']}"), TEAL)


def pass2(cv, a):
    prefix_chart(cv, 1000, 250, PASS2["prefixGains"], PASS2["bestK"], X("第二轮的累计收益", "Pass 2, cumulative gain"))
    tag(cv, 1320, 800, X("空前缀 k = 0 胜出 → 停止，cut 3", "The empty prefix k = 0 wins → stop, cut 3"), GOLD)


CODE = [X("repeat:                      # 每次一轮 pass", "repeat:                      # one pass each time"),
        X("  从当前分组开始，全部解锁", "  start from the current split, all unlocked"),
        X("  while 两侧都有未锁定的点:", "  while both sides have unlocked nodes:"),
        X("    在未锁定的 (a, b) 中选 g 最大的一对", "    pick the unlocked (a, b) with the largest g"),
        X("    交换 a, b（试探），锁定，更新 D", "    swap a, b (a trial), lock, update D"),
        X("  取累计收益最大的前缀 k（允许 k = 0）", "  take the prefix k with the largest total (k = 0 allowed)"),
        X("  从本轮起点只应用前 k 步", "  from the pass start apply only the first k"),
        "until k = 0"]


def pseudo(cv, a):
    code(cv, 960, 300, CODE, a.get("active", (4, 5)), 28, 64, w=860)


FIGURES = {"seed": seed, "dtable": dtable, "pairs": pairs, "minus2w": minus2w, "trial1": trial1, "trial2": trial2, "prefix": prefix, "pass2": pass2, "pseudo": pseudo}
