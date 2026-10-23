# 构建与复现

所有命令在仓库根目录运行。网站本身是纯静态文件（`site/`），访问者不需要安装任何东西；下面的工具只用于**重新生成**页面、影片和课件。

## 需要的工具

| 用途 | 工具 | 本次实测版本 |
| --- | --- | --- |
| 页面、trace、测试 | Node.js ≥ 20 | 26.5.0 |
| Python 练习、交叉测试、影片 | Python ≥ 3.9，NumPy | 3.13.9，NumPy 2.3.5 |
| 新影片套件 | pycairo、Pillow；实验演示录制用 Playwright（Chromium） | pycairo 1.29 |
| 影片逐帧绘制 / 课件 PDF | libcairo（`brew install cairo`；通过 ctypes 调用，不需要 pycairo） | Homebrew cairo |
| 编码 | FFmpeg（libx264、aac） | 本机 Homebrew 版 |
| 可编辑 PPTX | python-pptx | 1.0.2 |
| 中文字体 | 仓库自带 Noto Sans SC（`fonts/noto-sans-sc/`，OFL）。macOS 上渲染脚本在进程内注册，不用安装；其他系统请先安装这两个文件（fontconfig 能找到即可） | noto-cjk `f8d1575` |
| 网站字体子集 | fontTools（`scripts/build-fonts.py`；没有时保留已提交的子集） | 4.60.1 |

## 一步步

```sh
# 1. 数据与页面（快，几秒）：trace → 挑战元数据 → 页面 → 网站字体子集 → 练习包 README 与 zip
./scripts/build.sh

# 2. 影片（每部约 10–40 秒渲染）：先出静帧审片，再出成片
python3 scripts/film/render.py m07-kernighan-lin --stills          # build/<id>/*-contact.jpg
python3 scripts/film/render.py m07-kernighan-lin --sample 96.7 137 # 代表性小样 → build/samples/
python3 scripts/film/render.py m07-kernighan-lin                    # → site/media/<id>/
#   成片同时写出 .zh.vtt、poster、film.json（实际章节时间、场景时间、全文字幕）

# 3. 课件（影片之后：页角的“影片 mm:ss”取自 film.json）
python3 scripts/slides/build_slides.py m07-kernighan-lin           # → site/slides/<id>/ PDF + PPTX + 预览
#   需要能 import pptx 的 Python；本机用的是 ~/.cache/codex-runtimes/.../python/bin/python3

# 4. 再跑一次 ./scripts/build.sh，让页面读到新的影片与课件信息
./scripts/build.sh

# 5. 测试
node --test tests/*.test.mjs        # 引擎回归、挑战判定、站点静态检查
python3 tests/crosscheck.py         # JS 引擎 ↔ 独立 Python 参考
for d in python/m0*; do python3 $d/check.py $d/reference.py; done
python3 scripts/research/rw_no_replication.py   # M09 不复制时的穷举对照
```

## 四部影片（新管线，Module 05 起）

每章四部：科普（popular）、精讲（concise）、进阶（advanced）、实验演示（lab）。每部都有中文版与英文版（`<film>.zh.mp4` / `<film>.en.mp4`），`film.json` 为 schema 2。

```sh
# 精讲、进阶：video/<id>/films.py（scripts/film/cine.py 绘图套件，pycairo + Pillow）
python3 scripts/film/cinema.py m05-label-propagation --film concise --stills            # 每种语言一张审片接触表
python3 scripts/film/cinema.py m05-label-propagation --film advanced --lang en --sample 20 40
python3 scripts/film/cinema.py m05-label-propagation                                    # 全部 → site/media/<id>/

# 实验演示：Playwright 录制真实页面（先在本地起服务），再合成
python3 scripts/serve.py 8800
node video/m05-label-propagation/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh
node video/m05-label-propagation/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ en
python3 scripts/film/walkthrough.py m05-label-propagation

# Module 05 的科普片是作者原作，按原样导入
python3 video/m05-label-propagation/import_story.py
```

配乐：精讲、进阶、实验演示用课程原创的 NumPy 合成配乐（`score:<mood>`）。科普片按作者的选择用《We Never (Remix)》（`track:wenever`）；这段录音是第三方作品，**不进仓库**：设置 `LC_MUSIC_WENEVER=/path/to/audio`，或放在 `/mnt/project-files/private-music/wenever.m4a`。

字幕时长：每条字幕同时满足中文（4.5 字/秒）与英文（15 字符/秒）的最短阅读时间，两种语言共用一条时间线；`readingViolations` 必须为 0（测试会检查）。

## 本地预览（模拟 GitHub Pages 子路径）

```sh
python3 scripts/serve.py 8790            # http://127.0.0.1:8790/learning-clustering/
```

必须通过 HTTP 打开：直接双击 HTML 时，浏览器会阻止 ES module。

## 文件从哪里来

| 产物 | 来源 | 生成脚本 |
| --- | --- | --- |
| `site/modules/<id>/index.html` | `content/modules/<id>/module.json` + `lesson.md` | `scripts/build-site.mjs` |
| `site/data/<id>/traces.json` | `site/engines/*.js` 真实运行 | `scripts/build-traces.mjs` |
| `site/media/<id>/*.mp4/.vtt/film.json`（旧管线） | `video/<id>/film.py` + traces | `scripts/film/render.py` |
| `site/media/<id>/<film>.<lang>.*`（四部影片） | `video/<id>/films.py`、`walkthrough.mjs` | `scripts/film/cinema.py`、`scripts/film/walkthrough.py` |
| `site/slides/<id>/*` | `content/modules/<id>/slides.json` + `video/<id>/figures.py` | `scripts/slides/build_slides.py` |
| `site/downloads/<id>-python.zip` | `python/<id>/` | `scripts/package-downloads.mjs` |
| `site/assets/fonts/*.woff` | `fonts/noto-sans-sc/*.otf`，按全站用字裁剪 | `scripts/build-fonts.py` |
| `site/data/<id>/crosswalk.json` | `content/modules/<id>/crosswalk.json` + 实际影片/课件 | `scripts/build-site.mjs` |
