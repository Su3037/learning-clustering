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


def run_cfg(impl, k, cap, g=None, sizes=None):
    g = g or fixture("five_node.json")
    return impl.greedy_pair_merge(g["nodes"], g["edges"], k, cap, sizes)


def norm(parts):
    return sorted("".join(sorted(p)) for p in parts)


def c_key(impl):
    c10 = {"a": ("A",), "b": ("B",), "affinity": 10, "size": 2, "legal": True}
    c2 = {"a": ("A",), "b": ("C",), "affinity": 2, "size": 2, "legal": True}
    c25 = {"a": ("B",), "b": ("C",), "affinity": 2.5, "size": 2, "legal": True}
    expect(min([c2, c10], key=impl.selection_key) is c10, T("亲和度 10 应胜过 2（数值比较，不是字符串比较）", "affinity 10 should beat 2 (compare numbers, not strings)"))
    expect(min([c2, c25], key=impl.selection_key) is c25, T("亲和度 2.5 应胜过 2（小数）", "affinity 2.5 should beat 2 (decimals)"))
    t1 = {"a": ("A", "B"), "b": ("C",), "affinity": 5, "size": 3, "legal": True}
    t2 = {"a": ("D",), "b": ("E",), "affinity": 5, "size": 2, "legal": True}
    expect(min([t2, t1], key=impl.selection_key) is t1, T("AB–C 与 D–E 同为 5 时，按成员 A < D 选 AB–C", "when AB–C and D–E are both 5, members A < D pick AB–C"))


def c_k2(impl):
    r = run_cfg(impl, 2, None)
    expect(norm(r["parts"]) == ["ABC", "DE"], T(f"K=2 无容量应得 ABC|DE，得到 {r['parts']}", f"K=2 with no capacity should give ABC|DE; got {r['parts']}"))
    traj = [e["cutsize"] for e in r["log"]]
    expect(traj == [18, 13, 8, 3], T(f"cut 轨迹应为 18→13→8→3，得到 {traj}", f"the cut path should be 18→13→8→3; got {traj}"))
    expect(r["target_reached"] and r["stop_reason"] == "target-reached", T("应报告达到 K", "should report that K is reached"))


def c_k3(impl):
    r = run_cfg(impl, 3, None)
    expect(norm(r["parts"]) == ["ABC", "D", "E"] and r["cutsize"] == 8, T(f"K=3 应得 ABC|D|E cut8，得到 {r['parts']} cut{r['cutsize']}", f"K=3 should give ABC|D|E cut 8; got {r['parts']} cut {r['cutsize']}"))


def c_cap2(impl):
    r = run_cfg(impl, 2, 2)
    expect(norm(r["parts"]) == ["AB", "C", "DE"] and r["cutsize"] == 8, T(f"cap2 应得 AB|C|DE cut8，得到 {r['parts']} cut{r['cutsize']}", f"cap2 should give AB|C|DE cut 8; got {r['parts']} cut {r['cutsize']}"))
    expect(r["target_reached"] is False, T("cap2 只得到 3 簇：target_reached 必须为 False，不能强行凑 K", "cap2 gives only 3 clusters: target_reached must be False; never force K"))
    expect(r["stop_reason"] == "capacity-blocked", T(f"停止原因应为 capacity-blocked，得到 {r['stop_reason']}", f"the stop reason should be capacity-blocked; got {r['stop_reason']}"))


def c_cap3(impl):
    r = run_cfg(impl, 2, 3)
    expect(norm(r["parts"]) == ["ABC", "DE"] and r["cutsize"] == 3, T("cap3 应得 ABC|DE cut3", "cap3 should give ABC|DE cut 3"))


def c_drop(impl):
    g = {"nodes": ["P", "Q", "R", "S", "T", "U"],
         "edges": [("P", "Q", 10), ("Q", "R", 2), ("R", "S", 9), ("S", "T", 1.5), ("T", "U", 10), ("P", "U", 2)]}
    r = run_cfg(impl, 2, None, g)
    for prev, cur in zip(r["log"], r["log"][1:]):
        expect(abs((prev["cutsize"] - cur["cutsize"]) - cur["weight"]) < 1e-9, T(f"第 {cur['step']} 步 cut 下降应等于该次亲和度 {cur['weight']}", f"at step {cur['step']} the cut should drop by that merge's affinity, {cur['weight']}"))
    first = r["log"][1]["pair"]
    expect(first == "P-Q", T(f"多位数权重：第一步应合并 P-Q@10（10 > 9 > 2），得到 {first}", f"multi-digit weights: step 1 should merge P-Q@10 (10 > 9 > 2); got {first}"))
    members = "".join(r["parts"])
    expect(sorted(members) == sorted(g["nodes"]), T("每个节点恰好属于一个簇", "every node belongs to exactly one cluster"))


def c_disconnected(impl):
    g = {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B", 1)]}
    r = run_cfg(impl, 1, None, g)
    expect(r["stop_reason"] == "no-positive-affinity" and not r["target_reached"], T("图不连通时剩下的簇之间没有正亲和度：应停在 no-positive-affinity", "in a disconnected graph no positive affinity remains between clusters: it should stop with no-positive-affinity"))


CHECKS = [
    (T("[实现] 选择键：10>2、2.5>2、成员平票", "[Implement] Selection key: 10>2, 2.5>2, member ties"), c_key),
    (T("[推演] K=2：ABC|DE，轨迹 18→13→8→3", "[Trace] K=2: ABC|DE, path 18→13→8→3"), c_k2),
    (T("[推演] K=3：ABC|D|E，cut 8", "[Trace] K=3: ABC|D|E, cut 8"), c_k3),
    (T("[约束] cap2：3 簇、cut 8、未达到 K", "[Constraint] cap2: 3 clusters, cut 8, K not reached"), c_cap2),
    (T("[约束] cap3：ABC|DE，cut 3", "[Constraint] cap3: ABC|DE, cut 3"), c_cap3),
    (T("[实现] 每步 cut 下降 = 亲和度；多位数权重", "[Implement] Each cut drop = affinity; multi-digit weights"), c_drop),
    (T("[约束] 无合法正亲和度对时停止", "[Constraint] Stop when no legal positive pair remains"), c_disconnected),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
