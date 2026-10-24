"""Module 04 · Size-constrained agglomerative clustering — the four films.

  story     popular science, cut to "We Never (Remix)": two-seater cars that cannot take five friends in two,
            a taxi where two cellos block the obvious pairing, and tandem bikes where the best first pair costs
            the most. Three endings: impossible, stuck, legal but not the best.
  concise   the essentials: four report items, filter before choosing, the lower bound, greedy_trap, suboptimal,
            node sizes.
  advanced  why the filter must come first, what the bound can and cannot prove, how fast exhaustive search grows,
            comparing cuts only at the same K, how far from optimal greedy can land, and area instead of count.
  lab       experiment walkthrough recorded from the real page (walkthrough.mjs → scripts/film/walkthrough.py).

Every state on G01, greedy_trap and suboptimal is read from site/data/m04-size-constrained-agglomerative/
traces.json, which scripts/build-traces.mjs produces by running site/engines/merge.js (greedy run plus the
exhaustive oracle). The extra examples (three twin-size rooms, the scaled suboptimal family) run through the
course's Python reference, python/m04-size-constrained-agglomerative/reference.py, which tests/crosscheck.py
checks against the engine.
"""
import importlib.util
import json
import math
from pathlib import Path

from cine import (W, H, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, CORAL, LILAC, SAGE, IVORY, MUTED, FAINT, DIM,
                  PANEL_BG, NODE_BG, clamp, ease, lerp, title_card, panel, badge, bar, code_panel, table, graph, fit, pulse,
                  count_hits, substrate)
from story import S, TRACK, INTRO_HITS, FILL1, FILL2, PHRASE, FILL3, FILL4, title_assemble, credits, MUSIC_LINE, landed

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m04-size-constrained-agglomerative/traces.json").read_text())
BRAND = L("Learning Clustering · Module 04 · 容量约束凝聚聚类", "Learning Clustering · Module 04 · Size-constrained agglomerative")

_spec = importlib.util.spec_from_file_location("m04ref", ROOT / "python/m04-size-constrained-agglomerative/reference.py")
REF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REF)

NEUTRAL = "#9fbcbc"
G01E = [tuple(e) for e in T["g01"]["edges"]]
G01P = {k: tuple(v) for k, v in T["g01"]["positions"].items()}
TRAP_G, SUB_G = T["graphs"]["greedy_trap"], T["graphs"]["suboptimal"]
TRAPE, SUBE = [tuple(e) for e in TRAP_G["edges"]], [tuple(e) for e in SUB_G["edges"]]
TRAP_SIZE = {n["id"]: n["size"] for n in TRAP_G["nodes"]}
ONES = {n: 1 for n in "ABCDE"}
CAP2, CAP3, K3C2, TRAP, SUB, UNEVEN = T["cap2"], T["cap3"], T["k3cap2"], T["trap"], T["suboptimal"], T["uneven"]


def clusters_of(labels, sizes):
    return [{"label": l, "members": list(l), "size": sum(sizes[m] for m in l)} for l in labels]


# facts the captions state, checked against the engine output
assert CAP3["run"]["result"]["labels"] == ["ABC", "DE"] and CAP3["run"]["result"]["cut"] == 3
assert CAP2["run"]["result"]["labels"] == ["AB", "C", "DE"] and CAP2["run"]["result"]["cut"] == 8
assert CAP2["kind"] == "infeasible-by-bound" and CAP2["oracle"]["lowerBoundClusters"] == 3
assert [(c["a"], c["b"], c["size"], c["legal"]) for c in CAP2["run"]["events"][2]["candidates"][:2]] == [("AB", "C", 3, False), ("D", "E", 2, True)]
assert sorted((c["a"], c["b"], c["size"]) for c in CAP2["run"]["events"][-1]["candidates"]) == [("AB", "C", 3), ("C", "DE", 3)]
assert K3C2["run"]["result"]["targetReached"] and K3C2["run"]["result"]["labels"] == ["AB", "C", "DE"]
assert TRAP["kind"] == "greedy-stuck" and TRAP["run"]["result"]["labels"] == ["A", "B", "CD"] and TRAP["run"]["result"]["cut"] == 8
assert TRAP["oracle"]["lowerBoundClusters"] == 2 and TRAP["oracle"]["bestCutAtK"] == {"cut": 10, "clusters": [["A", "C"], ["B", "D"]]}
assert sorted((c["a"], c["b"], c["size"]) for c in TRAP["run"]["events"][-1]["candidates"]) == [("A", "CD", 4), ("B", "CD", 4)]
assert SUB["kind"] == "feasible-suboptimal" and SUB["run"]["result"]["cut"] == 18 and SUB["oracle"]["bestCutAtK"]["cut"] == 11
assert SUB["run"]["result"]["labels"] == ["AB", "CD"] and SUB["oracle"]["bestCutAtK"]["clusters"] == [["A", "C"], ["B", "D"]]
assert UNEVEN["result"]["labels"] == ["AB", "CDE"] and UNEVEN["result"]["cut"] == 5

# a lower bound that allows K is not a proof: three twin-size rooms
TRIO = {"nodes": ["X", "Y", "Z"], "sizes": {"X": 2, "Y": 2, "Z": 2}, "edges": [("X", "Y", 3), ("Y", "Z", 2), ("X", "Z", 1)]}
_trio_o = REF.oracle(TRIO, 2, 3)
assert _trio_o["lower_bound"] == 2 and _trio_o["min_feasible_clusters"] == 3 and _trio_o["best_cut_at_k"] is None
assert REF.classify(TRIO, 2, 3) == "infeasible-by-search"


# the suboptimal family: A–B = M, A–C = B–D = M − 1, C–D = 1, capacity 2
def sub_family(m):
    g = {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B", m), ("A", "C", m - 1), ("B", "D", m - 1), ("C", "D", 1)]}
    return REF.solve(g, 2, 2)["cutsize"], REF.oracle(g, 2, 2)["best_cut_at_k"][0]


FAMILY = [(m, *sub_family(m)) for m in (10, 100, 1000)]
assert FAMILY[0][1:] == (18, 11) and FAMILY[1][1:] == (198, 101) and FAMILY[2][1:] == (1998, 1001)


def bell(n):
    row = [1]
    for _ in range(n - 1):
        nxt = [row[-1]]
        for v in row:
            nxt.append(nxt[-1] + v)
        row = nxt
    return row[-1]


BELL = {n: bell(n) for n in (5, 10, 15, 20)}
assert BELL[5] == 52 and BELL[10] == 115975 and BELL[20] == 51724158235372
# with capacity 2 only 26 of G01's 52 partitions are legal (the oracle counts them)
assert CAP2["oracle"]["legalPartitions"] == 26


def key(u, v):
    return "|".join(sorted((u, v)))


def convex(points):
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def hull(fr, pts, col, alpha, R=72):
    if alpha <= 0:
        return
    ring = [(round(x + R * math.cos(t * math.pi / 14), 2), round(y + R * math.sin(t * math.pi / 14), 2)) for x, y in pts for t in range(28)]
    fr.polyline(convex(ring), col, 1.8, 0.75 * alpha, close=True, fill=col, fill_alpha=0.08 * alpha)


def seats(fr, x, y, used, cap, col, alpha, unit=22, over=False):
    """A row of `cap` seats centred on x; the first `used` are filled. Over capacity: extra seats in rose, outside."""
    n = max(cap, used)
    x0 = x - (n - 1) * unit * 1.25 / 2
    for i in range(n):
        p = (x0 + i * unit * 1.25, y)
        if i < cap:
            fr.rect(p[0] - unit / 2, p[1] - unit / 2, unit, unit, fill=(col if i < used else None), stroke=col if i < used else FAINT,
                    width=1.4, alpha=alpha * (0.85 if i < used else 0.9), r=4, screen=True)
        else:
            fr.rect(p[0] - unit / 2, p[1] - unit / 2, unit, unit, fill=ROSE, stroke=ROSE, width=1.4, alpha=alpha, r=4, screen=True, glow=0.4 * alpha)
    if over:
        fr.text(f"{used} > {cap}", x + n * unit * 0.7 + 18, y + 8, 22, ROSE, alpha, role="mono")


def scene_graph(fr, pos, edges, clusters, sizes, cap, alpha=1.0, hue=None, names=None, focus=(), blocked=(), r=40, seat_rows=True,
                weights=True, size_tags=False, hl=()):
    """Clusters as soft hulls with their seat rows (size / capacity); crossing wires rose; blocked nodes ringed rose."""
    hue = hue or {}
    where = {m: c["label"] for c in clusters for m in c["members"]}
    mean_y = sum(p[1] for p in pos.values()) / len(pos)
    hue_of = {}
    for i, c in enumerate(clusters):
        col = hue.get(c["label"], [TEAL, BLUE, AMBER, LILAC][i % 4]) if len(c["members"]) > 1 else NEUTRAL
        hue_of[c["label"]] = col
        pts = [pos[m] for m in c["members"]]
        R = r + 30
        if len(c["members"]) > 1:
            hull(fr, pts, col, alpha, R=R)
        if seat_rows and cap:
            below = sum(p[1] for p in pts) / len(pts) > mean_y
            cx = sum(p[0] for p in pts) / len(pts)
            cy = (max(p[1] for p in pts) + R + 30) if below else (min(p[1] for p in pts) - R - 22)
            seats(fr, cx, cy, c["size"], cap, col if len(c["members"]) > 1 else MUTED, alpha, unit=18)
    crossing = {key(u, v) for u, v, _ in edges if where[u] != where[v]}
    cols = {n: hue_of[where[n]] for n in pos}
    graph(fr, pos, edges, cols, alpha, cut=crossing, names=names is None, r=r, glow_nodes=focus, weights=weights, hl_edges=hl)
    for n in focus:
        fr.ring(pos[n], r + 9, GOLD, 2.4, alpha, glow=0.6 * alpha)
    for n in blocked:
        fr.ring(pos[n], r + 9, ROSE, 2.4, alpha, glow=0.5 * alpha, dash=[6, 5])
    if names:
        for n, p in pos.items():
            fr.text(tr(names[n]), p[0], p[1] + 9, 25, IVORY, alpha, anchor="c", role="serif")
    if size_tags:
        for n, p in pos.items():
            if sizes[n] != 1:
                badge(fr, p[0] + r + 16, p[1] - r - 6, f"s={sizes[n]}", GOLD, alpha, 16, screen=True)


def cand_rows(fr, x, y, cands, alpha, title, chosen=None, w=600, lh=50, size=24, cap=None, n_shown=99):
    panel(fr, x, y, w, 96 + lh * len(cands), alpha, title)
    for i, c_ in enumerate(cands):
        a = clamp(n_shown - i) * alpha
        if a <= 0:
            continue
        yy = y + 100 + i * lh
        on = chosen is not None and i == chosen
        bad = not c_.get("legal", True)
        if on:
            fr.rect(x + 12, yy - size - 6, w - 24, lh - 6, fill="#1d2f2a", alpha=a, r=4, screen=True)
        fr.text(f"{c_['a']}–{c_['b']}", x + 36, yy, size, ROSE if bad else IVORY, a, role="serif")
        fr.text(f"{c_['affinity']:g}", x + 250, yy, size, GOLD if on else (ROSE if bad else IVORY), a, role="mono", anchor="r")
        if cap is not None:
            fr.text(f"{c_['size']}/{cap}", x + 380, yy, size, ROSE if bad else MUTED, a, role="mono", anchor="r")
        if bad:
            fr.line((x + 28, yy - 8), (x + 390, yy - 8), ROSE, 2, 0.8 * a)
            fr.text(L("超容量", "over capacity"), x + w - 30, yy, size - 6, ROSE, a, anchor="r")
        elif on:
            fr.text(L("选中", "chosen"), x + w - 30, yy, size - 6, GOLD, a, anchor="r")


def report_card(fr, x, y, rows, alpha, title=None, w=600):
    """The four report items, each with its own verdict."""
    panel(fr, x, y, w, 70 + 58 * len(rows) + (40 if title else 0), alpha, title)
    y0 = y + (110 if title else 70)
    for i, (lab, val, col) in enumerate(rows):
        fr.text(lab, x + 36, y0 + i * 58, 24, MUTED, alpha, role="mono")
        fr.text(val, x + w - 36, y0 + i * 58, 26, col, alpha, role="mono", anchor="r")


# ====================================================================== popular film
FR = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev", "E": "Eva"}
FPOS = fit(G01P, (260, 250, 880, 740))
TRAP_POS = fit({k: tuple(v) for k, v in TRAP_G["positions"].items()}, (240, 360, 980, 640))
SUB_POS = fit({k: tuple(v) for k, v in SUB_G["positions"].items()}, (340, 300, 820, 700))
FHUE = {"AB": TEAL, "DE": BLUE, "CD": AMBER, "AC": TEAL, "BD": BLUE, "ABC": TEAL}


def p_open(fr, c):
    for i, n in enumerate("ABCDE"):
        a = landed(c.T, INTRO_HITS, i)
        if a <= 0:
            continue
        p = FPOS[n]
        fr.dot(p, 46, NODE_BG, a)
        fr.ring(p, 46, NEUTRAL, 2.8, a)
        fr.text(FR[n], p[0], p[1] + 9, 26, IVORY, a, anchor="c", role="serif")
    if c.on(1):
        a = c.p(1)
        for i in range(2):
            x = 1150 + i * 330
            fr.rect(x, 420, 260, 130, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.95 * a, r=34, screen=True)
            fr.text(L(f"双座车 {i + 1}", f"two-seater {i + 1}"), x + 130, 480, 26, MUTED, a, anchor="c", role="serif")
            seats(fr, x + 130, 520, 0, 2, TEAL, a, unit=26)


def p_ask(fr, c):
    scene_graph(fr, FPOS, G01E, clusters_of(list("ABCDE"), ONES), ONES, None, 1.0, names=FR, seat_rows=False)
    a = c.p(0)
    fr.text(L("合得来的坐一起——", "friends ride together —"), 1400, 420, 34, IVORY, a, anchor="c", role="serif")
    if c.on(1):
        fr.text(L("装得下吗？", "but does it fit?"), 1400, 510, 56, GOLD, c.p(1), anchor="c", role="serif", glow=0.3 * c.p(1))


def p_rule(fr, c):
    ev = CAP2["run"]["events"][2]
    scene_graph(fr, FPOS, G01E, ev["before"], ONES, 2, 1.0, hue=FHUE, names=FR)
    cands = [dict(x, a=" · ".join(FR[m] for m in x["a"]), b=" · ".join(FR[m] for m in x["b"])) for x in ev["candidates"][:3]]
    if not c.on(1):  # nothing is crossed out until the second line
        for x in cands:
            x["legal"] = True
    cand_rows(fr, 1060, 250, cands, c.p(0), L("下一对候选 · 两个座位", "THE NEXT CANDIDATES · TWO SEATS"), chosen=1 if c.on(2) else None, w=680, cap=2)
    if c.on(2):
        fr.paragraph(L("先划掉装不下的，再选最合得来的。", "Cross out what does not fit, then take the best pair."), 1080, 620, 30, 640, GOLD, c.p(2), role="serif")


def p_title(fr, c):
    title_assemble(fr, c, L("装得下吗", "Does It Fit?"), L("容量约束凝聚聚类 · SIZE-CONSTRAINED AGGLOMERATIVE", "SIZE-CONSTRAINED AGGLOMERATIVE CLUSTERING"), "MODULE 04")


def p_cars(fr, c):
    ev = CAP2["run"]["events"]
    landed_ = c.T >= FILL1[0]
    st = ev[-1]["after"] if landed_ else (ev[2]["after"] if c.on(1) else ev[1]["after"])
    scene_graph(fr, FPOS, G01E, st, ONES, 2, 1.0, hue=FHUE, names=FR, blocked=("C",) if c.on(1) else ())
    panel(fr, 1080, 260, 620, 330, c.p(0), L("五个人 · 双座车 · 想要两辆", "FIVE PEOPLE · TWO-SEATERS · WANT TWO CARS"))
    fr.text(L("Ada · Ben 先上车", "Ada · Ben go first"), 1120, 360, 26, TEAL, c.p(0))
    if c.on(1):
        fr.text(L("Cai 加进来就是 3 个人", "adding Cai makes 3 people"), 1120, 420, 26, ROSE, c.p(1))
        fr.text(L("Dev · Eva 上第二辆", "Dev · Eva take the second"), 1120, 480, 26, BLUE, c.p(1, delay=0.6))
    if landed_:
        a = landed(c.T, FILL1, len(FILL1) - 1)
        fr.text(L("Cai 只能单独一辆：三辆车", "Cai rides alone: three cars"), 1120, 545, 28, GOLD, a, role="serif", glow=0.3 * a)


def p_bound(fr, c):
    a0 = c.p(0)
    panel(fr, 260, 230, 1400, 330, a0, L("数座位", "COUNT THE SEATS"))
    for i in range(5):
        x = 360 + i * 90
        fr.dot((x, 360), 30, NODE_BG, a0)
        fr.ring((x, 360), 30, NEUTRAL, 2.4, a0)
        fr.text(FR["ABCDE"[i]][:1], x, 370, 24, IVORY, a0, anchor="c", role="serif")
    fr.text(L("5 个人", "5 people"), 540, 450, 26, MUTED, a0, anchor="c")
    fill = 0
    if c.T >= FILL2[0]:
        fill = sum(1 for t in FILL2 if c.T >= t)
    if c.on(1):
        a = c.p(1)
        for j in range(3):
            x = 1010 + j * 200
            fr.rect(x - 80, 320, 160, 80, fill=PANEL_BG, stroke=FAINT if j < 2 else ROSE, width=1.4, alpha=a, r=24, screen=True)
            used = min(2, max(0, (5 if fill or c.on(2) else 0) - 2 * j))
            seats(fr, x, 360, used, 2, ROSE if j == 2 else TEAL, a, unit=26)
        fr.text(L("每辆 2 座", "2 seats each"), 1210, 450, 26, MUTED, a, anchor="c")
    if c.on(2):
        a = c.p(2)
        fr.text("⌈ 5 ÷ 2 ⌉ = 3", W / 2, 680, 64, GOLD, a, role="mono", anchor="c", glow=0.3 * a)
        fr.text(L("至少三辆：两辆根本不可能", "at least three: two is simply impossible"), W / 2, 760, 28, IVORY, a, anchor="c")


def p_cello(fr, c):
    ev = TRAP["run"]["events"]
    st = ev[-1]["after"] if c.on(2) else (ev[1]["after"] if c.on(1) else ev[0]["after"])
    names = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev"}
    scene_graph(fr, TRAP_POS, TRAPE, st, TRAP_SIZE, 3, 1.0, hue=FHUE, names=names, blocked=("A", "B") if c.on(2) else (), size_tags=True)
    panel(fr, 1100, 260, 600, 300, c.p(0), L("出租车 · 每辆 3 座", "TAXIS · 3 SEATS EACH"))
    fr.text(L("Ada、Ben 各带一把大提琴：占 2 座", "Ada and Ben each carry a cello: 2 seats"), 1130, 350, 24, GOLD, c.p(0))
    if c.on(1):
        fr.text(L("Cai–Dev 最要好（10），先同车", "Cai–Dev are closest (10): they ride first"), 1130, 410, 24, AMBER, c.p(1))
    if c.on(2):
        fr.text(L("再加谁都是 4 座 > 3", "adding anyone makes 4 seats > 3"), 1130, 470, 24, ROSE, c.p(2))
        fr.text(L("三辆车", "three taxis"), 1130, 525, 28, ROSE, c.p(2), role="serif")


def p_flip(fr, c):
    n = count_hits(c.T, PHRASE)
    alt = c.T >= PHRASE[0] and n % 2 == 1
    if c.T > PHRASE[-1] + 0.2:
        alt = True
    greedy = clusters_of(TRAP["run"]["result"]["labels"], TRAP_SIZE)
    best = clusters_of(["".join(x) for x in TRAP["oracle"]["bestCutAtK"]["clusters"]], TRAP_SIZE)
    names = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev"}
    scene_graph(fr, TRAP_POS, TRAPE, best if alt else greedy, TRAP_SIZE, 3, 1.0, hue=FHUE, names=names, size_tags=True)
    col = TEAL if alt else ROSE
    fr.text(L("Ada · Cai ｜ Ben · Dev：两辆，每辆 3 座", "Ada · Cai | Ben · Dev: two taxis, 3 seats each") if alt else L("贪心：三辆", "greedy: three taxis"),
            1400, 420, 30, col, 1.0, anchor="c", role="serif", glow=0.3 * pulse(c.T, PHRASE, 0.4))
    if c.on(1):
        fr.text(L("两辆其实装得下", "two taxis do fit"), 1400, 500, 26, GOLD, c.p(1), anchor="c")


def p_stuck(fr, c):
    best = clusters_of(["".join(x) for x in TRAP["oracle"]["bestCutAtK"]["clusters"]], TRAP_SIZE)
    names = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev"}
    scene_graph(fr, TRAP_POS, TRAPE, best, TRAP_SIZE, 3, 0.55, hue=FHUE, names=names)
    a = c.p(0)
    fr.text(L("停下了 ≠ 没有答案", "stopped ≠ no answer"), 1400, 400, 40, GOLD, a, anchor="c", role="serif", glow=0.3 * a)
    if c.on(1):
        fr.text(L("第一步拿走了最大的 10，贪心不会回头", "the first step took the biggest 10, and greedy never goes back"), 1400, 480, 24, IVORY, c.p(1), anchor="c")


def p_breath(fr, c):
    a = c.p(0, 1.4)
    fr.text(L("装不下，还是走错了路？", "Impossible, or the wrong path?"), W / 2, 500, 52, GOLD, a, anchor="c", role="serif", glow=0.25 * a)


def p_bikes(fr, c):
    ev = SUB["run"]["events"]
    landed_ = c.T >= FILL3[0]
    if c.on(2) and landed_:
        st = clusters_of(["".join(x) for x in SUB["oracle"]["bestCutAtK"]["clusters"]], ONES)
    else:
        st = ev[-1]["after"] if c.on(1) else (ev[1]["after"] if c.on(0) else ev[0]["after"])
    names = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev"}
    scene_graph(fr, SUB_POS, SUBE, st, ONES, 2, 1.0, hue=FHUE, names=names)
    panel(fr, 1060, 250, 660, 360, c.p(0), L("第二天 · 双人自行车", "DAY TWO · TANDEM BIKES"))
    fr.text(L("贪心：Ada · Ben 最要好（10），先一辆", "greedy: Ada · Ben are closest (10), so first"), 1090, 340, 24, TEAL, c.p(0))
    if c.on(1):
        fr.text(L("Cai · Dev 只能一辆", "Cai · Dev take the other"), 1090, 400, 24, BLUE, c.p(1))
        fr.text(L("拆散的交情 9 + 9 = 18", "friendship split: 9 + 9 = 18"), 1090, 460, 26, ROSE, c.p(1), role="mono")
    if c.on(2) and landed_:
        a = landed(c.T, FILL3, len(FILL3) - 1)
        fr.text(L("换一种：Ada · Cai ｜ Ben · Dev", "another way: Ada · Cai | Ben · Dev"), 1090, 520, 24, GOLD, a)
        fr.text(L("拆散 10 + 1 = 11", "split: 10 + 1 = 11"), 1090, 575, 26, TEAL, a, role="mono", glow=0.3 * a)


def p_three(fr, c):
    cards = [(L("装不下", "Impossible"), L("下界：⌈5 ÷ 2⌉ = 3 > 2", "bound: ⌈5 ÷ 2⌉ = 3 > 2"), L("谁来都做不到", "no one can do it"), ROSE),
             (L("走错了路", "Stuck"), L("贪心三辆，其实两辆够", "greedy: 3, yet 2 fit"), L("停下 ≠ 无解", "stopped ≠ no answer"), AMBER),
             (L("不是最好", "Not the best"), "18  vs  11", L("合法 ≠ 最优", "legal ≠ best"), BLUE)]
    for i, (h1, h2, h3, col) in enumerate(cards):
        if not c.on(i):
            continue
        a = c.p(i)
        x = 300 + i * 460
        fr.rect(x, 300, 400, 380, fill=PANEL_BG, stroke=col, width=1.4, alpha=0.95 * a, r=10, screen=True)
        fr.text(f"0{i + 1}", x + 40, 370, 24, col, a, role="mono")
        fr.text(h1, x + 200, 460, 40, col, a, anchor="c", role="serif")
        fr.text(h2, x + 200, 540, 22, IVORY, a, anchor="c", role="mono" if i == 2 else "sans")
        fr.text(h3, x + 200, 610, 24, MUTED, a, anchor="c")


CHIP = [(i, j, 1 + ((i * 7 + j * 3) % 4 == 0) + ((i * 5 + j) % 9 == 0)) for i in range(10) for j in range(6)]


def p_chip(fr, c):
    a = c.p(0, 0.8)
    substrate(fr, 0.6 * a)
    lit = clamp((c.T - FILL4[0]) / 2.0) if c.T >= FILL4[0] else 0
    regions = [(370, 260, 600, 520, TEAL), (990, 260, 600, 520, BLUE)]
    for x, y, w, h, col in regions:
        fr.rect(x, y, w, h, stroke=col, width=1.6, alpha=(0.35 + 0.6 * lit) * a, r=6, screen=True, dash=[10, 6])
    for i, j, s in CHIP:
        x = 400 + i * 112 + (60 if i >= 5 else 0)
        y = 300 + j * 80
        col = TEAL if i < 5 else BLUE
        fr.rect(x, y, 34 * s, 40, fill=NODE_BG, stroke=col if lit > (i * 6 + j) / 60 else "#3d5d64", width=1.6, alpha=a, r=3)
    if lit > 0.5:
        fr.text(L("每块区域：面积有上限", "each region: a limit on area"), W / 2, 840, 26, GOLD, lit, anchor="c")


def p_outro(fr, c):
    a0 = c.p(0, 1.2) * (1 - 0.6 * c.p(3))
    lines = [(L("合法，不等于完成", "Legal is not the same as done"), TEAL, 0),
             (L("完成，不等于最好", "Done is not the same as best"), TEAL, 1),
             (L("停下时，说清楚是哪一种", "When it stops, say which it is"), GOLD, 2)]
    for s, col, k in lines:
        if c.on(k):
            fr.text(s, W / 2, 380 + k * 90, 40, col, c.p(k, 1.2) * (1 - 0.6 * c.p(3)), anchor="c", role="serif")
    if c.on(3):
        a = c.p(3, 1.4)
        fr.text(L("如果不合并，而是让每个节点改“标签”呢？", "What if nodes don't merge, but change labels?"), W / 2, 720, 40, GOLD, a, role="serif", anchor="c", glow=0.3 * a)


def p_end(fr, c):
    if not c.on(1):
        a = c.p(0, 1.0)
        scene_graph(fr, fit(G01P, (300, 260, 900, 740)), G01E, CAP2["run"]["events"][-1]["after"], ONES, 2, a, hue={"AB": TEAL, "DE": BLUE})
        fr.text(L("改容量 · 改节点大小 · 看诊断怎么说", "change the capacity · change a size · read the diagnosis"), 1360, 500, 26, GOLD, a, anchor="c")
    else:
        credits(fr, c, [(L("装得下吗", "Does It Fit?"), GOLD, 44),
                        (L("Learning Clustering · Module 04 · 容量约束凝聚聚类", "Learning Clustering · Module 04 · Size-constrained agglomerative clustering"), IVORY, 24),
                        (L("原作 GateUltra（Issue #3）· greedy_trap 与 suboptimal 两张图来自原作", "Original work by GateUltra (Issue #3) · the greedy_trap and suboptimal graphs come from it"), MUTED, 20),
                        (L("所有结果由本课程引擎 site/engines/merge.js 与穷举 oracle 计算", "Every result is computed by this course's engine, site/engines/merge.js, and the exhaustive oracle"), MUTED, 20),
                        (MUSIC_LINE, MUTED, 18)], k=1)


STORY = Film(
    "story", "popular", L("装得下吗", "Does It Fit?"), None, BRAND, poster_at=36.5, music=TRACK, seed=4,
    why=L("同样的五个朋友、同样的合并规则，只是座位有限：双座车装不下五个人（不可能），两把大提琴让出租车走进死胡同（卡住），双人自行车上最要好的一对反而拆散最多（不是最好）。",
          "The same five friends and the same merge rule, but seats are limited: two-seaters cannot take five in two cars (impossible), two cellos lead the taxis into a dead end (stuck), and on tandem bikes the closest pair splits the most (not the best)."),
    scenes=[
        Scene("p-open", p_open, [Beat(L("还是那五个朋友，还是那条规则。", "The same five friends, the same rule."), 4.8),
                                 Beat(L("这一次，每辆车只有两个座位。", "This time, every car has only two seats."), 4.6)],
              chapter=L("序 · 座位", "PROLOGUE · SEATS"), until=S["intro_end"]),
        Scene("p-ask", p_ask, [Beat(L("合得来的坐一起——", "Friends ride together —"), 2.6),
                               Beat(L("可是，装得下吗？", "but does it fit?"), 3.0)],
              until=S["groove"]),
        Scene("p-rule", p_rule, [Beat(L("规则多了一句：合并前，先看装不装得下。", "The rule gains one line: before merging, check that it fits."), 5.2),
                                 Beat(L("装不下的候选，再合得来也划掉。", "A candidate that does not fit is crossed out, however close."), 4.4),
                                 Beat(L("在剩下的里面，选最合得来的。", "Among the rest, take the closest pair."), 3.6)],
              until=S["roll"]),
        Scene("p-title", p_title, [Beat(None, 4.5)], fade=False, until=37.0),
        Scene("p-cars", p_cars, [Beat(L("Ada 和 Ben 先上了一辆双座车。", "Ada and Ben take the first two-seater."), 4.0),
                                 Beat(L("加上 Cai 就是三人，装不下；Dev、Eva 上第二辆。", "Three with Cai won't fit; Dev and Eva take the second."), 6.0),
                                 Beat(L("Cai 只能单独一辆。", "Cai has to ride alone."), 2.6)],
              chapter=L("一 · 装不下", "I · IT DOES NOT FIT"), until=S["fill1_end"]),
        Scene("p-bound", p_bound, [Beat(L("是规则太笨吗？数一数座位。", "Is the rule too dumb? Count the seats."), 3.6),
                                   Beat(L("五个人，每辆两个座位。", "Five people, two seats a car."), 3.6),
                                   Beat(L("五除以二，向上取整：至少三辆。两辆，谁来都做不到。", "Five divided by two, rounded up: at least three. Two cars is impossible for anyone."), 7.4)],
              until=S["fill2_end"]),
        Scene("p-cello", p_cello, [Beat(L("三座出租车：两人各带大提琴，占两座。", "Three-seat taxis: Ada and Ben carry cellos, two seats each."), 4.6),
                                   Beat(L("两个好朋友先同车。", "The two best friends ride first."), 2.8),
                                   Beat(L("再加谁都超座：三辆车。", "Anyone more overflows: three taxis."), 3.0)],
              chapter=L("二 · 走错了路", "II · THE WRONG PATH"), until=S["phrase"]),
        Scene("p-flip", p_flip, [Beat(L("可是，Ada 配 Cai，Ben 配 Dev——", "But Ada with Cai, Ben with Dev —"), 3.6),
                                 Beat(L("两辆车，刚好坐满。", "two taxis, exactly full."), 3.0)],
              until=89.0),
        Scene("p-stuck", p_stuck, [Beat(L("停下了，不等于没有答案。", "Stopping does not mean there is no answer."), 3.4),
                                   Beat(L("贪心拿走最大的交情，从不回头。", "Greedy grabbed the biggest bond and never went back."), 4.2)],
              until=S["breath"]),
        Scene("p-breath", p_breath, [Beat(None, 4.6)], until=S["reentry"]),
        Scene("p-bikes", p_bikes, [Beat(L("第二天骑双人车，Ada、Ben 先一辆。", "Day two, tandem bikes: Ada and Ben share one."), 4.8),
                                   Beat(L("Cai、Dev 一辆：拆散两份 9，共 18。", "Cai and Dev take the other: two 9s split, 18 in all."), 4.8),
                                   Beat(L("交换搭档：只拆散 11。", "Swap partners: only 11 is split."), 4.0)],
              chapter=L("三 · 不是最好", "III · NOT THE BEST"), until=S["fill3_end"]),
        Scene("p-three", p_three, [Beat(L("三个故事，三种结局。", "Three stories, three endings."), 3.0),
                                   Beat(L("装不下：谁来都做不到。", "Impossible: no one can do it."), 3.6),
                                   Beat(L("走错了路：有答案，贪心没找到。", "Stuck: an answer exists, and greedy missed it."), 4.0),
                                   Beat(L("不是最好：合法，但还能更好。", "Not the best: legal, but it could be better."), 3.8)],
              until=S["fill4"]),
        Scene("p-chip", p_chip, [Beat(L("芯片上，每块区域能放的面积有限，聚类也要装得下。", "On a chip, each region holds only so much area; clusters must fit too."), 6.4)],
              until=141.5),
        Scene("p-outro", p_outro, [Beat(L("合法，不等于完成。", "Legal is not the same as done."), 6.0),
                                   Beat(L("完成，不等于最好。", "Done is not the same as best."), 6.0),
                                   Beat(L("停下的时候，说清楚是哪一种。", "When it stops, say which one it is."), 7.0),
                                   Beat(L("如果节点不合并，只是改“标签”呢？下一章见。", "What if nodes don't merge, only change labels? See the next module."), 8.0)],
              chapter=L("尾声", "CODA"), until=S["quiet"]),
        Scene("p-end", p_end, [Beat(L("下面的实验里，改容量、改大小，看诊断怎么说。", "In the lab below, change the capacity or a size and read the diagnosis."), 6.0),
                               Beat(None, 10.0)], until=S["end"]),
    ])


# ====================================================================== concise film
P5 = fit(G01P, (240, 260, 860, 740))
HUE = {"AB": TEAL, "ABC": TEAL, "DE": BLUE, "CDE": BLUE, "CD": AMBER, "AC": TEAL, "BD": BLUE}


def k_title(fr, c):
    title_card(fr, L("容量约束凝聚聚类", "Size-Constrained Agglomerative"), L("SIZE-CONSTRAINED AGGLOMERATIVE  ·  精讲", "THE ESSENTIALS"), c.p(0, 1.2), kicker="MODULE 04")


def k_problem(fr, c):
    scene_graph(fr, P5, G01E, CAP2["run"]["events"][-1]["after"], ONES, 2, c.p(0, 1.0), hue=HUE)
    rows = [("count", "3", IVORY), ("capacityCompliant", L("是", "yes"), TEAL), ("targetReached", L("否", "no"), ROSE), ("stopReason", "capacity-blocked", GOLD)]
    if c.on(1):
        report_card(fr, 1040, 260, rows if c.on(2) else rows[:1], c.p(1), L("容量 2、K = 2 的报告", "THE REPORT AT CAPACITY 2, K = 2"), w=660)
    if c.on(3):
        fr.paragraph(L("四项互相独立：合法不等于达到 K。", "The four are independent: legal is not the same as reaching K."), 1040, 640, 26, 660, GOLD, c.p(3))


def k_fork(fr, c):
    ev2 = CAP2["run"]["events"]
    left = CAP3["run"]["events"][-1]["after"]
    right = ev2[-1]["after"] if c.on(2) else ev2[1]["after"]
    pl, pr = fit(G01P, (180, 330, 760, 700)), fit(G01P, (1100, 330, 1680, 700))
    scene_graph(fr, pl, G01E, left, ONES, 3, c.p(0), hue=HUE, r=32)
    scene_graph(fr, pr, G01E, right, ONES, 2, c.p(0), hue=HUE, r=32, blocked=("C",) if c.on(1) else ())
    fr.text(L("容量 3", "CAPACITY 3"), 470, 230, 28, TEAL, c.p(0), anchor="c", spacing=2)
    fr.text(L("容量 2", "CAPACITY 2"), 1390, 230, 28, GOLD, c.p(0), anchor="c", spacing=2)
    fr.text(L("ABC | DE · cut 3 · 达到 K", "ABC | DE · cut 3 · K reached"), 470, 840, 24, TEAL, c.p(0), anchor="c")
    if c.on(1):
        fr.text(L("AB + C = 3 > 2：被阻止，改选 D–E", "AB + C = 3 > 2: blocked, D–E instead"), 1390, 885, 22, ROSE, c.p(1), anchor="c")
    if c.on(2):
        fr.text(L("AB | C | DE · cut 8 · 未达到 K", "AB | C | DE · cut 8 · K not reached"), 1390, 840, 24, GOLD, c.p(2), anchor="c")


def k_bound(fr, c):
    a = c.p(0)
    panel(fr, 300, 250, 1320, 300, a, L("下界", "THE LOWER BOUND"))
    fr.text(L("至少需要的簇数", "clusters needed, at least"), 360, 360, 28, MUTED, a)
    fr.text("⌈ Σ s(v) ÷ C ⌉", 1560, 362, 40, IVORY, a, role="mono", anchor="r")
    if c.on(1):
        fr.text("G01, C = 2:", 360, 470, 28, MUTED, c.p(1), role="mono")
        fr.text("⌈ 5 ÷ 2 ⌉ = 3  >  K = 2", 1560, 472, 40, ROSE, c.p(1), role="mono", anchor="r")
    if c.on(2):
        fr.paragraph(L("所以容量 2 下分成 2 簇不可能：贪心停下没有错。", "So 2 clusters at capacity 2 is impossible: greedy stopping is not a mistake."), 300, 650, 30, 1320, GOLD, c.p(2), role="serif")
    if c.on(3):
        fr.paragraph(L("但下界只能证明“不可能”，不能证明“可能”。", "But a bound can only prove “impossible”, never “possible”."), 300, 750, 26, 1320, IVORY, c.p(3))


def k_trap(fr, c):
    ev = TRAP["run"]["events"]
    pos = fit({k: tuple(v) for k, v in TRAP_G["positions"].items()}, (200, 380, 900, 640))
    if c.on(3):
        st = clusters_of(["".join(x) for x in TRAP["oracle"]["bestCutAtK"]["clusters"]], TRAP_SIZE)
    else:
        st = ev[-1]["after"] if c.on(2) else (ev[1]["after"] if c.on(1) else ev[0]["after"])
    scene_graph(fr, pos, TRAPE, st, TRAP_SIZE, 3, 1.0, hue=HUE, size_tags=True, blocked=("A", "B") if c.on(2) and not c.on(3) else ())
    panel(fr, 1060, 250, 660, 420, c.p(0), L("greedy_trap · 容量 3 · K = 2", "greedy_trap · CAPACITY 3 · K = 2"))
    fr.text(L("下界 ⌈6 ÷ 3⌉ = 2：允许两簇", "bound ⌈6 ÷ 3⌉ = 2: two are allowed"), 1090, 340, 24, IVORY, c.p(0))
    if c.on(1):
        fr.text(L("贪心先合 C–D（10）", "greedy merges C–D (10) first"), 1090, 400, 24, AMBER, c.p(1))
    if c.on(2):
        fr.text(L("CD + A、CD + B 都是 4 > 3：停在 3 簇", "CD + A and CD + B are 4 > 3: stops at 3"), 1090, 460, 24, ROSE, c.p(2))
    if c.on(3):
        fr.text(L("穷举：AC | BD，大小 3、3，cut 10", "exhaustive: AC | BD, sizes 3 and 3, cut 10"), 1090, 520, 24, TEAL, c.p(3))
        fr.text(L("总体可行，但贪心卡住", "feasible, but greedy is stuck"), 1090, 590, 28, GOLD, c.p(3), role="serif")


def k_sub(fr, c):
    pl, pr = fit({k: tuple(v) for k, v in SUB_G["positions"].items()}, (240, 330, 680, 690)), fit({k: tuple(v) for k, v in SUB_G["positions"].items()}, (1180, 330, 1620, 690))
    greedy = SUB["run"]["events"][-1]["after"]
    best = clusters_of(["".join(x) for x in SUB["oracle"]["bestCutAtK"]["clusters"]], ONES)
    scene_graph(fr, pl, SUBE, greedy, ONES, 2, c.p(0), hue=HUE, r=34)
    fr.text(L("贪心：先合 A–B（10）", "greedy: A–B (10) first"), 460, 240, 26, IVORY, c.p(0), anchor="c")
    fr.text("cut 9 + 9 = 18", 460, 860, 28, ROSE, c.p(1), anchor="c", role="mono")
    if c.on(2):
        scene_graph(fr, pr, SUBE, best, ONES, 2, c.p(2), hue=HUE, r=34)
        fr.text(L("穷举最优：AC | BD", "exhaustive optimum: AC | BD"), 1400, 240, 26, IVORY, c.p(2), anchor="c")
        fr.text("cut 10 + 1 = 11", 1400, 860, 28, TEAL, c.p(2), anchor="c", role="mono")
    if c.on(3):
        fr.text(L("都合法、都达到 K：合法但非最优", "both legal, both reach K: legal but not optimal"), W / 2, 920 - 120, 26, GOLD, c.p(3), anchor="c")


def k_uneven(fr, c):
    sizes = {n: 2 if n == "A" else 1 for n in "ABCDE"}
    ev = UNEVEN["events"]
    st = ev[-1]["after"] if c.on(2) else (ev[1]["after"] if c.on(1) else ev[0]["after"])
    scene_graph(fr, P5, G01E, st, sizes, 3, 1.0, hue=HUE, size_tags=True, blocked=("C",) if c.on(1) and not c.on(2) else ())
    panel(fr, 1040, 260, 660, 330, c.p(0), L("把 A 的大小改成 2 · 容量 3", "SET A'S SIZE TO 2 · CAPACITY 3"))
    fr.text(L("A–B 合并后大小已是 3", "after A–B the size is already 3"), 1070, 350, 24, IVORY, c.p(0))
    if c.on(1):
        fr.text(L("AB + C = 4 > 3：被阻止", "AB + C = 4 > 3: blocked"), 1070, 410, 24, ROSE, c.p(1))
    if c.on(2):
        fr.text(L("AB | CDE · cut 5（原来 ABC | DE · cut 3）", "AB | CDE · cut 5 (was ABC | DE · cut 3)"), 1070, 480, 24, GOLD, c.p(2))
        fr.text(L("容量按面积算，不按个数算", "capacity counts area, not nodes"), 1070, 545, 24, TEAL, c.p(2))


def k_take(fr, c):
    items = [(L("先筛合法（合并后 ≤ C），再选亲和度最大", "Filter for legality (merged size ≤ C), then take the highest affinity"), TEAL),
             (L("四项分开报告：count、合法、达到 K、停止原因", "Report four items: count, legal, K reached, stop reason"), GOLD),
             (L("下界 ⌈Σs / C⌉ > K：不可能，不是贪心的错", "Bound ⌈Σs / C⌉ > K: impossible, not greedy's fault"), ROSE),
             (L("卡住 ≠ 不可能；合法 ≠ 最优：用穷举对照", "Stuck ≠ impossible; legal ≠ optimal: compare with search"), BLUE)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 260 + i * 120
            fr.rect(220, y, 1480, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 58, 28, col, a, role="mono")
            fr.text(s, 360, y + 58, 30, IVORY, a)


CONCISE = Film(
    "concise", "concise", L("精讲：先筛合法，再选最大", "The essentials"), None, BRAND, poster_at=30.0, music="score:steady", seed=24,
    why=L("只讲必须掌握的：四个报告项、先筛合法再选最大、下界、greedy_trap 的卡住、suboptimal 的非最优，以及节点大小。",
          "Only what you must know: the four report items, filtering before choosing, the lower bound, getting stuck in greedy_trap, the suboptimal result, and node sizes."),
    scenes=[
        Scene("k00-title", k_title, [Beat(None, 3.0)]),
        Scene("k01-problem", k_problem, [Beat(L("规则和 Module 03 一样，只多一条：每个簇的大小之和不能超过容量 C。", "The rule is Module 03's, plus one line: a cluster's total size may not exceed the capacity C."), 5.0),
                                         Beat(L("G01 在容量 2、K = 2 时停在 3 簇。", "At capacity 2 and K = 2, G01 stops at 3 clusters."), 3.0),
                                         Beat(L("报告：合法，但没有达到 K，停止原因是 capacity-blocked。", "The report: legal, but K is not reached; the stop reason is capacity-blocked."), 4.4),
                                         Beat(L("这四项互相独立，要分开写。", "The four are independent; report them separately."), 3.0)],
              chapter=L("问题", "THE PROBLEM")),
        Scene("k02-fork", k_fork, [Beat(L("同一张图：容量 3 时，AB 加 C 是 3，合法，得到 ABC | DE。", "One graph: at capacity 3, AB plus C is 3, legal, giving ABC | DE."), 4.6),
                                   Beat(L("容量 2 时，亲和度最大的 AB–C 被阻止，改选 D–E。", "At capacity 2, the highest-affinity AB–C is blocked, so D–E instead."), 4.4),
                                   Beat(L("之后两个候选都是 3：停在 AB | C | DE，cut 8。", "After that both candidates are 3: it stops at AB | C | DE, cut 8."), 4.2)],
              chapter=L("先筛合法", "FILTER FIRST")),
        Scene("k03-bound", k_bound, [Beat(L("这是贪心的错吗？先算下界。", "Is that greedy's fault? First, the lower bound."), 2.8),
                                     Beat(L("总大小 5，每簇最多 2：至少 3 簇。", "Total size 5, at most 2 per cluster: at least 3 clusters."), 3.4),
                                     Beat(L("K = 2 根本不可能，任何算法都做不到。", "K = 2 is impossible; no algorithm can do it."), 3.2),
                                     Beat(L("但下界只能证明不可能，不能证明可能。", "But a bound only proves impossible, never possible."), 3.4)],
              chapter=L("不可能", "IMPOSSIBLE")),
        Scene("k04-trap", k_trap, [Beat(L("原作者的 greedy_trap：A、B 大小 2，容量 3，下界允许两簇。", "The original author's greedy_trap: A and B have size 2, capacity 3, and the bound allows two clusters."), 5.0),
                                   Beat(L("贪心先合并最大的 C–D。", "Greedy merges the biggest, C–D, first."), 2.6),
                                   Beat(L("之后 A、B 都放不进：停在 3 簇。", "Then neither A nor B fits: it stops at 3 clusters."), 3.0),
                                   Beat(L("穷举却找到 AC | BD：总体可行，但贪心卡住。", "Yet exhaustive search finds AC | BD: feasible, but greedy is stuck."), 4.2)],
              chapter=L("卡住", "STUCK")),
        Scene("k05-sub", k_sub, [Beat(L("suboptimal 图：贪心先合并 A–B，10 最大。", "The suboptimal graph: greedy merges A–B first, the largest at 10."), 3.6),
                                 Beat(L("两条 9 都留在 cut 里：18。", "Both 9s stay in the cut: 18."), 2.6),
                                 Beat(L("合法的 AC | BD 只切断 10 和 1：11。", "The legal AC | BD cuts only 10 and 1: 11."), 3.4),
                                 Beat(L("都合法、都达到 K，只是贪心不是最优。", "Both legal, both reach K; greedy just isn't optimal."), 3.2)],
              chapter=L("非最优", "NOT OPTIMAL")),
        Scene("k06-uneven", k_uneven, [Beat(L("节点大小也会改变结局：把 A 的大小改成 2。", "Node sizes change the ending too: set A's size to 2."), 3.8),
                                       Beat(L("A–B 之后已满，C 放不进。", "After A–B it is full, and C does not fit."), 2.8),
                                       Beat(L("结果变成 AB | CDE，cut 5。容量按面积算。", "The result becomes AB | CDE, cut 5. Capacity counts area."), 4.0)],
              chapter=L("面积", "AREA")),
        Scene("k07-take", k_take, [Beat(L("记住四点。", "Four things to keep."), 1.4),
                                   Beat(L("先筛合法再选最大；四项分开报告；", "Filter first, then take the largest; report four items;"), 3.0),
                                   Beat(L("下界大于 K 就是不可能；", "a bound above K means impossible;"), 2.4),
                                   Beat(L("卡住和非最优，要用穷举对照。下面的实验里试一试。", "stuck and not optimal need a comparison with search. Try it in the lab below."), 4.6)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])


# ====================================================================== advanced film
def a_title(fr, c):
    title_card(fr, L("容量约束凝聚聚类", "Size-Constrained Agglomerative"), L("进阶：可行性、最优性与代价", "IN DEPTH: FEASIBILITY, OPTIMALITY AND COST"), c.p(0, 1.2), kicker="MODULE 04")


def a_filter(fr, c):
    ev = CAP2["run"]["events"]
    st = ev[1]["after"]
    pl = fit(G01P, (200, 330, 760, 690))
    scene_graph(fr, pl, G01E, st if not c.on(3) else ev[-1]["after"], ONES, 2, 1.0, hue=HUE, r=32, blocked=("C",) if c.on(1) and not c.on(3) else ())
    panel(fr, 1000, 250, 720, 230, c.p(0), L("错误写法：先选最大，再检查", "WRONG: PICK THE LARGEST, THEN CHECK"))
    fr.text(L("最大的是 AB–C（5）→ 超容量 → 停", "largest is AB–C (5) → over capacity → stop"), 1030, 350, 24, ROSE, c.p(1))
    fr.text(L("停在 4 簇，cut 13", "stops at 4 clusters, cut 13"), 1030, 410, 26, ROSE, c.p(1), role="mono")
    if c.on(2):
        a = c.p(2)
        panel(fr, 1000, 520, 720, 230, a, L("正确写法：先筛合法，再选最大", "RIGHT: FILTER, THEN TAKE THE LARGEST"))
        fr.text(L("合法里最大的是 D–E（5）→ 合并", "largest legal is D–E (5) → merge"), 1030, 620, 24, TEAL, a)
        fr.text(L("停在 3 簇，cut 8", "stops at 3 clusters, cut 8"), 1030, 680, 26, TEAL, a, role="mono")


def a_bound(fr, c):
    pos = {"X": (420, 360), "Y": (660, 560), "Z": (900, 360)}
    sizes = TRIO["sizes"]
    clusters = clusters_of(["X", "Y", "Z"], sizes)
    scene_graph(fr, pos, TRIO["edges"], clusters, sizes, 3, c.p(0), r=40, size_tags=True)
    panel(fr, 1100, 250, 620, 420, c.p(0), L("三间双人房 · 容量 3 · K = 2", "THREE TWIN ROOMS · CAPACITY 3 · K = 2"))
    fr.text(L("下界 ⌈6 ÷ 3⌉ = 2：没有排除 2 簇", "bound ⌈6 ÷ 3⌉ = 2: 2 clusters not ruled out"), 1130, 340, 24, IVORY, c.p(0))
    if c.on(1):
        fr.text(L("任意两个放一起：2 + 2 = 4 > 3", "any two together: 2 + 2 = 4 > 3"), 1130, 410, 24, ROSE, c.p(1))
        fr.text(L("穷举：最少 3 簇", "exhaustive: at least 3"), 1130, 470, 24, ROSE, c.p(1))
    if c.on(2):
        fr.text("infeasible-by-search", 1130, 550, 26, GOLD, c.p(2), role="mono")
        fr.paragraph(L("下界满足 ≠ 可行。判断能否装下，本身就是装箱问题。", "Meeting the bound ≠ feasible. Deciding whether it fits is bin packing itself."), 1130, 600, 22, 560, MUTED, c.p(2))


def a_bell(fr, c):
    panel(fr, 260, 230, 1400, 470, c.p(0), L("把 n 个节点分组：一共有多少种分法", "WAYS TO GROUP n NODES"))
    rows = [(5, L("G01：5 个节点", "G01: 5 nodes")), (10, L("本课程穷举的上限", "this course's exhaustive limit")), (15, ""), (20, "")]
    mx = math.log10(BELL[20])
    for i, (n, lab) in enumerate(rows):
        if not c.on(min(i, 2)):
            continue
        a = c.p(min(i, 2), delay=0.4 * (i - 2) if i >= 2 else 0)
        y = 330 + i * 90
        fr.text(f"n = {n}", 320, y, 28, MUTED, a, role="mono")
        fr.text(f"{BELL[n]:,}", 1600, y, 30, GOLD if n <= 10 else ROSE, a, role="mono", anchor="r")
        bar(fr, 520, y - 14, 700, 12, math.log10(BELL[n]) / mx, GOLD if n <= 10 else ROSE, a)
        if lab:
            fr.text(lab, 520, y + 30, 18, MUTED, a)
    if c.on(3):
        fr.paragraph(L(f"G01 的 {BELL[5]} 种分法里，容量 2 下合法的有 {CAP2['oracle']['legalPartitions']} 种。规模一大，只能靠启发式或数学规划。",
                       f"Of G01's {BELL[5]} groupings, {CAP2['oracle']['legalPartitions']} are legal at capacity 2. At scale you need heuristics or mathematical programming."),
                     260, 780, 26, 1400, IVORY, c.p(3))


def a_samek(fr, c):
    pos = fit({k: tuple(v) for k, v in TRAP_G["positions"].items()}, (200, 380, 900, 640))
    greedy = clusters_of(TRAP["run"]["result"]["labels"], TRAP_SIZE)
    best = clusters_of(["".join(x) for x in TRAP["oracle"]["bestCutAtK"]["clusters"]], TRAP_SIZE)
    scene_graph(fr, pos, TRAPE, best if c.on(1) else greedy, TRAP_SIZE, 3, 1.0, hue=HUE, size_tags=True)
    rows = [[L("分组", "Grouping"), L("簇数", "Clusters"), "cut"], ["A | B | CD", "3", "8"], ["AC | BD", "2", "10"]]
    table(fr, 1060, 330, [300, 200, 140], [[tr(x) for x in r] for r in rows[:2 + c.on(1)]], c.p(0), size=28, lh=64,
          colors={(1, 2): ROSE, (2, 2): TEAL})
    if c.on(2):
        fr.paragraph(L("贪心的 cut 反而更小——因为它多了一个簇。", "Greedy's cut is smaller, because it has one more cluster."), 1060, 590, 26, 640, GOLD, c.p(2))
    if c.on(3):
        fr.paragraph(L("cut 只能在相同的簇数下比较。", "Compare cuts only at the same number of clusters."), 1060, 690, 26, 640, IVORY, c.p(3))


def a_gap(fr, c):
    panel(fr, 260, 230, 1400, 420, c.p(0), L("把 suboptimal 放大：A–B = M，A–C = B–D = M − 1，C–D = 1", "SCALE suboptimal: A–B = M, A–C = B–D = M − 1, C–D = 1"))
    rows = [["M", L("贪心 cut", "greedy cut"), L("最优 cut", "optimal cut"), L("比值", "ratio")]] + [[str(m), f"{g:,}", f"{o:,}", f"{g / o:.2f}"] for m, g, o in FAMILY]
    shown = 1 + sum(c.on(k) for k in (1, 2, 3))
    table(fr, 340, 340, [240, 360, 360, 240], [[tr(x) for x in r] for r in rows[:shown]], c.p(0), size=28, lh=64,
          colors={(i, 1): ROSE for i in range(1, 4)} | {(i, 2): TEAL for i in range(1, 4)})
    if c.on(4):
        fr.paragraph(L("贪心 = 2(M − 1)，最优 = M + 1：差距逼近 2 倍。合法，却可以差很多。",
                       "Greedy = 2(M − 1), optimal = M + 1: the gap approaches 2×. Legal, yet far off."), 260, 740, 28, 1400, GOLD, c.p(4))


def a_area(fr, c):
    sizes = {n: 2 if n == "A" else 1 for n in "ABCDE"}
    pl = fit(G01P, (200, 330, 760, 690))
    st = UNEVEN["events"][-1]["after"] if c.on(1) else CAP3["run"]["events"][-1]["after"]
    scene_graph(fr, pl, G01E, st, sizes if c.on(1) else ONES, 3, 1.0, hue=HUE, r=32, size_tags=c.on(1))
    rows = [[L("大小", "Sizes"), L("结果", "Result"), "cut"], [L("都是 1", "all 1"), "ABC | DE", "3"], [L("A = 2", "A = 2"), "AB | CDE", "5"]]
    table(fr, 1000, 330, [240, 300, 120], [[tr(x) for x in r] for r in rows[:2 + c.on(1)]], c.p(0), size=28, lh=64, colors={(2, 2): GOLD})
    if c.on(2):
        fr.paragraph(L("真实单元面积差别很大：容量按面积之和算。把所有单元当成 1，答案可能是错的。",
                       "Real cell areas differ widely: capacity counts the sum of areas. Treat every cell as 1 and the answer may be wrong."), 1000, 600, 26, 720, IVORY, c.p(2))


def a_summary(fr, c):
    items = [(L("先筛合法再选最大；先选再查会提前停下", "Filter, then choose; choosing first stops too early"), TEAL),
             (L("下界只能证不可能；满足下界也可能装不下", "A bound only proves impossible; meeting it may still not fit"), ROSE),
             (L("穷举随 n 爆炸：只用于 10 个节点以内的对照", "Exhaustive search explodes with n: only a check at 10 nodes or fewer"), GOLD),
             (L("cut 只在相同簇数下比较", "Compare cuts only at the same number of clusters"), GOLD),
             (L("合法的贪心结果可以接近最优的 2 倍", "A legal greedy result can approach twice the optimum"), ROSE),
             (L("容量按面积之和，不按个数", "Capacity counts summed area, not nodes"), TEAL)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 200 + i * 104
            fr.rect(220, y, 1480, 84, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 54, 26, col, a, role="mono")
            fr.text(s, 350, y + 54, 30, IVORY, a)


ADVANCED = Film(
    "advanced", "advanced", L("进阶：可行性、最优性与代价", "In depth: feasibility and optimality"), None, BRAND, poster_at=40.0, music="score:calm", seed=36,
    why=L("为什么必须先筛合法、下界能证明什么不能证明什么、穷举随规模爆炸、cut 只能在相同簇数下比较、合法的贪心结果离最优能有多远，以及面积不同时的容量。",
          "Why the filter must come first, what a bound can and cannot prove, how exhaustive search explodes, comparing cuts only at the same K, how far a legal greedy result can be from optimal, and capacity with unequal areas."),
    scenes=[
        Scene("a00-title", a_title, [Beat(None, 3.0)]),
        Scene("a01-filter", a_filter, [Beat(L("顺序很重要。错误的写法：先选亲和度最大的一对，再检查容量。", "Order matters. The wrong way: pick the highest-affinity pair, then check the capacity."), 5.4),
                                       Beat(L("G01 容量 2 的第二步，最大的 AB–C 超容量，于是停在 4 簇，cut 13。", "At step two of G01 at capacity 2, the largest, AB–C, is over capacity, so it stops at 4 clusters, cut 13."), 6.4),
                                       Beat(L("正确的写法先筛合法：D–E 仍可合并，停在 3 簇，cut 8。", "The right way filters first: D–E can still merge, and it stops at 3 clusters, cut 8."), 5.6),
                                       Beat(L("同一张图，只因顺序不同。", "Same graph; only the order differs."), 2.6)],
              chapter=L("一 · 先筛后选", "I · FILTER, THEN CHOOSE")),
        Scene("a02-bound", a_bound, [Beat(L("三间双人房：每个节点大小 2，容量 3，K = 2。下界是 2，没有排除。", "Three twin rooms: every node has size 2, capacity 3, K = 2. The bound is 2; nothing is ruled out."), 6.2),
                                     Beat(L("可是任意两个放一起都是 4，超过 3：至少 3 簇。", "Yet any two together make 4, over 3: at least 3 clusters."), 4.4),
                                     Beat(L("满足下界不等于可行。判断能不能装下，本身就是装箱问题。", "Meeting the bound is not feasibility. Deciding whether it fits is bin packing itself."), 5.4)],
              chapter=L("二 · 下界的边界", "II · WHAT A BOUND CAN'T SAY")),
        Scene("a03-bell", a_bell, [Beat(L("穷举有多贵？n 个节点的分组方式：", "How costly is exhaustive search? Ways to group n nodes:"), 3.4),
                                   Beat(L("5 个节点 52 种，10 个节点已经十一万多种。", "5 nodes, 52; 10 nodes, already over a hundred thousand."), 4.4),
                                   Beat(L("15 个、20 个节点，很快到几十万亿。", "15 and 20 nodes quickly reach tens of trillions."), 4.0),
                                   Beat(L("所以本课程只在 10 个节点以内用穷举做对照。", "So this course uses exhaustive search only as a check at 10 nodes or fewer."), 4.4)],
              chapter=L("三 · 穷举的代价", "III · THE COST OF SEARCH")),
        Scene("a04-samek", a_samek, [Beat(L("greedy_trap 上，贪心停在 3 簇，cut 8。", "On greedy_trap, greedy stops at 3 clusters, cut 8."), 3.6),
                                     Beat(L("可行的两簇方案 AC | BD，cut 10。", "The feasible two-cluster plan AC | BD has cut 10."), 3.6),
                                     Beat(L("贪心的 cut 反而更小，因为它多了一个簇。", "Greedy's cut is smaller, because it has one more cluster."), 3.8),
                                     Beat(L("cut 只能在相同的簇数下比较。", "Compare cuts only at the same number of clusters."), 3.2)],
              chapter=L("四 · 同一个 K", "IV · THE SAME K")),
        Scene("a05-gap", a_gap, [Beat(L("合法的贪心结果能差多远？把 suboptimal 图放大。", "How far off can a legal greedy result be? Scale the suboptimal graph."), 4.6),
                                 Beat(L("M = 10：18 对 11。", "M = 10: 18 versus 11."), 2.4),
                                 Beat(L("M = 100：198 对 101。", "M = 100: 198 versus 101."), 2.6),
                                 Beat(L("M = 1000：1998 对 1001。", "M = 1000: 1998 versus 1001."), 2.6),
                                 Beat(L("贪心是 2(M − 1)，最优是 M + 1：差距逼近两倍。", "Greedy is 2(M − 1), optimal M + 1: the gap approaches twice."), 4.6)],
              chapter=L("五 · 离最优多远", "V · HOW FAR FROM OPTIMAL")),
        Scene("a06-area", a_area, [Beat(L("全部大小为 1 时，容量 3 得到 ABC | DE，cut 3。", "With every size 1, capacity 3 gives ABC | DE, cut 3."), 3.8),
                                   Beat(L("只把 A 改成 2，结果变成 AB | CDE，cut 5。", "Change only A to 2, and the result becomes AB | CDE, cut 5."), 4.0),
                                   Beat(L("真实单元面积各不相同，容量必须按面积之和算。", "Real cells differ in area; capacity must count the sum of areas."), 4.4)],
              chapter=L("六 · 面积", "VI · AREA")),
        Scene("a07-summary", a_summary, [Beat(L("六点小结。", "Six things to keep."), 1.6)] + [Beat(None, 2.6) for _ in range(5)]
              + [Beat(L("下一章：节点不合并，而是改标签。", "Next: nodes don't merge; they change labels."), 3.0)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

FILMS = [STORY, CONCISE, ADVANCED]
ORDER = ["story", "concise", "advanced", "lab"]
