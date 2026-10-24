// Module 07 challenges: all expected values come from engines/kl.js.
import { choice, fields, combine } from '../../assets/challenges.js';
import { L } from '../../assets/i18n.js';
import * as KL from '../../engines/kl.js';
import { G01, cutsize } from '../../engines/graph.js';

const run = () => KL.run(G01, { initial: KL.SEED });
const trials = r => r.events.filter(e => e.kind === 'trial-swap');

export const challenges = [
  {
    id: 'c1', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o2', title: L('D 值从哪里来', 'Where D comes from'),
    why: L('检查外部与内部边权的区分。', 'Checks that you tell external and internal edge weight apart.'),
    task: L('种子 AE | BCD（A、E 在左）。D(A) 和 D(D) 各是多少？', 'Seed AE | BCD (A and E on the left). What are D(A) and D(D)?'),
    build: () => fields([{ key: 'A', label: 'D(A)' }, { key: 'D', label: 'D(D)' }]),
    check: a => {
      const d = trials(run())[0].dValues;
      if (a.A !== d.A.D) return { ok: false, message: L('A 的边 A–B、A–C 都连到右侧：外部 6，内部 0。', 'A’s edges A–B and A–C both go to the right: external 6, internal 0.') };
      if (a.D !== d.D.D) return { ok: false, message: L('D 在右侧：D–E 连到左侧（外部），C–D 在同侧（内部）。', 'D is on the right: D–E goes to the left (external), C–D stays on the same side (internal).') };
      return { ok: true, message: L(`D(A) = ${d.A.ext} − ${d.A.int} = ${d.A.D}；D(D) = ${d.D.ext} − ${d.D.int} = ${d.D.D}。`, `D(A) = ${d.A.ext} − ${d.A.int} = ${d.A.D}; D(D) = ${d.D.ext} − ${d.D.int} = ${d.D.D}.`) };
    },
    hints: [L('D = 外部边权 − 内部边权。', 'D = external weight − internal weight.'), L('D 的邻居：C（右侧，2）、E（左侧，5）。', 'D’s neighbours: C (right, 2) and E (left, 5).')],
    answer: L('D(A) = 6，D(D) = 3。', 'D(A) = 6, D(D) = 3.'),
    explanation: L('D(v) 是“只把 v 换到对面”时 cut 的下降量。', 'D(v) is how much the cut drops if v alone moves to the other side.')
  },
  {
    id: 'c2', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o2', title: L('找到最大收益对', 'Find the largest-gain pair'),
    why: L('检查成对收益公式与候选枚举。', 'Checks the pair-gain formula and the enumeration of candidates.'),
    task: L('在种子 AE | BCD 上，哪一对交换的收益最大？收益是多少？', 'On seed AE | BCD, which pair’s swap has the largest gain, and what is it?'),
    build: () => combine(choice([['AD', 'A↔D'], ['EB', 'E↔B'], ['ED', 'E↔D'], ['AB', 'A↔B']]), fields([{ key: 'g', label: L('收益 g', 'Gain g') }])),
    check: ([p, f]) => {
      const t = trials(run())[0], best = t.candidates[0];
      if (p !== best.a + best.b) return { ok: false, message: p === 'ED' ? L('D(E) + D(D) = 9，但 E–D 之间有边 5，要减 2 × 5。', 'D(E) + D(D) = 9, but there is an edge of 5 between E and D: subtract 2 × 5.') : L('把 6 个候选对的 D(a) + D(b) − 2w(a,b) 都算出来比较。', 'Work out D(a) + D(b) − 2w(a,b) for all 6 candidate pairs and compare.') };
      if (f.g !== best.gain) return { ok: false, message: L('A 与 D 之间没有边，收益就是 D(A) + D(D)。', 'There is no edge between A and D, so the gain is just D(A) + D(D).') };
      return { ok: true, message: L(`A↔D：${best.Da} + ${best.Db} − 0 = ${best.gain}；次大的是 E↔B（+${t.candidates[1].gain}）。`, `A↔D: ${best.Da} + ${best.Db} − 0 = ${best.gain}; the runner-up is E↔B (+${t.candidates[1].gain}).`) };
    },
    hints: [L('先列出 D：A +6，E +6，B +1，C −4，D +3。', 'List the D values first: A +6, E +6, B +1, C −4, D +3.'), L('只有 A–B、A–C、E–C、E–D 之间有边，要扣 2w。', 'Only A–B, A–C, E–C and E–D have edges, so only they lose 2w.')],
    answer: L('A↔D，收益 9。', 'A↔D, gain 9.'),
    explanation: L('最大收益对不一定是 D 值最大的两个点相加——要扣掉它们之间的边。', 'The largest-gain pair is not always the two largest D values added up: the edge between them is subtracted.')
  },
  {
    id: 'c3', type: L('解释', 'Explain'), difficulty: 'Practice', objectiveId: 'o3', title: L('为什么还要走负收益', 'Why take a negative gain at all'),
    why: L('检查你能否区分试探与接受，并预测试探中的 cut。', 'Checks that you tell a trial from an acceptance, and can predict the cut during the trials.'),
    task: L('A↔D 交换并锁定后，剩下的候选收益全为负。KL 下一步会怎样？那一步之后 cut 是多少？这个 cut 会被接受吗？', 'After A↔D is swapped and locked, every remaining candidate has a negative gain. What does KL do next? What is the cut after that step? Will that cut be accepted?'),
    build: () => combine(choice([['go', L('照样选收益最大的一对（试探）', 'Still pick the largest-gain pair (a trial)')], ['stop', L('停止本轮', 'Stop the pass')]]), fields([{ key: 'cut', label: L('第 2 步试探后的 cut', 'Cut after trial step 2') }]), choice([['acc', L('会被接受', 'It will be accepted')], ['no', L('只是试探，不一定被接受', 'Only a trial; not necessarily accepted')]])),
    check: ([act, f, acc]) => {
      const t = trials(run())[1];
      if (act !== 'go') return { ok: false, message: L('KL 要走完整轮才比较前缀，不在第一个负收益处停下。', 'KL finishes the whole pass before comparing prefixes; it does not stop at the first negative gain.') };
      if (f.cut !== t.metrics.cut) return { ok: false, message: L(`最大的是 ${t.candidates[0].a}↔${t.candidates[0].b}（${t.candidates[0].gain}）：从 cut 3 出发会升到多少？`, `The largest is ${t.candidates[0].a}↔${t.candidates[0].b} (${t.candidates[0].gain}): starting from cut 3, where does it rise to?`) };
      if (acc !== 'no') return { ok: false, message: L('一轮结束后才按最佳前缀决定接受哪几步。', 'Which steps are accepted is decided by the best prefix, only after the pass ends.') };
      return { ok: true, message: L(`第 2 步试探 ${t.candidates[0].a}↔${t.candidates[0].b}（${t.trialGain}），cut 暂升到 ${t.metrics.cut}；它会在回退时被撤回。`, `Step 2 tries ${t.candidates[0].a}↔${t.candidates[0].b} (${t.trialGain}); the cut rises to ${t.metrics.cut} for now, and the rollback undoes it.`) };
    },
    hints: [L('剩下的未锁定节点：左 E，右 B、C。', 'The unlocked nodes left: E on the left, B and C on the right.'), L('E↔C 收益 −8：3 − (−8) = ?', 'E↔C has gain −8: 3 − (−8) = ?')],
    answer: L('照样试探 E↔C；cut 11；不被接受。', 'Try E↔C anyway; cut 11; not accepted.'),
    explanation: L('试探可以变差；在更大的图上，变差的一步可能让后面出现更大的正收益。', 'A trial can make things worse; on a bigger graph, a worse step can open up a larger positive gain later.')
  },
  {
    id: 'c4', type: L('决策', 'Decide'), difficulty: 'Practice', objectiveId: 'o4', title: L('保留几步', 'How many steps to keep'),
    why: L('检查最佳前缀的选择，包括空前缀。', 'Checks the choice of the best prefix, including the empty one.'),
    task: L('第一轮累计收益为 +9、+1；第二轮为 −8、−6。两轮分别保留前几步（k*）？', 'Pass 1’s cumulative gains are +9, +1; pass 2’s are −8, −6. How many leading steps (k*) does each pass keep?'),
    build: () => fields([{ key: 'k1', label: L('第一轮 k*', 'Pass 1 k*') }, { key: 'k2', label: L('第二轮 k*', 'Pass 2 k*') }]),
    check: a => {
      const p = run().result.passes;
      if (a.k1 !== p[0].bestK) return { ok: false, message: L('累计 0、+9、+1：哪个最大？', 'Cumulative 0, +9, +1: which is largest?') };
      if (a.k2 !== p[1].bestK) return { ok: false, message: L('累计 0、−8、−6：什么都不做（k = 0）也是候选。', 'Cumulative 0, −8, −6: doing nothing (k = 0) is a candidate too.') };
      return { ok: true, message: L(`第一轮 k* = ${p[0].bestK}（cut ${p[0].acceptedCut}）；第二轮 k* = ${p[1].bestK}：空前缀，算法停止。`, `Pass 1 k* = ${p[0].bestK} (cut ${p[0].acceptedCut}); pass 2 k* = ${p[1].bestK}: the empty prefix, so the algorithm stops.`) };
    },
    hints: [L('把 k = 0（累计 0）也列进比较。', 'Include k = 0 (cumulative 0) in the comparison.'), L('前缀必须连续，从第 1 步开始。', 'A prefix is consecutive and starts at step 1.')],
    answer: L('第一轮 1；第二轮 0。', 'Pass 1: 1; pass 2: 0.'),
    explanation: L('空前缀胜出说明这一轮没有任何改善，于是停止。', 'When the empty prefix wins, the pass found no improvement at all, so the algorithm stops.')
  },
  {
    id: 'c5', type: L('解释', 'Explain'), difficulty: 'Stretch', objectiveId: 'o2', title: L('减 2w 的那一对', 'The pair that loses 2w'),
    why: L('检查你是否真正理解 −2w 的来源。', 'Checks that you really understand where −2w comes from.'),
    task: L('在种子上计算 g(E, D)。为什么要从 D(E) + D(D) 中减去 2w(E, D)？', 'On the seed, compute g(E, D). Why subtract 2w(E, D) from D(E) + D(D)?'),
    build: () => combine(fields([{ key: 'g', label: 'g(E, D)' }]), choice([['twice', L('DE 被两个 D 都算作外部边，交换后它仍被切', 'DE is counted as external in both D values, and is still cut after the swap')], ['inside', L('交换后 DE 变成内部边', 'After the swap DE becomes internal')], ['none', L('其实不必减', 'There is no need to subtract')]])),
    check: ([f, why]) => {
      const c = trials(run())[0].candidates.find(x => x.a === 'E' && x.b === 'D');
      if (f.g !== c.gain) return { ok: false, message: L(`D(E) + D(D) = ${c.Da + c.Db}，w(E, D) = ${c.w}。`, `D(E) + D(D) = ${c.Da + c.Db}, w(E, D) = ${c.w}.`) };
      if (why !== 'twice') return { ok: false, message: L('交换后 E 在右、D 在左——它们仍分处两侧。', 'After the swap E is on the right and D on the left: still on opposite sides.') };
      const after = { ...KL.SEED, E: 1, D: 0 };
      return { ok: true, message: L(`g(E, D) = ${c.Da + c.Db} − 2×${c.w} = ${c.gain}；直接算 cut：${cutsize(G01, KL.SEED)} → ${cutsize(G01, after)}。`, `g(E, D) = ${c.Da + c.Db} − 2×${c.w} = ${c.gain}; computing the cut directly: ${cutsize(G01, KL.SEED)} → ${cutsize(G01, after)}.`) };
    },
    hints: [L('交换后画一下：E 去右边，D 去左边。', 'Sketch it after the swap: E goes right, D goes left.'), L('DE 交换前被切，交换后还是被切。', 'DE is cut before the swap, and still cut after it.')],
    answer: L('−1；因为 DE 被两个 D 都算作外部边，交换后它仍被切。', '−1; because DE is counted as external in both D values, and is still cut after the swap.'),
    explanation: L('用“交换前后的 cut 之差”可以直接验证：12 → 13，收益 −1。', 'You can check it with the cut before and after: 12 → 13, a gain of −1.')
  },
  {
    id: 'c6', type: L('实现', 'Implement'), difficulty: 'Stretch', objectiveId: 'o5', title: L('换一张图重算', 'Recompute on a changed graph'),
    why: L('检查收益随边权变化，而不是记住一个答案。', 'Checks that the gains follow the weights, rather than a memorised answer.'),
    task: L('把 A–B 从 5 改为 1，种子仍为 AE | BCD。初始 cut 是多少？A↔D 的收益是多少？', 'Change A–B from 5 to 1, keeping seed AE | BCD. What is the initial cut? What is the gain of A↔D?'),
    build: () => fields([{ key: 'cut', label: L('初始 cut', 'Initial cut') }, { key: 'g', label: 'g(A, D)' }]),
    check: a => {
      const g = { nodes: G01.nodes, edges: G01.edges.map(e => e.u === 'A' && e.v === 'B' ? { ...e, w: 1 } : e) };
      const r = KL.run(g, { initial: KL.SEED }), t = r.events.find(e => e.kind === 'trial-swap');
      const ad = t.candidates.find(c => c.a === 'A' && c.b === 'D');
      if (a.cut !== r.events[0].metrics.cut) return { ok: false, message: L('跨组的边：A–B（现在是 1）、A–C、C–E、D–E。', 'The edges across: A–B (now 1), A–C, C–E, D–E.') };
      if (a.g !== ad.gain) return { ok: false, message: L('D(A) 变了：外部 1 + 1 = 2。', 'D(A) has changed: external 1 + 1 = 2.') };
      return { ok: true, message: L(`初始 cut ${r.events[0].metrics.cut}；D(A) = ${ad.Da}，D(D) = ${ad.Db}，g(A, D) = ${ad.gain}。`, `Initial cut ${r.events[0].metrics.cut}; D(A) = ${ad.Da}, D(D) = ${ad.Db}, g(A, D) = ${ad.gain}.`) };
    },
    hints: [L('A 的外部边权变为 1 + 1 = 2。', 'A’s external weight becomes 1 + 1 = 2.'), L('D(D) 不受影响，仍是 3。', 'D(D) is unaffected: still 3.')],
    answer: L('初始 cut 8；g(A, D) = 5。', 'Initial cut 8; g(A, D) = 5.'),
    explanation: L('改一条边就要重算所有 D 值；Python 检查器也用随机图防止只记住五节点答案。', 'Changing one edge means recomputing every D value; the Python checker also uses random graphs, so a memorised five-node answer won’t pass.')
  }
];
