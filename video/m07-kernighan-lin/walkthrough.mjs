// Module 07 experiment walkthrough: records the real lab and code lab, one pass per language.
//   node video/m07-kernighan-lin/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh build/m07-kernighan-lin/walk-zh
// then: python3 scripts/film/walkthrough.py m07-kernighan-lin
import { Recorder } from '../../scripts/film/recorder.mjs';

const [base, lang = 'zh', out = `build/m07-kernighan-lin/walk-${lang}`] = process.argv.slice(2);
const url = new URL(`${lang === 'en' ? 'en/' : ''}modules/m07-kernighan-lin/index.html`, base).href;
const rec = await Recorder.start({ url, lang, out });
const p = rec.page, t = (zh, en) => rec.t(zh, en);
const lab = p.locator('#lab-root');
const btn = (root, zh, en) => root.getByRole('button', { name: t(zh, en), exact: false }).first();
const sel = (root, zh, en) => root.locator('label', { hasText: t(zh, en) }).locator('select').first();
const CH = {
  lab: { zh: '实验台', en: 'THE LAB' }, seed: { zh: '换种子、改边权', en: 'SEEDS AND WEIGHTS' }, code: { zh: '在线编程', en: 'CODE LAB' }, viz: { zh: '用你的代码跑', en: 'YOUR CODE, VISUALISED' }, end: { zh: '挑战', en: 'CHALLENGES' }
};
const step = r => r.click(btn(lab, '下一步', 'Next step'));
const toEnd = r => r.click(btn(lab, '跳到结束', 'To the end'));
const seedSel = () => sel(lab, '初始二分', 'Initial bisection');

await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#lab-root', { offset: 110, duration: 900 });
await rec.shot({ chapter: CH.lab, zh: '这是本章的实验台：选初始二分，还可以改任意一条边的权重。', en: 'This is the chapter\'s lab: choose the initial bisection, and change any edge\'s weight.' },
  async r => { await r.moveTo(seedSel()); await r.moveTo(sel(lab, '改一条边', 'Change an edge')); await r.wait(600); }, { hold: 1 });
await rec.shot({ zh: '第 1 轮开始：种子 AE | BCD，cut 12，全部解锁。', en: 'Pass 1 starts: seed AE | BCD, cut 12, everything unlocked.', zoom: '#lab-root .lab' },
  async r => { await r.moveTo(lab.locator('.lab-side .status').first()); await r.wait(1400); });
await rec.shot({ zh: '第一次试探：候选表里 A↔D 收益 +9 最大，cut 12 → 3，两点锁定。', en: 'The first trial: in the candidate table A↔D has the largest gain, +9; cut 12 → 3, and both lock.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(2000); });
await rec.shot({ zh: '第二次试探：剩下的全是负数，照样走 E↔C，收益 −8，cut 暂升到 11。', en: 'The second trial: everything left is negative; E↔C goes anyway, gain −8, and the cut rises to 11 for now.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(2000); });
await rec.shot({ zh: '本轮结束：累计 +9、+1，金框标出最佳前缀 k = 1，图回退到 cut 3。', en: 'The pass ends: cumulative +9, +1; the gold box marks the best prefix, k = 1, and the graph rolls back to cut 3.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(2200); });
await rec.shot({ zh: '跳到结束：第二轮累计 −8、−6，空前缀胜出，算法停在 cut 3。', en: 'Jump to the end: pass 2\'s totals are −8, −6; the empty prefix wins and the algorithm stops at cut 3.', zoom: '#lab-root .lab' },
  async r => { await toEnd(r); await r.wait(2200); });

await rec.shot({ chapter: CH.seed, zh: '换成种子 AB | CDE：两次试探都亏，第一轮就是空前缀，停在 cut 5。', en: 'Switch to seed AB | CDE: both trials lose, pass 1 already keeps the empty prefix, and it stops at cut 5.', zoom: '#lab-root .lab' },
  async r => { await r.choose(seedSel(), 'AB|CDE'); await r.wait(600); await toEnd(r); await r.wait(2400); });
await rec.shot({ zh: '回到 AE | BCD，把 A–B 改成 1：初始 cut 变成 8，A↔D 的收益变成 5。', en: 'Back to AE | BCD with A–B set to 1: the initial cut becomes 8, and A↔D\'s gain becomes 5.', zoom: '#lab-root .lab' },
  async r => {
    await r.choose(seedSel(), 'AE|BCD'); await r.wait(400);
    await r.choose(sel(lab, '改一条边', 'Change an edge'), 'A|B');
    await r.click(lab.locator('input[type=number]'), { after: 150 }); await p.keyboard.press('Control+A'); await p.keyboard.type('1', { delay: 120 }); await p.keyboard.press('Tab');
    await r.wait(600); await step(r); await r.wait(2400);
  });

// ---- code lab
const cl = p.locator('#codelab-root');
const idle = () => p.waitForTimeout(300).then(() => p.waitForFunction(() => !document.querySelector('#codelab-root .cl-bar button').disabled, null, { timeout: 90000 }));
await rec.scrollTo('#codelab-root', { duration: 10 });
await cl.locator('.cm-editor').waitFor({ timeout: 30000 });
await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#codelab-root .cl-bar', { offset: 130, duration: 1200 });
await rec.shot({ chapter: CH.code, zh: '在线编程：代码在浏览器里运行，不用安装 Python。一轮的框架和外层循环已经写好。', en: 'The code lab: your code runs in the browser, with no Python to install. The pass driver and the outer loop are already written.' },
  async r => { await r.moveTo(cl.locator('.cl-editor')); await r.wait(900); }, { hold: 1 });
await rec.shot({ zh: '先运行检查：两个任务都还没写，结果是 INCOMPLETE。', en: 'Run the checks first: neither task is written yet, so the result is INCOMPLETE.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(1600); });

async function replaceLine(r, needle, code) {
  await p.evaluate(n => {
    const view = document.querySelector('#codelab-root .cl-editor').editorView;
    const text = view.state.doc.toString(), at = text.indexOf(n);
    const line = view.state.doc.lineAt(at), indent = line.text.match(/^\s*/)[0].length;
    view.dispatch({ selection: { anchor: line.from + indent, head: line.to }, scrollIntoView: true });
    view.focus();
  }, needle);
  await r.wait(300);
  await r.moveTo(cl.locator('.cm-line', { hasText: needle }).first(), { dx: 0.6 });
  await r.wait(250);
  await r.type(code, { delay: 30 });
}
await rec.shot({ zh: '任务一：在未锁定的左右节点之间找收益最大的一对，g = D(a) + D(b) − 2w；负收益也要返回。', en: 'Task 1: find the unlocked left/right pair with the largest gain, g = D(a) + D(b) − 2w; return it even when negative.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("best_swap")',
      'D = d_values(adj, side)\nbest = None\nfor a in sorted(v for v in adj if side[v] == 0 and v not in locked):\nfor b in sorted(v for v in adj if side[v] == 1 and v not in locked):\nw = adj[a].get(b, 0)\ng = D[a] + D[b] - 2 * w\nif best is None or g > best["gain"]:\nbest = {"a": a, "b": b, "gain": g, "Da": D[a], "Db": D[b], "w": w}\n<<<return best');
    await r.wait(900);
  });
await rec.shot({ zh: '任务二：最佳前缀。累计收益严格变大才更新，k = 0 是合法答案。', en: 'Task 2: the best prefix. Update only when the running total is strictly larger; k = 0 is a valid answer.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("best_prefix")',
      'best_k, best, total = 0, 0, 0\nfor i, g in enumerate(gains, 1):\ntotal += g\nif total > best:\nbest_k, best = i, total\n<<return best_k, best');
    await r.wait(900);
  });
await rec.shot({ zh: '运行检查：全部通过，包括 120 个随机图上的人数、锁定和“收益 = cut 差”。', en: 'Run the checks: everything passes, including side sizes, locking and “gain = cut difference” on 120 random graphs.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2400); });

const viz = p.locator('#codelab-root .cl-viz');
await rec.scrollTo('#codelab-root .cl-viz', { offset: 140, duration: 900 });
await rec.shot({ chapter: CH.viz, zh: '下面用你写的函数跑 6 个情形，逐轮对照课程引擎：交换哪一对、收益、保留几步。', en: 'Below, your functions run on six cases, compared pass by pass with the course engine: which pair, what gain, how many steps kept.' },
  async r => {
    await r.click(btn(viz, '用我的代码运行', 'Run my code'), { after: 100 });
    await r.offscreen(() => p.waitForFunction(() => /ok|no/.test(document.querySelector('#codelab-root .cl-viz .match')?.className || ''), null, { timeout: 60000 }));
    await r.wait(1600);
  });
await rec.shot({ zh: '点新图那一行：第一步 −1，第二步 +7，保留前两步，cut 从 7 降到 1。', en: 'Click the new graph\'s row: step one is −1, step two +7; keeping two steps takes the cut from 7 to 1.' },
  async r => { await r.click(viz.locator('table.codelab-cases tbody tr').nth(5)); await r.wait(2600); });

await rec.scrollTo('#challenges', { duration: 900 });
await rec.shot({ chapter: CH.end, zh: '最后做挑战题，确认自己真的懂了。结果只保存在你的浏览器里。', en: 'Finally, try the challenges to check you really understand. Results stay in your browser.' },
  async r => { await r.moveTo(p.locator('#challenge-root').first(), { dy: 0.2 }); await r.wait(1500); }, { hold: 1.5 });
await rec.finish({ module: 'm07-kernighan-lin', url });
