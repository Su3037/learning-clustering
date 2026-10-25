"""Module 03 · Greedy pair merge — the four films.

  story     popular science, cut to "We Never (Remix)": five friends split into two cars, a folder that sorts 10
            before 2, and hotel rooms that hold two.
  concise   the essentials: the rule, the tie, contraction, the trajectory 18 → 13 → 8 → 3, the comparator bug, capacity.
  advanced  why the cut drops by the affinity, how sum affinity snowballs, comparing keys, the three stop states,
            no backtracking, and what a merge step costs.
  lab       experiment walkthrough recorded from the real page (walkthrough.mjs → scripts/film/walkthrough.py).

Every state on G01 is read from site/data/m03-greedy-pair-merge/traces.json, which scripts/build-traces.mjs
produces by running site/engines/merge.js. The larger examples (the 24-cell circuit, the grid) are run through the
course's Python reference, python/m03-greedy-pair-merge/reference.py, which tests/crosscheck.py checks against
the engine.
"""
import importlib.util
import json
import math
from pathlib import Path

from cine import (W, H, L, tr, Film, Scene, Beat, GOLD, TEAL, BLUE, ROSE, AMBER, CORAL, LILAC, SAGE, IVORY, MUTED, FAINT, DIM,
                  PANEL_BG, NODE_BG, clamp, ease, lerp, lerp2, title_card, panel, badge, bar, code_panel, table, graph, math_line,
                  fit, mixc, pulse, count_hits)
from hooks import droplets
from story import S, TRACK, INTRO_HITS, ROLL_HITS, FILL1, FILL2, PHRASE, FILL3, FILL4, title_assemble, credits, MUSIC_LINE, landed

ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m03-greedy-pair-merge/traces.json").read_text())
T4 = json.loads((ROOT / "site/data/m04-size-constrained-agglomerative/traces.json").read_text())
CIRCUIT = json.loads((ROOT / "site/data/m05-label-propagation/film-graphs.json").read_text())["circuit"]
BRAND = L("Learning Clustering · Module 03 · 贪心成对合并", "Learning Clustering · Module 03 · Greedy pair merge")

_spec = importlib.util.spec_from_file_location("m03ref", ROOT / "python/m03-greedy-pair-merge/reference.py")
REF = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(REF)

E5 = [tuple(e) for e in T["g01"]["edges"]]
P5 = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (260, 250, 860, 760))
RUN = T["runs"]["k2-capnone"]
EV = RUN["events"]
STATES = [e["after"] for e in EV]
CAP2 = T["runs"]["k2-cap2"]
LEG = T["legacy"]
NEUTRAL = "#9fbcbc"
HUE = {"AB": TEAL, "ABC": TEAL, "DE": BLUE, "AC": ROSE, "ACD": ROSE, "ACDE": ROSE}

# facts the captions state, checked against the engine output
assert RUN["result"]["cutTrajectory"] == [18, 13, 8, 3] and RUN["result"]["labels"] == ["ABC", "DE"]
assert [(e["decision"]["a"], e["decision"]["b"], e["decision"]["affinity"]) for e in EV[1:]] == [("A", "B", 5), ("AB", "C", 5), ("D", "E", 5)]
AB_C = next(x for x in EV[2]["candidates"] if (x["a"], x["b"]) == ("AB", "C"))
assert sorted(p["w"] for p in AB_C["parts"]) == [1, 4]
assert LEG["first"]["a"] == "A" and LEG["first"]["b"] == "C" and LEG["first"]["affinity"] == 1
assert LEG["result"]["labels"] == ["ACDE", "B"] and LEG["result"]["cut"] == 9
assert CAP2["result"]["labels"] == ["AB", "C", "DE"] and CAP2["result"]["cut"] == 8 and not CAP2["result"]["targetReached"]
assert CAP2["result"]["stopReason"] == "capacity-blocked"
CAP2_STOP = CAP2["events"][-1]
assert sorted((c["a"], c["b"], c["size"]) for c in CAP2_STOP["candidates"]) == [("AB", "C", 3), ("C", "DE", 3)]
assert T["runs"]["k3-capnone"]["result"]["cut"] == 8
assert sorted(["10", "9", "2"]) == ["10", "2", "9"] and sorted(["1.jpg", "2.jpg", "10.jpg"]) == ["1.jpg", "10.jpg", "2.jpg"]  # text order, as JS's default sort()


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


def hull(fr, pts, col, alpha, R=72, label=None, label_at=None, size=22):
    """A soft rounded outline around a cluster's nodes."""
    if alpha <= 0:
        return
    ring = [(round(x + R * math.cos(t * math.pi / 14), 2), round(y + R * math.sin(t * math.pi / 14), 2)) for x, y in pts for t in range(28)]
    poly = convex(ring)
    fr.polyline(poly, col, 1.8, 0.75 * alpha, close=True, fill=col, fill_alpha=0.08 * alpha)
    if label:
        x, y = label_at or (sum(p[0] for p in pts) / len(pts), min(p[1] for p in pts) - R - 14)
        fr.text(label, x, y, size, col, alpha, anchor="c", role="serif")


def state(fr, clusters, alpha=1.0, pos=None, names=None, focus=(), cut=True, labels=True, hue=None, hl=(), r=40, size=None):
    """G01 drawn as clusters: soft hulls around merged groups, crossing wires rose (they count in the cut)."""
    pos = pos or P5
    hue = hue or HUE
    where = {m: c["label"] for c in clusters for m in c["members"]}
    for c in clusters:
        if len(c["members"]) > 1:
            pts = [pos[m] for m in c["members"]]
            below = sum(p[1] for p in pts) / len(pts) > sum(p[1] for p in pos.values()) / len(pos)
            lab = None
            if labels:
                nm = "".join(names[m][:1] if names else m for m in c["members"]) if not names else " · ".join(tr(names[m]) for m in c["members"])
                lab = nm
            R = r + 32
            at = (sum(p[0] for p in pts) / len(pts), (max(p[1] for p in pts) + R + 34) if below else (min(p[1] for p in pts) - R - 14))
            hull(fr, pts, hue.get(c["label"], LILAC), alpha, R=R, label=lab, label_at=at, size=size or (20 if names else 24))
    crossing = {key(u, v) for u, v, _ in E5 if where[u] != where[v]} if cut else set()
    cols = {n: (hue.get(where[n], NEUTRAL) if len(where[n]) > 1 else NEUTRAL) for n in pos}
    graph(fr, pos, E5, cols, alpha, cut=crossing, hl_edges=hl, names=names is None, r=r, glow_nodes=focus)
    for n in focus:
        fr.ring(pos[n], r + 9, GOLD, 2.4, alpha, glow=0.6 * alpha)
    if names:
        for n, p in pos.items():
            fr.text(tr(names[n]), p[0], p[1] + 9, 26, IVORY, alpha, anchor="c", role="serif")


def cut_meter(fr, value, x=1120, y=250, alpha=1.0, title=None, total=18, w=560):
    title = title or L("cut · 被切断的边权", "CUT · WEIGHT ON SEVERED WIRES")
    panel(fr, x, y, w, 190, alpha, title)
    col = ROSE if value > 3.01 else TEAL
    fr.text(f"{value:g}" if abs(value - round(value)) < 1e-9 else f"{value:.0f}", x + w / 2, y + 128, 64, col, alpha, role="serif", anchor="c", glow=0.3 * alpha)
    bar(fr, x + 40, y + 160, w - 80, 10, value / total, col, alpha)


def cand_rows(fr, x, y, cands, alpha, title, chosen=None, w=560, lh=48, size=24, n_shown=99, blocked_word=None):
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
        fr.text(f"{c_['a']}–{c_['b']}", x + 40, yy, size, ROSE if bad else IVORY, a, role="serif")
        parts = c_.get("parts") or []
        aff = f"{c_['affinity']:g}" + (f"  ({' + '.join(f'{p['w']:g}' for p in parts)})" if len(parts) > 1 else "")
        fr.text(aff, x + w - 170, yy, size, GOLD if on else (ROSE if bad else IVORY), a, role="mono", anchor="r", glow=0.3 * a if on else 0)
        if bad:
            fr.text(tr(blocked_word or L("超容量", "over capacity")), x + w - 30, yy, size - 6, ROSE, a, anchor="r")
        elif on:
            fr.text(tr(L("选中", "chosen")), x + w - 30, yy, size - 6, GOLD, a, anchor="r")


# ---------------------------------------------------------------- five friends (popular film)
FR = {"A": "Ada", "B": "Ben", "C": "Cai", "D": "Dev", "E": "Eva"}
FPOS = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (280, 230, 860, 760))
FHUE = {"AB": TEAL, "ABC": TEAL, "DE": BLUE, "AC": ROSE, "ACD": ROSE, "ACDE": ROSE}


def friends(fr, alpha, shown=None, clusters=None, focus=(), cut=True, weights=True, hl=(), labels=True):
    clusters = clusters or STATES[0]
    if shown is not None:
        # people appear one by one; wires only between people already on screen
        vis = {n for i, n in enumerate("ABCDE") if shown[i] > 0}
        for i, n in enumerate("ABCDE"):
            a = alpha * shown[i]
            if a <= 0:
                continue
            p = FPOS[n]
            fr.dot(p, 46, NODE_BG, a)
            fr.ring(p, 46, NEUTRAL, 2.8, a)
            fr.text(FR[n], p[0], p[1] + 9, 26, IVORY, a, anchor="c", role="serif")
        return
    where = {m: c["label"] for c in clusters for m in c["members"]}
    for c in clusters:
        if len(c["members"]) > 1:
            pts = [FPOS[m] for m in c["members"]]
            below = sum(p[1] for p in pts) / len(pts) > 495
            at = (sum(p[0] for p in pts) / len(pts), (max(p[1] for p in pts) + 112) if below else (min(p[1] for p in pts) - 92))
            hull(fr, pts, FHUE.get(c["label"], LILAC), alpha, R=76, label=" · ".join(FR[m] for m in c["members"]) if labels else None, label_at=at, size=20)
    crossing = {key(u, v) for u, v, _ in E5 if where[u] != where[v]} if cut else set()
    cols = {n: (FHUE.get(where[n], NEUTRAL) if len(where[n]) > 1 else NEUTRAL) for n in FPOS}
    graph(fr, FPOS, E5, cols, alpha, cut=crossing, hl_edges=hl, names=False, r=46, weights=weights)
    for n in focus:
        fr.ring(FPOS[n], 56, GOLD, 2.4, alpha, glow=0.6 * alpha)
    for n, p in FPOS.items():
        fr.text(FR[n], p[0], p[1] + 9, 26, IVORY, alpha, anchor="c", role="serif")


def contraction(fr, k, alpha, pos, a="A", b="B", c_="C", label_y=-40):
    """The two wires from a and b to c slide together into one cluster wire labelled 1 + 4 = 5."""
    if k <= 0:
        return
    mid = ((pos[a][0] + pos[b][0]) / 2, (pos[a][1] + pos[b][1]) / 2)
    for s in (a, b):
        p = lerp2(pos[s], mid, ease(k))
        fr.line(p, pos[c_], GOLD, 3 + 2 * k, alpha * (0.9 - 0.4 * k), glow=0.5 * alpha)
    if k > 0.6:
        q = ease((k - 0.6) / 0.4)
        m = ((mid[0] + pos[c_][0]) / 2, (mid[1] + pos[c_][1]) / 2)
        badge(fr, m[0] + 70, m[1] + label_y, "1 + 4 = 5", GOLD, alpha * q, 22, screen=True)


# ====================================================================== popular film
def p_rule(fr, c):
    friends(fr, 1.0, clusters=STATES[0])
    if c.on(1):
        cut_meter(fr, 18, alpha=c.p(1), title=L("被拆散的交情", "FRIENDSHIP SPLIT APART"))
    if c.on(2):
        fr.paragraph(L("规则：每次把最投机的两组合并，直到只剩两组。", "The rule: merge the two groups that get along best, until two are left."),
                     1120, 540, 30, 600, IVORY, c.p(2), role="serif")


def p_title(fr, c):
    title_assemble(fr, c, L("合并，再合并", "Merge, and Merge Again"), L("贪心成对合并 · GREEDY PAIR MERGE", "GREEDY PAIR MERGE"), "MODULE 03")


def p_step1(fr, c):
    merged = c.T >= FILL1[0]
    clusters = STATES[1] if merged else STATES[0]
    hl = {key("A", "B"), key("D", "E")} if not merged else set()
    friends(fr, 1.0, clusters=clusters, hl=hl, focus=("A", "B", "D", "E") if c.on(0) and not merged else ())
    cuts = 13 if merged else 18
    k = landed(c.T, FILL1, len(FILL1) - 1) if merged else 0
    cut_meter(fr, lerp(18, 13, k) if merged else cuts, alpha=1.0, title=L("被拆散的交情", "FRIENDSHIP SPLIT APART"))
    cands = [{"a": "Ada", "b": "Ben", "affinity": 5}, {"a": "Dev", "b": "Eva", "affinity": 5}]
    cand_rows(fr, 1120, 500, cands, c.p(0), L("最投机的两对", "THE TWO BEST PAIRS"), chosen=0 if c.on(1) else None, w=560)
    if c.on(1):
        fr.text(tr(L("平票：按名字，A 在 D 前", "a tie: by name, A before D")), 1400, 760, 24, TEAL, c.p(1), anchor="c")


def p_step2(fr, c):
    joined = c.T >= S["accent"]
    clusters = STATES[2] if joined else STATES[1]
    friends(fr, 1.0, clusters=clusters, hl={key("A", "C"), key("B", "C")} if not joined and c.on(0) else set())
    if not joined:
        contraction(fr, c.span(0, 1) if c.on(0) else 0, 1.0, FPOS)
    k = ease((c.T - S["accent"]) / 0.4) if joined else 0
    cut_meter(fr, lerp(13, 8, k), alpha=1.0, title=L("被拆散的交情", "FRIENDSHIP SPLIT APART"))
    cands = [{"a": "Ada·Ben", "b": "Cai", "affinity": 5, "parts": [{"w": 1}, {"w": 4}]}, {"a": "Dev", "b": "Eva", "affinity": 5}]
    cand_rows(fr, 1120, 500, cands, c.p(0), L("下一步的候选", "THE NEXT CANDIDATES"), chosen=0 if c.on(1) else None, w=560)
    if c.on(1):
        fr.text(tr(L("又平票：[Ada, Ben] 在 [Dev] 前", "another tie: [Ada, Ben] before [Dev]")), 1400, 760, 24, TEAL, c.p(1), anchor="c")


def p_step3(fr, c):
    done = c.T >= FILL2[0]
    clusters = STATES[3] if done else STATES[2]
    friends(fr, 1.0, clusters=clusters)
    k = landed(c.T, FILL2, len(FILL2) - 1) if done else 0
    cut_meter(fr, lerp(8, 3, k), alpha=1.0, title=L("被拆散的交情", "FRIENDSHIP SPLIT APART"))
    traj = [18, 13, 8, 3]
    n = 3 + (k > 0.5)
    fr.text("  →  ".join(str(v) for v in traj[:n]), 1400, 520, 34, IVORY, c.p(0), role="mono", anchor="c")
    if done:
        a = landed(c.T, FILL2, len(FILL2) - 1)
        fr.text(tr(L("两辆车：Ada · Ben · Cai ｜ Dev · Eva", "two cars: Ada · Ben · Cai | Dev · Eva")), 1400, 600, 26, GOLD, a, anchor="c")
        fr.text(tr(L("只剩 Cai–Dev 2 和 Cai–Eva 1 被拆开", "only Cai–Dev 2 and Cai–Eva 1 are split")), 1400, 650, 22, MUTED, a, anchor="c")


FILES = ["1.jpg", "2.jpg", "10.jpg"]


def file_list(fr, x, y, order, alpha, title, col=IVORY, hl=None):
    panel(fr, x, y, 380, 300, alpha, title)
    for i, f in enumerate(order):
        yy = y + 120 + i * 60
        on = hl is not None and f == hl
        fr.rect(x + 40, yy - 30, 34, 40, fill="#16303a", stroke=FAINT, width=1, alpha=alpha, r=3, screen=True)
        fr.text(f, x + 96, yy, 30, GOLD if on else col, alpha, role="mono", glow=0.3 * alpha if on else 0)


def p_files(fr, c):
    file_list(fr, 760, 300, ["1.jpg", "10.jpg", "2.jpg"], c.p(0, 1.0), L("文件夹", "A FOLDER"), hl="10.jpg" if c.on(1) else None)


def p_flip(fr, c):
    n = count_hits(c.T, PHRASE)
    as_text = c.T >= PHRASE[0] and n % 2 == 1
    if c.T > PHRASE[-1] + 0.2:
        as_text = c.k < 1
    file_list(fr, 360, 280, ["1.jpg", "2.jpg", "10.jpg"], 1.0 if not as_text else 0.45, L("按数值", "AS NUMBERS"), col=TEAL if not as_text else MUTED)
    file_list(fr, 1180, 280, ["1.jpg", "10.jpg", "2.jpg"], 1.0 if as_text else 0.45, L("按文字", "AS TEXT"), col=ROSE if as_text else MUTED, hl="10.jpg" if as_text else None)
    if c.on(1):
        fr.paragraph(L("按文字比，是一个字符一个字符地比：“1” 比 “2” 小，于是 10 排在 2 前面。", "As text, characters compare one at a time: “1” is less than “2”, so 10 sorts before 2."),
                     W / 2 - 560, 680, 28, 1120, IVORY, c.p(1), anchor="l")


def p_bug(fr, c):
    a0 = c.p(0, 1.0)
    panel(fr, 300, 230, 1320, 330, a0, L("原网页怎样比较两对候选", "HOW THE ORIGINAL PAGE COMPARED TWO CANDIDATES"))
    rows = [("-5,A,B", "A–B · 5"), ("-1,A,C", "A–C · 1")]
    for i, (s, lab) in enumerate(rows):
        y = 350 + i * 100
        fr.text(lab, 360, y, 30, IVORY, a0, role="serif")
        for j, ch in enumerate(s):
            x = 700 + j * 46
            hot = c.on(1) and j == 1
            fr.rect(x - 20, y - 36, 40, 50, fill="#2a1d22" if hot else "#16303a", stroke=ROSE if hot else FAINT, width=1.4 if hot else 1, alpha=a0, r=4, screen=True)
            fr.text(ch, x, y, 30, ROSE if hot else IVORY, a0, role="mono", anchor="c")
    if c.on(1):
        fr.text(tr(L("“1” < “5”", "“1” < “5”")), 1380, 400, 34, ROSE, c.p(1), role="mono", anchor="c")
        fr.text(tr(L("→ 亲和度 1 被当成更好", "→ affinity 1 counts as better")), 1380, 450, 22, ROSE, c.p(1), anchor="c")
    if c.on(2):
        a = c.p(2)
        mini = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (420, 640, 820, 900))
        mini2 = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (1100, 640, 1500, 900))
        state(fr, [{"label": l, "members": list(l)} for l in LEG["result"]["labels"]], a, pos=mini, r=24, labels=False)
        state(fr, [{"label": l, "members": list(l)} for l in RUN["result"]["labels"]], a, pos=mini2, r=24, labels=False)
        fr.text(tr(L(f"字符串比较：cut {LEG['result']['cut']}", f"string compare: cut {LEG['result']['cut']}")), 620, 960, 24, ROSE, a, anchor="c")
        fr.text(tr(L(f"正确比较：cut {RUN['result']['cut']}", f"correct compare: cut {RUN['result']['cut']}")), 1300, 960, 24, TEAL, a, anchor="c")


def p_fix(fr, c):
    a0 = c.p(0, 1.0)
    panel(fr, 300, 240, 1320, 300, a0, L("修正：逐个字段比较", "THE FIX: COMPARE FIELD BY FIELD"))
    fr.text("(−5, A, B)", 520, 380, 40, TEAL, a0, role="mono", anchor="c")
    fr.text("<", W / 2 - 40, 380, 40, GOLD, a0, role="serif", anchor="c")
    fr.text("(−1, A, C)", 1240, 380, 40, MUTED, a0, role="mono", anchor="c")
    fr.text(tr(L("数字按数值比：−5 < −1，亲和度 5 胜出", "numbers compare as numbers: −5 < −1, so affinity 5 wins")), W / 2 - 40, 470, 24, IVORY, a0, anchor="c")
    if c.on(1):
        a = c.p(1)
        items = [("10  >  2", L("多位数", "multi-digit")), ("2.5  >  2", L("小数", "decimals"))]
        for i, (s, lab) in enumerate(items):
            x = 520 + i * 720
            panel(fr, x - 200, 600, 400, 170, a * clamp(c.since(1) * 1.5 - i * 0.5), accent=TEAL)
            fr.text(s, x, 690, 38, TEAL, a * clamp(c.since(1) * 1.5 - i * 0.5), role="mono", anchor="c")
            fr.text(tr(lab), x, 740, 22, MUTED, a * clamp(c.since(1) * 1.5 - i * 0.5), anchor="c")
        fr.text(tr(L("本课程的回归测试", "this course's regression tests")), W / 2 - 40, 840, 24, GOLD, a, anchor="c")


def p_rooms(fr, c):
    ev = CAP2["events"]
    st = ev[1]["after"] if c.T < FILL3[min(2, len(FILL3) - 1)] else ev[2]["after"]
    friends(fr, 1.0, clusters=st, labels=False)
    if c.on(0):
        for lab, members, x in (("AB", "AB", 1200), ("DE", "DE", 1500)):
            on = lab in [s["label"] for s in st]
            a = c.p(0) * (1.0 if on else 0.35)
            fr.rect(x - 120, 260, 240, 170, fill=PANEL_BG, stroke=FHUE[lab] if on else FAINT, width=1.4, alpha=0.95 * a, r=10, screen=True)
            fr.text(tr(L("双人房", "twin room")), x, 300, 20, MUTED, a, anchor="c")
            fr.text(" · ".join(FR[m] for m in members) if on else "—", x, 370, 26, FHUE[lab] if on else MUTED, a, anchor="c", role="serif")
    if c.on(1):
        a = c.p(1)
        for i, (lab, x) in enumerate((("Ada · Ben + Cai", 1200), ("Cai + Dev · Eva", 1500))):
            fr.text(lab, x, 520, 22, ROSE, a, anchor="c", role="serif")
            fr.text(tr(L("3 人 > 2 张床", "3 people > 2 beds")), x, 560, 22, ROSE, a, anchor="c")


def p_stop(fr, c):
    friends(fr, 1.0, clusters=CAP2["result"]["clusters"] and [{"label": l, "members": list(l)} for l in CAP2["result"]["labels"]], labels=False)
    panel(fr, 1100, 280, 600, 300, c.p(0), L("酒店的结果", "AT THE HOTEL"))
    fr.text(tr(L("三间房", "three rooms")), 1140, 380, 28, IVORY, c.p(0))
    fr.text("Ada·Ben | Cai | Dev·Eva", 1660, 380, 24, GOLD, c.p(0), role="serif", anchor="r")
    fr.text(tr(L("每间都没超员", "no room over capacity")), 1140, 440, 24, TEAL, c.p(0))
    fr.text("✓", 1660, 440, 26, TEAL, c.p(0), anchor="r")
    fr.text(tr(L("凑够两间房", "down to two rooms")), 1140, 500, 24, ROSE, c.p(0))
    fr.text("×", 1660, 500, 26, ROSE, c.p(0), anchor="r")


CIRC_POS = fit({k: tuple(v) for k, v in CIRCUIT["positions"].items()}, (360, 220, 1560, 780))
CIRC = REF.greedy_pair_merge(CIRCUIT["nodes"], [tuple(e) for e in CIRCUIT["edges"]], 3)
assert CIRC["cutsize"] == 2 and CIRC["target_reached"] and len(CIRC["log"]) == 22
CIRC_STEPS = [s["clusters"] for s in CIRC["log"]]
CIRC_HUES = [TEAL, BLUE, AMBER]


def circuit(fr, alpha, step, hull_alpha=1.0):
    """The fictional 24-cell schematic, coloured by the greedy-merge clusters after `step` merges."""
    groups = CIRC_STEPS[min(step, len(CIRC_STEPS) - 1)]
    final = CIRC["parts"]
    hue_of = {}
    for g in groups:
        if len(g) >= 6:  # names are concatenated: each cell id is 3 characters
            cells = [g[i:i + 3] for i in range(0, len(g), 3)]
            fi = next(i for i, f in enumerate(final) if cells[0] in f)
            for cl in cells:
                hue_of[cl] = CIRC_HUES[fi]
    for u, v, w in CIRCUIT["edges"]:
        inside = u in hue_of and v in hue_of and hue_of[u] == hue_of[v] and any(u in g and v in g for g in groups)
        fr.line(CIRC_POS[u], CIRC_POS[v], hue_of[u] if inside else "#6f9da0", 0.8 + w * 0.4, (0.75 if inside else 0.22) * alpha)
    for n, (x, y) in CIRC_POS.items():
        col = hue_of.get(n, NEUTRAL)
        fr.rect(x - 25, y - 13, 50, 26, fill=NODE_BG, stroke=col, width=1.8, alpha=alpha, r=3, glow=0.4 * alpha if n in hue_of else 0)


def p_chip(fr, c):
    if c.T < FILL4[0]:
        step = 0
    else:
        step = int(clamp((c.T - FILL4[0]) / 5.0) * (len(CIRC_STEPS) - 1))
    circuit(fr, c.p(0, 0.8), step)


def p_outro(fr, c):
    friends(fr, c.p(0, 1.2) * (1 - 0.6 * c.p(2)), clusters=STATES[3])
    if c.on(1):
        fr.text(tr(L("每一步：眼前最好的一对", "each step: the best pair in sight")), 1380, 420, 30, TEAL, c.p(1), anchor="c", role="serif")
        fr.text(tr(L("合并了，就不再拆开", "once merged, never split")), 1380, 480, 30, TEAL, c.p(1, delay=0.6), anchor="c", role="serif")
    if c.on(3):
        a = c.p(3, 1.4)
        fr.text(tr(L("如果早早选错一步呢？", "What if an early step is wrong?")), 1380, 640, 48, GOLD, a, role="serif", anchor="c", glow=0.3 * a)


def p_end(fr, c):
    if not c.on(1):
        a = c.p(0, 1.0)
        state(fr, STATES[0], a)
        fr.text(tr(L("改 K · 改容量 · 改边权 · 看轨迹怎么变", "change K · change capacity · change a weight · watch the path move")), 1380, 500, 26, GOLD, a, anchor="c")
    else:
        credits(fr, c, [(L("合并，再合并", "Merge, and Merge Again"), GOLD, 44),
                        (L("Learning Clustering · Module 03 · 贪心成对合并", "Learning Clustering · Module 03 · Greedy pair merge"), IVORY, 24),
                        (L("原作 thy031（Issue #2）· AB–C = 1 + 4 = 5 的收缩示意来自原作", "Original work by thy031 (Issue #2) · the AB–C = 1 + 4 = 5 contraction comes from it"), MUTED, 20),
                        (L("所有轨迹由本课程引擎 site/engines/merge.js 计算", "Every trajectory is computed by this course's engine, site/engines/merge.js"), MUTED, 20),
                        (MUSIC_LINE, MUTED, 18)], k=1)


STORY = Film(
    "story", "popular", L("合并，再合并", "Merge, and Merge Again"), None, BRAND, poster_at=36.5, music=TRACK, seed=3,
    why=L("从窗上的雨滴讲起：最近的两滴总是先合在一起。再看五个朋友分两辆车：每次把最投机的两组合并；一个把 10 排在 2 前面的文件夹，讲清原网页的比较器错误；酒店只有双人房，讲清为什么不能硬凑。",
          "It opens with rain on a window, where the nearest two drops always fuse first. Then five friends split into two cars by merging the best-matched groups; a folder that sorts 10 before 2 explains the original page's comparator bug; twin rooms at the hotel show why you never force a merge."),
    scenes=[
        Scene("p-drops", droplets, [Beat(L("雨落在窗上。", "Rain on a window."), 4.6),
                                    Beat(L("挨得最近的两滴，先连成一滴。", "The two nearest drops fuse first."), 4.6)],
              chapter=L("序 · 雨滴", "PROLOGUE · RAINDROPS"), until=S["intro_end"]),
        Scene("p-drops2", droplets, [Beat(L("然后再找最近的一对。合并，从不拆开。", "Then the next nearest pair. Merged, never split again."), 5.6)],
              until=S["groove"]),
        Scene("p-rule", p_rule, [Beat(L("五个朋友分两辆车，也可以这样分。", "Five friends splitting into two cars can do the same."), 4.4),
                                 Beat(L("一开始每人自成一组：拆散的交情共 18。", "At first everyone is a group of one: 18 in friendships split."), 4.8),
                                 Beat(L("每次合并最投机的两组，直到只剩两组。", "Merge the two best-matched groups, until two remain."), 4.6)],
              chapter=L("序 · 分车", "PROLOGUE · TWO CARS"), until=S["roll"]),
        Scene("p-title", p_title, [Beat(None, 4.5)], fade=False, until=37.0),
        Scene("p-step1", p_step1, [Beat(L("最投机的有两对：Ada–Ben 和 Dev–Eva，都是 5。", "Two pairs get along best: Ada–Ben and Dev–Eva, both 5."), 5.6),
                                   Beat(L("平票就按名字：A 在 D 前，Ada 和 Ben 先上车。", "A tie goes by name: A comes before D, so Ada and Ben go first."), 6.0)],
              chapter=L("一 · 平票", "I · A TIE"), until=S["fill1_end"]),
        Scene("p-step2", p_step2, [Beat(L("Ada 和 Ben 成了一组。Cai 的两根线合起来：1 + 4 = 5。", "Ada and Ben are one group now. Cai's two lines add up: 1 + 4 = 5."), 6.6),
                                   Beat(L("又和 Dev–Eva 平票；按名字，Cai 加入。", "Another tie with Dev–Eva; by name, Cai joins them."), 5.0)],
              chapter=L("二 · 两根线算一根", "II · TWO LINES COUNT AS ONE"), until=S["fill2"]),
        Scene("p-step3", p_step3, [Beat(L("最后 Dev 和 Eva 一车。只剩两组，停。", "Last, Dev and Eva share a car. Two groups left: stop."), 4.8)],
              until=73.0),
        Scene("p-files", p_files, [Beat(L("你见过这样的文件夹吗？", "Ever seen a folder like this?"), 2.6),
                                   Beat(L("10 排在 2 前面。", "10 sorts before 2."), 2.4)],
              chapter=L("三 · 排序的陷阱", "III · A SORTING TRAP"), until=S["phrase"]),
        Scene("p-flip", p_flip, [Beat(L("按数值，2 在前；按文字，10 在前。", "As numbers, 2 comes first; as text, 10 does."), 3.4),
                                 Beat(L("文字是一个字符一个字符地比。", "Text compares one character at a time."), 3.4)],
              until=89.0),
        Scene("p-bug", p_bug, [Beat(L("原网页比较候选，也是当成文字来比。", "The original page compared its candidates the same way: as text."), 4.0),
                               Beat(L("“-1” 排在 “-5” 前：亲和度 1 成了最好的一对。", "“-1” sorts before “-5”: affinity 1 looked like the best pair."), 4.4),
                               Beat(L("被切断的交情从 3 变成了 9。", "The split friendship went from 3 to 9."), 3.4)],
              until=104.0),
        Scene("p-fix", p_fix, [Beat(L("修正：逐个字段比，数字按数值比。", "The fix: compare field by field, numbers as numbers."), 4.4),
                               Beat(L("本课程还专门测了 10 对 2、2.5 对 2，防止碰巧正确。", "This course also tests 10 against 2 and 2.5 against 2, so it is not right by luck."), 6.0)],
              until=S["fill3"]),
        Scene("p-rooms", p_rooms, [Beat(L("到了酒店，每间房只有两张床。", "At the hotel, every room has two beds."), 4.0),
                                   Beat(L("Cai 想加入哪一间，都是三个人。", "Whichever room Cai joins, it holds three."), 4.0)],
              chapter=L("四 · 双人房", "IV · TWIN ROOMS"), until=127.6),
        Scene("p-stop", p_stop, [Beat(L("所以停在三间：不硬塞，也不谎称凑够了。", "So it stops at three: no squeezing, no pretending it made two."), 5.4)],
              until=S["fill4"]),
        Scene("p-chip", p_chip, [Beat(L("芯片设计里，同样的合并把成千上万个单元先粗化成几簇。", "In chip design, the same merging first coarsens thousands of cells into a few clusters."), 6.4)],
              until=141.5),
        Scene("p-outro", p_outro, [Beat(L("这一路，每一步都只看眼前。", "All the way, each step only looked at what was in front of it."), 6.0),
                                   Beat(L("选最好的一对，合并，不再回头。", "Pick the best pair, merge, never look back."), 7.0),
                                   Beat(L("这一次，结果恰好最好。", "This time, the result happened to be the best."), 6.0),
                                   Beat(L("如果早早选错一步呢？下一章见。", "What if an early step is wrong? See the next module."), 8.0)],
              chapter=L("尾声", "CODA"), until=S["quiet"]),
        Scene("p-end", p_end, [Beat(L("下面的实验里，改 K、改容量，看轨迹怎么变。", "In the lab below, change K or the capacity and watch the path change."), 6.0),
                               Beat(None, 10.0)], until=S["end"]),
    ])


# ====================================================================== concise film
def k_title(fr, c):
    title_card(fr, L("贪心成对合并", "Greedy Pair Merge"), L("GREEDY PAIR MERGE  ·  精讲", "THE ESSENTIALS"), c.p(0, 1.2), kicker="MODULE 03")


def k_problem(fr, c):
    state(fr, STATES[0], c.p(0, 1.0))
    a = c.p(1)
    panel(fr, 1080, 240, 660, 470, a, L("问题", "THE PROBLEM"))
    y = 340
    for i, (s, col) in enumerate([(L("输入：带权图、目标簇数 K、可选容量 C", "Input: a weighted graph, a target K, an optional capacity C"), IVORY),
                                  (L("每一步：合并亲和度最大的合法一对", "Each step: merge the legal pair with the highest affinity"), IVORY),
                                  (L("亲和度 = 两簇之间所有边权之和", "Affinity = the total weight between the two clusters"), TEAL),
                                  (L("停止：达到 K，或没有合法的正亲和度对", "Stop: K is reached, or no positive legal pair remains"), GOLD)]):
        b = [1, 1, 2, 3][i]
        if c.on(b):
            h = fr.paragraph(s, 1110, y, 26, 600, col, c.p(b, delay=0.3 * (i == 1)))
            y += h + 18


def k_step(fr, c, i):
    ev = EV[i + 1]
    d = ev["decision"]
    before, after = ev["before"], ev["after"]
    merged = c.on(2)
    clusters = after if merged else before
    focus = [m for cl in before if cl["label"] in (d["a"], d["b"]) for m in cl["members"]] if c.on(1) and not merged else []
    hl = {key(p["u"], p["v"]) for cnd in ev["candidates"] if (cnd["a"], cnd["b"]) == (d["a"], d["b"]) for p in cnd["parts"]} if c.on(1) and not merged else set()
    state(fr, clusters, 1.0, focus=focus, hl=hl)
    if i == 1 and c.on(1) and not merged:
        contraction(fr, c.span(1, 2), 1.0, P5)
    cand_rows(fr, 1060, 240, ev["candidates"][:4], c.p(0), L(f"第 {i + 1} 步 · 候选", f"STEP {i + 1} · CANDIDATES"), chosen=0 if c.on(1) else None, w=600, lh=50)
    m = ev["metrics"]
    k = c.p(2)
    fr.text("cut", 1100, 680, 28, MUTED, 1.0)
    fr.text(f"{m['cutBefore']}  →  {m['cut']}" if merged else f"{m['cutBefore']}", 1620, 684, 40, TEAL if merged else ROSE, 1.0, role="mono", anchor="r", glow=0.3 * k)
    if merged:
        fr.text(tr(L(f"下降 {m['drop']} = 这次的亲和度", f"down {m['drop']} = this merge's affinity")), 1620, 730, 22, TEAL, k, anchor="r")


def k_step1(fr, c):
    k_step(fr, c, 0)


def k_step2(fr, c):
    k_step(fr, c, 1)


def k_step3(fr, c):
    k_step(fr, c, 2)
    if c.on(3):
        a = c.p(3)
        fr.text("18 → 13 → 8 → 3", 1360, 820, 34, GOLD, a, role="mono", anchor="c", glow=0.3 * a)


def k_bug(fr, c):
    a0 = c.p(0)
    panel(fr, 260, 230, 1400, 250, a0, L("原网页：if (!best || cand < best)", "THE ORIGINAL PAGE: if (!best || cand < best)"))
    fr.text("[-5, \"A\", \"B\"]  →  \"-5,A,B\"", 320, 340, 30, IVORY, a0, role="mono")
    fr.text("[-1, \"A\", \"C\"]  →  \"-1,A,C\"", 320, 410, 30, IVORY, a0, role="mono")
    if c.on(1):
        fr.text(tr(L("“1” < “5”：A–C 被当成更好", "“1” < “5”: A–C looks better")), 1600, 380, 26, ROSE, c.p(1), anchor="r")
    if c.on(2):
        a = c.p(2)
        rows = [[L("配置", "Setting"), L("字符串比较", "String compare"), L("正确", "Correct")],
                ["K = 2", "9", "3"], ["K = 3", "16", "8"], [L("容量 2", "capacity 2"), "12", "8"], [L("容量 3", "capacity 3"), "16", "3"]]
        table(fr, 560, 540, [300, 300, 200], [[tr(x) for x in r] for r in rows], a, size=26, lh=56, colors={1: ROSE, 2: TEAL})
    if c.on(3):
        fr.text(tr(L("修正：逐字段比较，数字按数值", "fix: compare field by field, numbers as numbers")), W / 2, 900, 26, TEAL, c.p(3), anchor="c")


def k_capacity(fr, c):
    ev = CAP2["events"]
    st = ev[2]["after"] if c.on(1) else ev[1]["after"]
    state(fr, st, 1.0)
    cand_rows(fr, 1060, 240, CAP2_STOP["candidates"] if c.on(2) else ev[2]["candidates"][:2], c.p(0),
              L("容量 C = 2 · 候选", "CAPACITY C = 2 · CANDIDATES"), chosen=None if c.on(2) else 1, w=600, lh=50)
    if c.on(2):
        a = c.p(2)
        fr.text(tr(L("AB | C | DE · 3 簇 · cut 8", "AB | C | DE · 3 clusters · cut 8")), 1360, 560, 28, IVORY, a, anchor="c", role="serif")
        fr.text(tr(L("合法 ✓   达到 K ×   停止原因：capacity-blocked", "legal ✓   K reached ×   stop: capacity-blocked")), 1360, 620, 22, GOLD, a, anchor="c")


def k_take(fr, c):
    items = [(L("每次合并亲和度最大的合法一对；亲和度 = 簇间边权和", "Merge the legal pair with the highest affinity: the total weight between clusters"), TEAL),
             (L("平票看成员名字；比较要逐字段，不能转成字符串", "Ties go by member names; compare field by field, never as strings"), GOLD),
             (L("每次合并，cut 恰好下降这次的亲和度", "Each merge lowers the cut by exactly its affinity"), TEAL),
             (L("没有合法的一对就停：如实报告，不强行凑 K", "No legal pair? Stop and say so; never force K"), ROSE)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 260 + i * 120
            fr.rect(220, y, 1480, 92, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 58, 28, col, a, role="mono")
            fr.text(s, 360, y + 58, 30, IVORY, a)


CONCISE = Film(
    "concise", "concise", L("精讲：合并的规则", "The essentials"), None, BRAND, poster_at=40.0, music="score:steady", seed=23,
    why=L("只讲必须掌握的：规则与停止条件、平票、收缩时平行边相加、完整轨迹、比较器错误和容量。",
          "Only what you must know: the rule and when to stop, ties, adding parallel wires on contraction, the full path, the comparator bug and capacity."),
    scenes=[
        Scene("k00-title", k_title, [Beat(None, 3.0)]),
        Scene("k01-problem", k_problem, [Beat(L("从单点出发：每个节点自成一簇，cut 等于全部边权 18。", "Start from single nodes: each is its own cluster, and the cut is all 18 of the weight."), 4.0),
                                         Beat(L("每一步，合并亲和度最大的合法一对。", "Each step merges the legal pair with the highest affinity."), 3.0),
                                         Beat(L("亲和度是两簇之间所有边权之和。", "Affinity is the total weight between the two clusters."), 2.8),
                                         Beat(L("达到 K，或者没有合法的一对，就停。", "Stop when K is reached, or no legal pair remains."), 3.2)],
              chapter=L("问题", "THE PROBLEM")),
        Scene("k02-step1", k_step1, [Beat(L("第一步：A–B 和 D–E 都是 5。", "Step one: A–B and D–E both score 5."), 2.8),
                                     Beat(L("平票按名字：A 在 D 前，选 A–B。", "A tie goes by name: A before D, so A–B."), 3.2),
                                     Beat(L("cut 从 18 降到 13。", "The cut drops from 18 to 13."), 2.6)],
              chapter=L("平票", "TIES")),
        Scene("k03-step2", k_step2, [Beat(L("A、B 收缩成一簇。", "A and B contract into one cluster."), 2.4),
                                     Beat(L("AB 和 C 之间有两根线：1 + 4 = 5，又和 D–E 平票；按成员 [A, B] < [D]，选 AB–C。", "AB and C share two wires, 1 + 4 = 5, tying D–E again; by members [A, B] < [D], so AB–C."), 6.4),
                                     Beat(L("cut 从 13 降到 8。", "The cut drops from 13 to 8."), 2.6)],
              chapter=L("收缩", "CONTRACTION")),
        Scene("k04-step3", k_step3, [Beat(L("第三步：D–E。", "Step three: D–E."), 2.2),
                                     Beat(L("合并它们。", "Merge them."), 1.8),
                                     Beat(L("剩两簇，停：ABC | DE，cut 3。", "Two clusters left, stop: ABC | DE, cut 3."), 3.0),
                                     Beat(L("每次合并，cut 恰好下降这次的亲和度。", "Every merge lowers the cut by exactly its affinity."), 3.4)],
              chapter=L("轨迹", "THE PATH")),
        Scene("k05-bug", k_bug, [Beat(L("原网页用小于号直接比较数组。", "The original page compared arrays with a plain less-than."), 3.0),
                                 Beat(L("JavaScript 先把数组转成字符串：“-1” 排在 “-5” 前。", "JavaScript turns the arrays into strings first: “-1” sorts before “-5”."), 4.4),
                                 Beat(L("四个配置全部算错。", "All four settings came out wrong."), 2.6),
                                 Beat(L("修正：逐字段比较，数字按数值。", "The fix: compare field by field, numbers as numbers."), 3.0)],
              chapter=L("比较器错误", "THE COMPARATOR BUG")),
        Scene("k06-capacity", k_capacity, [Beat(L("容量 2：AB 加 C 是 3 个，被阻止，转而合并 D–E。", "Capacity 2: AB plus C is 3, blocked, so D–E merges instead."), 4.2),
                                           Beat(L("之后两个候选都超容量。", "After that, both candidates exceed the capacity."), 2.8),
                                           Beat(L("停在 3 簇，cut 8：合法，但没有达到 K。", "It stops at 3 clusters, cut 8: legal, but K is not reached."), 3.6)],
              chapter=L("容量", "CAPACITY")),
        Scene("k07-take", k_take, [Beat(L("记住四点。", "Four things to keep."), 1.4),
                                   Beat(L("簇间边权和最大的合法一对先合并；", "Merge the legal pair with the most weight between them;"), 2.6),
                                   Beat(L("平票看名字，逐字段比较；", "ties by name, field by field;"), 2.2),
                                   Beat(L("cut 每步下降该次亲和度；没有合法的一对就停。下面的实验里试一试。", "the cut drops by each affinity; with no legal pair, stop. Try it in the lab below."), 4.8)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])


# ====================================================================== advanced film
def grid_graph(n):
    nodes = [f"{chr(65 + r)}{c_}" for r in range(n) for c_ in range(n)]
    edges = []
    for r in range(n):
        for c_ in range(n):
            u = f"{chr(65 + r)}{c_}"
            if c_ + 1 < n:
                edges.append((u, f"{chr(65 + r)}{c_ + 1}", 1 + (r * 7 + c_ * 3) % 5))
            if r + 1 < n:
                edges.append((u, f"{chr(66 + r)}{c_}", 1 + (r * 5 + c_ * 11) % 5))
    return nodes, edges


def merge_cost(nodes, edges, k):
    """Count candidate pairs examined: naive (all positive cluster pairs, every step) vs local (pairs touching the new cluster)."""
    parts = sorted([[n] for n in nodes])
    weights = REF._weights(edges)
    naive = local = 0
    while len(parts) > k:
        cands = REF.candidates(parts, weights)
        if not cands:
            break
        naive += len(cands)
        best = min(cands, key=REF.selection_key)
        merged = sorted(best["a"] + best["b"])
        parts = sorted([p for p in parts if tuple(p) not in (best["a"], best["b"])] + [merged])
        local += sum(1 for c_ in REF.candidates(parts, weights) if tuple(merged) in (c_["a"], c_["b"]))
    return naive, local


GRID_N = 12
GRID_NAIVE, GRID_LOCAL = merge_cost(*grid_graph(GRID_N), 2)
GRID_RATIO = round(GRID_NAIVE / GRID_LOCAL)
assert GRID_RATIO >= 5, (GRID_NAIVE, GRID_LOCAL)

# sum affinity snowballs: on the 24-cell circuit, the first cluster swallows its whole block before any other cluster forms
CIRC_FIRST7 = [s["pair"] for s in CIRC["log"][1:8]]
assert all("N00" in p.split("-")[0] or p.startswith("N00") for p in CIRC_FIRST7)
SNOW = {"nodes": ["A", "B", "C", "D", "E", "F"], "edges": [("A", "B", 3), ("B", "C", 3), ("A", "C", 3), ("A", "D", 1), ("B", "D", 1), ("C", "D", 1), ("E", "F", 2)]}
_snow = REF.greedy_pair_merge(SNOW["nodes"], SNOW["edges"], 3)
assert _snow["log"][3]["pair"] == "ABC-D" and _snow["log"][3]["weight"] == 3, _snow["log"]
SNOW_POS = {"A": (420, 360), "B": (640, 360), "C": (530, 540), "D": (760, 640), "E": (980, 360), "F": (980, 640)}

SUB = T4["suboptimal"]
SUB_G = T4["graphs"]["suboptimal"]
assert SUB["run"]["result"]["cut"] == 18 and SUB["oracle"]["bestCutAtK"]["cut"] == 11 and SUB["run"]["result"]["labels"] == ["AB", "CD"]


def a_title(fr, c):
    title_card(fr, L("贪心成对合并", "Greedy Pair Merge"), L("进阶：贪心的性质与代价", "IN DEPTH: WHAT GREEDY GUARANTEES, AND WHAT IT COSTS"), c.p(0, 1.2), kicker="MODULE 03")


def a_drop(fr, c):
    i = 0 if not c.on(1) else 1
    ev = EV[2]
    state(fr, ev["before"] if not c.on(2) else ev["after"], 1.0, hl={key("A", "C"), key("B", "C")} if c.on(1) and not c.on(2) else set())
    panel(fr, 1060, 240, 640, 360, c.p(0), L("为什么 cut 恰好下降亲和度", "WHY THE CUT DROPS BY EXACTLY THE AFFINITY"))
    fr.paragraph(L("cut = 所有跨簇边的权重之和。", "cut = the weight of every wire between clusters."), 1090, 330, 26, 580, IVORY, c.p(0))
    if c.on(1):
        fr.paragraph(L("合并 P 和 Q：只有 P–Q 之间的边从“跨簇”变成“簇内”。", "Merge P and Q: only the wires between P and Q go from crossing to inside."), 1090, 420, 26, 580, GOLD, c.p(1))
    if c.on(2):
        fr.paragraph(L("其他边的两端仍在不同簇：不变。所以 cut 下降 = aff(P, Q)。", "Every other wire still crosses: unchanged. So the drop = aff(P, Q)."), 1090, 520, 26, 580, TEAL, c.p(2))
    if c.on(3):
        a = c.p(3)
        fr.paragraph(L("于是“选亲和度最大的一对”= 每一步让 cut 下降得最多：最陡下降，而不是全局最优。",
                       "So “take the highest affinity” = make the cut fall the most at each step: steepest descent, not a global optimum."),
                     1060, 680, 26, 680, IVORY, a)


def a_snow(fr, c):
    if not c.on(2):
        pos = SNOW_POS
        clusters = [{"label": "ABC", "members": ["A", "B", "C"]}, {"label": "D", "members": ["D"]}, {"label": "E", "members": ["E"]}, {"label": "F", "members": ["F"]}]
        hull(fr, [pos[m] for m in "ABC"], TEAL, c.p(0), R=70, label="ABC", label_at=(530, 250))
        graph(fr, pos, SNOW["edges"], {"A": TEAL, "B": TEAL, "C": TEAL, "D": NEUTRAL, "E": NEUTRAL, "F": NEUTRAL}, c.p(0), r=36,
              hl_edges={key("A", "D"), key("B", "D"), key("C", "D")} if c.on(1) else set())
        panel(fr, 1180, 280, 560, 300, c.p(1), L("下一步比谁", "WHO MERGES NEXT"))
        if c.on(1):
            a = c.p(1)
            fr.text(L("和（本模块）", "sum (this module)"), 1220, 380, 24, MUTED, a)
            fr.text("ABC–D = 1+1+1 = 3", 1700, 380, 24, GOLD, a, role="mono", anchor="r")
            fr.text("E–F = 2", 1700, 430, 24, IVORY, a, role="mono", anchor="r")
            fr.text(L("平均（除以 |P|·|Q|）", "average (÷ |P|·|Q|)"), 1220, 500, 24, MUTED, a * c.p(1, delay=1.6))
            fr.text("3 / 3 = 1  <  2", 1700, 540, 24, TEAL, a * c.p(1, delay=1.6), role="mono", anchor="r")
    else:
        step = int(clamp(c.span(2, 4) * 1.05) * 7)
        circuit(fr, 1.0, step)
        fr.text(tr(L(f"前 {step} 步：同一簇一个接一个吞掉邻居", f"first {step} steps: one cluster swallows its neighbours one by one")), W / 2, 880, 26, GOLD, c.p(2), anchor="c")


def a_compare(fr, c):
    panel(fr, 260, 230, 1400, 230, c.p(0), L("元组：逐字段，按类型比", "TUPLES: FIELD BY FIELD, BY TYPE"))
    fr.text("(−5, ('A',), ('B',))  <  (−1, ('A',), ('C',))", 320, 330, 30, TEAL, c.p(0), role="mono")
    fr.text(tr(L("第一字段 −5 < −1 就定了；后面的字段只在平票时才看", "−5 < −1 settles it; later fields only break ties")), 320, 400, 24, MUTED, c.p(0))
    if c.on(1):
        a = c.p(1)
        panel(fr, 260, 500, 1400, 230, a, L("字符串：逐字符", "STRINGS: CHARACTER BY CHARACTER"))
        fr.text("\"-10,A,B\"  <  \"-9,A,C\"     \"-1,A,C\"  <  \"-5,A,B\"", 320, 600, 30, ROSE, a, role="mono")
        fr.text(tr(L("第二个字符 “1” 就分出了胜负：10 和 9 谁大，根本没比", "the second character “1” decides: whether 10 beats 9 is never asked")), 320, 670, 24, MUTED, a)
    if c.on(2):
        a = c.p(2)
        fr.text("[10, 9, 2].sort()  →  [10, 2, 9]", W / 2, 820, 34, ROSE, a, role="mono", anchor="c")
        fr.text(tr(L("JavaScript 默认的 sort() 也按字符串排", "JavaScript's default sort() sorts as strings too")), W / 2, 870, 24, MUTED, a, anchor="c")


def a_states(fr, c):
    rows = [[L("运行", "Run"), L("簇", "Clusters"), "cut", L("合法", "Legal"), L("达到 K", "K reached"), L("停止原因", "Stop reason")],
            ["K=2", "ABC | DE", "3", "✓", "✓", "target-reached"],
            [L("K=2, 容量 2", "K=2, cap 2"), "AB | C | DE", "8", "✓", "×", "capacity-blocked"],
            [L("K=1, 不连通", "K=1, disconnected"), "AB | C | D", "0", "✓", "×", "no-positive-affinity"]]
    shown = [0, c.p(0), c.p(1), c.p(2)]
    for i, r in enumerate(rows):
        a = 1.0 * c.p(0) if i == 0 else shown[i]
        if a <= 0:
            continue
        y = 300 + i * 90
        xs = [200, 470, 810, 960, 1110, 1290]
        for j, cell in enumerate(r):
            col = MUTED if i == 0 else (ROSE if cell == "×" else TEAL if cell == "✓" else (GOLD if j == 5 else IVORY))
            fr.text(tr(cell) if isinstance(cell, L) or isinstance(cell, tuple) else cell, xs[j], y, 24 if i == 0 else 28, col, a, role="mono" if j in (2, 5) else "sans")
    if c.on(3):
        fr.paragraph(L("三件事分开报告：合法不等于达到 K。没有合法的正亲和度对时停下，不为凑 K 强行合并。",
                       "Report the three separately: legal is not the same as reaching K. With no legal positive pair, stop; never force K."),
                     200, 720, 26, 1500, GOLD, c.p(3))


def a_noback(fr, c):
    pos = fit({k: tuple(v) for k, v in SUB_G["positions"].items()}, (300, 300, 900, 700))
    edges = [tuple(e) for e in SUB_G["edges"]]
    greedy = c.k < 2
    groups = [["A", "B"], ["C", "D"]] if greedy else [["A", "C"], ["B", "D"]]
    for g, col in zip(groups, (TEAL, BLUE)):
        hull(fr, [pos[m] for m in g], col, c.p(0), R=70)
    where = {m: i for i, g in enumerate(groups) for m in g}
    cut = {key(u, v) for u, v, _ in edges if where[u] != where[v]}
    graph(fr, pos, edges, {n: (TEAL if where[n] == 0 else BLUE) for n in pos}, c.p(0), cut=cut, r=38)
    panel(fr, 1060, 300, 620, 300, c.p(0), L("容量 2，K = 2（Module 04 的例子）", "CAPACITY 2, K = 2 (A MODULE 04 EXAMPLE)"))
    fr.text(L("贪心：先合 A–B（10）", "greedy: A–B (10) first"), 1100, 400, 26, TEAL if greedy else MUTED, c.p(0))
    fr.text("cut 18", 1640, 400, 28, ROSE, c.p(0), role="mono", anchor="r")
    if c.on(2):
        fr.text(L("另一种分法：AC | BD", "another split: AC | BD"), 1100, 470, 26, TEAL, c.p(2))
        fr.text("cut 11", 1640, 470, 28, TEAL, c.p(2), role="mono", anchor="r")
    if c.on(3):
        fr.paragraph(L("第一步最好的选择，让后面只剩差的选择；贪心不会回头拆开。", "The best first step leaves only bad choices later, and greedy never goes back to undo it."),
                     1060, 680, 26, 640, GOLD, c.p(3))


def a_cost(fr, c):
    panel(fr, 260, 260, 1400, 400, c.p(0), L(f"{GRID_N}×{GRID_N} 网格合并到 2 簇：一共检查了多少个候选", f"A {GRID_N}×{GRID_N} GRID MERGED TO 2: CANDIDATES EXAMINED"))
    fr.text(L("每一步重算所有簇对", "recompute every pair each step"), 320, 400, 28, MUTED, c.p(0))
    fr.text(f"{GRID_NAIVE:,}", 1600, 400, 34, ROSE, c.p(0), role="mono", anchor="r")
    if c.on(1):
        fr.text(L("只更新和新簇相邻的那几对", "update only the pairs that touch the new cluster"), 320, 490, 28, MUTED, c.p(1))
        fr.text(f"{GRID_LOCAL:,}", 1600, 490, 34, TEAL, c.p(1), role="mono", anchor="r")
        bar(fr, 320, 550, 1280, 14, 1.0, ROSE, c.p(1))
        bar(fr, 320, 590, 1280, 14, GRID_LOCAL / GRID_NAIVE, TEAL, c.p(1), glow=0.5)
    if c.on(2):
        fr.paragraph(L("其余簇对的亲和度根本没变：把它们放进优先队列，每步只取堆顶、只改受影响的几项。",
                       "Every other pair's affinity is unchanged: keep them in a priority queue, pop the top, and update only the few that changed."),
                     320, 720, 26, 1280, GOLD, c.p(2))


def a_summary(fr, c):
    items = [(L("cut 每步下降 = 这次的亲和度：贪心就是每步最陡下降", "Each drop in the cut equals the affinity: greedy is steepest descent"), TEAL),
             (L("用“和”做亲和度，大簇越滚越大", "With a sum as the affinity, big clusters snowball"), ROSE),
             (L("比较键逐字段、按类型；字符串比较只看字符", "Compare keys field by field, by type; strings only see characters"), GOLD),
             (L("合法、达到 K、停止原因：三件事分开报告", "Legal, K reached, stop reason: report all three"), GOLD),
             (L("不回撤：第一步最好，不等于结果最好", "No backtracking: the best first step is not the best result"), ROSE),
             (L("只更新受影响的簇对，代价大大降低", "Update only the affected pairs, and the cost falls sharply"), TEAL)]
    for i, (s, col) in enumerate(items):
        if c.on(i):
            a = c.p(i)
            y = 200 + i * 104
            fr.rect(220, y, 1480, 84, fill=PANEL_BG, stroke=FAINT, width=1.2, alpha=0.93 * a, r=8, screen=True)
            fr.text(f"0{i + 1}", 270, y + 54, 26, col, a, role="mono")
            fr.text(s, 350, y + 54, 30, IVORY, a)


ADVANCED = Film(
    "advanced", "advanced", L("进阶：贪心的性质与代价", "In depth: what greedy guarantees"), None, BRAND, poster_at=50.0, music="score:calm", seed=35,
    why=L("为什么 cut 恰好下降亲和度、“和”亲和度的滚雪球效应、元组与字符串比较、三个停止状态、不回撤的代价，以及局部更新省下多少计算。",
          "Why the cut drops by exactly the affinity, how a sum affinity snowballs, tuples versus strings, the three stop states, the price of never backtracking, and how much local updates save."),
    scenes=[
        Scene("a00-title", a_title, [Beat(None, 3.0)]),
        Scene("a01-drop", a_drop, [Beat(L("cut 是所有跨簇边的权重之和。", "The cut is the total weight of the wires between clusters."), 3.4),
                                   Beat(L("合并 P 和 Q，只有它们之间的边变成簇内边。", "Merge P and Q, and only the wires between them become inside wires."), 4.2),
                                   Beat(L("其他边不变：所以 cut 恰好下降 P、Q 的亲和度。", "Nothing else changes, so the cut drops by exactly the affinity of P and Q."), 4.4),
                                   Beat(L("选亲和度最大的一对，就是每一步让 cut 下降最多：最陡下降，不保证全局最优。", "Taking the highest affinity makes the cut fall the most at each step: steepest descent, with no global guarantee."), 6.4)],
              chapter=L("一 · cut 为什么这样降", "I · WHY THE CUT FALLS LIKE THAT")),
        Scene("a02-snow", a_snow, [Beat(L("亲和度用“和”，有一个副作用。", "Using a sum as the affinity has a side effect."), 3.0),
                                   Beat(L("ABC 和 D 有三根细线，加起来 3，胜过 E–F 的 2；按平均算，只有 1。", "ABC and D share three thin wires, 3 in all, beating E–F's 2; as an average it is only 1."), 6.4),
                                   Beat(L("在 24 个单元的电路上：", "On the 24-cell circuit:"), 2.4),
                                   Beat(L("前 7 步都在喂同一个簇，大簇越滚越大。", "the first 7 steps all feed the same cluster. Big clusters snowball."), 5.0)],
              chapter=L("二 · 滚雪球", "II · SNOWBALLING")),
        Scene("a03-compare", a_compare, [Beat(L("比较选择键：元组逐字段比，第一字段就定了胜负。", "Comparing selection keys: a tuple compares field by field, and the first field settles it."), 5.0),
                                         Beat(L("字符串只比字符：第二个字符“1”就决定了结果，10 和 9 谁大根本没比。", "A string only sees characters: the second character “1” decides, and 10 versus 9 is never asked."), 6.4),
                                         Beat(L("JavaScript 默认的 sort() 也是这样：10、9、2 排成 10、2、9。", "JavaScript's default sort() does the same: 10, 9, 2 becomes 10, 2, 9."), 5.4)],
              chapter=L("三 · 比较键", "III · COMPARING KEYS")),
        Scene("a04-states", a_states, [Beat(L("不限容量，K = 2：合法，也达到了 K。", "No capacity, K = 2: legal, and K is reached."), 3.6),
                                       Beat(L("容量 2：合法，但还有正亲和度对，全都超容量。", "Capacity 2: legal, but the positive pairs left are all over capacity."), 4.2),
                                       Beat(L("图不连通：剩下的簇之间根本没有边。", "A disconnected graph: no wire at all between the remaining clusters."), 3.8),
                                       Beat(L("三件事要分开报告，没有合法的一对就停。", "Report all three separately, and stop when no legal pair remains."), 4.2)],
              chapter=L("四 · 三种停止", "IV · THREE WAYS TO STOP")),
        Scene("a05-noback", a_noback, [Beat(L("贪心不回头。Module 04 有一个例子：容量 2，K = 2。", "Greedy never backtracks. Module 04 has an example: capacity 2, K = 2."), 4.4),
                                       Beat(L("先合 A–B，权重 10 最大；剩下的 C–D 只能凑一起，cut 18。", "A–B goes first, the largest at 10; C and D are left together, cut 18."), 5.0),
                                       Beat(L("而 AC | BD 的 cut 只有 11。", "Yet AC | BD has a cut of only 11."), 3.0),
                                       Beat(L("第一步最好，后面只剩差的选择。下一章专门讲这件事。", "The best first step left only bad choices. The next module is about exactly this."), 5.2)],
              chapter=L("五 · 不回撤", "V · NO BACKTRACKING")),
        Scene("a06-cost", a_cost, [Beat(L(f"代价：把 {GRID_N}×{GRID_N} 的网格合并到 2 簇。", f"Cost: merge a {GRID_N}×{GRID_N} grid down to 2 clusters."), 3.6),
                                   Beat(L(f"每步重算所有簇对，比只更新与新簇相邻的那几对，多了约 {GRID_RATIO} 倍。", f"Recomputing every pair each step costs about {GRID_RATIO} times as much as updating only the pairs next to the new cluster."), 6.4),
                                   Beat(L("因为别的簇对亲和度没变：用优先队列，只改受影响的几项。", "Because no other pair's affinity changed: use a priority queue and update only those few."), 5.6)],
              chapter=L("六 · 代价", "VI · COST")),
        Scene("a07-summary", a_summary, [Beat(L("六点小结。", "Six things to keep."), 1.6)] + [Beat(None, 2.6) for _ in range(5)]
              + [Beat(L("下一章：容量成为主角。", "Next: capacity takes centre stage."), 3.0)],
              chapter=L("小结", "SUMMARY"), tail=1.4),
    ])

FILMS = [STORY, CONCISE, ADVANCED]
ORDER = ["story", "concise", "advanced", "lab"]
