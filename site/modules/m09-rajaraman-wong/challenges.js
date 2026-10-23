// Module 09 challenges: all values from engines/rw.js on the chain and the candidate DAG.
import { choice, fields, combine } from '../../assets/challenges.js';
import * as RW from '../../engines/rw.js';

const run = () => RW.run(RW.CANDIDATE_DAG);
// The best non-replicating clustering found by exhaustive search (scripts/research/rw_no_replication.py);
// its delay is re-evaluated here with the engine, so the number shown is computed, not typed.
export const NO_REPLICATION_BEST = [['a', 'd', 'f', 'h'], ['b', 'c', 'e', 'g'], ['i', 'j', 'k', 'l']];

export const challenges = [
  {
    id: 'c1', type: '概念', difficulty: 'Intro', objectiveId: 'o1', title: '目标变了',
    why: '检查你能否说出本章与前七章目标的区别。',
    task: 'Rajaraman–Wong 聚类要最小化的是什么？',
    build: () => choice([['delay', '从任一 PI 到任一 PO 的最大路径延迟'], ['cut', '跨簇连线的权重之和（cut）'], ['size', '簇的个数'], ['balance', '各簇大小之差']]),
    check: a => a === 'delay' ? { ok: true, message: '对：目标是最长路径的延迟；cut 小不保证延迟小。' }
      : { ok: false, message: a === 'cut' ? '那是 Module 02–08 的目标。本章看的是最慢的那条路径。' : '本章的目标与簇数、平衡无关。' },
    hints: ['芯片“跑多快”由哪条路径决定？', '跨簇一次，路径就多 D。'],
    answer: '最大 PI→PO 路径延迟。',
    explanation: '两种分法切断的连线数可以相同，关键路径跨界的次数却不同。'
  },
  {
    id: 'c2', type: '推演', difficulty: 'Intro', objectiveId: 'o1', title: '一条路径的延迟',
    why: '检查路径延迟 = 节点延迟之和 + D × 跨界次数。',
    task: '链 P → X → Y → O，每个节点延迟 1，跨簇 D = 3。分成 {P,X} | {Y,O} 时延迟是多少？分成 {P} | {X,Y} | {O} 时呢？',
    build: () => fields([{ key: 'one', label: '{P,X} | {Y,O}' }, { key: 'two', label: '{P} | {X,Y} | {O}' }]),
    check: a => {
      const one = RW.evaluatePartition(RW.CHAIN, [['P', 'X'], ['Y', 'O']]), two = RW.evaluatePartition(RW.CHAIN, [['P'], ['X', 'Y'], ['O']]);
      if (a.one !== one.maxDelay) return { ok: false, message: '4 个节点各 1，再加一次跨界 D。' };
      if (a.two !== two.maxDelay) return { ok: false, message: '这次 P→X 与 Y→O 两次跨界。' };
      return { ok: true, message: `一次跨界：${one.maxDelay}；两次跨界：${two.maxDelay}。` };
    },
    hints: ['先数节点延迟：4。', '每跨一次边界加 3。'],
    answer: '7 与 10。',
    explanation: '两种分法都满足容量 2，延迟差 3——只因为关键路径多跨了一次。'
  },
  {
    id: 'c3', type: '解释', difficulty: 'Practice', objectiveId: 'o3', title: '复制与实例',
    why: '检查你能否区分逻辑节点与物理实例，并读出复制的代价。',
    task: '在候选 DAG 的 RW 结果中，逻辑节点 b 有几个实例？全部实例一共多少个（逻辑节点是 12 个）？',
    build: () => fields([{ key: 'b', label: 'b 的实例数' }, { key: 'all', label: '实例总数' }]),
    check: a => {
      const r = run().result, nb = r.instances.filter(i => i.logicalId === 'b').length;
      if (a.b !== nb) return { ok: false, message: '数一数以 b 为逻辑节点的实例：b@b、b@d、b@e……' };
      if (a.all !== r.instanceCount) return { ok: false, message: '把 8 个簇的成员数加起来。' };
      return { ok: true, message: `b 有 ${nb} 个实例（${r.instances.filter(i => i.logicalId === 'b').map(i => i.instanceId).join('、')}）；共 ${r.instanceCount} 个实例，面积从 ${r.logicalCount} 变成 ${r.totalSize}。` };
    },
    hints: ['b 出现在簇 b、d、e 中。', '8 个簇的大小：4、4、3、3、2、2、1、1。'],
    answer: 'b 有 3 个实例；共 20 个实例。',
    explanation: '复制让多个簇在簇内拿到同一个信号，代价是面积。一个“节点 → 簇”的映射表示不了这种结果。'
  },
  {
    id: 'c4', type: '推演', difficulty: 'Practice', objectiveId: 'o4', title: 'i 的标签',
    why: '检查标记阶段：候选簇、l1、l2 的含义。',
    task: '容量 4、D = 3。节点 i 的祖先得分（l(x) + Δ(x,i)）为 g 4、e 4、c 4、b 4、f 3、d 3、a 3；按假设的平票规则，候选簇是 {i, g, e, c}。l1、l2 和 l(i) 各是多少？',
    build: () => fields([{ key: 'l1', label: 'l1' }, { key: 'l2', label: 'l2' }, { key: 'l', label: 'l(i)' }]),
    check: a => {
      const e = run().events.find(x => x.kind === 'label' && x.after.node === 'i');
      if (a.l1 !== e.metrics.l1) return { ok: false, message: 'l1 只看簇内的 PI：簇里哪个是 PI？' };
      if (a.l2 !== e.metrics.l2) return { ok: false, message: 'l2 = 簇外祖先的最大得分 + D。簇外最大的是 b（4）。' };
      if (a.l !== e.metrics.label) return { ok: false, message: 'l(i) = max(l1, l2)。' };
      return { ok: true, message: `l1 = ${e.metrics.l1}（簇内 PI c），l2 = 4 + 3 = ${e.metrics.l2}，l(i) = ${e.metrics.label}。` };
    },
    hints: ['簇内的 PI 只有 c。', '簇外最大得分是 b 的 4，跨界加 3。'],
    answer: 'l1 = 4，l2 = 7，l(i) = 7。',
    explanation: 'l(v) 是一个时间：在模型内信号到达 v 的最早可能时间。'
  },
  {
    id: 'c5', type: '探索', difficulty: 'Stretch', objectiveId: 'o5', title: '复制换来了多少',
    why: '检查你能否比较允许复制与禁止复制时的结果。',
    task: '候选 DAG、容量 4、D = 3。RW（允许复制）的最大延迟是多少？如果禁止复制，穷举得到的最好最大延迟是多少？',
    build: () => fields([{ key: 'rw', label: 'RW（允许复制）' }, { key: 'nr', label: '禁止复制的最好值' }]),
    check: a => {
      const r = run().result, nr = RW.evaluatePartition(RW.CANDIDATE_DAG, NO_REPLICATION_BEST);
      if (a.rw !== r.maxDelay) return { ok: false, message: '看两个 PO 的到达时间。' };
      if (a.nr !== nr.maxDelay) return { ok: false, message: '不能复制时，关键路径至少要多跨一次边界。' };
      return { ok: true, message: `允许复制：${r.maxDelay}（${r.instanceCount} 个实例）；禁止复制最好 ${nr.maxDelay}（例如 ${NO_REPLICATION_BEST.map(c => c.join('')).join(' | ')}）。` };
    },
    hints: ['RW 的输出延迟等于 l(k) = l(l)。', '不复制的最好方案之一是 adfh | bceg | ijkl。'],
    answer: '8 与 10。',
    explanation: '“10”由穷举所有容量合法的不复制分组得到（见 scripts/research/rw_no_replication.py），这里用引擎重新评估。RW 的最优性结论只在允许复制时成立。'
  },
  {
    id: 'c6', type: '解释', difficulty: 'Stretch', objectiveId: 'o6', title: '哪些说法站得住',
    why: '检查你能否区分论文结论、本课程的测试与待确认事项。',
    task: '选出所有正确的说法（可多选）。',
    build: () => choice([['rep', 'RW 的延迟最优性以“允许复制”为前提'], ['teacher', '12 节点候选 DAG 已由教师确认'], ['proof', '本课程的测试证明了 RW 最优'], ['multi', '本模块就是教师目录中的 Multilevel'], ['tie', '平票规则是本课程采用的假设']], { multi: true }),
    check: a => {
      const want = ['rep', 'tie'], got = [...a].sort();
      if (got.join() === want.join()) return { ok: true, message: '对：最优性以允许复制为前提；平票规则是假设。候选图待原作者确认，测试只检查实现一致，本模块不替代 Multilevel。' };
      const wrong = got.filter(x => !want.includes(x)), miss = want.filter(x => !got.includes(x));
      return { ok: false, message: (wrong.length ? '有说法不成立。' : '') + (miss.length ? '还漏了正确的说法。' : '') };
    },
    hints: ['哪些来自论文，哪些是本课程的假设，哪些尚未确认？', '测试能证明“实现一致”，不能证明“算法最优”。'],
    answer: '“RW 的延迟最优性以允许复制为前提”与“平票规则是本课程采用的假设”。',
    explanation: '把论文结论、实现检查、候选数据与课程映射分开说，是本模块最重要的边界意识。'
  }
];
