#!/usr/bin/env node
// Writes python/<id>/README.md from content/modules/<id>/module.json so the exercise text
// on the page and in the download are the same. Run before packaging downloads.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const course = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/course.json'), 'utf8'));
for (const id of course.modules) {
  const m = JSON.parse(fs.readFileSync(path.join(ROOT, 'content/modules', id, 'module.json'), 'utf8'));
  const dir = path.join(ROOT, 'python', id);
  const fixtures = fs.readdirSync(path.join(dir, 'fixtures')).sort();
  // Run the reference once so the README shows real output from this exact package.
  let sample = '';
  try { sample = execFileSync('python3', ['reference.py'], { cwd: dir, encoding: 'utf8', timeout: 20000 }).trim(); } catch (e) { sample = `（运行失败：${e.message}）`; }
  const numpy = id === 'm06-spectral-bisection' ? '\n可选：NumPy（检查器中“与 NumPy 对照”一项需要它；没有时报 SKIP，不算通过）。' : '';
  const md = `# ${m.display} ${m.title} · Python 练习包

${m.pythonPackage.title}。来自 Learning Clustering 统一课程（${m.display}）。网页上的实验与挑战不需要 Python；这个包是可选的实现轨道。

## 环境

Python 3.9 或更新版本，只用标准库。${numpy}在任意空目录解压即可运行，不依赖课程仓库的其他文件。

## 文件

| 文件 | 用途 |
| --- | --- |
| \`starter.py\` | 起始代码：留有 TODO（\`NotImplementedError\`） |
| \`check.py\` | 检查器：逐项报告 PASS / FAIL / INCOMPLETE / ERROR / SKIP |
| \`reference.py\` | 参考实现：卡住时再看 |
| \`fixtures/\` | ${fixtures.map(f => `\`${f}\``).join('、')} |

## 运行

\`\`\`
python3 check.py              # 检查 starter.py（未完成的函数报 INCOMPLETE，不算通过）
python3 check.py reference.py # 参考实现应全部 PASS
python3 reference.py          # 看参考实现在本章例子上的输出
\`\`\`

全部 PASS 时退出码为 0；有 FAIL、ERROR 或 INCOMPLETE 时为 1。SKIP 表示缺少可选依赖而未运行，不是通过。

${m.pythonPackage.md}

## 参考实现的输出（本包实际运行）

\`\`\`
${sample}
\`\`\`

## 说明

- 检查器同时检查本章的手算例子和不在讲义中的新例子（随机图或新图），只记住答案无法通过。
- 原作者：${m.credits.student.name}（${m.sourceIssue.title}）。本练习包为统一课程新写；许可见课程仓库（拟定：代码 MIT）。
`;
  fs.writeFileSync(path.join(dir, 'README.md'), md);
  console.log('README', id);
  // English README for the English pack (python/<id>/en/), from module.en.json.
  const enDir = path.join(dir, 'en'), enJson = path.join(ROOT, 'content/modules', id, 'module.en.json');
  if (!fs.existsSync(enDir) || !fs.existsSync(enJson)) continue;
  const e = { ...m, ...JSON.parse(fs.readFileSync(enJson, 'utf8')) };
  e.pythonPackage = { ...m.pythonPackage, ...(e.pythonPackage || {}) };
  const sampleEn = sample; // same code, same output; the English reference reads ../fixtures only once packed
  fs.writeFileSync(path.join(enDir, 'README.md'), `# ${m.display} ${e.title} · Python exercise pack

${e.pythonPackage.title}. From the Learning Clustering course (${m.display}). You can also do this exercise in the browser on the module page, with nothing to install; this pack is for working offline.

## Requirements

Python 3.9 or newer, standard library only. Unzip into any empty folder; nothing else from the course repository is needed.

## Files

| File | Purpose |
| --- | --- |
| \`starter.py\` | Starter code with TODOs (\`NotImplementedError\`) |
| \`check.py\` | Checker: reports PASS / FAIL / INCOMPLETE / ERROR / SKIP for each check |
| \`reference.py\` | Reference solution, for when you are stuck |
| \`fixtures/\` | ${fixtures.map(f => `\`${f}\``).join(', ')} |

## Running

\`\`\`
python3 check.py --lang en              # check starter.py (unfinished functions report INCOMPLETE, never PASS)
python3 check.py reference.py --lang en # the reference passes every check
python3 reference.py                    # the reference on this module's example
\`\`\`

The exit code is 0 when everything passes, and 1 on any FAIL, ERROR or INCOMPLETE. SKIP means an optional dependency was missing and the check did not run; it is not a pass. Set \`COURSE_LANG=en\` to drop the \`--lang en\`.

${e.pythonPackage.md}

## Output of the reference (actually run for this pack)

\`\`\`
${sampleEn}
\`\`\`

## Notes

- The checker tests the hand-worked examples of the module and new examples that are not in the lesson, so memorised answers will not pass.
- Original author: ${m.credits.student.name} (${m.sourceIssue.title}). This pack was written for the unified course; code under MIT.
`);
  console.log('README (en)', id);
}
