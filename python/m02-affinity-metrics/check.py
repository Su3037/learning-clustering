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


def as_dict(lst):
    return {(u, v): s for u, v, s in lst}


def c_edge(impl):
    g = fixture("five_node.json")
    got = impl.affinity_edge_weight(g["edges"])
    expect(len(got) == 6, f"五节点图应有 6 对直接连线，得到 {len(got)} 对")
    expect([(u, v) for u, v, _ in got[:2]] == [("A", "B"), ("D", "E")], "并列 5 分时应按 u、v 字典序：A-B 在 D-E 前")


def c_shared(impl):
    g = fixture("five_node.json")
    got = impl.affinity_shared_neighbors(g["nodes"], g["edges"])
    d = as_dict(got)
    expect(len(got) == 10, f"共同邻居评分应列出 10 对正分，得到 {len(got)} 对——是否漏了没有直接连线的节点对？")
    expect(d.get(("A", "C")) == 5, f"A-C 应为直接 1 + 经 B 的 min(5,4)=4，共 5；得到 {d.get(('A', 'C'))}")
    expect(d.get(("B", "D")) == 2, f"B-D 没有直接边，但经共同邻居 C 得 min(4,2)=2；得到 {d.get(('B', 'D'))}")
    expect(all(u < v for u, v, _ in got), "每一对都应写成 u < v")


def c_priority(impl):
    g = fixture("priority_graph.json")
    e = impl.affinity_edge_weight(g["edges"])
    s = impl.affinity_shared_neighbors(g["nodes"], g["edges"])
    expect(e[0] == ("X", "Y", 5), f"按直接边权，第一对应为 X-Y@5，得到 {e[0]}")
    expect(s[0] == ("P", "Q", 8), f"按共同邻居，第一对应为 P-Q@8，得到 {s[0]}")


def c_order_invariant(impl):
    g = fixture("five_node.json")
    shuffled = [(v, u, w) for u, v, w in reversed(g["edges"])]
    a = impl.affinity_shared_neighbors(g["nodes"], g["edges"])
    b = impl.affinity_shared_neighbors(list(reversed(g["nodes"])), shuffled)
    expect(a == b, "乱序、反向输入边后排名应完全相同（稳定排名）")


def c_pin(impl):
    n = fixture("tiny_netlist.json")
    got = as_dict(impl.affinity_pin_count(n["nodes"], n["nets"]))
    expect(abs(got.get(("A", "B"), -1) - 0.5) < 1e-9, f"A-B 应为 1/4 + 1/4 = 0.5，得到 {got.get(('A', 'B'))}")
    expect(abs(got.get(("E", "F"), -1) - 1) < 1e-9, f"E-F 应为 1/(2-1) = 1，得到 {got.get(('E', 'F'))}")
    dup = impl.affinity_pin_count(["A", "B", "C"], [{"id": "x", "pins": ["A", "A", "B"], "w": 1}, {"id": "y", "pins": ["C"], "w": 1}])
    expect(dup == [("A", "B", 1)], f"重复引脚只算一次、单引脚 net 忽略：应得 [('A','B',1)]，得到 {dup}")


def c_new_graph(impl):
    # 一张练习里没出现过的图：防止只对五节点图写死答案
    nodes = ["M", "N", "O", "P"]
    edges = [("M", "N", 2), ("N", "O", 10), ("M", "O", 3), ("O", "P", 1)]
    got = impl.affinity_shared_neighbors(nodes, edges)
    want = [("N", "O", 12), ("M", "O", 5), ("M", "N", 5), ("M", "P", 1), ("N", "P", 1), ("O", "P", 1)]
    want = sorted(want, key=lambda t: (-t[2], t[0], t[1]))
    expect(got == want, f"新图应为 {want}，得到 {got}")


CHECKS = [
    ("[推演] 直接边权：6 对，平票按字典序", c_edge),
    ("[推演] 共同邻居：10 对，A-C=5，B-D=2", c_shared),
    ("[探索] priority 图：XY@5 与 PQ@8", c_priority),
    ("[实现] 稳定排名：乱序输入结果不变", c_order_invariant),
    ("[实现] pin-count：AB=0.5，EF=1，重复引脚策略", c_pin),
    ("[实现] 新图：不能只记住五节点答案", c_new_graph),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
