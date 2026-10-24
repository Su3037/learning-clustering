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


def g5():
    g = fixture("five_node.json")
    return g["nodes"], g["edges"]


def groups(labels):
    d = {}
    for n, l in labels.items():
        d.setdefault(l, []).append(n)
    return sorted("".join(sorted(v)) for v in d.values())


def c_votes(impl):
    nodes, edges = g5()
    adj = impl.build_adjacency(nodes, edges)
    v = impl.count_votes(adj, {"A": "B", "B": "B", "C": "C", "D": "D", "E": "E"}, "C")
    expect(v == {"B": 5, "D": 2, "E": 1}, T(f"C 的票应为 B=5、D=2、E=1（按权重），得到 {v}", f"C's votes should be B=5, D=2, E=1 (by weight); got {v}"))


def c_golden(impl):
    nodes, edges = g5()
    r = impl.solve(nodes, edges)
    expect(r["labels"] == {"A": "B", "B": "B", "C": "B", "D": "E", "E": "E"}, T(f"A→E 异步 min 应得 B/B/B/E/E，得到 {r['labels']}", f"A→E asynchronous with min ties should give B/B/B/E/E; got {r['labels']}"))
    expect(r["rounds"] == 2 and r["status"] == "stable", T(f"两轮（含零变化确认轮）后 stable，得到 {r['rounds']} 轮、{r['status']}", f"stable after 2 rounds (including the zero-change round); got {r['rounds']} rounds, {r['status']}"))
    expect(r["cut"] == 3, T("cut 应为 3", "cut should be 3"))


def c_cycle(impl):
    r = impl.solve(["A", "B"], [("A", "B", 1)], mode="sync")
    expect(r["status"] == "cycle", T(f"两节点同步更新会来回交换：应报告 cycle 而不是 stable/limit，得到 {r['status']}", f"two nodes updated synchronously swap back and forth: report cycle, not stable/limit; got {r['status']}"))
    r = impl.solve(["A", "B"], [("A", "B", 1)], mode="async")
    expect(r["status"] == "stable", T("同一图异步更新会统一并 stable", "the same graph updated asynchronously agrees and is stable"))


def c_bridge(impl):
    nodes, edges = g5()
    heavy = [(u, v, 10 if {u, v} == {"C", "D"} else w) for u, v, w in edges]
    r = impl.solve(nodes, heavy)
    expect(r["cut"] == 5, T(f"把 C–D 改成 10 后重新运行，cut 应为 5，得到 {r['cut']}", f"with C–D set to 10 and a fresh run, the cut should be 5; got {r['cut']}"))


def c_order(impl):
    nodes, edges = g5()
    a = impl.solve(nodes, edges)
    b = impl.solve(nodes, edges, order=["E", "D", "C", "B", "A"])
    expect(groups(a["labels"]) == groups(b["labels"]), T("反向顺序在这张图上分组相同（标签名可以不同）", "reverse order gives the same grouping on this graph (label names may differ)"))
    expect(b["rounds"] == 3, T(f"但轮数变为 3，得到 {b['rounds']}", f"but it takes 3 rounds; got {b['rounds']}"))


def c_edges(impl):
    r = impl.solve(["A", "B", "C"], [], max_iters=5)
    expect(r["status"] == "stable" and r["rounds"] == 1, T("无边图：一轮确认零变化即 stable", "a graph without edges is stable after one zero-change round"))
    r = impl.solve(["A", "B", "C", "D"], [("A", "B", 1), ("A", "C", 1), ("A", "D", 4)], tie="max")
    expect(r["status"] in ("stable", "cycle"), T("平票图应正常结束", "the tie graph should finish normally"))
    r = impl.solve(["A", "B"], [("A", "B", 1)], mode="sync", max_iters=1)
    expect(r["status"] == "limit", T(f"上限 1 轮且尚未重复：应报告 limit，得到 {r['status']}", f"cap of 1 round and no repeat yet: report limit; got {r['status']}"))


def c_film(impl):
    for name, rounds, cut in [("circuit.json", 5, 2), ("contacts.json", 3, 4)]:
        g = fixture(name)
        r = impl.solve(g["nodes"], [tuple(e) for e in g["edges"]])
        expect(r["rounds"] == rounds and r["cut"] == cut, T(f"{name}：应 {rounds} 轮、cut {cut}，得到 {r['rounds']} 轮、cut {r['cut']}", f"{name}: expected {rounds} rounds, cut {cut}; got {r['rounds']} rounds, cut {r['cut']}"))


CHECKS = [
    (T("[推演] C 的票数：B=5、D=2、E=1", "[Trace] C’s votes: B=5, D=2, E=1"), c_votes),
    (T("[推演] 默认：B/B/B/E/E，两轮，cut 3", "[Trace] Default: B/B/B/E/E, 2 rounds, cut 3"), c_golden),
    (T("[探索] 同步双点振荡 = cycle", "[Explore] Two nodes, synchronous = cycle"), c_cycle),
    (T("[探索] C–D=10 重新运行 cut 5", "[Explore] C–D = 10, fresh run: cut 5"), c_bridge),
    (T("[探索] 反向顺序：同分组、3 轮", "[Explore] Reverse order: same groups, 3 rounds"), c_order),
    (T("[实现] 停止状态：孤点、平票、上限", "[Implement] Stopping: isolated nodes, ties, the cap"), c_edges),
    (T("[应用] 24 单元与联系人图", "[Apply] The 24-cell circuit and the contact graph"), c_film),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
