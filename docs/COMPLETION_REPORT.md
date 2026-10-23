# 完成报告

日期 2026-10-23。范围：Clustering Issue #1–#8 → Module 02–09。未做 Partitioning / Multilevel。所有工作只在本地完成：没有创建远程仓库、没有推送、没有发布、没有在 Issue 上评论、没有联系任何人。

## 1. 交付内容

| 项 | 位置 | 数量 |
| --- | --- | --- |
| 算法引擎 | `site/engines/*.js` | 8（graph 公共 + affinity / merge / lp / spectral / kl / fm / rw） |
| 模块页 | `site/modules/<id>/index.html` | 8，另有首页、基础速查、术语表、如何挑战、学习记录、资源与贡献、404 |
| 影片 | `site/media/<id>/` | 10 部（M05、M09 各两部） |
| 课件 | `site/slides/<id>/`（PDF、PPTX、每页 PNG/JPG） | 8 套，共 96 页 |
| 挑战 | `site/modules/<id>/challenges.js` | 49 题，每题两级提示 |
| Python 练习 | `python/<id>/`、`site/downloads/<id>-python.zip` | 8 包 |
| 对照表 | `site/data/<id>/crosswalk.json` | 每个学习目标 → 讲义节、影片场景、课件页、挑战 |
| 旧路径入口 | `site/labs/<旧 slug>/` | Module 02–08；Module 09 不为 multilevel 生成 |

## 2. 验证命令与结果

| 命令 | 结果 |
| --- | --- |
| `./scripts/build.sh` | 成功 |
| `node --test tests/*.test.mjs` | 41 / 41 通过（引擎回归与性质 15、挑战 8、站点结构 18，含 GitHub Pages 路径大小写、CSS 字体地址、字体子集覆盖） |
| `python3 tests/crosscheck.py` | PASS：1324 项 JS ↔ Python 比较（M03、M05、M07、M08 逐步） |
| `python3 python/<id>/check.py python/<id>/reference.py` | 8 包全 PASS（6/7/6/7/8/5/8/5 项）；用 `python3 -I` 在仓库根目录运行结果相同 |
| `python3 python/<id>/check.py`（starter） | 均为 INCOMPLETE，无 FAIL |
| 课件文件核对（python-pptx + mdls） | 每套 PPTX 页数 = PDF 页数 = slides.json 页数，每页都有讲稿备注 |
| PDF 内嵌字体 | 8 套 PDF 都只嵌入 NotoSansSC-Regular / Bold 子集 |
| 网页字体（浏览器） | `noto-sans-sc-400.woff`、`-700.woff` 在 `/learning-clustering/` 子路径下 200 加载，`document.fonts` 状态 loaded |

教师反馈 24 项的逐条核对见 [teacher-feedback-verification.md](teacher-feedback-verification.md)。

## 3. 已修正的原作算法问题

- M03：原网页把 `[-亲和度, i, j]` 数组当字符串比较（“-5” < “-1” 不成立），首步错选 A–C@1。引擎保留 `legacyComparator` 复现原结果（cut 9/16/12/16），教学版逐字段比较（3/8/8/3）。
- M04：区分“下界证明不可能”“搜索证明不可能”“贪心卡住”“合法但非最优”四种结局，穷举 oracle 给出对照。
- M06：特征向量由 Jacobi 实时求解，不再使用三位小数的存储向量（残差 0.0044）；“无约束最优是单点”的说法用穷举证伪。
- M07：gain 公式（−2w）、最佳前缀包含空前缀、平票取较短前缀。
- M08：原 hill-climb 不是 FM。改为按 net 的引脚计数 gain、增量更新、桶结构；原文“9 → 4”的说法证伪，换成可验证的反例（cut 6 → 4，前两步 gain 为负）。
- M09：逻辑节点与物理实例分开表示；12 节点候选图标注为“候选复原”，平票规则为假设。

## 4. 浏览器实测（本地子路径 `/learning-clustering/`）

- 14 个页面在 375 px 宽度下都没有横向滚动（代码块在自身容器内滚动）。
- 实验台：方向键单步；伪代码高亮随事件变化（M03：第 1 行 → 3、4、6、7 行）；导出运行记录。
- localStorage 抛错时：页面正常渲染，实验与挑战可用，显示“进度只保留在这次打开的页面中”，无脚本错误。
- 进度导入：非 JSON 与错误版本号都被拒绝并给出原因。
- 不存在的地址返回 404 页，并能找回课程首页。
- 课件：画面下方即该页讲稿，支持搜索、缩略图、方向键翻页。
- 深链接：`#slides`、`#slide-<页 id>` 刷新后停在课件区并打开对应页；同一页内切换 `#slide-…` 也会翻到那一页（这一轮发现并修复：之前首次加载会把地址改成第 1 页，同页跳转不翻页）。

## 5. 媒体

| 模块 | 影片 | 时长 | 场景 | 字幕条 | 大小 |
| --- | --- | --- | --- | --- | --- |
| M02 | 谁和谁最亲近 | 3:21 | 10 | 35 | 13.7 MB |
| M03 | 合并，再合并 | 3:15 | 10 | 36 | 13.5 MB |
| M04 | 装得下吗 | 3:10 | 11 | 41 | 13.7 MB |
| M05 | 圈子从哪里来 | 2:57 | 12 | 37 | 14.2 MB |
| M05 | 一票一票（慢速推演） | 1:28 | 12 | 22 | 6.4 MB |
| M06 | 给每个点一个数 | 3:42 | 12 | 42 | 14.1 MB |
| M07 | 先试探，再回退 | 3:18 | 12 | 40 | 14.9 MB |
| M08 | 合法的那一步 | 3:45 | 12 | 45 | 15.3 MB |
| M09 | 关键路径的代价（上） | 3:00 | 9 | 34 | 12.6 MB |
| M09 | 关键路径的代价（下） | 2:22 | 8 | 28 | 11.3 MB |

1920×1080，H.264 + AAC，中文字幕烧录并另附 WebVTT，无配音，配乐为本课程用 NumPy 合成的原创音乐。画面文字全部为 Noto Sans SC（代码行为 Menlo），全部 10 部已按新字体重新渲染。所有字幕的停留时间都不短于阅读时长（字数 / 4.5 + 0.8 秒）。`site/` 总计约 146 MB，单个文件最大 15.3 MB。

## 6. 局限与未做的检查

- **没有逐帧人工审看完整影片**：每部片做过分镜静帧检查；换字体后抽查了 10 帧，修正了 M04 标签压住标题、M03 簇标签压住边权、M06 公式下标三处。
- **没有听审**：影片无配音；配乐由程序生成，没有人工试听评价。
- **没有真实设备与多浏览器矩阵**：只在本机内置浏览器（Chromium 内核）中测试，手机用 375 px 视口模拟。
- **公开地址未验证**：尚未部署；推送后需要在真实 GitHub Pages 地址上重做第 4 节的检查。
- **M09**：12 节点例子与平票规则是从原作影片复原的候选，待原作者确认；与教师目录 Lab 09（Multilevel）的对应待教师确认。
- **字体**：全部改用 Noto Sans SC（OFL 1.1，随仓库附许可）。PPTX 不能内嵌字体：没有安装 Noto Sans SC 的电脑会替换字体，课件区已提示免费安装途径；PDF 已内嵌。网站子集不含个别上下标与符号（ᵀ ₀ ⌈ 等 17 个），这些由访问者系统字体补字。
- **许可**：代码 MIT；内容、影片与原创配乐 CC BY 4.0；字体 OFL；学生原作保留原权利（`LICENSE-CONTENT.md`、`THIRD_PARTY_NOTICES.md`）。

## 7. 发布与公开地址验证（2026-10-23）

作者在线程中确认“push”后执行：

- 创建公开仓库 https://github.com/Su3037/learning-clustering ，推送单提交的 `publish` 分支为 `main`，开启 Pages（GitHub Actions）。
- 工作流 `pages` 第一次运行成功：测试作业（Node 引擎 / 挑战 / 站点测试、JS ↔ Python 交叉、8 个 Python 包）全部通过，随后部署。
- 公开地址 https://su3037.github.io/learning-clustering/ ：首页、模块页、字体、影片、PDF、Python 下载包、旧路径入口均返回 200；`/learning-clustering` 301 到带斜杠的地址；`labs/multilevel-clustering/` 为 404（按要求不跳转）；任意不存在路径返回 404 页，页面上的链接指回课程首页。
- 浏览器（公开地址）：网页字体两个字重均 loaded；M07 影片可播放（readyState 4）；实验单步正常；挑战 6 题渲染；`#slide-m08-walk` 打开第 5 页并停在课件区；375 px 宽无横向滚动；没有 4xx 资源请求。
- 仍未做：真实手机与多浏览器测试、完整影片的人工审看。
