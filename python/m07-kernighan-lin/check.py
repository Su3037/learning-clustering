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
    expect((s["a"], s["b"], s["gain"]) == ("A", "D", 9), f"首对应为 A↔D 收益 9，得到 {s}")
    expect((s["Da"], s["Db"]) == (6, 3), "D(A)=6（外 6 内 0），D(D)=3（外 5 内 2）")


def c_trial(impl):
    nodes, edges = g5()
    p = impl.kl_pass(nodes, edges, SEED)
    expect([s["gain"] for s in p["swaps"]] == [9, -8], f"第一轮试探收益应为 9, −8，得到 {[s['gain'] for s in p['swaps']]}")
    expect(p["swaps"][1]["cut_after"] == 11, "第二步试探后 cut 暂时升到 11——这是试探，不是接受")
    expect(p["best_k"] == 1 and p["accepted_cut"] == 3, "累计 9, 1：保留前 1 步，接受 cut 3")


def c_empty(impl):
    expect(impl.best_prefix([-8, 2]) == (0, 0), "累计 −8, −6：选空前缀 (0, 0)")
    expect(impl.best_prefix([9, -8]) == (1, 9), "累计 9, 1：选 (1, 9)")
    expect(impl.best_prefix([3, -3, 3]) == (1, 3), "累计 3, 0, 3：并列最大时保留更短的前缀（本课程约定），应为 (1, 3)")
    nodes, edges = g5()
    r = impl.kernighan_lin(nodes, edges, SEED)
    expect(len(r["passes"]) == 2 and r["passes"][1]["best_k"] == 0, "第二轮最佳前缀为空，算法停止")
    expect(r["cut"] == 3, "最终 cut 3")


def c_ab1(impl):
    nodes, edges = g5(ab=1)
    expect(impl.cut(edges, SEED) == 8, "AB 改为 1 后初始 cut 为 8")
    s = impl.best_swap(impl._adj(nodes, edges), SEED, set())
    expect(s["gain"] == 5 and (s["a"], s["b"]) == ("A", "D"), f"AB=1 时 g(A,D) = 5，得到 {s}")


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
        expect(sizes == (n // 2, n - n // 2), f"案例 {case}：两侧节点数必须保持")
        used = [x for s in p["swaps"] for x in (s["a"], s["b"])]
        expect(len(used) == len(set(used)), f"案例 {case}：每个节点每轮最多交换一次（锁定）")
        for s in p["swaps"]:
            expect(s["cut_before"] - s["cut_after"] == s["gain"], f"案例 {case}：收益必须等于交换前后 cut 之差")
        expect(impl.cut(edges, side) - p["accepted_cut"] == p["best_gain"], f"案例 {case}：接受的 cut 下降 = 最佳累计收益")


CHECKS = [
    ("[推演] 最大收益对：A↔D = 9", c_first),
    ("[解释] 负收益也要试探：cut 暂升 11", c_trial),
    ("[决策] 最佳前缀与空前缀", c_empty),
    ("[推演] AB=1：初始 cut 8，g(A,D)=5", c_ab1),
    ("[实现] 120 个随机图：基数、锁定、收益=cut 差", c_random),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
