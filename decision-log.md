# 决策记录

格式：编号 · 决定 · 理由 · 来源/依据 · 可否改变。“教师要求”只写原话明确的项；其余标为设计选择。

## 范围与命名

- **D-SCOPE-1** 仅 8 个已关闭 Clustering 提交，Module 02–09。依据：handoff §3、request-scope。不可变。
- **D-SCOPE-2** M09 显示为“Module 09 · Rajaraman–Wong 延迟导向聚类”，首页与本章页眉显示“提交主题与教师目录 Lab09（Multilevel）对应待确认”。`labs/multilevel-clustering/` 不生成跳转。依据：D08、module-mapping。确认后只改 registry 的 `teacherMappingStatus`。
- **D-SCOPE-3** M08 来源登记为 Issue #7 的 HTML 附件，TCLhw 只出现在来源轨迹里。
- **D-NAME-1** 学习界面统一 “Module / 模块”（T01 原话明确）。Lab/Lesson/Issue 只出现在来源映射。

## 技术

- **D-TECH-1** 纯静态站点，无框架、无外部 CDN、无构建期依赖（Node 脚本仅生成 HTML，不打包）。理由：GitHub Pages 子路径可用、浏览器端运行、学生可读源码。
- **D-TECH-2** 每模块生成独立 `modules/<id>/index.html`，页内锚点导航，刷新深链无需 SPA 回退。
- **D-TECH-3** 所有路径相对化；不硬编码域名根。
- **D-ENG-1** 引擎接口 `validate()`/`run()`，事件流 + 结果 + status；不同算法保留各自数据结构（谱带诊断、RW 带实例图）。M03/M04 共用凝聚引擎但 M04 结果额外报告 `capacityCompliant / targetReached / feasibility`。
- **D-ENG-2** M06 网页实现 Jacobi 特征分解（对称小矩阵，n≤40），改图即重算；同时保留原作三位小数向量作为“原作存储值”对照并显示其残差。这样“实时求解”是真的。Python 参考用 NumPy（声明依赖）并另有纯 Python 幂迭代备选。
- **D-ENG-3** M08 基础轨道为带权二端图；引擎内部以 net（pin 列表）表示，二端边是 2-pin net，因此可选拓展“多引脚 net”使用同一套 pin 计数 gain 更新。桶结构是按 gain 分组的 Map，每次在合法候选中取最大——明确写“未达到论文 O(P) 实现”。
- **D-ENG-4** 平票：M03/M04 `(-affinity, 成员排序后标签串)` 逐字段比较；M07 候选 `(−gain, a, b)`；M08 `(−gain, 节点名)`；M05 沿用 min/max/keep；M09 采用审计候选的“lv 降序，再逆拓扑序”，标为 candidate 假设。
- **D-ENG-5** M05 引擎改写自用户本人 LP 仓库 `site/algorithm.js`（MIT，commit 7b4eca7），其他模块引擎为本项目新写，不复制无许可学生代码。

## 媒体

- **D-MEDIA-1** 默认中文字幕、无配音（延续用户 LP 片）；TTS/旁白为可选，未制作，因此没有听审项。T15/T18 不作为必须配音的依据。
- **D-MEDIA-2** 配乐为本项目程序合成的原创氛围音（NumPy），每片一条，音量低于 −18 LUFS 目标附近，事件节点有轻微提示音。不使用 We Never。
- **D-MEDIA-3** 1920×1080、30fps、H.264 yuv420p、AAC、faststart。字幕烧录在画面下方 150–180px 专区，同时提供 WebVTT（网页 track 默认关闭，避免重复）。
- **D-MEDIA-4** 片长按知识量：M02/M03/M04 约 3.5–5 分钟，M05 核心片 + 原有慢推演概念（统一为一部，内含慢节奏推演段），M06 约 4–5 分钟，M07/M08 约 4–5 分钟，M09 两段。具体实测写入 implementation-log。不做多版本。
- **D-MEDIA-5** 代表性小样选 M07 “试探变差→最佳前缀→回退”（约 40 秒），因其最能检验 trial/accepted 区分、字幕节奏与数值读图时间。

## 课件

- **D-SLIDE-1** 16:9（设计选择，与影片一致、适合投影；不是教师指定）。每页页脚 `Module 0X · 模块名 · p/total`，网页 viewer 顶部同号。
- **D-SLIDE-2** 同一 `slides.json` 生成 PDF（cairo，真文字）、PNG 预览、PPTX（python-pptx 原生文本框/形状/表格，讲稿写入备注）。

## 挑战与进度

- **D-CH-1** 类型：概念、推演、探索、约束、纠错、解释、决策、实现、应用等按章选用（T08 的执行解释）；难度 Intro/Practice/Stretch 独立字段。
- **D-CH-2** 状态：未开始 / 尝试中 / 独立完成 / 看过答案后完成。看答案不扣分，可重置重试。
- **D-PROG-1** localStorage 键 `learning-clustering:v1`，结构 `{schemaVersion, savedAt, modules:{id:{challenges:{cid:{status,attempts,hintsUsed,updatedAt}}}}}`；导入时校验大小（<200KB）、schemaVersion、已知 moduleId/challengeId。

## 许可

- **D-LIC-1（用户已确认，2026-10-23）** 新写代码 MIT；新写教材、图解、影片、课件、字幕 CC BY 4.0。配乐由本课程用 NumPy 程序合成（`scripts/film/music.py`），权利归本课程，因此同样按 CC BY 4.0。复用材料保留原许可与署名：学生原作不复制进仓库，只署名并链接固定 commit；Module 05 引擎改写自作者本人 MIT 许可的 Lab05。
- **D-LIC-2（用户已确认，2026-10-23）** 字体统一为 Noto Sans SC（OFL 1.1），从 notofonts/noto-cjk 固定提交 `f8d1575` 下载 Regular / Bold 到 `fonts/noto-sans-sc/`（附 OFL.txt）。渲染时在进程范围内注册（CoreText，不安装到系统）。网站用 `scripts/build-fonts.py` 生成的 WOFF 子集；PDF 嵌入子集；PPTX 声明 Noto Sans SC。Noto 没有的上下标改为缩小并升降的普通字符绘制；影片代码行仍用 Menlo（只作为画面像素，不分发字体），课件中的代码也改用 Noto。

## 改版（2026-10-23）

- **D-RD-1** 每章四部影片，页面顺序：科普、精讲、进阶、实验演示；`film.json` schema 2，每部一个条目、每种语言一个版本。
- **D-RD-2** 双语字幕共用一条时间线：每条字幕的时长同时满足中文 4.5 字/秒与英文 15 字符/秒（各加 0.8 秒）；中文版画面字幕附小号英文。
- **D-RD-3** 科普片配乐用《We Never (Remix)》（作者指定，第三方，不在本课程许可内，不进仓库）；其余三部用课程原创合成配乐（CC BY 4.0）。
- **D-RD-4** Module 05 科普片直接使用作者原作《圈子从哪里来》（作者本人 CC BY 4.0），不重做。
- **D-RD-5** 进阶片的结论（异步严格改进必停、同步可振荡、顺序影响结果、size 上限变体）全部由引擎跑出的数字支撑，并有回归测试；字幕里的数字取自数据并 assert。
- **D-RD-6** 在线编程用自托管 Pyodide 0.28.3（MPL-2.0）与打包的 CodeMirror 6（MIT），代码只在访问者浏览器里运行。

## 待用户或教师确认（不阻塞）

- M09 与 Lab09 Multilevel 的对应（教师）。
- RW 候选 DAG 与平票（原作者 muranfei）。
- “jump”原意（教师）。
