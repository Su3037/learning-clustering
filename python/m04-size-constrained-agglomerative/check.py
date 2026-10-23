# ---- 自包含检查框架（每个练习包各复制一份，不依赖外部 common/）----
import importlib.util
import json
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_impl(argv):
    target = Path(argv[1]) if len(argv) > 1 else HERE / "starter.py"
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
    """可选检查因环境缺少依赖而未运行；不计为通过。"""


def expect(cond, message):
    if not cond:
        raise Fail(message)


def run_checks(checks, argv=sys.argv):
    target, impl = load_impl(argv)
    print(f"检查对象：{target.name}")
    counts = {"PASS": 0, "FAIL": 0, "INCOMPLETE": 0, "ERROR": 0, "SKIP": 0}
    for name, fn in checks:
        try:
            fn(impl)
            status, note = "PASS", ""
        except NotImplementedError as e:
            status, note = "INCOMPLETE", f"尚未实现：{e}" if str(e) else "尚未实现"
        except Skip as e:
            status, note = "SKIP", str(e)
        except Fail as e:
            status, note = "FAIL", str(e)
        except Exception as e:  # 代码本身抛错，给出最后一行位置
            tb = traceback.extract_tb(e.__traceback__)[-1]
            status, note = "ERROR", f"{type(e).__name__}: {e}（{Path(tb.filename).name}:{tb.lineno}）"
        counts[status] += 1
        print(f"{status:<10} {name}" + (f"\n           {note}" if note else ""))
    print("—— 合计：" + "，".join(f"{k} {v}" for k, v in counts.items()))
    if counts["INCOMPLETE"]:
        print("INCOMPLETE 不等于通过：补全对应函数后再运行。")
    if counts["SKIP"]:
        print("SKIP 表示该项没有运行（缺少可选依赖），不是通过。")
    return 0 if counts["PASS"] + counts["SKIP"] == len(checks) and counts["PASS"] > 0 else 1
# ---- 框架结束 ----


def s(impl, name, k, cap):
    return impl.solve(fixture(name), k, cap)


def j(parts):
    return sorted("".join(sorted(p)) for p in parts)


def c_cap2(impl):
    r = s(impl, "five_node.json", 2, 2)
    expect(j(r["clusters"]) == ["AB", "C", "DE"] and r["cutsize"] == 8, f"原图 K2 C2 应得 AB|C|DE cut8，得到 {r['clusters']}")
    expect(r["capacity_compliant"] is True, "每簇都 ≤ 2：capacity_compliant 应为 True")
    expect(r["target_reached"] is False, "只有 3 簇：target_reached 应为 False")
    expect(r["count"] == 3 and r["stop_reason"] == "capacity-blocked", f"应报告 3 簇、capacity-blocked，得到 {r.get('count')}、{r.get('stop_reason')}")


def c_cap3(impl):
    r = s(impl, "five_node.json", 2, 3)
    expect(j(r["clusters"]) == ["ABC", "DE"] and r["target_reached"], "K2 C3 应得 ABC|DE 并达到 K")


def c_k3(impl):
    r = s(impl, "five_node.json", 3, 2)
    expect(r["target_reached"] and r["cutsize"] == 8, "K3 C2：同样的 AB|C|DE 这次达到了 K")


def c_classes(impl):
    got = {
        "原图 K2 C2": impl.classify(fixture("five_node.json"), 2, 2),
        "greedy_trap K2 C3": impl.classify(fixture("greedy_trap.json"), 2, 3),
        "suboptimal K2 C2": impl.classify(fixture("suboptimal.json"), 2, 2),
    }
    want = {"原图 K2 C2": "infeasible-by-bound", "greedy_trap K2 C3": "greedy-stuck", "suboptimal K2 C2": "feasible-suboptimal"}
    for key in want:
        expect(got[key] == want[key], f"{key} 应为 {want[key]}，得到 {got[key]}")


def c_oracle(impl):
    o = impl.oracle(fixture("greedy_trap.json"), 2, 3)
    expect(o["best_cut_at_k"][0] == 10, "greedy_trap 穷举存在 2 簇合法划分 AC|BD，cut 10")
    o = impl.oracle(fixture("suboptimal.json"), 2, 2)
    expect(o["best_cut_at_k"][0] == 11, "suboptimal 穷举最优 cut 11，贪心得 18")


def c_edge_cases(impl):
    r = impl.solve({"nodes": ["A", "B"], "sizes": {"A": 3}, "edges": [("A", "B", 1)]}, 1, 2)
    expect(r["capacity_compliant"] is False and r["stop_reason"] == "invalid-input", "单点已超容量：应报告 invalid-input，不做非法合并")
    r = impl.solve({"nodes": ["A", "B", "C"], "edges": []}, 1, 5)
    expect(r["stop_reason"] == "no-positive-affinity" and r["count"] == 3, "无边图：没有正亲和度对，停在 3 簇")


CHECKS = [
    ("[概念] 合法与目标不同：cap2 的 3 簇结果", c_cap2),
    ("[推演] cap3 达到 K", c_cap3),
    ("[推演] K3 C2 同一分组达到 K", c_k3),
    ("[工具] 已提供的 oracle：trap 10，suboptimal 11", c_oracle),
    ("[探索] 三种情况的分类", c_classes),
    ("[约束] 超容量单点与无边图", c_edge_cases),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
