// Module 02 experiment walkthrough: records the real lab and code lab, one pass per language.
//   node video/m02-affinity-metrics/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh build/m02-affinity-metrics/walk-zh
// then: python3 scripts/film/walkthrough.py m02-affinity-metrics
import { Recorder } from '../../scripts/film/recorder.mjs';

const [base, lang = 'zh', out = `build/m02-affinity-metrics/walk-${lang}`] = process.argv.slice(2);
const url = new URL(`${lang === 'en' ? 'en/' : ''}modules/m02-affinity-metrics/index.html`, base).href;
const rec = await Recorder.start({ url, lang, out });
const p = rec.page, t = (zh, en) => rec.t(zh, en);
const lab = p.locator('#lab-root');
const btn = (root, zh, en) => root.getByRole('button', { name: t(zh, en), exact: false }).first();
const sel = (root, zh, en) => root.locator('label', { hasText: t(zh, en) }).locator('select').first();
const CH = {
  lab: { zh: '实验台', en: 'THE LAB' }, code: { zh: '在线编程', en: 'CODE LAB' }, viz: { zh: '用你的代码跑', en: 'YOUR CODE, VISUALISED' }, end: { zh: '挑战', en: 'CHALLENGES' }
};
// Jump the lab's player to the row for one pair by clicking it in the trace table.
async function pickPair(r, pair) {
  const det = lab.locator('details.trace');
  if (!(await det.evaluate(el => el.open))) await r.click(det.locator('summary'));
  await r.click(det.locator('tbody tr', { hasText: pair }).first());
}

await rec.scrollTo('#lab', { duration: 10 });
await rec.shot({ chapter: CH.lab, zh: '这是本章的实验台：先选例子，这里用课程公共图 G01，再选评分方式。', en: 'This is the chapter\'s lab: choose an example, here the course graph G01, then a way to score.' },
  async r => { await r.choose(sel(lab, '例子', 'Example'), 'g01'); await r.choose(sel(lab, '评分方式', 'Score'), 'edge'); await r.wait(600); }, { hold: 1 });
await rec.shot({ zh: '直接边权：G01 只有 6 对。A–B 和 D–E 都是 5，按名字 A–B 在前。', en: 'Direct weight: G01 has only 6 pairs. A–B and D–E are both 5; by name, A–B comes first.', zoom: '#lab-root .lab-side' },
  async r => { await r.click(btn(lab, '下一步', 'Next step')); await r.wait(1200); });
await rec.shot({ zh: '换成共同邻居：10 对全部有分。A–B 变成 6。', en: 'Switch to shared neighbours: all 10 pairs score. A–B becomes 6.', zoom: '#lab-root .lab' },
  async r => { await r.choose(sel(lab, '评分方式', 'Score'), 'shared'); await r.wait(1400); });
await rec.shot({ zh: '在记录表里点 B–D：没有直接边，经 C 得 min(4, 2) = 2。', en: 'Click B–D in the log: no direct edge, and through C it gets min(4, 2) = 2.', zoom: '#lab-root .lab' },
  async r => { await r.scrollTo('#lab-root details.trace', { offset: 420 }); await pickPair(r, 'B–D'); await r.wait(400); await r.scrollTo('#lab', { duration: 700 }); await r.wait(1400); });
await rec.shot({ zh: '换成 priority 图：按直接边权第一对是 X–Y。', en: 'Switch to the priority graph: by direct weight, the first pair is X–Y.', zoom: '#lab-root .lab' },
  async r => { await r.choose(sel(lab, '例子', 'Example'), 'priority'); await r.choose(sel(lab, '评分方式', 'Score'), 'edge'); await r.wait(1400); });
await rec.shot({ zh: '按共同邻居，三角形里的三对都是 8，第一对变成 P–Q。', en: 'By shared neighbours, the three triangle pairs score 8, and the first pair becomes P–Q.', zoom: '#lab-root .lab' },
  async r => { await r.choose(sel(lab, '评分方式', 'Score'), 'shared'); await r.wait(1500); });
await rec.shot({ zh: '把 X–Y 改成 9：它刚好重新排到第一。', en: 'Change X–Y to 9: it just takes first place again.', zoom: '#lab-root .lab' },
  async r => {
    await r.choose(lab.locator('label', { hasText: t('改一条边', 'Change an edge') }).locator('select'), 'X|Y');
    const w = lab.locator('label', { hasText: t('新权重', 'New weight') }).locator('input');
    await r.click(w); await w.fill(''); await r.type('9'); await w.dispatchEvent('change');
    await r.wait(1500);
  });
await rec.shot({ zh: '换成 tiny netlist，用 pin-count：私有的 E–F 得 1，排第一；A–B 只有 0.5。', en: 'Switch to the tiny netlist with pin-count: the private E–F gets 1 and comes first; A–B has only 0.5.', zoom: '#lab-root .lab' },
  async r => { await r.choose(sel(lab, '例子', 'Example'), 'netlist'); await r.wait(1600); });
await rec.shot({ zh: '对照“按 net 计数”：不摊薄的话，A–B 以 2 分排在 E–F 前面。', en: 'Compare with net count: without sharing out, A–B scores 2 and beats E–F.', zoom: '#lab-root .lab' },
  async r => { await r.choose(sel(lab, '评分方式', 'Score'), 'raw'); await r.wait(1600); });

// ---- code lab
const cl = p.locator('#codelab-root');
const idle = () => p.waitForTimeout(300).then(() => p.waitForFunction(() => !document.querySelector('#codelab-root .cl-bar button').disabled, null, { timeout: 90000 }));
await rec.scrollTo('#codelab-root', { duration: 10 });
await cl.locator('.cm-editor').waitFor({ timeout: 30000 });
await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#codelab-root .cl-bar', { offset: 130, duration: 1200 });
await rec.shot({ chapter: CH.code, zh: '在线编程：代码在浏览器里运行，不用安装 Python。', en: 'The code lab: your code runs in the browser, with no Python to install.' },
  async r => { await r.moveTo(cl.locator('.cl-editor')); await r.wait(900); }, { hold: 1 });
await rec.shot({ zh: '先运行检查：三个函数都还没写，结果是 INCOMPLETE。', en: 'Run the checks first: none of the three functions is written, so the result is INCOMPLETE.', zoom: '#codelab-root .cl-side' },
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
  await r.type(code, { delay: 28 });
}
await rec.shot({ zh: '任务一：直接边权就是把规范化后的边排个名，一行就够。', en: 'Task 1: direct weight just ranks the normalised edges. One line is enough.', zoom: '#codelab-root .cl-editor' },
  async r => { await replaceLine(r, 'NotImplementedError("affinity_edge_weight")', 'return _rank([(u, v, w) for (u, v), w in _norm_edges(edges).items()])'); await r.wait(900); });
await rec.shot({ zh: '任务二：先建邻接表，再检查每一个无序节点对，包括没有直接边的。', en: 'Task 2: build the adjacency first, then check every unordered pair, including pairs with no direct edge.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("affinity_shared_neighbors")',
      'w = _norm_edges(edges)\nadj = {n: {} for n in nodes}\nfor (u, v), x in w.items():\nadj[u][v] = x\nadj[v][u] = x\n<result = []\nfor u in nodes:\nfor v in nodes:\nif u < v:\nscore = adj[u].get(v, 0)\nfor x, wu in adj[u].items():\nif x != v and x in adj[v]:\nscore += min(wu, adj[v][x])\n<<if score > 0:\nresult.append((u, v, score))\n<<<<return _rank(result)');
    await r.wait(900);
  });
await rec.shot({ zh: '任务三：每条 net 去掉重复引脚，把 w/(|e|−1) 加给其中每一对。', en: 'Task 3: drop repeated pins in each net, and add w/(|e|−1) to every pair in it.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, 'NotImplementedError("affinity_pin_count")',
      'acc = {}\nfor net in nets:\npins = sorted(set(net["pins"]))\nif len(pins) < 2:\ncontinue\n<share = net.get("w", 1) / (len(pins) - 1)\nfor i, u in enumerate(pins):\nfor v in pins[i + 1:]:\nacc[(u, v)] = acc.get((u, v), 0) + share\n<<<return _rank([(u, v, round(s, 9)) for (u, v), s in acc.items()])');
    await r.wait(900);
  });
await rec.shot({ zh: '运行检查：全部通过，包括作者原作的 priority 图和 tiny netlist。', en: 'Run the checks: everything passes, including the original author\'s priority graph and tiny netlist.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2400); });

const viz = p.locator('#codelab-root .cl-viz');
await rec.scrollTo('#codelab-root .cl-viz', { offset: 140, duration: 900 });
await rec.shot({ chapter: CH.viz, zh: '下面用你自己的函数跑一张练习里没出现过的新图，逐行对照课程引擎。', en: 'Below, your own function runs on a new graph the exercise never used, compared row by row with the course engine.' },
  async r => { await r.choose(sel(viz, '例子', 'Example'), 'fresh'); await r.choose(sel(viz, '函数', 'Function'), 'shared'); await r.wait(400); });
await rec.shot({ zh: '每一行都和引擎一致。', en: 'Every row matches the engine.' },
  async r => {
    await r.click(btn(viz, '用我的代码运行', 'Run my code'), { after: 100 });
    await r.offscreen(() => p.waitForFunction(() => /ok|no/.test(document.querySelector('#codelab-root .cl-viz .match')?.className || ''), null, { timeout: 60000 }));
    await r.click(btn(viz, '自动播放', 'Play')); await r.wait(4200);
  });

await rec.scrollTo('#challenges', { duration: 900 });
await rec.shot({ chapter: CH.end, zh: '最后做挑战题，确认自己真的懂了。结果只保存在你的浏览器里。', en: 'Finally, try the challenges to check you really understand. Results stay in your browser.' },
  async r => { await r.moveTo(p.locator('#challenge-root').first(), { dy: 0.2 }); await r.wait(1500); }, { hold: 1.5 });
await rec.finish({ module: 'm02-affinity-metrics', url });
