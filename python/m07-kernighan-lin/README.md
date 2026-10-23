# Module 07 Kernighan–Lin 改进 · Python 练习包

实现最大收益对与最佳前缀。来自 Learning Clustering 统一课程（Module 07）。网页上的实验与挑战不需要 Python；这个包是可选的实现轨道。

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

1. `best_swap(adj, side, locked)`：在未锁定的左右节点对中找收益最大的一对（收益可为负）。
2. `best_prefix(gains)`：返回 (k, 累计收益)，k = 0 合法。

**提示一**：先算每个节点的 D = 外部 − 内部，再对每一对算 D(a) + D(b) − 2w(a,b)。

**提示二**：前缀必须从第 1 步起连续；只在累计收益严格变大时更新 k。检查器会在 120 个随机图上检查：两侧人数不变、每点每轮最多交换一次、收益 = 交换前后 cut 之差。

## 参考实现的输出（本包实际运行）

```
pass 1: A↔D g=9 cut→3, E↔C g=-8 cut→11；最佳前缀 1，接受 cut 3
pass 2: E↔C g=-8 cut→11, D↔B g=2 cut→9；最佳前缀 0，接受 cut 3
```

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：FanqinZeng（Clustering Module - Lesson 7）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
