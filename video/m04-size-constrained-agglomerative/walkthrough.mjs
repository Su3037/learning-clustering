// Module 04 experiment walkthrough: records the real lab and code lab, one pass per language.
//   node video/m04-size-constrained-agglomerative/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh build/m04-size-constrained-agglomerative/walk-zh
// then: python3 scripts/film/walkthrough.py m04-size-constrained-agglomerative
import { Recorder } from '../../scripts/film/recorder.mjs';

const [base, lang = 'zh', out = `build/m04-size-constrained-agglomerative/walk-${lang}`] = process.argv.slice(2);
const url = new URL(`${lang === 'en' ? 'en/' : ''}modules/m04-size-constrained-agglomerative/index.html`, base).href;
const rec = await Recorder.start({ url, lang, out });
const p = rec.page, t = (zh, en) => rec.t(zh, en);
const lab = p.locator('#lab-root');
const btn = (root, zh, en) => root.getByRole('button', { name: t(zh, en), exact: false }).first();
const sel = (root, zh, en) => root.locator('label', { hasText: t(zh, en) }).locator('select').first();
const CH = {
  lab: { zh: '实验台', en: 'THE LAB' }, diag: { zh: '诊断', en: 'DIAGNOSIS' }, code: { zh: '在线编程', en: 'CODE LAB' }, viz: { zh: '用你的代码跑', en: 'YOUR CODE, VISUALISED' }, end: { zh: '挑战', en: 'CHALLENGES' }
};
const step = r => r.click(btn(lab, '下一步', 'Next step'));
const toEnd = r => r.click(btn(lab, '跳到结束', 'To the end'));

await rec.scrollTo('#lab', { duration: 10 });
await rec.shot({ chapter: CH.lab, zh: '这是本章的实验台：选例子、目标 K 和容量 C，还可以改每个节点的大小。', en: 'This is the chapter\'s lab: choose an example, the target K and the capacity C, and change any node\'s size.' },
  async r => { await r.moveTo(sel(lab, '例子', 'Example')); await r.moveTo(sel(lab, '容量 C', 'Capacity C')); await r.moveTo(lab.locator('input[type=number]')); await r.wait(600); }, { hold: 1 });
await rec.shot({ zh: 'G01、容量 2：第一步合并 A–B，大小 2，合法。', en: 'G01 at capacity 2: step one merges A–B, size 2, legal.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(1400); });
await rec.shot({ zh: '第二步：亲和度最大的 AB–C 大小 3，超容量，标红跳过；改选 D–E。', en: 'Step two: the highest-affinity AB–C has size 3, over capacity, marked red and skipped; D–E instead.', zoom: '#lab-root .lab-side' },
  async r => { await step(r); await r.wait(1800); });
await rec.shot({ zh: '跳到结束：停在 AB | C | DE。报告分开写：合法，但没有达到 K。', en: 'Jump to the end: it stops at AB | C | DE. The report is separate: legal, but K is not reached.', zoom: '#lab-root .lab-side' },
  async r => { await toEnd(r); await r.wait(1800); });

const diag = lab.locator('.lab-diag .decision');
await rec.shot({ chapter: CH.diag, zh: '诊断栏：下界 ⌈5/2⌉ = 3 已经大于 K，目标不可能，贪心停下不是错。', en: 'The diagnosis: the bound ⌈5/2⌉ = 3 already exceeds K, so the target is impossible and greedy stopping is not a mistake.', zoom: '#lab-root .lab-diag' },
  async r => { await r.scrollTo('#lab-root .lab-diag', { offset: 260 }); await r.moveTo(diag); await r.wait(2000); });
await rec.shot({ zh: '换成原作者的 greedy_trap：贪心停在 3 簇，可穷举找到合法的 AC | BD。诊断：贪心卡住。', en: 'Switch to the original author\'s greedy_trap: greedy stops at 3 clusters, yet search finds the legal AC | BD. Diagnosis: greedy is stuck.', zoom: '#lab-root .lab-diag' },
  async r => { await r.choose(sel(lab, '例子', 'Example'), 'trap'); await r.wait(600); await r.moveTo(diag); await r.wait(2200); });
await rec.shot({ zh: 'suboptimal：贪心 cut 18，穷举最优 11。合法、达到 K，但不是最优。', en: 'suboptimal: greedy cut 18, the exhaustive optimum 11. Legal and K reached, but not optimal.', zoom: '#lab-root .lab-diag' },
  async r => { await r.choose(sel(lab, '例子', 'Example'), 'sub'); await r.wait(600); await r.moveTo(diag); await r.wait(2200); });
await rec.shot({ chapter: CH.lab, zh: '回到 G01，容量 3，把 A 的大小改成 2：结果从 ABC | DE 变成 AB | CDE，cut 5。', en: 'Back to G01 at capacity 3, with A\'s size set to 2: the result changes from ABC | DE to AB | CDE, cut 5.', zoom: '#lab-root .lab' },
  async r => {
    await r.scrollTo('#lab', { offset: 90 });
    await r.choose(sel(lab, '例子', 'Example'), 'g01'); await r.choose(sel(lab, '容量 C', 'Capacity C'), '3');
    await r.click(lab.locator('input[type=number]'), { after: 150 }); await p.keyboard.press('Control+A'); await p.keyboard.type('2', { delay: 120 }); await p.keyboard.press('Tab');
    await r.wait(500); await toEnd(r); await r.wait(2000);
  });

// ---- code lab
const cl = p.locator('#codelab-root');
const idle = () => p.waitForTimeout(300).then(() => p.waitForFunction(() => !document.querySelector('#codelab-root .cl-bar button').disabled, null, { timeout: 90000 }));
await rec.scrollTo('#codelab-root', { duration: 10 });
await cl.locator('.cm-editor').waitFor({ timeout: 30000 });
await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#codelab-root .cl-bar', { offset: 130, duration: 1200 });
await rec.shot({ chapter: CH.code, zh: '在线编程：代码在浏览器里运行，不用安装 Python。贪心主循环和穷举 oracle 已经写好。', en: 'The code lab: your code runs in the browser, with no Python to install. The greedy loop and the exhaustive oracle are already written.' },
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
await rec.shot({ zh: '任务一：四项分开报告。合法看每簇大小，达到 K 看簇数，停止原因由主循环给出。', en: 'Task 1: report four separate items. Legal checks every cluster\'s size, K reached checks the count, and the main loop gives the stop reason.', zoom: '#codelab-root .cl-editor' },
  async r => { await replaceLine(r, 'NotImplementedError("report")', 'return {"count": len(parts), "capacity_compliant": capacity is None or all(sum(size[n] for n in p) <= capacity for p in parts), "target_reached": len(parts) <= k, "stop_reason": stop}'); await r.wait(900); });
await rec.shot({ zh: '任务二：分类。没达到 K 时，先看下界，再看穷举；达到 K 时，比较 cut。', en: 'Task 2: classify. If K is not reached, check the bound, then the search; if it is, compare the cuts.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("classify")',
      'r, o = solve(graph, k, capacity), oracle(graph, k, capacity)\nif not r["target_reached"]:\nif o["lower_bound"] > k:\nreturn "infeasible-by-bound"\n<return "greedy-stuck" if o["best_cut_at_k"] else "infeasible-by-search"\n<if o["best_cut_at_k"] and o["best_cut_at_k"][0] < r["cutsize"]:\nreturn "feasible-suboptimal"\n<return "reached-and-optimal-here"');
    await r.wait(900);
  });
await rec.shot({ zh: '运行检查：全部通过，包括超容量的单点和没有边的图。', en: 'Run the checks: everything passes, including an over-capacity node and a graph with no edges.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2400); });

const viz = p.locator('#codelab-root .cl-viz');
await rec.scrollTo('#codelab-root .cl-viz', { offset: 140, duration: 900 });
await rec.shot({ chapter: CH.viz, zh: '下面用你写的函数跑 8 个情形，包括一张新图，逐项对照课程引擎。', en: 'Below, your functions run on eight cases, including a new graph, compared item by item with the course engine.' },
  async r => {
    await r.click(btn(viz, '用我的代码运行', 'Run my code'), { after: 100 });
    await r.offscreen(() => p.waitForFunction(() => /ok|no/.test(document.querySelector('#codelab-root .cl-viz .match')?.className || ''), null, { timeout: 60000 }));
    await r.wait(1600);
  });
await rec.shot({ zh: '五种诊断都出现了，全部一致。点 greedy_trap 那一行，左边画出你的结果。', en: 'All five diagnoses appear, and all agree. Click the greedy_trap row to draw your result on the left.' },
  async r => { await r.click(viz.locator('table.codelab-cases tbody tr').nth(3)); await r.wait(2400); });

await rec.scrollTo('#challenges', { duration: 900 });
await rec.shot({ chapter: CH.end, zh: '最后做挑战题，确认自己真的懂了。结果只保存在你的浏览器里。', en: 'Finally, try the challenges to check you really understand. Results stay in your browser.' },
  async r => { await r.moveTo(p.locator('#challenge-root').first(), { dy: 0.2 }); await r.wait(1500); }, { hold: 1.5 });
await rec.finish({ module: 'm04-size-constrained-agglomerative', url });
