# ---- 自包含检查框架（每个练习包各复制一份，不依赖外部 common/）----
# Self-contained checker framework (copied into every pack). Language: --lang en or COURSE_LANG=en.
# --json prints one machine-readable line (used by the in-browser code lab).
import importlib.util
import json
import os
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
LANG = "en" if ("--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1:][:1] == ["en"]) or os.environ.get("COURSE_LANG") == "en" else "zh"
JSON_MODE = "--json" in sys.argv


def T(zh, en):
    """Pick the message for the current language."""
    return en if LANG == "en" else zh


def load_impl(argv):
    args = [a for i, a in enumerate(argv[1:], 1) if not a.startswith("--") and argv[i - 1] != "--lang"]
    target = Path(args[0]) if args else HERE / "starter.py"
    if not target.is_absolute():
        target = (Path.cwd() / target).resolve()
    spec = importlib.util.spec_from_file_location("impl", target)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return target, mod


def fixture(name):
    return json.loads((HERE / "fixtures" / name).read_text(encoding="utf-8"))


class Fail(Exception):
    pass


class Skip(Exception):
    """可选检查因环境缺少依赖而未运行；不计为通过。 / An optional check did not run; it does not count as a pass."""


def expect(cond, message):
    if not cond:
        raise Fail(message)


def run_one(fn, impl):
    try:
        fn(impl)
        return "PASS", ""
    except NotImplementedError as e:
        return "INCOMPLETE", (T(f"尚未实现：{e}", f"not implemented yet: {e}") if str(e) else T("尚未实现", "not implemented yet"))
    except Skip as e:
        return "SKIP", str(e)
    except Fail as e:
        return "FAIL", str(e)
    except Exception as e:  # 代码本身抛错，给出最后一行位置 / the code itself raised: show where
        tb = traceback.extract_tb(e.__traceback__)[-1]
        return "ERROR", f"{type(e).__name__}: {e} ({Path(tb.filename).name}:{tb.lineno})"


def run_checks(checks, argv=sys.argv):
    target, impl = load_impl(argv)
    results = []
    for name, fn in checks:
        status, note = run_one(fn, impl)
        results.append({"name": name, "status": status, "note": note})
    counts = {k: sum(r["status"] == k for r in results) for k in ("PASS", "FAIL", "INCOMPLETE", "ERROR", "SKIP")}
    ok = counts["PASS"] + counts["SKIP"] == len(checks) and counts["PASS"] > 0
    if JSON_MODE:
        print("@@CHECK@@" + json.dumps({"results": results, "counts": counts, "ok": ok}, ensure_ascii=False))
        return 0 if ok else 1
    print(T(f"检查对象：{target.name}", f"Checking: {target.name}"))
    for r in results:
        print(f"{r['status']:<10} {r['name']}" + (f"\n           {r['note']}" if r["note"] else ""))
    print(T("—— 合计：", "—— Total: ") + T("，", ", ").join(f"{k} {v}" for k, v in counts.items()))
    if counts["INCOMPLETE"]:
        print(T("INCOMPLETE 不等于通过：补全对应函数后再运行。", "INCOMPLETE is not a pass: finish the function and run again."))
    if counts["SKIP"]:
        print(T("SKIP 表示该项没有运行（缺少可选依赖），不是通过。", "SKIP means the check did not run (an optional dependency is missing); it is not a pass."))
    return 0 if ok else 1
# ---- 框架结束 ----
import itertools
import random

SEED = {"A": 0, "B": 1, "C": 1, "D": 1, "E": 0}


def c_legal(impl):
    g = fixture("five_node.json")
    legal = impl.legal_moves(SEED, set(), 1)
    expect("A" not in legal and "E" not in legal, T("A、E 在只有 2 人的一侧，移走会违反平衡", "A and E are on the side with only 2 nodes; moving either breaks the balance"))
    expect(legal == ["B", "C", "D"], T(f"合法候选应为 B、C、D，得到 {legal}", f"the legal candidates should be B, C, D; got {legal}"))


def c_fs_te(impl):
    nets = impl.to_nets(fixture("five_node.json"))
    g, fs, te = impl.gain(nets, SEED, "D")
    expect(g == 3 and fs == ["DE"] and te == ["CD"], T(f"D：FS=DE(5)，TE=CD(2)，gain 3；得到 {g} {fs} {te}", f"D: FS=DE(5), TE=CD(2), gain 3; got {g} {fs} {te}"))
    after = {**SEED, "D": 0}
    expect(impl.gain(nets, after, "A")[0] == 6, T("D 移过去之后 A 的 gain 是 6，且此时合法", "after D moves, A’s gain is 6 and A is now legal"))


def c_pass(impl):
    p = impl.fm_pass(fixture("five_node.json"), SEED, 1)
    seq = [(m["node"], m["gain"], m["cut_after"]) for m in p["trial_moves"]]
    want = [("D", 3, 9), ("A", 6, 3), ("C", -2, 5), ("E", -6, 11), ("B", -1, 12)]
    expect(seq == want, T(f"首轮试探应为 {want}，得到 {seq}", f"pass 1’s trials should be {want}; got {seq}"))
    expect(p["best_prefix"] == 2 and p["accepted_cut"] == 3, T("累计 3,9,7,1,0：k*=2，接受 cut 3，而不是最后的 12", "cumulative 3,9,7,1,0: k*=2, accept cut 3, not the final 12"))


def c_refine(impl):
    r = impl.fm_refine(fixture("five_node.json"), SEED, 1)
    expect(r["cut"] == 3 and r["stop_reason"] == "no-positive-prefix" and len(r["passes"]) == 2, T("第二轮无正前缀即停止", "pass 2 has no positive prefix, so the algorithm stops"))


def c_legacy(impl):
    h = fixture("legacy_hillclimb.json")
    nets = impl.to_nets(h)
    expect(impl.net_cut(nets, h["seed"]) == 18, T("原附件说初始 cut 9，实际为 18", "the attachment says the initial cut is 9; it is 18"))
    gains = {v: impl.gain(nets, h["seed"], v)[0] for v in impl.legal_moves(h["seed"], set(), h["max_diff"])}
    expect(gains.get("E") == 10, T(f"原附件说所有合法 gain ≤ 0，实际 E 合法且 gain +10：{gains}", f"the attachment says every legal gain is ≤ 0; in fact E is legal with gain +10: {gains}"))
    p = impl.fm_pass(h, h["seed"], h["max_diff"])
    expect(p["accepted_cut"] == 8, T("首轮最佳 cut 8，而不是原文的 4", "pass 1’s best cut is 8, not the 4 the text claims"))


def c_escape(impl):
    h = fixture("neg_escape.json")
    nets = impl.to_nets(h)
    gains = [impl.gain(nets, h["seed"], v)[0] for v in impl.legal_moves(h["seed"], set(), h["max_diff"])]
    expect(max(gains) <= 0, T("替换反例：初始所有合法移动 gain ≤ 0（只走正收益的爬山会停在 cut 6）", "replacement example: at the start every legal move has gain ≤ 0 (hill climbing on positive gains stops at cut 6)"))
    p = impl.fm_pass(h, h["seed"], h["max_diff"])
    expect([m["gain"] for m in p["trial_moves"][:3]] == [-1, -1, 4], T("FM 先接受 −1、−1，再得到 +4", "FM takes −1, −1, then gets +4"))
    expect(p["best_prefix"] == 3 and p["accepted_cut"] == 4, T("保留前 3 步，cut 6 → 4", "keep the first 3 steps: cut 6 → 4"))
    best = min(impl.net_cut(nets, dict(zip(sorted(h["seed"]), bits)))
               for bits in itertools.product([0, 1], repeat=6) if impl.balance_ok(dict(zip(sorted(h["seed"]), bits)), 2))
    expect(best == 4, T("穷举核验：平衡最优 cut 就是 4", "exhaustive check: the balanced optimum is cut 4"))


def c_multipin(impl):
    g = {"nodes": ["A", "B", "C", "D"], "nets": [{"id": "bus", "pins": ["A", "B", "C"], "w": 2}, {"id": "n2", "pins": ["C", "D"], "w": 1}]}
    nets = impl.to_nets(g)
    side = {"A": 0, "B": 0, "C": 1, "D": 1}
    expect(impl.gain(nets, side, "C")[0] == 1, T("C 是 bus 在 1 侧唯一引脚：+2；n2 在 0 侧无引脚：−1；gain 1", "C is bus’s only pin on side 1: +2; n2 has no pin on side 0: −1; gain 1"))
    expect(impl.gain(nets, side, "A")[0] == 0, T("A 移走后 bus 两侧仍各有引脚：gain 0（不能把 3 引脚 net 拆成边来算）", "after A moves, bus still has pins on both sides: gain 0 (don’t split a 3-pin net into edges)"))


def c_random(impl):
    rnd = random.Random(8)
    for case in range(150):
        n = rnd.choice([4, 5, 6, 7])
        nodes = [chr(65 + i) for i in range(n)]
        g = {"nodes": nodes, "edges": [(u, v, rnd.randint(1, 9)) for u, v in itertools.combinations(nodes, 2) if rnd.random() < 0.5]}
        if rnd.random() < 0.4:
            g["nets"] = [{"id": f"m{i}", "pins": rnd.sample(nodes, 3), "w": rnd.randint(1, 4)} for i in range(2)]
        side = {v: rnd.randint(0, 1) for v in nodes}
        if not impl.balance_ok(side, 1):
            continue
        p = impl.fm_pass(g, side, 1)
        for m in p["trial_moves"]:
            expect(m["cut_before"] - m["cut_after"] == m["gain"], T(f"案例 {case}：gain 必须等于移动前后 cut 之差", f"case {case}: the gain must equal the cut before minus the cut after"))
        expect(len({m["node"] for m in p["trial_moves"]}) == len(p["trial_moves"]), T(f"案例 {case}：每点每轮最多移动一次", f"case {case}: each node moves at most once per pass"))
        expect(impl.balance_ok(p["accepted"], 1), T(f"案例 {case}：接受的二分必须平衡", f"case {case}: the accepted bisection must be balanced"))


CHECKS = [
    (T("[合法性] 为什么不选 A：平衡窗口", "[legality] why not A: the balance window"), c_legal),
    (T("[推演] D 的 FS/TE 与 gain", "[trace] D’s FS/TE and gain"), c_fs_te),
    (T("[回退] 首轮试探与 k*=2", "[roll back] pass 1’s trials and k*=2"), c_pass),
    (T("[回退] 第二轮空前缀停止", "[roll back] pass 2’s empty prefix stops"), c_refine),
    (T("[纠错] 审查原 hillclimb 说明", "[debug] audit the original hillclimb claim"), c_legacy),
    (T("[探索] 替换反例：先负后正", "[explore] the replacement: negative first, then positive"), c_escape),
    (T("[拓展] 多引脚 net 的 gain", "[extension] the gain on a multi-pin net"), c_multipin),
    (T("[实现] 150 个随机图：gain = cut 差、锁定、平衡", "[implement] 150 random graphs: gain = cut difference, locks, balance"), c_random),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
