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


def run_cfg(impl, k, cap, g=None, sizes=None):
    g = g or fixture("five_node.json")
    return impl.greedy_pair_merge(g["nodes"], g["edges"], k, cap, sizes)


def norm(parts):
    return sorted("".join(sorted(p)) for p in parts)


def c_key(impl):
    c10 = {"a": ("A",), "b": ("B",), "affinity": 10, "size": 2, "legal": True}
    c2 = {"a": ("A",), "b": ("C",), "affinity": 2, "size": 2, "legal": True}
    c25 = {"a": ("B",), "b": ("C",), "affinity": 2.5, "size": 2, "legal": True}
    expect(min([c2, c10], key=impl.selection_key) is c10, "亲和度 10 应胜过 2（数值比较，不是字符串比较）")
    expect(min([c2, c25], key=impl.selection_key) is c25, "亲和度 2.5 应胜过 2（小数）")
    t1 = {"a": ("A", "B"), "b": ("C",), "affinity": 5, "size": 3, "legal": True}
    t2 = {"a": ("D",), "b": ("E",), "affinity": 5, "size": 2, "legal": True}
    expect(min([t2, t1], key=impl.selection_key) is t1, "AB–C 与 D–E 同为 5 时，按成员 A < D 选 AB–C")


def c_k2(impl):
    r = run_cfg(impl, 2, None)
    expect(norm(r["parts"]) == ["ABC", "DE"], f"K=2 无容量应得 ABC|DE，得到 {r['parts']}")
    traj = [e["cutsize"] for e in r["log"]]
    expect(traj == [18, 13, 8, 3], f"cut 轨迹应为 18→13→8→3，得到 {traj}")
    expect(r["target_reached"] and r["stop_reason"] == "target-reached", "应报告达到 K")


def c_k3(impl):
    r = run_cfg(impl, 3, None)
    expect(norm(r["parts"]) == ["ABC", "D", "E"] and r["cutsize"] == 8, f"K=3 应得 ABC|D|E cut8，得到 {r['parts']} cut{r['cutsize']}")


def c_cap2(impl):
    r = run_cfg(impl, 2, 2)
    expect(norm(r["parts"]) == ["AB", "C", "DE"] and r["cutsize"] == 8, f"cap2 应得 AB|C|DE cut8，得到 {r['parts']} cut{r['cutsize']}")
    expect(r["target_reached"] is False, "cap2 只得到 3 簇：target_reached 必须为 False，不能强行凑 K")
    expect(r["stop_reason"] == "capacity-blocked", f"停止原因应为 capacity-blocked，得到 {r['stop_reason']}")


def c_cap3(impl):
    r = run_cfg(impl, 2, 3)
    expect(norm(r["parts"]) == ["ABC", "DE"] and r["cutsize"] == 3, "cap3 应得 ABC|DE cut3")


def c_drop(impl):
    g = {"nodes": ["P", "Q", "R", "S", "T", "U"],
         "edges": [("P", "Q", 10), ("Q", "R", 2), ("R", "S", 9), ("S", "T", 1.5), ("T", "U", 10), ("P", "U", 2)]}
    r = run_cfg(impl, 2, None, g)
    for prev, cur in zip(r["log"], r["log"][1:]):
        expect(abs((prev["cutsize"] - cur["cutsize"]) - cur["weight"]) < 1e-9, f"第 {cur['step']} 步 cut 下降应等于该次亲和度 {cur['weight']}")
    first = r["log"][1]["pair"]
    expect(first == "P-Q", f"多位数权重：第一步应合并 P-Q@10（10 > 9 > 2），得到 {first}")
    members = "".join(r["parts"])
    expect(sorted(members) == sorted(g["nodes"]), "每个节点恰好属于一个簇")


def c_disconnected(impl):
    g = {"nodes": ["A", "B", "C", "D"], "edges": [("A", "B", 1)]}
    r = run_cfg(impl, 1, None, g)
    expect(r["stop_reason"] == "no-positive-affinity" and not r["target_reached"], "图不连通时剩下的簇之间没有正亲和度：应停在 no-positive-affinity")


CHECKS = [
    ("[实现] 选择键：10>2、2.5>2、成员平票", c_key),
    ("[推演] K=2：ABC|DE，轨迹 18→13→8→3", c_k2),
    ("[推演] K=3：ABC|D|E，cut 8", c_k3),
    ("[约束] cap2：3 簇、cut 8、未达到 K", c_cap2),
    ("[约束] cap3：ABC|DE，cut 3", c_cap3),
    ("[实现] 每步 cut 下降 = 亲和度；多位数权重", c_drop),
    ("[约束] 无合法正亲和度对时停止", c_disconnected),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
