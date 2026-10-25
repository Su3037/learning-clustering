"""Cold opens for the chapter popular-science films. Each hook starts from the algorithm's own idea in everyday
life, not from clustering in general (the homepage film introduces clustering once, for the whole course).

Every hook fills the first two slots of the We Never cut: 0–10.75 s lands on the sparse intro hits, and
10.75–17.41 s is the silent punchline. Each draw function takes (fr, c) and reads the absolute film time c.T.

  droplets   M03  rain on a window: the two nearest drops always merge first        (greedy pair merge)
  chairlift  M04  a two-seat chairlift: three best friends cannot ride together       (capacity)
  dialect    M05  a dorm floor: everyone picks up what most neighbours say            (label propagation)
  chladni    M06  sand on a bowed plate gathers on one line and splits it in two     (the Fiedler vector)
  chess      M07  a sacrifice: lose 3 now, take 9 two moves later                      (KL trial swaps)
  boats      M08  two boats, one person across at a time, neither too crowded        (FM single moves, balance)
"""
import math

import numpy as np

from cine import (W, L, tr, GOLD, TEAL, BLUE, ROSE, AMBER, CORAL, LILAC, SAGE, IVORY, MUTED, FAINT, DIM, PANEL_BG, NODE_BG,
                  clamp, ease, lerp, lerp2, pulse, badge)
from story import S, INTRO_HITS, landed

PUNCH = S["intro_end"]          # the silent punchline starts here
TURN = S["groove"]              # and the groove takes over here


def hit(i):
    return INTRO_HITS[min(i, len(INTRO_HITS) - 1)]


# ---------------------------------------------------------------- M03 · droplets
def _drops():
    rng = np.random.RandomState(3)
    pts = []
    while len(pts) < 11:
        p = (rng.uniform(650, 1270), rng.uniform(290, 730), rng.uniform(18, 30))
        if all(math.hypot(p[0] - q[0], p[1] - q[1]) > p[2] + q[2] + 40 for q in pts):
            pts.append(p)
    return pts


def _merge_plan():
    """Greedy: at every merge time the pair with the smallest gap fuses (area-weighted centre, area adds)."""
    times = list(INTRO_HITS[1:]) + [PUNCH + 0.8, PUNCH + 2.0, PUNCH + 3.2, PUNCH + 4.4]
    drops = _drops()
    plan = []
    for t in times:
        if len(drops) < 3:
            break
        best = None
        for i in range(len(drops)):
            for j in range(i + 1, len(drops)):
                a, b = drops[i], drops[j]
                gap = math.hypot(a[0] - b[0], a[1] - b[1]) - a[2] - b[2]
                if best is None or gap < best[0] - 1e-9:
                    best = (gap, i, j)
        _, i, j = best
        a, b = drops[i], drops[j]
        wa, wb = a[2] ** 2, b[2] ** 2
        m = ((a[0] * wa + b[0] * wb) / (wa + wb), (a[1] * wa + b[1] * wb) / (wa + wb), math.sqrt(wa + wb))
        plan.append((t, list(drops), i, j, m))
        drops = [d for k, d in enumerate(drops) if k not in (i, j)] + [m]
    return plan, drops


DROP_PLAN, DROP_END = _merge_plan()


def _drop(fr, x, y, r, a, hot=False):
    fr.dot((x, y), r, "#123848", 0.85 * a)
    fr.ring((x, y), r, GOLD if hot else "#9cc9d6", 1.8, a, glow=0.5 * a if hot else 0.15 * a)
    fr.dot((x - r * 0.35, y - r * 0.4), max(2, r * 0.18), IVORY, 0.55 * a)


def droplets(fr, c):
    T = c.T
    pane = landed(T, INTRO_HITS, 0)
    fr.rect(560, 220, 800, 580, fill=PANEL_BG, stroke=FAINT, width=1.4, alpha=0.9 * pane, r=14)
    fr.line((960, 220), (960, 800), FAINT, 1.2, 0.6 * pane)
    fr.line((560, 510), (1360, 510), FAINT, 1.2, 0.6 * pane)
    # the state at time T: the last merge that has started, animating over 0.4 s
    k = sum(1 for t, *_ in DROP_PLAN if t <= T)
    if k == 0:
        drops = DROP_PLAN[0][1]
        for n, d in enumerate(drops):
            a = ease((T - hit(0) - n * 0.05) / 0.5)
            _drop(fr, *d, a)
        nxt = DROP_PLAN[0]
    else:
        t, before, i, j, m = DROP_PLAN[k - 1]
        q = ease((T - t) / 0.4)
        for n, d in enumerate(before):
            if n in (i, j):
                continue
            _drop(fr, *d, 1.0)
        if q < 1:
            for n in (i, j):
                d = before[n]
                p = lerp2(d[:2], m[:2], q)
                _drop(fr, p[0], p[1], lerp(d[2], m[2] * 0.85, q), 1.0, hot=True)
        else:
            _drop(fr, *m, 1.0, hot=T - t < 0.9)
        nxt = DROP_PLAN[k] if k < len(DROP_PLAN) else None
    if nxt and T >= hit(0) + 0.5 and T < nxt[0]:
        a, b = nxt[1][nxt[2]], nxt[1][nxt[3]]
        lead = clamp(1 - (nxt[0] - T) / 1.0)
        fr.line(a[:2], b[:2], GOLD, 1.6, 0.25 + 0.6 * lead, glow=0.4 * lead, dash=[6, 6])
    left = len(DROP_PLAN[k][1]) if k < len(DROP_PLAN) else len(DROP_END)
    fr.text(L(f"{left} 滴", f"{left} drops"), 1360, 840, 22, MUTED, pane, anchor="r", role="mono")
    if T >= PUNCH:
        fr.text(L("最近的一对，先合并", "the nearest pair merges first"), 560, 840, 22, GOLD, ease((T - PUNCH) / 0.8), role="serif")


# ---------------------------------------------------------------- M04 · chairlift
CABLE = ((200, 250), (1720, 170))
LOAD_X = 620
SEATS2 = [(LOAD_X - 58, 610), (LOAD_X + 58, 610)]
QUEUE = [(840, 740), (940, 740), (1040, 740), (1260, 740), (1360, 740)]


def _cable_at(x):
    (x0, y0), (x1, y1) = CABLE
    return (x, y0 + (y1 - y0) * (x - x0) / (x1 - x0))


def _chair(fr, x, a, big=False):
    top = _cable_at(x)
    if big:
        fr.line(top, (x, 560), DIM, 3, a)
        fr.line((x - 110, 560), (x + 110, 560), DIM, 3, a)
        for sx in (-110, 110):
            fr.line((x + sx, 560), (x + sx, 640), DIM, 3, a)
        fr.rect(x - 112, 640, 224, 14, fill="#5d7f86", alpha=a, r=6)
        return
    fr.line(top, (top[0], top[1] + 110), DIM, 2, a)
    fr.rect(top[0] - 46, top[1] + 110, 92, 9, fill=FAINT, alpha=a, r=4)


def chairlift(fr, c):
    T = c.T
    a0 = landed(T, INTRO_HITS, 0)
    fr.line(*CABLE, MUTED, 2.0, 0.8 * a0)
    for k in range(5):
        x = 820 + ((k * 230 + 40 * max(0.0, T - 0.5)) % 1150)
        _chair(fr, x, a0 * clamp((1700 - x) / 120) * clamp((x - 800) / 80))
    _chair(fr, LOAD_X, a0, big=True)
    badge(fr, LOAD_X, 500, L("每把吊椅 · 两个座位", "EACH CHAIR · TWO SEATS"), GOLD, landed(T, INTRO_HITS, 1), 20, screen=True)
    board = ease((T - PUNCH - 1.0) / 1.2) if T >= PUNCH else 0.0
    back = ease((T - PUNCH - 2.6) / 0.8) if T >= PUNCH else 0.0
    trio = (0, 1, 2)
    for i, p in enumerate(QUEUE):
        a = landed(T, INTRO_HITS, 1 + i)
        if a <= 0:
            continue
        q = p
        if i in (0, 1):
            q = lerp2(p, SEATS2[i], board)
        if i == 2:
            q = lerp2(p, (LOAD_X + 170, 610), board * (1 - back))
        col = GOLD if i in trio else "#9fbcbc"
        fr.dot(q, 32, NODE_BG, a)
        fr.ring(q, 32, col, 2.6, a, glow=0.3 * a if i in trio else 0)
        if i == 2 and back > 0:
            fr.ring(q, 44, ROSE, 2.4, back, glow=0.4 * back)
    link = landed(T, INTRO_HITS, 3) * (1 - board)
    if link > 0:
        for i, j in ((0, 1), (1, 2), (0, 2)):
            p, q = QUEUE[i], QUEUE[j]
            mid = ((p[0] + q[0]) / 2, p[1] - (40 if j - i == 1 else 80))
            pts = [lerp2(lerp2(p, mid, t), lerp2(mid, q, t), t) for t in (k / 16 for k in range(17))]
            fr.polyline(pts, GOLD, 2.2, 0.8 * link, glow=0.3 * link)
        fr.text(L("最要好的三个人", "three best friends"), 940, 830, 22, GOLD, link, anchor="c", role="serif")
    if back > 0:
        fr.text(L("第三个：等下一把", "the third: wait for the next chair"), 1040, 830, 24, ROSE, back, anchor="c", role="serif")


# ---------------------------------------------------------------- M05 · dialect
DIA_COLS, DIA_ROWS = 9, 5
DIA_HUES = [TEAL, GOLD, BLUE, ROSE, LILAC, CORAL]


def _dialect_run(seed=11):
    rng = np.random.RandomState(seed)
    n = DIA_COLS * DIA_ROWS
    pos = [(560 + (i % DIA_COLS) * 100 + rng.uniform(-14, 14), 270 + (i // DIA_COLS) * 112 + rng.uniform(-12, 12)) for i in range(n)]
    nb = {i: set() for i in range(n)}
    for i in range(n):
        x, y = i % DIA_COLS, i // DIA_COLS
        for dx, dy in ((1, 0), (0, 1), (1, 1), (-1, 1)):
            if 0 <= x + dx < DIA_COLS and 0 <= y + dy < DIA_ROWS and (dx == 0 or dy == 0 or rng.rand() < 0.35):
                j = (y + dy) * DIA_COLS + x + dx
                nb[i].add(j)
                nb[j].add(i)
    lab = [int(rng.randint(len(DIA_HUES))) for _ in range(n)]
    start = list(lab)
    steps = []
    for _ in range(12):
        changed = 0
        for i in rng.permutation(n):
            votes = {}
            for j in nb[i]:
                votes[lab[j]] = votes.get(lab[j], 0) + 1
            top = max(votes.values())
            best = lab[i] if votes.get(lab[i], 0) == top else min(l for l, v in votes.items() if v == top)
            if best != lab[i]:
                lab[i] = best
                steps.append((int(i), best))
                changed += 1
        if not changed:
            break
    return pos, nb, start, steps, lab


DIA_POS, DIA_NB, DIA_START, DIA_STEPS, DIA_END = _dialect_run()


def dialect(fr, c):
    T = c.T
    lab = list(DIA_START)
    if T >= PUNCH + 0.6:
        k = int(len(DIA_STEPS) * clamp((T - PUNCH - 0.6) / 4.6))
        for i, l in DIA_STEPS[:k]:
            lab[i] = l
    for i, js in DIA_NB.items():
        for j in js:
            if j > i:
                same = lab[i] == lab[j]
                fr.line(DIA_POS[i], DIA_POS[j], DIA_HUES[lab[i]] if same else DIM, 1.6 if same else 1.0,
                        (0.55 if same else 0.3) * min(landed(T, INTRO_HITS, i % 6), landed(T, INTRO_HITS, j % 6)))
    for i, p in enumerate(DIA_POS):
        a = landed(T, INTRO_HITS, i % 6)
        if a <= 0:
            continue
        fr.dot(p, 22, NODE_BG, a)
        fr.ring(p, 22, DIA_HUES[lab[i]], 3.0, a, glow=0.25 * a)
        fr.dot(p, 7, DIA_HUES[lab[i]], 0.9 * a)
    if T >= PUNCH:
        zones = len(set(lab))
        fr.text(L(f"{zones} 种说法", f"{zones} ways of saying it"), 1400, 840, 22, MUTED, ease((T - PUNCH) / 0.6), anchor="r", role="mono")


# ---------------------------------------------------------------- M06 · Chladni plate
PLATE = (660, 230, 600)  # x, y, side


def _grains(n=1100, seed=6):
    rng = np.random.RandomState(seed)
    u, v = rng.rand(n), rng.rand(n)
    target = np.arccos(-0.35 * np.cos(2 * np.pi * v)) / np.pi  # the nodal line of cos(πx) + 0.35·cos(2πy)
    jitter = rng.normal(0, 0.006, n)
    phase = rng.rand(n) * 2 * np.pi
    return u, v, target + jitter, phase


GR_U, GR_V, GR_T, GR_PH = _grains()


def chladni(fr, c):
    T = c.T
    x0, y0, side = PLATE
    a = landed(T, INTRO_HITS, 0)
    fr.rect(x0, y0, side, side, fill="#0d2530", stroke="#5d7f86", width=2, alpha=a, r=6)
    fr.dot((x0 + side / 2, y0 + side / 2), 8, DIM, a)
    sand = landed(T, INTRO_HITS, 1)
    bow = landed(T, INTRO_HITS, 2)
    if bow > 0:
        bx = x0 + side + 18
        fr.line((bx + 40, y0 + 60), (bx - 10, y0 + 300), AMBER, 4, bow, glow=0.3 * bow)
        for k in range(3):
            r = 30 + 26 * k + 20 * pulse(T, INTRO_HITS[2:], 0.5)
            fr.ring((bx, y0 + 180), r, AMBER, 1.2, 0.35 * bow * (1 - k / 3), frac=0.3)
    gather = ease((T - PUNCH - 0.3) / 4.6) if T >= PUNCH else 0.0
    shake = pulse(T, INTRO_HITS[2:], 0.45) * (1 - gather)
    if sand > 0:
        xs = GR_U + (GR_T - GR_U) * gather
        for k in range(len(GR_U)):
            dx = math.sin(GR_PH[k] + T * 11) * 0.006 * shake
            px = x0 + side * clamp(xs[k] + dx, 0.004, 0.996)
            py = y0 + side * (0.004 + 0.992 * GR_V[k])
            fr.dot((px, py), 2.2, "#e8d9a8", 0.85 * sand)
    if gather > 0.85:
        t = ease((gather - 0.85) / 0.15)
        fr.rect(x0 + 4, y0 + 4, side * 0.45, side - 8, fill=TEAL, alpha=0.08 * t, r=4)
        fr.rect(x0 + side * 0.55, y0 + 4, side * 0.45 - 4, side - 8, fill=BLUE, alpha=0.08 * t, r=4)


# ---------------------------------------------------------------- M07 · chess
BOARD = (700, 240, 64)  # x, y, square
CH_PIECES = {"knight": (L("马", "N"), GOLD, (4, 4)), "bishop": (L("象", "B"), GOLD, (1, 7)), "rook": (L("车", "R"), GOLD, (0, 6)),
             "queen": (L("后", "Q"), ROSE, (6, 2)), "pawn": (L("兵", "P"), ROSE, (6, 1)), "king": (L("王", "K"), ROSE, (7, 0))}
CH_KNIGHT_TO, CH_TAKE_T, CH_SAC_T = (5, 2), PUNCH + 1.6, None


def _sq(col, row):
    x, y, s = BOARD
    return (x + col * s + s / 2, y + row * s + s / 2)


def _piece(fr, glyph, col, p, a):
    fr.dot(p, 25, NODE_BG, a)
    fr.ring(p, 25, col, 2.6, a, glow=0.25 * a)
    fr.text(glyph, p[0], p[1] + 9, 26, col, a, anchor="c", role="serif")


def chess(fr, c):
    T = c.T
    x, y, s = BOARD
    a = landed(T, INTRO_HITS, 0)
    for i in range(8):
        for j in range(8):
            fr.rect(x + i * s, y + j * s, s, s, fill="#12303a" if (i + j) % 2 else "#0b1f28", alpha=a)
    fr.rect(x, y, 8 * s, 8 * s, stroke="#5d7f86", width=1.6, alpha=a, r=2)
    gold_in, rose_in = landed(T, INTRO_HITS, 1), landed(T, INTRO_HITS, 2)
    jump = ease((T - hit(3)) / 0.45)
    taken = ease((T - hit(4)) / 0.45)
    opened = landed(T, INTRO_HITS, 5)
    slide = ease((T - CH_TAKE_T) / 0.9)
    # knight: jumps forward on hit 3, is taken by the pawn on hit 4
    n_at = lerp2(_sq(*CH_PIECES["knight"][2]), _sq(*CH_KNIGHT_TO), jump)
    if taken < 1:
        _piece(fr, CH_PIECES["knight"][0], GOLD, n_at, gold_in * (1 - taken))
    p_at = lerp2(_sq(*CH_PIECES["pawn"][2]), _sq(*CH_KNIGHT_TO), taken)
    _piece(fr, CH_PIECES["pawn"][0], ROSE, p_at, rose_in)
    _piece(fr, CH_PIECES["rook"][0], GOLD, _sq(*CH_PIECES["rook"][2]), gold_in)
    _piece(fr, CH_PIECES["king"][0], ROSE, _sq(*CH_PIECES["king"][2]), rose_in)
    if slide < 1:
        _piece(fr, CH_PIECES["queen"][0], ROSE, _sq(*CH_PIECES["queen"][2]), rose_in * (1 - slide * (slide > 0.9)))
    if opened > 0 and slide < 1:
        fr.line(_sq(1, 7), _sq(6, 2), GOLD, 2, 0.5 * opened * (1 - slide), glow=0.4 * opened, dash=[8, 7])
    _piece(fr, CH_PIECES["bishop"][0], GOLD, lerp2(_sq(1, 7), _sq(6, 2), slide), gold_in)
    # the score
    sx = x + 8 * s + 90
    if taken > 0:
        fr.text("−3", sx, 420, 64, ROSE, taken, role="mono", glow=0.3 * taken)
        fr.text(L("送掉一匹马", "a knight given away"), sx, 460, 20, MUTED, taken)
    if slide > 0.9:
        q = ease((slide - 0.9) / 0.1)
        fr.text("+9", sx, 560, 64, GOLD, q, role="mono", glow=0.4 * q)
        fr.text(L("吃掉对方的后", "the queen taken"), sx, 600, 20, MUTED, q)
        r = ease((T - CH_TAKE_T - 1.4) / 0.6)
        if r > 0:
            fr.line((sx, 640), (sx + 180, 640), DIM, 1.4, r)
            fr.text(L("净赚 +6", "net +6"), sx, 690, 30, TEAL, r, role="serif")


# ---------------------------------------------------------------- M08 · boats
WATER = 640
BOAT_X = {0: 680, 1: 1240}


def _boat(fr, cx, n, a, tilt=0.0):
    hw = 220
    pts = [(cx - hw, WATER - 50 - tilt), (cx + hw, WATER - 50 + tilt), (cx + hw - 50, WATER + 20 + tilt * 0.6), (cx - hw + 50, WATER + 20 - tilt * 0.6)]
    fr.polyline(pts, "#7aa5a6", 2.2, a, close=True, fill=PANEL_BG, fill_alpha=0.95 * a)
    fr.text(L(f"{n} 人", f"{n} aboard"), cx, WATER + 70, 22, MUTED, a, anchor="c", role="mono")


def _seat(side, k, tilt=0.0):
    """Four places per boat, left to right; the tilt lifts one end."""
    cx = BOAT_X[side]
    x = cx + (k - 1.5) * 100
    return (x, WATER - 92 + (x - cx) / 220 * tilt)


def boats(fr, c):
    T = c.T
    wa = landed(T, INTRO_HITS, 0)
    for k in range(5):
        xx = 200 + k * 30
        fr.line((xx - 40, WATER + 40 + k * 22), (1700 - k * 30, WATER + 40 + k * 22), "#1d4250", 1.4, wa * (0.8 - k * 0.12))
    # who is where: the eager one E starts on the left (2 aboard); R crosses from the right first, then E may go
    try_e = ease((T - PUNCH - 0.4) / 0.6) * (1 - ease((T - PUNCH - 2.2) / 0.5)) if T >= PUNCH else 0.0
    r_go = ease((T - PUNCH - 3.0) / 1.0) if T >= PUNCH else 0.0
    e_go = ease((T - PUNCH - 4.6) / 1.0) if T >= PUNCH else 0.0
    left_n = 2 + (r_go >= 1) - (e_go >= 1)
    right_n = 3 - (r_go >= 1) + (e_go >= 1)
    tilt_l = -26 * try_e
    _boat(fr, BOAT_X[0], left_n, landed(T, INTRO_HITS, 1), tilt_l)
    _boat(fr, BOAT_X[1], right_n, landed(T, INTRO_HITS, 2), 26 * try_e)
    tilt = {0: tilt_l, 1: -tilt_l}
    # (id, start boat, start place, later boat, later place, mover progress)
    people = [("E", 0, 1, 1, 0, e_go), ("x", 0, 2, 0, 2, 0.0), ("R", 1, 0, 0, 3, r_go), ("y", 1, 1, 1, 1, 0.0), ("z", 1, 2, 1, 2, 0.0)]
    for i, (pid, s0, k0, s1, k1, go) in enumerate(people):
        a = landed(T, INTRO_HITS, 3 + min(i, 2))
        if a <= 0:
            continue
        p = lerp2(_seat(s0, k0, tilt[s0]), _seat(s1, k1, tilt[s1]), go)
        if pid == "E" and try_e > 0:
            p = lerp2(p, (BOAT_X[0] + 250, WATER - 150), try_e)
        col = GOLD if pid == "E" else (TEAL if pid == "R" and r_go > 0 else "#9fbcbc")
        fr.dot(p, 30, NODE_BG, a)
        fr.ring(p, 30, col, 2.6, a, glow=0.4 * a if pid == "E" else 0)
    if 0 < try_e:
        fr.text("1 : 4", W / 2, 360, 44, ROSE, try_e, anchor="c", role="mono", glow=0.3 * try_e)
        fr.text(L("差得太多：不许", "too lopsided: not allowed"), W / 2, 408, 22, ROSE, try_e, anchor="c")
    if r_go > 0 and e_go < 1:
        q = r_go * (1 - e_go)
        fr.text("3 : 2", W / 2, 360, 44, TEAL, q, anchor="c", role="mono")
    if e_go > 0:
        fr.text("2 : 3", W / 2, 360, 44, GOLD, e_go, anchor="c", role="mono", glow=0.3 * e_go)
        fr.text(L("这下可以了", "now it is allowed"), W / 2, 408, 22, GOLD, e_go, anchor="c")
