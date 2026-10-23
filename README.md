# Learning Clustering · 连接与分组

一门中文的聚类入门课，把 eda-learning 课程中 8 份已关闭的 Clustering 提交（Issue #1–#8）整合成 Module 02–09：

| Module | 主题 |
| --- | --- |
| 02 | 亲和度指标 |
| 03 | 贪心成对合并 |
| 04 | 容量约束凝聚聚类 |
| 05 | 标签传播 |
| 06 | 谱二分 |
| 07 | Kernighan–Lin |
| 08 | Fiduccia–Mattheyses |
| 09 | Rajaraman–Wong 延迟导向聚类（与教师目录 Lab 09 Multilevel 的对应关系待确认） |

公开地址（发布后）：https://su3037.github.io/learning-clustering/

每个模块包含：二维讲解短片（中文字幕、无配音、原创配乐）、带页码与讲稿的课件（网页 / PDF / PPTX）、讲义与伪代码、由真实算法引擎驱动的实验台、带两级提示的挑战题、Python 练习包（starter / reference / check / fixtures）。

## 本地运行

```sh
python3 scripts/serve.py 8790
# 打开 http://127.0.0.1:8790/learning-clustering/（与 GitHub Pages 的子路径一致）
```

站点是纯静态文件（`site/`），不依赖 CDN，只用相对路径，可以部署在任意子路径下。

## 构建与测试

```sh
./scripts/build.sh                 # trace → 挑战元数据 → 页面 → 下载包
node --test tests/*.test.mjs       # 引擎、挑战、站点结构（38 项）
python3 tests/crosscheck.py        # JS 引擎与 Python 参考实现逐步对照
python3 python/m07-kernighan-lin/check.py python/m07-kernighan-lin/reference.py
```

影片与课件的重新生成见 [docs/BUILD.md](docs/BUILD.md)，部署见 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)。

## 目录

- `site/`：发布内容（引擎 `site/engines/`、公共组件 `site/assets/`、各模块页、媒体、课件、下载）
- `content/`：课程文本源（每模块 `module.json`、`module.md` 大纲、`lesson.md`、`slides.json`）
- `video/`、`scripts/film/`：影片脚本与渲染器（cairo + FFmpeg）
- `scripts/slides/`：课件生成（PDF / PNG / PPTX）
- `python/`：练习包
- `tests/`：自动测试
- `docs/`：构建、部署、教师反馈核对、完成报告

## 来源与许可

各模块的原作者、原仓库与保留内容见站内“资源与贡献”页和 `THIRD_PARTY_NOTICES.md`。新写的代码按 MIT（`LICENSE`）；新写的教材、图解、影片、课件、字幕与原创配乐按 CC BY 4.0（`LICENSE-CONTENT.md`）；字体 Noto Sans SC 按 SIL OFL 1.1（`fonts/noto-sans-sc/OFL.txt`）。学生原作保留各自作者的权利与许可。
