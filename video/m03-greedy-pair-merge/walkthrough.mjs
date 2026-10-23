// Module 03 experiment walkthrough: records the real lab and code lab, one pass per language.
//   node video/m03-greedy-pair-merge/walkthrough.mjs http://127.0.0.1:8800/learning-clustering/ zh build/m03-greedy-pair-merge/walk-zh
// then: python3 scripts/film/walkthrough.py m03-greedy-pair-merge
import { Recorder } from '../../scripts/film/recorder.mjs';

const [base, lang = 'zh', out = `build/m03-greedy-pair-merge/walk-${lang}`] = process.argv.slice(2);
const url = new URL(`${lang === 'en' ? 'en/' : ''}modules/m03-greedy-pair-merge/index.html`, base).href;
const rec = await Recorder.start({ url, lang, out });
const p = rec.page, t = (zh, en) => rec.t(zh, en);
const lab = p.locator('#lab-root');
const btn = (root, zh, en) => root.getByRole('button', { name: t(zh, en), exact: false }).first();
const sel = (root, zh, en) => root.locator('label', { hasText: t(zh, en) }).locator('select').first();
const CH = {
  lab: { zh: '实验台', en: 'THE LAB' }, code: { zh: '在线编程', en: 'CODE LAB' }, viz: { zh: '用你的代码跑', en: 'YOUR CODE, VISUALISED' }, end: { zh: '挑战', en: 'CHALLENGES' }
};
const step = r => r.click(btn(lab, '下一步', 'Next step'));

await rec.scrollTo('#lab', { duration: 10 });
await rec.shot({ chapter: CH.lab, zh: '这是本章的实验台：选目标簇数 K 和容量，图和候选表会重新计算。', en: 'This is the chapter\'s lab: choose the target K and a capacity, and the graph and candidate table recompute.' },
  async r => { await r.moveTo(sel(lab, '目标簇数 K', 'Target K')); await r.moveTo(sel(lab, '容量 C', 'Capacity C')); await r.wait(600); }, { hold: 1 });
await rec.shot({ zh: '按“下一步”：A–B 和 D–E 都是 5，平票按名字，金色的 A–B 被选中。cut 18 → 13。', en: 'Press Step: A–B and D–E are both 5, the tie goes by name, and A–B (gold) is chosen. cut 18 → 13.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(1400); });
await rec.shot({ zh: '第二步：AB–C 显示为 5（1+4），两根平行边相加；又平票，[A, B] 在 [D] 前。', en: 'Step two: AB–C shows 5 (1+4), two parallel wires added up; another tie, and [A, B] comes before [D].', zoom: '#lab-root .lab-side' },
  async r => { await step(r); await r.wait(1600); });
await rec.shot({ zh: '第三步合并 D–E：剩两簇 ABC | DE，cut 3。', en: 'Step three merges D–E: two clusters, ABC | DE, cut 3.', zoom: '#lab-root .lab' },
  async r => { await step(r); await r.wait(1500); });
await rec.shot({ zh: '容量改成 2，跳到结束：AB+C 超容量被阻止，停在 3 簇，cut 8，没有达到 K。', en: 'Set the capacity to 2 and jump to the end: AB+C is blocked as over capacity, and it stops at 3 clusters, cut 8, without reaching K.', zoom: '#lab-root .lab' },
  async r => { await r.choose(sel(lab, '容量 C', 'Capacity C'), '2'); await r.click(btn(lab, '跳到结束', 'To the end')); await r.wait(1800); });
await rec.shot({ zh: '下方是原网页字符串比较的对照：同一组参数，它第一步错选了 A–C。', en: 'Below, the original page\'s string comparison for contrast: with the same settings, its first step wrongly picks A–C.' },
  async r => { await r.choose(sel(lab, '容量 C', 'Capacity C'), ''); await r.scrollTo('#lab-root .lab-note', { offset: 420 }); await r.moveTo(lab.locator('.lab-note')); await r.wait(1800); });
await rec.shot({ zh: '记录表列出每一步；点任一行就回到那一步。', en: 'The log lists every step; click any row to jump back to it.' },
  async r => { await r.click(lab.locator('details.trace > summary')); await r.wait(500); await r.click(lab.locator('details.trace tbody tr').nth(1)); await r.wait(1200); });

// ---- code lab
const cl = p.locator('#codelab-root');
const idle = () => p.waitForTimeout(300).then(() => p.waitForFunction(() => !document.querySelector('#codelab-root .cl-bar button').disabled, null, { timeout: 90000 }));
await rec.scrollTo('#codelab-root', { duration: 10 });
await cl.locator('.cm-editor').waitFor({ timeout: 30000 });
await rec.scrollTo('#lab', { duration: 10 });
await rec.scrollTo('#codelab-root .cl-bar', { offset: 130, duration: 1200 });
await rec.shot({ chapter: CH.code, zh: '在线编程：代码在浏览器里运行，不用安装 Python。', en: 'The code lab: your code runs in the browser, with no Python to install.' },
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
await rec.shot({ zh: '任务一：选择键是一个元组，数字按数值比，平票再比成员。', en: 'Task 1: the selection key is a tuple: numbers compare as numbers, and members break ties.', zoom: '#codelab-root .cl-editor' },
  async r => { await replaceLine(r, 'NotImplementedError("selection_key")', 'return (-c["affinity"], c["a"], c["b"])'); await r.wait(900); });
await rec.shot({ zh: '任务二：主循环。达到 K 就停；没有合法候选就停，并分清两种原因；否则合并最好的一对。', en: 'Task 2: the main loop. Stop at K; stop when no candidate is legal, telling the two reasons apart; otherwise merge the best pair.', zoom: '#codelab-root .cl-editor' },
  async r => {
    await replaceLine(r, t('NotImplementedError("greedy_pair_merge 主循环")', 'NotImplementedError("greedy_pair_merge main loop")'),
      'while True:\nif len(parts) <= k:\nstop_reason = "target-reached"\nbreak\n<cands = candidates(parts, weights, capacity, sizes)\nlegal = [c for c in cands if c["legal"]]\nif not legal:\nstop_reason = "capacity-blocked" if cands else "no-positive-affinity"\nbreak\n<best = min(legal, key=selection_key)\nmerged = sorted(best["a"] + best["b"])\nparts = sorted([q for q in parts if tuple(q) not in (best["a"], best["b"])] + [merged])\nlog.append({"step": len(log), "event": "merge", "pair": "".join(best["a"]) + "-" + "".join(best["b"]), "weight": best["affinity"], "clusters": ["".join(q) for q in parts], "cutsize": cutsize(parts, weights)})\n<return {"parts": ["".join(q) for q in parts], "cutsize": cutsize(parts, weights), "log": log, "target_reached": len(parts) <= k, "stop_reason": stop_reason}');
    await r.wait(900);
  });
await rec.shot({ zh: '运行检查：全部通过，包括 10 > 9 > 2 的多位数权重和不连通的图。', en: 'Run the checks: everything passes, including multi-digit weights 10 > 9 > 2 and a disconnected graph.', zoom: '#codelab-root .cl-side' },
  async r => { await r.click(btn(cl, '运行检查', 'Run checks'), { after: 100 }); await r.offscreen(idle); await r.wait(2400); });

const viz = p.locator('#codelab-root .cl-viz');
await rec.scrollTo('#codelab-root .cl-viz', { offset: 140, duration: 900 });
await rec.shot({ chapter: CH.viz, zh: '下面用你自己的 greedy_pair_merge() 跑一张新图，逐步对照课程引擎。', en: 'Below, your own greedy_pair_merge() runs on a new graph, compared step by step with the course engine.' },
  async r => { await r.choose(sel(viz, '例子', 'Example'), 'fresh'); await r.wait(500); });
await rec.shot({ zh: '每一步的簇和 cut 都和引擎一致。', en: 'Every step\'s clusters and cut match the engine.' },
  async r => {
    await r.click(btn(viz, '用我的代码运行', 'Run my code'), { after: 100 });
    await r.offscreen(() => p.waitForFunction(() => /ok|no/.test(document.querySelector('#codelab-root .cl-viz .match')?.className || ''), null, { timeout: 60000 }));
    await r.click(btn(viz, '自动播放', 'Play')); await r.wait(5200);
  });

await rec.scrollTo('#challenges', { duration: 900 });
await rec.shot({ chapter: CH.end, zh: '最后做挑战题，确认自己真的懂了。结果只保存在你的浏览器里。', en: 'Finally, try the challenges to check you really understand. Results stay in your browser.' },
  async r => { await r.moveTo(p.locator('#challenge-root').first(), { dy: 0.2 }); await r.wait(1500); }, { hold: 1.5 });
await rec.finish({ module: 'm03-greedy-pair-merge', url });
