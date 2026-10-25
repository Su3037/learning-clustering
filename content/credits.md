<p class="eyebrow">资源与贡献</p>

## 资源与贡献

本课程整合 [yongfu-li/eda-learning](https://github.com/yongfu-li/eda-learning/issues?q=is%3Aissue+state%3Aclosed) 中 8 个**已关闭**的 Clustering 提交。讲解、引擎、影片、课件和练习在统一课程中重新编写；每份原作的独有贡献在对应模块的“来源”区署名并说明保留了什么。原作仓库多数没有声明统一许可，因此本课程**没有复制**这些仓库的源代码、视频、音轨或字体，只链接到固定提交。唯一的例外是 Module 05：作者本人以 MIT / CC BY 4.0 发布了 Lab05 仓库，本章引擎改写自其代码，并原样收录其原作科普片（配乐另属第三方，见下）。

### 八份原作

| 本课程 | 主题 | 原作者 | 提交 | 原作（固定提交） |
| --- | --- | --- | --- | --- |
| Module 02 | 亲和度指标 | Capeur | [Issue #1](https://github.com/yongfu-li/eda-learning/issues/1) | [网站](https://capeur.github.io/eda-clustering-module-lab2/) · [仓库 49b8725](https://github.com/Capeur/eda-clustering-module-lab2/tree/49b87257d4df69ce24a7256bb47a8dcce3c8d69a) |
| Module 03 | 贪心成对合并 | thy031 | [Issue #2](https://github.com/yongfu-li/eda-learning/issues/2) | [网站](https://thy031.github.io/lab-03/#lab) · [仓库 491283a](https://github.com/thy031/lab-03/tree/491283a3895b38f5de94c81f65b396000ba431cd) |
| Module 04 | 容量约束凝聚聚类 | GateUltra | [Issue #3](https://github.com/yongfu-li/eda-learning/issues/3) | [网站](https://gateultra.github.io/eda-clustering-lab4/) · [仓库 0b5e84b](https://github.com/GateUltra/eda-clustering-lab4/tree/0b5e84b85b3c16d42b43fe387c631addfefa901f) |
| Module 05 | 标签传播 | Su3037 | [Issue #4](https://github.com/yongfu-li/eda-learning/issues/4) | [网站](https://su3037.github.io/clustering-lab5-label-propagation/) · [仓库 7b4eca7](https://github.com/Su3037/clustering-lab5-label-propagation/tree/7b4eca7787d532d30c79659c104798d57f8f3495)（MIT） |
| Module 06 | 谱二分 | xingguangyaoyu | [Issue #5](https://github.com/yongfu-li/eda-learning/issues/5) | [网站](https://xingguangyaoyu.github.io/eda-clustering-module-lab6/) · [仓库 cb892be](https://github.com/xingguangyaoyu/eda-clustering-module-lab6/tree/cb892be765b3f9ab80a05bb8c4333e47ecc3589c) |
| Module 07 | Kernighan–Lin 改进 | FanqinZeng | [Issue #6](https://github.com/yongfu-li/eda-learning/issues/6) | [网站](https://fanqinzeng.github.io/eda-clustering-lab7-kl/) · [仓库 b47cd64](https://github.com/FanqinZeng/eda-clustering-lab7-kl/tree/b47cd64cc9c9a11c4e9c144f8cf45de4bdb4c820) |
| Module 08 | Fiduccia–Mattheyses 改进 | stephQ-lab | [Issue #7](https://github.com/yongfu-li/eda-learning/issues/7) | [HTML 附件](https://github.com/user-attachments/files/33714154/eda_lab_08_fiduccia_mattheyses_fm.html)（Issue 中先贴的 TCLhw 仓库是 Tcl 作业，不是 FM 成果） |
| Module 09 | Rajaraman–Wong 延迟导向聚类 | muranfei | [Issue #8](https://github.com/yongfu-li/eda-learning/issues/8) | [网站](https://muranfei.github.io/rajaraman-wong-algorithm-teaching/) · [仓库 63c23ec](https://github.com/muranfei/rajaraman-wong-algorithm-teaching/tree/63c23ecd6bc38d3c490eebf5eab2322da5dec063) |

Module 03 的补交网址 `thy031.github.io/lab-03/#lab` 已在 Issue #2 的评论中出现，是同一份作品，不算第九份。

### 编号与教师目录的对应

教师原课程目录（[Learning Clustering](https://yongfu-li.github.io/eda-learning/courses/learn_clustering/index.html)）有 14 项，本课程只整合其中有对应已关闭提交的 8 项。Issue #1–#7 的主题与教师目录 Lab 02–08 一致，旧路径 `labs/<slug>/` 保留兼容入口。**Issue #8 提交的是 Rajaraman–Wong，而教师目录的 Lab 09 是 Multilevel**：本课程保留真实提交主题，标为“对应待教师确认”，不为 multilevel 旧路径生成跳转，也不制作 Multilevel 内容。

### 本课程新写的部分

- 算法引擎 `site/engines/`、Python 参考与练习、测试：本项目新写。Module 05 引擎改写自 Su3037 本人的 Lab05 实现（MIT）。
- 影片：每章四部。精讲、进阶与实验演示是 Python + cairo 逐帧绘制（实验演示由 Playwright 录下真实页面后合成）的原创影片，配乐为程序合成的原创氛围音（NumPy）。科普片按作者指定使用《We Never (Remix)（若如初见）》（Hi Noise / 秋成，第三方录音，不在本课程许可范围内）；Module 05 另原样收录作者原作《圈子从哪里来》。首页另有一部导论片，讲所有章节共同的背景：什么是聚类。
- 课件：同一份 JSON 生成 PDF、PNG 预览与可编辑 PPTX。
- 许可：新写代码 MIT（`LICENSE`）；新写教材、图解、影片、课件、字幕与原创配乐 CC BY 4.0（`LICENSE-CONTENT.md`），署名“Su3037 · Learning Clustering”；不覆盖上表中的原作，它们保留各自作者的权利与许可。

### 第三方工具

FFmpeg（libx264、AAC）、libcairo、NumPy、python-pptx（MIT）、pypdfium2 只用于本地生成媒体与检查，不随网站分发。字体：网站、课件（PDF / PPTX / 预览图）与影片画面统一使用 [Noto Sans SC](https://github.com/notofonts/noto-cjk)（SIL Open Font License 1.1，版权归 Adobe，“Noto”为 Google 的商标）；网站加载按本课程用字裁剪的子集，许可全文随附于 `assets/fonts/OFL.txt`。影片中的代码行使用等宽字体 Menlo 渲染为画面，不分发该字体。

### 参考文献

- Kernighan, B. W., & Lin, S. (1970). An efficient heuristic procedure for partitioning graphs. *Bell System Technical Journal*, 49(2), 291–307.
- Fiduccia, C. M., & Mattheyses, R. M. (1982). A linear-time heuristic for improving network partitions. *Proc. 19th Design Automation Conference*, 175–181.
- Fiedler, M. (1973). Algebraic connectivity of graphs. *Czechoslovak Mathematical Journal*, 23(2), 298–305.
- Raghavan, U. N., Albert, R., & Kumara, S. (2007). Near linear time algorithm to detect community structures in large-scale networks. *Physical Review E*, 76, 036106.
- Rajaraman, R., & Wong, D. F. (1995). Optimum clustering for delay minimization. *IEEE Transactions on Computer-Aided Design*, 14(12), 1490–1495. [doi:10.1109/43.476579](https://doi.org/10.1109/43.476579)（会议版本：DAC 1993）
