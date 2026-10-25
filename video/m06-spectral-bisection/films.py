"""Module 06 · Spectral bisection — the four films.

  story     popular science, cut to "We Never (Remix)": five friends line up along one line, joined by rubber bands
            that pull harder the thicker they are; where they settle is the Fiedler vector, and a pair of scissors
            tries every gap. A mirror flip, a group that falls apart, and the count 15, not 16.
  concise   the essentials: the problem with its balance window, building L = D − A, the quadratic form, the Fiedler
            order, the sweep 6 / 3 / 5 / 6, and the two warnings (sign flip, disconnected graph).
  advanced  the cut as a quadratic form on ±1 vectors, relaxing to real numbers, rounding by a sweep, why a window,
            repeated and zero eigenvalues, and numerics (residuals, solvers).
  lab       experiment walkthrough recorded from the real page (walkthrough.mjs → scripts/film/walkthrough.py).

Every value on G01 and on the disconnected graph is read from site/data/m06-spectral-bisection/traces.json, which
scripts/build-traces.mjs produces by running site/engines/spectral.js. The extra examples (the four-node ring,
quadratic forms of other vectors) run through the course's Python reference,
python/m06-spectral-bisection/reference.py, which tests/crosscheck.py checks against the engine.
"""
import importlib.util
import json
import math
from pathlib import Path

from cine import (W, H, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, CORAL, LILAC, SAGE, IVORY, MUTED, FAINT, DIM,
                  PANEL_BG, NODE_BG, clamp, ease, lerp, lerp2, title_card, panel, badge, bar, code_panel, table, graph, fit, pulse,
                  count_hits, substrate)
from hooks import chladni
from story import S, TRACK, INTRO_HITS, FILL1, FILL2, PHRASE, FILL3, FILL4, title_assemble, credits, MUSIC_LINE, landed

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m06-spectral-bisection/traces.json").read_text())
BRAND = L("Learning Clustering · Module 06 · 谱二分", "Learning Clustering · Module 06 · Spectral bisection")

_spec = importlib.util.spec_from_file_location("m06ref", ROOT / "python/m06-spectral-bisection/reference.py")
REF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REF)

NEUTRAL = "#9fbcbc"
IDS = T["g01"]["nodes"] if isinstance(T["g01"]["nodes"][0], str) else [n["id"] for n in T["g01"]["nodes"]]
E5 = [tuple(e) for e in T["g01"]["edges"]]
P5RAW = {k: tuple(v) for k, v in T["g01"]["positions"].items()}
R = T["run"]["result"]
FORDER, VALS = R["order"], R["orderValues"]
FIED = dict(zip(R["ids"], R["fiedler"]))
LAM = R["eigenvalues"]
SWEEP = R["sweep"]
LAP = T["laplacian"]
DISC = T["disconnected"]
DISC_E = [tuple(e) for e in DISC["graph"]["edges"]]

# facts the captions state, checked against the engine output
assert FORDER == ["E", "D", "C", "B", "A"] and [s["cut"] for s in SWEEP] == [6, 3, 5, 6]
assert [s["k"] for s in SWEEP if s["legal"]] == [2, 3] and R["bestK"] == 2 and R["cut"] == 3
assert [round(x) for x in LAP["L"][0]] == [6, -5, -1, 0, 0] and all(abs(s) < 1e-12 for s in LAP["rowSums"])
assert abs(LAM[0]) < 1e-12 and abs(LAM[1] - 1.7733143437) < 1e-9
assert T["bipartitions5"] == 15 and T["exhaustive"]["count"] == 15 and T["exhaustive"]["unconstrained"]["cut"] == 3
assert min(LAP["L"][i][i] for i in range(5)) == 6
assert abs(DISC["run"]["eigenvalues"][1]) < 1e-12 and DISC["run"]["cut"] == 0
assert T["stored"]["residual"] > 1e-3 and T["stored"]["liveResidual"] < 1e-12


def quad(x, edges=E5, ids=IDS):
    v = dict(zip(ids, x))
    return sum(w * (v[a] - v[b]) ** 2 for a, b, w in edges)


# the cut is a quadratic form on ±1 vectors: x_u = ±1 gives xᵀLx = 4 · cut
PM = [1 if n in "DE" else -1 for n in IDS]
assert quad(PM) == 4 * 3
# the Fiedler vector (unit length, ⟂ 1) attains λ2; a ±1 split scaled to unit length does worse
assert abs(quad([FIED[n] for n in IDS]) - LAM[1]) < 1e-9
PM_UNIT = [x / math.sqrt(5) for x in [1, 1, 1, -1.5, -1.5]]  # ⟂ 1, unit-length split vector for DE | ABC
PM_UNIT = [x / math.sqrt(sum(y * y for y in PM_UNIT)) for x in PM_UNIT]
Q_SPLIT = quad(PM_UNIT)
assert Q_SPLIT > LAM[1]

# a four-node ring: λ2 = λ3 = 2, the second eigenvector is not unique
RING = {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B", 1), ("B", "C", 1), ("C", "D", 1), ("D", "A", 1)]}
RING_EIG = [round(p[0], 9) for p in REF.jacobi_eigen(REF.laplacian(RING["nodes"], RING["edges"]))]
assert RING_EIG[1] == RING_EIG[2] == 2.0
RING_POS = {"A": (420, 330), "B": (700, 330), "C": (700, 610), "D": (420, 610)}

# a sign threshold is not a balance guarantee: a star with one heavy leaf
STAR = {"nodes": ["H", "P", "Q", "R", "S"], "edges": [("H", "P", 9), ("H", "Q", 1), ("H", "R", 1), ("H", "S", 1), ("Q", "R", 1), ("R", "S", 1)]}
_star = REF.spectral_bisection(STAR["nodes"], STAR["edges"], (0.0, 1.0))
STAR_SIGN = sum(1 for x in _star["vector"] if x > 0)


def key(u, v):
    return "|".join(sorted((u, v)))


def numline(fr, x0, x1, y, order, values, alpha=1.0, k=None, colors=None, labels=True, r=30, lo=None, hi=None, ticks=True):
    """The Fiedler number line: nodes at their values; a gold dashed cut between positions k and k+1."""
    if alpha <= 0:
        return
    lo = min(values) if lo is None else lo
    hi = max(values) if hi is None else hi
    sx = lambda v: x0 + (x1 - x0) * (v - lo) / ((hi - lo) or 1)
    fr.line((x0 - 40, y), (x1 + 40, y), DIM, 2, alpha)
    if ticks:
        z = sx(0)
        if x0 - 40 < z < x1 + 40:
            fr.line((z, y - 12), (z, y + 12), MUTED, 1.4, alpha)
            fr.text("0", z, y + 40, 18, MUTED, alpha, anchor="c", role="mono")
    last, up = -1e9, False
    for i, (n, v) in enumerate(zip(order, values)):
        x = sx(v)
        up = (x - last < 2 * r + 6) and not up
        last = x
        cy = y - (2 * r + 10) * up
        col = (colors or {}).get(n, NEUTRAL)
        if up:
            fr.line((x, cy + r), (x, y), DIM, 1.2, alpha)
        fr.dot((x, cy), r, NODE_BG, alpha)
        fr.ring((x, cy), r, col, 2.6, alpha)
        fr.text(n, x, cy + 10, 26, IVORY, alpha, anchor="c", role="serif")
        if labels:
            fr.text(f"{v:+.2f}", x, y + 70 + 24 * (i % 2), 18, MUTED, alpha, anchor="c", role="mono")
    if k:
        xc = (sx(values[k - 1]) + sx(values[k])) / 2
        fr.line((xc, y - 3 * r - 10), (xc, y + 40), GOLD, 3, alpha, glow=0.5 * alpha, dash=[8, 6])


def split_colors(order, k):
    return {n: (TEAL if i < k else BLUE) for i, n in enumerate(order)} if k else {}


def g01(fr, box, alpha=1.0, k=None, order=FORDER, hl=(), r=36, weights=True):
    pos = fit(P5RAW, box)
    left = set(order[:k]) if k else None
    cols = {n: (TEAL if n in left else BLUE) for n in pos} if left else {}
    crossing = {key(u, v) for u, v, _ in E5 if (u in left) != (v in left)} if left else set()
    graph(fr, pos, E5, cols, alpha, cut=crossing, r=r, hl_edges=hl, weights=weights)
    return pos


# ====================================================================== popular film
FR = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev", "E": "Eva"}
LINE_Y = 640


def friends_on_line(fr, k_place, alpha=1.0, cut_k=None, flip=False, bands=True):
    """Friends glide from their graph positions to their Fiedler positions on a horizontal line; bands between them."""
    graph_pos = fit(P5RAW, (300, 220, 900, 560))
    vals = {n: (FIED[n] if not flip else -FIED[n]) for n in IDS}  # E, D on the left as in the lesson
    lo, hi = min(vals.values()), max(vals.values())
    line_pos = {n: (360 + 1200 * (vals[n] - lo) / (hi - lo), LINE_Y) for n in IDS}
    seat, last, up = {}, -1e9, False
    for n in sorted(IDS, key=lambda n: vals[n]):  # a friend too close to the previous one steps up a row
        x = line_pos[n][0]
        up = (x - last < 96) and not up
        last = x
        seat[n] = (x, LINE_Y - 104 * up)
    k = ease(k_place)
    pos = {n: lerp2(graph_pos[n], seat[n], k) for n in IDS}
    if k > 0.2:
        fr.line((300, LINE_Y), (1620, LINE_Y), DIM, 2, alpha * clamp((k - 0.2) / 0.3))
    order = sorted(IDS, key=lambda n: vals[n])
    left = set(order[:cut_k]) if cut_k else set()
    if bands:
        for u, v, w in E5:
            crossing = cut_k and ((u in left) != (v in left))
            col = ROSE if crossing else AMBER
            p, q = pos[u], pos[v]
            # bands bow upward once the friends stand on the line, so parallel ones stay visible
            if k > 0.5:
                mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 - 30 - abs(q[0] - p[0]) * 0.18)
                arc = [((1 - t) ** 2 * p[0] + 2 * t * (1 - t) * mid[0] + t * t * q[0],
                        (1 - t) ** 2 * p[1] + 2 * t * (1 - t) * mid[1] + t * t * q[1]) for t in (i / 24 for i in range(25))]
                fr.polyline(arc, col, 1 + w * 0.7, alpha * (0.85 if crossing else 0.6), glow=0.3 * alpha if crossing else 0)
            else:
                fr.line(p, q, col, 1 + w * 0.7, alpha * 0.6)
    for n in IDS:
        p = pos[n]
        col = (TEAL if n in left else BLUE) if cut_k else NEUTRAL
        if seat[n][1] != LINE_Y and k > 0.5:
            fr.line((p[0], p[1] + 44), (p[0], LINE_Y), DIM, 1.2, alpha * clamp((k - 0.5) / 0.3))
        fr.dot(p, 44, NODE_BG, alpha)
        fr.ring(p, 44, col, 2.8, alpha)
        fr.text(FR[n], p[0], p[1] + 9, 24, IVORY, alpha, anchor="c", role="serif")
    if cut_k:
        xs = sorted(line_pos[n][0] for n in IDS)
        xc = (xs[cut_k - 1] + xs[cut_k]) / 2
        fr.line((xc, LINE_Y - 220), (xc, LINE_Y + 70), GOLD, 3, alpha, glow=0.5 * alpha, dash=[10, 7])
        fr.polyline([(xc - 11, LINE_Y - 240), (xc + 11, LINE_Y - 240), (xc, LINE_Y - 222)], GOLD, 1.5, alpha, close=True, fill=GOLD)  # the cut marker (no font has a reliable ✂)
    return line_pos


def p_rule(fr, c):
    friends_on_line(fr, 0.0, 1.0)
    panel(fr, 1060, 230, 660, 420, c.p(0), L("橡皮筋", "RUBBER BANDS"))
    fr.paragraph(L("交情越深，橡皮筋越粗，拉得越紧。", "The closer two friends, the thicker the band and the harder it pulls."), 1090, 320, 26, 600, IVORY, c.p(0))
    if c.on(1):
        fr.paragraph(L("总拉力 = Σ 粗细 × 距离²。", "Total pull = Σ thickness × distance²."), 1090, 430, 28, 600, AMBER, c.p(1), role="serif")
    if c.on(2):
        fr.paragraph(L("挤在同一点不算：必须散开，再让拉力最小。", "Huddling on one spot doesn't count: spread out, then make the pull as small as possible."), 1090, 520, 24, 600, GOLD, c.p(2))


def p_title(fr, c):
    title_assemble(fr, c, L("给每个点一个数", "A Number for Every Point"), L("谱二分 · SPECTRAL BISECTION", "SPECTRAL BISECTION"), "MODULE 06")


def p_settle(fr, c):
    k = clamp(c.span(0, 2) * 1.0) if c.T < FILL1[0] else 1.0
    if c.T < FILL1[0]:
        k = 0.15 + 0.6 * clamp(c.span(0, 2))
    else:
        k = 0.75 + 0.25 * landed(c.T, FILL1, len(FILL1) - 1)
    friends_on_line(fr, k, 1.0)
    if c.T >= FILL1[0]:
        a = landed(c.T, FILL1, len(FILL1) - 1)
        fr.text(L("Eva · Dev ｜ Cai ｜ Ben · Ada", "Eva · Dev | Cai | Ben · Ada"), W / 2, 270, 30, GOLD, a, anchor="c", role="serif", glow=0.3 * a)


def p_numbers(fr, c):
    friends_on_line(fr, 1.0, 1.0)
    a = c.p(0)
    vals = {n: FIED[n] for n in IDS}
    lo, hi = min(vals.values()), max(vals.values())
    for n in IDS:
        x = 360 + 1200 * (vals[n] - lo) / (hi - lo)
        fr.text(f"{vals[n]:+.2f}", x, LINE_Y + 90, 22, MUTED, a, anchor="c", role="mono")
    if c.on(1):
        fr.text(L("每个人得到一个数：这串数叫 Fiedler 向量", "each person gets a number: together, the Fiedler vector"), W / 2, 270, 28, TEAL, c.p(1), anchor="c")
    if c.on(2):
        fr.text(L("交情深的，数靠得近", "close friends get close numbers"), W / 2, 330, 26, GOLD, c.p(2), anchor="c")


def p_scissors(fr, c):
    n_hits = sum(1 for t in FILL2 if c.T >= t)
    if c.T < FILL2[0]:
        k = 1 + min(3, int(c.span(0, 2) * 4))
    else:
        k = [1, 2, 3, 4, 2][min(n_hits, 4)] if n_hits < 4 else 2
    if c.on(2) and c.T > FILL2[-1] + 0.3:
        k = 2
    friends_on_line(fr, 1.0, 1.0, cut_k=k)
    cuts = [s["cut"] for s in SWEEP]
    for i, v in enumerate(cuts):
        x = 560 + i * 260
        on = (i + 1) == k
        legal = SWEEP[i]["legal"]
        fr.rect(x - 90, 230, 180, 90, fill=PANEL_BG, stroke=GOLD if on else (FAINT if legal else "#4a3236"), width=1.6 if on else 1.2, alpha=0.95, r=8, screen=True)
        fr.text(f"k = {i + 1}", x, 262, 18, MUTED, 1.0, anchor="c", role="mono")
        fr.text(L(f"拆散 {v}", f"split {v}"), x, 302, 26, (GOLD if on else IVORY) if legal else ROSE, 1.0, anchor="c")
    if c.on(2):
        fr.text(L("两边各 2–3 人：选拆散最少的 3", "2–3 a side: take the smallest split, 3"), W / 2, 370, 26, TEAL, c.p(2), anchor="c")


def p_mirror(fr, c):
    n = count_hits(c.T, PHRASE)
    flip = c.T >= PHRASE[0] and n % 2 == 1
    if c.T > PHRASE[-1] + 0.2:
        flip = False
    friends_on_line(fr, 1.0, 1.0, cut_k=2 if not flip else 3, flip=flip)
    fr.text(L("整串数乘以 −1：镜像", "multiply every number by −1: a mirror image") if flip else L("原来的数", "the original numbers"),
            W / 2, 300, 30, ROSE if flip else TEAL, 1.0, anchor="c", role="serif", glow=0.3 * pulse(c.T, PHRASE, 0.4))
    if c.on(1):
        fr.text(L("同一刀，只是左右换了名字", "the same cut, with left and right renamed"), W / 2, 360, 26, GOLD, c.p(1), anchor="c")


def p_same(fr, c):
    friends_on_line(fr, 1.0, 0.6, cut_k=2)
    fr.text(L("翻号 ≠ 新答案", "a sign flip ≠ a new answer"), W / 2, 330, 40, GOLD, c.p(0), anchor="c", role="serif", glow=0.3 * c.p(0))


def p_breath(fr, c):
    a = c.p(0, 1.4)
    fr.text(L("一个数，就够了吗？", "Is one number enough?"), W / 2, 500, 52, GOLD, a, anchor="c", role="serif", glow=0.25 * a)


def p_apart(fr, c):
    raw = {k: tuple(v) for k, v in DISC["graph"]["positions"].items()}
    pos = fit(raw, (300, 240, 1000, 520))
    graph(fr, pos, DISC_E, {n: (TEAL if n in "ABC" else BLUE) for n in pos}, 1.0, r=34)
    if c.on(1):
        a = c.p(1)
        ids, vals = DISC["run"]["order"], DISC["run"]["orderValues"]
        numline(fr, 360, 960, 760, ids, vals, a, colors={n: (TEAL if n in "ABC" else BLUE) for n in ids}, labels=False, r=26, ticks=False)
        fr.text(L("同一组的人挤在同一个数上", "everyone in a group lands on the same number"), 660, 860 - 20, 22, MUTED, a, anchor="c")
    panel(fr, 1100, 260, 600, 300, c.p(0), L("两群人彼此不认识", "TWO GROUPS WHO NEVER MET"))
    fr.text("λ₂ = 0", 1140, 370, 34, ROSE, c.p(0), role="mono")
    if c.on(2):
        fr.paragraph(L("这串数只说明“谁和谁连着”，不再说明谁和谁更近。先检查连通。",
                       "The numbers only say who is connected to whom, not who is closer. Check connectivity first."), 1140, 430, 24, 520, IVORY, c.p(2))


def p_count(fr, c):
    a0 = c.p(0)
    fr.text("2⁵ = 32", W / 2, 330, 56, IVORY, a0, anchor="c", role="mono")
    fr.text(L("每人贴“左”或“右”", "each person marked left or right"), W / 2, 390, 24, MUTED, a0, anchor="c")
    if c.on(1):
        fr.text("− 2", W / 2, 480, 48, ROSE, c.p(1), anchor="c", role="mono")
        fr.text(L("去掉“全左”“全右”", "drop all-left and all-right"), W / 2, 530, 24, MUTED, c.p(1), anchor="c")
    if c.on(2):
        fr.text("÷ 2  =  15", W / 2, 630, 56, GOLD, c.p(2), anchor="c", role="mono", glow=0.3 * c.p(2))
        fr.text(L("左右交换算同一种：不是 16", "swapping sides is the same split: not 16"), W / 2, 690, 24, TEAL, c.p(2), anchor="c")


def p_chip(fr, c):
    a = c.p(0, 0.8)
    substrate(fr, 0.6 * a)
    lit = clamp((c.T - FILL4[0]) / 2.0) if c.T >= FILL4[0] else 0
    cells = [(i, j) for i in range(12) for j in range(5)]
    for i, j in cells:
        x, y = 380 + i * 100, 300 + j * 90
        v = (i - 5.5) / 6 + 0.12 * math.sin(i * 1.7 + j * 2.3)
        col = TEAL if v < 0 else BLUE
        fr.rect(x, y, 56, 40, fill=NODE_BG, stroke=col if lit > 0.3 else "#3d5d64", width=1.6, alpha=a, r=3)
    if lit > 0:
        fr.line((958, 260), (958, 760), GOLD, 3, lit * a, glow=0.5 * lit, dash=[10, 7])
        fr.text(L("第一刀：交给 Module 07、08 继续改进", "the first cut: handed to Modules 07 and 08 to improve"), W / 2, 840, 24, GOLD, lit, anchor="c")


def p_outro(fr, c):
    lines = [(L("一个数，来自整张图", "One number each, from the whole graph"), TEAL, 0),
             (L("沿数轴，每个缝隙都试一刀", "Along the line, try every gap"), TEAL, 1),
             (L("好的候选，不是最优的保证", "A good candidate, not a guarantee"), GOLD, 2)]
    for s, col, k in lines:
        if c.on(k):
            fr.text(s, W / 2, 380 + k * 90, 40, col, c.p(k, 1.2) * (1 - 0.6 * c.p(3)), anchor="c", role="serif")
    if c.on(3):
        a = c.p(3, 1.4)
        fr.text(L("切好之后，换一换两边的人会更好吗？", "After the cut, would swapping people across help?"), W / 2, 720, 40, GOLD, a, role="serif", anchor="c", glow=0.3 * a)


def p_end(fr, c):
    if not c.on(1):
        a = c.p(0, 1.0)
        g01(fr, (260, 240, 860, 720), a, k=2)
        fr.text(L("改边权 · 看数轴怎么动 · 看残差", "change a weight · watch the line move · read the residual"), 1360, 500, 26, GOLD, a, anchor="c")
    else:
        credits(fr, c, [(L("给每个点一个数", "A Number for Every Point"), GOLD, 44),
                        (L("Learning Clustering · Module 06 · 谱二分", "Learning Clustering · Module 06 · Spectral bisection"), IVORY, 24),
                        (L("原作 xingguangyaoyu（Issue #5）· 矩阵、数轴、扫描并排的版面来自原作", "Original work by xingguangyaoyu (Issue #5) · the matrix, line and sweep side by side come from it"), MUTED, 20),
                        (L("所有数值由本课程引擎 site/engines/spectral.js 在浏览器内实时求解", "Every value is solved live by this course's engine, site/engines/spectral.js"), MUTED, 20),
                        (MUSIC_LINE, MUTED, 18)], k=1)


STORY = Film(
    "story", "popular", L("给每个点一个数", "A Number for Every Point"), None, BRAND, poster_at=36.5, music=TRACK, seed=6,
    why=L("从撒了沙的振动金属板讲起：沙聚成一条线，把板分成两半。再看五个朋友沿一条长凳站开，交情越深的橡皮筋越粗、拉得越紧；他们停下的位置就是 Fiedler 向量，剪刀逐个缝隙试一刀。还有镜像翻号、彼此不认识的两群人，以及 15 而不是 16。",
          "It opens with sand on a bowed metal plate, gathering on one line that splits it in two. Then five friends spread along a bench, tied by rubber bands that pull harder the closer they are; where they settle is the Fiedler vector, and scissors try every gap. Plus a mirror flip, two groups who never met, and 15, not 16."),
    scenes=[
        Scene("p-plate", chladni, [Beat(L("在金属板上撒一层细沙，", "Sprinkle fine sand on a metal plate,"), 4.6),
                                   Beat(L("用琴弓拉它的边。", "and draw a violin bow along its edge."), 4.6)],
              chapter=L("序 · 沙与琴弓", "PROLOGUE · SAND AND A BOW"), until=S["intro_end"]),
        Scene("p-plate2", chladni, [Beat(L("沙聚成一条线：振动自己把板分成两半。", "The sand gathers on one line: the vibration splits the plate in two."), 5.6)],
              until=S["groove"]),
        Scene("p-rule", p_rule, [Beat(L("长凳上的五个朋友，用橡皮筋连着。", "Five friends on a bench, tied by rubber bands."), 4.2),
                                 Beat(L("总拉力：粗细乘以距离的平方，加起来。", "Total pull: thickness times distance squared, added up."), 4.4),
                                 Beat(L("不许挤在一点，散开后让拉力最小。", "No huddling on one spot: spread out, with the least pull."), 4.4)],
              chapter=L("序 · 一条线", "PROLOGUE · ONE LINE"), until=S["roll"]),
        Scene("p-title", p_title, [Beat(None, 4.5)], fade=False, until=37.0),
        Scene("p-settle", p_settle, [Beat(L("放手，让橡皮筋把大家拉到位。", "Let go, and the bands pull everyone into place."), 4.2),
                                     Beat(L("交情深的被拉到一起。", "Close friends are pulled together."), 3.2),
                                     Beat(L("Eva、Dev 在左，Ben、Ada 在右，Cai 居中。", "Eva, Dev left; Ben, Ada right; Cai between."), 6.0)],
              chapter=L("一 · 站好", "I · SETTLING"), until=S["fill1_end"]),
        Scene("p-numbers", p_numbers, [Beat(L("读出每个人的位置。", "Read off each person's position."), 3.0),
                                       Beat(L("这串数就是 Fiedler 向量。", "That list of numbers is the Fiedler vector."), 3.6),
                                       Beat(L("交情深的人，数靠得近。", "Close friends get close numbers."), 3.4)],
              until=S["accent"]),
        Scene("p-scissors", p_scissors, [Beat(L("现在，沿着长凳，每个缝隙试一刀。", "Now try a cut at every gap along the bench."), 3.6),
                                         Beat(L("拆散的交情：6、3、5、6。", "Friendship split: 6, 3, 5, 6."), 3.4),
                                         Beat(L("两边各两三个人：选 3，不是正中间。", "Two or three a side: take 3, not the middle."), 3.6)],
              chapter=L("二 · 剪刀", "II · SCISSORS"), until=S["phrase"]),
        Scene("p-mirror", p_mirror, [Beat(L("把每个数都乘以负一——", "Multiply every number by minus one —"), 3.4),
                                     Beat(L("整排镜像翻过去。", "the whole line mirrors over."), 3.0)],
              until=89.0),
        Scene("p-same", p_same, [Beat(L("还是同一刀，只是左右换了名字。", "Still the same cut, with left and right renamed."), 3.6),
                                 Beat(L("翻号不是新答案。", "A sign flip is not a new answer."), 3.0)],
              until=S["breath"]),
        Scene("p-breath", p_breath, [Beat(None, 4.6)], until=S["reentry"]),
        Scene("p-apart", p_apart, [Beat(L("如果是两群彼此不认识的人呢？", "What if they are two groups who never met?"), 3.6),
                                   Beat(L("同一群的人挤在同一个数上。", "Everyone in a group lands on the same number."), 3.6),
                                   Beat(L("这时 λ₂ = 0：数只说明谁连着谁。先检查连通。", "Then λ₂ = 0: the numbers only say who connects. Check connectivity first."), 6.0)],
              chapter=L("三 · 断开", "III · APART"), until=S["fill3_end"]),
        Scene("p-count", p_count, [Beat(L("五个人分两边，有几种分法？", "How many ways to split five people in two?"), 3.4),
                                   Beat(L("每人左或右：32 种，去掉全左、全右。", "Left or right each: 32, minus all-left and all-right."), 4.6),
                                   Beat(L("左右交换算一种：15 种，不是 16。", "Swapping sides is the same: 15, not 16."), 4.0)],
              chapter=L("四 · 数一数", "IV · COUNTING"), until=S["fill4"]),
        Scene("p-chip", p_chip, [Beat(L("芯片上，这一刀常常是划分的起点。", "On a chip, this cut is often where partitioning starts."), 5.4)],
              until=141.5),
        Scene("p-outro", p_outro, [Beat(L("一个数，来自整张图。", "One number each, from the whole graph."), 6.0),
                                   Beat(L("沿着数轴，每个缝隙都试一刀。", "Along the line, try every gap."), 6.0),
                                   Beat(L("得到的是好的候选，不是最优的保证。", "What you get is a good candidate, not a guarantee."), 7.0),
                                   Beat(L("切好之后，换一换两边的人呢？下一章见。", "After the cut, what about swapping people across? See the next module."), 8.0)],
              chapter=L("尾声", "CODA"), until=S["quiet"]),
        Scene("p-end", p_end, [Beat(L("下面的实验里，改边权，看数轴怎么动。", "In the lab below, change a weight and watch the line move."), 6.0),
                               Beat(None, 10.0)], until=S["end"]),
    ])


# ====================================================================== concise film
def k_title(fr, c):
    title_card(fr, L("谱二分", "Spectral Bisection"), L("SPECTRAL BISECTION  ·  精讲", "THE ESSENTIALS"), c.p(0, 1.2), kicker="MODULE 06")


def k_problem(fr, c):
    g01(fr, (240, 260, 860, 740), c.p(0, 1.0))
    panel(fr, 1040, 250, 680, 420, c.p(1), L("问题", "THE PROBLEM"))
    items = [(L("把节点分成两组，两组都非空", "Split the nodes in two, both sides non-empty"), IVORY, 1),
             (L("声明平衡窗口：每组 40%–60%（这里 2–3 个）", "Declare a balance window: 40%–60% a side (2–3 here)"), GOLD, 2),
             (L("在窗口内让 cut 尽量小", "Make the cut small inside the window"), TEAL, 2),
             (L("5 个节点的非空二分：(2⁵ − 2) / 2 = 15", "Non-empty bipartitions of 5 nodes: (2⁵ − 2) / 2 = 15"), IVORY, 3)]
    y = 350
    for s, col, b in items:
        if c.on(b):
            h = fr.paragraph(s, 1070, y, 25, 620, col, c.p(b))
            y += h + 18


def k_laplacian(fr, c):
    g01(fr, (200, 300, 760, 720), 1.0, hl={key("A", "B"), key("A", "C")} if c.on(1) else ())
    rows = [[""] + IDS] + [[IDS[i]] + [f"{x:g}" for x in LAP["L"][i]] for i in range(5)]
    cols = {(1, j): GOLD for j in range(1, 6)} if c.on(1) else {}
    table(fr, 960, 320, [80] + [110] * 5, rows, c.p(0), size=28, lh=64, colors=cols)
    fr.text("L = D − A", 1240, 260, 34, IVORY, c.p(0), role="mono", anchor="c")
    if c.on(2):
        fr.text(L("对角 = 度；非对角 = −w；每行和 0", "diagonal = degree; off-diagonal = −w; each row sums to 0"), 1240, 740, 24, TEAL, c.p(2), anchor="c")


def k_quad(fr, c):
    panel(fr, 260, 240, 1400, 280, c.p(0), L("二次型", "THE QUADRATIC FORM"))
    fr.text("xᵀ L x  =  Σ w(u,v) · (x_u − x_v)²", W / 2, 380, 40, IVORY, c.p(0), role="mono", anchor="c")
    if c.on(1):
        fr.text(L("边越重，两端的数越要接近", "the heavier the edge, the closer its two numbers must be"), W / 2, 460, 26, GOLD, c.p(1), anchor="c")
    if c.on(2):
        fr.paragraph(L("要求 x 与全 1 向量正交、长度为 1，最小值就是 λ₂，取到它的 x 就是 Fiedler 向量。",
                       "Require x ⊥ the all-ones vector with length 1: the minimum is λ₂, and the x that attains it is the Fiedler vector."),
                     260, 620, 28, 1400, IVORY, c.p(2))
    if c.on(3):
        fr.text(L(f"G01：λ₂ = {LAM[1]:.4f}", f"G01: λ₂ = {LAM[1]:.4f}"), W / 2, 780, 30, TEAL, c.p(3), anchor="c", role="mono")


def k_fiedler(fr, c):
    g01(fr, (240, 230, 760, 560), c.p(0), r=30)
    numline(fr, 440, 1480, 760, FORDER, VALS, c.p(1))
    panel(fr, 1060, 240, 640, 300, c.p(0), L("Fiedler 向量", "THE FIEDLER VECTOR"))
    fr.text(L("排序：E, D, C, B, A", "order: E, D, C, B, A"), 1090, 340, 28, IVORY, c.p(1), role="mono")
    if c.on(2):
        fr.text(L("E、D 靠在一起；A、B 靠在一起", "E and D together; A and B together"), 1090, 410, 24, GOLD, c.p(2))
        fr.text(L("C 在中间：它和两边都有边", "C between: it has edges to both"), 1090, 460, 24, MUTED, c.p(2))


def k_sweep(fr, c):
    k = 1 + min(3, int(c.span(0, 2) * 4)) if not c.on(2) else 2
    numline(fr, 440, 1480, 400, FORDER, VALS, 1.0, k=k, colors=split_colors(FORDER, k))
    rows = [["k", L("左组", "Left"), "cut", L("窗口内", "In window")]] + [[str(s["k"]), "".join(s["left"]), str(s["cut"]), "✓" if s["legal"] else "×"] for s in SWEEP]
    cols = {(i + 1, 2): (GOLD if s["k"] == 2 else (IVORY if s["legal"] else ROSE)) for i, s in enumerate(SWEEP)}
    table(fr, 640, 600, [120, 260, 160, 200], [[tr(x) for x in r] for r in rows], c.p(0), size=26, lh=50, colors=cols)
    if c.on(2):
        fr.text(L("窗口内选最小：k = 2，DE | ABC，cut 3（正中间 k = 3 是 5）", "least inside the window: k = 2, DE | ABC, cut 3 (the middle, k = 3, is 5)"), W / 2, 880 - 40, 24, TEAL, c.p(2), anchor="c")


def k_warn(fr, c):
    panel(fr, 220, 240, 700, 460, c.p(0), L("翻号", "A SIGN FLIP"))
    fr.paragraph(L("x 是特征向量，−x 也是。排序反向，同一刀左右互换：分组不变。", "If x is an eigenvector, so is −x. The order reverses and the same cut swaps sides: the grouping is unchanged."), 250, 330, 24, 640, IVORY, c.p(0))
    numline(fr, 300, 840, 600, list(reversed(FORDER)), [-v for v in reversed(VALS)], c.p(1), k=3, colors=split_colors(list(reversed(FORDER)), 3), labels=False, r=24, ticks=False)
    if c.on(2):
        a = c.p(2)
        panel(fr, 1000, 240, 700, 460, a, L("断开的图", "A DISCONNECTED GRAPH"))
        fr.paragraph(L("每个连通分量各给一个 λ = 0：λ₂ = 0，排序只反映分量。先检查连通。",
                       "Each component gives its own λ = 0: λ₂ = 0, and the order only reflects the components. Check connectivity first."), 1030, 330, 24, 640, IVORY, a)
        ids, vals = DISC["run"]["order"], DISC["run"]["orderValues"]
        numline(fr, 1080, 1620, 600, ids, vals, a, colors={n: (TEAL if n in "ABC" else BLUE) for n in ids}, labels=False, r=22, ticks=False)


def k_take(fr, c):
    items = [(L("先声明：两组非空、平衡窗口（5 个节点有 15 种非空二分）", "Declare first: both sides non-empty, a balance window (5 nodes: 15 bipartitions)"), GOLD),
             (L("L = D − A：对角是度，非对角是 −w，每行和 0", "L = D − A: degrees on the diagonal, −w off it, rows sum to 0"), TEAL),
             (L("Fiedler 向量排序，窗口内逐个切点取最小 cut", "Sort by the Fiedler vector; take the least cut over cut points in the window"), TEAL),
             (L("翻号不改分组；不连通时 λ₂ = 0，先检查", "A sign flip changes nothing; disconnected means λ₂ = 0, so check first"), ROSE)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 260 + i * 120
            fr.rect(220, y, 1480, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 58, 28, col, a, role="mono")
            fr.text(s, 360, y + 58, 28, IVORY, a)


CONCISE = Film(
    "concise", "concise", L("精讲：矩阵、数轴、扫描", "The essentials"), None, BRAND, poster_at=40.0, music="score:steady", seed=26,
    why=L("只讲必须掌握的：问题与平衡窗口、构造 L = D − A、二次型、Fiedler 排序、扫描 6 / 3 / 5 / 6，以及翻号与断开两条警告。",
          "Only what you must know: the problem and its balance window, building L = D − A, the quadratic form, the Fiedler order, the sweep 6 / 3 / 5 / 6, and two warnings: sign flips and disconnected graphs."),
    scenes=[
        Scene("k00-title", k_title, [Beat(None, 3.0)]),
        Scene("k01-problem", k_problem, [Beat(L("谱二分要把一张图分成两组。", "Spectral bisection splits a graph into two groups."), 2.8),
                                         Beat(L("两组都非空。", "Both groups non-empty."), 1.8),
                                         Beat(L("还要声明平衡窗口：这里每组 2 到 3 个，在窗口内让 cut 尽量小。", "And a declared balance window, here 2 to 3 a side; inside it, make the cut small."), 5.4),
                                         Beat(L("5 个节点一共有 15 种非空二分。", "Five nodes have 15 non-empty bipartitions."), 3.0)],
              chapter=L("问题", "THE PROBLEM")),
        Scene("k02-laplacian", k_laplacian, [Beat(L("第一步，构造拉普拉斯矩阵 L = D − A。", "Step one: build the Laplacian L = D − A."), 3.4),
                                             Beat(L("A 行：度 5 + 1 = 6，和 B 是 −5，和 C 是 −1。", "Row A: degree 5 + 1 = 6, −5 to B, −1 to C."), 4.4),
                                             Beat(L("每行和都是 0。", "Every row sums to 0."), 2.4)],
              chapter=L("拉普拉斯矩阵", "THE LAPLACIAN")),
        Scene("k03-quad", k_quad, [Beat(L("为什么用 L？看二次型：每条边贡献 w 乘以两端之差的平方。", "Why L? Look at the quadratic form: each edge adds w times the squared difference of its ends."), 5.4),
                                   Beat(L("边越重，两端的数就越要接近。", "The heavier the edge, the closer its two numbers must be."), 3.4),
                                   Beat(L("在与全 1 正交、长度为 1 的向量里，最小值是 λ₂。", "Among unit vectors orthogonal to all-ones, the minimum is λ₂."), 4.4),
                                   Beat(L("取到它的，就是 Fiedler 向量。", "The vector that attains it is the Fiedler vector."), 3.0)],
              chapter=L("二次型", "THE QUADRATIC FORM")),
        Scene("k04-fiedler", k_fiedler, [Beat(L("G01 的 Fiedler 向量给每个节点一个数。", "G01's Fiedler vector gives each node a number."), 3.4),
                                         Beat(L("排序：E、D、C、B、A。", "The order: E, D, C, B, A."), 2.6),
                                         Beat(L("连得紧的靠在一起；C 和两边都有边，落在中间。", "Tightly linked nodes sit together; C, linked to both sides, sits between."), 4.8)],
              chapter=L("Fiedler 向量", "THE FIEDLER VECTOR")),
        Scene("k05-sweep", k_sweep, [Beat(L("沿排序，在每个相邻位置之间试切。", "Along the order, try a cut between each pair of neighbours."), 3.6),
                                     Beat(L("cut 依次是 6、3、5、6。", "The cuts are 6, 3, 5, 6."), 2.8),
                                     Beat(L("窗口内只有 k = 2 和 3：选 cut 3 的 k = 2，不是正中间。", "Only k = 2 and 3 are in the window: choose k = 2 with cut 3, not the middle."), 5.2)],
              chapter=L("扫描", "THE SWEEP")),
        Scene("k06-warn", k_warn, [Beat(L("两条警告。第一，翻号：−x 也是特征向量。", "Two warnings. First, the sign: −x is an eigenvector too."), 3.8),
                                   Beat(L("排序反向，同一刀只是左右互换。", "The order reverses; the same cut just swaps sides."), 3.2),
                                   Beat(L("第二，图不连通时 λ₂ = 0，排序只反映分量。", "Second, when the graph is disconnected λ₂ = 0, and the order only reflects components."), 4.8)],
              chapter=L("警告", "WARNINGS")),
        Scene("k07-take", k_take, [Beat(L("记住四点。", "Four things to keep."), 1.4),
                                   Beat(L("先声明非空与平衡窗口；", "Declare non-empty sides and a window;"), 2.6),
                                   Beat(L("构造 L，按 Fiedler 排序扫描；", "build L, sort by Fiedler, sweep;"), 2.6),
                                   Beat(L("翻号不变，断开先查。下面的实验里试一试。", "Sign flips change nothing; check connectivity. Try it in the lab below."), 4.2)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])


# ====================================================================== advanced film
def a_title(fr, c):
    title_card(fr, L("谱二分", "Spectral Bisection"), L("进阶：松弛、取整与数值", "IN DEPTH: RELAXATION, ROUNDING AND NUMERICS"), c.p(0, 1.2), kicker="MODULE 06")


def a_cutform(fr, c):
    g01(fr, (200, 300, 760, 720), 1.0, k=2 if c.on(1) else None)
    panel(fr, 960, 240, 760, 440, c.p(0), L("cut 本身就是一个二次型", "THE CUT IS ITSELF A QUADRATIC FORM"))
    fr.text(L("x_u = +1（左） 或 −1（右）", "x_u = +1 (left) or −1 (right)"), 1000, 340, 26, IVORY, c.p(0), role="mono")
    if c.on(1):
        fr.text(L("同侧边：(x_u − x_v)² = 0", "same side: (x_u − x_v)² = 0"), 1000, 410, 24, MUTED, c.p(1), role="mono")
        fr.text(L("跨侧边：(x_u − x_v)² = 4", "crossing: (x_u − x_v)² = 4"), 1000, 460, 24, ROSE, c.p(1), role="mono")
    if c.on(2):
        fr.text("xᵀLx = 4 · cut", 1000, 550, 36, GOLD, c.p(2), role="mono", glow=0.3 * c.p(2))
        fr.text(L(f"DE | ABC：xᵀLx = {quad(PM):g} = 4 × 3", f"DE | ABC: xᵀLx = {quad(PM):g} = 4 × 3"), 1000, 620, 24, TEAL, c.p(2), role="mono")


def a_relax(fr, c):
    panel(fr, 260, 230, 1400, 300, c.p(0), L("松弛：把 ±1 放宽成实数", "RELAXATION: LOOSEN ±1 TO REAL NUMBERS"))
    fr.paragraph(L("在 ±1 向量里找最小 cut 要试遍所有分法；放宽成实数后，问题变成求 L 的特征向量。",
                   "Finding the least cut among ±1 vectors means trying every split; loosened to real numbers, it becomes an eigenvector of L."), 300, 320, 26, 1320, IVORY, c.p(0))
    if c.on(1):
        a = c.p(1)
        rows = [[L("单位长度、与 1 正交的向量", "Unit vector ⊥ 1"), "xᵀLx"], [L("DE | ABC 的分组向量", "the DE | ABC split vector"), f"{Q_SPLIT:.3f}"], [L("Fiedler 向量", "the Fiedler vector"), f"{LAM[1]:.3f}"]]
        table(fr, 420, 640, [700, 300], [[tr(x) for x in r] for r in rows], a, size=28, lh=64, colors={(1, 1): ROSE, (2, 1): TEAL})
    if c.on(2):
        fr.paragraph(L("λ₂ 是下界：任何分组向量都不会更小。代价是答案不再是 ±1，需要取整。", "λ₂ is a lower bound: no split vector does better. The price: the answer is no longer ±1 and must be rounded."),
                     300, 860 - 20, 24, 1320, GOLD, c.p(2))


def a_round(fr, c):
    numline(fr, 440, 1480, 360, FORDER, VALS, 1.0, k=2 if c.on(2) else None, colors=split_colors(FORDER, 2) if c.on(2) else None)
    panel(fr, 260, 520, 660, 300, c.p(0), L("按正负号切", "CUT BY SIGN"))
    fr.paragraph(L("只试一个阈值 0。在 G01 上恰好是 k = 2。", "Try only the threshold 0. On G01 it happens to be k = 2."), 290, 610, 24, 600, IVORY, c.p(0))
    if c.on(1):
        fr.paragraph(L(f"但它不看平衡：一个重叶子的星形图上，正号一侧只有 {STAR_SIGN} 个点。", f"But it ignores balance: on a star with one heavy leaf, the positive side holds {STAR_SIGN} node(s)."), 290, 700, 22, 600, ROSE, c.p(1))
    if c.on(2):
        a = c.p(2)
        panel(fr, 1000, 520, 660, 300, a, L("扫描（本课程）", "SWEEP (THIS COURSE)"))
        fr.paragraph(L("试遍 n − 1 个阈值，只在窗口内取最小 cut：取整更稳。", "Try all n − 1 thresholds and take the least cut inside the window: a sturdier rounding."), 1030, 610, 24, 600, TEAL, a)


def a_window(fr, c):
    rows = [[L("约束", "Constraint"), L("最小 cut", "Least cut"), L("分组", "Grouping")],
            [L("孤立一个点", "isolate one node"), "6", "A | BCDE"],
            [L("不限（只要非空）", "any (non-empty)"), str(T["exhaustive"]["unconstrained"]["cut"]), "ABC | DE"],
            [L("40/60 窗口", "40/60 window"), str(T["exhaustive"]["best"]["cut"]), "ABC | DE"]]
    table(fr, 420, 330, [500, 260, 300], [[tr(x) for x in r] for r in rows[:2 + c.on(1) + c.on(2)]], c.p(0), size=30, lh=74, colors={(1, 1): ROSE, (2, 1): TEAL, (3, 1): TEAL})
    if c.on(3):
        fr.paragraph(L("原作说“无约束时总是切掉一个点”，这张图就是反例。正确的说法：无约束可能切出过小的组，所以要声明窗口。",
                       "The original claims “with no constraint you always cut off one node”; this graph is a counterexample. The right statement: with no constraint a group can come out too small, so declare a window."),
                     300, 700, 26, 1320, GOLD, c.p(3))


def a_degenerate(fr, c):
    graph(fr, RING_POS, RING["edges"], {}, c.p(0), r=36)
    panel(fr, 1000, 250, 700, 320, c.p(0), L("四节点环", "A FOUR-NODE RING"))
    fr.text(f"λ = {', '.join(f'{abs(x) if abs(x) < 1e-9 else x:g}' for x in RING_EIG)}", 1040, 350, 28, IVORY, c.p(0), role="mono")
    if c.on(1):
        fr.paragraph(L("λ₂ = λ₃ = 2：第二特征向量不唯一，这个特征空间里任何方向都同样合法。", "λ₂ = λ₃ = 2: the second eigenvector is not unique; any direction in that eigenspace is equally valid."), 1040, 410, 24, 620, ROSE, c.p(1))
    if c.on(2):
        a = c.p(2)
        panel(fr, 1000, 610, 700, 200, a, L("看间隙", "WATCH THE GAP"))
        fr.text(L(f"G01：λ₃ − λ₂ = {LAM[2] - LAM[1]:.2f}，排序稳定", f"G01: λ₃ − λ₂ = {LAM[2] - LAM[1]:.2f}, a stable order"), 1040, 710, 24, TEAL, a)
        fr.text(L("间隙越小，排序越容易被小扰动改变", "the smaller the gap, the more easily a small change reorders it"), 1040, 760, 22, MUTED, a)


def a_numerics(fr, c):
    rows = [[L("向量来源", "Vector source"), L("残差 ‖Lx − λx‖ / ‖x‖", "Residual ‖Lx − λx‖ / ‖x‖")],
            [L("原作存储的三位小数", "the original's stored 3 decimals"), f"{T['stored']['residual']:.4f}"],
            [L("本课程实时求解（Jacobi）", "this course, solved live (Jacobi)"), f"{T['stored']['liveResidual']:.1e}"]]
    table(fr, 360, 330, [640, 520], [[tr(x) for x in r] for r in rows[:2 + c.on(1)]], c.p(0), size=28, lh=74, colors={(1, 1): AMBER, (2, 1): TEAL})
    if c.on(2):
        fr.paragraph(L("残差告诉你向量有多“真”：0.0044 是舍入，够展示，但改图后不会重算。", "The residual tells you how genuine the vector is: 0.0044 is rounding, fine for display, but never recomputed when the graph changes."), 300, 600, 26, 1320, IVORY, c.p(2))
    if c.on(3):
        fr.paragraph(L("Jacobi 每次扫掠约 n³ 次运算，适合教学规模；大电路用稀疏迭代法（如 Lanczos），只求最小的几个特征对。",
                       "Each Jacobi sweep costs about n³ operations, fine at teaching scale; large circuits use sparse iterative methods (such as Lanczos) for just the few smallest eigenpairs."), 300, 720, 26, 1320, GOLD, c.p(3))


def a_summary(fr, c):
    items = [(L("±1 向量上，xᵀLx = 4 · cut", "On ±1 vectors, xᵀLx = 4 · cut"), TEAL),
             (L("放宽成实数：最小值 λ₂ 是 cut 的下界线索", "Loosen to real numbers: the minimum λ₂ bounds the relaxed problem"), TEAL),
             (L("取整：扫描 n − 1 个阈值，胜过只看正负号", "Round by sweeping n − 1 thresholds, not by sign alone"), GOLD),
             (L("平衡窗口必须声明：无约束可能切出过小的组", "Declare a balance window: no constraint can give a tiny group"), GOLD),
             (L("λ₂ 简并或为 0：向量不唯一或只反映分量", "λ₂ repeated or zero: the vector is not unique, or only shows components"), ROSE),
             (L("看残差；大规模用稀疏迭代求解", "Read the residual; use sparse iterative solvers at scale"), TEAL)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 200 + i * 104
            fr.rect(220, y, 1480, 84, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 54, 26, col, a, role="mono")
            fr.text(s, 350, y + 54, 30, IVORY, a)


ADVANCED = Film(
    "advanced", "advanced", L("进阶：松弛、取整与数值", "In depth: relaxation and rounding"), None, BRAND, poster_at=40.0, music="score:calm", seed=38,
    why=L("cut 在 ±1 向量上是二次型、放宽成实数为什么得到特征向量、扫描取整与正负号取整、为什么要平衡窗口、简并与零特征值，以及残差和求解器。",
          "The cut as a quadratic form on ±1 vectors, why relaxing to real numbers gives an eigenvector, rounding by a sweep versus by sign, why a balance window, repeated and zero eigenvalues, and residuals and solvers."),
    scenes=[
        Scene("a00-title", a_title, [Beat(None, 3.0)]),
        Scene("a01-cutform", a_cutform, [Beat(L("给每个节点贴 +1 或 −1，表示在哪一侧。", "Mark each node +1 or −1 for its side."), 3.6),
                                         Beat(L("同侧的边差为 0，跨侧的边差的平方是 4。", "A same-side edge contributes 0; a crossing edge's squared difference is 4."), 4.6),
                                         Beat(L("所以 xᵀLx 恰好是 cut 的 4 倍：DE | ABC 得 12。", "So xᵀLx is exactly 4 times the cut: 12 for DE | ABC."), 4.6)],
              chapter=L("一 · cut 是二次型", "I · THE CUT AS A QUADRATIC FORM")),
        Scene("a02-relax", a_relax, [Beat(L("只允许 ±1，就得试遍所有分法。放宽成实数，问题变成求特征向量。", "Allow only ±1 and you must try every split. Loosen to real numbers, and it becomes an eigenvector problem."), 6.4),
                                     Beat(L(f"同样单位长度：分组向量是 {Q_SPLIT:.2f}，Fiedler 向量只有 {LAM[1]:.2f}。", f"At the same unit length: the split vector gives {Q_SPLIT:.2f}, the Fiedler vector only {LAM[1]:.2f}."), 5.4),
                                     Beat(L("λ₂ 是放宽后的最小值；代价是答案不再是 ±1，必须取整。", "λ₂ is the relaxed minimum; the price is an answer that is no longer ±1 and must be rounded."), 5.4)],
              chapter=L("二 · 松弛", "II · RELAXATION")),
        Scene("a03-round", a_round, [Beat(L("最简单的取整：按正负号切，只试阈值 0。", "The simplest rounding: cut by sign, trying only the threshold 0."), 4.2),
                                     Beat(L("它不看平衡：在重叶子的星形图上，一侧可能只剩一个点。", "It ignores balance: on a star with a heavy leaf, one side can hold a single node."), 5.4),
                                     Beat(L("本课程试遍 n − 1 个阈值，只在窗口内取最小。", "This course tries all n − 1 thresholds and takes the least inside the window."), 4.6)],
              chapter=L("三 · 取整", "III · ROUNDING")),
        Scene("a04-window", a_window, [Beat(L("为什么要平衡窗口？比较三种约束。", "Why a balance window? Compare three constraints."), 3.4),
                                       Beat(L("孤立一个点最少要切 6；不限的话，最小是 3。", "Isolating one node cuts at least 6; with no limit, the least is 3."), 4.4),
                                       Beat(L("40/60 窗口里也是 3。", "Inside the 40/60 window it is also 3."), 2.8),
                                       Beat(L("“无约束总切单点”不对；正确说法是可能切出过小的组。", "“No constraint always cuts off one node” is wrong; a group can come out too small."), 5.4)],
              chapter=L("四 · 平衡窗口", "IV · THE BALANCE WINDOW")),
        Scene("a05-degenerate", a_degenerate, [Beat(L("四节点环的特征值：0、2、2、4。", "The four-node ring's eigenvalues: 0, 2, 2, 4."), 3.6),
                                               Beat(L("λ₂ = λ₃：第二特征向量不唯一，任何方向都合法。", "λ₂ = λ₃: the second eigenvector is not unique; any direction is valid."), 4.6),
                                               Beat(L("G01 的间隙有 6.68，排序稳定；间隙越小越容易被扰动。", "G01's gap is 6.68, a stable order; the smaller the gap, the more fragile."), 5.2)],
              chapter=L("五 · 简并", "V · REPEATED EIGENVALUES")),
        Scene("a06-numerics", a_numerics, [Beat(L("向量真不真，看残差。", "Is the vector genuine? Read the residual."), 2.8),
                                           Beat(L("原作存储的三位小数是 0.0044；实时求解是 10⁻¹⁵。", "The original's three stored decimals give 0.0044; the live solve gives 10⁻¹⁵."), 4.8),
                                           Beat(L("0.0044 是舍入，够展示，但改图后不会重算。", "0.0044 is rounding: fine for display, but never recomputed when the graph changes."), 4.6),
                                           Beat(L("大电路用 Lanczos 这类稀疏迭代法，只求最小的几个特征对。", "Large circuits use sparse iterative methods like Lanczos, for only the smallest eigenpairs."), 5.2)],
              chapter=L("六 · 数值", "VI · NUMERICS")),
        Scene("a07-summary", a_summary, [Beat(L("六点小结。", "Six things to keep."), 1.6)] + [Beat(None, 2.6) for _ in range(5)]
              + [Beat(L("下一章：在这一刀上，交换两边的节点。", "Next: improve the cut by swapping nodes across it."), 3.0)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

FILMS = [STORY, CONCISE, ADVANCED]
ORDER = ["story", "concise", "advanced", "lab"]
