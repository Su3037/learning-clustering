| 模块 | 在 G01 上做什么 | 结果 | 这一步说明了什么 |
| --- | --- | --- | --- |
| [M02](modules/m02-affinity-metrics/index.html) | 给 10 对节点打共同邻居分 | 最高 A–B、D–E = 6；B–D 无直接边也得 2 | 评分是排名，不是分组 |
| [M03](modules/m03-greedy-pair-merge/index.html) | K=2，从单点反复合并 | ABC \| DE，cut 18→13→8→3 | 每次合并 cut 恰好下降该次亲和度 |
| [M04](modules/m04-size-constrained-agglomerative/index.html) | K=2，容量 2 | AB \| C \| DE，cut 8，未达到 K | 下界 ⌈5/2⌉ = 3 已证明 K=2 不可能 |
| [M05](modules/m05-label-propagation/index.html) | A→E 异步、平票取小 | B/B/B/E/E，2 轮，cut 3 | 改顺序或同步，轮数和是否停止都会变 |
| [M06](modules/m06-spectral-bisection/index.html) | Fiedler 排序 E,D,C,B,A 再扫描 | k=2：DE \| ABC，cut 3 | 中间那一刀（k=3）反而是 5 |
| [M07](modules/m07-kernighan-lin/index.html) | 从 AE \| BCD 成对交换 | 试探 9、−8，保留 1 步，cut 12→3 | 试探可以变差，接受看最佳前缀 |
| [M08](modules/m08-fiduccia-mattheyses/index.html) | 从 AE \| BCD 单点移动，人数差 ≤1 | D(+3)、A(+6)，保留 2 步，cut 3 | A 收益最大却不合法，先移 D |
| [M09](modules/m09-rajaraman-wong/index.html) | 不用 G01：12 节点有向电路 | 8 簇、20 个实例，最长延迟 8 | 目标换成延迟，并且允许复制 |

几种方法在这张小图上都得到 cut 3，这只是这张图的性质。M07/M08 得到 3 也不说明它们一般能找到全局最优；M09 的“最优”只在论文的延迟模型和允许复制的前提下成立。
