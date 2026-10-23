# Module 04 容量约束凝聚聚类 · Python 练习包

补全停止报告与诊断分类。来自 Learning Clustering 统一课程（Module 04）。网页上的实验与挑战不需要 Python；这个包是可选的实现轨道。

## 环境

Python 3.9 或更新版本，只用标准库。在任意空目录解压即可运行，不依赖课程仓库的其他文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| `starter.py` | 起始代码：留有 TODO（`NotImplementedError`） |
| `check.py` | 检查器：逐项报告 PASS / FAIL / INCOMPLETE / ERROR / SKIP |
| `reference.py` | 参考实现：卡住时再看 |
| `fixtures/` | `five_node.json`、`greedy_trap.json`、`suboptimal.json` |

## 运行

```
python3 check.py              # 检查 starter.py（未完成的函数报 INCOMPLETE，不算通过）
python3 check.py reference.py # 参考实现应全部 PASS
python3 reference.py          # 看参考实现在本章例子上的输出
```

全部 PASS 时退出码为 0；有 FAIL、ERROR 或 INCOMPLETE 时为 1。SKIP 表示缺少可选依赖而未运行，不是通过。

**任务**（`starter.py`）：

1. `report(parts, k, capacity, size, stop)`：返回 count、capacity_compliant、target_reached、stop_reason 四项。
2. `classify(graph, k, capacity)`：结合 `solve()` 与已提供的 `oracle()`，返回五种结局之一。

**提示一**：四项是互相独立的；容量 2 的 AB | C | DE 合法但没有达到 K。

**提示二**：先看是否达到 K；没达到时，看下界是否已大于 K，再看穷举是否找到恰好 K 簇的合法划分。检查器还会测超容量单点与无边图。

## 参考实现的输出（本包实际运行）

```
five_node.json K=2 C=2: ['AB', 'C', 'DE'] cut=8 合法=True 达到K=False 停止=capacity-blocked → infeasible-by-bound
five_node.json K=2 C=3: ['ABC', 'DE'] cut=3 合法=True 达到K=True 停止=target-reached → reached-and-optimal-here
five_node.json K=3 C=2: ['AB', 'C', 'DE'] cut=8 合法=True 达到K=True 停止=target-reached → reached-and-optimal-here
greedy_trap.json K=2 C=3: ['A', 'B', 'CD'] cut=8 合法=True 达到K=False 停止=capacity-blocked → greedy-stuck
suboptimal.json K=2 C=2: ['AB', 'CD'] cut=18 合法=True 达到K=True 停止=target-reached → feasible-suboptimal
```

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：GateUltra（Clustering Module - Lesson 4）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
