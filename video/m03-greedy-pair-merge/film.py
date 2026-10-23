"""Module 03 · 贪心成对合并 —— 影片《合并，再合并》. Data: site/data/m03-greedy-pair-merge/traces.json."""
from render import Scene, Beat
from kit import (W, H, TEAL, GOLD, RED, BLUE, PURPLE, INK, MUTED, FAINT, PANEL2, GROUP, SERIF, MONO,
                 ease, clamp, lerp, lerp2, node, edge, panel, tag, table, code, formula, title_card, fit, load_trace, hull, bar, number_box)

ID, TITLE = "merge", "合并，再合并"
MODULE = "Module 03 · 贪心成对合并"
MOOD, SEED = "steady", 3
WHY = "约 3 分半：三步合并各留出比较候选的时间；比较器错误单独一段，说明机制而不只给结论。"
T = load_trace("m03-greedy-pair-merge")
POS = fit({k: tuple(v) for k, v in T["g01"]["positions"].items()}, (220, 250, 920, 800))
EDGES = [tuple(e) for e in T["g01"]["edges"]]
RUN = T["runs"]["k2-capnone"]
CAP2 = T["runs"]["k2-cap2"]
MERGES = [e for e in RUN["events"] if e["kind"] == "merge"]
HC = {"AB": TEAL, "ABC": TEAL, "DE": BLUE}


def state_graph(cv, clusters, focus=(), alpha=1.0, cut_hl=False, ghost=None):
    where = {m: c["label"] for c in clusters for m in c["members"]}
    for c in clusters:
        if len(c["members"]) > 1:
            hull(cv, [POS[m] for m in c["members"]], HC.get(c["label"], PURPLE), 66, alpha, f"{c['label']} · 大小 {c['size']}",
                 below=sum(POS[m][1] for m in c["members"]) / len(c["members"]) > sum(p[1] for p in POS.values()) / len(POS))  # lower clusters: label underneath, clear of edge weights
    for u, v, w in EDGES:
        st = "inside" if where[u] == where[v] else ("cut" if cut_hl else "normal")
        edge(cv, POS[u], POS[v], w, st, alpha)
    for n, p in POS.items():
        node(cv, *p, n, HC.get(where[n], "#a9bdb8") if len(where[n]) > 1 else "#a9bdb8", 40, alpha, GOLD if n in focus else None)


def cut_panel(cv, value, prev=None, p=1.0, alpha=1.0):
    v = round(lerp(prev, value, p)) if prev is not None else value
    number_box(cv, 1440, 190, 360, 150, "cut（跨簇边权和）", v, RED if v > 3 else TEAL, alpha)
    bar(cv, 1464, 352, 312, 12, v / 18, RED if v > 3 else TEAL, alpha)


def cand_table(cv, ev, chosen_i=0, alpha=1.0, x=1060, y=440, show=99):
    rows = [["候选簇对", "亲和度", ""]]
    hl = {}
    for i, c in enumerate(ev["candidates"][:show]):
        rows.append([f"{c['a']}–{c['b']}", f"{c['affinity']}" + (f"（{'+'.join(str(p['w']) for p in c['parts'])}）" if len(c["parts"]) > 1 else ""), "超容量" if not c["legal"] else ("选中" if i == chosen_i else "")])
        if i == chosen_i and chosen_i is not None:
            hl[i + 1] = GOLD
    table(cv, x, y, [230, 230, 140], rows, 32, 62, hl, alpha=alpha)


def s_title(cv, c):
    title_card(cv, "合并，再合并", "Greedy pair merge · Module 03", c.p(0, 1.2))


def s_hook(cv, c):
    state_graph(cv, RUN["events"][0]["after"], alpha=c.p(0))
    cut_panel(cv, 18, alpha=c.p(1))
    if c.on(2):
        cv.paragraph(1080, 480, "规则只有一句：每次把最亲近的两个簇合在一起。", 34, 700, INK, alpha=c.p(2))


def s_setup(cv, c):
    state_graph(cv, RUN["events"][0]["after"])
    panel(cv, 1040, 170, 780, 640, "三个词")
    items = [("单点簇", "开始时每个节点自己是一个簇"), ("目标簇数 K", "簇数降到 K 就停（这里 K = 2）"), ("簇间亲和度", "两个簇之间所有边权之和")]
    for i, (a, b) in enumerate(items):
        if c.on(i):
            cv.text(1080, 290 + i * 160, a, 36, GOLD, "bold", alpha=c.p(i))
            cv.paragraph(1080, 340 + i * 160, b, 30, 700, INK, alpha=c.p(i))
    if c.on(3):
        tag(cv, 1430, 770, "合并一次，cut 恰好减少这一次的亲和度", TEAL, c.p(3))


def s_step1(cv, c):
    ev = MERGES[0]
    p = c.p(2, 1.4)
    state_graph(cv, ev["after"] if p > 0.5 else ev["before"], ("A", "B") if c.on(1) else (), 1.0)
    cut_panel(cv, ev["metrics"]["cut"], ev["metrics"]["cutBefore"], p)
    cand_table(cv, ev, 0 if c.on(1) else None, c.p(0), show=6)
    if c.on(1) and not c.on(2):
        tag(cv, 1360, 880 - 30, "并列 5：比较成员 A < D", GOLD, c.p(1))


def s_step2(cv, c):
    ev = MERGES[1]
    before = ev["before"]
    p = c.p(3, 1.4)
    state_graph(cv, ev["after"] if p > 0.5 else before, ("A", "B", "C") if c.on(2) else ())
    if c.on(0) and not c.on(3):
        # the two parallel edges A–C and B–C, highlighted and summed
        q = c.p(0)
        edge(cv, POS["A"], POS["C"], 1, "hl", q)
        edge(cv, POS["B"], POS["C"], 4, "hl", q)
        tag(cv, POS["C"][0] + 140, POS["C"][1] - 10, "AB–C = 1 + 4 = 5", GOLD, c.p(1), 28)
    cut_panel(cv, ev["metrics"]["cut"], ev["metrics"]["cutBefore"], p)
    cand_table(cv, ev, 0 if c.on(2) else None, 1.0)
    if c.on(2) and not c.on(3):
        tag(cv, 1360, 760, "并列 5：[A, B] < [D]", GOLD, c.p(2))


def s_step3(cv, c):
    ev = MERGES[2]
    p = c.p(1, 1.4)
    state_graph(cv, ev["after"] if p > 0.5 else ev["before"], ("D", "E") if not c.on(2) else (), cut_hl=c.on(2))
    cut_panel(cv, ev["metrics"]["cut"], ev["metrics"]["cutBefore"], p)
    cand_table(cv, ev, 0, c.p(0))
    if c.on(2):
        tag(cv, 1340, 680, f"剩下：C–D 2 + C–E 1 = {RUN['result']['cut']}", TEAL, c.p(2), 28)
    if c.on(3):
        cv.paragraph(1080, 760, "轨迹 18 → 13 → 8 → 3：每一步的下降量就是那一次的亲和度。", 30, 720, MUTED, alpha=c.p(3))


def s_bug(cv, c):
    panel(cv, 140, 160, 1640, 680, "原网页的比较器：数组被转成了字符串")
    a = c.p(0)
    cv.text(220, 290, "[−5, \"A\", \"B\"]", 40, INK, family=MONO, alpha=a)
    cv.text(220, 370, "[−1, \"A\", \"C\"]", 40, INK, family=MONO, alpha=a)
    if c.on(1):
        b = c.p(1)
        cv.text(760, 290, "→  \"-5,A,B\"", 40, GOLD, family=MONO, alpha=b)
        cv.text(760, 370, "→  \"-1,A,C\"", 40, GOLD, family=MONO, alpha=b)
        dx = 760 + cv.measure("→  \"-", 40, family=MONO)
        cv.rect(dx - 4, 248, cv.measure("5", 40, family=MONO) + 8, 136, stroke=RED, width=3, r=6, alpha=b)
        cv.text(1120, 330, "逐个字符比较：1 < 5", 34, RED, "bold", alpha=b)
    if c.on(2):
        q = c.p(2)
        cv.text(220, 470, f"于是第一步合并 A–C（亲和度 1），最终 {' | '.join(T['legacy']['result']['labels'])}，cut {T['legacy']['result']['cut']}。", 34, INK, alpha=q)
    if c.on(3):
        rows = [["配置", "K=2", "K=3", "K=2 容量2", "K=2 容量3"], ["原网页（字符串比较）", "9", "16", "12", "16"],
                ["正确比较（逐字段）", str(T["runs"]["k2-capnone"]["result"]["cut"]), str(T["runs"]["k3-capnone"]["result"]["cut"]), str(T["runs"]["k2-cap2"]["result"]["cut"]), str(T["runs"]["k2-cap3"]["result"]["cut"])]]
        table(cv, 220, 600, [420, 200, 200, 280, 280], rows, 32, 66, {2: TEAL}, alpha=c.p(3))


def s_capacity(cv, c):
    ev = [e for e in CAP2["events"] if e["kind"] == "merge"]
    stop = [e for e in CAP2["events"] if e["kind"] == "stopped"][0]
    if not c.on(2):
        state_graph(cv, ev[0]["after"], ("A", "B", "C") if c.on(1) else ())
    else:
        state_graph(cv, stop["after"], ())
    panel(cv, 1040, 170, 780, 360, "容量 C = 2（每个节点大小 1）")
    # capacity bar for AB+C
    for i in range(3):
        col = TEAL if i < 2 else RED
        cv.rect(1090 + i * 110, 290, 96, 70, fill=col, r=8, alpha=(1 if i < 2 else c.p(1)) * c.p(0))
    cv.line(1090 + 2 * 110 - 7, 270, 1090 + 2 * 110 - 7, 380, GOLD, 4, c.p(0), dash=[8, 6])
    cv.text(1090, 420, "AB + C 的大小 = 3 > 2：被阻止", 32, RED if c.on(1) else INK, "bold", alpha=c.p(1))
    if c.on(2):
        cv.text(1090, 480, "转选 D–E；之后 AB+C、C+DE 都是 3", 30, INK, alpha=c.p(2))
    if c.on(3):
        x = 1050
        for t, col in [("3 簇", INK), ("cut 8", RED), ("合法", TEAL), ("未达到 K", GOLD)]:
            x += tag(cv, x + 10, 640, t, col, c.p(3), 30, align="left") + 24
    if c.on(4):
        cv.paragraph(1060, 740, "没有合法的正亲和度对就停下，如实报告——绝不为了凑 K 硬塞。", 30, 740, MUTED, alpha=c.p(4))


CODE = ["clusters ← 每个节点一个单点簇",
        "while 簇数 > K:",
        "    cands ← 亲和度 > 0 的簇对",
        "    legal ← 合并后大小 ≤ C 的候选",
        "    if legal 为空: 停止（如实报告）",
        "    选 (−亲和度, P, Q) 最小的一对",
        "    收缩 P ∪ Q：cut 下降该亲和度",
        "返回 簇、cut、是否达到 K、停止原因"]


def s_code(cv, c):
    active = [(1,), (2, 3), (4, 5), (6,), (7, 8)][min(c.k, 4)]
    code(cv, 170, 270, CODE, active, 32, 70, w=1040)
    notes = ["开始：cut = 全部边权 18。", "每一步先列出所有正亲和度的簇对。", "有容量时先过滤；没有合法候选就停。", "逐字段比较：数值优先，平票看成员名字。", "四项结果分开报告。"]
    cv.paragraph(1290, 360, notes[min(c.k, 4)], 36, 520, INK, alpha=c.p(c.k, 0.5))


def s_limits(cv, c):
    items = ["不回撤：合并了就不再拆开，早期的选择限制后面的可能",
             "G01 得到 cut 3 只是这张图的性质，不说明贪心总是最优",
             "结果依赖评分与平票规则：换评分，顺序就会变",
             "下一模块：容量成为主角——装不下，还是走错了路？"]
    for i, s in enumerate(items):
        if c.on(i):
            cv.rect(200, 210 + i * 150, 1520, 116, fill=PANEL2, stroke="#24474d", width=2, r=14, alpha=c.p(i))
            cv.text(250, 282 + i * 150, f"0{i + 1}", 34, GOLD, "bold", family=MONO, alpha=c.p(i))
            cv.text(340, 282 + i * 150, s, 34, INK, alpha=c.p(i))


SCENES = [
    Scene("s00-title", s_title, [Beat("", 2.6)]),
    Scene("s01-hook", s_hook, [Beat("五个单元，六条带权的连线。", 2.4), Beat("每个单元先自己成一组：所有连线都跨组，cut = 18。", 3.2), Beat("连接最紧的先合并——这样一定能分出最好的结果吗？", 3.6)], chapter="一 · 连接与局部选择"),
    Scene("s02-setup", s_setup, [Beat("先说三个词。单点簇：开始时每个节点自己是一个簇。", 3.0), Beat("目标簇数 K：簇数降到 K 就停。这里 K = 2。", 3.0), Beat("簇间亲和度：两个簇之间所有边权之和。", 3.2), Beat("合并以后，这些边变成内部边——cut 恰好减少这么多。", 3.6)], chapter="二 · 单点簇、K 与亲和度"),
    Scene("s03-step1", s_step1, [Beat("第一步：列出所有候选。A–B 和 D–E 都是 5。", 3.4), Beat("并列时比较成员名字：A 在 D 前，选 A–B。", 3.4), Beat("合并：cut 从 18 降到 13。", 3.0)], chapter="三 · 逐步推演"),
    Scene("s04-step2", s_step2, [Beat("A、B 收缩成一个超节点 AB。", 2.4), Beat("AB 到 C 有两条平行边：1 和 4，加起来是 5。", 3.6), Beat("AB–C 和 D–E 又并列 5：比较 [A, B] 与 [D]，选 AB–C。", 4.0), Beat("cut 从 13 降到 8。", 2.6)]),
    Scene("s05-step3", s_step3, [Beat("第三步只剩一个大候选：D–E = 5。", 2.8), Beat("合并：cut 从 8 降到 3，簇数到 2，停止。", 3.2), Beat("剩下被切断的是 C–D 和 C–E。", 2.8), Beat("轨迹 18 → 13 → 8 → 3。", 2.6)]),
    Scene("s06-bug", s_bug, [Beat("原网页的 JavaScript 用 cand < best 比较这些数组。", 3.0), Beat("JavaScript 先把数组变成字符串，再一个字符一个字符地比较。", 3.6), Beat("字符 1 排在 5 前面：亲和度 1 的 A–C 被当成了“更好”。", 3.8), Beat("四个配置全受影响。本课程改为逐字段比较，并加了回归测试。", 4.2)], chapter="四 · 平票规则与比较器错误"),
    Scene("s07-capacity", s_capacity, [Beat("再加一条规则：每个簇最多放 2 个单元。", 2.8), Beat("第一步照旧合并 A–B。第二步想加入 C：大小 3，超过容量。", 3.8), Beat("被阻止，就转选 D–E。之后再也没有合法的合并。", 3.4), Beat("结果：3 个簇，cut 8。合法，但没有达到 K。", 3.4), Beat("没有合法的合并就停下，如实报告——不硬塞。", 3.2)], chapter="五 · 容量预览与停止"),
    Scene("s08-code", s_code, [Beat("把规则写成伪代码。", 2.0), Beat("每一步：先列出全部正亲和度的簇对。", 2.8), Beat("有容量就先过滤；没有合法候选就停止。", 3.0), Beat("选择键逐字段比较：数值优先，平票看名字。", 3.2), Beat("最后分开报告：簇、cut、是否达到 K、停止原因。", 3.4)], chapter="六 · 伪代码与局限"),
    Scene("s09-limits", s_limits, [Beat("贪心的边界：", 1.6), Beat("一次 cut 3，不等于总是最优。", 2.6), Beat("换评分，合并顺序就会变。", 2.4), Beat("下一模块：装不下，还是走错了路？", 3.0)], tail=1.2),
]
POSTER_AT = 72.0
