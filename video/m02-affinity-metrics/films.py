"""Module 02 · Affinity metrics — the four films.

  story     popular science, cut to "We Never (Remix)": group chats → a chip → three ways to score a pair.
  concise   the essentials: three scores, the stable ranking, the priority-graph flip.
  advanced  why min, the hub problem, enumeration cost, what pin-count preserves, and why ties need a rule.
  lab       experiment walkthrough recorded from the real page (walkthrough.mjs → scripts/film/walkthrough.py).

Every score and ranking is read from site/data/m02-affinity-metrics/traces.json, which
scripts/build-traces.mjs produces by running site/engines/affinity.js.
"""
import json
from pathlib import Path

from cine import (W, H, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, CORAL, LILAC, SAGE, IVORY, MUTED, FAINT, DIM,
                  PANEL_BG, NODE_BG, HUES, clamp, ease, ramp, lerp, lerp2, title_card, panel, badge, note, bar, code_panel, table,
                  graph, math_line, fit, mixc, pulse, count_hits)
import cine
from story import S, TRACK, INTRO_HITS, ROLL_HITS, FILL1, FILL2, PHRASE, FILL3, FILL4, title_assemble, credits, MUSIC_LINE, landed

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m02-affinity-metrics/traces.json").read_text())
CIRCUIT = json.loads((ROOT / "site/data/m05-label-propagation/film-graphs.json").read_text())["circuit"]
BRAND = L("Learning Clustering · Module 02 · 亲和度指标", "Learning Clustering · Module 02 · Affinity metrics")

E5 = [tuple(e) for e in T["g01"]["edges"]]
P5 = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (250, 250, 840, 740))
EDGE = T["edge"]
SHARED = T["shared"]
SH = {(p["u"], p["v"]): p for p in SHARED}
PR_E = [tuple(e) for e in T["priority"]["edges"]]
PR_EDGE, PR_SHARED = T["priorityEdge"], T["priorityShared"]
PIN = T["pin"]
PINS = {(p["u"], p["v"]): p for p in PIN["scores"]}
NEUTRAL = "#9fbcbc"

# facts the captions state, checked against the engine output
assert [(p["u"], p["v"], p["score"]) for p in EDGE[:2]] == [("A", "B", 5), ("D", "E", 5)]
assert SH[("B", "D")]["score"] == 2 and SH[("B", "D")]["parts"]["direct"] == 0 and len(SHARED) == 10
assert (PR_EDGE[0]["u"], PR_EDGE[0]["v"], PR_EDGE[0]["score"]) == ("X", "Y", 5)
assert (PR_SHARED[0]["u"], PR_SHARED[0]["v"], PR_SHARED[0]["score"]) == ("P", "Q", 8)
assert PINS[("A", "B")]["score"] == 0.5 and PINS[("E", "F")]["score"] == 1


def fmt(x):
    return f"{x:g}" if abs(x - round(x, 2)) < 1e-9 else f"{x:.2f}"


def key(u, v):
    return "|".join(sorted((u, v)))


# ---------------------------------------------------------------- shared drawing
def ranking(fr, x, y, rows, n_shown, alpha, title, hl=None, w=560, lh=50, size=26, show_parts=None, col=GOLD):
    """A ranked list: rank, pair, score; the first n_shown rows are visible (fractional = the next row fading in)."""
    h = 96 + lh * len(rows)
    panel(fr, x, y, w, h, alpha, title)
    for i, r in enumerate(rows):
        a = clamp(n_shown - i) * alpha
        if a <= 0:
            continue
        yy = y + 100 + i * lh
        on = hl is not None and i == hl
        if on:
            fr.rect(x + 12, yy - size - 6, w - 24, lh - 6, fill="#1d2f2a", alpha=a, r=4, screen=True)
        fr.text(f"{i + 1}", x + 40, yy, size - 4, GOLD if on else MUTED, a, role="mono", anchor="r")
        fr.text(f"{r['u']}–{r['v']}", x + 70, yy, size, IVORY, a, role="serif")
        if show_parts:
            fr.text(show_parts(r), x + 200, yy, size - 6, MUTED, a)
        fr.text(fmt(r["score"]), x + w - 40, yy, size, col if (on or i == 0) else IVORY, a, role="mono", anchor="r", glow=0.3 * a if on else 0)
    return h


def g01(fr, alpha=1.0, colors=None, hl=(), weights=True, active=None, ghost=None, **kw):
    graph(fr, P5, E5, colors or {n: NEUTRAL for n in P5}, alpha, hl_edges=hl, weights=weights, active=active, **kw)
    if ghost:  # a dashed "no wire here" between two nodes
        u, v = ghost[0], ghost[1]
        fr.line(P5[u], P5[v], ROSE, 1.6, 0.55 * alpha * ghost[2], dash=[8, 8])


def via_token(fr, u, v, x, k, col=GOLD):
    """Two pulses run from u and v to their common neighbour x and merge (k: 0→1)."""
    if k <= 0 or k >= 1:
        return
    for s in (u, v):
        p = lerp2(P5[s], P5[x], ease(k))
        fr.dot(p, 7, col, 1 - k * 0.3, glow=1, screen=False)


# ---------------------------------------------------------------- the office's group chats (popular film)
CH = T["chats"]
PEOPLE = CH["netlist"]["nodes"]
NAME = {"Me": L("我", "Me"), "Boss": L("老板", "Boss"), "Lin": L("小林", "Lin"), "Zhou": L("小周", "Zhou"), "Chen": L("阿陈", "Chen"), "Wu": L("老吴", "Wu")}
PPOS = {"Me": (560, 520), "Boss": (560, 270), "Lin": (330, 420), "Zhou": (790, 420), "Chen": (400, 720), "Wu": (720, 720)}
CHAT_NAME = {"all": L("全员群", "Everyone"), "project": L("项目群", "Project"), "weekly": L("周报群", "Weekly report"),
             "notice": L("通知群", "Announcements"), "outing": L("团建群", "Team outing"), "dm": L("私聊", "Private chat")}
NETS = CH["netlist"]["nets"]
CPIN = {(p["u"], p["v"]): p for p in CH["pin"]["scores"]}
RAW = {(p["u"], p["v"]): p["score"] for p in CH["pin"]["raw"]}
BOSS_ME, LIN_ME = ("Boss", "Me"), ("Lin", "Me")
SHARED_WITH_BOSS = [n["id"] for n in NETS if "Me" in n["pins"] and "Boss" in n["pins"]]
assert RAW[BOSS_ME] == 5 == len(SHARED_WITH_BOSS) and max(RAW.values()) == 5
assert CH["pin"]["scores"][0]["u"] == "Lin" and CH["pin"]["scores"][0]["v"] == "Me" and CPIN[LIN_ME]["score"] == 1.7 and CPIN[BOSS_ME]["score"] == 1.2


def people(fr, alpha, shown=None, hl=(), dim_others=0.0, r=46):
    for i, n in enumerate(PEOPLE):
        a = alpha * (shown[i] if shown else 1.0)
        if a <= 0:
            continue
        on = n in hl
        a2 = a * (1 - dim_others * (not on))
        x, y = PPOS[n]
        fr.dot((x, y), r, NODE_BG, a2)
        fr.ring((x, y), r, GOLD if on else NEUTRAL, 2.6, a2, glow=0.6 * a2 if on else 0)
        fr.text(NAME[n], x, y + 10, 28, IVORY, a2, anchor="c")


def chat_cards(fr, alpha, shown=6.0, lit=(), share=0.0, x=1060, y=200, w=660):
    """The office's chat list. lit: chat ids drawn gold; share: 0→1 fades in each chat's share per pair, w/(|e|−1)."""
    for i, net in enumerate(NETS):
        a = clamp(shown - i) * alpha
        if a <= 0:
            continue
        yy = y + i * 94
        on = net["id"] in lit
        fr.rect(x, yy, w, 80, fill=PANEL_BG, stroke=GOLD if on else FAINT, width=1.4 if on else 1.1, alpha=0.95 * a, r=10, screen=True,
                glow=0.25 * a if on else 0)
        fr.text(CHAT_NAME[net["id"]], x + 28, yy + 50, 28, GOLD if on else IVORY, a)
        k = len(net["pins"])
        fr.text(L(f"{k} 人", f"{k} people"), x + 300, yy + 50, 22, MUTED, a)
        for j, p in enumerate(net["pins"]):
            cx = x + 380 + j * 30
            fr.dot((cx, yy + 40), 13, "#123039", a)
            fr.text(tr(NAME[p])[:1], cx, yy + 47, 16, IVORY if p in ("Me", "Boss", "Lin") else MUTED, a, anchor="c")
        if share > 0:
            fr.text(f"1/{k - 1}" if k > 2 else "1", x + w - 24, yy + 50, 26, TEAL, a * share, role="mono", anchor="r")


def chip(fr, alpha, grow=1.0, pos=None, hl=None):
    """The fictional 24-cell schematic from Module 05: cells with pins, wires drawn in."""
    pos = pos or fit({k: tuple(v) for k, v in CIRCUIT["positions"].items()}, (360, 220, 1560, 780))
    for i, (u, v, w) in enumerate(CIRCUIT["edges"]):
        a = clamp(grow * len(CIRCUIT["edges"]) - i) * alpha
        if a <= 0:
            continue
        on = hl and {u, v} == set(hl)
        fr.line(pos[u], pos[v], GOLD if on else "#6f9da0", 0.8 + w * 0.45, (0.9 if on else 0.22 + w * 0.08) * a, glow=0.5 * a if on else 0.08 * a)
    for n, (x, y) in pos.items():
        on = hl and n in hl
        fr.rect(x - 25, y - 13, 50, 26, fill=NODE_BG, stroke=GOLD if on else "#9fbcbc", width=1.6, alpha=alpha, r=3, glow=0.5 * alpha if on else 0)
        for dx in (-14, 0, 14):
            fr.line((x + dx, y - 13), (x + dx, y - 18), "#9fbcbc", 1, 0.6 * alpha)
    return pos


# ====================================================================== popular film
def p_chats(fr, c):
    shown = [landed(c.T, INTRO_HITS, i) for i in range(len(PEOPLE))]
    people(fr, 1.0, shown)


def p_count(fr, c):
    if c.on(1):
        fr.line(PPOS["Me"], PPOS["Boss"], GOLD, 3, 0.9, glow=0.6)
    people(fr, 1.0, hl=("Me", "Boss"), dim_others=0.5 * c.p(1))
    chat_cards(fr, c.p(0, 1.0), shown=c.since(0) * 5)
    if c.on(1):
        n = min(len(SHARED_WITH_BOSS), int(c.since(1) / 0.7) + 1)
        chat_cards(fr, 1.0, lit=SHARED_WITH_BOSS[:n])
        fr.text(str(n), 640, 400, 72, GOLD, 1.0, role="serif", glow=0.4 + 0.6 * pulse(c.t, [c.at(1) + i * 0.7 for i in range(n)], 0.3))
        fr.text(L("个共同群", "shared chats"), 640, 440, 22, MUTED, 1.0)


def p_chip(fr, c):
    pos = chip(fr, c.p(0, 1.2), grow=c.span(0, 1) * 1.1)
    if c.on(1):
        a = c.p(1)
        # a wired pair of neighbouring cells, and the cell farthest from them: short wire vs long wire
        u, v, _ = max(CIRCUIT["edges"], key=lambda e: e[2])
        far = max(pos, key=lambda n: (pos[n][0] - pos[u][0]) ** 2 + (pos[n][1] - pos[u][1]) ** 2)
        fr.line(pos[u], pos[v], TEAL, 4, a, glow=0.6 * a)
        fr.line(pos[u], pos[far], ROSE, 2.5, a * 0.9, glow=0.4 * a, dash=[10, 8])
        badge(fr, (pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2 - 34, L("挨着：导线短", "side by side: a short wire"), TEAL, a, 18, screen=True)
        badge(fr, (pos[u][0] + pos[far][0]) / 2, (pos[u][1] + pos[far][1]) / 2 + 40, L("隔得远：导线长", "far apart: a long wire"), ROSE, a, 18, screen=True)


def p_title(fr, c):
    title_assemble(fr, c, L("谁和谁最亲近", "Who Is Closest?"), L("亲和度 · AFFINITY METRICS", "AFFINITY METRICS"), L("MODULE 02", "MODULE 02"))


def p_direct(fr, c):
    n_hl = count_hits(c.T, FILL1)
    shown = (c.span(0, 2) * 4.5) if c.T < FILL1[0] else 4.5 + n_hl * 0.25
    lit = {key(r["u"], r["v"]) for r in EDGE[: int(shown) + 1]}
    g01(fr, 1.0, hl=lit)
    ranking(fr, 1080, 210, EDGE, shown if c.T < FILL1[0] else len(EDGE), 1.0, L("直接边权 · 排名", "DIRECT WEIGHT · RANKING"),
            hl=0 if c.on(1) else None, show_parts=lambda r: f"w = {fmt(r['score'])}")
    if c.on(1):
        fr.text(L("平票：A–B 在 D–E 前（按名字）", "tie: A–B before D–E (by name)"), 1360, 560 + 48, 22, TEAL, c.p(1), anchor="c")


def p_shared(fr, c):
    bd = SH[("B", "D")]
    ghost = ("B", "D", c.p(0))
    hl = {key("B", "C"), key("C", "D")} if c.on(1) else set()
    cols = {n: NEUTRAL for n in P5}
    cols.update({"B": GOLD, "D": GOLD})
    if c.on(1):
        cols["C"] = TEAL
    g01(fr, 1.0, colors=cols, hl=hl, ghost=ghost if not c.on(2) or c.T < S["accent"] else None)
    if c.on(1):
        via_token(fr, "B", "D", "C", (c.since(1) % 2.0) / 1.2)
    panel(fr, 1080, 250, 600, 360, c.p(0), L("B–D 的分数", "THE SCORE OF B–D"))
    fr.text(L("直接连线", "direct wire"), 1120, 360, 26, MUTED, c.p(0))
    fr.text(L("没有：0", "none: 0"), 1640, 360, 26, ROSE, c.p(0), anchor="r")
    if c.on(1):
        fr.text(L("经共同邻居 C", "via the shared neighbour C"), 1120, 430, 26, MUTED, c.p(1))
        v = bd["parts"]["via"][0]
        fr.text(f"min({v['wu']:g}, {v['wv']:g})", 1640, 430, 26, IVORY, c.p(1), role="mono", anchor="r")
    if c.T >= S["accent"]:
        a = ease((c.T - S["accent"]) / 0.3)
        fr.line((1120, 480), (1640, 480), FAINT, 1.2, a)
        fr.text(L("合计", "total"), 1120, 550, 30, IVORY, a)
        fr.text(fmt(bd["score"]), 1640, 556, 64, GOLD, a, role="serif", anchor="r", glow=0.4 + 0.6 * pulse(c.T, [S["accent"]], 0.5))


def p_list(fr, c):
    n = count_hits(c.T, FILL2)
    shown = min(len(SHARED), 1 + n * len(SHARED) / max(1, len(FILL2))) if c.T >= FILL2[0] else 0.5
    cols = {n_: NEUTRAL for n_ in P5}
    g01(fr, 0.8, colors=cols)
    hl = next(i for i, r in enumerate(SHARED) if (r["u"], r["v"]) == ("B", "D"))
    ranking(fr, 1040, 150, SHARED, shown, 1.0, L("共同邻居 · 10 对", "SHARED NEIGHBOURS · 10 PAIRS"), hl=hl if shown >= len(SHARED) else None,
            lh=56, size=26, w=620,
            show_parts=lambda r: (tr(L("直接 ", "direct ")) + fmt(r["parts"]["direct"]) + "".join(f" + {fmt(v['min'])}" for v in r["parts"]["via"])))


def priority(fr, alpha, mode=None, box=(420, 230, 1500, 720), k=1.0):
    pos = fit({n: tuple(p) for n, p in T["priority"]["positions"].items()}, box)
    cols = {n: (TEAL if n in "PQR" else BLUE) for n in pos}
    hl = set()
    if mode == "edge":
        hl = {key("X", "Y")}
        cols.update({"X": GOLD, "Y": GOLD})
    elif mode == "shared":
        hl = {key("P", "Q"), key("P", "R"), key("Q", "R")}
        cols.update({"P": GOLD, "Q": GOLD})
    graph(fr, pos, PR_E, cols, alpha, hl_edges=hl, r=44, name_size=38)
    return pos


def p_predict(fr, c):
    mode = "edge" if c.on(1) else None
    pos = priority(fr, c.p(0, 1.0), mode)
    if c.on(1):
        badge(fr, (pos["X"][0] + pos["Y"][0]) / 2 + 60, (pos["X"][1] + pos["Y"][1]) / 2 - 60, L("最粗的线：5", "the thickest wire: 5"), GOLD, c.p(1), 20, screen=True)
        fr.text(L("三角形：每条边 4", "the triangle: every edge 4"), (pos["P"][0] + pos["Q"][0]) / 2, pos["P"][1] + 110, 24, TEAL, c.p(1), anchor="c")


def p_flip(fr, c):
    n = count_hits(c.T, PHRASE)
    mode = "edge" if c.T < PHRASE[0] or n % 2 == 1 else "shared"
    if c.T > PHRASE[-1] + 0.2:
        mode = "shared" if c.k >= 1 else "edge"
    pos = priority(fr, 1.0, mode, box=(240, 260, 1100, 720))
    panel(fr, 1240, 260, 520, 360, 1.0)
    on_e, on_s = mode == "edge", mode == "shared"
    fr.text(L("直接边权", "direct weight"), 1280, 350, 26, GOLD if on_e else MUTED, 1.0)
    fr.text("X–Y  5", 1720, 350, 30, GOLD if on_e else MUTED, 1.0, role="mono", anchor="r", glow=0.4 if on_e else 0)
    fr.text(L("共同邻居", "shared neighbours"), 1280, 450, 26, GOLD if on_s else MUTED, 1.0)
    fr.text("P–Q  8", 1720, 450, 30, GOLD if on_s else MUTED, 1.0, role="mono", anchor="r", glow=0.4 if on_s else 0)
    fr.text("4 + min(4, 4)", 1720, 500, 22, TEAL if on_s else FAINT, 1.0, role="mono", anchor="r")
    fr.text(L("第一对", "first pair"), 1280, 570, 20, MUTED, 1.0)


def p_models(fr, c):
    cards = [(L("一根线有多粗", "how thick one wire is"), L("直接边权 → X–Y", "direct weight → X–Y"), GOLD),
             (L("一群人有多紧", "how tight a group is"), L("共同邻居 → P–Q", "shared neighbours → P–Q"), TEAL)]
    for i, (q, a_, col) in enumerate(cards):
        a = c.p(0, delay=0.3 + i * 0.6)
        x = 300 + i * 700
        panel(fr, x, 300, 620, 260, a, accent=col)
        fr.text(q, x + 310, 410, 40, col, a, role="serif", anchor="c")
        fr.text(a_, x + 310, 480, 24, MUTED, a, anchor="c")
    fr.text(L("所以：写明你用的是哪一种评分", "so: say which score you use"), W / 2, 700, 34, IVORY, c.p(0, delay=4.0), anchor="c", role="serif")


def p_boss(fr, c):
    people(fr, c.p(0, 1.2), hl=("Me", "Boss"), dim_others=0.5)
    chat_cards(fr, c.p(0, 1.2), lit=SHARED_WITH_BOSS)


def p_dilute(fr, c):
    if not c.on(1):
        # one 5-person chat ties 10 pairs at once
        net = next(n for n in NETS if n["id"] == "project")
        pins = net["pins"]
        k = c.span(0)
        pairs = [(a, b) for i, a in enumerate(pins) for b in pins[i + 1:]]
        for j, (a, b) in enumerate(pairs):
            if k * len(pairs) > j:
                fr.line(PPOS[a], PPOS[b], GOLD, 1.6, 0.6, glow=0.2)
        fr.text(L(f"{len(pairs)} 对", f"{len(pairs)} pairs"), 560, 840, 26, GOLD, c.p(0), anchor="c")
    else:
        fr.line(PPOS["Me"], PPOS["Lin"], TEAL, 3, c.p(1), glow=0.6 * c.p(1))
    people(fr, 1.0, hl=("Me", "Lin") if c.on(1) else ("Me", "Boss", "Lin", "Zhou", "Chen"), dim_others=0.5)
    chat_cards(fr, 1.0, lit=("dm",) if c.on(1) else ("project",), share=c.p(1, 1.0))
    if c.on(1):
        math_line(fr, [(L("每对得到", "each pair gets"), IVORY), ("   w / (|e| − 1)", GOLD)], 1390, 820, 36, c.p(1))


def p_rank(fr, c):
    rows = [{"u": u, "v": v, "score": CPIN[(u, v)]["score"]} for (u, v) in sorted(CPIN, key=lambda k: (-CPIN[k]["score"], k))][:4]
    rows_raw = sorted([{"u": u, "v": v, "score": s} for (u, v), s in RAW.items()], key=lambda r: (-r["score"], r["u"], r["v"]))[:4]
    n = count_hits(c.T, FILL3)
    flip = c.T >= FILL3[min(3, len(FILL3) - 1)]
    nm = lambda r: {**r, "u": tr(NAME[r["u"]]), "v": tr(NAME[r["v"]])}
    ranking(fr, 260, 230, [nm(r) for r in rows_raw], 4, 1.0 - 0.6 * flip, L("按共同群数", "BY SHARED CHATS"), hl=0, w=620)
    if c.T >= FILL3[0]:
        ranking(fr, 1040, 230, [nm(r) for r in rows], min(4, n * 0.7), 1.0, L("按群的大小摊薄", "SHARED OUT BY GROUP SIZE"), hl=0 if flip else None, w=620, col=TEAL)


def netlist(fr, alpha, focus=None, k=1.0):
    """Capeur's tiny netlist: two 5-pin nets (en, rst) over A–E, and a private 2-pin net n1 = E–F."""
    xs = {n: 380 + i * 230 for i, n in enumerate("ABCDEF")}
    y_cell = 600
    rails = {"en": 330, "rst": 410}
    for nid, y in rails.items():
        on = focus in ("wide", nid)
        col = BLUE if not on else GOLD
        fr.line((xs["A"] - 40, y), (xs["E"] + 40, y), col, 3, alpha * 0.9, glow=0.3 * alpha * on)
        for n in "ABCDE":
            fr.line((xs[n], y), (xs[n], y_cell - 26), col, 1.4, alpha * 0.55)
            fr.dot((xs[n], y), 5, col, alpha)
        fr.text(L(f"{nid} · 5 个引脚", f"{nid} · 5 pins"), xs["A"] - 60, y - 16, 20, col, alpha, anchor="r")
    on = focus == "n1"
    fr.line((xs["E"], y_cell + 30), (xs["E"], y_cell + 90), ROSE if not on else GOLD, 2.5, alpha)
    fr.line((xs["E"], y_cell + 90), (xs["F"], y_cell + 90), ROSE if not on else GOLD, 3, alpha, glow=0.4 * alpha * on)
    fr.line((xs["F"], y_cell + 90), (xs["F"], y_cell + 26), ROSE if not on else GOLD, 2.5, alpha)
    fr.text(L("n1 · 2 个引脚", "n1 · 2 pins"), (xs["E"] + xs["F"]) / 2, y_cell + 126, 20, ROSE if not on else GOLD, alpha, anchor="c")
    for n, x in xs.items():
        fr.rect(x - 34, y_cell - 26, 68, 52, fill=NODE_BG, stroke=NEUTRAL, width=1.8, alpha=alpha, r=4)
        fr.text(n, x, y_cell + 12, 30, IVORY, alpha, role="serif", anchor="c")
    return xs


def pin_box(fr, a, x=1420, y=150):
    panel(fr, x, y, 400, 150, a)
    fr.text("A–B   1/4 + 1/4", x + 30, y + 64, 22, MUTED, a, role="mono")
    fr.text(fmt(PINS[("A", "B")]["score"]), x + 370, y + 64, 26, IVORY, a, role="mono", anchor="r")
    fr.text("E–F   1/(2 − 1)", x + 30, y + 114, 22, MUTED, a, role="mono")
    fr.text(fmt(PINS[("E", "F")]["score"]), x + 370, y + 114, 26, GOLD, a, role="mono", anchor="r", glow=0.4 * a)


def p_netlist(fr, c):
    focus = "wide" if c.k == 0 else "n1" if c.k >= 1 else None
    netlist(fr, c.p(0, 1.0), focus)
    if c.on(1):
        a = c.p(1)
        pin_box(fr, a)


def p_pipeline(fr, c):
    steps = [(L("打分", "Score pairs"), L("本章", "this module"), GOLD), (L("合并", "Merge"), "Module 03–04", TEAL),
             (L("分组与划分", "Group and partition"), "Module 05–09", BLUE), (L("布局布线", "Place and route"), L("芯片后端", "the chip back end"), LILAC)]
    for i, (s, sub, col) in enumerate(steps):
        a = landed(c.T, FILL4, i * 2) if c.T >= FILL4[0] else (1.0 if i == 0 else 0.0)
        a *= c.p(0, 0.6)
        x = 210 + i * 400
        panel(fr, x, 380, 330, 200, a, accent=col)
        fr.text(s, x + 165, 470, 34, col, a, role="serif", anchor="c")
        fr.text(sub, x + 165, 520, 20, MUTED, a, anchor="c")
        if i < 3:
            fr.arrow((x + 340, 480), (x + 390, 480), MUTED, 2, a)


def p_outro(fr, c):
    a0 = c.p(0, 1.2)
    ab_e, ab_s = next(r for r in EDGE if (r["u"], r["v"]) == ("A", "B"))["score"], SH[("A", "B")]["score"]
    g01(fr, a0 * (1 - 0.7 * c.p(2)), colors={n: (GOLD if n in "AB" else NEUTRAL) for n in P5}, hl={key("A", "B")})
    if c.on(0):
        panel(fr, 1080, 300, 560, 220, a0, L("同一对 A–B", "THE SAME PAIR A–B"))
        fr.text(L("直接边权", "direct weight"), 1120, 410, 26, MUTED, a0)
        fr.text(fmt(ab_e), 1600, 410, 32, IVORY, a0, role="mono", anchor="r")
        fr.text(L("共同邻居", "shared neighbours"), 1120, 470, 26, MUTED, a0)
        fr.text(fmt(ab_s), 1600, 470, 32, IVORY, a0, role="mono", anchor="r")
    if c.on(1):
        a = c.p(1)
        fr.text(L("不是距离 · 不是概率 · 是一个模型给出的排名", "not a distance · not a probability · a ranking under one model"), 1360, 600, 22, TEAL, a, anchor="c")
    if c.on(3):
        a = c.p(3, 1.4)
        fr.text(L("按哪种算法？", "By which score?"), W / 2, 760, 64, GOLD, a, role="serif", anchor="c", glow=0.3 * a)


def p_end(fr, c):
    if not c.on(1):
        a = c.p(0, 1.0)
        g01(fr, a, colors={n: NEUTRAL for n in P5})
        fr.text(L("改一条边 · 换一种评分 · 看排名怎么变", "change one wire · switch the score · watch the ranking move"), 1380, 500, 26, GOLD, a, anchor="c")
    else:
        credits(fr, c, [(L("谁和谁最亲近", "Who Is Closest?"), GOLD, 44),
                        (L("Learning Clustering · Module 02 · 亲和度指标", "Learning Clustering · Module 02 · Affinity metrics"), IVORY, 24),
                        (L("原作 Capeur（Issue #1）· priority 图与 tiny netlist 的数值来自原作", "Original work by Capeur (Issue #1) · the priority graph and tiny netlist come from it"), MUTED, 20),
                        (L("所有分数由本课程引擎 site/engines/affinity.js 计算", "Every score is computed by this course’s engine, site/engines/affinity.js"), MUTED, 20),
                        (MUSIC_LINE, MUTED, 18)], k=1)


STORY = Film(
    "story", "popular", L("谁和谁最亲近", "Who Is Closest?"), None, BRAND, poster_at=36.5, music=TRACK, seed=2,
    why=L("从群聊讲起：数共同群聊会得出“老板最亲近”；再到芯片，讲清直接连线、共同邻居和按群大小摊薄三种评分。",
          "It starts with group chats, where counting them says the boss is your closest person, then moves to a chip: direct wires, shared neighbours, and sharing a net out by its size."),
    scenes=[
        Scene("p-chats", p_chats, [Beat(L("要排座位、分小组，先得回答一个更小的问题：", "Before you seat people or split them into teams, there is a smaller question:"), 6.0),
                                   Beat(L("谁和谁最亲近？", "who is closest to whom?"), 2.4)],
              chapter=L("序 · 群聊", "PROLOGUE · GROUP CHATS"), until=S["intro_end"]),
        Scene("p-count", p_count, [Beat(None, 1.2), Beat(L("按共同群聊数，你最亲近的人……是老板。", "Count shared group chats, and your closest person is… the boss."), 5.0)],
              until=S["groove"]),
        Scene("p-chip", p_chip, [Beat(L("芯片里是同一个问题：成千上万个单元，哪两个最该挨着放？", "A chip has the same problem: thousands of cells. Which two belong side by side?"), 6.6),
                                 Beat(L("所以先给每一对打分：分数越高，越该放在一起。", "So first, give every pair a score: the higher it is, the closer they belong."), 5.9)],
              chapter=L("序 · 芯片", "PROLOGUE · THE CHIP"), until=S["roll"]),
        Scene("p-title", p_title, [Beat(None, 4.5)], fade=False, until=37.0),
        Scene("p-direct", p_direct, [Beat(L("第一种算法：两个单元之间的线有多粗，分数就是多少。", "The first way: a pair's score is the weight of the wire between them."), 6.4),
                                     Beat(L("A–B 和 D–E 都是 5：平票按名字排，与输入顺序无关。", "A–B and D–E both score 5: ties go by name, whatever the input order."), 6.6)],
              chapter=L("一 · 直接连线", "I · DIRECT WIRES"), until=S["fill1_end"]),
        Scene("p-shared", p_shared, [Beat(L("B 和 D 之间没有线：按第一种算法，毫无关系。", "B and D share no wire: by the first rule, nothing in common."), 5.0),
                                     Beat(L("但都连着 C：经过 C 的联系，只和较弱的边一样强：", "Both are wired to C, and a link through C is only as strong as its weaker wire:"), 6.0),
                                     Beat(L("min(4, 2) = 2。", "min(4, 2) = 2."), 2.0)],
              chapter=L("二 · 朋友的朋友", "II · FRIENDS OF FRIENDS"), until=S["fill2"]),
        Scene("p-list", p_list, [Beat(L("检查所有对：10 对都有分，包括 B–D。", "Check every pair: all 10 score, B–D included."), 4.6)], until=71.3),
        Scene("p-predict", p_predict, [Beat(L("先猜：哪一对最亲近？", "Take a guess: which pair is closest?"), 3.2),
                                       Beat(L("X–Y 的线最粗：5；三角形每条边只有 4。", "X–Y has the thickest wire, 5; each triangle edge is only 4."), 4.6)],
              chapter=L("三 · 换一种算法", "III · ANOTHER RULE"), until=S["phrase"]),
        Scene("p-flip", p_flip, [Beat(L("按直接连线，第一对是 X–Y；", "By direct wires, the first pair is X–Y;"), 3.6),
                                 Beat(L("按共同邻居，P–Q = 8，跑到了前面。", "by shared neighbours, P–Q = 4 + 4 = 8 moves ahead."), 4.0)],
              until=89.0),
        Scene("p-models", p_models, [Beat(L("两个答案都没错：一个问线有多粗，一个问一群人有多紧。", "Both answers are right: one asks how thick a wire is, the other how tight a group is."), 6.4)],
              until=S["breath"]),
        Scene("p-boss", p_boss, [Beat(L("还记得老板吗？", "Remember the boss?"), 3.0)],
              chapter=L("四 · 大群与私聊", "IV · BIG GROUPS, PRIVATE CHATS"), until=S["reentry"]),
        Scene("p-dilute", p_dilute, [Beat(L("一个 5 人群同时连着 10 对人，对其中任何一对都说明不了多少。", "One five-person chat ties ten pairs at once, so it says little about any one of them."), 6.2),
                                     Beat(L("把一个群的分量摊开：5 人群里每对只得 1/4，私聊得整整 1。", "So share each chat out: in a five-person chat each pair gets 1/4; a private chat gives a whole 1."), 7.2)],
              until=S["fill3"]),
        Scene("p-rank", p_rank, [Beat(L("这样算，最亲近的是小林。", "Counted this way, your closest is Lin."), 3.4)], until=120.8),
        Scene("p-netlist", p_netlist, [Beat(L("时钟线、复位线连着成千上万个单元：不摊薄，谁都显得一样亲近。", "Clock and reset nets reach thousands of cells: unshared, every pair looks equally close."), 7.0),
                                       Beat(L("原作者的小网表：A–B 得 0.5，E–F 得 1。", "In the original tiny netlist: A–B gets 0.5, E–F gets 1."), 5.0)],
              until=S["fill4"]),
        Scene("p-pipeline", p_pipeline, [Beat(L("分数只决定先合并谁；真正的合并，从下一章开始。", "A score only decides who merges first; the merging itself starts in the next module."), 5.6)],
              until=141.5),
        Scene("p-outro", p_outro, [Beat(L("同一对单元，换一种算法，分数就变了。", "The same pair of cells gets a different score under a different rule."), 6.0),
                                   Beat(L("亲和度不是距离，也不是概率：它是某个模型给出的排名。", "Affinity is not a distance and not a probability: it is a ranking under one model."), 8.0),
                                   Beat(L("下次有人说“我们最熟”，可以问一句：", "Next time someone says “we are the closest”, you can ask:"), 7.0),
                                   Beat(L("按哪种算法？", "by which score?"), 6.0)],
              chapter=L("尾声", "CODA"), until=S["quiet"]),
        Scene("p-end", p_end, [Beat(L("下面的实验里，改一条边的权重，看排名怎么变。", "In the lab below, change one wire's weight and watch the ranking move."), 6.0),
                               Beat(None, 10.0)], until=S["end"]),
    ])


# ====================================================================== concise film
def k_title(fr, c):
    title_card(fr, L("亲和度指标", "Affinity Metrics"), L("AFFINITY METRICS  ·  精讲", "THE ESSENTIALS"), c.p(0, 1.2), kicker=L("MODULE 02", "MODULE 02"))


def k_question(fr, c):
    g01(fr, c.p(0, 1.0))
    if c.on(1):
        a = c.p(1)
        panel(fr, 1080, 280, 640, 360, a, L("要解决的问题", "THE PROBLEM"))
        h1 = fr.paragraph(L("输入：带权图，或多引脚网表。", "Input: a weighted graph, or a multi-pin netlist."), 1110, 380, 28, 580, IVORY, a)
        h2 = fr.paragraph(L("输出：所有节点对按分数排名。", "Output: every pair of nodes, ranked by score."), 1110, 380 + h1 + 16, 28, 580, IVORY, a)
        fr.paragraph(L("它只排名，不分组。", "It ranks; it does not group."), 1110, 380 + h1 + h2 + 40, 28, 580, GOLD, a * c.p(2))


def k_edge(fr, c):
    shown = c.span(1, 2) * len(EDGE) if c.on(1) else 0
    lit = {key(r["u"], r["v"]) for r in EDGE[: max(0, int(shown))]}
    g01(fr, 1.0, hl=lit)
    math_line(fr, [("edge(u, v)  =  w(u, v)", IVORY)], 1380, 210, 40, c.p(0))
    ranking(fr, 1100, 280, EDGE, shown, 1.0, L("直接边权", "DIRECT WEIGHT"), hl=1 if c.on(2) else None, w=560)
    if c.on(2):
        badge(fr, 1380, 700, L("排序键 (−分数, u, v)：A–B 在 D–E 前", "sort key (−score, u, v): A–B before D–E"), TEAL, c.p(2), 20, screen=True)


def k_shared(fr, c):
    ac = SH[("A", "C")]
    cols = {n: NEUTRAL for n in P5}
    cols.update({"A": GOLD, "C": GOLD})
    hl = {key("A", "C")}
    if c.on(2):
        hl |= {key("A", "B"), key("B", "C")}
        cols["B"] = TEAL
    g01(fr, 1.0, colors=cols, hl=hl)
    math_line(fr, [("shared(u, v)  =  w(u, v)  +  ", IVORY), ("Σ", IVORY), ("x", MUTED, "under"), ("  min(w(u, x), w(v, x))", GOLD)], 1380, 220, 34, c.p(0))
    panel(fr, 1100, 300, 560, 260, c.p(1), "A–C")
    fr.text(L("直接", "direct"), 1140, 400, 26, MUTED, c.p(1))
    fr.text(fmt(ac["parts"]["direct"]), 1620, 400, 28, IVORY, c.p(1), role="mono", anchor="r")
    if c.on(2):
        v = ac["parts"]["via"][0]
        fr.text(L(f"经 {v['x']}", f"via {v['x']}"), 1140, 450, 26, MUTED, c.p(2))
        fr.text(f"min({v['wu']:g}, {v['wv']:g}) = {v['min']:g}", 1620, 450, 28, TEAL, c.p(2), role="mono", anchor="r")
    if c.on(3):
        fr.line((1140, 480), (1620, 480), FAINT, 1.2, c.p(3))
        fr.text(L("合计", "total"), 1140, 530, 28, IVORY, c.p(3))
        fr.text(fmt(ac["score"]), 1620, 534, 40, GOLD, c.p(3), role="serif", anchor="r")


def k_bd(fr, c):
    bd = SH[("B", "D")]
    cols = {n: NEUTRAL for n in P5}
    cols.update({"B": GOLD, "D": GOLD, "C": TEAL})
    g01(fr, 1.0, colors=cols, hl={key("B", "C"), key("C", "D")} if c.on(1) else set(), ghost=("B", "D", 1.0))
    panel(fr, 1100, 300, 560, 220, c.p(0), "B–D")
    fr.text(L("直接：没有线", "direct: no wire"), 1140, 400, 26, ROSE, c.p(0))
    fr.text("0", 1620, 400, 28, ROSE, c.p(0), role="mono", anchor="r")
    if c.on(1):
        fr.text(L("经 C", "via C"), 1140, 460, 26, MUTED, c.p(1))
        fr.text(f"min(4, 2) = {fmt(bd['score'])}", 1620, 460, 28, GOLD, c.p(1), role="mono", anchor="r")
    if c.on(2):
        fr.text(L("要检查所有 10 对，而不只是有线的 6 对", "check all 10 pairs, not only the 6 that share a wire"), 1380, 600, 24, GOLD, c.p(2), anchor="c")


def k_priority(fr, c):
    mode = None if not c.on(1) else ("edge" if c.k == 1 else "shared")
    pos = priority(fr, c.p(0, 1.0), mode, box=(260, 260, 1080, 720))
    if c.on(1):
        panel(fr, 1220, 300, 520, 300, 1.0, L("第一对", "THE FIRST PAIR"))
        a1, a2 = c.p(1), c.p(2)
        fr.text(L("直接边权", "direct weight"), 1260, 400, 26, GOLD if c.k == 1 else MUTED, a1)
        fr.text(f"X–Y @ {PR_EDGE[0]['score']:g}", 1700, 400, 30, GOLD if c.k == 1 else MUTED, a1, role="mono", anchor="r")
        if c.on(2):
            fr.text(L("共同邻居", "shared neighbours"), 1260, 480, 26, GOLD, a2)
            fr.text(f"P–Q @ {PR_SHARED[0]['score']:g}", 1700, 480, 30, GOLD, a2, role="mono", anchor="r")
            fr.text("4 + min(4, 4)", 1700, 530, 22, TEAL, a2, role="mono", anchor="r")


def k_pin(fr, c):
    netlist(fr, c.p(0, 1.0), "wide" if c.k <= 1 else "n1")
    math_line(fr, [("pin-count(u, v)  =  ", IVORY), ("Σ", IVORY), ("e ∋ u, v", MUTED, "under"), ("  w(e) / (|e| − 1)", GOLD)], W / 2, 200, 34, c.p(1))
    if c.on(2):
        a = c.p(2)
        pin_box(fr, a, 60, 700)


def k_take(fr, c):
    items = [(L("评分只排名，不分组；分组从 Module 03 开始", "A score ranks; grouping starts in Module 03"), TEAL),
             (L("稳定排名：(−分数, u, v)，与输入顺序无关", "Stable ranking: (−score, u, v), whatever the input order"), TEAL),
             (L("换评分，第一对就可能变：写明用哪一种", "Change the score and the first pair may change: say which"), GOLD),
             (L("不是距离，也不是概率", "Not a distance, not a probability"), ROSE)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 260 + i * 120
            fr.rect(260, y, 1400, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 310, y + 58, 28, col, a, role="mono")
            fr.text(s, 400, y + 58, 32, IVORY, a)


CONCISE = Film(
    "concise", "concise", L("精讲：三种评分", "The essentials"), None, BRAND, poster_at=60.0, music="score:steady", seed=22,
    why=L("只讲必须掌握的：三种评分怎么算、稳定排名、换评分为什么换第一对。", "Only what you must know: how the three scores work, the stable ranking, and why a different score picks a different first pair."),
    scenes=[
        Scene("k00-title", k_title, [Beat(None, 3.0)]),
        Scene("k01-question", k_question, [Beat(L("聚类的第一步：谁和谁更该在一起？", "Step one of clustering: which pairs belong together?"), 2.6),
                                            Beat(L("给每一对打一个分，再从高到低排好。", "Give every pair a score, then rank them from high to low."), 3.0),
                                            Beat(L("注意：分数只排名，不分组。", "Note: a score ranks pairs; it does not group them."), 2.8)],
              chapter=L("问题", "THE PROBLEM")),
        Scene("k02-edge", k_edge, [Beat(L("第一种：直接边权，线有多粗，分数就是多少。", "One: direct weight. The score is the weight of the wire."), 3.4),
                                   Beat(L("G01 的 6 条边，就是 6 对。", "G01's six edges give six pairs."), 3.6),
                                   Beat(L("A–B 和 D–E 并列 5：按 (−分数, u, v) 排，A–B 在前。", "A–B and D–E tie at 5: sorted by (−score, u, v), A–B comes first."), 4.2)],
              chapter=L("直接边权", "DIRECT WEIGHT")),
        Scene("k03-shared", k_shared, [Beat(L("第二种：共同邻居。", "Two: shared neighbours."), 2.0),
                                       Beat(L("A–C：直接边 1。", "A–C: the direct wire is 1."), 2.0),
                                       Beat(L("再加经过 B 的联系：取较弱的边，min(5, 4) = 4。", "Add the link through B, at its weaker wire: min(5, 4) = 4."), 3.6),
                                       Beat(L("合计 5。", "Total: 5."), 1.8)],
              chapter=L("共同邻居", "SHARED NEIGHBOURS")),
        Scene("k04-bd", k_bd, [Beat(L("B 和 D 之间没有线，", "B and D share no wire,"), 2.0),
                               Beat(L("但经过 C 得到 min(4, 2) = 2。", "but through C they get min(4, 2) = 2."), 2.8),
                               Beat(L("所以要检查所有 10 对，没有线的对也可能有分。", "So check all 10 pairs: a pair with no wire can still score."), 3.6)]),
        Scene("k05-priority", k_priority, [Beat(L("换评分，第一对会变。看原作者的 priority 图。", "Change the score and the first pair changes. Look at the original author's priority graph."), 3.8),
                                           Beat(L("直接边权：X–Y = 5 排第一。", "Direct weight: X–Y = 5 comes first."), 2.6),
                                           Beat(L("共同邻居：P–Q = 4 + 4 = 8，超过了 X–Y。", "Shared neighbours: P–Q = 4 + 4 = 8 overtakes X–Y."), 3.4)],
              chapter=L("换评分", "ANOTHER SCORE")),
        Scene("k06-pin", k_pin, [Beat(L("第三种用于多引脚 net：两条 5 引脚的宽 net，一条私有 net。", "Three, for multi-pin nets: two wide 5-pin nets and one private net."), 4.0),
                                 Beat(L("每个 net 摊成 |e| − 1 份。", "Share each net out over |e| − 1."), 2.6),
                                 Beat(L("A–B 只得 1/4 + 1/4 = 0.5，E–F 得 1。", "A–B gets only 1/4 + 1/4 = 0.5; E–F gets 1."), 3.4)],
              chapter="PIN-COUNT"),
        Scene("k07-take", k_take, [Beat(L("记住四点。", "Four things to keep."), 1.4),
                                   Beat(L("只排名，不分组；", "It ranks; it does not group;"), 1.8),
                                   Beat(L("排名要稳定；", "the ranking must be stable;"), 1.6),
                                   Beat(L("换评分会换第一对，也不要把分数当距离。下面的实验里试一试。", "a different score can pick a different first pair, and a score is not a distance. Try it in the lab below."), 4.6)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])


# ====================================================================== advanced film
HUB = T["hub"]
LOP = T["lopsided"]
COST = T["cost"]
REV_OK = T["reversedShared"] == SHARED
HUB_POS = {"H": (560, 500), "a": (560, 290), "b": (742, 395), "c": (742, 605), "d": (560, 710), "e": (378, 605), "f": (378, 395), "P": (980, 330), "Q": (980, 670)}
HUB_LEAF = [p for p in HUB["shared"] if "H" not in (p["u"], p["v"]) and p["u"] not in "PQ" and p["v"] not in "PQ"]
HUB_PQ = next(p for p in HUB["shared"] if (p["u"], p["v"]) == ("P", "Q"))
assert len(HUB_LEAF) == 15 and all(p["score"] == 3 and p["parts"]["direct"] == 0 for p in HUB_LEAF) and HUB_PQ["score"] == 2
assert COST["grid"]["allPairs"] == 49995000 and COST["grid"]["viaNeighbours"] == 58804 and REV_OK
UV = next(p for p in LOP["shared"] if (p["u"], p["v"]) == ("U", "V"))
assert UV["score"] == 1 and UV["parts"]["via"][0]["wu"] == 10


def a_title(fr, c):
    title_card(fr, L("亲和度指标", "Affinity Metrics"), L("进阶：模型的代价", "IN DEPTH: WHAT A SCORE ASSUMES"), c.p(0, 1.2), kicker=L("MODULE 02", "MODULE 02"))


def a_recap(fr, c):
    rows = [("edge", "w(u, v)"), ("shared", "w(u, v) + Σ min(w(u,x), w(v,x))"), ("pin-count", "Σ w(e) / (|e| − 1)")]
    panel(fr, 340, 280, 1240, 380, c.p(0), L("三种评分", "THREE SCORES"))
    for i, (n, f) in enumerate(rows):
        a = c.p(0, delay=i * 0.4)
        fr.text(n, 400, 400 + i * 90, 32, GOLD, a, role="mono")
        fr.text(f, 700, 400 + i * 90, 32, IVORY, a, role="serif")
    if c.on(1):
        fr.text(L("每一种都是一个假设：它认为什么样的联系“算数”", "each one is an assumption about which links count"), W / 2, 740, 26, TEAL, c.p(1), anchor="c")


def lop_graph(fr, alpha, show=0.0):
    pos = {"U": (420, 520), "X": (760, 340), "V": (1100, 520)}
    graph(fr, pos, [("U", "X", 10), ("V", "X", 1)], {"U": GOLD, "V": GOLD, "X": TEAL}, alpha, r=44, name_size=38)
    fr.line(pos["U"], pos["V"], ROSE, 1.6, 0.5 * alpha, dash=[8, 8])
    return pos


def a_min(fr, c):
    lop_graph(fr, c.p(0, 1.0))
    panel(fr, 1240, 300, 520, 300, c.p(1), L("U–V 经过 X", "U–V THROUGH X"))
    v = UV["parts"]["via"][0]
    if c.on(1):
        fr.text(L("取较弱：min", "weaker: min"), 1280, 400, 26, TEAL, c.p(1))
        fr.text(f"min({v['wu']:g}, {v['wv']:g}) = {UV['score']:g}", 1720, 400, 28, TEAL, c.p(1), role="mono", anchor="r")
    if c.on(2):
        fr.text(L("若用和：sum", "if we used: sum"), 1280, 480, 26, ROSE, c.p(2))
        fr.text(f"{v['wu']:g} + {v['wv']:g} = {v['wu'] + v['wv']:g}", 1720, 480, 28, ROSE, c.p(2), role="mono", anchor="r")
    if c.on(3):
        fr.text(L("V 和 X 只有一根细线：链条的强度由最弱的一环决定", "V barely touches X: a chain is as strong as its weakest link"), W / 2, 760, 24, GOLD, c.p(3), anchor="c")


def a_hub(fr, c):
    leaves = "abcdef"
    hl = set()
    k = c.span(1, 2) if c.on(1) else 0
    pairs = [(p["u"], p["v"]) for p in HUB_LEAF]
    edges = [tuple(e) for e in HUB["graph"]["edges"]]
    cols = {n: (TEAL if n == "H" else BLUE if n in "PQ" else NEUTRAL) for n in HUB_POS}
    graph(fr, HUB_POS, edges, cols, c.p(0, 1.0), r=34, name_size=30)
    for j, (u, v) in enumerate(pairs):
        if k * len(pairs) > j:
            fr.line(HUB_POS[u], HUB_POS[v], GOLD, 1.4, 0.55, glow=0.2, dash=[6, 6])
    if c.on(1):
        panel(fr, 1220, 300, 540, 320, 1.0, L("共同邻居排名", "SHARED-NEIGHBOUR RANKING"))
        fr.text(L("叶子两两（无直接线）", "leaf pairs (no wire)"), 1260, 400, 24, MUTED, c.p(1))
        fr.text(L(f"{len(HUB_LEAF)} 对 × {HUB_LEAF[0]['score']:g}", f"{len(HUB_LEAF)} pairs × {HUB_LEAF[0]['score']:g}"), 1720, 400, 26, GOLD, c.p(1), role="mono", anchor="r")
        fr.text(L("真正连着的 P–Q", "P–Q, actually wired"), 1260, 470, 24, MUTED, c.p(1))
        fr.text(f"{HUB_PQ['score']:g}", 1720, 470, 26, ROSE, c.p(1), role="mono", anchor="r")
    if c.on(3):
        fr.paragraph(L("常见的修正：按度数归一化（例如 Jaccard），或把大枢纽单独处理。本课程不实现，只指出问题。",
                       "Common fixes: normalise by degree (Jaccard, for example) or treat big hubs separately. This course does not implement them; it only names the problem."),
                     1240, 680, 22, 520, TEAL, c.p(3))


def a_cost(fr, c):
    g = COST["grid"]
    panel(fr, 260, 260, 1400, 420, c.p(0), L("10 000 个单元的网格（每个连 4 个邻居）", "A GRID OF 10,000 CELLS (EACH WIRED TO 4 NEIGHBOURS)"))
    fr.text(L("检查所有无序对", "check every unordered pair"), 320, 390, 28, MUTED, c.p(0))
    fr.text("n(n − 1) / 2", 900, 390, 28, IVORY, c.p(0), role="serif")
    fr.text(f"{g['allPairs']:,}", 1600, 390, 34, ROSE, c.p(0), role="mono", anchor="r")
    if c.on(1):
        fr.text(L("只沿邻居枚举", "enumerate along neighbours"), 320, 480, 28, MUTED, c.p(1))
        fr.text("Σ C(deg(x), 2)", 900, 480, 28, IVORY, c.p(1), role="serif")
        fr.text(f"{g['viaNeighbours']:,}", 1600, 480, 34, TEAL, c.p(1), role="mono", anchor="r")
        bar(fr, 320, 540, 1280, 14, 1.0, ROSE, c.p(1))
        bar(fr, 320, 580, 1280, 14, g["viaNeighbours"] / g["allPairs"], TEAL, c.p(1), glow=0.5)
    if c.on(2):
        fr.paragraph(L("零分对根本不必看：有分的对，要么有直接线，要么有共同邻居。", "Zero-score pairs never need a look: a pair that scores has a wire or a shared neighbour."), 320, 640, 24, 1280, GOLD, c.p(2))
    if c.on(3):
        a = c.p(3)
        fr.text(L("但一个 1 000 引脚的时钟 net 自己就带来", "but a single 1,000-pin clock net alone brings"), 320, 760, 24, MUTED, a)
        fr.text(f"{1000 * 999 // 2:,}", 1600, 760, 30, ROSE, a, role="mono", anchor="r")
        fr.text(L("对：很多工具会跳过或单独处理超大 net", "pairs: many tools skip or treat very large nets separately"), 320, 800, 22, MUTED, a)


def a_conserve(fr, c):
    xs = netlist(fr, c.p(0, 1.0), "wide" if c.k >= 1 else None)
    totals = {}
    for p in PIN["scores"]:
        for n in (p["u"], p["v"]):
            totals[n] = totals.get(n, 0) + p["score"]
    nets_of = {n: sum(net["w"] for net in T["netlist"]["nets"] if n in net["pins"]) for n in xs}
    assert all(abs(totals[n] - nets_of[n]) < 1e-9 for n in xs)
    if c.on(1):
        for n, x in xs.items():
            badge(fr, x, 760, f"{fmt(totals[n])}", GOLD, c.p(1), 22, screen=True)
        fr.text(L("每个单元收到的分数之和", "each cell's total score"), 380 - 60, 770, 20, GOLD, c.p(1), anchor="r")
    if c.on(2):
        fr.paragraph(L("= 它所在 net 的权重之和：一个 net 不论多大，都只给每个引脚整整 w(e)。", "= the total weight of its nets: a net of any size gives each pin exactly w(e)."),
                     W / 2 - 600, 860 - 40, 26, 1200, TEAL, c.p(2), anchor="l")


def a_ties(fr, c):
    rows = SHARED[:4]
    ranking(fr, 260, 260, rows, 4, c.p(0), L("原输入", "ORIGINAL INPUT"), w=560)
    if c.on(1):
        ranking(fr, 1100, 260, T["reversedShared"][:4], 4, c.p(1), L("节点与边全部倒序", "NODES AND EDGES REVERSED"), w=560, col=TEAL)
        fr.text("=", W / 2 + 10, 420, 60, TEAL, c.p(1), anchor="c", role="serif")
    if c.on(2):
        fr.paragraph(L("Module 03 先合并排名第一的一对：平票规则不固定，同一张图就可能合并出不同的结果。",
                       "Module 03 merges the top pair first: without a fixed tie rule, the same graph could merge into different results."),
                     W / 2 - 640, 640, 26, 1280, GOLD, c.p(2))


M03 = json.loads((ROOT / "site/data/m03-greedy-pair-merge/traces.json").read_text())["runs"]["k2-capnone"]["events"]
MERGE1, MERGE2 = M03[1]["decision"], M03[2]
assert (MERGE1["a"], MERGE1["b"], MERGE1["affinity"]) == ("A", "B", 5)
AB_C = next(x for x in MERGE2["candidates"] if (x["a"], x["b"]) == ("AB", "C"))
AB_D = next((x for x in MERGE2["candidates"] if (x["a"], x["b"]) == ("AB", "D")), None)
assert AB_C["affinity"] == 5 and sorted(p["w"] for p in AB_C["parts"]) == [1, 4]


def a_clusters(fr, c):
    cols = {n: (GOLD if n in "AB" else NEUTRAL) for n in P5}
    if c.on(1):
        cols["C"] = TEAL
    hl = {key(p["u"], p["v"]) for p in AB_C["parts"]} if c.on(1) else {key("A", "B")}
    # the merged cluster AB as a soft halo around A and B
    (ax, ay), (bx, by) = P5["A"], P5["B"]
    fr.line((ax, ay), (bx, by), GOLD, 96, 0.10 * c.p(0), glow=0.2 * c.p(0))
    g01(fr, 1.0, colors=cols, hl=hl)
    fr.text("AB", (ax + bx) / 2, min(ay, by) - 70, 30, GOLD, c.p(0), role="serif", anchor="c")
    panel(fr, 1080, 280, 620, 300, c.p(0), L("簇与簇之间的亲和度", "AFFINITY BETWEEN CLUSTERS"))
    fr.text(L("合并 A、B 之后", "after merging A and B"), 1120, 380, 26, MUTED, c.p(0))
    if c.on(1):
        parts = " + ".join(f"w({p['u']},{p['v']})" for p in AB_C["parts"])
        fr.text("AB–C", 1120, 450, 28, IVORY, c.p(1), role="serif")
        fr.text(f"{parts} = " + " + ".join(f"{p['w']:g}" for p in AB_C["parts"]) + f" = {AB_C['affinity']:g}", 1660, 450, 24, TEAL, c.p(1), role="mono", anchor="r")
    if c.on(2):
        fr.paragraph(L("把两簇之间所有边的权重加起来：本章的“直接边权”推广到簇。", "Add up every wire between the two clusters: this module's direct weight, extended to clusters."), 1120, 510, 24, 560, GOLD, c.p(2))


def a_summary(fr, c):
    items = [(L("min：经过第三者的联系，不比最弱的一环强", "min: a link through a third cell is no stronger than its weakest wire"), TEAL),
             (L("共同邻居会高估“共享一个大枢纽”的对", "shared neighbours overrate pairs that only share a big hub"), ROSE),
             (L("沿邻居枚举，代价随度数而不是 n² 增长", "enumerate along neighbours: cost grows with degree, not n²"), TEAL),
             (L("pin-count 让每个 net 给每个引脚整整 w(e)", "pin-count gives each pin exactly w(e) from each net"), GOLD),
             (L("固定平票规则，下游的合并才可复现", "fix the tie rule so downstream merging is reproducible"), GOLD),
             (L("簇间亲和度 = 两簇之间边权之和（下一章）", "cluster affinity = the summed weight between clusters (next module)"), BLUE)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 200 + i * 104
            fr.rect(220, y, 1480, 84, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 54, 26, col, a, role="mono")
            fr.text(s, 350, y + 54, 30, IVORY, a)


ADVANCED = Film(
    "advanced", "advanced", L("进阶：评分背后的假设", "In depth: what a score assumes"), None, BRAND, poster_at=70.0, music="score:calm", seed=34,
    why=L("为什么取 min、共同邻居的枢纽问题、只沿邻居枚举的代价、pin-count 守恒了什么，以及平票为什么必须有规则。",
          "Why min, the hub problem of shared neighbours, the cost of enumerating along neighbours, what pin-count preserves, and why ties need a rule."),
    scenes=[
        Scene("a00-title", a_title, [Beat(None, 3.0)]),
        Scene("a01-recap", a_recap, [Beat(L("回顾三种评分。", "The three scores again."), 2.4),
                                     Beat(L("每一种都在假设：什么样的联系才“算数”。", "Each one assumes something about which links count."), 3.2)],
              chapter=L("回顾", "RECAP")),
        Scene("a02-min", a_min, [Beat(L("U 和 V 之间没有线，都连着 X：U–X 是 10，V–X 只有 1。", "U and V share no wire; both touch X: U–X is 10, V–X only 1."), 4.2),
                                 Beat(L("取较弱的边：经过 X 的联系是 1。", "Take the weaker wire: the link through X is 1."), 3.0),
                                 Beat(L("如果改用和，会得到 11，比 U–X 本身还像“亲近”。", "With a sum it would be 11, and look almost as close as U–X itself."), 4.2),
                                 Beat(L("V 只是轻轻碰了 X 一下。链条的强度，由最弱的一环决定。", "V barely touches X. A chain is as strong as its weakest link."), 4.4)],
              chapter=L("一 · 为什么取 min", "I · WHY MIN")),
        Scene("a03-hub", a_hub, [Beat(L("再看一个枢纽：H 连着 6 个叶子，每条边 3；旁边 P–Q 真有一根线，权重 2。", "Now a hub: H reaches six leaves at weight 3; nearby, P–Q share a real wire of weight 2."), 6.0),
                                 Beat(L(f"叶子两两没有线，却都经过 H 得到 3：一共 {len(HUB_LEAF)} 对。", f"No two leaves are wired, yet each pair gets 3 through H: {len(HUB_LEAF)} pairs in all."), 4.6),
                                 Beat(L("它们全都排在真正连着的 P–Q 前面。", "Every one of them ranks above P–Q, which really are wired."), 3.6),
                                 Beat(L("这是共同邻居的已知弱点；常见的修正是按度数归一化。", "This is a known weakness of shared neighbours; a common fix is to normalise by degree."), 4.8)],
              chapter=L("二 · 枢纽问题", "II · THE HUB PROBLEM")),
        Scene("a04-cost", a_cost, [Beat(L("代价：一万个单元，所有无序对将近五千万。", "Cost: with ten thousand cells, there are almost fifty million unordered pairs."), 4.4),
                                   Beat(L("只沿邻居枚举，在这张网格上只要不到六万次。", "Enumerating along neighbours takes under sixty thousand steps on this grid."), 4.4),
                                   Beat(L("因为有分的对，要么有直接线，要么有共同邻居。", "Because a pair that scores has either a wire or a shared neighbour."), 4.0),
                                   Beat(L("但超大的 net 本身就会带来几十万对，所以很多工具会把它们单独处理。", "But one huge net alone brings hundreds of thousands of pairs, so many tools treat such nets separately."), 6.2)],
              chapter=L("三 · 代价", "III · COST")),
        Scene("a05-conserve", a_conserve, [Beat(L("pin-count 为什么除以 |e| − 1？", "Why does pin-count divide by |e| − 1?"), 3.0),
                                           Beat(L("把每个单元收到的分数加起来：", "Add up the score each cell receives:"), 3.0),
                                           Beat(L("正好等于它所在 net 的权重之和。一个 net 不论多大，都只给每个引脚整整 w(e)。", "it equals the total weight of the cell's nets. Whatever its size, a net gives each pin exactly w(e)."), 6.6)],
              chapter=L("四 · pin-count 守恒什么", "IV · WHAT PIN-COUNT PRESERVES")),
        Scene("a06-ties", a_ties, [Beat(L("最后，平票。", "Last, ties."), 1.8),
                                   Beat(L("把节点和边全部倒序输入，排名一模一样。", "Feed the nodes and edges in reverse and the ranking is identical."), 3.8),
                                   Beat(L("这很重要：下一章先合并第一名，平票没有规则，结果就不可复现。", "It matters: the next module merges the top pair first, and without a tie rule the result is not reproducible."), 6.4)],
              chapter=L("五 · 平票", "V · TIES")),
        Scene("a07-clusters", a_clusters, [Beat(L("排名第一的 A–B 合并之后，下一步要比的就不再是两个单元，而是簇。", "Once the top pair A–B merges, the next comparison is no longer between two cells but between clusters."), 5.6),
                                           Beat(L("AB 和 C 之间有两根线：1 + 4 = 5。", "AB and C share two wires: 1 + 4 = 5."), 3.4),
                                           Beat(L("把两簇之间的边权加起来，这就是下一章用的亲和度。", "Add up the wires between two clusters: that is the affinity the next module uses."), 4.8)],
              chapter=L("六 · 从一对到一簇", "VI · FROM PAIRS TO CLUSTERS")),
        Scene("a08-summary", a_summary, [Beat(L("六点小结。", "Six things to keep."), 1.6)] + [Beat(None, 2.6) for _ in range(5)]
              + [Beat(L("下一章：用簇间边权和真正开始合并。", "Next: merging for real, with the summed weight between clusters."), 3.4)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

FILMS = [STORY, CONCISE, ADVANCED]
ORDER = ["story", "concise", "advanced", "lab"]
