# Module 08 Fiduccia–Mattheyses 改进 · Python 练习包

实现 gain 与合法候选。来自 Learning Clustering 统一课程（Module 08）。网页上的实验与挑战不需要 Python；这个包是可选的实现轨道。

## 环境

Python 3.9 或更新版本，只用标准库。在任意空目录解压即可运行，不依赖课程仓库的其他文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| `starter.py` | 起始代码：留有 TODO（`NotImplementedError`） |
| `check.py` | 检查器：逐项报告 PASS / FAIL / INCOMPLETE / ERROR / SKIP |
| `reference.py` | 参考实现：卡住时再看 |
| `fixtures/` | `five_node.json`、`legacy_hillclimb.json`、`neg_escape.json` |

## 运行

```
python3 check.py              # 检查 starter.py（未完成的函数报 INCOMPLETE，不算通过）
python3 check.py reference.py # 参考实现应全部 PASS
python3 reference.py          # 看参考实现在本章例子上的输出
```

全部 PASS 时退出码为 0；有 FAIL、ERROR 或 INCOMPLETE 时为 1。SKIP 表示缺少可选依赖而未运行，不是通过。

**任务**（`starter.py`）：

1. `gain(nets, side, v)`：返回 (gain, FS 列表, TE 列表)；按 net 的两侧引脚计数，多引脚 net 也适用。
2. `legal_moves(side, locked, max_diff)`：未锁定、移动后仍平衡的节点。

**提示一**：对 v 所在的每个 net，数一数 v 所在侧（F）和对面（T）各有几个引脚：F 侧只有 v → +w；T 侧为 0 → −w。

**提示二**：用 `balance_ok({**side, v: 1 - side[v]}, max_diff)` 判断移动后是否合法。检查器会审查原附件的 hillclimb 数据，并在 150 个随机图（含多引脚 net）上检查收益 = 移动前后 cut 之差。

## 参考实现的输出（本包实际运行）

```
pass 1: D(+3)→9, A(+6)→3, C(-2)→5, E(-6)→11, B(-1)→12；k*=2，接受 cut 3
pass 2: C(-2)→5, E(-6)→11, B(-1)→12, D(+3)→9, A(+6)→3；k*=0，接受 cut 3
```

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：stephQ-lab（Clustering Module - Lesson 8）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
