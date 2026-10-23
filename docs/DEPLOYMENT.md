# 部署说明（已准备，等作者最终确认后执行）

**到目前为止没有创建远程仓库、没有推送、没有开启 Pages。**

## 目标

| 项 | 值 |
| --- | --- |
| 仓库 | `Su3037/learning-clustering`（公开） |
| 分支 | 本地 `publish`（与 `main` 文件完全相同、只有一个提交）推送为远程 `main` |
| Pages 来源 | GitHub Actions（`.github/workflows/pages.yml`：先跑测试，再上传 `site/`） |
| 公开地址 | https://su3037.github.io/learning-clustering/ |

站点只用相对路径，`404.html` 能从任意深度找回项目根，`site/.nojekyll` 关闭 Jekyll 处理。本地 `scripts/serve.py` 用同一个子路径 `/learning-clustering/` 模拟 Pages（包括 404 页）。`tests/site.test.mjs` 额外检查了 Pages 才会暴露的问题：路径大小写必须与文件名完全一致、CSS 中的字体地址、没有以 `/` 开头的绝对路径。

## 步骤（作者确认后）

```sh
gh repo create Su3037/learning-clustering --public --source . --remote origin \
  --description "Learning Clustering · 连接与分组：Module 02–09 中文聚类课程"
git push -u origin publish:main   # 只含当前文件的单个提交（约 168 MB），不带历次重渲染的旧影片
gh api -X POST repos/Su3037/learning-clustering/pages -f build_type=workflow
gh run watch    # 等 pages 工作流跑完
```

推送后要在公开地址上再验证一次（不能用 localhost 代替）：首页、8 个模块页的影片与课件、下载、深链接刷新、404、移动端、字体加载。

## 体积

推送的 `publish` 分支是当前文件树的单个提交，约 168 MB；本地 `main` 保留完整开发历史（约 318 MB，含旧版影片），不推送。单个文件最大约 15 MB，远低于 GitHub 的 100 MB 单文件限制，也低于 Pages 站点 1 GB 的上限。若以后影片变大，可以把 MP4 移到 Release 附件或其他静态托管，只需改 `film.json` 的 `src`。

## 兼容旧路径

`site/labs/<旧 slug>/index.html` 为 Module 02–08 保留了教师原目录风格的旧路径入口（跳转到新模块）。**Module 09 没有为 `multilevel-clustering` 生成入口**：RW 不接管 Multilevel 的旧地址。

## 进度迁移

各同学原网站在不同域名下，浏览器不允许本站读取它们的 localStorage，因此不会自动迁移旧进度。“学习记录”页提供导出 / 导入（JSON，带结构校验）。
