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


def g5(ab=None):
    g = fixture("five_node.json")
    edges = [tuple(e) for e in g["edges"]]
    if ab is not None:
        edges = [(u, v, ab if (u, v) == ("A", "B") else w) for u, v, w in edges]
    return g["nodes"], edges


def c_first(impl):
    nodes, edges = g5()
    s = impl.best_swap(impl._adj(nodes, edges), SEED, set())
    expect((s["a"], s["b"], s["gain"]) == ("A", "D", 9), T(f"首对应为 A↔D 收益 9，得到 {s}", f"the first pair should be A↔D with gain 9; got {s}"))
    expect((s["Da"], s["Db"]) == (6, 3), T("D(A)=6（外 6 内 0），D(D)=3（外 5 内 2）", "D(A)=6 (external 6, internal 0), D(D)=3 (external 5, internal 2)"))


def c_trial(impl):
    nodes, edges = g5()
    p = impl.kl_pass(nodes, edges, SEED)
    expect([s["gain"] for s in p["swaps"]] == [9, -8], T(f"第一轮试探收益应为 9, −8，得到 {[s['gain'] for s in p['swaps']]}", f"pass 1 trial gains should be 9, −8; got {[s['gain'] for s in p['swaps']]}"))
    expect(p["swaps"][1]["cut_after"] == 11, T("第二步试探后 cut 暂时升到 11——这是试探，不是接受", "after the second trial swap the cut rises to 11 for now: a trial, not an acceptance"))
    expect(p["best_k"] == 1 and p["accepted_cut"] == 3, T("累计 9, 1：保留前 1 步，接受 cut 3", "cumulative 9, 1: keep the first step, accept cut 3"))


def c_empty(impl):
    expect(impl.best_prefix([-8, 2]) == (0, 0), T("累计 −8, −6：选空前缀 (0, 0)", "cumulative −8, −6: choose the empty prefix (0, 0)"))
    expect(impl.best_prefix([9, -8]) == (1, 9), T("累计 9, 1：选 (1, 9)", "cumulative 9, 1: choose (1, 9)"))
    expect(impl.best_prefix([3, -3, 3]) == (1, 3), T("累计 3, 0, 3：并列最大时保留更短的前缀（本课程约定），应为 (1, 3)", "cumulative 3, 0, 3: on a tie keep the shorter prefix (this course's convention), so (1, 3)"))
    nodes, edges = g5()
    r = impl.kernighan_lin(nodes, edges, SEED)
    expect(len(r["passes"]) == 2 and r["passes"][1]["best_k"] == 0, T("第二轮最佳前缀为空，算法停止", "pass 2's best prefix is empty, so the algorithm stops"))
    expect(r["cut"] == 3, T("最终 cut 3", "final cut 3"))


def c_ab1(impl):
    nodes, edges = g5(ab=1)
    expect(impl.cut(edges, SEED) == 8, T("AB 改为 1 后初始 cut 为 8", "with AB set to 1 the initial cut is 8"))
    s = impl.best_swap(impl._adj(nodes, edges), SEED, set())
    expect(s["gain"] == 5 and (s["a"], s["b"]) == ("A", "D"), T(f"AB=1 时 g(A,D) = 5，得到 {s}", f"with AB=1, g(A,D) = 5; got {s}"))


def c_random(impl):
    rnd = random.Random(20261023)
    for case in range(120):
        n = rnd.choice([4, 5, 6])
        nodes = [chr(65 + i) for i in range(n)]
        edges = [(u, v, rnd.randint(1, 9)) for u, v in itertools.combinations(nodes, 2) if rnd.random() < 0.55]
        ids = nodes[:]
        rnd.shuffle(ids)
        side = {v: (0 if i < n // 2 else 1) for i, v in enumerate(ids)}
        p = impl.kl_pass(nodes, edges, side)
        sizes = (sum(1 for v in nodes if p["accepted"][v] == 0), sum(1 for v in nodes if p["accepted"][v] == 1))
        expect(sizes == (n // 2, n - n // 2), T(f"案例 {case}：两侧节点数必须保持", f"case {case}: the node count on each side must stay the same"))
        used = [x for s in p["swaps"] for x in (s["a"], s["b"])]
        expect(len(used) == len(set(used)), T(f"案例 {case}：每个节点每轮最多交换一次（锁定）", f"case {case}: each node swaps at most once per pass (locking)"))
        for s in p["swaps"]:
            expect(s["cut_before"] - s["cut_after"] == s["gain"], T(f"案例 {case}：收益必须等于交换前后 cut 之差", f"case {case}: the gain must equal the cut before minus the cut after"))
        expect(impl.cut(edges, side) - p["accepted_cut"] == p["best_gain"], T(f"案例 {case}：接受的 cut 下降 = 最佳累计收益", f"case {case}: the accepted drop in cut = the best cumulative gain"))


CHECKS = [
    (T("[推演] 最大收益对：A↔D = 9", "[trace] largest-gain pair: A↔D = 9"), c_first),
    (T("[解释] 负收益也要试探：cut 暂升 11", "[explain] negative gains are tried too: the cut rises to 11 for now"), c_trial),
    (T("[决策] 最佳前缀与空前缀", "[decide] the best prefix and the empty prefix"), c_empty),
    (T("[推演] AB=1：初始 cut 8，g(A,D)=5", "[trace] AB=1: initial cut 8, g(A,D)=5"), c_ab1),
    (T("[实现] 120 个随机图：基数、锁定、收益=cut 差", "[implement] 120 random graphs: side sizes, locking, gain = cut difference"), c_random),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
