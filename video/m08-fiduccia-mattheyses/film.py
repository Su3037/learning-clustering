"""Module 08 · Fiduccia–Mattheyses 改进 —— 影片《合法的那一步》. Data: site/data/m08-fiduccia-mattheyses/traces.json."""
from render import Scene, Beat
from kit import (W, H, TEAL, GOLD, RED, BLUE, PURPLE, INK, MUTED, FAINT, PANEL2, GROUP, SERIF, MONO,
                 ease, clamp, lerp, node, edge, panel, tag, table, code, formula, title_card, fit, load_trace, number_box, bar)

ID, TITLE = "fm", "合法的那一步"
MODULE = "Module 08 · Fiduccia–Mattheyses 改进"
MOOD, SEED = "curious", 8
WHY = "约 4 分钟：合法性与回退为主；单独一段审查原附件反例，再用经穷举核验的反例说明负收益。"
T = load_trace("m08-fiduccia-mattheyses")
G = T["g01"]
POS = fit({k: tuple(v) for k, v in G["positions"].items()}, (200, 230, 860, 780))
E5 = [tuple(e) for e in G["edges"]]
EV = T["run"]["events"]
P1 = T["run"]["result"]["passes"][0]
SIDEC = {0: TEAL, 1: BLUE}


def graph(cv, pos, edges, side, locked=(), focus=None, blocked=(), alpha=1.0, hl=None, r=40):
    for u, v, w in edges:
        k = "|".join(sorted((u, v)))
        st = (hl or {}).get(k) or ("cut" if side[u] != side[v] else "inside")
        edge(cv, pos[u], pos[v], w, st, alpha)
    for n, p in pos.items():
        ring = GOLD if n == focus else (RED if n in blocked else None)
        node(cv, *p, n, SIDEC[side[n]], r, alpha, ring, n in locked)


def side_count(cv, side, x, y, maxdiff, alpha=1.0):
    n0 = sum(1 for s in side.values() if s == 0)
    n1 = len(side) - n0
    ok = n0 > 0 and n1 > 0 and abs(n0 - n1) <= maxdiff
    tag(cv, x, y, f"两侧人数 {n0} : {n1}", TEAL if ok else RED, alpha, 28)


def gain_table(cv, gains, x, y, chosen=None, alpha=1.0):
    rows = [["节点", "侧", "收益", "合法"]] + [[g["node"], str(g["side"]), f"{g['gain']:+d}", "已锁定" if g["locked"] else ("是" if g["legal"] else "否")] for g in gains]
    hl = {i + 1: (GOLD if g["node"] == chosen else RED) for i, g in enumerate(gains) if g["node"] == chosen or (not g["legal"] and not g["locked"])}
    table(cv, x, y, [120, 90, 130, 150], rows, 32, 62, hl, alpha=alpha)


def s_title(cv, c):
    title_card(cv, "合法的那一步", "Fiduccia–Mattheyses refinement · Module 08", c.p(0, 1.2))


def s_diff(cv, c):
    panel(cv, 140, 170, 800, 620, "KL：一换一", c.p(0))
    panel(cv, 980, 170, 800, 620, "FM：一次动一个", c.p(1))
    for i, n in enumerate("AB"):
        node(cv, 330, 340 + i * 200, n, TEAL, 40, c.p(0))
    for i, n in enumerate("CDE"):
        node(cv, 740, 300 + i * 160, n, BLUE, 40, c.p(0))
    cv.arrow(380, 345, 690, 455, GOLD, 4, 16, c.p(0)); cv.arrow(690, 470, 380, 360, GOLD, 4, 16, c.p(0))
    cv.text(540, 740, "两侧人数永远 2 : 3", 30, MUTED, align="center", alpha=c.p(0))
    if c.on(1):
        for i, n in enumerate("AB"):
            node(cv, 1170, 340 + i * 200, n, TEAL, 40, c.p(1))
        for i, n in enumerate("CDE"):
            node(cv, 1580, 300 + i * 160, n, BLUE, 40, c.p(1))
        cv.arrow(1530, 460, 1230, 440, GOLD, 4, 16, c.p(1))
        cv.text(1380, 740, "移动后 3 : 2：在窗口内才允许", 30, MUTED, align="center", alpha=c.p(1))
    if c.on(2):
        tag(cv, W / 2, 860, "平衡窗口：|n₀ − n₁| ≤ maxDiff，两侧非空", GOLD, c.p(2), 30)


def s_gains(cv, c):
    g0 = EV[0]["gains"]
    graph(cv, POS, E5, T["seed"], blocked=("A", "E") if c.on(1) else (), focus="D" if c.on(2) else None)
    gain_table(cv, g0, 1100, 260, "D" if c.on(2) else None)
    side_count(cv, T["seed"], 540, 860, 1)
    if c.on(1):
        cv.paragraph(1100, 700, "A、E 收益 +6，但在只有 2 人的左侧：移走就是 1 : 4。", 30, 700, RED, alpha=c.p(1))


def s_fste(cv, c):
    m = P1["moves"][0]
    hl = {}
    if c.on(1):
        hl["D|E"] = "hl"
    if c.on(2):
        hl["C|D"] = "trial"
    graph(cv, POS, E5, T["seed"], focus="D", hl=hl)
    panel(cv, 1060, 220, 720, 520, "D 的收益 = FS − TE")
    if c.on(1):
        cv.paragraph(1100, 330, "FS：D–E 在右侧只有 D 一个端点 → 移走后不再被切，+5", 32, 640, TEAL, alpha=c.p(1))
    if c.on(2):
        cv.paragraph(1100, 470, "TE：C–D 在左侧没有端点 → 移走后开始被切，−2", 32, 640, RED, alpha=c.p(2))
    if c.on(3):
        cv.text(1100, 650, f"收益 = 5 − 2 = {m['gain']}", 40, GOLD, "bold", alpha=c.p(3))


def s_walk(cv, c):
    k = min(c.k, len(P1["moves"]))
    side = dict(T["seed"])
    locked = []
    for m in P1["moves"][:k]:
        side[m["node"]] = m["to"]; locked.append(m["node"])
    cur = P1["moves"][k - 1] if k else None
    graph(cv, POS, E5, side, locked, cur["node"] if cur else None)
    side_count(cv, side, 540, 860, 1)
    rows = [["步", "移动", "收益", "cut"]] + [[str(i + 1), m["node"], f"{m['gain']:+d}", str(m["cutAfter"])] for i, m in enumerate(P1["moves"][:k])]
    table(cv, 1100, 260, [100, 140, 140, 140], rows, 32, 66, {k: GOLD} if k else None)


def cum_chart(cv, x, y, gains, best, reveal=99, chosen=True, title="累计收益"):
    panel(cv, x, y, 680, 420, title)
    base, sc = y + 260, 18
    cv.line(x + 40, base, x + 650, base, "#3b5a5e", 2)
    for k, g in enumerate(gains):
        if k > reveal:
            continue
        bx = x + 60 + k * 100
        col = GOLD if (chosen and k == best) else (TEAL if g > 0 else RED if g < 0 else MUTED)
        hgt = abs(g) * sc
        cv.rect(bx, base - hgt if g >= 0 else base, 70, max(5, hgt), fill=col, r=6)
        cv.text(bx + 35, (base - hgt - 12) if g >= 0 else base + hgt + 36, f"{g:+d}" if g else "0", 30, col, "bold", "center")
        cv.text(bx + 35, y + 400, f"k={k}", 24, MUTED, align="center")
        if chosen and k == best:
            cv.rect(bx - 10, y + 60, 90, 360, stroke=GOLD, width=3, r=10, dash=[10, 7])


def s_prefix(cv, c):
    side = P1["accepted"] if c.on(2) else {**T["seed"], **{m["node"]: m["to"] for m in P1["moves"]}}
    graph(cv, POS, E5, side, () if c.on(2) else [m["node"] for m in P1["moves"]])
    cum_chart(cv, 1080, 200, P1["prefixGains"], P1["bestK"], chosen=c.on(1))
    if c.on(2):
        tag(cv, 1420, 700, f"接受前 {P1['bestK']} 步：ABC | DE，cut {P1['acceptedCut']}", TEAL, c.p(2), 28)
    if c.on(3):
        cv.paragraph(1100, 780, f"试探终点 cut {P1['moves'][-1]['cutAfter']} 被丢弃。第二轮最佳前缀为空，停止。", 28, 660, MUTED, alpha=c.p(3))


def s_legacy(cv, c):
    L = T["legacy"]
    panel(cv, 160, 170, 1600, 640, "审查原附件的 hillclimb 说明")
    gE = next(g for g in L["run"]["events"][0]["gains"] if g["node"] == "E")
    rows = [["", "原文", "按附件数据计算"], ["初始 cut", "9", str(L["run"]["events"][0]["metrics"]["cut"])], ["合法移动的收益", "全部 ≤ 0", f"E 合法，+{gE['gain']}"], ["最终 cut", "4", f"首轮 {L['run']['result']['passes'][0]['acceptedCut']}；穷举最优 {L['optimum']['cut']}"]]
    shown = 1 + min(3, c.k + 1)
    table(cv, 220, 290, [400, 400, 640], rows[:shown], 36, 100, {i: RED for i in range(1, shown)})
    if c.on(3):
        cv.paragraph(220, 720, "文字与数据不符：它不能用来说明负收益的作用。本课程只把它留作回归测试。", 30, 1480, GOLD, alpha=c.p(3))


def s_escape(cv, c):
    E = T["escape"]
    g = E["graph"]
    pos = fit({k: tuple(v) for k, v in g["positions"].items()}, (200, 260, 900, 760))
    edges = [tuple(e) for e in g["edges"]]
    p = E["run"]["result"]["passes"][0]
    k = min(max(c.k - 1, 0), 3)
    side = dict(g["seed"])
    locked = []
    for m in p["moves"][:k]:
        side[m["node"]] = m["to"]; locked.append(m["node"])
    if c.k >= 5:
        side, locked = p["accepted"], []
    graph(cv, pos, edges, side, locked, p["moves"][k - 1]["node"] if 0 < k <= 3 and c.k < 5 else None)
    panel(cv, 1040, 200, 760, 580, "替换反例（穷举核验）")
    if c.k == 0 or c.k == 1:
        gains = [x for x in E["run"]["events"][0]["gains"] if x["legal"]]
        cv.text(1080, 300, "初始合法收益：" + "，".join(f"{x['node']} {x['gain']:+d}" for x in gains), 28, INK)
        cv.text(1080, 360, f"全部 ≤ 0：只走正收益的爬山法停在 cut {p['startCut']}", 30, RED, "bold", alpha=c.p(0))
    else:
        rows = [["步", "移动", "收益", "cut"]] + [[str(i + 1), m["node"], f"{m['gain']:+d}", str(m["cutAfter"])] for i, m in enumerate(p["moves"][:min(k, 3)])]
        table(cv, 1080, 300, [100, 140, 140, 140], rows, 32, 66, {min(k, 3): GOLD})
    if c.k >= 5:
        tag(cv, 1420, 690, f"保留 {p['bestK']} 步：cut {p['acceptedCut']} = 穷举最优 {E['optimum']['cut']}", TEAL, 1.0, 28)


def s_bucket(cv, c):
    ev = EV[0]
    panel(cv, 160, 170, 1600, 640, "桶：按收益分组")
    for i, b in enumerate(ev["buckets"]):
        y = 290 + i * 100
        cv.text(240, y, f"{b['gain']:+d}", 36, GOLD, "bold", family=MONO)
        for j, n in enumerate(b["nodes"]):
            leg = next(g for g in ev["gains"] if g["node"] == n)["legal"]
            node(cv, 380 + j * 100, y - 12, n, TEAL if leg else "#5d7c80", 34, c.p(0), None if leg else RED, size=28)
    if c.on(1):
        cv.paragraph(900, 300, "论文：桶链表 + 最大收益指针，增量更新，每轮代价与引脚总数成正比。", 32, 800, INK, alpha=c.p(1))
    if c.on(2):
        cv.paragraph(900, 480, "本课程：收益增量更新；但选最大时仍扫描合法候选——不能称为线性时间。", 32, 800, GOLD, alpha=c.p(2))


def s_multipin(cv, c):
    pins = {"A": (360, 360), "B": (360, 560), "C": (560, 460), "D": (1000, 460)}
    side = {"A": 0, "B": 0, "C": 0, "D": 1}
    hub = (760, 460)
    for n, p in pins.items():
        cv.line(*hub, *p, PURPLE, 4)
    cv.circle(*hub, 14, fill=PURPLE)
    cv.text(760, 420, "net（权 3）", 26, PURPLE, "bold", "center")
    for n, p in pins.items():
        node(cv, *p, n, SIDEC[side[n]], 40)
    cv.line(820, 220, 820, 760, GOLD, 3, 1.0, dash=[10, 8])
    panel(cv, 1150, 220, 640, 560, "按引脚计数")
    if c.on(0):
        cv.paragraph(1190, 320, "D 是右侧唯一的引脚：移过去 net 不再被切，收益 +3。", 30, 570, TEAL, alpha=c.p(0))
    if c.on(1):
        cv.paragraph(1190, 460, "A 移走后，两侧仍各有引脚：net 仍被切，收益 0。", 30, 570, INK, alpha=c.p(1))
    if c.on(2):
        cv.paragraph(1190, 600, "拆成团（每对 1）再按边算，A 会变成 −1：两种模型不等价。", 30, 570, RED, alpha=c.p(2))


CODE = ["repeat：全部解锁，记下起点", "  按 net 计数，算出所有收益", "  while 有合法的未锁定节点:", "    v ← 合法候选中收益最大者", "    移动 v（试探），锁定 v", "    只更新受影响节点的收益", "  k* ← 最佳前缀（允许 0）", "  回到起点，只应用前 k* 步", "until k* = 0"]


def s_code(cv, c):
    active = [(1, 2), (3, 4), (5, 6), (7, 8), (9,)][min(c.k, 4)]
    code(cv, 170, 260, CODE, active, 30, 64, w=1040)
    notes = ["与 KL 相同的外层结构。", "“最大”只在合法候选中比较。", "收益可以为负；增量更新。", "回退到最佳前缀。", "空前缀即停止。"]
    cv.paragraph(1290, 360, notes[min(c.k, 4)], 36, 520, INK, alpha=c.p(c.k, 0.5))


def s_limits(cv, c):
    items = ["平衡按人数，不是面积（面积窗口未实现）", "多引脚 net 已按引脚计数实现，标为拓展", "教学实现没有达到论文的线性时间", "下一模块：目标换成延迟，节点可以复制"]
    for i, s in enumerate(items):
        if c.on(i):
            cv.rect(200, 210 + i * 150, 1520, 116, fill=PANEL2, stroke="#24474d", width=2, r=14, alpha=c.p(i))
            cv.text(250, 282 + i * 150, f"0{i + 1}", 34, GOLD, "bold", family=MONO, alpha=c.p(i))
            cv.text(340, 282 + i * 150, s, 34, INK, alpha=c.p(i))


SCENES = [
    Scene("s00-title", s_title, [Beat("", 2.6)]),
    Scene("s01-diff", s_diff, [Beat("KL 一换一：两侧人数永远不变。", 2.6), Beat("FM 一次只移动一个点：更灵活，但人数会变。", 3.2), Beat("所以要加一个平衡窗口：两侧人数之差不超过 maxDiff。", 3.6)], chapter="一 · 与 KL 的差别"),
    Scene("s02-gains", s_gains, [Beat("同一个种子 AE | BCD，maxDiff = 1。", 2.6), Beat("A、E 的收益是 +6，最大——可它们在只有 2 人的左侧。", 3.6), Beat("移走就违反平衡。合法候选里最大的是 D：+3。", 3.4)], chapter="二 · 合法性与收益"),
    Scene("s03-fste", s_fste, [Beat("把 D 的收益拆开看。", 2.0), Beat("D–E：D 是它在右侧唯一的端点，移走后不再被切，+5。", 3.6), Beat("C–D：左侧没有端点，移走后开始被切，−2。", 3.2), Beat("收益 = 5 − 2 = 3。", 2.4)]),
    Scene("s04-walk", s_walk, [Beat("一轮：每次在合法的未锁定节点里选收益最大的。", 3.2), Beat("D：+3，cut 9。", 2.0), Beat("左侧变成 3 人，A 合法了：+6，cut 3。", 3.0), Beat("之后全是负收益：C −2，cut 5。", 2.6), Beat("E −6，cut 11。", 2.0), Beat("B −1，cut 12。没有合法节点了，本轮结束。", 3.2)], chapter="三 · 走完一轮"),
    Scene("s05-prefix", s_prefix, [Beat("累计收益：3、9、7、1、0。", 2.8), Beat("最大的是前 2 步。", 2.2), Beat("回到起点，只做 D 和 A：ABC | DE，cut 3。", 3.4), Beat("最后的 cut 12 只是试探的终点。", 2.8)], chapter="四 · 最佳前缀"),
    Scene("s06-legacy", s_legacy, [Beat("原附件里有一个“负收益爬坡”的案例。我们用它自己的数据核验。", 3.8), Beat("原文说初始 cut 9；按数据算是 18。", 3.0), Beat("原文说所有合法收益都 ≤ 0；可 E 合法，收益 +10。", 3.4), Beat("原文说降到 4；首轮最佳和穷举最优都是 8。它不能当反例。", 4.0)], chapter="五 · 审查一个反例"),
    Scene("s07-escape", s_escape, [Beat("这是本课程用固定种子搜索、再穷举核验的反例。", 3.4), Beat("初始时所有合法移动的收益都 ≤ 0：只走正收益就停在 cut 6。", 3.8), Beat("FM 先把 A 移过去：−1。", 2.4), Beat("再移 B：−1，cut 升到 8。", 2.4), Beat("这时 E 的收益变成 +4：cut 4。", 2.8), Beat("保留前 3 步：cut 4，正是平衡最优。", 3.2)]),
    Scene("s08-bucket", s_bucket, [Beat("FM 论文把节点按收益放进“桶”。", 2.6), Beat("桶链表加最大指针，让每一轮的代价与引脚总数成正比。", 3.6), Beat("本课程的实验显示了桶，但选择时仍在扫描——不能说成线性时间。", 4.0)], chapter="六 · 桶与多引脚 net"),
    Scene("s09-multipin", s_multipin, [Beat("真正的多引脚 net：一根线连着 A、B、C、D。", 3.0), Beat("A 移走后，两侧仍各有引脚——收益 0。", 2.8), Beat("拆成团再按边算，会得到 −1。两种模型不等价。", 3.4)]),
    Scene("s10-code", s_code, [Beat("写成伪代码：外层与 KL 相同。", 2.4), Beat("内层：只在合法候选里选最大收益。", 2.8), Beat("移动、锁定、增量更新收益。", 2.6), Beat("一轮结束，回退到最佳前缀。", 2.6), Beat("空前缀即停止。", 1.8)], chapter="七 · 伪代码与局限"),
    Scene("s11-limits", s_limits, [Beat("FM 的边界：", 1.6), Beat("多引脚 net 是拓展。", 2.0), Beat("这份实现不是线性时间。", 2.2), Beat("下一模块：目标从 cut 换成延迟。", 3.0)], tail=1.2),
]
POSTER_AT = 70.0
