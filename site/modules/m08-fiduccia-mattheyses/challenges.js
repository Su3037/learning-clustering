// Module 08 challenges: all values from engines/fm.js (net-based gains, balance window, exhaustive check).
import { choice, fields, combine } from '../../assets/challenges.js';
import * as FM from '../../engines/fm.js';
import { G01 } from '../../engines/graph.js';

const run = () => FM.run(G01, { initial: FM.SEED, maxDiff: 1 });

export const challenges = [
  {
    id: 'c1', type: '合法性', difficulty: 'Intro', objectiveId: 'o2', title: '为什么不选 A',
    why: '检查“最大”只在合法候选中比较。',
    task: '种子 AE | BCD，maxDiff = 1。A 的收益是 +6，是最大的之一。第一步应移动哪个节点？为什么不移动 A？',
    build: () => combine(choice([['A', '移动 A'], ['D', '移动 D'], ['B', '移动 B'], ['E', '移动 E']]), choice([['bal', 'A 移走后左侧只剩 1 人，违反平衡'], ['neg', 'A 的收益其实是负的'], ['lock', 'A 已被锁定']])),
    check: ([v, why]) => {
      const r = run(), first = r.result.passes[0].moves[0], g0 = Object.fromEntries(r.events[0].gains.map(x => [x.node, x]));
      if (v !== first.node) return { ok: false, message: v === 'A' || v === 'E' ? `${v} 在只有 2 人的一侧，移走后 |1 − 4| = 3 > 1。` : `${v} 合法，但收益 ${g0[v].gain} 不是合法候选里最大的。` };
      if (why !== 'bal') return { ok: false, message: 'A 的收益确实是 +6，也没有被锁定。' };
      return { ok: true, message: `合法候选：${r.events[0].gains.filter(x => x.legal).map(x => `${x.node}(${x.gain > 0 ? '+' : ''}${x.gain})`).join('、')}；选 ${first.node}。` };
    },
    hints: ['先看哪些节点移动后仍是 2 : 3 或 3 : 2。', 'A、E 都在左侧（只有 2 人）。'],
    answer: '移动 D（+3）；A 移走后左侧只剩 1 人，违反平衡。',
    explanation: 'D 移过去以后，左侧有 3 人，A 才变成合法候选，下一步收益 +6。'
  },
  {
    id: 'c2', type: '推演', difficulty: 'Intro', objectiveId: 'o3', title: '拆开 D 的收益',
    why: '检查 FS / TE 的判定。',
    task: '种子 AE | BCD 上，D 的收益由哪两部分组成？填写 FS 部分的权重、TE 部分的权重和总收益。',
    build: () => fields([{ key: 'fs', label: 'FS（+）' }, { key: 'te', label: 'TE（−）' }, { key: 'g', label: '收益' }]),
    check: a => {
      const m = run().result.passes[0].moves[0];
      const fs = m.fs.reduce((s, x) => s + x.w, 0), te = m.te.reduce((s, x) => s + x.w, 0);
      if (a.fs !== fs) return { ok: false, message: 'FS：D 是哪条边在右侧唯一的端点？D–E 的另一端在左侧。' };
      if (Math.abs(a.te) !== te) return { ok: false, message: 'TE：哪条边在左侧（目标侧）一个端点都没有？C–D 两端都在右侧。' };
      if (a.g !== m.gain) return { ok: false, message: '收益 = FS − TE。' };
      return { ok: true, message: `FS = D–E ${fs}，TE = C–D ${te}，收益 ${m.gain}；移动后 cut ${m.cutBefore} → ${m.cutAfter}。` };
    },
    hints: ['D 的边：C–D（2，C 在右）与 D–E（5，E 在左）。', 'D–E 移动后不再被切（+5）；C–D 移动后开始被切（−2）。'],
    answer: 'FS 5，TE 2，收益 3。',
    explanation: '对二端边，FS − TE 就是外部边权 − 内部边权。多引脚 net 要按两侧的引脚计数判断。'
  },
  {
    id: 'c3', type: '回退', difficulty: 'Practice', objectiveId: 'o4', title: '选出 k*',
    why: '检查最佳前缀的选择，以及区分试探终点与接受状态。',
    task: '第一轮试探的累计收益为 3、9、7、1、0。保留前几步？接受的 cut 是多少？',
    build: () => fields([{ key: 'k', label: 'k*' }, { key: 'cut', label: '接受的 cut' }]),
    check: a => {
      const p = run().result.passes[0];
      if (a.k !== p.bestK) return { ok: false, message: '找累计收益最大的位置（包括 k = 0 的 0）。' };
      if (a.cut !== p.acceptedCut) return { ok: false, message: `起点 cut ${p.startCut}，减去最佳累计收益。不要报告试探终点的 cut ${p.moves.at(-1).cutAfter}。` };
      return { ok: true, message: `k* = ${p.bestK}：只应用 D、A，接受 cut ${p.acceptedCut}；试探终点 cut ${p.moves.at(-1).cutAfter} 被丢弃。` };
    },
    hints: ['最大的累计收益是 9。', '12 − 9 = ?'],
    answer: 'k* = 2，接受 cut 3。',
    explanation: '第二轮从 ABC | DE 出发，最佳前缀为空，算法停止。'
  },
  {
    id: 'c4', type: '纠错', difficulty: 'Practice', objectiveId: 'o5', title: '审查原附件的反例',
    why: '检查你能否用计算核验一段说明，而不是直接相信它。',
    task: '原附件 hillclimb：边 A–B 6、A–C 4、B–D 4、C–D 1、C–E 4、D–F 4、E–F 6；种子 ABE | CDF，maxDiff = 2。原文说“初始 cut 9，所有合法移动收益 ≤ 0”。请算出真实的初始 cut，以及 E 的收益（它合法吗？）。',
    build: () => combine(fields([{ key: 'cut', label: '初始 cut' }, { key: 'gE', label: 'E 的收益' }]), choice([['legal', 'E 的移动合法'], ['illegal', 'E 的移动不合法']])),
    check: ([f, l]) => {
      const h = FM.LEGACY_HILLCLIMB, r = FM.run(h, { initial: h.seed, maxDiff: h.maxDiff, firstPassOnly: true });
      const e = r.events[0].gains.find(x => x.node === 'E');
      if (f.cut !== r.events[0].metrics.cut) return { ok: false, message: '跨组的边：A–C、B–D、C–E、E–F……逐条加起来。' };
      if (f.gE !== e.gain) return { ok: false, message: 'E 在左：C–E（C 在右）和 E–F（F 在右）都是外部边。' };
      if ((l === 'legal') !== e.legal) return { ok: false, message: '移动后两侧为 2 : 4，差 2 ≤ maxDiff。' };
      return { ok: true, message: `初始 cut ${r.events[0].metrics.cut}（不是 9），E 合法且收益 +${e.gain}——原文的说法不成立；首轮最佳 cut ${r.result.passes[0].acceptedCut}，穷举最优 ${FM.exhaustive(h, 2).cut}。` };
    },
    hints: ['被切的边：A–C 4、B–D 4、C–E 4、E–F 6。', 'E 的两条边都连到右侧：移过去收益 4 + 6。'],
    answer: '初始 cut 18；E 合法，收益 +10。',
    explanation: '用独立计算（逐个合法移动的收益 + 穷举最优）核验反例，再决定能否写进教材。'
  },
  {
    id: 'c5', type: '探索', difficulty: 'Stretch', objectiveId: 'o5', title: '先负后正',
    why: '检查你能否在一个经过核验的反例上，说明负收益试探的作用。',
    task: '替换反例：边 A–C 4、A–E 5、B–C 2、B–E 1、C–F 3、D–E 1、E–F 1；种子 ADE | BCF，maxDiff = 2。只接受正收益的爬山法停在哪个 cut？FM 一轮后接受的 cut 是多少？',
    build: () => fields([{ key: 'hill', label: '爬山法的 cut' }, { key: 'fm', label: 'FM 接受的 cut' }]),
    check: a => {
      const e = FM.NEG_ESCAPE, r = FM.run(e, { initial: e.seed, maxDiff: 2 });
      const allNonPos = r.events[0].gains.filter(x => x.legal).every(x => x.gain <= 0);
      if (a.hill !== r.result.passes[0].startCut) return { ok: false, message: allNonPos ? '初始时所有合法移动的收益都 ≤ 0：爬山法一步也走不了。' : '再看初始收益。' };
      if (a.fm !== r.result.passes[0].acceptedCut) return { ok: false, message: '在实验里选这个例子单步：前两步是 −1、−1，第三步呢？' };
      return { ok: true, message: `爬山法停在 ${r.result.passes[0].startCut}；FM 试探 ${r.result.passes[0].moves.slice(0, 3).map(m => `${m.node}(${m.gain > 0 ? '+' : ''}${m.gain})`).join('、')}，保留 ${r.result.passes[0].bestK} 步，cut ${r.result.passes[0].acceptedCut}——穷举最优也是 ${FM.exhaustive(e, 2).cut}。` };
    },
    hints: ['初始合法收益：A、B、C、D 为 −1，F 为 −2，E 为 −4。', 'FM 走完 A、B 之后，E 的收益变成 +4。'],
    answer: '爬山法 6；FM 4。',
    explanation: '先变差的两步改变了 E 周围的局面。这是本课程用固定种子搜索、再穷举核验得到的反例。'
  },
  {
    id: 'c6', type: '拓展', difficulty: 'Stretch', objectiveId: 'o6', title: '多引脚 net 的收益',
    why: '检查你是否按引脚计数计算 FS/TE，而不是把 net 拆成边。',
    task: '一个 net 连着 A、B、C、D（权 3）。A、B、C 在左，D 在右。按引脚计数，A 的收益是多少？D 的收益是多少？',
    build: () => fields([{ key: 'a', label: 'A 的收益' }, { key: 'd', label: 'D 的收益' }]),
    check: f => {
      const n = FM.toNets({ nodes: ['A', 'B', 'C', 'D'], nets: [{ id: 'bus', pins: ['A', 'B', 'C', 'D'], w: 3 }] });
      const g = FM.gainsFromScratch(n.nets, { A: 0, B: 0, C: 0, D: 1 }, n.ids);
      if (f.a !== g.A.gain) return { ok: false, message: f.a === -1 ? '这是把 net 拆成团再按边算的结果；按引脚计数，A 移走后 net 两侧仍各有引脚。' : 'A 移走后，左侧还有 B、C，右侧有 D 和 A：net 仍被切。' };
      if (f.d !== g.D.gain) return { ok: false, message: 'D 是这个 net 在右侧唯一的引脚：移过去 net 就不再被切。' };
      return { ok: true, message: `A：${g.A.gain}；D：+${g.D.gain}（FS）。` };
    },
    hints: ['FS：v 是 net 在本侧唯一的引脚。TE：net 在目标侧没有引脚。', '对 A：本侧还有 B、C；目标侧有 D。'],
    answer: 'A 的收益 0；D 的收益 +3。',
    explanation: '把 4 引脚 net 拆成团（每对 1）再按边算，会得到 A 的“收益” −1。本课程引擎按引脚计数实现多引脚 net，标为拓展。'
  }
];
