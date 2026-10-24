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


def c_cycle(impl):
    try:
        impl.topological_order(["A", "B", "C"], [("A", "B"), ("B", "C"), ("C", "A")])
    except ValueError:
        pass
    else:
        raise Fail(T("有环输入必须报错", "an input with a cycle must raise an error"))
    expect(impl.topological_order(["P", "X", "Y", "O"], [("P", "X"), ("X", "Y"), ("Y", "O")]) == ["P", "X", "Y", "O"], T("链的拓扑序", "the chain's topological order"))


def c_delta(impl):
    g = fixture("candidate_dag.json")
    d = impl.longest_node_delays(g["nodes"], [tuple(e) for e in g["edges"]], {v: 1 for v in g["nodes"]})
    expect(d["b"]["k"] == 4 and d["a"]["k"] == 3 and d["a"]["e"] is None, T(f"Δ[b][k]=4、Δ[a][k]=3、a 到不了 e；得到 {d['b']['k']}, {d['a']['k']}, {d['a']['e']}", f"Δ[b][k]=4, Δ[a][k]=3, a cannot reach e; got {d['b']['k']}, {d['a']['k']}, {d['a']['e']}"))


def chain_instances(groups, D=3):
    where = {v: i for i, grp in enumerate(groups) for v in grp}
    inst = {v: v for v in "PXYO"}
    edges = [(a, b, 0 if where[a] == where[b] else D) for a, b in [("P", "X"), ("X", "Y"), ("Y", "O")]]
    return inst, edges


def c_chain(impl):
    inst, e = chain_instances([["P", "X"], ["Y", "O"]])
    t = impl.evaluate_instance_delay(inst, e, {v: 1 for v in "PXYO"})
    expect(t["O"] == 7, T(f"一次跨簇：4 个节点延迟 + 一次 D=3，共 7；得到 {t['O']}", f"one crossing: 4 node delays + one D=3, 7 in all; got {t['O']}"))
    inst, e = chain_instances([["P"], ["X", "Y"], ["O"]])
    t = impl.evaluate_instance_delay(inst, e, {v: 1 for v in "PXYO"})
    expect(t["O"] == 10, T(f"两次跨簇：4 + 3 + 3 = 10；得到 {t['O']}", f"two crossings: 4 + 3 + 3 = 10; got {t['O']}"))


def c_labels(impl):
    g = fixture("candidate_dag.json")
    label, cluster, steps = impl.rw_label(g)
    want = {"a": 1, "b": 1, "c": 1, "d": 2, "e": 2, "f": 2, "g": 3, "h": 2, "i": 7, "j": 7, "k": 8, "l": 8}
    expect(label == want, T(f"候选图的标签应为 {want}，得到 {label}", f"the candidate graph's labels should be {want}; got {label}"))
    expect(sorted(cluster["k"]) == ["g", "i", "j", "k"], T("k 的候选簇为 {g,i,j,k}（容量 4）", "k's candidate cluster is {g,i,j,k} (capacity 4)"))


def c_reconstruct(impl):
    g = fixture("candidate_dag.json")
    r = impl.rajaraman_wong(g)
    expect(len(r["clusters"]) == 8 and len(r["instances"]) == 20, T(f"在所述平票假设下应得 8 簇、20 个实例，得到 {len(r['clusters'])}、{len(r['instances'])}", f"under the stated tie assumption there should be 8 clusters and 20 instances; got {len(r['clusters'])}, {len(r['instances'])}"))
    expect(r["output_delay"] == {"k": 8, "l": 8}, T(f"输出延迟应为 k=8、l=8，得到 {r['output_delay']}", f"the output delays should be k=8, l=8; got {r['output_delay']}"))
    logical = {}
    for inst, m in r["instances"].items():
        logical.setdefault(m, []).append(inst)
    expect(len(logical["b"]) == 3, T("逻辑节点 b 有 3 个实例：一个逻辑 id 可以对应多个物理实例", "logical node b has 3 instances: one logical id can map to several physical instances"))
    preds = {v: sorted(u for u, w in g["edges"] if w == v) for v in g["nodes"]}
    for inst, m in r["instances"].items():
        got = sorted(r["instances"][a] for a, b, _ in r["instance_edges"] if b == inst)
        expect(got == preds[m], T(f"实例 {inst} 的输入必须完整：需要 {preds[m]}，得到 {got}", f"instance {inst} must have all its inputs: needs {preds[m]}, got {got}"))


CHECKS = [
    (T("[基础] 拓扑序；有环输入报错", "[basic] topological order; a cycle raises an error"), c_cycle),
    (T("[基础] 最长节点延迟 Δ", "[basic] longest node delay Δ"), c_delta),
    (T("[推演] 链：一次跨界 7，两次 10", "[trace] the chain: one crossing 7, two crossings 10"), c_chain),
    (T("[进阶] 标记阶段：候选图标签", "[advanced] labelling: the candidate graph's labels"), c_labels),
    (T("[进阶] 恢复与复制：8 簇、20 实例、输出 8、fanin 完整", "[advanced] recovery and replication: 8 clusters, 20 instances, output 8, complete fan-in"), c_reconstruct),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
