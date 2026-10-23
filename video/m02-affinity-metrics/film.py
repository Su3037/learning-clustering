"""Module 02 · 亲和度指标 —— 影片《谁和谁最亲近》. Numbers from site/data/m02-affinity-metrics/traces.json."""
import math
from render import Scene, Beat
from kit import (W, H, TEAL, GOLD, RED, BLUE, PURPLE, INK, MUTED, FAINT, PANEL2, GROUP, SERIF, MONO,
                 ease, clamp, lerp, lerp2, node, edge, panel, tag, table, code, formula, title_card, fit, load_trace, score_box)

ID, TITLE = "affinity", "谁和谁最亲近"
MODULE = "Module 02 · 亲和度指标"
MOOD, SEED = "calm", 2
WHY = "约 3 分半：先预测、再拆分数。B–D 的“无直接边也有分”与宽 net 稀释各留足停顿。"
T = load_trace("m02-affinity-metrics")
G = {k: tuple(v) for k, v in T["g01"]["positions"].items()}
E5 = [tuple(e) for e in T["g01"]["edges"]]
POS5 = fit(G, (230, 230, 900, 790))
PR = T["priority"]
PRPOS = {k: tuple(v) for k, v in PR["positions"].items()}
PREDGES = [tuple(e) for e in PR["edges"]]
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


def s_title(cv, c):
    title_card(cv, "谁和谁最亲近", "Affinity metrics · Module 02", c.p(0, 1.2))


def priority_graph(cv, box, states=None, rings=None, alpha=1.0, tags=None):
    pos = fit(PRPOS, box)
    for u, v, w in PREDGES:
        edge(cv, pos[u], pos[v], w, (states or {}).get(f"{u}|{v}", "normal"), alpha)
    for n, p in pos.items():
        node(cv, *p, n, TEAL if n in "PQR" else BLUE, 40, alpha, (rings or {}).get(n))
        if tags and tags.get(n):
            cv.text(p[0], p[1] + 84, tags[n], 26, GOLD, "bold", "center", alpha=alpha)
    return pos


def s_hook(cv, c):
    priority_graph(cv, (360, 260, 1560, 760), alpha=c.p(0, 1.0))
    if c.on(1):
        tag(cv, W / 2, 860, "先在心里选一对", GOLD, c.p(1))


def s_model(cv, c):
    # left: an ordinary edge between two cells; right: one net with five pins
    panel(cv, 140, 170, 760, 640, "普通的边：两端", c.p(0))
    node(cv, 330, 500, "A", TEAL, 44, c.p(0)); node(cv, 710, 500, "B", TEAL, 44, c.p(0))
    edge(cv, (330, 500), (710, 500), 5, "normal", c.p(0))
    panel(cv, 1020, 170, 760, 640, "一个 net：五个引脚", c.p(1))
    hub = (1400, 500)
    pins = {n: (1400 + 230 * math.cos(-math.pi / 2 + i * 2 * math.pi / 5), 500 + 210 * math.sin(-math.pi / 2 + i * 2 * math.pi / 5)) for i, n in enumerate("ABCDE")}
    a = c.p(1)
    cv.circle(*hub, 14, fill=GOLD, alpha=a)
    for n, p in pins.items():
        cv.line(hub[0], hub[1], p[0], p[1], GOLD, 4, a)
        node(cv, *p, n, TEAL, 38, a)
    if c.on(2):
        q = c.p(2, 1.2)
        names = list(pins)
        for i in range(5):
            for j in range(i + 1, 5):
                cv.line(*pins[names[i]], *pins[names[j]], "#8fb1e6", 2, 0.55 * q, dash=[8, 8])
        cv.text(1400, 780, "展开成 10 对“示意贡献”——不是 10 根新导线", 28, MUTED, "bold", "center", alpha=q)


def s_edge(cv, c):
    p = c.p(0)
    order = [(x["u"], x["v"], x["score"]) for x in EDGE_RANK]
    shown = min(6, int(c.since(0) / 0.6) + 1) if c.on(0) else 0
    hi = {f"{u}|{v}": "hl" for u, v, _ in order[:1]} if c.on(1) else {}
    g5(cv, hi, alpha=p)
    panel(cv, 1080, 170, 700, 640, "直接边权排名", p)
    rows = [["名次", "节点对", "分数"]] + [[str(i + 1), f"{u}–{v}", str(s)] for i, (u, v, s) in enumerate(order[:shown])]
    hl = {1: GOLD, 2: GOLD} if c.on(1) else {}
    if c.on(2):
        hl = {5: GOLD, 6: GOLD}
    table(cv, 1130, 270, [150, 260, 160], rows, 34, 74, hl)


def contribution_scene(cv, c, pair, via_label):
    u, v = pair
    s = SHARED[pair]
    st = {}
    if c.on(0) and s["parts"]["direct"]:
        st["|".join(sorted(pair))] = "hl"
    if c.on(1):
        for x in s["parts"]["via"]:
            st["|".join(sorted((u, x["x"])))] = "hl"; st["|".join(sorted((v, x["x"])))] = "hl"
    rings = {u: GOLD, v: GOLD}
    tags = {x["x"]: "共同邻居" for x in s["parts"]["via"]} if c.on(1) else None
    g5(cv, st, rings, tags=tags)
    if not s["parts"]["direct"] and c.on(0):
        a, b = POS5[u], POS5[v]
        cv.line(*a, *b, RED, 3, 0.8 * c.p(0), dash=[4, 12])
        mid = lerp2(a, b, 0.5)
        tag(cv, mid[0], mid[1] + 10, "没有导线", RED, c.p(0), 24)
    items = [("直接边 w(" + u + "," + v + ")", s["parts"]["direct"], TEAL, c.p(0, 0.6))]
    for x in s["parts"]["via"]:
        items.append((f"经 {x['x']}：min({x['wu']}, {x['wv']})", x["min"], GOLD, c.p(2, 0.8)))
    score_box(cv, 1080, 220, 700, items, s["score"] if c.on(3) else None, 1.0, f"{u}–{v} 的共同邻居分")


def s_ac(cv, c):
    contribution_scene(cv, c, ("A", "C"), "B")


def s_bd(cv, c):
    contribution_scene(cv, c, ("B", "D"), "C")
    if c.on(4):
        cv.paragraph(1100, 760, "图上的边一条没变；变的只是我们给这一对的分数。", 30, 660, MUTED, alpha=c.p(4))


def s_priority(cv, c):
    left = (170, 280, 860, 700)
    right = (1060, 280, 1750, 700)
    panel(cv, 130, 160, 800, 700, "按直接边权", c.p(0))
    panel(cv, 1010, 160, 800, 700, "按共同邻居", c.p(1))
    priority_graph(cv, left, {"X|Y": "hl"} if c.on(0) else None, {"X": GOLD, "Y": GOLD} if c.on(0) else None)
    pr = T["priorityShared"]
    st = {"P|Q": "hl", "P|R": "hl", "Q|R": "hl"} if c.on(2) else None
    pos = priority_graph(cv, right, st, {"P": GOLD, "Q": GOLD} if c.on(3) else None)
    if c.on(2):
        tag(cv, pos["R"][0], pos["R"][1] - 70, "经 R：min(4, 4) = 4", GOLD, c.p(2), 24)
    if c.on(0):
        tag(cv, 530, 820, "第一对：X–Y @ 5", BLUE, c.p(0))
    if c.on(3):
        tag(cv, 1410, 820, f"第一对：{pr[0]['u']}–{pr[0]['v']} @ {pr[0]['score']}", TEAL, c.p(3))


def netlist(cv, alpha=1.0, show_clique=0.0, pick=None):
    """Nets drawn as hyperedge outlines around their pins (not as extra wires)."""
    pos = {"A": (300, 420), "B": (450, 420), "C": (600, 420), "D": (750, 420), "E": (900, 420), "F": (900, 640)}
    cv.rect(220, 330, 760, 180, stroke=GOLD, width=4, r=60, alpha=alpha)
    cv.rect(195, 300, 810, 240, stroke=PURPLE, width=4, r=80, alpha=alpha, dash=[14, 9])
    cv.rect(830, 350, 140, 360, stroke=TEAL, width=5, r=60, alpha=alpha)
    cv.text(230, 284, "net enable（5 引脚）", 26, GOLD, "bold", alpha=alpha)
    cv.text(230, 580, "net reset（5 引脚）", 26, PURPLE, "bold", alpha=alpha)
    cv.text(1000, 760, "net n1（2 引脚，私有）", 26, TEAL, "bold", "right", alpha=alpha)
    for n, p in pos.items():
        node(cv, *p, n, "#a9bdb8", 38, alpha, GOLD if pick and n in pick else None)
    return pos


def s_pin(cv, c):
    netlist(cv, 1.0, 0, ("A", "B") if c.k in (1, 2) else ("E", "F") if c.k >= 3 else None)
    raw = {(p["u"], p["v"]): p["score"] for p in PIN["raw"]}
    sc = {(p["u"], p["v"]): p["score"] for p in PIN["scores"]}
    panel(cv, 1180, 170, 610, 640, "两种计分", 1.0)
    rows = [["", "按 net 计数", "pin-count"]]
    rows.append(["A–B", str(raw[("A", "B")]) if c.on(1) else "", f"{sc[('A', 'B')]:g}" if c.on(2) else ""])
    rows.append(["E–F", str(raw[("E", "F")]) if c.on(1) else "", f"{sc[('E', 'F')]:g}" if c.on(3) else ""])
    table(cv, 1220, 280, [130, 220, 200], rows, 36, 80, {2: GOLD} if c.on(3) else {1: GOLD} if c.on(1) else None)
    if c.on(2):
        formula(cv, 1470, 560, [("1/(5−1) + 1/(5−1) = ", INK), ("0.5", GOLD)], 36, c.p(2))
    if c.on(3):
        formula(cv, 1470, 640, [("1/(2−1) = ", INK), ("1", TEAL)], 36, c.p(3))
    if c.on(4):
        cv.paragraph(1190, 720, "宽 net 连着 10 对单元，几乎说明不了谁和谁特别亲近。", 28, 580, MUTED, alpha=c.p(4))


CODE = ["for 每个无序节点对 (u, v)，u < v:",
        "    score ← w(u, v)，没有边则为 0",
        "    for 每个共同邻居 x:",
        "        score ← score + min(w(u,x), w(v,x))",
        "    if score > 0: 记下 (u, v, score)",
        "按 (−score, u, v) 排序",
        "返回排名（不是分组）"]


def s_code(cv, c):
    active = [(1,), (2,), (3, 4), (5,), (6, 7)][min(c.k, 4)]
    code(cv, 170, 280, CODE, active, 32, 70, w=1000)
    notes = ["B–D 也要检查：没有直接边，从 0 开始。", "w(B, D) 不存在：score = 0。", "共同邻居 C：min(4, 2) = 2。", "2 > 0：B–D 进入列表。", "排序时并列按名字，结果与输入顺序无关。"]
    cv.paragraph(1250, 360, notes[min(c.k, 4)], 36, 560, INK, alpha=c.p(c.k, 0.5))


def s_eda(cv, c):
    items = ["评分决定“先把谁粘在一起”：连得紧的单元先合并，跨区长线就少",
             "评分是一种模型：直接边权、共同邻居、pin-count 回答的问题不同",
             "宽 net（时钟、复位）不摊薄，会让所有单元看起来一样亲近",
             "评分只排名，不分组；下一模块用“簇间边权和”真正开始合并"]
    for i, s in enumerate(items):
        if c.on(i):
            cv.rect(200, 210 + i * 150, 1520, 116, fill=PANEL2, stroke="#24474d", width=2, r=14, alpha=c.p(i))
            cv.text(250, 282 + i * 150, f"0{i + 1}", 34, GOLD, "bold", family=MONO, alpha=c.p(i))
            cv.text(340, 282 + i * 150, s, 34, INK, alpha=c.p(i))


SCENES = [
    Scene("s00-title", s_title, [Beat("", 2.6)]),
    Scene("s01-hook", s_hook, [Beat("一个三角形 PQR，每条边 4；旁边一对 X–Y，边权 5。"), Beat("如果要先合并一对，你会选哪一对？", 4.2)], chapter="一 · 先预测"),
    Scene("s02-model", s_model, [Beat("先说清输入：普通的边只连两个单元。", 2.6), Beat("一个 net 可以连五个、甚至上千个单元。", 3.0), Beat("要给其中的“一对”打分，就得先选一个模型。", 3.6)], chapter="二 · 图与 net"),
    Scene("s03-edge", s_edge, [Beat("最直接的模型：两点之间的边权就是分数。", 4.0), Beat("A–B 和 D–E 都是 5，谁排前面？按名字：A 在 D 前。", 3.4), Beat("A–C 与 C–E 也并列：同样按名字。排名就与输入顺序无关了。", 3.4)], chapter="三 · 直接边权"),
    Scene("s04-ac", s_ac, [Beat("第二个模型：共同邻居。先看 A–C 的直接边：1。", 2.6), Beat("A 和 C 都连着 B。", 2.4), Beat("经过 B 的联系只和较弱的那条边一样强：min(5, 4) = 4。", 3.6), Beat("A–C 的共同邻居分 = 1 + 4 = 5。", 3.0)], chapter="四 · 共同邻居"),
    Scene("s05-bd", s_bd, [Beat("再看 B–D：它们之间没有导线，直接部分是 0。", 2.8), Beat("可是 B 和 D 都连着 C。", 2.4), Beat("经 C：min(4, 2) = 2。", 2.6), Beat("B–D 的分数是 2——只在已有的边上打分，就会漏掉它。", 3.4), Beat("这不是新增导线：图没变，变的是这一对的分数。", 3.4)]),
    Scene("s06-priority", s_priority, [Beat("回到开头的问题。按直接边权：X–Y 最粗，第一对是 X–Y。", 3.4), Beat("按共同邻居：三角形里每一对都经过第三个点。", 3.0), Beat("P–Q = 4 + min(4, 4) = 8，P–R、Q–R 也是 8。", 3.6), Beat("三对并列，按名字取 P–Q。换一种评分，第一对就变了。", 4.0)], chapter="五 · 换评分，第一对就变"),
    Scene("s07-pin", s_pin, [Beat("网表也一样。两条宽 net 连着 A 到 E，一条私有 net 只连 E、F。", 3.8), Beat("如果只数“有几条 net 同时连着”：A–B 有 2 条，E–F 只有 1 条。", 3.8), Beat("clique 模型把一个 net 摊成 |e|−1 份：A–B = 1/4 + 1/4 = 0.5。", 4.2), Beat("E–F 的 net 只有两个引脚：1/(2−1) = 1。E–F 排第一。", 3.8), Beat("宽 net 被稀释，私有连接才显出来。", 3.0)], chapter="六 · 宽 net 的稀释"),
    Scene("s08-code", s_code, [Beat("把共同邻居评分写成伪代码，用 B–D 走一遍。", 2.6), Beat("没有直接边：从 0 开始。", 2.2), Beat("对每个共同邻居，加上较弱的那条边。", 2.8), Beat("分数为正，记下这一对。", 2.2), Beat("最后按分数降序、名字升序排好。输出的是排名，不是分组。", 3.6)], chapter="七 · 伪代码与 EDA"),
    Scene("s09-eda", s_eda, [Beat("回到芯片设计。", 1.8), Beat("评分是模型的选择，要写明用的是哪一种。", 3.0), Beat("宽 net 不摊薄，会掩盖真正的局部结构。", 3.0), Beat("下一模块：用簇间边权和，开始真正的合并。", 3.4)], tail=1.2),
]
POSTER_AT = 120.0
