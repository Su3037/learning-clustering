"""Module 07 · Kernighan–Lin 改进 —— 影片《先试探，再回退》.
All numbers are read from site/data/m07-kernighan-lin/traces.json (engines/kl.js)."""
import json
import math
from pathlib import Path
from render import Scene, Beat
from kit import (W, H, TEAL, GOLD, RED, BLUE, INK, MUTED, FAINT, PANEL2, GROUP, SERIF, MONO,
                 ease, ramp, lerp, lerp2, clamp, node, edge, panel, tag, table, code, formula, bar, number_box, title_card)

ID, TITLE = "kl", "先试探，再回退"
MODULE = "Module 07 · Kernighan–Lin 改进"
MOOD, SEED = "curious", 7
WHY = "约 5 分钟：负收益试探、−2w 与回退各留出阅读停顿，其余公共定义回链 Module 03 与基础速查。"
ROOT = Path(__file__).resolve().parents[2]
T = json.loads((ROOT / "site/data/m07-kernighan-lin/traces.json").read_text())
EDGES = [tuple(e) for e in T["g01"]["edges"]]
EV = T["run"]["events"]
PASS1 = T["run"]["result"]["passes"][0]
PASS2 = T["run"]["result"]["passes"][1]
TRIAL1, TRIAL2 = [e for e in EV if e["kind"] == "trial-swap"][:2]
SEEDSIDE = T["seed"]

LEFT_X, RIGHT_X = 380, 900
SLOTS = {0: [(LEFT_X, 330), (LEFT_X, 620)], 1: [(RIGHT_X, 250), (RIGHT_X, 470), (RIGHT_X, 690)]}
SIDE_C = {0: TEAL, 1: BLUE}


def layout(side, prev=None):
    """Assign slots: keep a node's previous slot when it has not changed side."""
    pos, used = {}, {0: set(), 1: set()}
    if prev:
        for n, (s, k) in prev.items():
            if side[n] == s:
                pos[n] = (s, k); used[s].add(k)
    for n in sorted(side):
        if n not in pos:
            s = side[n]
            k = next(i for i in range(len(SLOTS[s])) if i not in used[s])
            pos[n] = (s, k); used[s].add(k)
    return pos


L0 = layout(SEEDSIDE)
S1 = dict(SEEDSIDE); S1["A"], S1["D"] = 1, 0
L1 = {**L0, "A": (1, L0["D"][1]), "D": (0, L0["A"][1])}
S2 = dict(S1); S2["E"], S2["C"] = 1, 0
L2 = {**L1, "E": (1, L1["C"][1]), "C": (0, L1["E"][1])}


def xy(lay, n):
    s, k = lay[n]
    return SLOTS[s][k]


def stage(cv, side, lay_from, lay_to=None, p=1.0, locked=(), rings=None, alpha=1.0, edge_states=None, arc_pair=None):
    """Draw the two rooms and the graph, nodes interpolating from lay_from to lay_to."""
    cv.rect(150, 150, 460, 640, stroke="#2b5158", width=2, r=24, alpha=alpha, dash=[10, 8])
    cv.rect(670, 150, 460, 640, stroke="#2b5158", width=2, r=24, alpha=alpha, dash=[10, 8])
    cv.text(380, 196, "左侧 · 2 个位置", 26, MUTED, "bold", "center", alpha=alpha)
    cv.text(900, 196, "右侧 · 3 个位置", 26, MUTED, "bold", "center", alpha=alpha)
    pos = {}
    for n in "ABCDE":
        a, b = xy(lay_from, n), xy(lay_to or lay_from, n)
        if arc_pair and n in arc_pair and lay_to:
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + (-120 if n == arc_pair[0] else 120))
            q = ease(p)
            pos[n] = (lerp(lerp(a[0], mid[0], q), lerp(mid[0], b[0], q), q), lerp(lerp(a[1], mid[1], q), lerp(mid[1], b[1], q), q))
        else:
            pos[n] = lerp2(a, b, ease(p))
    st = edge_states or {}
    for u, v, w in EDGES:
        k = "|".join(sorted((u, v)))
        state = st.get(k) or ("cut" if side[u] != side[v] else "inside")
        edge(cv, pos[u], pos[v], w, state, alpha, label_offset=26)
    for n in "ABCDE":
        node(cv, *pos[n], n, SIDE_C[side[n]], 42, alpha, (rings or {}).get(n), n in locked)
    return pos


def cut_meter(cv, x, y, value, label="cut", alpha=1.0, c=RED, total=18):
    number_box(cv, x, y, 250, 150, label, value, c, alpha)
    from kit import bar as _bar
    _bar(cv, x + 24, y + 160, 202, 10, value / total, c, alpha)


def cut_of(side):
    return sum(w for u, v, w in EDGES if side[u] != side[v])


# ---------------- scenes ----------------
def s_hook(cv, c):
    p = c.p(0, 1.2)
    stage(cv, SEEDSIDE, L0, alpha=p, edge_states={"|".join(sorted((u, v))): "normal" for u, v, _ in EDGES} if not c.on(1) else None)
    if c.on(1):
        q = c.p(1, 0.8)
        cut_meter(cv, 1300, 260, cut_of(SEEDSIDE), "跨组边权 cut", q)
    if c.on(2):
        cv.paragraph(1300, 520, "两侧人数固定：左 2，右 3。只能一对一交换。", 34, 470, INK, alpha=c.p(2))


def s_dvalue(cv, c):
    stage(cv, SEEDSIDE, L0, rings={n: GOLD for n in ("A",) if not c.on(2)})
    panel(cv, 1220, 170, 620, 600, "D(v) = 外部 − 内部")
    d = TRIAL1["dValues"]
    rows = [["节点", "外部", "内部", "D"]] + [[n, str(d[n]["ext"]), str(d[n]["int"]), f"{d[n]['D']:+d}"] for n in "ABCDE"]
    shown = 2 if not c.on(1) else 6
    hi = {1: GOLD} if not c.on(2) else {}
    table(cv, 1260, 270, [120, 140, 140, 140], rows[:shown], 34, 64, hi, alpha=c.p(0))
    if c.on(3):
        cv.paragraph(1260, 700, "D 越大，这个点越想换到对面。", 30, 560, MUTED, alpha=c.p(3))


def s_pairs(cv, c):
    stage(cv, SEEDSIDE, L0, rings={"A": GOLD, "D": GOLD} if c.on(2) else None)
    panel(cv, 1180, 150, 680, 660, "成对收益 g(a, b)")
    formula(cv, 1520, 270, [("g", GOLD), (" = D(a) + D(b) − ", INK), ("2w(a,b)", RED)], 40, c.p(0))
    cands = TRIAL1["candidates"]
    rows = [["左 a", "右 b", "D(a)+D(b)", "−2w", "g"]] + [[x["a"], x["b"], str(x["Da"] + x["Db"]), str(-2 * x["w"]), f"{x['gain']:+d}"] for x in cands]
    table(cv, 1220, 360, [90, 90, 190, 120, 120], rows, 32, 62, {1: GOLD} if c.on(2) else None, alpha=c.p(1))


def s_minus2w(cv, c):
    # E–D: both count the DE edge as external, but after the swap DE is still cut.
    p = c.p(1, 1.6)
    side_after = dict(SEEDSIDE); side_after["E"], side_after["D"] = 1, 0
    lay_after = {**L0, "E": (1, L0["D"][1]), "D": (0, L0["E"][1])}
    stage(cv, SEEDSIDE if p < 0.5 else side_after, L0, lay_after if c.on(1) else None, p, arc_pair=("E", "D"),
          edge_states={"D|E": "hl"})
    panel(cv, 1220, 170, 620, 600, "为什么减 2w")
    lines = [("D(E) = 6，D(D) = 3，相加是 9", INK), ("两者都把边 DE（5）算作外部", GOLD), ("交换后 E、D 仍在两侧：DE 还是被切", RED), ("所以要扣回 2 × 5 = 10", RED), ("g(E, D) = 9 − 10 = −1", TEAL)]
    for i, (s, col) in enumerate(lines):
        if c.on(min(i, len(c.scene.beats) - 1)) or i == 0:
            cv.text(1260, 290 + i * 86, s, 32, col, "bold" if i == 4 else "normal", alpha=c.p(min(i, len(c.scene.beats) - 1), 0.6) if i else 1)


def s_trial1(cv, c):
    p = c.p(1, 1.8)
    side = S1 if p > 0.5 else SEEDSIDE
    locked = ("A", "D") if c.on(2) else ()
    stage(cv, side, L0, L1 if c.on(1) else None, p, locked, rings={"A": GOLD, "D": GOLD} if not c.on(2) else None, arc_pair=("A", "D"))
    cut_meter(cv, 1300, 220, TRIAL1["metrics"]["cut"] if p > 0.5 else TRIAL1["metrics"]["cutBefore"], "第 1 步试探后的 cut" if p > 0.5 else "起点 cut", 1.0, GOLD if p > 0.5 else RED)
    tag(cv, 1425, 470, "第 1 步 · 试探 g = +9", GOLD, c.p(1))
    if c.on(2):
        cv.paragraph(1300, 560, "A、D 锁定（虚线圈），本轮不再移动。", 30, 500, MUTED, alpha=c.p(2))


def s_trial2(cv, c):
    p = c.p(2, 1.8)
    side = S2 if p > 0.5 else S1
    locked = ("A", "D", "E", "C") if p > 0.5 else ("A", "D")
    stage(cv, side, L1, L2 if c.on(2) else None, p, locked, rings={"E": GOLD, "C": GOLD} if c.on(1) and p < 1 else None, arc_pair=("E", "C"))
    panel(cv, 1200, 150, 660, 300, "剩下的候选")
    cands = TRIAL2["candidates"]
    rows = [["左 a", "右 b", "g"]] + [[x["a"], x["b"], f"{x['gain']:+d}"] for x in cands]
    table(cv, 1240, 240, [130, 130, 130], rows, 32, 62, {1: GOLD} if c.on(1) else None, alpha=c.p(0))
    cut_meter(cv, 1300, 500, TRIAL2["metrics"]["cut"] if p > 0.5 else TRIAL2["metrics"]["cutBefore"], "第 2 步试探后的 cut" if p > 0.5 else "当前 cut（第 1 步之后）", 1.0, RED if p > 0.5 else GOLD)
    if c.on(2):
        tag(cv, 1425, 760, "第 2 步 · 试探 g = −8", RED, c.p(2))


def prefix_chart(cv, x, y, gains, best, alpha=1.0, reveal=1.0, chosen=True, title="累计收益（前 k 步）"):
    panel(cv, x, y, 640, 460, title, alpha)
    base_y, scale = y + 300, 18
    cv.line(x + 50, base_y, x + 600, base_y, "#3b5a5e", 2, alpha)
    cv.text(x + 40, base_y + 10, "0", 24, MUTED, align="right", alpha=alpha)
    n = len(gains)
    for k, g in enumerate(gains):
        if k / max(1, n - 1) > reveal + 1e-9 and k:
            continue
        bx = x + 90 + k * 160
        h = g * scale
        col = GOLD if (chosen and k == best) else (TEAL if g > 0 else RED if g < 0 else MUTED)
        if g:
            cv.rect(bx, base_y - max(h, 0), 90, abs(h), fill=col, r=6, alpha=alpha)
        else:
            cv.rect(bx, base_y - 3, 90, 6, fill=col, r=3, alpha=alpha)
        cv.text(bx + 45, base_y - max(h, 0) - 14 if g >= 0 else base_y - h + 40, f"{g:+d}" if g else "0", 32, col, "bold", "center", alpha=alpha)
        cv.text(bx + 45, y + 420, f"k = {k}", 26, MUTED, align="center", alpha=alpha)
        if chosen and k == best:
            cv.rect(bx - 14, y + 70, 118, 370, stroke=GOLD, width=3, r=12, alpha=alpha, dash=[10, 7])


def s_prefix(cv, c):
    back = c.p(3, 1.6)
    if back > 0:
        stage(cv, S1 if back > 0.5 else S2, L2, L1, back, ("A", "D") if back < 1 else (), arc_pair=("C", "E"))
    else:
        stage(cv, S2, L2, locked=("A", "D", "E", "C"))
    gains = PASS1["prefixGains"]
    prefix_chart(cv, 1200, 150, gains, PASS1["bestK"], 1.0, c.p(0, 1.6), chosen=c.on(1))
    if c.on(3):
        tag(cv, 1520, 690, f"接受前 {PASS1['bestK']} 步 · cut {PASS1['acceptedCut']}", TEAL, c.p(3))
    if c.on(4):
        cv.paragraph(1210, 760, "第 2 步被撤回；它只是为了看清后面还有没有更好的。", 28, 640, MUTED, alpha=c.p(4))


def s_pass2(cv, c):
    s_after = PASS1["accepted"]
    lay = layout(s_after)
    stage(cv, s_after, lay)
    prefix_chart(cv, 1200, 150, PASS2["prefixGains"], PASS2["bestK"], 1.0, c.p(1, 1.4), chosen=c.on(2), title="第二轮的累计收益")
    tag(cv, 1520, 690, "空前缀 k = 0 胜出 → 停止", GOLD, c.p(2))
    if c.on(0):
        cv.paragraph(1210, 760, f"第二轮试探：{' 、'.join(f'{s['a']}↔{s['b']} {s['gain']:+d}' for s in PASS2['swaps'])}", 28, 640, MUTED, alpha=c.p(0))


CODE = ["repeat:                      # 每次一轮 pass",
        "  从当前分组开始，全部解锁",
        "  while 两侧都有未锁定的点:",
        "    在未锁定的 (a, b) 中选 g 最大的一对",
        "    交换 a, b（试探），锁定，更新 D",
        "  取累计收益最大的前缀 k（允许 k = 0）",
        "  从本轮起点只应用前 k 步",
        "until k = 0"]


def s_code(cv, c):
    active = {0: (1, 2), 1: (3, 4, 5), 2: (6, 7), 3: (8,)}[min(c.k, 3)]
    code(cv, 200, 260, CODE, active, 30, 62, w=1100)
    notes = {0: "外层循环：一轮接一轮，直到某轮没有改善。", 1: "内层循环：负收益也照走，这是“试探”。", 2: "回退：只保留最好的连续前缀。", 3: "空前缀胜出就停：没有一轮能让 cut 变小了。"}
    cv.paragraph(1360, 330, notes[min(c.k, 3)], 34, 460, INK, alpha=c.p(c.k, 0.5))


def s_ab1(cv, c):
    ev = T["ab1"]["events"]
    first = [e for e in ev if e["kind"] == "trial-swap"][0]
    best = first["candidates"][0]
    edges = [(u, v, (1 if (u, v) == ("A", "B") else w)) for u, v, w in EDGES]
    pos = {n: xy(L0, n) for n in "ABCDE"}
    cv.rect(150, 150, 460, 640, stroke="#2b5158", width=2, r=24, dash=[10, 8])
    cv.rect(670, 150, 460, 640, stroke="#2b5158", width=2, r=24, dash=[10, 8])
    for u, v, w in edges:
        st = "hl" if (u, v) == ("A", "B") else ("cut" if SEEDSIDE[u] != SEEDSIDE[v] else "inside")
        edge(cv, pos[u], pos[v], w, st)
    for n in "ABCDE":
        node(cv, *pos[n], n, SIDE_C[SEEDSIDE[n]], 42)
    number_box(cv, 1300, 220, 250, 150, "初始 cut", first["metrics"]["cutBefore"], RED, c.p(0))
    if c.on(1):
        formula(cv, 1500, 520, [("g(A, D) = ", INK), (f"{best['Da']}", TEAL), (" + ", INK), (f"{best['Db']}", TEAL), (f" − {2 * best['w']} = ", INK), (f"{best['gain']}", GOLD)], 44, c.p(1))
    if c.on(2):
        cv.paragraph(1250, 610, "边权变了，D 值和收益随之改变；同一种子，换图就要重新计算。", 30, 560, MUTED, alpha=c.p(2))


def s_limits(cv, c):
    items = ["两侧人数固定：成对交换保持人数，不保证单元面积平衡", "结果依赖初始分组：从同一个坏种子出发比较才公平",
             "得到 cut 3 只说明这张图；KL 是启发式，一般不保证全局最优", "下一章 FM：一次只移动一个点，用平衡窗口代替“一换一”"]
    for i, s in enumerate(items):
        if c.on(i):
            cv.rect(220, 220 + i * 150, 1480, 116, fill=PANEL2, stroke="#24474d", width=2, r=14, alpha=c.p(i))
            cv.text(270, 292 + i * 150, f"0{i + 1}", 34, GOLD, "bold", family=MONO, alpha=c.p(i))
            cv.text(360, 292 + i * 150, s, 36, INK, alpha=c.p(i))


def s_title(cv, c):
    title_card(cv, "先试探，再回退", "Kernighan–Lin refinement · Module 07", c.p(0, 1.2))


SCENES = [
    Scene("s00-title", s_title, [Beat("", 2.6)], chapter=None),
    Scene("s01-hook", s_hook, [Beat("两个机房：左边放 2 个单元，右边放 3 个。人数不能变。", 0), Beat("跨房间的连线越多，代价越大：现在 cut = 12。"), Beat("能不能用一对一交换，把 cut 降下来？", 3.0)], chapter="一 · 固定人数的改进"),
    Scene("s02-dvalue", s_dvalue, [Beat("先给每个点算一个数：D = 外部边权 − 内部边权。"), Beat("A 的连线全在对面：D(A) = 6 − 0 = 6。", 3.2), Beat("D 大，说明这个点“想去对面”。"), Beat("五个点的 D 值都由当前分组算出。", 2.6)], chapter="二 · cut 与 D 值"),
    Scene("s03-pairs", s_pairs, [Beat("交换一对 a、b，收益是 D(a) + D(b) − 2w(a,b)。", 3.0), Beat("把左右各一点配成 6 对，逐一计算。", 3.0), Beat("最大的是 A↔D：6 + 3 − 0 = 9。", 3.4)], chapter="三 · 成对收益与 −2w"),
    Scene("s04-minus2w", s_minus2w, [Beat("为什么要减 2w？看 E 与 D。", 2.4), Beat("D(E) + D(D) = 9，可是两个 D 都把边 DE 算成了“外部”。", 4.0), Beat("交换以后，E、D 依旧分处两侧——DE 还是被切。", 3.4), Beat("这条边被多算了两次，要扣回 2 × 5。", 3.0), Beat("所以 g(E, D) = 9 − 10 = −1，并不划算。", 3.2)]),
    Scene("s05-trial1", s_trial1, [Beat("第一步：选收益最大的 A↔D。", 2.4), Beat("交换——cut 从 12 降到 3。", 3.4), Beat("A、D 锁定。注意：这还只是试探。", 3.4)], chapter="四 · 试探与锁定"),
    Scene("s06-trial2", s_trial2, [Beat("重新计算 D。剩下的候选，收益全是负数。", 3.2), Beat("KL 不停下：照样选最大的那个，E↔C，−8。", 3.6), Beat("cut 暂时升到 11。这一步也只是试探。", 3.6)]),
    Scene("s07-prefix", s_prefix, [Beat("一轮走完，回头看累计收益：0、+9、+1。", 3.6), Beat("最大的是前 1 步，累计 +9。", 3.0), Beat("所以只保留连续的前 1 步——", 2.2), Beat("从本轮起点重来：只做 A↔D，cut = 3。", 3.8), Beat("这就是回退：试探可以变差，接受只看最佳前缀。", 3.6)], chapter="五 · 最佳前缀与回退"),
    Scene("s08-pass2", s_pass2, [Beat("从 ABC | DE 再来一轮。", 2.4), Beat("累计收益：−8，然后 −6。", 3.0), Beat("都不如什么都不做：空前缀胜出，算法停止。", 3.6)]),
    Scene("s09-code", s_code, [Beat("把规则写成伪代码：外层一轮接一轮。", 3.0), Beat("内层：选最大收益的一对，交换、锁定、更新 D。", 3.6), Beat("一轮结束：取最佳前缀，从起点只应用这几步。", 3.6), Beat("直到最佳前缀为空。", 2.4)], chapter="六 · 伪代码与局限"),
    Scene("s10-ab1", s_ab1, [Beat("换一张图：把 AB 从 5 改成 1。", 2.6), Beat("初始 cut 变成 8，A↔D 的收益变成 5。", 3.4), Beat("同一个种子，图一变，所有 D 值都要重算。", 3.2)]),
    Scene("s11-limits", s_limits, [Beat("KL 的边界：", 1.6), Beat("人数平衡不等于面积平衡。", 2.6), Beat("从不同种子出发，结果可能不同。", 2.6), Beat("下一章 FM：一次只移动一个点。", 3.2)], tail=1.2),
]
POSTER_AT = 75.0
