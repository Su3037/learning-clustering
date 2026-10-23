# Module 08 Fiduccia–Mattheyses 改进 · Markdown 大纲

> 先于页面与媒体编写（T09）。来源：Issue #7 的 HTML 附件，作者 stephQ-lab；Issue 中先贴的 TCLhw 是 Tcl 作业，不作来源。P0：原 hillclimb 反例证伪并替换；桶展示 ≠ 线性实现；二端图 ≠ 超图。

## 问题定义

带权二端图（拓展：多引脚 net）+ 初始二分 + maxDiff → 每轮在合法未锁定节点中选最大收益（可为负）单点移动、锁定、增量更新；轮末取最佳前缀并回退；空前缀停止。平衡按节点个数。

## 目标

o1 与 KL 的差别 · o2 合法候选中取最大 · o3 FS/TE · o4 一轮与 k*=2 · o5 审查与替换反例 · o6 桶与复杂度、多引脚 net、Python

## 讲解顺序

`m08-diff` → `m08-legal` → `m08-walk` → `m08-escape` → `m08-bucket` → `m08-pseudocode` → `m08-limits`

## 验收数值（engines/fm.js；穷举 exhaustive()）

- 种子初始收益 A +6 ✗、B +1、C −4、D +3、E +6 ✗；移动 D+3/9、A+6/3、C−2/5、E−6/11、B−1/12；累计 3,9,7,1,0；k*=2；接受 cut 3；第二轮空前缀。
- D：FS = DE 5，TE = CD 2。
- 原 hillclimb：初始 18（非 9）；E 合法 +10；首轮最佳 8；穷举 8（非 4）。
- 替换反例 NEG_ESCAPE（randomGraph 种子 4198）：初始合法收益全 ≤ 0；A−1、B−1、E+4；k*=3；cut 6→4 = 穷举最优。
- 第三例 7 节点：初始 22，k*=3，cut 1；hasMultiPin = false。
- 多引脚：net{A,B,C,D}（权 3）、D 在右：A 0、D +3（团近似 A −1）。
- 250 个随机图（含多引脚 net）：增量收益 = 从零重算收益；收益 = cut 差；接受的二分平衡。

## 影片《合法的那一步》（约 3 分 45 秒）

s01 KL vs FM · s02 合法性（A、E 红圈） · s03 FS/TE · s04 一轮 · s05 最佳前缀 · s06 审查原反例 · s07 替换反例 · s08 桶与复杂度 · s09 多引脚 net · s10 伪代码 · s11 局限

## 课件（12 页）与挑战

c1 [合法性] 为什么不选 A · c2 [推演] 拆开 D 的收益 · c3 [回退] 选出 k* · c4 [纠错] 审查原附件的反例 · c5 [探索] 先负后正 · c6 [拓展] 多引脚 net 的收益

## 去重（T02）

gain / lock / prefix 只用复习卡回链 Module 07；本章时间用于平衡合法性、反例审查与复杂度边界。
