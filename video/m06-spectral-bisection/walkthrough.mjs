// Module 06 experiment walkthrough: records the real lab and code lab, one pass per language.
//   node video/m06-spectral-bisection/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh build/m06-spectral-bisection/walk-zh
// then: python3 scripts/film/walkthrough.py m06-spectral-bisection
import { Recorder } from '../../scripts/film/recorder.mjs';

const [base, lang = 'zh', out = `build/m06-spectral-bisection/walk-${lang}`] = process.argv.slice(2);
const url = new URL(`${lang === 'en' ? 'en/' : ''}modules/m06-spectral-bisection/index.html`, base).href;
const rec = await Recorder.start({ url, lang, out });
const p = rec.page, t = (zh, en) => rec.t(zh, en);
const lab = p.locator('#lab-root');
const btn = (root, zh, en) => root.getByRole('button', { name: t(zh, en), exact: false }).first();
const sel = (root, zh, en) => root.locator('label', { hasText: t(zh, en) }).locator('select').first();
const CH = {
  lab: { zh: '实验台', en: 'THE LAB' }, check: { zh: '对照与警告', en: 'CHECKS AND WARNINGS' }, code: { zh: '在线编程', en: 'CODE LAB' }, viz: { zh: '用你的代码跑', en: 'YOUR CODE, VISUALISED' }, end: { zh: '挑战', en: 'CHALLENGES' }
};
const step = r => r.click(btn(lab, '下一步', 'Next step'));
const toEnd = r => r.click(btn(lab, '跳到结束', 'To the end'));

await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#lab-root', { offset: 110, duration: 900 });  // the number line sits below the graph: keep the whole lab in view
await rec.shot({ chapter: CH.lab, zh: '这是本章的实验台：选例子、平衡窗口和特征向量的来源，还可以改任意一条边的权重。', en: 'This is the chapter\'s lab: choose an example, a balance window and where the eigenvector comes from, and change any edge\'s weight.' },
  async r => { await r.moveTo(sel(lab, '例子', 'Example')); await r.moveTo(sel(lab, '平衡窗口', 'Balance window')); await r.moveTo(sel(lab, '特征向量来源', 'Eigenvector source')); await r.wait(600); }, { hold: 1 });
await rec.shot({ zh: '播放从构造 L 开始：每条边给两个对角 +w、两个非对角 −w，每行和为 0。', en: 'Playback starts by building L: each edge adds +w to two diagonal entries and −w to two off-diagonal ones; every row sums to 0.', zoom: '#lab-root .lab' },
  async r => { await r.moveTo(lab.locator('.lab-side .status').first()); await r.wait(1600); });
await rec.shot({ zh: '第二步求特征值：λ₂ ≈ 1.7733，Fiedler 排序 E, D, C, B, A，数轴上排成一行。', en: 'Step two finds the eigenvalues: λ₂ ≈ 1.7733, and the Fiedler order E, D, C, B, A lines up on the number line.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(1800); });
await rec.shot({ zh: '开始扫描：k = 1 只切下 E，cut 6，但一边只有 1 个，不在 40/60 窗口内。', en: 'The sweep begins: k = 1 cuts off only E, cut 6, but one side has a single node, outside the 40/60 window.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(1800); });
await rec.shot({ zh: 'k = 2：ED | CBA，cut 3，在窗口内。金线就是这一刀。', en: 'k = 2: ED | CBA, cut 3, inside the window. The gold line is this cut.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(1800); });
await rec.shot({ zh: '跳到结束：k = 3 是 5，k = 4 不合法；选窗口内最小的 k = 2，DE | ABC，cut 3。', en: 'Jump to the end: k = 3 gives 5 and k = 4 is not legal; the least inside the window is k = 2, DE | ABC, cut 3.', zoom: '#lab-root .lab' },
  async r => { await toEnd(r); await r.wait(2200); });

await rec.shot({ chapter: CH.check, zh: '把来源换成原作存储的三位小数：排序相同，但残差是 0.0044，而实时求解约 10⁻¹⁵。', en: 'Switch the source to the original\'s stored three decimals: the order is the same, but the residual is 0.0044, against about 10⁻¹⁵ when solved live.', zoom: '#lab-root .lab-side' },
  async r => { await r.choose(sel(lab, '特征向量来源', 'Eigenvector source'), 'stored'); await r.wait(600); await toEnd(r); await r.moveTo(lab.locator('.lab-side .decision').last()); await r.wait(2200); });
await rec.shot({ zh: '换成两个分量的断开图：λ₂ = 0，诊断区发出警告，排序只反映分量。', en: 'Switch to the disconnected graph with two components: λ₂ = 0, the diagnostics raise a warning, and the order only reflects the components.', zoom: '#lab-root .lab-side' },
  async r => { await r.choose(sel(lab, '例子', 'Example'), 'disc'); await r.wait(600); await toEnd(r); await r.moveTo(lab.locator('.lab-side .decision').last()); await r.wait(2400); });
await rec.shot({ chapter: CH.lab, zh: '回到 G01，把 C–D 改成 6：C 被拉向 D、E，最好的一刀移到 k = 3，EDC | BA，cut 5。', en: 'Back to G01, with C–D set to 6: C is pulled towards D and E, and the best cut moves to k = 3, EDC | BA, cut 5.', zoom: '#lab-root .lab' },
  async r => {
    await r.scrollTo('#lab-root', { offset: 110 });
    await r.choose(sel(lab, '例子', 'Example'), 'g01'); await r.wait(400);
    await r.choose(sel(lab, '改一条边', 'Change an edge'), 'C|D');
    await r.click(lab.locator('input[type=number]'), { after: 150 }); await p.keyboard.press('Control+A'); await p.keyboard.type('6', { delay: 120 }); await p.keyboard.press('Tab');
    await r.wait(500); await toEnd(r); await r.wait(2400);
  });

// ---- code lab
const cl = p.locator('#codelab-root');
const idle = () => p.waitForTimeout(300).then(() => p.waitForFunction(() => !document.querySelector('#codelab-root .cl-bar button').disabled, null, { timeout: 90000 }));
await rec.scrollTo('#codelab-root', { duration: 10 });
await cl.locator('.cm-editor').waitFor({ timeout: 30000 });
await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#codelab-root .cl-bar', { offset: 130, duration: 1200 });
await rec.shot({ chapter: CH.code, zh: '在线编程：代码在浏览器里运行，不用安装 Python。Jacobi 求解器和扫描框架已经写好。', en: 'The code lab: your code runs in the browser, with no Python to install. The Jacobi solver and the bisection driver are already written.' },
  async r => { await r.moveTo(cl.locator('.cl-editor')); await r.wait(900); }, { hold: 1 });
await rec.shot({ zh: '先运行检查：三个任务都还没写，结果是 INCOMPLETE。', en: 'Run the checks first: none of the three tasks is written yet, so the result is INCOMPLETE.', zoom: '#codelab-root .cl-side' },
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
await rec.shot({ zh: '任务一：构造 L。每条边做四处贡献：两个对角加 w，两个非对角减 w。', en: 'Task 1: build L. Each edge makes four contributions: +w on two diagonals, −w on two off-diagonals.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("laplacian")',
      'idx = {n: i for i, n in enumerate(nodes)}\nL = [[0.0] * len(nodes) for _ in nodes]\nfor u, v, w in edges:\ni, j = idx[u], idx[v]\nL[i][i] += w; L[j][j] += w\nL[i][j] -= w; L[j][i] -= w\n<return L');
    await r.wait(900);
  });
await rec.shot({ zh: '任务二：扫描。前 k 个为一组，每个切点算 cut，并检查两边大小是否都在窗口内。', en: 'Task 2: the sweep. The first k form one side; compute every cut point\'s cut and check both sizes are inside the window.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("sweep")',
      'n = len(order)\nreturn [{"k": k, "left": order[:k], "right": order[k:], "cut": cut(edges, set(order[:k])),\n"legal": lo <= k <= hi and lo <= n - k <= hi} for k in range(1, n)]');
    await r.wait(900);
  });
await rec.shot({ zh: '任务三：2ⁿ 种标记去掉全左、全右，再除以 2。', en: 'Task 3: of the 2ⁿ labellings, drop all-left and all-right, then divide by 2.', zoom: '#codelab-root .cl-editor' },
  async r => { await replaceLine(r, 'NotImplementedError("count_bipartitions")', 'return (2 ** n - 2) // 2'); await r.wait(900); });
await rec.shot({ zh: '运行检查：全部通过，包括残差、翻号等价和断开图的 λ₂ = 0。', en: 'Run the checks: everything passes, including the residual, sign-flip equivalence and λ₂ = 0 on a disconnected graph.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2400); });

const viz = p.locator('#codelab-root .cl-viz');
await rec.scrollTo('#codelab-root .cl-viz', { offset: 140, duration: 900 });
await rec.shot({ chapter: CH.viz, zh: '下面用你写的函数跑一张新图：两个四节点块，由两根弱线相连。', en: 'Below, your functions run on a new graph: two four-node blocks joined by two weak wires.' },
  async r => { await r.choose(sel(viz, '例子', 'Example'), 'twin'); await r.wait(500); }, { hold: 0.6 });
await rec.shot({ zh: '你的扫描切在两块之间：WUVT | SRQP，cut 2，每个切点都与引擎一致。', en: 'Your sweep cuts between the blocks: WUVT | SRQP, cut 2, and every cut point matches the engine.' },
  async r => {
    await r.click(btn(viz, '用我的代码运行', 'Run my code'), { after: 100 });
    await r.offscreen(() => p.waitForFunction(() => /ok|no/.test(document.querySelector('#codelab-root .cl-viz .match')?.className || ''), null, { timeout: 60000 }));
    await r.wait(2400);
  });

await rec.scrollTo('#challenges', { duration: 900 });
await rec.shot({ chapter: CH.end, zh: '最后做挑战题，确认自己真的懂了。结果只保存在你的浏览器里。', en: 'Finally, try the challenges to check you really understand. Results stay in your browser.' },
  async r => { await r.moveTo(p.locator('#challenge-root').first(), { dy: 0.2 }); await r.wait(1500); }, { hold: 1.5 });
await rec.finish({ module: 'm06-spectral-bisection', url });
