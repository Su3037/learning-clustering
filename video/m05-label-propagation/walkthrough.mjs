// Module 05 experiment walkthrough: records the real lab and code lab, one pass per language.
//   node video/m05-label-propagation/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh build/m05-label-propagation/walk-zh
// then: python3 scripts/film/walkthrough.py m05-label-propagation
import { Recorder } from '../../scripts/film/recorder.mjs';

const [base, lang = 'zh', out = `build/m05-label-propagation/walk-${lang}`] = process.argv.slice(2);
const url = new URL(`${lang === 'en' ? 'en/' : ''}modules/m05-label-propagation/index.html`, base).href;
const rec = await Recorder.start({ url, lang, out });
const p = rec.page, t = (zh, en) => rec.t(zh, en);
const lab = p.locator('#lab-root');
const btn = (root, zh, en) => root.getByRole('button', { name: t(zh, en), exact: false }).first();
const sel = (root, zh, en) => root.locator('label', { hasText: t(zh, en) }).locator('select').first();
const CH = {
  lab: { zh: '实验台', en: 'THE LAB' }, code: { zh: '在线编程', en: 'CODE LAB' }, viz: { zh: '用你的代码跑', en: 'YOUR CODE, VISUALISED' }, end: { zh: '挑战', en: 'CHALLENGES' }
};

await rec.scrollTo('#lab', { duration: 10 });
await rec.shot({ chapter: CH.lab, zh: '这是本章的实验台：先选例子、更新方式、平票规则和访问顺序。', en: 'This is the chapter\'s lab: choose an example, the update mode, the tie rule and the visiting order.' },
  async r => { await r.moveTo(sel(lab, '例子', 'Example')); await r.moveTo(sel(lab, '平票规则', 'Tie rule')); await r.wait(600); }, { hold: 1 });
await rec.shot({ zh: '按“下一步”，更新一个节点。右边是这一票的明细。', en: 'Press Step to update one node. The panel on the right shows that vote in detail.', zoom: '#lab-root .lab' },
  async r => { await r.click(btn(lab, '下一步', 'Step')); await r.wait(900); });
await rec.shot({ zh: '再按两次轮到 C：B = 1 + 4 = 5，D = 2，E = 1。金色那一行是赢家。', en: 'Two more steps and it is C\'s turn: B = 1 + 4 = 5, D = 2, E = 1. The gold row wins.', zoom: '#lab-root .lab' },
  async r => { await r.click(btn(lab, '下一步', 'Step'), { glide: 0.3 }); await r.wait(500); await r.click(btn(lab, '下一步', 'Step'), { glide: 0.2 }); await r.wait(1200); });
await rec.shot({ zh: '“跳到结束”：2 轮，状态 stable，cut 3。', en: 'To the end: 2 rounds, status stable, cut 3.', zoom: '#lab-root .lab-side' },
  async r => { await r.click(btn(lab, '跳到结束', 'To the end')); await r.wait(1200); });
await rec.shot({ zh: '下面的记录表列出每一步；点任一行就回到那一步。', en: 'The log below lists every step; click any row to jump back to it.' },
  async r => { await r.scrollTo('#lab-root details.trace', { offset: 380 }); await r.click(lab.locator('details.trace > summary')); await r.wait(500); await r.click(lab.locator('details.trace tbody tr').nth(3)); await r.wait(1000); });
await rec.scrollTo('#lab', { duration: 600 });
await rec.shot({ zh: '换成同步更新，再跳到结束：同一张图开始振荡，状态是 cycle。', en: 'Switch to synchronous updates and jump to the end: the same graph oscillates, and the status is cycle.' },
  async r => { await r.choose(sel(lab, '更新方式', 'Update mode'), 'sync'); await r.click(btn(lab, '跳到结束', 'To the end')); await r.wait(1500); });
await rec.shot({ zh: '换回异步，按“反向顺序”：3 轮，标签名不同，分组不变。', en: 'Back to asynchronous, then Reverse order: 3 rounds, other label names, the same groups.' },
  async r => { await r.choose(sel(lab, '更新方式', 'Update mode'), 'async'); await r.click(btn(lab, '反向顺序', 'Reverse order')); await r.click(btn(lab, '跳到结束', 'To the end')); await r.wait(1300); });
await rec.shot({ zh: '把 C–D 这座桥调到 10：分组变成 AB | CDE，cut 5。', en: 'Raise the C–D bridge to 10: the groups become AB | CDE, cut 5.' },
  async r => {
    const order = lab.locator('input[type=text]').first();
    await order.fill('A B C D E'); await order.dispatchEvent('change');
    const range = lab.locator('input[type=range]').first();
    await r.moveTo(range, { dx: 0.1 });
    await range.evaluate(el => { el.value = '10'; el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); });
    await r.moveTo(range, { dx: 0.82, glide: 0.4 });
    await r.wait(500);
    await r.scrollTo('#lab', { duration: 700 });
    await r.click(btn(lab, '跳到结束', 'To the end')); await r.wait(1600);
  });

// ---- code lab
const cl = p.locator('#codelab-root');
const idle = () => p.waitForTimeout(300).then(() => p.waitForFunction(() => !document.querySelector('#codelab-root .cl-bar button').disabled, null, { timeout: 90000 }));
// The editor loads when it scrolls into view: load it first, then frame the run bar.
await rec.scrollTo('#codelab-root', { duration: 10 });
await cl.locator('.cm-editor').waitFor({ timeout: 30000 });
await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#codelab-root .cl-bar', { offset: 130, duration: 1200 });
await rec.shot({ chapter: CH.code, zh: '在线编程：代码在浏览器里运行，不用安装 Python。', en: 'The code lab: your code runs in the browser, with no Python to install.' },
  async r => { await r.moveTo(cl.locator('.cl-editor')); await r.wait(900); }, { hold: 1 });
await rec.shot({ zh: '先运行检查：两个任务都还没写，结果是 INCOMPLETE。', en: 'Run the checks first: neither task is written yet, so the result is INCOMPLETE.', zoom: '#codelab-root .cl-side' },
  async r => {
    await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 });
    await r.offscreen(idle);
    await r.wait(1600);
  });

async function replaceLine(r, needle, code) {
  // CodeMirror only renders visible lines: select the target line through the editor, then move the drawn cursor there.
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
  await r.type(code);
}
await rec.shot({ zh: '任务一 count_votes：按标签把邻居的边权加起来。', en: 'Task 1, count_votes: add up the neighbours\' edge weights per label.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("count_votes")',
      'votes = {}\nfor neighbor, weight in adj[vertex]:\nvotes[labels[neighbor]] = votes.get(labels[neighbor], 0) + weight\n<return votes');
    await r.wait(1000);
  });
await rec.shot({ zh: '再运行检查：计票通过了，停止判定还没写。', en: 'Run the checks again: the vote counting passes; the stopping test is still missing.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2200); });
await rec.shot({ zh: '任务二：整轮零变化就是 stable；状态以前出现过就是 cycle。', en: 'Task 2: a round with no change is stable; a state seen before is a cycle.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, t('NotImplementedError("停止判定")', 'NotImplementedError("stopping test")'),
      'signature = tuple(labels[n] for n in nodes)\nif changes == 0:\nstatus = "stable"\nbreak\n<if signature in seen:\nstatus = "cycle"\nbreak\n<seen[signature] = rounds');
    await r.wait(1000);
  });
await rec.shot({ zh: '运行检查：全部通过，包括作者原作的 24 单元电路和 28 人通讯录。', en: 'Run the checks: everything passes, including the original 24-cell circuit and 28-person contact list.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2400); });

const viz = p.locator('#codelab-root .cl-viz');
await rec.scrollTo('#codelab-root .cl-viz', { offset: 140, duration: 900 });
await rec.shot({ chapter: CH.viz, zh: '下面用你自己的 solve() 运行，并和课程引擎逐步对照。选两节点、同步。', en: 'Below, your own solve() runs and is compared with the course engine step by step. Pick two nodes, synchronous.' },
  async r => { await r.choose(sel(viz, '例子', 'Example'), 'pair'); await r.choose(sel(viz, '更新方式', 'Update mode'), 'sync'); await r.wait(400); });
await rec.shot({ zh: '你的代码也报告了 cycle，而且每一步都和课程引擎一致。', en: 'Your code reports a cycle too, and agrees with the course engine at every step.' },
  async r => {
    await r.click(btn(viz, '用我的 solve() 运行', 'Run my solve()'), { after: 100 });
    await r.offscreen(() => p.waitForFunction(() => /ok|no/.test(document.querySelector('#codelab-root .cl-viz .match')?.className || ''), null, { timeout: 60000 }));
    await r.click(btn(viz, '自动播放', 'Play')); await r.wait(4200);
  });

await rec.scrollTo('#challenges', { duration: 900 });
await rec.shot({ chapter: CH.end, zh: '最后做挑战题，确认自己真的懂了。结果只保存在你的浏览器里。', en: 'Finally, try the challenges to check you really understand. Results stay in your browser.' },
  async r => { await r.moveTo(p.locator('#challenge-root').first(), { dy: 0.2 }); await r.wait(1500); }, { hold: 1.5 });
await rec.finish({ module: 'm05-label-propagation', url });
