"""Module 08 · Fiduccia–Mattheyses refinement — the four films.

  story     popular science, cut to "We Never (Remix)": the five friends in two rooms of three beds, now moving one at a
            time, with the rooms allowed to differ by one at most. Ada and Eva would save the most but may not move;
            Dev may, and then Ada can; the losing moves are tried too; the roll-back to the best prefix; six other
            people where two small losses open a gain of 4; and the empty prefix that ends it.
  concise   the essentials: FM versus KL and the balance window, legality before the largest gain, the FS/TE split,
            one pass of trial moves, the best prefix and the stop.
  advanced  a verified negative-gain example, an audit of the attachment's disproved claim, multi-pin nets counted by
            pins, buckets and what "linear time" does and does not mean here, and count versus area balance.
  lab       experiment walkthrough recorded from the real page (walkthrough.mjs → scripts/film/walkthrough.py).

Every value on G01 is read from site/data/m08-fiduccia-mattheyses/traces.json, which scripts/build-traces.mjs produces
by running site/engines/fm.js. The other computations (the escape example's states, the area split) run through the
course's Python reference, python/m08-fiduccia-mattheyses/reference.py, whose checker the tests run.
"""
import importlib.util
import json
from pathlib import Path

from cine import (W, H, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, IVORY, MUTED, FAINT, DIM,
                  PANEL_BG, NODE_BG, clamp, ease, lerp2, title_card, panel, badge, table, graph, fit, pulse,
                  count_hits, substrate)
from story import S, TRACK, INTRO_HITS, FILL1, FILL2, PHRASE, FILL3, FILL4, title_assemble, credits, MUSIC_LINE, landed

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m08-fiduccia-mattheyses/traces.json").read_text())
BRAND = L("Learning Clustering · Module 08 · Fiduccia–Mattheyses 改进", "Learning Clustering · Module 08 · Fiduccia–Mattheyses refinement")
VIOLET = "#c2a6e6"

_spec = importlib.util.spec_from_file_location("m08ref", ROOT / "python/m08-fiduccia-mattheyses/reference.py")
REF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REF)

IDS = [n if isinstance(n, str) else n["id"] for n in T["g01"]["nodes"]]
E5 = [tuple(e) if isinstance(e, list) else (e["u"], e["v"], e["w"]) for e in T["g01"]["edges"]]
P5RAW = {k: tuple(v) for k, v in T["g01"]["positions"].items()}
NETS5 = REF.to_nets({"edges": E5})
SEED = T["seed"]
EV = T["run"]["events"]
R = T["run"]["result"]
P1, P2 = R["passes"]
MOVES = P1["moves"]
G0 = {g["node"]: g for g in EV[0]["gains"]}


def cut5(side):
    return REF.net_cut(NETS5, side)


# facts the captions state, checked against the engine output
assert SEED == {"A": 0, "B": 1, "C": 1, "D": 1, "E": 0} and P1["startCut"] == 12
assert {n: (g["gain"], g["legal"]) for n, g in G0.items()} == {"A": (6, False), "B": (1, True), "C": (-4, True), "D": (3, True), "E": (6, False)}
assert [(m["node"], m["gain"], m["cutAfter"]) for m in MOVES] == [("D", 3, 9), ("A", 6, 3), ("C", -2, 5), ("E", -6, 11), ("B", -1, 12)]
assert MOVES[0]["blockedBetter"] == ["A", "E"]
assert [f["net"] for f in MOVES[0]["fs"]] == ["DE"] and [t["net"] for t in MOVES[0]["te"]] == ["CD"]
assert P1["prefixGains"] == [0, 3, 9, 7, 1, 0] and P1["bestK"] == 2 and P1["acceptedCut"] == 3
assert P2["prefixGains"] == [0, -2, -8, -9, -6, 0] and P2["bestK"] == 0
assert R["cut"] == 3 and R["stopReason"] == "no-positive-prefix"
assert EV[0]["buckets"] == [{"gain": 6, "nodes": ["A", "E"]}, {"gain": 3, "nodes": ["D"]}, {"gain": 1, "nodes": ["B"]}, {"gain": -4, "nodes": ["C"]}]

# the trial states of pass 1, one per move, and the accepted state
STATES = [dict(SEED)]
for m in MOVES:
    STATES.append(dict(STATES[-1], **{m["node"]: m["to"]}))
ACCEPTED = P1["accepted"]
assert ACCEPTED == STATES[2] and cut5(STATES[5]) == 12
GAINS_AT = [{g["node"]: g for g in EV[i]["gains"]} for i in range(6)]  # before move i+1 (index 0 = pass start)

# the replacement negative-gain example: every legal first move loses, then −1, −1, +4 reaches the balanced optimum 4
ESC = T["escape"]
ESC_E = [tuple(e) for e in ESC["graph"]["edges"]]
ESC_POS = dict({k: tuple(v) for k, v in ESC["graph"]["positions"].items()}, F=(620, 400))  # F moved right so C–F and E–B labels part
ESC_SEED = ESC["graph"]["seed"]
ESC_G = {"nodes": ESC["graph"]["nodes"], "edges": ESC_E}
ESC_NETS = REF.to_nets(ESC_G)
ESC_P = REF.fm_pass(ESC_G, ESC_SEED, 2)
_esc_first = [REF.gain(ESC_NETS, ESC_SEED, v)[0] for v in REF.legal_moves(ESC_SEED, set(), 2)]
assert max(_esc_first) <= 0 and REF.net_cut(ESC_NETS, ESC_SEED) == 6
assert [(m["node"], m["gain"], m["cut_after"]) for m in ESC_P["trial_moves"][:3]] == [("A", -1, 7), ("B", -1, 8), ("E", 4, 4)]
assert ESC_P["best_prefix"] == 3 and ESC_P["accepted_cut"] == 4 and ESC["optimum"]["cut"] == 4
ESC_STATES = [dict(ESC_SEED)]
for m in ESC_P["trial_moves"][:3]:
    ESC_STATES.append(dict(ESC_STATES[-1], **{m["node"]: 1 - ESC_STATES[-1][m["node"]]}))

# the attachment's hillclimb case, audited: its text claims 9 / all ≤ 0 / 4; its own data say 18 / E +10 / 8
LEG = T["legacy"]
LEG0 = LEG["run"]["events"][0]
LEG_E = next(g for g in LEG0["gains"] if g["node"] == "E")
assert LEG["graph"]["claimed"] == {"initialCut": 9, "allLegalGainsNonPositive": True, "finalCut": 4}
assert LEG0["metrics"]["cut"] == 18 and LEG_E["legal"] and LEG_E["gain"] == 10
assert LEG["run"]["result"]["passes"][0]["acceptedCut"] == 8 and LEG["optimum"]["cut"] == 8

# a 4-pin net {A,B,C,D}, weight 3, with D alone on the right: counting pins, A 0 and D +3; as a clique, A would get −1
BUS = REF.to_nets({"nets": [{"id": "bus", "pins": ["A", "B", "C", "D"], "w": 3}]})
BUS_SIDE = {"A": 0, "B": 0, "C": 0, "D": 1}
assert REF.gain(BUS, BUS_SIDE, "A")[0] == 0 and REF.gain(BUS, BUS_SIDE, "D")[0] == 3
_clique = REF.to_nets({"edges": [(u, v, 1) for i, u in enumerate("ABCD") for v in "ABCD"[i + 1:]]})
assert REF.gain(_clique, BUS_SIDE, "A")[0] == -1

# count versus area: with A of area 3, the accepted ABC | DE is 3 : 2 by count and 5 : 2 by area
AREA = {"A": 3, "B": 1, "C": 1, "D": 1, "E": 1}
_area = lambda side, s: sum(AREA[n] for n in IDS if side[n] == s)
assert sum(1 for n in IDS if ACCEPTED[n] == 1) == 3 and _area(ACCEPTED, 1) == 5 and _area(ACCEPTED, 0) == 2


def key(u, v):
    return "|".join(sorted((u, v)))


def crossing(edges, side):
    return {key(u, v) for u, v, _ in edges if side[u] != side[v]}


def signed(g):
    return ("+" if g > 0 else "") + f"{g}"


def g01(fr, box, side=None, alpha=1.0, r=36, focus=(), locked=(), blocked=(), badges=None, badge_cols=None, hl=()):
    pos = fit(P5RAW, box)
    cols = {n: (TEAL if side[n] == 0 else BLUE) for n in pos} if side else {}
    graph(fr, pos, E5, cols, alpha, cut=crossing(E5, side) if side else set(), r=r, badges=badges, badge_cols=badge_cols, glow_nodes=focus, hl_edges=hl)
    for n in locked:
        fr.ring(pos[n], r + 9, IVORY, 1.4, 0.7 * alpha, dash=[5, 5])
    for n in blocked:
        fr.ring(pos[n], r + 9, ROSE, 2.4, alpha, glow=0.4 * alpha)
    for n in focus:
        fr.ring(pos[n], r + 9, GOLD, 2.4, alpha, glow=0.5 * alpha)
    return pos


def prefix_bars(fr, x, y, gains, alpha, best=None, shown=None, w=90, scale=24, labels=True):
    """Cumulative gains as bars over k = 0…n; the best prefix boxed in gold."""
    shown = len(gains) - 1 if shown is None else shown
    top = max(abs(g) for g in gains) * scale
    fr.line((x - 20, y), (x + len(gains) * (w + 30), y), DIM, 2, alpha)
    for k, g in enumerate(gains):
        if k > shown:
            continue
        bx, hgt = x + k * (w + 30), max(4, abs(g) * scale)
        col = GOLD if best == k else (TEAL if g > 0 else ROSE if g < 0 else MUTED)
        fr.rect(bx, y - hgt if g >= 0 else y, w, hgt, fill=col, alpha=0.85 * alpha, r=4)
        fr.text(signed(g), bx + w / 2, (y - hgt - 14) if g >= 0 else (y + hgt + 30), 24, col, alpha, anchor="c", role="mono")
        if labels:
            fr.text(f"k={k}", bx + w / 2, y + 40 if g >= 0 else y - 16, 18, MUTED, alpha, anchor="c", role="mono")
        if best == k:
            fr.rect(bx - 10, y - top - 50, w + 20, top * 2 + 90, stroke=GOLD, width=2, alpha=alpha, r=6, dash=[6, 5])


# ====================================================================== popular film
FR = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev", "E": "Eva"}
FE = [(FR[u], FR[v], w) for u, v, w in E5]
ROOMS = {0: (170, 300, 680, 420), 1: (1070, 300, 680, 420)}
BEDS = {s: [(x + 140, y + 130), (x + 340, y + 310), (x + 540, y + 130)] for s, (x, y, w, h) in ROOMS.items()}


def seat_sequence(states):
    """Stable beds: a friend keeps a bed until they move; a mover takes the lowest free bed in the other room."""
    first = {}
    for s in (0, 1):
        for i, n in enumerate(sorted(n for n in IDS if states[0][n] == s)):
            first[n] = (s, i)
    seq = [first]
    for prev, now in zip(states, states[1:]):
        seat = dict(seq[-1])
        for n in IDS:
            if now[n] != prev[n]:
                taken = {i for m, (s, i) in seat.items() if s == now[n] and m != n}
                seat[n] = (now[n], min(set(range(3)) - taken))
        seq.append(seat)
    return [{n: BEDS[s][i] for n, (s, i) in st.items()} for st in seq]


SEATS = seat_sequence(STATES)
# the roll-back: from the end of the trials the three last movers return to the beds they held at step 2
SEATS_BACK = SEATS[2]


def rooms(fr, state, seat, alpha=1.0, prev=None, prev_seat=None, k=1.0, locked=(), focus=(), blocked=(), badges=None,
          badge_cols=None, counter=True, count_glow=0.0):
    """Two rooms of three beds; friends in their beds; split friendships drawn rose; the head count under each room."""
    shown = state if not prev or k >= 0.5 else prev
    for s, (x, y, w, h) in ROOMS.items():
        n = sum(1 for m in IDS if shown[m] == s)
        fr.rect(x, y, w, h, fill=PANEL_BG, stroke=FAINT, width=1.4, alpha=0.9 * alpha, r=18)
        fr.text(L("左屋", "LEFT ROOM") if s == 0 else L("右屋", "RIGHT ROOM"), x + 24, y + 38, 18, MUTED, alpha, spacing=2)
        for bx, by in BEDS[s]:
            fr.rect(bx - 60, by + 44, 120, 14, fill=FAINT, alpha=0.35 * alpha, r=6)
        fr.text(L(f"{n} 人", f"{n} here"), x + w - 24, y + 38, 20, IVORY, alpha, anchor="r", role="mono")
    pos = {FR[n]: lerp2(prev_seat[n], seat[n], ease(k)) for n in IDS} if prev_seat and k < 1 else {FR[n]: seat[n] for n in IDS}
    cols = {FR[n]: (TEAL if shown[n] == 0 else BLUE) for n in IDS}
    cut = {key(FR[u], FR[v]) for u, v, _ in E5 if shown[u] != shown[v]}
    graph(fr, pos, FE, cols, alpha, cut=cut, r=46, name_size=22, badges={FR[n]: b for n, b in (badges or {}).items()},
          badge_cols={FR[n]: c for n, c in (badge_cols or {}).items()} or None, glow_nodes=[FR[n] for n in focus])
    for n in locked:
        fr.ring(pos[FR[n]], 56, IVORY, 1.4, 0.75 * alpha, dash=[5, 5])
    for n in blocked:
        fr.ring(pos[FR[n]], 56, ROSE, 2.6, alpha, glow=0.45 * alpha)
    for n in focus:
        fr.ring(pos[FR[n]], 56, GOLD, 2.4, alpha, glow=0.5 * alpha)
    if counter:
        fr.text(L("被拆散的交情", "friendships split"), W / 2, 200, 22, MUTED, alpha, anchor="c", spacing=2)
        fr.text(f"{cut5(shown)}", W / 2, 262, 56, ROSE, alpha, anchor="c", role="mono", glow=0.2 + count_glow)
    return pos


def gain_badges(i, legal_only=False):
    """Gain badges before move i+1: legal ones ivory, blocked ones rose; locked friends get none."""
    g = GAINS_AT[i]
    badges = {n: signed(x["gain"]) for n, x in g.items() if not x["locked"] and (x["legal"] or not legal_only)}
    cols = {n: (IVORY if x["legal"] else ROSE) for n, x in g.items()}
    return badges, cols


def p_open(fr, c):
    for s, (x, y, w, h) in ROOMS.items():
        a = landed(c.T, INTRO_HITS, s)
        fr.rect(x, y, w, h, fill=PANEL_BG, stroke=FAINT, width=1.4, alpha=0.9 * a, r=18)
        for bx, by in BEDS[s]:
            fr.rect(bx - 60, by + 44, 120, 14, fill=FAINT, alpha=0.35 * a, r=6)
    for i, n in enumerate("AEBCD"):
        a = landed(c.T, INTRO_HITS, 2 + i)
        if a <= 0:
            continue
        p = SEATS[0][n]
        fr.dot(p, 46, NODE_BG, a)
        fr.ring(p, 46, TEAL if SEED[n] == 0 else BLUE, 2.8, a)
        fr.text(FR[n], p[0], p[1] + 8, 22, IVORY, a, anchor="c", role="serif")
    if c.on(1):
        a = c.p(1)
        for s, (x, y, w, h) in ROOMS.items():
            fr.text(L("左屋 · 三张床", "LEFT ROOM · THREE BEDS") if s == 0 else L("右屋 · 三张床", "RIGHT ROOM · THREE BEDS"), x + 24, y + 38, 18, MUTED, a, spacing=2)


def p_ask(fr, c):
    rooms(fr, SEED, SEATS[0], counter=c.on(0), count_glow=0.3 * c.p(0))
    if c.on(1):
        fr.text(L("这次：一次只搬一个人", "this time: one person moves at a time"), W / 2, 820, 34, GOLD, c.p(1), anchor="c", role="serif", glow=0.3 * c.p(1))


def p_rule(fr, c):
    b, cols = gain_badges(0)
    rooms(fr, SEED, SEATS[0], badges=b if c.on(1) else None, badge_cols={n: IVORY for n in IDS})
    if c.on(0):
        fr.text(L("两屋人数最多差 1：2 比 3，或 3 比 2", "the rooms may differ by one at most: 2 to 3, or 3 to 2"), W / 2, 800, 26, IVORY, c.p(0), anchor="c")
    if c.on(1):
        fr.text(L("收益 = 屋外朋友 − 屋里朋友", "gain = friends outside − friends inside"), W / 2, 850, 26, GOLD, c.p(1), anchor="c", role="serif")
    if c.on(2):
        a = c.p(2)
        for n in ("A", "E"):
            fr.ring(SEATS[0][n], 58, GOLD, 2.4, a, glow=0.5 * a)


def p_title(fr, c):
    title_assemble(fr, c, L("合法的那一步", "The Legal Move"), L("FM 改进 · FIDUCCIA–MATTHEYSES", "FIDUCCIA–MATTHEYSES REFINEMENT"), "MODULE 08")


def p_blocked(fr, c):
    b, cols = gain_badges(0)
    blk = ("A", "E") if c.on(1) else ()
    rooms(fr, SEED, SEATS[0], badges=b, badge_cols=cols if c.on(1) else {n: IVORY for n in IDS}, blocked=blk, focus=("A",) if not c.on(1) else ())
    if c.on(0) and not c.on(1):
        fr.text(L("Ada 搬走？左屋只剩 1 人", "Ada moves? The left room keeps one"), W / 2, 820, 30, IVORY, c.p(0), anchor="c")
    if c.on(1):
        stamp = max([ease((c.T - t) / 0.3) for t in FILL1 if c.T >= t] or [c.p(1)])
        fr.text("1 : 4", W / 2, 820, 54, ROSE, stamp, anchor="c", role="mono", glow=0.35 * pulse(c.T, FILL1, 0.5))
        fr.text(L("差 3 > 1：不合法", "a gap of 3 > 1: not legal"), W / 2, 870, 24, ROSE, c.p(1), anchor="c")


def p_dev(fr, c):
    b, cols = gain_badges(0, legal_only=True)
    k = clamp(c.span(1, 2) * 1.6) if c.on(1) else 0
    if k == 0:
        rooms(fr, SEED, SEATS[0], badges=b, badge_cols=cols, blocked=("A", "E"), focus=("D",) if c.on(0) else ())
    else:
        rooms(fr, STATES[1], SEATS[1], prev=SEED, prev_seat=SEATS[0], k=k, focus=("D",) if k < 1 else (),
              locked=("D",) if k >= 1 else (), count_glow=0.4 * pulse(c.t, [c.at(1) + 0.6], 0.6))
    if c.on(0) and not c.on(1):
        fr.text(L("合法的里面，Dev 最大：+3", "of the legal moves, Dev's is largest: +3"), W / 2, 830, 28, GOLD, c.p(0), anchor="c")
    if c.on(2):
        fr.text(L("左屋 3 人，右屋 2 人", "left room 3, right room 2"), W / 2, 830, 28, TEAL, c.p(2), anchor="c", role="mono")


def p_ada(fr, c):
    k = clamp((c.T - FILL2[0]) / 1.2) if FILL2 and c.T >= FILL2[0] else 0
    b, cols = gain_badges(1)
    if k == 0:
        rooms(fr, STATES[1], SEATS[1], badges=b, badge_cols=cols, locked=("D",), focus=("A",) if c.on(0) else ())
    else:
        rooms(fr, STATES[2], SEATS[2], prev=STATES[1], prev_seat=SEATS[1], k=k, focus=("A",) if k < 1 else (),
              locked=("D",) + (("A",) if k >= 1 else ()), count_glow=0.5 * pulse(c.T, FILL2, 0.5))
    if c.on(0) and k == 0:
        fr.text(L("现在 Ada 可以走了：+6", "now Ada may go: +6"), W / 2, 830, 30, GOLD, c.p(0), anchor="c")
    if c.on(2):
        fr.text(L("两人锁定，这一轮不再动", "both locked for the rest of the round"), W / 2, 830, 26, MUTED, c.p(2), anchor="c")


def p_rest(fr, c):
    # Cai, Eva, Ben move on the first three strong hits of the phrase
    hits = []
    for t in PHRASE + [S["phrase"] + 1.6 * i for i in range(3)]:
        if not hits or t - hits[-1] >= 1.0:
            hits.append(t)
    hits = sorted(hits)[:3]
    i = sum(1 for t in hits if c.T >= t)
    k = clamp((c.T - hits[i - 1]) / 0.9) if i else 1.0
    state, seat = STATES[2 + i], SEATS[2 + i]
    if i == 0:
        b, cols = gain_badges(2, legal_only=True)
        rooms(fr, state, seat, locked=("D", "A"), badges=b if c.on(0) else None, badge_cols=cols)
    else:
        mover = MOVES[1 + i]["node"]
        rooms(fr, state, seat, prev=STATES[1 + i], prev_seat=SEATS[1 + i], k=k, focus=(mover,) if k < 1 else (),
              locked=tuple(m["node"] for m in MOVES[:2 + i] if m["node"] != mover or k >= 1), count_glow=0.5 * pulse(c.T, hits, 0.5))
        fr.text("  ".join(f"{FR[m['node']]} {signed(m['gain'])}" for m in MOVES[2:2 + i]), W / 2, 830, 28, ROSE, 1.0, anchor="c", role="mono")
    if c.on(2):
        fr.text(L("全是试探", "all of it trials"), W / 2, 880, 26, AMBER, c.p(2), anchor="c", role="serif")


def p_keep(fr, c):
    prefix_bars(fr, 250, 600, P1["prefixGains"], c.p(0, 0.6), best=2, w=70, scale=18)
    k = clamp(c.span(1, 2) * 1.5) if c.on(1) else 0
    small(fr, STATES[2] if k >= 0.5 else STATES[5], SEATS_BACK if k else SEATS[5], SEATS[5] if 0 < k < 1 else None, k, 1.0)


def small(fr, state, seat, prev_seat, k, alpha):
    """A compact copy of the rooms on the right, while the bars hold the left."""
    ox, oy, s = 940, 330, 0.5

    def tf(p):
        return (ox + (p[0] - 170) * s, oy + (p[1] - 300) * s)
    for r, (x, y, w, h) in ROOMS.items():
        fr.rect(*tf((x, y)), w * s, h * s, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.9 * alpha, r=12)
    pos = {FR[n]: tf(lerp2(prev_seat[n], seat[n], ease(k)) if prev_seat else seat[n]) for n in IDS}
    cols = {FR[n]: (TEAL if state[n] == 0 else BLUE) for n in IDS}
    graph(fr, pos, FE, cols, alpha, cut={key(FR[u], FR[v]) for u, v, _ in E5 if state[u] != state[v]}, r=30, name_size=16, weights=False)
    v = cut5(state)
    fr.text(f"cut {v}", ox + 395, oy + 270, 34, ROSE if v > 3 else TEAL, alpha, anchor="c", role="mono")


def p_breath(fr, c):
    a = c.p(0, 1.4)
    fr.text(L("亏的那几步，何必试？", "Why try the losing moves?"), W / 2, 500, 52, GOLD, a, anchor="c", role="serif", glow=0.25 * a)


def p_escape(fr, c):
    i = 0 if not c.on(1) else (1 + min(1, int(c.since(1) / 1.6)) if not (FILL3 and c.T >= FILL3[0]) else 3)
    state = ESC_STATES[i]
    pos = fit(ESC_POS, (420, 300, 1500, 700))
    cols = {n: (TEAL if state[n] == 0 else BLUE) for n in state}
    graph(fr, pos, ESC_E, cols, c.p(0, 1.0), cut=crossing(ESC_E, state), r=40)
    cut = REF.net_cut(ESC_NETS, state)
    fr.text(f"{cut}", W / 2, 250, 56, ROSE if cut > 4 else TEAL, c.p(0), anchor="c", role="mono", glow=0.2 + 0.4 * pulse(c.T, FILL3, 0.5))
    if not c.on(1):
        fr.text(L("每一个合法的移动都亏：爬山法就停在 6", "every legal move loses: hill climbing stops at 6"), W / 2, 800, 26, MUTED, c.p(0), anchor="c")
    else:
        shown = ESC_P["trial_moves"][:i]
        fr.text("   ".join(f"{m['node']} {signed(m['gain'])}" for m in shown), W / 2, 800, 34, GOLD if i == 3 else ROSE, 1.0, anchor="c", role="mono")
    if c.on(2) and i == 3:
        fr.text(L("4：所有平衡分法里最好的", "4: the best of every balanced split"), W / 2, 860, 26, TEAL, c.p(2), anchor="c")


def p_round2(fr, c):
    rooms(fr, ACCEPTED, SEATS_BACK, counter=True)
    if c.on(1):
        prefix_bars(fr, 640, 800, P2["prefixGains"], c.p(1), best=0 if c.on(2) else None, w=60, scale=5, labels=False)


def p_chip(fr, c):
    a = c.p(0, 0.8)
    substrate(fr, 0.6 * a)
    moved = c.T >= (FILL4[0] if FILL4 else S["fill4"])
    for i in range(12):
        for j in range(5):
            x, y = 380 + i * 100, 300 + j * 90
            left = i < 6 or (moved and (i, j) == (6, 2))
            hot = moved and (i, j) == (6, 2)
            fr.rect(x, y, 56, 40, fill=NODE_BG, stroke=TEAL if left else BLUE, width=2.2 if hot else 1.4, alpha=a, r=3, glow=0.4 if hot else 0)
    fr.line((958, 260), (958, 760), GOLD, 2, 0.6 * a, dash=[10, 7])
    if moved:
        b = ease((c.T - (FILL4[0] if FILL4 else S["fill4"])) / 0.6)
        fr.text("31 : 29", W / 2, 230, 30, TEAL, b, anchor="c", role="mono")
        fr.text(L("两半可以差一点：单元一个一个地搬", "the halves may differ a little: cells move one by one"), W / 2, 840, 24, GOLD, b, anchor="c")


def p_outro(fr, c):
    lines = [(L("一次一个人，人数在窗口里", "One at a time, inside the window"), TEAL, 0),
             (L("最大的收益，也得合法", "The biggest gain must also be legal"), GOLD, 1),
             (L("亏的也试，只留最好的前缀", "Try the losses; keep the best prefix"), TEAL, 2)]
    for s, col, k in lines:
        if c.on(k):
            fr.text(s, W / 2, 380 + k * 90, 40, col, c.p(k, 1.2) * (1 - 0.6 * c.p(3)), anchor="c", role="serif")
    if c.on(3):
        a = c.p(3, 1.4)
        fr.text(L("要是在乎的不是交情，而是路程呢？", "What if what matters is not ties, but distance?"), W / 2, 720, 40, GOLD, a, role="serif", anchor="c", glow=0.3 * a)


def p_end(fr, c):
    if not c.on(1):
        a = c.p(0, 1.0)
        g01(fr, (260, 240, 860, 720), ACCEPTED, a)
        fr.text(L("单步看合法候选 · 看被挡住的收益 · 改 maxDiff", "step through legal moves · see blocked gains · change maxDiff"), 1360, 500, 26, GOLD, a, anchor="c")
    else:
        credits(fr, c, [(L("合法的那一步", "The Legal Move"), GOLD, 44),
                        (L("Learning Clustering · Module 08 · Fiduccia–Mattheyses 改进", "Learning Clustering · Module 08 · Fiduccia–Mattheyses refinement"), IVORY, 24),
                        (L("原作 stephQ-lab（Issue #7 附件）· 白盒单步、收益分解与 D(+3)、A(+6) 的推演来自原作", "Original work by stephQ-lab (Issue #7 attachment) · the white-box stepping, the gain breakdown and the D(+3), A(+6) walk-through come from it"), MUTED, 20),
                        (L("所有数值由本课程引擎 site/engines/fm.js 计算", "Every value is computed by this course's engine, site/engines/fm.js"), MUTED, 20),
                        (MUSIC_LINE, MUTED, 18)], k=1)


STORY = Film(
    "story", "popular", L("合法的那一步", "The Legal Move"), None, BRAND, poster_at=44.0, music=TRACK, seed=8,
    why=L("五个朋友住进两间三张床的屋子，一次只搬一个人，两屋人数最多差 1。Ada、Eva 能省最多却不许动；Dev 可以，然后 Ada 才可以；亏的也试，回退到最佳前缀；另外六个人身上，两步小亏换来 +4；最后空前缀让一切停下。",
          "Five friends in two rooms of three beds, moving one at a time, the rooms differing by one at most. Ada and Eva would save the most but may not move; Dev may, and then Ada can; the losses are tried too, and it rolls back to the best prefix; with six other people, two small losses buy a gain of 4; and the empty prefix ends it."),
    scenes=[
        Scene("p-open", p_open, [Beat(L("还是那五个朋友，分住两间屋。", "The same five friends, in two rooms."), 4.6),
                                 Beat(L("这次每间屋都有三张床。", "This time each room has three beds."), 4.4)],
              chapter=L("序 · 两间屋", "PROLOGUE · TWO ROOMS"), until=S["intro_end"]),
        Scene("p-ask", p_ask, [Beat(L("被拆散的交情：12。", "Friendships split: 12."), 3.0),
                               Beat(L("新规矩：一次只搬一个人。", "New rule: one person moves at a time."), 3.2)],
              until=S["groove"]),
        Scene("p-rule", p_rule, [Beat(L("但两屋人数最多差 1。", "But the rooms may differ by one at most."), 4.4),
                                 Beat(L("每人的收益：屋外朋友减屋里朋友。", "Each person's gain: friends outside minus inside."), 4.8),
                                 Beat(L("Ada 和 Eva 各是 6，最大。", "Ada and Eva: 6 each, the biggest."), 4.0)],
              until=S["roll"]),
        Scene("p-title", p_title, [Beat(None, 4.5)], fade=False, until=37.0),
        Scene("p-blocked", p_blocked, [Beat(L("让 Ada 搬？左屋就只剩一个人。", "Move Ada? The left room would keep just one."), 4.2),
                                       Beat(L("1 比 4，差得太多：不许。", "One to four is too lopsided: not allowed."), 4.0),
                                       Beat(L("Eva 也一样。", "The same for Eva."), 2.6)],
              chapter=L("一 · 不许动", "I · NOT ALLOWED"), until=S["fill1_end"]),
        Scene("p-dev", p_dev, [Beat(L("合法的人里，Dev 最好：+3。", "Among the legal ones, Dev is best: +3."), 4.0),
                               Beat(L("Dev 搬过去：12 → 9。", "Dev moves across: 12 → 9."), 3.2),
                               Beat(L("现在左屋有三个人。", "Now the left room has three."), 3.0)],
              until=S["accent"]),
        Scene("p-ada", p_ada, [Beat(L("这下 Ada 可以走了：+6。", "Now Ada may go: +6."), 3.0),
                               Beat(L("9 → 3。", "9 → 3."), 2.4),
                               Beat(L("两人都锁定，这一轮不再动。", "Both lock for the rest of the round."), 3.4)],
              chapter=L("二 · 一个接一个", "II · ONE AFTER ANOTHER"), until=74.0),
        Scene("p-rest", p_rest, [Beat(L("接着走，亏也走：", "Keep going, even at a loss:"), 3.0),
                                 Beat(L("Cai −2，Eva −6，Ben −1。", "Cai −2, Eva −6, Ben −1."), 4.6),
                                 Beat(L("又回到 12：都只是试探。", "Back to 12: all of it trials."), 3.6)],
              until=89.0),
        Scene("p-keep", p_keep, [Beat(L("最好的前缀：前两步。", "The best prefix: the first two steps."), 3.4),
                                 Beat(L("回退到 3。", "Roll back to 3."), 2.6)],
              until=S["breath"]),
        Scene("p-breath", p_breath, [Beat(None, 4.6)], until=S["reentry"]),
        Scene("p-escape", p_escape, [Beat(L("换六个人：一开始，每个合法的移动都亏。", "Six others: at first every legal move loses."), 4.4),
                                     Beat(L("先吃两个小亏：6 → 7 → 8。", "Take two small losses: 6 → 7 → 8."), 4.0),
                                     Beat(L("E 一下赚 4：降到 4，最好的分法。", "Then E gains 4: down to 4, the best split."), 4.6)],
                    chapter=L("三 · 先亏后赚", "III · LOSE, THEN GAIN"), until=S["fill3_end"]),
        Scene("p-round2", p_round2, [Beat(L("回到五个人，第二轮从 3 出发。", "Back to the five: round two starts from 3."), 3.6),
                                     Beat(L("每一段前缀都不如不动。", "Every prefix is worse than staying put."), 3.6),
                                     Beat(L("空前缀胜出：停。", "The empty prefix wins: stop."), 3.0)],
                    chapter=L("四 · 第二轮", "IV · ROUND TWO"), until=S["fill4"]),
        Scene("p-chip", p_chip, [Beat(L("芯片上：两半可以差一点，单元一个一个地搬。", "On a chip: the halves may differ a little; cells move one by one."), 5.4)],
              until=141.5),
        Scene("p-outro", p_outro, [Beat(L("一次一个人，人数留在窗口里。", "One at a time, the head count inside the window."), 6.0),
                                   Beat(L("最大的收益，也得先合法。", "The biggest gain must be legal first."), 6.0),
                                   Beat(L("亏的也试，最后只留最好的前缀。", "Try the losses; keep only the best prefix."), 7.0),
                                   Beat(L("要是在乎的是路程而不是交情呢？下一章见。", "What if distance matters, not ties? Next module."), 8.0)],
              chapter=L("尾声", "CODA"), until=S["quiet"]),
        Scene("p-end", p_end, [Beat(L("下面的实验里，看哪些移动被平衡挡住。", "In the lab below, see which moves the balance blocks."), 6.0),
                               Beat(None, 10.0)], until=S["end"]),
    ])


# ====================================================================== concise film
def k_title(fr, c):
    title_card(fr, L("Fiduccia–Mattheyses 改进", "Fiduccia–Mattheyses Refinement"), L("FM  ·  精讲", "THE ESSENTIALS"), c.p(0, 1.2), kicker="MODULE 08")


def k_problem(fr, c):
    panel(fr, 160, 230, 760, 520, c.p(0), L("KL：一换一", "KL: ONE FOR ONE"))
    panel(fr, 1000, 230, 760, 520, c.p(0), L("FM：一次动一个", "FM: ONE AT A TIME"))
    g01(fr, (240, 320, 840, 650), SEED, c.p(0), r=30)
    g01(fr, (1080, 320, 1680, 650), STATES[1] if c.on(1) else SEED, c.p(0), r=30, focus=("D",) if c.on(1) else ())
    fr.text(L("两侧人数永远 2 : 3", "the side sizes stay 2 : 3"), 540, 728, 24, MUTED, c.p(0), anchor="c")
    if c.on(1):
        fr.text(L("移动 D 后 3 : 2：人数会变", "after moving D, 3 : 2: sizes change"), 1380, 728, 24, MUTED, c.p(1), anchor="c")
    if c.on(2):
        fr.text(L("平衡窗口：|n₀ − n₁| ≤ maxDiff，两侧非空", "the balance window: |n₀ − n₁| ≤ maxDiff, both sides nonempty"), W / 2, 830, 30, GOLD, c.p(2), anchor="c", role="serif")


def k_legal(fr, c):
    g01(fr, (200, 300, 760, 720), SEED, 1.0, blocked=("A", "E") if c.on(1) else (), focus=("D",) if c.on(2) else ())
    rows = [[L("节点", "Node"), L("收益", "Gain"), L("移动后", "After"), L("合法", "Legal")]]
    for n in IDS:
        n0 = sum(1 for m in IDS if dict(SEED, **{n: 1 - SEED[n]})[m] == 0)
        rows.append([n, signed(G0[n]["gain"]), f"{n0} : {5 - n0}", L("是", "yes") if G0[n]["legal"] else L("否", "no")])
    colors = {}
    if c.on(1):
        colors.update({(i + 1, j): ROSE for i, n in enumerate(IDS) if not G0[n]["legal"] for j in range(4)})
    if c.on(2):
        colors.update({(IDS.index("D") + 1, j): GOLD for j in range(4)})
    table(fr, 980, 290, [140, 160, 180, 160], [[tr(x) for x in r] for r in rows], c.p(0), size=28, lh=62, colors=colors)
    if c.on(2):
        fr.text(L("先筛合法，再选最大", "filter for legality, then take the largest"), 1300, 750, 28, GOLD, c.p(2), anchor="c", role="serif")


def k_fste(fr, c):
    hl = ()
    if c.on(1):
        hl = ("D|E",)
    if c.on(2):
        hl = ("D|E", "C|D")
    g01(fr, (200, 300, 760, 720), SEED, 1.0, focus=("D",), hl=hl)
    panel(fr, 960, 250, 760, 470, c.p(0), L("把 v 从 F 侧移到 T 侧", "MOVING v FROM SIDE F TO SIDE T"))
    if c.on(1):
        fr.paragraph(L("FS：v 是某 net 在 F 侧唯一的引脚 → 移走后不再被切，+w。D–E：+5。", "FS: v is a net's only pin on F → after the move it is no longer cut, +w. D–E: +5."), 1000, 360, 25, 680, TEAL, c.p(1))
    if c.on(2):
        fr.paragraph(L("TE：某 net 在 T 侧没有引脚 → 移走后开始被切，−w。C–D：−2。", "TE: a net has no pin on T → after the move it becomes cut, −w. C–D: −2."), 1000, 500, 25, 680, ROSE, c.p(2))
    if c.on(3):
        fr.text(L("收益 = 5 − 2 = 3 = 外部 − 内部", "gain = 5 − 2 = 3 = external − internal"), 1340, 650, 28, GOLD, c.p(3), anchor="c", role="mono")


def k_pass(fr, c):
    step = 0 if not c.on(0) else (1 if not c.on(1) else (2 if not c.on(2) else 5))
    side = STATES[step]
    locked = tuple(m["node"] for m in MOVES[:step])
    g01(fr, (180, 300, 740, 720), side, 1.0, locked=locked, focus=(MOVES[step - 1]["node"],) if step else ())
    rows = [[L("步", "Step"), L("移动", "Move"), L("收益", "Gain"), "cut", L("累计", "Cum.")]]
    for i, m in enumerate(MOVES[:step]):
        rows.append([str(i + 1), m["node"], signed(m["gain"]), str(m["cutAfter"]), signed(m["cumulative"])])
    table(fr, 960, 290, [100, 150, 140, 120, 140], [[tr(x) for x in r] for r in rows], c.p(0), size=28, lh=62,
          colors={(i + 1, 2): ROSE for i, m in enumerate(MOVES[:step]) if m["gain"] < 0})
    if c.on(0) and not c.on(1):
        fr.text(L("D 移过去后左侧 3 人：A 变得合法", "with D across, the left has 3: A becomes legal"), 1300, 760, 24, TEAL, c.p(0), anchor="c")
    if c.on(3):
        fr.text(L("试探终点 cut 12：不是结果", "the trials end at cut 12: not the result"), 1300, 760, 26, AMBER, c.p(3), anchor="c")


def k_prefix(fr, c):
    prefix_bars(fr, 200, 560, P1["prefixGains"], c.p(0), best=2 if c.on(1) else None, w=80, scale=20)
    if c.on(1):
        g01(fr, (1080, 280, 1660, 680), ACCEPTED, c.p(1))
        fr.text(L("从起点只应用 D、A：ABC | DE，cut 3", "from the start apply only D and A: ABC | DE, cut 3"), 1370, 770, 24, TEAL, c.p(1), anchor="c")
    if c.on(2):
        fr.text(L("第二轮：累计全 ≤ 0 → 空前缀，停止", "pass 2: every total ≤ 0 → the empty prefix, stop"), W / 2, 870, 26, GOLD, c.p(2), anchor="c")


def k_take(fr, c):
    items = [(L("单点移动；两侧人数在平衡窗口内", "Single moves; the side sizes stay in the window"), TEAL),
             (L("“最大”只在合法候选中比较", "“Largest” is compared among legal candidates only"), GOLD),
             (L("收益 = FS − TE：按 net 的两侧引脚判断", "Gain = FS − TE: decided by each net's pins per side"), AMBER),
             (L("负收益也试探；只接受最佳前缀，空前缀就停", "Try negative gains; accept the best prefix; stop on the empty one"), TEAL)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 260 + i * 120
            fr.rect(220, y, 1480, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 58, 28, col, a, role="mono")
            fr.text(s, 360, y + 58, 28, IVORY, a)


CONCISE = Film(
    "concise", "concise", L("精讲：合法、收益、回退", "The essentials"), None, BRAND, poster_at=30.0, music="score:steady", seed=28,
    why=L("只讲必须掌握的：FM 与 KL 的差别和平衡窗口、先筛合法再选最大、收益的 FS/TE 分解、一轮试探移动、最佳前缀与停止。",
          "Only what you must know: FM versus KL and the balance window, legality before the largest gain, the FS/TE split of a gain, one pass of trial moves, the best prefix and the stop."),
    scenes=[
        Scene("k00-title", k_title, [Beat(None, 3.0)]),
        Scene("k01-problem", k_problem, [Beat(L("KL 一换一；FM 一次只移动一个节点。", "KL swaps pairs; FM moves one node at a time."), 4.2),
                                         Beat(L("于是两侧人数会变，要用平衡窗口限制。", "So the side sizes change, and a balance window limits them."), 4.4),
                                         Beat(L("这里 maxDiff = 1：五个点只能 2 : 3 或 3 : 2。", "Here maxDiff = 1: five nodes split 2 : 3 or 3 : 2."), 4.4)],
              chapter=L("问题", "THE PROBLEM")),
        Scene("k02-legal", k_legal, [Beat(L("种子 AE | BCD 上，A、E 的收益最大：+6。", "On seed AE | BCD, A and E have the largest gain: +6."), 4.2),
                                     Beat(L("但移走任何一个都是 1 : 4，不合法。", "But moving either one leaves 1 : 4: not legal."), 3.8),
                                     Beat(L("合法候选里最大的是 D：+3。", "Among the legal candidates, D is largest: +3."), 3.8)],
              chapter=L("合法性", "LEGALITY")),
        Scene("k03-fste", k_fste, [Beat(L("收益可以拆成两部分。", "A gain splits into two parts."), 2.6),
                                   Beat(L("FS：D 是 D–E 在本侧唯一的端点，移走后不再被切，+5。", "FS: D is D–E's only end on its side; after the move it is no longer cut, +5."), 5.0),
                                   Beat(L("TE：C–D 在左侧没有端点，移走后开始被切，−2。", "TE: C–D has no end on the left; after the move it becomes cut, −2."), 4.6),
                                   Beat(L("收益 3；对普通边，就是外部减内部。", "Gain 3; for plain edges, that is external minus internal."), 4.0)],
              chapter=L("FS 与 TE", "FS AND TE")),
        Scene("k04-pass", k_pass, [Beat(L("第 1 步移动 D，cut 9；左侧有 3 人，A 变合法。", "Step 1 moves D, cut 9; the left has 3, and A becomes legal."), 4.6),
                                   Beat(L("第 2 步移动 A，+6，cut 3。", "Step 2 moves A, +6, cut 3."), 3.0),
                                   Beat(L("之后 C、E、B 全是负收益，照样试探。", "Then C, E, B all lose, and are tried anyway."), 4.0),
                                   Beat(L("试探停在 cut 12。", "The trials end at cut 12."), 2.8)],
              chapter=L("一轮试探", "ONE PASS")),
        Scene("k05-prefix", k_prefix, [Beat(L("累计收益：3、9、7、1、0。", "Cumulative gains: 3, 9, 7, 1, 0."), 3.4),
                                       Beat(L("最佳前缀 k = 2：从起点只做 D、A，cut 3。", "The best prefix is k = 2: from the start do only D and A, cut 3."), 4.6),
                                       Beat(L("第二轮没有正的前缀，算法停止。", "Pass 2 has no positive prefix, and the algorithm stops."), 3.8)],
              chapter=L("最佳前缀", "THE BEST PREFIX")),
        Scene("k06-take", k_take, [Beat(L("记住四点。", "Four things to keep."), 1.4),
                                   Beat(L("单点移动，守住平衡窗口；先合法，再最大；", "Single moves inside the window; legal first, then largest;"), 3.6),
                                   Beat(L("收益 = FS − TE；负收益也试，只接受最佳前缀。", "gain = FS − TE; try losses too, accept only the best prefix."), 3.8),
                                   Beat(L("下面的实验里，看哪些移动被平衡挡住。", "In the lab below, see which moves the balance blocks."), 3.4)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])


# ====================================================================== advanced film
def a_title(fr, c):
    title_card(fr, L("Fiduccia–Mattheyses 改进", "Fiduccia–Mattheyses Refinement"), L("进阶：反例、多引脚与复杂度", "IN DEPTH: EXAMPLES, MULTI-PIN NETS, COST"), c.p(0, 1.2), kicker="MODULE 08")


def a_escape(fr, c):
    i = 0 if not c.on(2) else (2 if not c.on(3) else 3)
    state = ESC_STATES[i]
    pos = fit(ESC_POS, (200, 300, 960, 680))
    graph(fr, pos, ESC_E, {n: (TEAL if state[n] == 0 else BLUE) for n in state}, c.p(0, 1.0), cut=crossing(ESC_E, state), r=36)
    cut = REF.net_cut(ESC_NETS, state)
    fr.text(f"cut {cut}", 580, 250, 34, ROSE if cut > 4 else TEAL, c.p(0), anchor="c", role="mono")
    if c.on(1):
        legal = REF.legal_moves(ESC_SEED, set(), 2)
        rows = [[L("初始移动", "First move"), L("收益", "Gain")]] + [[v, signed(REF.gain(ESC_NETS, ESC_SEED, v)[0])] for v in legal]
        table(fr, 1100, 250, [220, 160], [[tr(x) for x in r] for r in rows], c.p(1), size=22, lh=40, colors={(k + 1, 1): ROSE for k in range(len(legal))})
    if c.on(2):
        prefix_bars(fr, 1120, 790, [0] + [m["gain"] for m in ESC_P["trial_moves"][:1]] + [sum(m["gain"] for m in ESC_P["trial_moves"][:k]) for k in (2, 3)],
                    c.p(2), best=3 if c.on(3) else None, w=70, scale=26)
    if c.on(4):
        fr.text(L("穷举所有平衡二分：最优正是 4", "exhaustive search over balanced splits: the optimum is 4"), W / 2, 860, 26, TEAL, c.p(4), anchor="c")


def a_legacy(fr, c):
    rows = [["", L("原文说", "The text says"), L("按它的数据算", "Its own data say")],
            [L("初始 cut", "Initial cut"), "9", str(LEG0["metrics"]["cut"])],
            [L("合法收益", "Legal gains"), L("全部 ≤ 0", "all ≤ 0"), L(f"E 合法，+{LEG_E['gain']}", f"E legal, +{LEG_E['gain']}")],
            [L("最终 cut", "Final cut"), "4", L(f"首轮 {LEG['run']['result']['passes'][0]['acceptedCut']}", f"pass 1: {LEG['run']['result']['passes'][0]['acceptedCut']}")],
            [L("穷举最优", "Exhaustive optimum"), "—", str(LEG["optimum"]["cut"])]]
    shown = 1 + sum(1 for k in (1, 2, 3) if c.on(k))
    table(fr, 360, 280, [340, 360, 460], [[tr(x) for x in r] for r in rows[:shown + 1]], c.p(0), size=30, lh=74,
          colors={(r, 2): ROSE for r in range(1, 5)})
    if c.on(4):
        fr.text(L("文字与数据不符：只作回归测试，不作教材", "the text does not match the data: a regression test, not a lesson"), W / 2, 820, 28, GOLD, c.p(4), anchor="c", role="serif")


def a_multipin(fr, c):
    pins = {"A": (420, 380), "B": (420, 580), "C": (620, 480), "D": (1060, 480)}
    hub = (820, 480)
    a = c.p(0, 1.0)
    for n, p in pins.items():
        fr.line(hub, p, VIOLET, 4, a)
    fr.dot(hub, 14, VIOLET, a)
    fr.text(L("net（权 3）", "net (weight 3)"), hub[0] - 20, 395, 24, VIOLET, a, anchor="c")
    fr.line((880, 300), (880, 680), GOLD, 2, 0.7 * a, dash=[10, 8])
    for n, p in pins.items():
        fr.dot(p, 40, NODE_BG, a)
        fr.ring(p, 40, TEAL if BUS_SIDE[n] == 0 else BLUE, 2.8, a)
        fr.text(n, p[0], p[1] + 12, 32, IVORY, a, anchor="c", role="serif")
    if c.on(2):
        fr.text(L("按引脚计数", "counting pins"), 1460, 340, 26, MUTED, c.p(2), anchor="c", spacing=2)
        fr.text(L("移动 D：net 不再被切，+3", "move D: the net is no longer cut, +3"), 1460, 400, 26, TEAL, c.p(2), anchor="c")
        fr.text(L("移动 A：两侧仍有引脚，0", "move A: pins remain on both sides, 0"), 1460, 450, 26, IVORY, c.p(2), anchor="c")
    if c.on(3):
        fr.text(L("拆成团（每对 1）再按边算", "split into a clique (1 per pair)"), 1460, 560, 26, MUTED, c.p(3), anchor="c")
        fr.text(L("A 的“收益”变成 −1：错", "A's “gain” becomes −1: wrong"), 1460, 610, 26, ROSE, c.p(3), anchor="c")


def a_bucket(fr, c):
    bk = EV[0]["buckets"]
    a = c.p(0, 1.0)
    fr.text(L("按收益分组的桶（种子 AE | BCD）", "buckets by gain (seed AE | BCD)"), 520, 260, 24, MUTED, a, anchor="c", spacing=1)
    for i, b in enumerate(bk):
        y = 320 + i * 96
        fr.rect(260, y, 140, 70, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=a, r=6)
        fr.text(signed(b["gain"]), 330, y + 46, 30, GOLD if i == 0 else IVORY, a, anchor="c", role="mono")
        for j, n in enumerate(b["nodes"]):
            col = ROSE if not G0[n]["legal"] else (GOLD if n == "D" and c.on(1) else IVORY)
            fr.dot((470 + j * 110, y + 35), 30, NODE_BG, a)
            fr.ring((470 + j * 110, y + 35), 30, col, 2.4, a)
            fr.text(n, 470 + j * 110, y + 45, 26, IVORY, a, anchor="c", role="serif")
    if c.on(1):
        fr.arrow((210, 355 + 96), (255, 355 + 96), GOLD, 3, c.p(1), head=14)
        fr.text(L("最大合法", "max legal"), 150, 360 + 96, 20, GOLD, c.p(1), anchor="c")
    panel(fr, 1000, 260, 720, 520, c.p(1), L("线性时间从哪里来", "WHERE LINEAR TIME COMES FROM"))
    lines = [(L("论文：每个收益一个链表，加最大收益指针", "The paper: one list per gain, plus a max-gain pointer"), IVORY, 1),
             (L("每次移动只更新邻居的收益：一轮 O(P)", "Each move updates only its neighbours: a pass costs O(P)"), TEAL, 2),
             (L("本课程：收益增量更新，但选择时扫描", "This course: gains update incrementally, but choosing scans"), AMBER, 3),
             (L("所以不能称为 O(P)", "So it cannot be called O(P)"), ROSE, 3)]
    y = 350
    for s, col, k in lines:
        if c.on(k):
            y += fr.paragraph(s, 1040, y, 25, 640, col, c.p(k)) + 22


def a_area(fr, c):
    side = SEED if not c.on(1) else ACCEPTED
    g01(fr, (200, 300, 760, 720), side, 1.0, badges={n: L(f"面积 {s}", f"area {s}") for n, s in AREA.items()})
    panel(fr, 960, 260, 760, 400, c.p(0), L("人数窗口 ≠ 面积窗口", "A COUNT WINDOW ≠ AN AREA WINDOW"))
    fr.paragraph(L("maxDiff 数的是节点个数。", "maxDiff counts nodes."), 1000, 340, 26, 680, IVORY, c.p(0))
    if c.on(1):
        n1 = sum(1 for n in IDS if ACCEPTED[n] == 1)
        fr.text(L(f"ABC | DE：人数 {n1} : {5 - n1}", f"ABC | DE: count {n1} : {5 - n1}"), 1000, 420, 28, TEAL, c.p(1), role="mono")
    if c.on(2):
        fr.text(L(f"面积 {_area(ACCEPTED, 1)} : {_area(ACCEPTED, 0)}", f"area {_area(ACCEPTED, 1)} : {_area(ACCEPTED, 0)}"), 1000, 480, 28, ROSE, c.p(2), role="mono")
    if c.on(3):
        fr.paragraph(L("面积平衡要用面积之和定义合法性：本课程标为拓展。", "Area balance needs legality defined by summed area: an extension here."), 1000, 540, 24, 680, GOLD, c.p(3))


def a_summary(fr, c):
    items = [(L("负收益试探有用：先 −1、−1，再 +4 到平衡最优", "Trying losses pays: −1, −1, then +4 to the balanced optimum"), AMBER),
             (L("反例要独立核验：原 hillclimb 说明不成立", "Verify examples independently: the original hillclimb claim fails"), ROSE),
             (L("多引脚 net 按引脚计数，不能拆成团", "Count a multi-pin net's pins; don't split it into a clique"), TEAL),
             (L("桶 + 最大指针才是 O(P)；扫描选择不是", "Buckets with a max pointer give O(P); a scan does not"), GOLD),
             (L("人数窗口不管面积", "A count window ignores area"), ROSE),
             (L("结果依赖种子与平票规则", "The result depends on the seed and the tie rule"), TEAL)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 200 + i * 104
            fr.rect(220, y, 1480, 84, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 54, 26, col, a, role="mono")
            fr.text(s, 350, y + 54, 30, IVORY, a)


ADVANCED = Film(
    "advanced", "advanced", L("进阶：反例、多引脚与复杂度", "In depth: examples, multi-pin nets, cost"), None, BRAND, poster_at=20.0, music="score:calm", seed=40,
    why=L("一个经穷举核验的负收益反例、对原附件说明的审查、按引脚计数的多引脚 net、桶与“线性时间”到底指什么，以及人数平衡与面积平衡。",
          "A negative-gain example verified exhaustively, an audit of the attachment's claim, multi-pin nets counted by pins, buckets and what “linear time” does and does not mean here, and count versus area balance."),
    scenes=[
        Scene("a00-title", a_title, [Beat(None, 3.0)]),
        Scene("a01-escape", a_escape, [Beat(L("为什么要试负收益？看一个核验过的例子。", "Why try negative gains? A verified example."), 3.8),
                                       Beat(L("六个点，maxDiff 2，cut 6：每个合法移动的收益都 ≤ 0。", "Six nodes, maxDiff 2, cut 6: every legal move has gain ≤ 0."), 5.0),
                                       Beat(L("爬山法停在 6；FM 先走 A −1、B −1，cut 8。", "Hill climbing stops at 6; FM takes A −1, B −1: cut 8."), 4.6),
                                       Beat(L("这时 E 最强的连接已在对面：+4，cut 4。", "Now E's strongest tie is across: +4, cut 4."), 4.0),
                                       Beat(L("穷举确认：4 就是平衡最优。", "Exhaustive search confirms 4 is the balanced optimum."), 3.8)],
              chapter=L("一 · 负收益的用处", "I · WHAT LOSSES ARE FOR")),
        Scene("a02-legacy", a_legacy, [Beat(L("原附件也有一个例子，配了一段说明。", "The attachment had its own example, with a claim."), 3.8),
                                       Beat(L("用它自己的数据算：初始 cut 是 18，不是 9。", "Computed from its own data: the initial cut is 18, not 9."), 4.0),
                                       Beat(L("E 的移动合法，收益 +10。", "E's move is legal, with gain +10."), 3.0),
                                       Beat(L("首轮最佳和真正的最优都是 8，不是 4。", "Pass 1's best and the true optimum are both 8, not 4."), 4.0),
                                       Beat(L("所以它只留作回归测试，不当教材。", "So it stays a regression test, not a lesson."), 3.4)],
              chapter=L("二 · 审查一个反例", "II · AUDITING AN EXAMPLE")),
        Scene("a03-multipin", a_multipin, [Beat(L("真实网表里，一个 net 常连三个以上的单元。", "In real netlists a net often joins three or more cells."), 3.8),
                                           Beat(L("net {A,B,C,D}，权 3，只有 D 在右边。", "A net {A, B, C, D}, weight 3, with only D on the right."), 3.8),
                                           Beat(L("按引脚计数：移 D 收益 +3，移 A 收益 0。", "Counting pins: moving D gains +3, moving A gains 0."), 4.2),
                                           Beat(L("拆成团再按边算，A 会错得到 −1。", "Split into a clique and counted by edges, A would wrongly get −1."), 4.2)],
              chapter=L("三 · 多引脚 net", "III · MULTI-PIN NETS")),
        Scene("a04-bucket", a_bucket, [Beat(L("1982 年论文的快，来自桶。", "The 1982 paper's speed comes from buckets."), 3.2),
                                       Beat(L("每个收益一个链表，再加一个指向最大合法收益的指针。", "One list per gain, plus a pointer to the largest legal gain."), 4.6),
                                       Beat(L("每次移动只更新邻居：一轮的代价与引脚总数成正比。", "Each move updates only its neighbours: a pass costs time in proportion to the pins."), 5.0),
                                       Beat(L("本课程的收益是增量更新的，但选择时仍在扫描：不能称为 O(P)。", "This course updates gains incrementally, but still scans to choose: not O(P)."), 5.2)],
              chapter=L("四 · 桶与复杂度", "IV · BUCKETS AND COST")),
        Scene("a05-area", a_area, [Beat(L("平衡窗口数的是人数，不是面积。", "The window counts nodes, not area."), 3.4),
                                   Beat(L("给 A 面积 3：接受的 ABC | DE 人数是 3 : 2。", "Give A area 3: the accepted ABC | DE is 3 : 2 by count."), 4.2),
                                   Beat(L("面积却是 5 : 2。", "By area it is 5 : 2."), 2.6),
                                   Beat(L("面积平衡需要自己的窗口：标为拓展。", "Area balance needs its own window: an extension."), 3.6)],
              chapter=L("五 · 人数与面积", "V · COUNT AND AREA")),
        Scene("a06-summary", a_summary, [Beat(L("六点小结。", "Six things to keep."), 1.6)] + [Beat(None, 2.6) for _ in range(5)]
              + [Beat(L("下一章：目标从 cut 换成延迟。", "Next: the goal changes from cut to delay."), 3.0)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

FILMS = [STORY, CONCISE, ADVANCED]
ORDER = ["story", "concise", "advanced", "lab"]
