// Module 09 experiment walkthrough: records the real lab and code lab, one pass per language.
//   node video/m09-rajaraman-wong/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh build/m09-rajaraman-wong/walk-zh
// then: python3 scripts/film/walkthrough.py m09-rajaraman-wong
import { Recorder } from '../../scripts/film/recorder.mjs';

const [base, lang = 'zh', out = `build/m09-rajaraman-wong/walk-${lang}`] = process.argv.slice(2);
const url = new URL(`${lang === 'en' ? 'en/' : ''}modules/m09-rajaraman-wong/index.html`, base).href;
const rec = await Recorder.start({ url, lang, out });
const p = rec.page, t = (zh, en) => rec.t(zh, en);
const lab = p.locator('#lab-root');
const btn = (root, zh, en) => root.getByRole('button', { name: t(zh, en), exact: false }).first();
const sel = (root, zh, en) => root.locator('label', { hasText: t(zh, en) }).locator('select').last();
const CH = {
  chain: { zh: '一条链', en: 'ONE CHAIN' }, lab: { zh: '标记与恢复', en: 'LABEL AND RECOVER' }, code: { zh: '在线编程', en: 'CODE LAB' }, viz: { zh: '用你的代码跑', en: 'YOUR CODE, VISUALISED' }, end: { zh: '挑战', en: 'CHALLENGES' }
};
const step = r => r.click(btn(lab, '下一步', 'Next step'));
const toEnd = r => r.click(btn(lab, '跳到结束', 'To the end'));
const toggle = i => lab.locator('.lab-side .lab-toolbar button').nth(i);

// ---- A · the chain
await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#lab-root', { offset: 110, duration: 900 });
await rec.shot({ chapter: CH.chain, zh: '先看一条链：每个节点延迟 1，跨簇加 D = 3。现在只有 X→Y 跨簇：延迟 7。', en: 'First, a chain: each node delay 1, crossing clusters adds D = 3. Only X→Y crosses now: delay 7.', zoom: '#lab-root .lab-side' },
  async r => { await r.moveTo(toggle(1)); await r.wait(1400); }, { hold: 1 });
await rec.shot({ zh: '改成 P→X、Y→O 跨簇：跨界两次，延迟 10。切断的线多一条，路径就慢 3。', en: 'Make P→X and Y→O cross instead: two crossings, delay 10. One more boundary on the path costs 3.', zoom: '#lab-root .lab-side' },
  async r => { await r.click(toggle(0)); await r.wait(500); await r.click(toggle(1)); await r.wait(500); await r.click(toggle(2)); await r.wait(1800); });

// ---- B · labelling and recovery on the candidate DAG
await rec.scrollTo('#lab-root .lab', { offset: 170, duration: 1000 });
await rec.shot({ chapter: CH.lab, zh: '下面是候选 DAG（由原作影片复原，平票规则为假设）：PI 蓝色，容量 4，D = 3。', en: 'Below is the candidate DAG (reconstructed from the original film, tie rule assumed): PIs blue, capacity 4, D = 3.', zoom: '#lab-root .lab' },
  async r => { await r.moveTo(lab.locator('.lab-stage').first(), { dy: 0.4 }); await r.wait(1600); }, { hold: 1 });
await rec.shot({ zh: '单步到 i：候选簇 {i, g, e, c}；簇内 PI c 给 l1 = 4，簇外的 b 给 l2 = 7，所以 l(i) = 7。', en: 'Step to i: candidate cluster {i, g, e, c}; the PI c inside gives l1 = 4, b outside gives l2 = 7, so l(i) = 7.', zoom: '#lab-root .lab' },
  async r => { for (let i = 0; i < 6; i++) { await step(r); await r.wait(380); } await r.wait(2600); });
await rec.shot({ zh: '跳到结束：从输出倒推出 8 个簇、20 个实例，两个输出都在 8 到达；金色虚线圈是被复制的节点。', en: 'Jump to the end: working back from the outputs gives 8 clusters and 20 instances, both outputs arrive at 8; gold dashed rings are replicated nodes.', zoom: '#lab-root .lab' },
  async r => { await toEnd(r); await r.wait(3000); });
await rec.shot({ zh: '把容量改成 3：簇装不下了，关键路径多跨一次边界，输出 k 变成 11。', en: 'Set the capacity to 3: the clusters no longer fit, the critical path crosses once more, and output k becomes 11.', zoom: '#lab-root .lab' },
  async r => { await r.choose(sel(lab, '簇容量 M', 'Cluster capacity M'), '3'); await r.wait(600); await toEnd(r); await r.wait(2800); });

// ---- code lab
const cl = p.locator('#codelab-root');
const idle = () => p.waitForTimeout(300).then(() => p.waitForFunction(() => !document.querySelector('#codelab-root .cl-bar button').disabled, null, { timeout: 90000 }));
await rec.scrollTo('#codelab-root', { duration: 10 });
await cl.locator('.cm-editor').waitFor({ timeout: 30000 });
await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#codelab-root .cl-bar', { offset: 130, duration: 1200 });
await rec.shot({ chapter: CH.code, zh: '在线编程：代码在浏览器里运行，不用安装 Python。五个函数分两层：先评估延迟，再做标记与恢复。', en: 'The code lab: your code runs in the browser, with no Python to install. Five functions in two layers: evaluate delay first, then label and recover.' },
  async r => { await r.moveTo(cl.locator('.cl-editor')); await r.wait(900); }, { hold: 1 });
await rec.shot({ zh: '先运行检查：五个任务都没写，结果是 INCOMPLETE。', en: 'Run the checks first: none of the five tasks is written, so the result is INCOMPLETE.', zoom: '#codelab-root .cl-side' },
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
await rec.shot({ zh: '任务三：实例的到达时间 = 自身延迟 + 各输入的最大（到达时间 + 代价）。', en: 'Task 3: an instance\'s arrival = its own delay + the largest (input arrival + cost).', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("evaluate_instance_delay")',
      'inc = {i: [] for i in instances}\nfor a, b, c in instance_edges:\ninc[b].append((a, c))\n<memo = {}\ndef t(i):\nif i not in memo:\nmemo[i] = delay[instances[i]] + max([t(a) + c for a, c in inc[i]], default=0)\n<return memo[i]\n<return {i: t(i) for i in instances}');
    await r.wait(900);
  });
await rec.shot({ zh: '再运行检查：链的 7 与 10 通过了，其余还是 INCOMPLETE。', en: 'Run the checks again: the chain\'s 7 and 10 pass; the rest are still INCOMPLETE.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2000); });
await rec.shot({ zh: '其余四个函数这里快进：直接填入与参考实现相同的代码。', en: 'The other four functions are fast-forwarded here: filled in with the same code as the reference.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await p.evaluate(async lang => {
      const d = await (await fetch(new URL('../../data/m09-rajaraman-wong/codelab.json', location.href.replace('/en/modules/', '/modules/')))).json();
      const ref = d.reference[lang] ?? d.reference.zh, view = document.querySelector('#codelab-root .cl-editor').editorView;
      const text = typeof ref === 'string' ? ref : Object.values(ref)[0];
      view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: text }, selection: { anchor: 0 }, scrollIntoView: true });
    }, lang);
    await r.wait(2200);
  });
await rec.shot({ zh: '运行检查：全部通过，包括候选图的 8 簇、20 实例、输出 8 和每个实例的输入完整。', en: 'Run the checks: everything passes, including 8 clusters, 20 instances and output 8 on the candidate graph, with every instance\'s inputs complete.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2400); });

const viz = p.locator('#codelab-root .cl-viz');
await rec.scrollTo('#codelab-root .cl-viz', { offset: 140, duration: 900 });
await rec.shot({ chapter: CH.viz, zh: '下面用你写的函数跑 6 个情形，与课程引擎对照：标签、簇数、实例数和输出延迟。', en: 'Below, your functions run on six cases, compared with the course engine: labels, clusters, instances and output delays.' },
  async r => {
    await r.click(btn(viz, '用我的代码运行', 'Run my code'), { after: 100 });
    await r.offscreen(() => p.waitForFunction(() => /ok|no/.test(document.querySelector('#codelab-root .cl-viz .match')?.className || ''), null, { timeout: 90000 }));
    await r.wait(1600);
  });
await rec.shot({ zh: '点菱形新图那一行：看你的代码恢复出的簇与实例，金色是被复制的节点。', en: 'Click the new diamond graph\'s row: see the clusters and instances your code recovered; gold nodes were replicated.' },
  async r => { await r.click(viz.locator('table.codelab-cases tbody tr').nth(4)); await r.wait(2600); });

await rec.scrollTo('#challenges', { duration: 900 });
await rec.shot({ chapter: CH.end, zh: '最后做挑战题，确认自己真的懂了。结果只保存在你的浏览器里。', en: 'Finally, try the challenges to check you really understand. Results stay in your browser.' },
  async r => { await r.moveTo(p.locator('#challenge-root').first(), { dy: 0.2 }); await r.wait(1500); }, { hold: 1.5 });
await rec.finish({ module: 'm09-rajaraman-wong', url });
