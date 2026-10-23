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

## 影片（两集）

上集《模型与标记》（约 3 分）：a01 链 7/10 · a02 模型 · a03 复制示意 · a04 候选 DAG 与 Δ · a05 早期标签 · a06 i 的标记 · a07 j、k、l · a08 伪代码
下集《恢复与复制》（约 2 分 20 秒）：b01 回顾 · b02 逆向选簇 · b03 实例与复制 · b04 到达时间 · b05 复制 vs 不复制 · b06 适用边界 · b07 伪代码
每个出现候选 DAG 的画面都标“候选复原数据 · 平票为假设”。

## 课件（12 页）与挑战

c1 [概念] 目标变了 · c2 [推演] 一条路径的延迟 · c3 [解释] 复制与实例 · c4 [推演] i 的标签 · c5 [探索] 复制换来了多少 · c6 [解释] 哪些说法站得住

## 弹簧（T17）

本模块不使用弹簧类比，使用 DAG 与信号路径。
