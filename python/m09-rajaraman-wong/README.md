# Module 09 Rajaraman–Wong 延迟导向聚类 · Python 练习包

分层完成：先评估延迟，再实现标记与恢复。来自 Learning Clustering 统一课程（Module 09）。这个练习也可以直接在模块页面的在线编程里完成，无需安装；这个包用于离线练习。

## 环境

Python 3.9 或更新版本，只用标准库。在任意空目录解压即可运行，不依赖课程仓库的其他文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| `starter.py` | 起始代码：留有 TODO（`NotImplementedError`） |
| `check.py` | 检查器：逐项报告 PASS / FAIL / INCOMPLETE / ERROR / SKIP |
| `reference.py` | 参考实现：卡住时再看 |
| `fixtures/` | `candidate_dag.json`、`chain.json` |

## 运行

```
python3 check.py              # 检查 starter.py（未完成的函数报 INCOMPLETE，不算通过）
python3 check.py reference.py # 参考实现应全部 PASS
python3 reference.py          # 看参考实现在本章例子上的输出
```

全部 PASS 时退出码为 0；有 FAIL、ERROR 或 INCOMPLETE 时为 1。SKIP 表示缺少可选依赖而未运行，不是通过。

**基础任务**（可以先独立完成这三项）：

1. `topological_order(nodes, edges)`：有环时报错。
2. `longest_node_delays(...)`：Δ[x][v]。
3. `evaluate_instance_delay(...)`：实例到达时间；链的 7 与 10。

**进阶任务**：

4. `rw_label(dag)`：按拓扑序打标签。
5. `rw_reconstruct(dag, cluster)`：从 PO 倒推簇与实例。

**提示一**：Δ 只计路径上 v 的延迟、不计起点 x；无路径记为 None。

**提示二**：实例 id 写成 “节点@簇根”；簇外输入 u 来自 “u@u”，代价 D。检查器在候选图上核对 8 簇、20 实例、输出 8，并检查每个实例的输入完整。

## 参考实现的输出（本包实际运行）

```
labels {'a': 1, 'b': 1, 'c': 1, 'd': 2, 'e': 2, 'f': 2, 'g': 3, 'h': 2, 'i': 7, 'j': 7, 'k': 8, 'l': 8}
簇 8 实例 20 输出延迟 {'k': 8, 'l': 8}
```

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：muranfei（Clustering Module - Lesson 9）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
