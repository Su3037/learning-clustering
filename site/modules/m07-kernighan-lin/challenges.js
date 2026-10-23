// Module 07 challenges: all expected values come from engines/kl.js.
import { choice, fields, combine } from '../../assets/challenges.js';
import * as KL from '../../engines/kl.js';
import { G01, cutsize } from '../../engines/graph.js';

const run = () => KL.run(G01, { initial: KL.SEED });
const trials = r => r.events.filter(e => e.kind === 'trial-swap');

export const challenges = [
  {
    id: 'c1', type: '推演', difficulty: 'Intro', objectiveId: 'o2', title: 'D 值从哪里来',
    why: '检查外部与内部边权的区分。',
    task: '种子 AE | BCD（A、E 在左）。D(A) 和 D(D) 各是多少？',
    build: () => fields([{ key: 'A', label: 'D(A)' }, { key: 'D', label: 'D(D)' }]),
    check: a => {
      const d = trials(run())[0].dValues;
      if (a.A !== d.A.D) return { ok: false, message: 'A 的边 A–B、A–C 都连到右侧：外部 6，内部 0。' };
      if (a.D !== d.D.D) return { ok: false, message: 'D 在右侧：D–E 连到左侧（外部），C–D 在同侧（内部）。' };
      return { ok: true, message: `D(A) = ${d.A.ext} − ${d.A.int} = ${d.A.D}；D(D) = ${d.D.ext} − ${d.D.int} = ${d.D.D}。` };
    },
    hints: ['D = 外部边权 − 内部边权。', 'D 的邻居：C（右侧，2）、E（左侧，5）。'],
    answer: 'D(A) = 6，D(D) = 3。',
    explanation: 'D(v) 是“只把 v 换到对面”时 cut 的下降量。'
  },
  {
    id: 'c2', type: '推演', difficulty: 'Intro', objectiveId: 'o2', title: '找到最大收益对',
    why: '检查成对收益公式与候选枚举。',
    task: '在种子 AE | BCD 上，哪一对交换的收益最大？收益是多少？',
    build: () => combine(choice([['AD', 'A↔D'], ['EB', 'E↔B'], ['ED', 'E↔D'], ['AB', 'A↔B']]), fields([{ key: 'g', label: '收益 g' }])),
    check: ([p, f]) => {
      const t = trials(run())[0], best = t.candidates[0];
      if (p !== best.a + best.b) return { ok: false, message: p === 'ED' ? 'D(E) + D(D) = 9，但 E–D 之间有边 5，要减 2 × 5。' : '把 6 个候选对的 D(a) + D(b) − 2w(a,b) 都算出来比较。' };
      if (f.g !== best.gain) return { ok: false, message: 'A 与 D 之间没有边，收益就是 D(A) + D(D)。' };
      return { ok: true, message: `A↔D：${best.Da} + ${best.Db} − 0 = ${best.gain}；次大的是 E↔B（+${t.candidates[1].gain}）。` };
    },
    hints: ['先列出 D：A +6，E +6，B +1，C −4，D +3。', '只有 A–B、A–C、E–C、E–D 之间有边，要扣 2w。'],
    answer: 'A↔D，收益 9。',
    explanation: '最大收益对不一定是 D 值最大的两个点相加——要扣掉它们之间的边。'
  },
  {
    id: 'c3', type: '解释', difficulty: 'Practice', objectiveId: 'o3', title: '为什么还要走负收益',
    why: '检查你能否区分试探与接受，并预测试探中的 cut。',
    task: 'A↔D 交换并锁定后，剩下的候选收益全为负。KL 下一步会怎样？那一步之后 cut 是多少？这个 cut 会被接受吗？',
    build: () => combine(choice([['go', '照样选收益最大的一对（试探）'], ['stop', '停止本轮']]), fields([{ key: 'cut', label: '第 2 步试探后的 cut' }]), choice([['acc', '会被接受'], ['no', '只是试探，不一定被接受']])),
    check: ([act, f, acc]) => {
      const t = trials(run())[1];
      if (act !== 'go') return { ok: false, message: 'KL 要走完整轮才比较前缀，不在第一个负收益处停下。' };
      if (f.cut !== t.metrics.cut) return { ok: false, message: `最大的是 ${t.candidates[0].a}↔${t.candidates[0].b}（${t.candidates[0].gain}）：从 cut 3 出发会升到多少？` };
      if (acc !== 'no') return { ok: false, message: '一轮结束后才按最佳前缀决定接受哪几步。' };
      return { ok: true, message: `第 2 步试探 ${t.candidates[0].a}↔${t.candidates[0].b}（${t.trialGain}），cut 暂升到 ${t.metrics.cut}；它会在回退时被撤回。` };
    },
    hints: ['剩下的未锁定节点：左 E，右 B、C。', 'E↔C 收益 −8：3 − (−8) = ?'],
    answer: '照样试探 E↔C；cut 11；不被接受。',
    explanation: '试探可以变差；在更大的图上，变差的一步可能让后面出现更大的正收益。'
  },
  {
    id: 'c4', type: '决策', difficulty: 'Practice', objectiveId: 'o4', title: '保留几步',
    why: '检查最佳前缀的选择，包括空前缀。',
    task: '第一轮累计收益为 +9、+1；第二轮为 −8、−6。两轮分别保留前几步（k*）？',
    build: () => fields([{ key: 'k1', label: '第一轮 k*' }, { key: 'k2', label: '第二轮 k*' }]),
    check: a => {
      const p = run().result.passes;
      if (a.k1 !== p[0].bestK) return { ok: false, message: '累计 0、+9、+1：哪个最大？' };
      if (a.k2 !== p[1].bestK) return { ok: false, message: '累计 0、−8、−6：什么都不做（k = 0）也是候选。' };
      return { ok: true, message: `第一轮 k* = ${p[0].bestK}（cut ${p[0].acceptedCut}）；第二轮 k* = ${p[1].bestK}：空前缀，算法停止。` };
    },
    hints: ['把 k = 0（累计 0）也列进比较。', '前缀必须连续，从第 1 步开始。'],
    answer: '第一轮 1；第二轮 0。',
    explanation: '空前缀胜出说明这一轮没有任何改善，于是停止。'
  },
  {
    id: 'c5', type: '解释', difficulty: 'Stretch', objectiveId: 'o2', title: '减 2w 的那一对',
    why: '检查你是否真正理解 −2w 的来源。',
    task: '在种子上计算 g(E, D)。为什么要从 D(E) + D(D) 中减去 2w(E, D)？',
    build: () => combine(fields([{ key: 'g', label: 'g(E, D)' }]), choice([['twice', 'DE 被两个 D 都算作外部边，交换后它仍被切'], ['inside', '交换后 DE 变成内部边'], ['none', '其实不必减']])),
    check: ([f, why]) => {
      const c = trials(run())[0].candidates.find(x => x.a === 'E' && x.b === 'D');
      if (f.g !== c.gain) return { ok: false, message: `D(E) + D(D) = ${c.Da + c.Db}，w(E, D) = ${c.w}。` };
      if (why !== 'twice') return { ok: false, message: '交换后 E 在右、D 在左——它们仍分处两侧。' };
      const after = { ...KL.SEED, E: 1, D: 0 };
      return { ok: true, message: `g(E, D) = ${c.Da + c.Db} − 2×${c.w} = ${c.gain}；直接算 cut：${cutsize(G01, KL.SEED)} → ${cutsize(G01, after)}。` };
    },
    hints: ['交换后画一下：E 去右边，D 去左边。', 'DE 交换前被切，交换后还是被切。'],
    answer: '−1；因为 DE 被两个 D 都算作外部边，交换后它仍被切。',
    explanation: '用“交换前后的 cut 之差”可以直接验证：12 → 13，收益 −1。'
  },
  {
    id: 'c6', type: '实现', difficulty: 'Stretch', objectiveId: 'o5', title: '换一张图重算',
    why: '检查收益随边权变化，而不是记住一个答案。',
    task: '把 A–B 从 5 改为 1，种子仍为 AE | BCD。初始 cut 是多少？A↔D 的收益是多少？',
    build: () => fields([{ key: 'cut', label: '初始 cut' }, { key: 'g', label: 'g(A, D)' }]),
    check: a => {
      const g = { nodes: G01.nodes, edges: G01.edges.map(e => e.u === 'A' && e.v === 'B' ? { ...e, w: 1 } : e) };
      const r = KL.run(g, { initial: KL.SEED }), t = r.events.find(e => e.kind === 'trial-swap');
      const ad = t.candidates.find(c => c.a === 'A' && c.b === 'D');
      if (a.cut !== r.events[0].metrics.cut) return { ok: false, message: '跨组的边：A–B（现在是 1）、A–C、C–E、D–E。' };
      if (a.g !== ad.gain) return { ok: false, message: 'D(A) 变了：外部 1 + 1 = 2。' };
      return { ok: true, message: `初始 cut ${r.events[0].metrics.cut}；D(A) = ${ad.Da}，D(D) = ${ad.Db}，g(A, D) = ${ad.gain}。` };
    },
    hints: ['A 的外部边权变为 1 + 1 = 2。', 'D(D) 不受影响，仍是 3。'],
    answer: '初始 cut 8；g(A, D) = 5。',
    explanation: '改一条边就要重算所有 D 值；Python 检查器也用随机图防止只记住五节点答案。'
  }
];
