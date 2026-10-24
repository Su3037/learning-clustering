// Module 08 experiment walkthrough: records the real lab and code lab, one pass per language.
//   node video/m08-fiduccia-mattheyses/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh build/m08-fiduccia-mattheyses/walk-zh
// then: python3 scripts/film/walkthrough.py m08-fiduccia-mattheyses
import { Recorder } from '../../scripts/film/recorder.mjs';

const [base, lang = 'zh', out = `build/m08-fiduccia-mattheyses/walk-${lang}`] = process.argv.slice(2);
const url = new URL(`${lang === 'en' ? 'en/' : ''}modules/m08-fiduccia-mattheyses/index.html`, base).href;
const rec = await Recorder.start({ url, lang, out });
const p = rec.page, t = (zh, en) => rec.t(zh, en);
const lab = p.locator('#lab-root');
const btn = (root, zh, en) => root.getByRole('button', { name: t(zh, en), exact: false }).first();
const sel = (root, zh, en) => root.locator('label', { hasText: t(zh, en) }).locator('select').first();
const CH = {
  lab: { zh: '实验台', en: 'THE LAB' }, seed: { zh: '换个例子', en: 'OTHER EXAMPLES' }, code: { zh: '在线编程', en: 'CODE LAB' }, viz: { zh: '用你的代码跑', en: 'YOUR CODE, VISUALISED' }, end: { zh: '挑战', en: 'CHALLENGES' }
};
const step = r => r.click(btn(lab, '下一步', 'Next step'));
const toEnd = r => r.click(btn(lab, '跳到结束', 'To the end'));
const exSel = () => sel(lab, '例子', 'Example');

await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#lab-root', { offset: 110, duration: 900 });
await rec.shot({ chapter: CH.lab, zh: '这是本章的白盒实验台：选例子，再选平衡窗口 maxDiff。', en: 'This is the chapter\'s white-box lab: pick an example, then the balance window maxDiff.' },
  async r => { await r.moveTo(exSel()); await r.moveTo(sel(lab, '平衡 maxDiff', 'Balance maxDiff')); await r.wait(600); }, { hold: 1 });
await rec.shot({ zh: '第 1 轮开始：种子 AE | BCD，cut 12。表里 A、E 收益 +6 最大，却标着“不合法”。', en: 'Pass 1 starts: seed AE | BCD, cut 12. In the table A and E have the largest gain, +6, yet are marked not legal.', zoom: '#lab-root .lab' },
  async r => { await r.moveTo(lab.locator('.lab-side .decision').first()); await r.wait(1600); });
await rec.shot({ zh: '第 1 步：A、E 被平衡挡住（红圈），合法的 D 收益 +3 最大，移动后 cut 9。', en: 'Step 1: A and E are blocked by the balance (red rings); D, legal with +3, is largest, and the cut becomes 9.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(2200); });
await rec.shot({ zh: '第 2 步：左侧有 3 人了，A 变得合法：+6，cut 3。', en: 'Step 2: the left now has 3 nodes, so A is legal: +6, cut 3.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(2200); });
await rec.shot({ zh: '跳到结束：C、E、B 都是负收益；保留最佳前缀 k* = 2，cut 3；第二轮空前缀，停止。', en: 'Jump to the end: C, E, B all lose; the best prefix k* = 2 is kept, cut 3; pass 2\'s prefix is empty, so it stops.', zoom: '#lab-root .lab' },
  async r => { await toEnd(r); await r.wait(2400); });

await rec.shot({ chapter: CH.seed, zh: '换成替换反例：一开始每个合法移动都亏；A −1、B −1 之后，E 收益 +4，cut 4。', en: 'Switch to the replacement example: at first every legal move loses; after A −1 and B −1, E gains +4, and the cut is 4.', zoom: '#lab-root .lab' },
  async r => { await r.choose(exSel(), 'escape'); await r.wait(700); for (let i = 0; i < 3; i++) { await step(r); await r.wait(900); } await r.wait(1400); });
await rec.shot({ zh: '拓展：bus 是一个 4 引脚 net（紫色虚线）。收益按两侧引脚计数，不把 net 拆成边。', en: 'Extension: bus is a 4-pin net (dashed violet). Gains count its pins on each side; the net is not split into edges.', zoom: '#lab-root .lab' },
  async r => { await r.choose(exSel(), 'multi'); await r.wait(700); await step(r); await r.wait(2400); });

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
await rec.shot({ zh: '任务一：收益。对 v 所在的每个 net 数两侧引脚：F 侧只有 v 就 +w，T 侧没有引脚就 −w。', en: 'Task 1: the gain. For each net that contains v, count its pins per side: only v on F gives +w, none on T gives −w.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("gain")',
      'F, T = side[v], 1 - side[v]\ng, fs, te = 0, [], []\nfor n in nets:\nif v not in n["pins"]:\ncontinue\n<on_f = sum(1 for p in n["pins"] if side[p] == F)\non_t = len(n["pins"]) - on_f\nif on_f == 1:\ng += n["w"]\nfs.append(n["id"])\n<if on_t == 0:\ng -= n["w"]\nte.append(n["id"])\n<<return g, fs, te');
    await r.wait(900);
  });
await rec.shot({ zh: '任务二：合法候选。未锁定、且移动后仍满足平衡的节点，按名字排序。', en: 'Task 2: the legal candidates. The unlocked nodes that stay balanced after moving, sorted by name.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("legal_moves")',
      'return [v for v in sorted(side) if v not in locked and balance_ok({**side, v: 1 - side[v]}, max_diff)]');
    await r.wait(900);
  });
await rec.shot({ zh: '运行检查：全部通过，包括审查原 hillclimb 数据、多引脚 net 和 150 个随机图。', en: 'Run the checks: everything passes, including the audit of the hillclimb data, multi-pin nets and 150 random graphs.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2400); });

const viz = p.locator('#codelab-root .cl-viz');
await rec.scrollTo('#codelab-root .cl-viz', { offset: 140, duration: 900 });
await rec.shot({ chapter: CH.viz, zh: '下面用你写的函数跑 7 个情形，逐轮对照课程引擎：移动哪个点、收益、保留几步。', en: 'Below, your functions run on seven cases, compared pass by pass with the course engine: which node, what gain, how many steps kept.' },
  async r => {
    await r.click(btn(viz, '用我的代码运行', 'Run my code'), { after: 100 });
    await r.offscreen(() => p.waitForFunction(() => /ok|no/.test(document.querySelector('#codelab-root .cl-viz .match')?.className || ''), null, { timeout: 60000 }));
    await r.wait(1600);
  });
await rec.shot({ zh: '点六点环那一行：三轮，第二轮先 −2 再 +4，最后 cut 2。', en: 'Click the ring of six: three passes; pass 2 takes −2 before +4, ending at cut 2.' },
  async r => { await r.click(viz.locator('table.codelab-cases tbody tr').nth(5)); await r.wait(2600); });

await rec.scrollTo('#challenges', { duration: 900 });
await rec.shot({ chapter: CH.end, zh: '最后做挑战题，确认自己真的懂了。结果只保存在你的浏览器里。', en: 'Finally, try the challenges to check you really understand. Results stay in your browser.' },
  async r => { await r.moveTo(p.locator('#challenge-root').first(), { dy: 0.2 }); await r.wait(1500); }, { hold: 1.5 });
await rec.finish({ module: 'm08-fiduccia-mattheyses', url });
