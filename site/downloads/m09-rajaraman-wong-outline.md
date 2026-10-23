# Module 09 Rajaraman–Wong 延迟导向聚类 · Markdown 大纲

> 先于页面与媒体编写（T09）。来源：Issue #8（Lesson 9），原作者 muranfei。**映射待确认**：教师目录 Lab 09 为 Multilevel；本模块保留真实提交主题，不替代 Multilevel，不为 multilevel 旧路径生成跳转。

## 问题定义

组合 DAG + δ(v) + s(v) + 容量 M + 跨簇 D，簇内 0，允许复制；最小化 PI→PO 最大延迟。逻辑节点与实例分开：instances[{instanceId, logicalId, clusterId}] + instanceEdges。有环报错。

## 目标

o1 目标变化（链 7/10） · o2 模型 · o3 逻辑节点与实例 · o4 Δ 与标记 l = max(l1, l2) · o5 逆向恢复（8 簇、20 实例、输出 8；不复制最好 10） · o6 边界与待确认事项

## 讲解顺序

`m09-goal` → `m09-model` → `m09-replication` → `m09-init` → `m09-label` → `m09-reconstruct` → `m09-pseudocode` → `m09-scope`

## 验收数值（engines/rw.js；scripts/research/rw_no_replication.py）

- 链：{P,X}|{Y,O} 7；{P}|{X,Y}|{O} 10；加环报错。
- 候选 DAG（15 边，平票：lv 降序、逆拓扑序优先——假设）：标签 a,b,c 1；d,e,f,h 2；g 3；i,j 7；k,l 8；8 簇；20 实例；输出 k = l = 8；实例输入全部完整。
- 不复制、容量 4、D 3：穷举最好 10（例 adfh | bceg | ijkl，引擎复评 10）。
- 120 个随机 DAG：实例图合法，输出到达时间 = 标签；JS/Python 标签、簇、实例数、输出一致。

## 影片（四部）

- 科普片《关键路径的代价》（189.8 秒，配 We Never (Remix)）：p-open 一道菜 · p-ask/p-rule 链 7/10 · p-dag 候选 DAG · p-time 早期标签 · p-i i 的标签 7 · p-labels j、k、l · p-twins g、j 各做两份 · p-back 逆向恢复 8 簇 20 实例 · p-compare 不复制最好 10 · p-chip · p-outro · p-end
- 精讲：k01 目标 · k02 模型 · k03 Δ · k04 i 的标记 · k05 逆向恢复 · k06 小结
- 进阶：a01 全部标签与平票假设 · a02 逻辑节点与实例 · a03 复制 vs 不复制 · a04 结论的边界 · a05 候选数据 · a06 小结
- 实验演示：从真实页面录制（video/m09-rajaraman-wong/walkthrough.mjs）。
- 每个出现候选 DAG 的画面都标“候选复原数据 · 平票规则为假设”。

## 课件（12 页）与挑战

c1 [概念] 目标变了 · c2 [推演] 一条路径的延迟 · c3 [解释] 复制与实例 · c4 [推演] i 的标签 · c5 [探索] 复制换来了多少 · c6 [解释] 哪些说法站得住

## 弹簧（T17）

本模块不使用弹簧类比，使用 DAG 与信号路径。
