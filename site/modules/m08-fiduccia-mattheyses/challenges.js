// Module 08 challenges: all values from engines/fm.js (net-based gains, balance window, exhaustive check).
import { choice, fields, combine } from '../../assets/challenges.js';
import { L } from '../../assets/i18n.js';
import * as FM from '../../engines/fm.js';
import { G01 } from '../../engines/graph.js';

const run = () => FM.run(G01, { initial: FM.SEED, maxDiff: 1 });
const signed = g => (g > 0 ? '+' : '') + g;

export const challenges = [
  {
    id: 'c1', type: L('合法性', 'Legality'), difficulty: 'Intro', objectiveId: 'o2', title: L('为什么不选 A', 'Why not A'),
    why: L('检查“最大”只在合法候选中比较。', 'Checks that “largest” is compared among legal candidates only.'),
    task: L('种子 AE | BCD，maxDiff = 1。A 的收益是 +6，是最大的之一。第一步应移动哪个节点？为什么不移动 A？', 'Seed AE | BCD, maxDiff = 1. A’s gain is +6, one of the largest. Which node should the first step move, and why not A?'),
    build: () => combine(choice([['A', L('移动 A', 'Move A')], ['D', L('移动 D', 'Move D')], ['B', L('移动 B', 'Move B')], ['E', L('移动 E', 'Move E')]]),
      choice([['bal', L('A 移走后左侧只剩 1 人，违反平衡', 'Moving A leaves 1 node on the left, which breaks the balance')], ['neg', L('A 的收益其实是负的', 'A’s gain is actually negative')], ['lock', L('A 已被锁定', 'A is already locked')]])),
    check: ([v, why]) => {
      const r = run(), first = r.result.passes[0].moves[0], g0 = Object.fromEntries(r.events[0].gains.map(x => [x.node, x]));
      if (v !== first.node) return { ok: false, message: v === 'A' || v === 'E' ? L(`${v} 在只有 2 人的一侧，移走后 |1 − 4| = 3 > 1。`, `${v} is on the side with only 2 nodes; after the move |1 − 4| = 3 > 1.`) : L(`${v} 合法，但收益 ${g0[v].gain} 不是合法候选里最大的。`, `${v} is legal, but its gain ${g0[v].gain} is not the largest among the legal candidates.`) };
      if (why !== 'bal') return { ok: false, message: L('A 的收益确实是 +6，也没有被锁定。', 'A’s gain really is +6, and it is not locked.') };
      const legal = r.events[0].gains.filter(x => x.legal).map(x => `${x.node}(${signed(x.gain)})`);
      return { ok: true, message: L(`合法候选：${legal.join('、')}；选 ${first.node}。`, `Legal candidates: ${legal.join(', ')}; choose ${first.node}.`) };
    },
    hints: [L('先看哪些节点移动后仍是 2 : 3 或 3 : 2。', 'First see which nodes leave the sides at 2 : 3 or 3 : 2 after moving.'), L('A、E 都在左侧（只有 2 人）。', 'A and E are both on the left (only 2 nodes).')],
    answer: L('移动 D（+3）；A 移走后左侧只剩 1 人，违反平衡。', 'Move D (+3); moving A leaves 1 node on the left, which breaks the balance.'),
    explanation: L('D 移过去以后，左侧有 3 人，A 才变成合法候选，下一步收益 +6。', 'Once D has moved, the left has 3 nodes, and only then does A become a legal candidate, with gain +6 at the next step.')
  },
  {
    id: 'c2', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o3', title: L('拆开 D 的收益', 'Split D’s gain'),
    why: L('检查 FS / TE 的判定。', 'Checks how FS and TE are decided.'),
    task: L('种子 AE | BCD 上，D 的收益由哪两部分组成？填写 FS 部分的权重、TE 部分的权重和总收益。', 'On seed AE | BCD, which two parts make up D’s gain? Enter the FS weight, the TE weight and the total gain.'),
    build: () => fields([{ key: 'fs', label: L('FS（+）', 'FS (+)') }, { key: 'te', label: L('TE（−）', 'TE (−)') }, { key: 'g', label: L('收益', 'Gain') }]),
    check: a => {
      const m = run().result.passes[0].moves[0];
      const fs = m.fs.reduce((s, x) => s + x.w, 0), te = m.te.reduce((s, x) => s + x.w, 0);
      if (a.fs !== fs) return { ok: false, message: L('FS：D 是哪条边在右侧唯一的端点？D–E 的另一端在左侧。', 'FS: of which edge is D the only end on the right? D–E’s other end is on the left.') };
      if (Math.abs(a.te) !== te) return { ok: false, message: L('TE：哪条边在左侧（目标侧）一个端点都没有？C–D 两端都在右侧。', 'TE: which edge has no end on the left (the target side)? Both ends of C–D are on the right.') };
      if (a.g !== m.gain) return { ok: false, message: L('收益 = FS − TE。', 'Gain = FS − TE.') };
      return { ok: true, message: L(`FS = D–E ${fs}，TE = C–D ${te}，收益 ${m.gain}；移动后 cut ${m.cutBefore} → ${m.cutAfter}。`, `FS = D–E ${fs}, TE = C–D ${te}, gain ${m.gain}; after the move the cut goes ${m.cutBefore} → ${m.cutAfter}.`) };
    },
    hints: [L('D 的边：C–D（2，C 在右）与 D–E（5，E 在左）。', 'D’s edges: C–D (2, C on the right) and D–E (5, E on the left).'), L('D–E 移动后不再被切（+5）；C–D 移动后开始被切（−2）。', 'After the move D–E is no longer cut (+5); C–D becomes cut (−2).')],
    answer: L('FS 5，TE 2，收益 3。', 'FS 5, TE 2, gain 3.'),
    explanation: L('对二端边，FS − TE 就是外部边权 − 内部边权。多引脚 net 要按两侧的引脚计数判断。', 'For 2-pin edges, FS − TE is just external weight − internal weight. A multi-pin net is decided by counting its pins on each side.')
  },
  {
    id: 'c3', type: L('回退', 'Roll back'), difficulty: 'Practice', objectiveId: 'o4', title: L('选出 k*', 'Choose k*'),
    why: L('检查最佳前缀的选择，以及区分试探终点与接受状态。', 'Checks the choice of the best prefix, and telling the end of the trials from the accepted state.'),
    task: L('第一轮试探的累计收益为 3、9、7、1、0。保留前几步？接受的 cut 是多少？', 'Pass 1’s cumulative trial gains are 3, 9, 7, 1, 0. How many steps are kept, and what cut is accepted?'),
    build: () => fields([{ key: 'k', label: 'k*' }, { key: 'cut', label: L('接受的 cut', 'Accepted cut') }]),
    check: a => {
      const p = run().result.passes[0];
      if (a.k !== p.bestK) return { ok: false, message: L('找累计收益最大的位置（包括 k = 0 的 0）。', 'Find where the cumulative gain peaks (including 0 at k = 0).') };
      if (a.cut !== p.acceptedCut) return { ok: false, message: L(`起点 cut ${p.startCut}，减去最佳累计收益。不要报告试探终点的 cut ${p.moves.at(-1).cutAfter}。`, `Start from cut ${p.startCut} and subtract the best cumulative gain. Don’t report the cut ${p.moves.at(-1).cutAfter} where the trials ended.`) };
      return { ok: true, message: L(`k* = ${p.bestK}：只应用 D、A，接受 cut ${p.acceptedCut}；试探终点 cut ${p.moves.at(-1).cutAfter} 被丢弃。`, `k* = ${p.bestK}: apply only D and A, accept cut ${p.acceptedCut}; the trials’ end at cut ${p.moves.at(-1).cutAfter} is discarded.`) };
    },
    hints: [L('最大的累计收益是 9。', 'The largest cumulative gain is 9.'), '12 − 9 = ?'],
    answer: L('k* = 2，接受 cut 3。', 'k* = 2, accepted cut 3.'),
    explanation: L('第二轮从 ABC | DE 出发，最佳前缀为空，算法停止。', 'Pass 2 starts from ABC | DE; its best prefix is empty, and the algorithm stops.')
  },
  {
    id: 'c4', type: L('纠错', 'Debug'), difficulty: 'Practice', objectiveId: 'o5', title: L('审查原附件的反例', 'Audit the attachment’s example'),
    why: L('检查你能否用计算核验一段说明，而不是直接相信它。', 'Checks that you verify a claim by computing it rather than taking it on trust.'),
    task: L('原附件 hillclimb：边 A–B 6、A–C 4、B–D 4、C–D 1、C–E 4、D–F 4、E–F 6；种子 ABE | CDF，maxDiff = 2。原文说“初始 cut 9，所有合法移动收益 ≤ 0”。请算出真实的初始 cut，以及 E 的收益（它合法吗？）。',
      'The attachment’s hillclimb: edges A–B 6, A–C 4, B–D 4, C–D 1, C–E 4, D–F 4, E–F 6; seed ABE | CDF, maxDiff = 2. The text says “initial cut 9, every legal move has gain ≤ 0”. Compute the real initial cut and E’s gain (is E’s move legal?).'),
    build: () => combine(fields([{ key: 'cut', label: L('初始 cut', 'Initial cut') }, { key: 'gE', label: L('E 的收益', 'E’s gain') }]), choice([['legal', L('E 的移动合法', 'E’s move is legal')], ['illegal', L('E 的移动不合法', 'E’s move is not legal')]])),
    check: ([f, l]) => {
      const h = FM.LEGACY_HILLCLIMB, r = FM.run(h, { initial: h.seed, maxDiff: h.maxDiff, firstPassOnly: true });
      const e = r.events[0].gains.find(x => x.node === 'E');
      if (f.cut !== r.events[0].metrics.cut) return { ok: false, message: L('跨组的边：A–C、B–D、C–E、E–F……逐条加起来。', 'The edges across: A–C, B–D, C–E, E–F… add them one by one.') };
      if (f.gE !== e.gain) return { ok: false, message: L('E 在左：C–E（C 在右）和 E–F（F 在右）都是外部边。', 'E is on the left: C–E (C on the right) and E–F (F on the right) are both external.') };
      if ((l === 'legal') !== e.legal) return { ok: false, message: L('移动后两侧为 2 : 4，差 2 ≤ maxDiff。', 'After the move the sides are 2 : 4, a difference of 2 ≤ maxDiff.') };
      return { ok: true, message: L(`初始 cut ${r.events[0].metrics.cut}（不是 9），E 合法且收益 +${e.gain}——原文的说法不成立；首轮最佳 cut ${r.result.passes[0].acceptedCut}，穷举最优 ${FM.exhaustive(h, 2).cut}。`,
        `Initial cut ${r.events[0].metrics.cut} (not 9), and E is legal with gain +${e.gain}: the text’s claim does not hold. Pass 1’s best cut is ${r.result.passes[0].acceptedCut}; the exhaustive optimum is ${FM.exhaustive(h, 2).cut}.`) };
    },
    hints: [L('被切的边：A–C 4、B–D 4、C–E 4、E–F 6。', 'The cut edges: A–C 4, B–D 4, C–E 4, E–F 6.'), L('E 的两条边都连到右侧：移过去收益 4 + 6。', 'Both of E’s edges go to the right: moving it gains 4 + 6.')],
    answer: L('初始 cut 18；E 合法，收益 +10。', 'Initial cut 18; E is legal, with gain +10.'),
    explanation: L('用独立计算（逐个合法移动的收益 + 穷举最优）核验反例，再决定能否写进教材。', 'Check an example with an independent computation (the gain of every legal move, plus the exhaustive optimum) before deciding whether it can go into teaching material.')
  },
  {
    id: 'c5', type: L('探索', 'Explore'), difficulty: 'Stretch', objectiveId: 'o5', title: L('先负后正', 'Negative first, then positive'),
    why: L('检查你能否在一个经过核验的反例上，说明负收益试探的作用。', 'Checks that you can show, on a verified example, what trying negative gains is for.'),
    task: L('替换反例：边 A–C 4、A–E 5、B–C 2、B–E 1、C–F 3、D–E 1、E–F 1；种子 ADE | BCF，maxDiff = 2。只接受正收益的爬山法停在哪个 cut？FM 一轮后接受的 cut 是多少？',
      'The replacement example: edges A–C 4, A–E 5, B–C 2, B–E 1, C–F 3, D–E 1, E–F 1; seed ADE | BCF, maxDiff = 2. At what cut does hill climbing on positive gains stop? What cut does FM accept after one pass?'),
    build: () => fields([{ key: 'hill', label: L('爬山法的 cut', 'Hill climbing’s cut') }, { key: 'fm', label: L('FM 接受的 cut', 'FM’s accepted cut') }]),
    check: a => {
      const e = FM.NEG_ESCAPE, r = FM.run(e, { initial: e.seed, maxDiff: 2 }), p = r.result.passes[0];
      const allNonPos = r.events[0].gains.filter(x => x.legal).every(x => x.gain <= 0);
      if (a.hill !== p.startCut) return { ok: false, message: allNonPos ? L('初始时所有合法移动的收益都 ≤ 0：爬山法一步也走不了。', 'At the start every legal move has gain ≤ 0: hill climbing cannot take a single step.') : L('再看初始收益。', 'Look at the initial gains again.') };
      if (a.fm !== p.acceptedCut) return { ok: false, message: L('在实验里选这个例子单步：前两步是 −1、−1，第三步呢？', 'Pick this example in the lab and step: the first two steps are −1, −1; what is the third?') };
      const steps = p.moves.slice(0, 3).map(m => `${m.node}(${signed(m.gain)})`);
      return { ok: true, message: L(`爬山法停在 ${p.startCut}；FM 试探 ${steps.join('、')}，保留 ${p.bestK} 步，cut ${p.acceptedCut}——穷举最优也是 ${FM.exhaustive(e, 2).cut}。`,
        `Hill climbing stops at ${p.startCut}; FM tries ${steps.join(', ')}, keeps ${p.bestK} steps, cut ${p.acceptedCut}, and the exhaustive optimum is ${FM.exhaustive(e, 2).cut} too.`) };
    },
    hints: [L('初始合法收益：A、B、C、D 为 −1，F 为 −2，E 为 −4。', 'Initial legal gains: A, B, C, D are −1, F is −2, E is −4.'), L('FM 走完 A、B 之后，E 的收益变成 +4。', 'Once FM has moved A and B, E’s gain becomes +4.')],
    answer: L('爬山法 6；FM 4。', 'Hill climbing 6; FM 4.'),
    explanation: L('先变差的两步改变了 E 周围的局面。这是本课程用固定种子搜索、再穷举核验得到的反例。', 'The two steps that first make things worse change E’s surroundings. This course found the example by a seeded search and verified it exhaustively.')
  },
  {
    id: 'c6', type: L('拓展', 'Extension'), difficulty: 'Stretch', objectiveId: 'o6', title: L('多引脚 net 的收益', 'The gain on a multi-pin net'),
    why: L('检查你是否按引脚计数计算 FS/TE，而不是把 net 拆成边。', 'Checks that you compute FS/TE by counting pins, not by splitting the net into edges.'),
    task: L('一个 net 连着 A、B、C、D（权 3）。A、B、C 在左，D 在右。按引脚计数，A 的收益是多少？D 的收益是多少？', 'One net connects A, B, C, D (weight 3). A, B, C are on the left, D on the right. Counting pins, what is A’s gain? What is D’s gain?'),
    build: () => fields([{ key: 'a', label: L('A 的收益', 'A’s gain') }, { key: 'd', label: L('D 的收益', 'D’s gain') }]),
    check: f => {
      const n = FM.toNets({ nodes: ['A', 'B', 'C', 'D'], nets: [{ id: 'bus', pins: ['A', 'B', 'C', 'D'], w: 3 }] });
      const g = FM.gainsFromScratch(n.nets, { A: 0, B: 0, C: 0, D: 1 }, n.ids);
      if (f.a !== g.A.gain) return { ok: false, message: f.a === -1 ? L('这是把 net 拆成团再按边算的结果；按引脚计数，A 移走后 net 两侧仍各有引脚。', 'That is the result of splitting the net into a clique and counting edges; counting pins, the net still has pins on both sides after A moves.') : L('A 移走后，左侧还有 B、C，右侧有 D 和 A：net 仍被切。', 'After A moves, B and C remain on the left and D and A are on the right: the net is still cut.') };
      if (f.d !== g.D.gain) return { ok: false, message: L('D 是这个 net 在右侧唯一的引脚：移过去 net 就不再被切。', 'D is the net’s only pin on the right: once it moves, the net is no longer cut.') };
      return { ok: true, message: L(`A：${g.A.gain}；D：+${g.D.gain}（FS）。`, `A: ${g.A.gain}; D: +${g.D.gain} (FS).`) };
    },
    hints: [L('FS：v 是 net 在本侧唯一的引脚。TE：net 在目标侧没有引脚。', 'FS: v is the net’s only pin on its side. TE: the net has no pin on the target side.'), L('对 A：本侧还有 B、C；目标侧有 D。', 'For A: B and C remain on its side; D is on the target side.')],
    answer: L('A 的收益 0；D 的收益 +3。', 'A’s gain 0; D’s gain +3.'),
    explanation: L('把 4 引脚 net 拆成团（每对 1）再按边算，会得到 A 的“收益” −1。本课程引擎按引脚计数实现多引脚 net，标为拓展。', 'Splitting the 4-pin net into a clique (1 per pair) and counting edges would give A a “gain” of −1. This course’s engine counts pins for multi-pin nets, marked as an extension.')
  }
];
