# Module 04 容量约束凝聚聚类 · Markdown 大纲

> 先于页面与媒体编写（T09）。来源：Issue #3，原作者 GateUltra（先贴截图、后补仓库，合并为同一成果）。

## 问题定义

图 + 节点大小 s(v) + 容量 C + 目标 K。先筛合法再选最大；K 不凌驾容量；单点超容量为输入错误。输出 count、capacityCompliant、targetReached、stopReason，并以下界与小图穷举诊断结局。

## 目标

o1 四个报告项 · o2 先筛合法再选最大 · o3 下界 ⌈Σs/C⌉ · o4 greedy_trap：可行但卡住 · o5 suboptimal 与大小差异 · o6 伪代码与 Python

## 讲解顺序

`m04-review` → `m04-size` → `m04-fork` → `m04-infeasible` → `m04-suboptimal` → `m04-pseudocode` → `m04-application`

## 验收数值（engines/merge.js：run / exhaustive / diagnose）

- G01 K2 C2：AB|C|DE cut8，未达到 K，infeasible-by-bound（下界 3）；K2 C3：ABC|DE cut3；K3 C2：AB|C|DE 达到 K。
- greedy_trap K2 C3：贪心 A|B|CD（cut 8），greedy-stuck；穷举 AC|BD cut 10。
- suboptimal K2 C2：贪心 AB|CD cut 18；穷举 AC|BD cut 11。
- A 大小 2、C3、K2：AB|CDE cut 5。
- 150 个随机带大小图：贪心从不违反容量，且达到 K 时 cut ≥ 穷举最优。

## 影片（四部）

- 科普片《装得下吗》（约 190 秒，配 We Never (Remix)）：序 · 座位；一 · 装不下；二 · 走错了路；三 · 不是最好；尾声
- 精讲《精讲：先筛合法，再选最大》（约 144 秒）：问题；先筛合法；不可能；卡住；非最优；面积；小结
- 进阶《进阶：可行性、最优性与代价》（约 157 秒）：一 · 先筛后选；二 · 下界的边界；三 · 穷举的代价；四 · 同一个 K；五 · 离最优多远；六 · 面积；小结
- 实验演示：从真实页面录制（video/m04-size-constrained-agglomerative/walkthrough.mjs）。

## 课件（11 页）与挑战

c1 [概念] 合法与目标是两回事 · c2 [推演] 被挡住时选谁 · c3 [约束] 至少要几个簇 · c4 [探索] 卡住还是不可能 · c5 [探索] 合法但差多少 · c6 [应用] 面积不同，结局不同

## 去重（T02）

合并规则只用一段复习卡回链 Module 03；五节点部分只保留容量分叉，时间留给两个独立反例。
