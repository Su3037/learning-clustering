"""Module 07 · Kernighan–Lin refinement — the four films.

  story     popular science, cut to "We Never (Remix)": the five friends now sleep in two rooms, two beds and three,
            and may only swap one for one. Each person's D value, a pair's gain, a swap that pays 9, a trial that
            loses 8, the roll-back to the best prefix, a bigger group where one loss opens a door, and the empty
            prefix that ends it.
  concise   the essentials: the problem and the seed AE | BCD, D values, the pair gain and its −2w, one pass of
            trial swaps, the best prefix and roll-back, and the stop.
  advanced  why −2w, why negative gains are tried (an 8-node case: −1 then +7), why a prefix must be consecutive,
            seed dependence (AB | CDE is stuck at 5), counts versus areas, and the cost of a pass.
  lab       experiment walkthrough recorded from the real page (walkthrough.mjs → scripts/film/walkthrough.py).

Every value on G01 is read from site/data/m07-kernighan-lin/traces.json, which scripts/build-traces.mjs produces by
running site/engines/kl.js. The other examples (other seeds, the eight-node graph) run through the course's Python
reference, python/m07-kernighan-lin/reference.py, which tests/crosscheck.py checks against the engine.
"""
import importlib.util
import json
from pathlib import Path

from cine import (W, H, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, IVORY, MUTED, FAINT, DIM,
                  PANEL_BG, NODE_BG, clamp, ease, lerp, lerp2, title_card, panel, badge, code_panel, table, graph, fit, pulse,
                  count_hits, substrate)
from hooks import chess
from story import S, TRACK, INTRO_HITS, FILL1, FILL2, PHRASE, FILL3, FILL4, title_assemble, credits, MUSIC_LINE, landed

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m07-kernighan-lin/traces.json").read_text())
BRAND = L("Learning Clustering · Module 07 · Kernighan–Lin 改进", "Learning Clustering · Module 07 · Kernighan–Lin refinement")

_spec = importlib.util.spec_from_file_location("m07ref", ROOT / "python/m07-kernighan-lin/reference.py")
REF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REF)

IDS = [n if isinstance(n, str) else n["id"] for n in T["g01"]["nodes"]]
E5 = [tuple(e) if isinstance(e, list) else (e["u"], e["v"], e["w"]) for e in T["g01"]["edges"]]
P5RAW = {k: tuple(v) for k, v in T["g01"]["positions"].items()}
SEED = T["seed"]
R = T["run"]["result"]
P1, P2 = R["passes"]
TRIALS = [e for e in T["run"]["events"] if e["kind"] == "trial-swap"]
D0 = {n: d["D"] for n, d in TRIALS[0]["dValues"].items()}
CANDS0 = TRIALS[0]["candidates"]
CANDS1 = TRIALS[1]["candidates"]
AB1 = T["ab1"]["result"]
W5 = {"|".join(sorted((u, v))): w for u, v, w in E5}

# facts the captions state, checked against the engine output
assert SEED == {"A": 0, "B": 1, "C": 1, "D": 1, "E": 0} and P1["startCut"] == 12
assert D0 == {"A": 6, "B": 1, "C": -4, "D": 3, "E": 6}
assert [(c["a"], c["b"], c["gain"]) for c in CANDS0] == [("A", "D", 9), ("E", "B", 7), ("A", "C", 0), ("E", "C", 0), ("E", "D", -1), ("A", "B", -3)]
assert [(s["a"], s["b"], s["gain"], s["cutAfter"]) for s in P1["swaps"]] == [("A", "D", 9, 3), ("E", "C", -8, 11)]
assert [(c["a"], c["b"], c["gain"]) for c in CANDS1] == [("E", "C", -8), ("E", "B", -13)]
assert P1["prefixGains"] == [0, 9, 1] and P1["bestK"] == 1 and P1["acceptedCut"] == 3
assert [(s["a"], s["b"], s["gain"]) for s in P2["swaps"]] == [("E", "C", -8), ("D", "B", 2)] and P2["prefixGains"] == [0, -8, -6] and P2["bestK"] == 0
assert R["cut"] == 3 and R["stopReason"] == "no-positive-prefix"
assert AB1["passes"][0]["startCut"] == 8 and AB1["passes"][0]["swaps"][0]["gain"] == 5

# the swap E↔D: a cut check of the −2w rule, 12 → 13
_ed = dict(SEED, E=1, D=0)
assert REF.cut(E5, SEED) == 12 and REF.cut(E5, _ed) == 13

# a prefix must be consecutive: in pass 2, D↔B gained +2 only after E↔C; from the pass start alone it loses 12
_p2start = P2["start"]
_db = dict(_p2start, D=1, B=0)
DB_ALONE = REF.cut(E5, _p2start) - REF.cut(E5, _db)
assert DB_ALONE == -12

# seeds: AB | CDE is a local optimum at 5; the other seeds reach 3
SEEDS = {"AE|BCD": SEED, "AB|CDE": {"A": 0, "B": 0, "C": 1, "D": 1, "E": 1}, "BD|ACE": {"A": 1, "B": 0, "C": 1, "D": 0, "E": 1}, "CE|ABD": {"A": 1, "B": 1, "C": 0, "D": 1, "E": 0}}
SEED_RUNS = {k: (REF.cut(E5, s), REF.kernighan_lin(IDS, E5, s)["cut"]) for k, s in SEEDS.items()}
assert SEED_RUNS == {"AE|BCD": (12, 3), "AB|CDE": (5, 5), "BD|ACE": (16, 3), "CE|ABD": (12, 3)}

# an eight-node graph where the first trial loses 1 and the second gains 7 (the code lab's new graph)
BR_IDS = list("PQRSTUVW")
BR_E = [("P", "V", 4), ("P", "W", 2), ("Q", "S", 4), ("Q", "T", 2), ("Q", "U", 1), ("R", "S", 3), ("R", "T", 4), ("U", "W", 2)]
BR_POS = {"P": (80, 70), "W": (230, 70), "V": (80, 220), "U": (230, 220), "T": (400, 70), "Q": (400, 220), "R": (550, 70), "S": (550, 220)}
BR_SEED = {n: i % 2 for i, n in enumerate(BR_IDS)}
BR = REF.kernighan_lin(BR_IDS, BR_E, BR_SEED)
BR1 = BR["passes"][0]
assert REF.cut(BR_E, BR_SEED) == 7 and [s["gain"] for s in BR1["swaps"]] == [-1, 7, -9, 3] and BR1["best_k"] == 2 and BR["cut"] == 1
BR_STEP1 = dict(BR_SEED, **{BR1["swaps"][0]["a"]: 1, BR1["swaps"][0]["b"]: 0})


def key(u, v):
    return "|".join(sorted((u, v)))


def crossing(edges, side):
    return {key(u, v) for u, v, _ in edges if side[u] != side[v]}


def g01(fr, box, side=None, alpha=1.0, r=36, focus=(), locked=(), badges=None, weights=True):
    pos = fit(P5RAW, box)
    cols = {n: (TEAL if side[n] == 0 else BLUE) for n in pos} if side else {}
    graph(fr, pos, E5, cols, alpha, cut=crossing(E5, side) if side else set(), r=r, weights=weights, badges=badges, glow_nodes=focus)
    for n in locked:
        fr.ring(pos[n], r + 9, IVORY, 1.4, 0.7 * alpha, dash=[5, 5])
    for n in focus:
        fr.ring(pos[n], r + 9, GOLD, 2.4, alpha, glow=0.5 * alpha)
    return pos


def prefix_bars(fr, x, y, gains, alpha, best=None, shown=None, w=90, scale=24, labels=True):
    """Cumulative gains as bars over k = 0…n; the best prefix boxed in gold."""
    shown = len(gains) - 1 if shown is None else shown
    fr.line((x - 20, y), (x + len(gains) * (w + 30), y), DIM, 2, alpha)
    for k, g in enumerate(gains):
        if k > shown:
            continue
        bx, hgt = x + k * (w + 30), max(4, abs(g) * scale)
        col = GOLD if best == k else (TEAL if g > 0 else ROSE if g < 0 else MUTED)
        fr.rect(bx, y - hgt if g >= 0 else y, w, hgt, fill=col, alpha=0.85 * alpha, r=4)
        fr.text(("+" if g > 0 else "") + f"{g}", bx + w / 2, (y - hgt - 14) if g >= 0 else (y + hgt + 30), 24, col, alpha, anchor="c", role="mono")
        if labels:
            fr.text(f"k={k}", bx + w / 2, y + (40 if g >= 0 else -16) + (0 if g >= 0 else 0), 18, MUTED, alpha, anchor="c", role="mono")
        if best == k:
            fr.rect(bx - 10, y - max(abs(x_) for x_ in gains) * scale - 50, w + 20, max(abs(x_) for x_ in gains) * scale * 2 + 90, stroke=GOLD, width=2, alpha=alpha, r=6, dash=[6, 5])


# ====================================================================== popular film
FR = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev", "E": "Eva"}
FE = [(FR[u], FR[v], w) for u, v, w in E5]
ROOM_L, ROOM_R = (190, 300, 560, 420), (930, 300, 800, 420)
SEATS = {0: [(330, 420), (610, 600)], 1: [(1070, 420), (1330, 600), (1590, 420)]}


def seats(side):
    pos = {}
    for s in (0, 1):
        for n, p in zip(sorted(n for n in IDS if side[n] == s), SEATS[s]):
            pos[FR[n]] = p
    return pos


def rooms(fr, side, alpha=1.0, prev=None, k=1.0, locked=(), focus=(), badges=None, counter=True, count_val=None, count_glow=0.0):
    """Two rooms (two beds and three); friends in their beds; split friendships drawn rose."""
    for (x, y, w, h), label in ((ROOM_L, L("左屋 · 两张床", "LEFT ROOM · TWO BEDS")), (ROOM_R, L("右屋 · 三张床", "RIGHT ROOM · THREE BEDS"))):
        fr.rect(x, y, w, h, fill=PANEL_BG, stroke=FAINT, width=1.4, alpha=0.9 * alpha, r=18)
        fr.text(label, x + 24, y + 38, 18, MUTED, alpha, spacing=2)
    now = seats(side)
    pos = {n: lerp2(p0, now[n], ease(k)) for n, p0 in seats(prev).items()} if prev and k < 1 else now
    shown = side if not prev or k >= 0.5 else prev
    cols = {FR[n]: (TEAL if shown[n] == 0 else BLUE) for n in IDS}
    cut = {key(FR[u], FR[v]) for u, v, _ in E5 if shown[u] != shown[v]}
    graph(fr, pos, FE, cols, alpha, cut=cut, r=46, name_size=22, badges={FR[n]: b for n, b in (badges or {}).items()},
          glow_nodes=[FR[n] for n in focus])
    for n in locked:
        fr.ring(pos[FR[n]], 56, IVORY, 1.4, 0.75 * alpha, dash=[5, 5])
    for n in focus:
        fr.ring(pos[FR[n]], 56, GOLD, 2.4, alpha, glow=0.5 * alpha)
    if counter:
        v = REF.cut(E5, shown) if count_val is None else count_val
        fr.text(L("被拆散的交情", "friendships split"), W / 2, 200, 22, MUTED, alpha, anchor="c", spacing=2)
        fr.text(f"{v:g}", W / 2, 262, 56, ROSE, alpha, anchor="c", role="mono", glow=0.2 + count_glow)
    return pos


AFTER1 = P1["accepted"]
TRIAL2 = TRIALS[1]["after"]


def p_rule(fr, c):
    badges = {n: f"D {D0[n]:+d}" for n in IDS} if c.on(1) else None
    rooms(fr, SEED, 1.0, badges=badges)
    if c.on(1):
        fr.text(L("规则：只能一换一，床位数不变", "the rule: swap one for one, the bed count stays"), W / 2, 790, 26, IVORY, c.p(1), anchor="c")
    if c.on(1):
        fr.text(L("D = 屋外朋友 − 屋里朋友", "D = friends outside − friends inside"), W / 2, 840, 26, GOLD, c.p(1), anchor="c", role="serif")


def p_title(fr, c):
    title_assemble(fr, c, L("先试探，再回退", "Try, Then Roll Back"), L("KL 改进 · KERNIGHAN–LIN", "KERNIGHAN–LIN REFINEMENT"), "MODULE 07")


def cand_list(fr, x, y, cands, alpha, n_shown, best=0, names=True, size=26, lh=50):
    for i, cd in enumerate(cands[:n_shown]):
        a, b = (FR[cd["a"]], FR[cd["b"]]) if names else (cd["a"], cd["b"])
        col = GOLD if i == best else (ROSE if cd["gain"] < 0 else IVORY)
        fr.text(f"{a} ↔ {b}", x, y + i * lh, size, col, alpha, role="serif")
        fr.text(("+" if cd["gain"] > 0 else "") + f"{cd['gain']}", x + 300, y + i * lh, size, col, alpha, role="mono", anchor="r")


def p_gain(fr, c):
    rooms(fr, SEED, 1.0, badges={n: f"D {D0[n]:+d}" for n in IDS}, counter=False)
    if c.on(1):
        fr.text(L("g = D(a) + D(b) − 2·交情(a, b)", "g = D(a) + D(b) − 2·friendship(a, b)"), W / 2, 230, 30, GOLD, c.p(1), anchor="c", role="serif")
    if c.T >= FILL1[0]:
        n = 1 + count_hits(c.T, FILL1) * 2
        cand_list(fr, 760, 790, CANDS0, landed(c.T, FILL1, 0), min(6, n), size=22, lh=34)


def p_swap(fr, c):
    k = clamp(c.span(0, 1) * 1.4)
    rooms(fr, AFTER1, 1.0, prev=SEED, k=k, focus=("A", "D") if k < 1 else (), locked=("A", "D") if c.on(1) else (), count_glow=0.4 * pulse(c.T, [c.at(0) + 1.2], 0.6))
    if c.on(2):
        fr.text(L("还能动的：Eva，和 Ben、Cai", "free to move: Eva, and Ben, Cai"), W / 2, 830, 26, MUTED, c.p(2), anchor="c")


def p_worse(fr, c):
    n = count_hits(c.T, FILL2)
    k = clamp((c.T - FILL2[0]) / 1.2) if c.T >= FILL2[0] else 0
    rooms(fr, TRIAL2 if k > 0 else AFTER1, 1.0, prev=AFTER1 if k > 0 else None, k=k, locked=("A", "D") + (("E", "C") if k >= 1 else ()),
          focus=("E", "C") if 0 < k < 1 else (), count_glow=0.5 * pulse(c.T, FILL2, 0.5))
    if not c.T >= FILL2[0]:
        cand_list(fr, 800, 800, CANDS1, c.p(0), 2, best=0, size=24, lh=40)
    if c.on(2):
        fr.text(L("试探 · 不是接受", "a trial · not an acceptance"), W / 2, 850, 30, AMBER, c.p(2), anchor="c", role="serif", glow=0.25 * c.p(2))


def p_back(fr, c):
    a = c.p(0, 1.0)
    fr.text(L("这一轮的累计收益", "this pass, cumulative gain"), W / 2, 260, 26, MUTED, a, anchor="c", spacing=2)
    shown = 0 if not c.on(1) else 1 + min(1, int(c.since(1) / 1.2))
    prefix_bars(fr, 690, 600, P1["prefixGains"], a, shown=shown, w=120, scale=26)


def p_keep(fr, c):
    a = c.p(0)
    prefix_bars(fr, 330, 560, P1["prefixGains"], 1.0, best=1 if c.T >= PHRASE[0] else None, w=80, scale=18)
    k = clamp((c.T - PHRASE[0]) / 1.4) if c.T >= PHRASE[0] else 0
    if k > 0:
        rooms_small(fr, TRIAL2, AFTER1, k, 1.0)
    else:
        rooms_small(fr, TRIAL2, None, 1, a)


def rooms_small(fr, end, start_from, k, alpha):
    """A compact pair of rooms on the right, used while the bars hold the left."""
    ox, sc = 760, 0.62
    box = {0: [(ox + 140, 470), (ox + 300, 600)], 1: [(ox + 560, 470), (ox + 760, 600), (ox + 960, 470)]}

    def at(side):
        pos = {}
        for s in (0, 1):
            for n, p in zip(sorted(n for n in IDS if side[n] == s), box[s]):
                pos[FR[n]] = p
        return pos
    fr.rect(ox + 40, 380, 380, 300, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.9 * alpha, r=14)
    fr.rect(ox + 460, 380, 620, 300, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.9 * alpha, r=14)
    target = start_from if start_from is not None else end
    now, before = at(target), at(end)
    pos = {n: lerp2(before[n], now[n], ease(k)) for n in now}
    shown = target if k >= 0.5 else end
    cols = {FR[n]: (TEAL if shown[n] == 0 else BLUE) for n in IDS}
    graph(fr, pos, FE, cols, alpha, cut={key(FR[u], FR[v]) for u, v, _ in E5 if shown[u] != shown[v]}, r=40, name_size=20)
    fr.text(f"cut {REF.cut(E5, shown)}", ox + 560, 740, 30, ROSE if REF.cut(E5, shown) > 3 else TEAL, alpha, anchor="c", role="mono")


def p_breath(fr, c):
    a = c.p(0, 1.4)
    fr.text(L("亏的那一步，何必试？", "Why try the losing swap?"), W / 2, 500, 52, GOLD, a, anchor="c", role="serif", glow=0.25 * a)


def p_why(fr, c):
    state = BR_SEED if not c.on(1) else (BR_STEP1 if c.T < FILL3[0] else BR1["accepted"])
    pos = fit(BR_POS, (380, 280, 1540, 640))
    cols = {n: (TEAL if state[n] == 0 else BLUE) for n in BR_IDS}
    graph(fr, pos, BR_E, cols, c.p(0, 1.0), cut=crossing(BR_E, state), r=38)
    fr.text(f"cut {REF.cut(BR_E, state)}", W / 2, 230, 40, ROSE if REF.cut(BR_E, state) > 1 else TEAL, c.p(0), anchor="c", role="mono",
            glow=0.4 * pulse(c.T, FILL3, 0.5))
    if c.on(1):
        g = [s["gain"] for s in BR1["swaps"]][:1 + (c.T >= FILL3[0])]
        fr.text("  ".join(("+" if x > 0 else "") + str(x) for x in g), W / 2, 760, 40, GOLD, c.p(1), anchor="c", role="mono")


def p_round2(fr, c):
    rooms(fr, AFTER1, 1.0, counter=True)
    if c.on(1):
        prefix_bars(fr, 760, 790, P2["prefixGains"], c.p(1), best=0 if c.on(2) else None, w=80, scale=6, labels=False)


def p_chip(fr, c):
    a = c.p(0, 0.8)
    substrate(fr, 0.6 * a)
    for i in range(12):
        for j in range(5):
            x, y = 380 + i * 100, 300 + j * 90
            left = i < 6
            sw = (i, j) in ((5, 2), (6, 1)) and c.T >= FILL4[0]
            col = (BLUE if left else TEAL) if sw else (TEAL if left else BLUE)
            fr.rect(x, y, 56, 40, fill=NODE_BG, stroke=col, width=2.2 if sw else 1.4, alpha=a, r=3, glow=0.4 if sw else 0)
    fr.line((958, 260), (958, 760), GOLD, 2, 0.6 * a, dash=[10, 7])
    if c.T >= FILL4[0]:
        fr.text(L("两半个数固定：成对交换", "two halves of fixed size: swaps in pairs"), W / 2, 840, 24, GOLD, ease((c.T - FILL4[0]) / 0.6), anchor="c")


def p_outro(fr, c):
    lines = [(L("成对交换，屋子大小不变", "Swap in pairs; the rooms keep their size"), TEAL, 0),
             (L("每一步都试，亏的也试", "Try every step, even the losses"), TEAL, 1),
             (L("只留最好的那段前缀", "Keep only the best prefix"), GOLD, 2)]
    for s, col, k in lines:
        if c.on(k):
            fr.text(s, W / 2, 380 + k * 90, 40, col, c.p(k, 1.2) * (1 - 0.6 * c.p(3)), anchor="c", role="serif")
    if c.on(3):
        a = c.p(3, 1.4)
        fr.text(L("一次只搬一个人，行吗？", "What if one person moves at a time?"), W / 2, 720, 40, GOLD, a, role="serif", anchor="c", glow=0.3 * a)


def p_end(fr, c):
    if not c.on(1):
        a = c.p(0, 1.0)
        g01(fr, (260, 240, 860, 720), AFTER1, a)
        fr.text(L("单步看试探 · 看累计收益 · 换种子", "step through the trials · read the gains · change the seed"), 1360, 500, 26, GOLD, a, anchor="c")
    else:
        credits(fr, c, [(L("先试探，再回退", "Try, Then Roll Back"), GOLD, 44),
                        (L("Learning Clustering · Module 07 · Kernighan–Lin 改进", "Learning Clustering · Module 07 · Kernighan–Lin refinement"), IVORY, 24),
                        (L("原作 FanqinZeng（Issue #6）· 人数固定的引入与 D、−2w、锁定、最佳前缀的讲解顺序来自原作", "Original work by FanqinZeng (Issue #6) · the fixed head-count framing and the order D, −2w, locks, best prefix come from it"), MUTED, 20),
                        (L("所有数值由本课程引擎 site/engines/kl.js 计算", "Every value is computed by this course's engine, site/engines/kl.js"), MUTED, 20),
                        (MUSIC_LINE, MUTED, 18)], k=1)


STORY = Film(
    "story", "popular", L("先试探，再回退", "Try, Then Roll Back"), None, BRAND, poster_at=36.5, music=TRACK, seed=7,
    why=L("从一步弃子讲起：先亏 3，两步后赚回 9。再看五个朋友分住两间屋，两张床和三张床，只许一换一。每个人的 D 值、一对的收益、省下 9 的交换、亏 8 的试探、回退到最佳前缀；人更多时亏一步可能打开一扇门；最后空前缀让一切停下。",
          "It opens with a chess sacrifice: lose 3 now, take 9 two moves later. Then five friends in two rooms, two beds and three, allowed only one-for-one swaps. Each person's D value, a pair's gain, a swap that saves 9, a trial that loses 8, the roll-back to the best prefix; with more people one loss can open a door; and the empty prefix that ends it."),
    scenes=[
        Scene("p-chess", chess, [Beat(L("下棋时，高手有时故意送掉一个子。", "In chess, a strong player sometimes gives a piece away."), 4.6), Beat(L("眼下，亏了 3 分——", "Three points down, for now —"), 4.6)],
              chapter=L("序 · 弃子", "PROLOGUE · A SACRIFICE"), until=S["intro_end"]),
        Scene("p-chess2", chess, [Beat(None, 1.0), Beat(L("路一打开，两步后赢回 9 分。", "the line opens, and two moves later nine come back."), 4.8)],
              until=S["groove"]),
        Scene("p-rule", p_rule, [Beat(L("五个朋友住两间屋：拆散的交情 12。", "Five friends, two rooms: 12 in friendships split."), 4.4), Beat(L("只能一换一。每人的 D：屋外朋友减屋里朋友。", "Swap one for one only. Each person's D: friends outside minus inside."), 5.6), Beat(L("D 就是他一个人搬走能省多少。", "D is what moving alone would save."), 4.2)],
              chapter=L("序 · 两间屋", "PROLOGUE · TWO ROOMS"), until=S["roll"]),
        Scene("p-title", p_title, [Beat(None, 4.5)], fade=False, until=37.0),
        Scene("p-gain", p_gain, [Beat(L("换一对：两人的 D 相加——", "Swap a pair: add the two D values —"), 3.6),
                                 Beat(L("两人若是朋友，再减两倍交情。", "if they're friends, take off twice that."), 4.2),
                                 Beat(L("Ada↔Dev：9；Eva↔Dev：−1。", "Ada↔Dev: 9. Eva↔Dev: −1."), 4.6)],
              chapter=L("一 · 一对", "I · A PAIR"), until=S["fill1_end"]),
        Scene("p-swap", p_swap, [Beat(L("Ada 和 Dev 换屋：12 → 3。", "Ada and Dev swap: 12 → 3."), 3.4),
                                 Beat(L("两人锁定，这一轮不再动。", "Both lock for the rest of the round."), 3.6),
                                 Beat(L("剩下 Eva、Ben、Cai。", "Still free: Eva, Ben, Cai."), 3.2)],
              until=S["accent"]),
        Scene("p-worse", p_worse, [Beat(L("剩下的交换，全是亏的。", "Every swap left is a loss."), 3.4),
                                   Beat(L("照样换：Eva↔Cai，3 → 11。", "Swap anyway: Eva↔Cai, 3 → 11."), 4.0),
                                   Beat(L("这只是试探。", "This is only a trial."), 3.0)],
              chapter=L("二 · 试探", "II · A TRIAL"), until=S["phrase"]),
        Scene("p-back", p_back, [Beat(L("回头看这一轮——", "Look back over the round —"), 2.8),
                                 Beat(L("累计 +9，然后 +1。", "+9 in all, then +1."), 3.2)],
              until=89.0),
        Scene("p-keep", p_keep, [Beat(L("只留最好的前缀：第一步。", "Keep the best prefix: step one."), 3.6),
                                 Beat(L("回退到 3。", "Roll back to 3."), 2.6)],
              until=S["breath"]),
        Scene("p-breath", p_breath, [Beat(None, 4.6)], until=S["reentry"]),
        Scene("p-why", p_why, [Beat(L("人多时，亏一步可能打开一扇门：", "With more people, one loss can open a door:"), 4.2),
                               Beat(L("先 −1，接着 +7。", "−1 first, then +7."), 3.0),
                               Beat(L("只肯赚的会停在 7；KL 走到 1。", "Refusing losses stops at 7; KL gets to 1."), 5.2)],
              chapter=L("三 · 一扇门", "III · A DOOR"), until=S["fill3_end"]),
        Scene("p-round2", p_round2, [Beat(L("第二轮，全部解锁。", "Round two: all unlocked."), 3.0),
                                     Beat(L("−8，再 −6：都不如不动。", "−8, then −6: staying put wins."), 4.2),
                                     Beat(L("空前缀胜出：停。", "The empty prefix wins: stop."), 3.4)],
              chapter=L("四 · 第二轮", "IV · ROUND TWO"), until=S["fill4"]),
        Scene("p-chip", p_chip, [Beat(L("芯片上：两半个数固定，成对交换单元。", "On a chip: halves of fixed size, cells swapped in pairs."), 5.4)],
              until=141.5),
        Scene("p-outro", p_outro, [Beat(L("成对交换，屋子大小不变。", "Swap in pairs; the rooms keep their size."), 6.0),
                                   Beat(L("每一步都试，亏的也试。", "Try every step, even the losses."), 6.0),
                                   Beat(L("最后只留最好的那段前缀。", "Then keep only the best prefix."), 7.0),
                                   Beat(L("一次只搬一个人呢？下一章见。", "What if one person moves at a time? Next module."), 8.0)],
              chapter=L("尾声", "CODA"), until=S["quiet"]),
        Scene("p-end", p_end, [Beat(L("下面的实验里，单步看每一次试探。", "In the lab below, step through every trial."), 6.0),
                               Beat(None, 10.0)], until=S["end"]),
    ])


# ====================================================================== concise film
def k_title(fr, c):
    title_card(fr, L("Kernighan–Lin 改进", "Kernighan–Lin Refinement"), L("KERNIGHAN–LIN  ·  精讲", "THE ESSENTIALS"), c.p(0, 1.2), kicker="MODULE 07")


def k_problem(fr, c):
    g01(fr, (240, 260, 860, 740), SEED if c.on(1) else None, c.p(0, 1.0))
    panel(fr, 1040, 250, 680, 440, c.p(0), L("问题", "THE PROBLEM"))
    items = [(L("输入：一个已有的二分，两侧人数固定", "Input: an existing bisection, side sizes fixed"), IVORY, 0),
             (L("种子 AE | BCD：cut 12", "Seed AE | BCD: cut 12"), ROSE, 1),
             (L("唯一的操作：左右各一个，互换", "The only move: swap one from each side"), GOLD, 2),
             (L("目标：让 cut 变小", "Goal: make the cut smaller"), TEAL, 2)]
    y = 350
    for s, col, b in items:
        if c.on(b):
            h = fr.paragraph(s, 1070, y, 26, 620, col, c.p(b))
            y += h + 20


def k_dvalues(fr, c):
    g01(fr, (200, 280, 760, 720), SEED, 1.0, badges={n: f"D {D0[n]:+d}" for n in IDS} if c.on(1) else None)
    ext = {n: TRIALS[0]["dValues"][n]["ext"] for n in IDS}
    inn = {n: TRIALS[0]["dValues"][n]["int"] for n in IDS}
    rows = [[L("节点", "Node"), L("外部", "Ext."), L("内部", "Int."), "D"]] + [[n, str(ext[n]), str(inn[n]), f"{D0[n]:+d}"] for n in IDS]
    table(fr, 1000, 300, [140, 160, 160, 160], [[tr(x) for x in r] for r in rows], c.p(0), size=28, lh=62, colors={(i + 1, 3): (TEAL if D0[n] > 0 else ROSE) for i, n in enumerate(IDS)})
    if c.on(2):
        fr.text(L("D(v) = 外部 − 内部：只把 v 换过去，cut 降多少", "D(v) = external − internal: how much the cut drops if v alone moves"), 1320, 760, 24, GOLD, c.p(2), anchor="c")


def k_gain(fr, c):
    pos = g01(fr, (200, 300, 760, 720), SEED, 1.0)
    fr.text("g(a, b) = D(a) + D(b) − 2·w(a, b)", 1340, 300, 34, GOLD, c.p(0), anchor="c", role="mono")
    if c.on(1):
        a = c.p(1)
        panel(fr, 1000, 360, 680, 210, a, L("为什么减 2w", "WHY −2w"))
        fr.paragraph(L("E–D 这条边被两个 D 都算成外部边；交换后 E、D 仍分处两侧，它依然被切。",
                       "Both D values count the E–D edge as external; after the swap E and D are still on opposite sides, so it is still cut."), 1030, 440, 23, 620, IVORY, a)
    if c.on(2):
        rows = [[L("对", "Pair"), "D(a)+D(b)", "−2w", "g"]] + [[f"{x['a']}↔{x['b']}", str(x["Da"] + x["Db"]), str(-2 * x["w"]), ("+" if x["gain"] > 0 else "") + str(x["gain"])] for x in CANDS0]
        table(fr, 1040, 610, [150, 190, 120, 120], [[tr(x) for x in r] for r in rows], c.p(2), size=22, lh=38, colors={(1, 3): GOLD, (5, 3): ROSE, (6, 3): ROSE})


def k_pass(fr, c):
    step = 0 if not c.on(1) else (1 if not c.on(2) else 2)
    side = SEED if step == 0 else (AFTER1 if step == 1 else TRIAL2)
    locked = () if step == 0 else (("A", "D") if step == 1 else ("A", "D", "E", "C"))
    g01(fr, (200, 300, 760, 720), side, 1.0, locked=locked)
    rows = [[L("步", "Step"), L("试探交换", "Trial swap"), L("收益", "Gain"), "cut", L("累计", "Cum.")]]
    for s in P1["swaps"][:step]:
        rows.append([str(s["index"]), f"{s['a']}↔{s['b']}", ("+" if s["gain"] > 0 else "") + str(s["gain"]), str(s["cutAfter"]), ("+" if s["cumulative"] > 0 else "") + str(s["cumulative"])])
    table(fr, 960, 320, [100, 220, 140, 120, 140], [[tr(x) for x in r] for r in rows], c.p(0), size=28, lh=64, colors={(2, 2): ROSE, (2, 3): ROSE})
    if c.on(2):
        fr.text(L("收益为负也照走：这是试探", "a negative gain is taken anyway: it is a trial"), 1320, 600, 26, AMBER, c.p(2), anchor="c")
    if c.on(3):
        fr.text(L("左侧没有未锁定的点：本轮试探结束", "no unlocked node on the left: the trials end"), 1320, 660, 24, MUTED, c.p(3), anchor="c")


def k_prefix(fr, c):
    prefix_bars(fr, 300, 560, P1["prefixGains"], c.p(0), best=1 if c.on(1) else None, w=110, scale=22)
    if c.on(1):
        g01(fr, (1060, 300, 1640, 700), AFTER1, c.p(1))
        fr.text(L("从起点只应用 A↔D：ABC | DE，cut 3", "from the start apply only A↔D: ABC | DE, cut 3"), 1350, 790, 24, TEAL, c.p(1), anchor="c")
    if c.on(2):
        fr.text(L("第 2 步被撤回：试探 ≠ 接受", "step 2 is undone: trial ≠ accepted"), 560, 850, 26, GOLD, c.p(2), anchor="c")


def k_stop(fr, c):
    g01(fr, (200, 300, 760, 720), AFTER1, 1.0)
    panel(fr, 960, 260, 740, 300, c.p(0), L("第二轮", "PASS 2"))
    fr.text(L("全部解锁，从 cut 3 出发", "all unlocked, from cut 3"), 1000, 350, 26, IVORY, c.p(0))
    if c.on(1):
        fr.text(L("试探：E↔C −8，D↔B +2", "trials: E↔C −8, D↔B +2"), 1000, 410, 26, IVORY, c.p(1), role="mono")
        fr.text(L("累计：0，−8，−6", "cumulative: 0, −8, −6"), 1000, 470, 26, ROSE, c.p(1), role="mono")
    if c.on(2):
        fr.text(L("空前缀 k* = 0 胜出 → 停止，cut 3", "the empty prefix k* = 0 wins → stop, cut 3"), 1330, 640, 30, GOLD, c.p(2), anchor="c", role="serif", glow=0.3 * c.p(2))


def k_take(fr, c):
    items = [(L("一换一：两侧人数始终不变", "One for one: the side sizes never change"), TEAL),
             (L("g = D(a) + D(b) − 2w：减掉两人之间的边", "g = D(a) + D(b) − 2w: take off the edge between them"), GOLD),
             (L("走完整轮，负收益也试探；每点锁定一次", "Finish the pass, trying negative gains; each node locks once"), AMBER),
             (L("只接受最佳前缀；空前缀就停止", "Accept only the best prefix; stop on the empty one"), TEAL)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 260 + i * 120
            fr.rect(220, y, 1480, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 58, 28, col, a, role="mono")
            fr.text(s, 360, y + 58, 28, IVORY, a)


CONCISE = Film(
    "concise", "concise", L("精讲：交换、试探、回退", "The essentials"), None, BRAND, poster_at=40.0, music="score:steady", seed=27,
    why=L("只讲必须掌握的：问题与种子 AE | BCD、D 值、成对收益与 −2w、一轮试探交换、最佳前缀与回退、停止条件。",
          "Only what you must know: the problem and the seed AE | BCD, D values, the pair gain and its −2w, one pass of trial swaps, the best prefix and roll-back, and when it stops."),
    scenes=[
        Scene("k00-title", k_title, [Beat(None, 3.0)]),
        Scene("k01-problem", k_problem, [Beat(L("KL 不从零分组，而是改进一个已有的二分。", "KL doesn't group from scratch; it improves an existing bisection."), 4.2),
                                         Beat(L("本章的种子是 AE | BCD，cut 12。", "This chapter's seed is AE | BCD, cut 12."), 3.2),
                                         Beat(L("唯一的操作：左右各一个互换，两侧人数不变。", "The only move: swap one from each side; the side sizes stay."), 4.4)],
              chapter=L("问题", "THE PROBLEM")),
        Scene("k02-dvalues", k_dvalues, [Beat(L("每个节点先算外部与内部边权。", "First, each node's external and internal weight."), 3.6),
                                         Beat(L("D = 外部 − 内部：A 是 +6，C 是 −4。", "D = external − internal: A is +6, C is −4."), 4.0),
                                         Beat(L("D 是只把这个点换过去时 cut 的下降量。", "D is how much the cut drops if that node alone moves."), 4.0)],
              chapter=L("D 值", "D VALUES")),
        Scene("k03-gain", k_gain, [Beat(L("一对交换的收益：两个 D 相加，再减 2w。", "A pair swap's gain: the two D values added, minus 2w."), 4.4),
                                   Beat(L("E–D 被两个 D 都算成外部边，交换后它仍被切，所以减两次。", "Both D values count E–D as external, and it stays cut after the swap, so it comes off twice."), 6.0),
                                   Beat(L("六个候选里，A↔D 最大：+9；E↔D 是 −1。", "Of the six candidates A↔D is largest, +9; E↔D is −1."), 4.6)],
              chapter=L("成对收益", "THE PAIR GAIN")),
        Scene("k04-pass", k_pass, [Beat(L("一轮：选最大收益对，交换，锁定，重算 D。", "One pass: pick the largest-gain pair, swap, lock, recompute D."), 4.6),
                                   Beat(L("第 1 步 A↔D，cut 12 → 3。", "Step 1, A↔D: cut 12 → 3."), 3.0),
                                   Beat(L("第 2 步剩下的全是负数，照样走 E↔C：cut 升到 11。", "At step 2 every gain is negative; take E↔C anyway: the cut rises to 11."), 5.2),
                                   Beat(L("左侧没有可动的点，本轮试探结束。", "No movable node is left on the left; the trials end."), 3.4)],
              chapter=L("一轮试探", "ONE PASS")),
        Scene("k05-prefix", k_prefix, [Beat(L("累计收益：0、+9、+1。", "Cumulative gains: 0, +9, +1."), 3.0),
                                       Beat(L("最大的是 k = 1：从起点只应用 A↔D，cut 3。", "The largest is k = 1: from the start, apply only A↔D, cut 3."), 4.6),
                                       Beat(L("第 2 步被撤回：试探不等于接受。", "Step 2 is undone: a trial is not an acceptance."), 3.6)],
              chapter=L("最佳前缀", "THE BEST PREFIX")),
        Scene("k06-stop", k_stop, [Beat(L("第二轮从 cut 3 出发，全部解锁。", "Pass 2 starts from cut 3, everything unlocked."), 3.4),
                                   Beat(L("累计 −8、−6，都不如什么都不做。", "Cumulative −8, −6: neither beats doing nothing."), 4.0),
                                   Beat(L("空前缀胜出，算法停止。", "The empty prefix wins, and the algorithm stops."), 3.2)],
              chapter=L("停止", "THE STOP")),
        Scene("k07-take", k_take, [Beat(L("记住四点。", "Four things to keep."), 1.4),
                                   Beat(L("一换一，人数不变；收益减 2w；", "One for one, sizes fixed; the gain loses 2w;"), 3.2),
                                   Beat(L("负收益也试探，只接受最佳前缀。", "try negative gains too, accept only the best prefix."), 3.2),
                                   Beat(L("下面的实验里，单步看每一次试探。", "Step through every trial in the lab below."), 3.4)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])


# ====================================================================== advanced film
def a_title(fr, c):
    title_card(fr, L("Kernighan–Lin 改进", "Kernighan–Lin Refinement"), L("进阶：收益、前缀与局部最优", "IN DEPTH: GAINS, PREFIXES AND LOCAL OPTIMA"), c.p(0, 1.2), kicker="MODULE 07")


def a_why2w(fr, c):
    g01(fr, (200, 300, 760, 720), SEED if not c.on(2) else _ed, 1.0, focus=("E", "D"))
    panel(fr, 960, 240, 760, 460, c.p(0), L("交换 a、b 时 cut 怎么变", "HOW THE CUT CHANGES WHEN a, b SWAP"))
    fr.paragraph(L("a 搬过去：cut 降 D(a)。b 搬过来：再降 D(b)。", "a moves across: the cut drops by D(a). b moves back: it drops by D(b)."), 1000, 330, 24, 680, IVORY, c.p(0))
    if c.on(1):
        fr.paragraph(L("但 a–b 这条边在两个 D 里都算作“将被修好”，实际上交换后它仍跨两侧：多算了 2w。",
                       "But the a–b edge is counted as “about to be fixed” in both D values, while after the swap it still crosses: 2w too many."), 1000, 420, 24, 680, IVORY, c.p(1))
    if c.on(2):
        fr.text(L("E↔D：6 + 3 − 2×5 = −1；实际 cut 12 → 13", "E↔D: 6 + 3 − 2×5 = −1; actual cut 12 → 13"), 1000, 600, 26, GOLD, c.p(2), role="mono")


def a_negative(fr, c):
    state = BR_SEED if not c.on(1) else (BR_STEP1 if not c.on(2) else BR1["accepted"])
    pos = fit(BR_POS, (240, 300, 1060, 620))
    graph(fr, pos, BR_E, {n: (TEAL if state[n] == 0 else BLUE) for n in BR_IDS}, c.p(0, 1.0), cut=crossing(BR_E, state), r=34)
    fr.text(f"cut {REF.cut(BR_E, state)}", 650, 250, 34, ROSE if REF.cut(BR_E, state) > 1 else TEAL, c.p(0), anchor="c", role="mono")
    prefix_bars(fr, 1180, 560, [0] + [sum(s["gain"] for s in BR1["swaps"][:i + 1]) for i in range(4)], c.p(1), best=BR1["best_k"] if c.on(2) else None, w=70, scale=22)
    if c.on(3):
        fr.paragraph(L("只接受正收益的贪心：第一步就是 −1，停在 cut 7。KL 走完整轮，保留前两步：cut 1。",
                       "A greedy that only accepts positive gains sees −1 first and stops at cut 7. KL finishes the pass and keeps two steps: cut 1."), 240, 780, 26, 1440, GOLD, c.p(3))


def a_prefix(fr, c):
    panel(fr, 260, 240, 1400, 260, c.p(0), L("前缀必须连续", "A PREFIX MUST BE CONSECUTIVE"))
    fr.paragraph(L("每一步的收益都是在前面几步已经做过的情况下算的。跳过中间一步，后面的收益就不再成立。",
                   "Each step's gain is computed with the earlier steps already made. Skip one in the middle, and the later gains no longer hold."), 300, 330, 26, 1320, IVORY, c.p(0))
    if c.on(1):
        rows = [[L("第二轮", "Pass 2"), L("在序列里", "In sequence"), L("从起点单独做", "Alone from the start")],
                ["D↔B", "+2", str(DB_ALONE)]]
        table(fr, 480, 600, [300, 340, 400], [[tr(x) for x in r] for r in rows], c.p(1), size=30, lh=70, colors={(1, 1): TEAL, (1, 2): ROSE})
    if c.on(2):
        fr.text(L("只取从第 1 步起的前 k 步，k = 0 合法", "take only the first k steps, from step 1; k = 0 is valid"), W / 2, 860 - 20, 28, GOLD, c.p(2), anchor="c")


def a_seed(fr, c):
    rows = [[L("种子", "Seed"), L("起点 cut", "Start cut"), L("KL 结果", "KL result")]] + [[k, str(v[0]), str(v[1])] for k, v in SEED_RUNS.items()]
    table(fr, 300, 300, [300, 240, 240], [[tr(x) for x in r] for r in rows], c.p(0), size=30, lh=70, colors={(2, 2): ROSE, (1, 2): TEAL, (3, 2): TEAL, (4, 2): TEAL})
    if c.on(1):
        g01(fr, (1080, 300, 1660, 700), SEEDS["AB|CDE"], c.p(1))
        fr.text(L("AB | CDE：两个候选都是负收益，空前缀，停在 5", "AB | CDE: both trials lose, the empty prefix wins, stuck at 5"), 1370, 790, 22, ROSE, c.p(1), anchor="c")
    if c.on(2):
        fr.text(L("局部最优：要变成 DE | ABC 得同时换两对", "a local optimum: reaching DE | ABC needs two pairs at once"), 560, 760, 24, GOLD, c.p(2), anchor="c")


def a_area(fr, c):
    sizes = {"A": 3, "B": 1, "C": 1, "D": 1, "E": 1}
    g01(fr, (200, 300, 760, 720), SEED if not c.on(1) else AFTER1, 1.0, badges={n: L(f"面积 {s}", f"area {s}") for n, s in sizes.items()})
    area = lambda side, s: sum(sizes[n] for n in IDS if side[n] == s)
    panel(fr, 960, 260, 740, 380, c.p(0), L("人数平衡 ≠ 面积平衡", "COUNT BALANCE ≠ AREA BALANCE"))
    fr.text(L(f"种子：人数 2 | 3，面积 {area(SEED, 0)} | {area(SEED, 1)}", f"seed: count 2 | 3, area {area(SEED, 0)} | {area(SEED, 1)}"), 1000, 360, 26, IVORY, c.p(0), role="mono")
    if c.on(1):
        fr.text(L(f"A↔D 之后：人数 2 | 3，面积 {area(AFTER1, 0)} | {area(AFTER1, 1)}", f"after A↔D: count 2 | 3, area {area(AFTER1, 0)} | {area(AFTER1, 1)}"), 1000, 430, 26, ROSE, c.p(1), role="mono")
    if c.on(2):
        fr.paragraph(L("KL 一换一只保持个数。面积要平衡，就另加检查，或用允许加权平衡的方法（下一章的 FM）。",
                       "KL's one-for-one swap keeps only the count. To balance area, add a check, or use a method that allows weighted balance (next module's FM)."), 1000, 500, 24, 660, GOLD, c.p(2))


def a_cost(fr, c):
    panel(fr, 260, 240, 1400, 520, c.p(0), L("一轮的代价", "THE COST OF A PASS"))
    lines = [(L("n 个节点、两侧各 n/2：一轮 n/2 步", "n nodes, n/2 a side: a pass has n/2 steps"), IVORY, 0),
             (L("每步枚举所有未锁定的跨侧对：最多 (n/2)² 对", "each step scans every unlocked cross pair: up to (n/2)² pairs"), IVORY, 1),
             (L("朴素实现一轮约 O(n³)；按 D 排序剪枝可以更快", "a naive pass is about O(n³); sorting by D prunes it"), GOLD, 2),
             (L("下一章 FM 改成单点移动，用桶结构把一轮做到近线性", "next module, FM moves one node at a time and uses buckets for a near-linear pass"), TEAL, 3)]
    for s, col, k in lines:
        if c.on(k):
            fr.paragraph(s, 300, 340 + k * 100, 28, 1320, col, c.p(k))


def a_summary(fr, c):
    items = [(L("收益 = 交换前后 cut 之差；−2w 修正被多算的边", "Gain = cut before − cut after; −2w corrects the double-counted edge"), GOLD),
             (L("负收益要试探：它可能打开后面更大的收益", "Try negative gains: they can open larger gains later"), AMBER),
             (L("前缀必须连续：后面的收益依赖前面的步", "A prefix must be consecutive: later gains depend on earlier steps"), TEAL),
             (L("结果依赖种子；AB | CDE 停在局部最优 5", "The result depends on the seed; AB | CDE is stuck at a local optimum, 5"), ROSE),
             (L("只保持个数，不保持面积", "It keeps the count, not the area"), ROSE),
             (L("朴素一轮约 O(n³)；FM 用单点移动更快", "A naive pass is about O(n³); FM's single moves are faster"), TEAL)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 200 + i * 104
            fr.rect(220, y, 1480, 84, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 54, 26, col, a, role="mono")
            fr.text(s, 350, y + 54, 30, IVORY, a)


ADVANCED = Film(
    "advanced", "advanced", L("进阶：收益、前缀与局部最优", "In depth: gains, prefixes, local optima"), None, BRAND, poster_at=40.0, music="score:calm", seed=39,
    why=L("为什么减 2w、为什么负收益也要试探（一张八节点图：先 −1 再 +7）、为什么前缀必须连续、结果怎样依赖种子（AB | CDE 停在 5）、人数与面积，以及一轮的代价。",
          "Why −2w, why negative gains are tried (an eight-node graph: −1 then +7), why a prefix must be consecutive, how the result depends on the seed (AB | CDE stops at 5), counts versus areas, and the cost of a pass."),
    scenes=[
        Scene("a00-title", a_title, [Beat(None, 3.0)]),
        Scene("a01-why2w", a_why2w, [Beat(L("交换 a、b：a 过去降 D(a)，b 过来降 D(b)。", "Swap a and b: a moving drops D(a), b moving drops D(b)."), 4.6),
                                     Beat(L("可 a–b 这条边两边都算了“会被修好”，交换后它还跨着：多算 2w。", "But both count the a–b edge as “fixed”, and it still crosses after the swap: 2w too many."), 6.0),
                                     Beat(L("E↔D：9 − 10 = −1；直接数 cut，12 → 13，一致。", "E↔D: 9 − 10 = −1; counting the cut directly, 12 → 13, it agrees."), 5.0)],
              chapter=L("一 · 为什么减 2w", "I · WHY −2w")),
        Scene("a02-negative", a_negative, [Beat(L("一张八节点图，从交错的种子出发，cut 7。", "An eight-node graph from an alternating seed: cut 7."), 4.0),
                                           Beat(L("第一步最好也只有 −1。", "The best first step is only −1."), 2.8),
                                           Beat(L("但第二步 +7：保留前两步，cut 1。", "But step two is +7: keep two steps, cut 1."), 4.0),
                                           Beat(L("只肯接受正收益的贪心，一开始就会停在 7。", "A greedy that accepts only gains would stop at 7 right away."), 4.4)],
              chapter=L("二 · 负收益", "II · NEGATIVE GAINS")),
        Scene("a03-prefix", a_prefix, [Beat(L("为什么前缀必须连续？每一步的收益都依赖前面的步。", "Why must a prefix be consecutive? Each gain depends on the steps before it."), 5.0),
                                       Beat(L("第二轮的 D↔B 在序列里是 +2，从起点单独做却是 −12。", "Pass 2's D↔B is +2 in sequence, but −12 alone from the start."), 5.0),
                                       Beat(L("所以只取前 k 步；k = 0 也合法。", "So take only the first k steps; k = 0 is valid too."), 3.6)],
              chapter=L("三 · 连续前缀", "III · CONSECUTIVE PREFIXES")),
        Scene("a04-seed", a_seed, [Beat(L("换种子：三个种子都到 cut 3。", "Change the seed: three seeds reach cut 3."), 3.6),
                                   Beat(L("AB | CDE 却停在 5：两次试探都是亏的。", "But AB | CDE stays at 5: both trials lose."), 4.2),
                                   Beat(L("要到 DE | ABC 得同时换两对：这是局部最优。", "Reaching DE | ABC needs two pairs at once: a local optimum."), 4.8)],
              chapter=L("四 · 种子", "IV · THE SEED")),
        Scene("a05-area", a_area, [Beat(L("给 A 面积 3，其他都是 1。", "Give A area 3 and the rest 1."), 3.0),
                                   Beat(L("A↔D 之后人数还是 2 比 3，面积从 4 比 3 变成 2 比 5。", "After A↔D the count is still 2 to 3, but the area goes from 4 : 3 to 2 : 5."), 5.4),
                                   Beat(L("KL 只保持个数；面积要另外检查。", "KL keeps only the count; area needs its own check."), 3.6)],
              chapter=L("五 · 人数与面积", "V · COUNT AND AREA")),
        Scene("a06-cost", a_cost, [Beat(L("一轮有 n/2 步。", "A pass has n/2 steps."), 2.4),
                                   Beat(L("每步最多看 (n/2)² 对。", "Each step looks at up to (n/2)² pairs."), 3.0),
                                   Beat(L("朴素实现一轮约 n³；按 D 排序可以剪掉很多。", "A naive pass is about n³; sorting by D prunes a lot."), 4.4),
                                   Beat(L("下一章的 FM 一次只动一个点，一轮接近线性。", "Next module's FM moves one node at a time, for a near-linear pass."), 4.6)],
              chapter=L("六 · 代价", "VI · COST")),
        Scene("a07-summary", a_summary, [Beat(L("六点小结。", "Six things to keep."), 1.6)] + [Beat(None, 2.6) for _ in range(5)]
              + [Beat(L("下一章：一次只移动一个节点。", "Next: move one node at a time."), 3.0)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

FILMS = [STORY, CONCISE, ADVANCED]
ORDER = ["story", "concise", "advanced", "lab"]
