# Module 02 亲和度指标 · Python 练习包

实现三种评分。来自 Learning Clustering 统一课程（Module 02）。这个练习也可以直接在模块页面的在线编程里完成，无需安装；这个包用于离线练习。

## 环境

Python 3.9 或更新版本，只用标准库。在任意空目录解压即可运行，不依赖课程仓库的其他文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| `starter.py` | 起始代码：留有 TODO（`NotImplementedError`） |
| `check.py` | 检查器：逐项报告 PASS / FAIL / INCOMPLETE / ERROR / SKIP |
| `reference.py` | 参考实现：卡住时再看 |
| `fixtures/` | `five_node.json`、`priority_graph.json`、`tiny_netlist.json` |

## 运行

```
python3 check.py              # 检查 starter.py（未完成的函数报 INCOMPLETE，不算通过）
python3 check.py reference.py # 参考实现应全部 PASS
python3 reference.py          # 看参考实现在本章例子上的输出
```

全部 PASS 时退出码为 0；有 FAIL、ERROR 或 INCOMPLETE 时为 1。SKIP 表示缺少可选依赖而未运行，不是通过。

**任务**（`starter.py` 中三个 `TODO`）：

1. `affinity_edge_weight(edges)`：直接边权。
2. `affinity_shared_neighbors(nodes, edges)`：检查所有无序节点对，只列正分。
3. `affinity_pin_count(nodes, nets)`：clique 模型，重复引脚只算一次。

三个函数都返回 `[(u, v, score), ...]`，u < v，按 (分数降序, u, v) 排序。

**提示一**：先写出“所有无序节点对”的双重循环，再决定每一对加什么。

**提示二**：共同邻居是同时出现在 u 和 v 邻接表中的 x；它贡献 `min(w(u,x), w(v,x))`。检查器还会用一张新图测试，不能只记住五节点答案。

## 参考实现的输出（本包实际运行）

```
edge   : [('A', 'B', 5), ('D', 'E', 5), ('B', 'C', 4), ('C', 'D', 2), ('A', 'C', 1), ('C', 'E', 1)]
shared : [('A', 'B', 6), ('D', 'E', 6), ('A', 'C', 5), ('B', 'C', 5), ('C', 'D', 3), ('C', 'E', 3), ('B', 'D', 2), ('A', 'D', 1), ('A', 'E', 1), ('B', 'E', 1)]
```

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：Capeur（Clustering Module - Lesson 2）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
