# Module 03 贪心成对合并 · Python 练习包

修好比较器，再写主循环。来自 Learning Clustering 统一课程（Module 03）。网页上的实验与挑战不需要 Python；这个包是可选的实现轨道。

## 环境

Python 3.9 或更新版本，只用标准库。在任意空目录解压即可运行，不依赖课程仓库的其他文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| `starter.py` | 起始代码：留有 TODO（`NotImplementedError`） |
| `check.py` | 检查器：逐项报告 PASS / FAIL / INCOMPLETE / ERROR / SKIP |
| `reference.py` | 参考实现：卡住时再看 |
| `fixtures/` | `five_node.json` |

## 运行

```
python3 check.py              # 检查 starter.py（未完成的函数报 INCOMPLETE，不算通过）
python3 check.py reference.py # 参考实现应全部 PASS
python3 reference.py          # 看参考实现在本章例子上的输出
```

全部 PASS 时退出码为 0；有 FAIL、ERROR 或 INCOMPLETE 时为 1。SKIP 表示缺少可选依赖而未运行，不是通过。

**任务**（`starter.py`）：

1. `selection_key(c)`：返回候选的选择键，使 `min(...)` 选出应合并的一对。
2. `greedy_pair_merge(nodes, edges, k, capacity)`：完成主循环与停止原因。

**提示一**：Python 的元组逐字段比较，数字按数值比——这正是原网页 JS 缺少的。

**提示二**：每一步先列出全部正亲和度候选，再过滤掉超容量的；没有合法候选时停止，并区分 `capacity-blocked` 与 `no-positive-affinity`。检查器还会测 10 > 9 > 2 的多位数权重。

## 参考实现的输出（本包实际运行）

```
K=2 cap=None: ABC|DE cut=3 轨迹=[18, 13, 8, 3] 达到K=True 停止=target-reached
K=3 cap=None: ABC|D|E cut=8 轨迹=[18, 13, 8] 达到K=True 停止=target-reached
K=2 cap=2: AB|C|DE cut=8 轨迹=[18, 13, 8] 达到K=False 停止=capacity-blocked
K=2 cap=3: ABC|DE cut=3 轨迹=[18, 13, 8, 3] 达到K=True 停止=target-reached
```

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：thy031（Clustering Module - Lesson 3）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
