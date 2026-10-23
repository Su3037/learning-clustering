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
    expect(v == {"B": 5, "D": 2, "E": 1}, f"C 的票应为 B=5、D=2、E=1（按权重），得到 {v}")


def c_golden(impl):
    nodes, edges = g5()
    r = impl.solve(nodes, edges)
    expect(r["labels"] == {"A": "B", "B": "B", "C": "B", "D": "E", "E": "E"}, f"A→E 异步 min 应得 B/B/B/E/E，得到 {r['labels']}")
    expect(r["rounds"] == 2 and r["status"] == "stable", f"两轮（含零变化确认轮）后 stable，得到 {r['rounds']} 轮、{r['status']}")
    expect(r["cut"] == 3, "cut 应为 3")


def c_cycle(impl):
    r = impl.solve(["A", "B"], [("A", "B", 1)], mode="sync")
    expect(r["status"] == "cycle", f"两节点同步更新会来回交换：应报告 cycle 而不是 stable/limit，得到 {r['status']}")
    r = impl.solve(["A", "B"], [("A", "B", 1)], mode="async")
    expect(r["status"] == "stable", "同一图异步更新会统一并 stable")


def c_bridge(impl):
    nodes, edges = g5()
    heavy = [(u, v, 10 if {u, v} == {"C", "D"} else w) for u, v, w in edges]
    r = impl.solve(nodes, heavy)
    expect(r["cut"] == 5, f"把 C–D 改成 10 后重新运行，cut 应为 5，得到 {r['cut']}")


def c_order(impl):
    nodes, edges = g5()
    a = impl.solve(nodes, edges)
    b = impl.solve(nodes, edges, order=["E", "D", "C", "B", "A"])
    expect(groups(a["labels"]) == groups(b["labels"]), "反向顺序在这张图上分组相同（标签名可以不同）")
    expect(b["rounds"] == 3, f"但轮数变为 3，得到 {b['rounds']}")


def c_edges(impl):
    r = impl.solve(["A", "B", "C"], [], max_iters=5)
    expect(r["status"] == "stable" and r["rounds"] == 1, "无边图：一轮确认零变化即 stable")
    r = impl.solve(["A", "B", "C", "D"], [("A", "B", 1), ("A", "C", 1), ("A", "D", 4)], tie="max")
    expect(r["status"] in ("stable", "cycle"), "平票图应正常结束")
    r = impl.solve(["A", "B"], [("A", "B", 1)], mode="sync", max_iters=1)
    expect(r["status"] == "limit", f"上限 1 轮且尚未重复：应报告 limit，得到 {r['status']}")


def c_film(impl):
    for name, rounds, cut in [("circuit.json", 5, 2), ("contacts.json", 3, 4)]:
        g = fixture(name)
        r = impl.solve(g["nodes"], [tuple(e) for e in g["edges"]])
        expect(r["rounds"] == rounds and r["cut"] == cut, f"{name}：应 {rounds} 轮、cut {cut}，得到 {r['rounds']} 轮、cut {r['cut']}")


CHECKS = [
    ("[推演] C 的票数：B=5、D=2、E=1", c_votes),
    ("[推演] 默认：B/B/B/E/E，两轮，cut 3", c_golden),
    ("[探索] 同步双点振荡 = cycle", c_cycle),
    ("[探索] C–D=10 重新运行 cut 5", c_bridge),
    ("[探索] 反向顺序：同分组、3 轮", c_order),
    ("[实现] 停止状态：孤点、平票、上限", c_edges),
    ("[应用] 24 单元与联系人图", c_film),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
