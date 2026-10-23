# Module 02 亲和度指标 · Markdown 大纲

> 本大纲先于网页、影片、课件与练习编写（T09）。来源：Issue #1，原作者 Capeur。参考包 `module-plans/m02-affinity-metrics/` 的大纲与改造方案经本课程核对后采用。

## 问题定义

- 输入：带权无向图，或多引脚网表。
- 输出：所有正分节点对 (u, v, score)，u < v，按 (−score, u, v) 排序。
- 目标：在明确声明的模型下量化“这一对有多该放在一起”。不输出分组。
- 约束与约定：无自环、无重复边；net 内重复引脚只算一次；少于 2 引脚的 net 忽略；零分对不列出。

## 学习目标（id 与 crosswalk 一致）

| id | 目标 |
| --- | --- |
| o1 | 区分评分（排名）与分组；亲和度不是距离或概率 |
| o2 | 手算直接边权并给出稳定排名 |
| o3 | 分解共同邻居分数，包括无直接边的节点对 |
| o4 | 解释 priority 图中换评分后第一对的变化 |
| o5 | 计算 clique 模型 pin-count，解释宽 net 稀释 |
| o6 | 逐行读懂伪代码并用 Python 实现 |

## 讲解顺序（网页 #lesson 小节）

1. `m02-why` 为什么要先给一对单元打分；graph 与 net；评分不是分组
2. `m02-edge` 直接边权与稳定排名
3. `m02-shared` 共同邻居分解；A–C = 1 + 4；B–D = 0 + 2（无直接边）
4. `m02-priority` priority 图：X–Y@5 → P–Q@8
5. `m02-pincount` 宽 net 稀释：A–B 计数 2 → pin-count 0.5；E–F = 1
6. `m02-pseudocode` 逐行伪代码，与实验事件联动
7. `m02-application` EDA 含义与局限

## 代表例子与验收数值（由 `site/engines/affinity.js` 计算，`tests/engines.test.mjs` 断言）

- G01 直接边权 6 对：A-B 5, D-E 5, B-C 4, C-D 2, A-C 1, C-E 1。
- G01 共同邻居 10 对：A-B 6, D-E 6, A-C 5, B-C 5, C-D 3, C-E 3, B-D 2, A-D 1, A-E 1, B-E 1。
- priority：edge 第一 X–Y@5；shared 第一 P–Q@8；X–Y 需 ≥ 9 才在 shared 中排第一。
- tiny netlist：计数 A–B 2；pin-count A–B 0.5、E–F 1。

## 影片（约 4 分钟，中文字幕，无配音）

| sceneId | 画面与推理动作 | 绑定数据 |
| --- | --- | --- |
| s01-hook | priority 图出现，提问“先合并谁？”，留预测时间 | PRIORITY_GRAPH |
| s02-model | 图与 net 的区别：一条 5 引脚 net 展开 | TINY_NETLIST |
| s03-edge | G01 六条边按权重升起成排名，平票按字母 | edgeWeight(G01) |
| s04-ac | A–C：直接 1 与经 B 的 min(5,4)=4 分别飞入总分框 | sharedNeighbors(G01) A–C |
| s05-bd | B–D 无直接线，经 C 得 2；强调不新增导线 | sharedNeighbors(G01) B–D |
| s06-priority | 左右双栏：X–Y=5 先亮；三角形贡献叠成 8 | 两种评分 |
| s07-pin | 宽 net 每对 1/4，A–B=0.5，E–F=1 排第一 | pinCount |
| s08-code | 伪代码逐行亮起，对应 B–D 一次循环 | 同上 |
| s09-eda | 回到芯片：评分决定先粘谁；三条局限 | — |

## 课件（16:9，页脚 Module 02 · p/total，讲稿放网页下方）

封面 → 问题定义 → 图与 net → 直接边权与稳定排名 → 共同邻居公式 → A–C/B–D 手算 → priority 对比 → pin-count → 伪代码 → 常见错误 → EDA 与局限 → 小结与下一模块。

## 挑战（类型与难度分开）

c1 [概念] 评分不是分组（入门）· c2 [推演] 没有直接边也能评分（入门）· c3 [推演] 把 A–C 拆开（练习）· c4 [探索] 换一种评分，第一对是谁（练习）· c5 [实现] 手工排出稳定排名（练习）· c6 [探索] 让 X–Y 重新排第一（挑战）· c7 [应用] 宽 net 的稀释（挑战）

## Python

`affinity_edge_weight`、`affinity_shared_neighbors`、`affinity_pin_count`；检查器含乱序输入与一张新图，防止写死答案。练习包自包含，不依赖课程 common/。

## 去重说明（T02）

图、边权、cut 的定义放在基础速查，本章只用一段复习卡回链；G01 在后续模块出现时每次标明“这次做什么”。
