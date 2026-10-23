# Module 05 标签传播 · Python 练习包

实现计票与停止判定。来自 Learning Clustering 统一课程（Module 05）。网页上的实验与挑战不需要 Python；这个包是可选的实现轨道。

## 环境

Python 3.9 或更新版本，只用标准库。在任意空目录解压即可运行，不依赖课程仓库的其他文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| `starter.py` | 起始代码：留有 TODO（`NotImplementedError`） |
| `check.py` | 检查器：逐项报告 PASS / FAIL / INCOMPLETE / ERROR / SKIP |
| `reference.py` | 参考实现：卡住时再看 |
| `fixtures/` | `circuit.json`、`contacts.json`、`five_node.json` |

## 运行

```
python3 check.py              # 检查 starter.py（未完成的函数报 INCOMPLETE，不算通过）
python3 check.py reference.py # 参考实现应全部 PASS
python3 reference.py          # 看参考实现在本章例子上的输出
```

全部 PASS 时退出码为 0；有 FAIL、ERROR 或 INCOMPLETE 时为 1。SKIP 表示缺少可选依赖而未运行，不是通过。

**任务**（`starter.py`）：

1. `count_votes(adj, labels, vertex)`：按标签累加邻居边权。
2. 主循环中的停止判定：stable / cycle（limit 由循环上限负责）。

**提示一**：同一标签的邻居，把它们的边权加起来；C 的票应为 B = 5、D = 2、E = 1。

**提示二**：一整轮零变化 → stable；这一轮结束后的完整标签状态以前出现过 → cycle。检查器还会跑作者原作的 24 单元电路图与 28 人联系人图。

## 参考实现的输出（本包实际运行）

```
{'A': 'B', 'B': 'B', 'C': 'B', 'D': 'E', 'E': 'E'} 2 stable cut 3
```

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：Su3037（Clustering Module - Lesson 5）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
