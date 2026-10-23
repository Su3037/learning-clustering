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
    return g["nodes"], [tuple(e) for e in g["edges"]]


def c_row(impl):
    nodes, edges = g5()
    L = impl.laplacian(nodes, edges)
    expect([round(x, 9) for x in L[0]] == [6, -5, -1, 0, 0], f"A 行应为 6,-5,-1,0,0，得到 {L[0]}")
    expect(all(abs(sum(r)) < 1e-9 for r in L), "每行和应为 0")
    expect(all(abs(L[i][j] - L[j][i]) < 1e-12 for i in range(5) for j in range(5)), "L 应对称")


def c_eigen(impl):
    nodes, edges = g5()
    r = impl.spectral_bisection(nodes, edges)
    expect(abs(r["eigenvalues"][0]) < 1e-9, "连通图 λ1 应为 0")
    expect(abs(r["eigenvalues"][1] - 1.7733143437) < 1e-8, f"λ2 应约为 1.7733143437，得到 {r['eigenvalues'][1]}")
    expect(r["diagnostics"]["residual"] < 1e-8, "未舍入的 Fiedler 向量残差 ‖Lx−λx‖/‖x‖ 应很小")


def c_sweep(impl):
    nodes, edges = g5()
    r = impl.spectral_bisection(nodes, edges, (0.4, 0.6))
    expect(r["order"] == ["E", "D", "C", "B", "A"], f"排序应为 E,D,C,B,A，得到 {r['order']}")
    expect([c["cut"] for c in r["candidates"]] == [6, 3, 5, 6], f"扫描 cut 应为 6,3,5,6，得到 {[c['cut'] for c in r['candidates']]}")
    expect([c["k"] for c in r["candidates"] if c["legal"]] == [2, 3], "40/60 窗口只允许 k=2、3")
    expect(r["cut"] == 3 and sorted(r["partition"][0]) == ["D", "E"], "应选 k=2：DE | ABC，cut 3（不是中间 k=3 的 5）")


def c_flip(impl):
    nodes, edges = g5()
    a = impl.sweep(["E", "D", "C", "B", "A"], edges, 2, 3)
    b = impl.sweep(["A", "B", "C", "D", "E"], edges, 2, 3)
    expect([c["cut"] for c in a] == [c["cut"] for c in reversed(b)], "向量翻号 = 排序反向：同一刀两侧互换，cut 不变")


def c_count(impl):
    expect(impl.count_bipartitions(5) == 15, f"5 个节点、两组非空、不分左右：15 种（不是 16），得到 {impl.count_bipartitions(5)}")
    expect(impl.count_bipartitions(2) == 1, "2 个节点只有 1 种")


def c_singleton(impl):
    nodes, edges = g5()
    r = impl.sweep(["E", "D", "C", "B", "A"], edges, 1, 4)
    best = min(r, key=lambda c: c["cut"])
    expect(best["cut"] == 3 and best["k"] == 2, "不加平衡约束时最小 cut 也是 ABC|DE=3，而孤立一个点最小是 6：无约束并不总是切出单点")


def c_disconnected(impl):
    g = fixture("disconnected.json")
    r = impl.spectral_bisection(g["nodes"], [tuple(e) for e in g["edges"]], (0.5, 0.5))
    expect(abs(r["eigenvalues"][1]) < 1e-9, "两个分量：λ2 = 0")
    expect(r["cut"] == 0, "切在两个分量之间时 cut = 0")


def c_numpy(impl):
    try:
        import numpy as np
    except ImportError:
        raise Skip("未安装 NumPy：跳过与 numpy.linalg.eigh 的对照")
    nodes, edges = g5()
    L = np.array(impl.laplacian(nodes, edges), dtype=float)
    want = np.linalg.eigvalsh(L)
    got = impl.spectral_bisection(nodes, edges)["eigenvalues"]
    expect(np.allclose(sorted(got), want, atol=1e-9), "与 NumPy 特征值不一致")


CHECKS = [
    ("[概念] 构造一行 L：6,-5,-1,0,0，行和 0", c_row),
    ("[实现] 特征值与残差", c_eigen),
    ("[推演] 扫描 6,3,5,6；窗口内选 k=2", c_sweep),
    ("[推演] 翻号只交换左右", c_flip),
    ("[纠错] 非空二分数 = 15", c_count),
    ("[纠错] 无约束最优不必是单点", c_singleton),
    ("[探索] 断开图 λ2 = 0", c_disconnected),
    ("[实现] 可选：与 NumPy 对照", c_numpy),
]

if __name__ == "__main__":
    sys.exit(run_checks(CHECKS))
