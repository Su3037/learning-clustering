# Module 06 谱二分 · Python 练习包

构造 L、扫描切分、数值自检。来自 Learning Clustering 统一课程（Module 06）。这个练习也可以直接在模块页面的在线编程里完成，无需安装；这个包用于离线练习。

## 环境

Python 3.9 或更新版本，只用标准库。
可选：NumPy（检查器中“与 NumPy 对照”一项需要它；没有时报 SKIP，不算通过）。在任意空目录解压即可运行，不依赖课程仓库的其他文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| `starter.py` | 起始代码：留有 TODO（`NotImplementedError`） |
| `check.py` | 检查器：逐项报告 PASS / FAIL / INCOMPLETE / ERROR / SKIP |
| `reference.py` | 参考实现：卡住时再看 |
| `fixtures/` | `disconnected.json`、`five_node.json` |

## 运行

```
python3 check.py              # 检查 starter.py（未完成的函数报 INCOMPLETE，不算通过）
python3 check.py reference.py # 参考实现应全部 PASS
python3 reference.py          # 看参考实现在本章例子上的输出
```

全部 PASS 时退出码为 0；有 FAIL、ERROR 或 INCOMPLETE 时为 1。SKIP 表示缺少可选依赖而未运行，不是通过。

**任务**（`starter.py`）：

1. `laplacian(nodes, edges)`：构造 L = D − A。
2. `sweep(order, edges, lo, hi)`：沿排序逐个位置切分，标出是否合法。
3. `count_bipartitions(n)`：两组非空、不分左右的二分数。

已提供纯 Python 的 Jacobi 求解器；检查器在装有 NumPy 时会额外与 `numpy.linalg.eigvalsh` 对照（没有 NumPy 时报 SKIP，不算通过）。

**提示一**：每条边对 L 的四个位置做贡献：两个对角 +w，两个非对角 −w。

**提示二**：2ⁿ 种左右标记里要去掉哪两种？再除以几？

## 参考实现的输出（本包实际运行）

```
λ = [-0.0, 1.7733143437, 8.4551152172, 11.6052655098, 14.1663049292]
顺序 ['E', 'D', 'C', 'B', 'A'] 扫描 [6, 3, 5, 6] 选择 (['E', 'D'], ['C', 'B', 'A']) cut 3
残差 3.8543291529169345e-15 非空二分数 15
```

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：xingguangyaoyu（Clustering Module - Lesson 6）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
