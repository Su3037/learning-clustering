// Module 09 challenges: all values from engines/rw.js on the chain and the candidate DAG.
import { choice, fields, combine } from '../../assets/challenges.js';
import { L } from '../../assets/i18n.js';
import * as RW from '../../engines/rw.js';

const run = () => RW.run(RW.CANDIDATE_DAG);
const list = xs => xs.join(L('、', ', '));
// The best non-replicating clustering found by exhaustive search (scripts/research/rw_no_replication.py);
// its delay is re-evaluated here with the engine, so the number shown is computed, not typed.
export const NO_REPLICATION_BEST = [['a', 'd', 'f', 'h'], ['b', 'c', 'e', 'g'], ['i', 'j', 'k', 'l']];

export const challenges = [
  {
    id: 'c1', type: L('概念', 'Concept'), difficulty: 'Intro', objectiveId: 'o1', title: L('目标变了', 'The goal has changed'),
    why: L('检查你能否说出本章与前七章目标的区别。', 'Checks that you can say how this chapter’s goal differs from the previous seven.'),
    task: L('Rajaraman–Wong 聚类要最小化的是什么？', 'What does Rajaraman–Wong clustering minimise?'),
    build: () => choice([['delay', L('从任一 PI 到任一 PO 的最大路径延迟', 'The largest path delay from any PI to any PO')], ['cut', L('跨簇连线的权重之和（cut）', 'The total weight of the wires between clusters (the cut)')], ['size', L('簇的个数', 'The number of clusters')], ['balance', L('各簇大小之差', 'The difference between cluster sizes')]]),
    check: a => a === 'delay' ? { ok: true, message: L('对：目标是最长路径的延迟；cut 小不保证延迟小。', 'Right: the goal is the delay of the longest path; a small cut does not guarantee a small delay.') }
      : { ok: false, message: a === 'cut' ? L('那是 Module 02–08 的目标。本章看的是最慢的那条路径。', 'That was the goal of Modules 02–08. This chapter looks at the slowest path.') : L('本章的目标与簇数、平衡无关。', 'This chapter’s goal has nothing to do with the number of clusters or balance.') },
    hints: [L('芯片“跑多快”由哪条路径决定？', 'Which path decides how fast a chip can run?'), L('跨簇一次，路径就多 D。', 'Each crossing between clusters adds D to the path.')],
    answer: L('最大 PI→PO 路径延迟。', 'The largest PI→PO path delay.'),
    explanation: L('两种分法切断的连线数可以相同，关键路径跨界的次数却不同。', 'Two groupings can cut the same number of wires while their critical paths cross a boundary a different number of times.')
  },
  {
    id: 'c2', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o1', title: L('一条路径的延迟', 'The delay of one path'),
    why: L('检查路径延迟 = 节点延迟之和 + D × 跨界次数。', 'Checks that path delay = the sum of node delays + D × the number of crossings.'),
    task: L('链 P → X → Y → O，每个节点延迟 1，跨簇 D = 3。分成 {P,X} | {Y,O} 时延迟是多少？分成 {P} | {X,Y} | {O} 时呢？', 'Chain P → X → Y → O, each node delay 1, inter-cluster D = 3. What is the delay for {P,X} | {Y,O}? And for {P} | {X,Y} | {O}?'),
    build: () => fields([{ key: 'one', label: '{P,X} | {Y,O}' }, { key: 'two', label: '{P} | {X,Y} | {O}' }]),
    check: a => {
      const one = RW.evaluatePartition(RW.CHAIN, [['P', 'X'], ['Y', 'O']]), two = RW.evaluatePartition(RW.CHAIN, [['P'], ['X', 'Y'], ['O']]);
      if (a.one !== one.maxDelay) return { ok: false, message: L('4 个节点各 1，再加一次跨界 D。', 'Four nodes at 1 each, plus one crossing D.') };
      if (a.two !== two.maxDelay) return { ok: false, message: L('这次 P→X 与 Y→O 两次跨界。', 'This time P→X and Y→O both cross.') };
      return { ok: true, message: L(`一次跨界：${one.maxDelay}；两次跨界：${two.maxDelay}。`, `One crossing: ${one.maxDelay}; two crossings: ${two.maxDelay}.`) };
    },
    hints: [L('先数节点延迟：4。', 'Count the node delays first: 4.'), L('每跨一次边界加 3。', 'Each crossing adds 3.')],
    answer: L('7 与 10。', '7 and 10.'),
    explanation: L('两种分法都满足容量 2，延迟差 3——只因为关键路径多跨了一次。', 'Both groupings respect capacity 2, yet the delays differ by 3, only because the critical path crosses one more time.')
  },
  {
    id: 'c3', type: L('解释', 'Explain'), difficulty: 'Practice', objectiveId: 'o3', title: L('复制与实例', 'Replication and instances'),
    why: L('检查你能否区分逻辑节点与物理实例，并读出复制的代价。', 'Checks that you can tell logic nodes from physical instances, and read off the cost of replication.'),
    task: L('在候选 DAG 的 RW 结果中，逻辑节点 b 有几个实例？全部实例一共多少个（逻辑节点是 12 个）？', 'In the RW result on the candidate DAG, how many instances does logic node b have? How many instances are there in all (there are 12 logic nodes)?'),
    build: () => fields([{ key: 'b', label: L('b 的实例数', 'Instances of b') }, { key: 'all', label: L('实例总数', 'Total instances') }]),
    check: a => {
      const r = run().result, ib = r.instances.filter(i => i.logicalId === 'b');
      if (a.b !== ib.length) return { ok: false, message: L('数一数以 b 为逻辑节点的实例：b@b、b@d、b@e……', 'Count the instances whose logic node is b: b@b, b@d, b@e…') };
      if (a.all !== r.instanceCount) return { ok: false, message: L('把 8 个簇的成员数加起来。', 'Add up the members of the 8 clusters.') };
      return { ok: true, message: L(`b 有 ${ib.length} 个实例（${list(ib.map(i => i.instanceId))}）；共 ${r.instanceCount} 个实例，面积从 ${r.logicalCount} 变成 ${r.totalSize}。`, `b has ${ib.length} instances (${list(ib.map(i => i.instanceId))}); ${r.instanceCount} instances in all, so the area goes from ${r.logicalCount} to ${r.totalSize}.`) };
    },
    hints: [L('b 出现在簇 b、d、e 中。', 'b appears in clusters b, d and e.'), L('8 个簇的大小：4、4、3、3、2、2、1、1。', 'The 8 cluster sizes: 4, 4, 3, 3, 2, 2, 1, 1.')],
    answer: L('b 有 3 个实例；共 20 个实例。', 'b has 3 instances; 20 instances in all.'),
    explanation: L('复制让多个簇在簇内拿到同一个信号，代价是面积。一个“节点 → 簇”的映射表示不了这种结果。', 'Replication lets several clusters get the same signal inside themselves, at the cost of area. A “node → cluster” map cannot represent such a result.')
  },
  {
    id: 'c4', type: L('推演', 'Trace'), difficulty: 'Practice', objectiveId: 'o4', title: L('i 的标签', 'The label of i'),
    why: L('检查标记阶段：候选簇、l1、l2 的含义。', 'Checks the labelling phase: what the candidate cluster, l1 and l2 mean.'),
    task: L('容量 4、D = 3。节点 i 的祖先得分（l(x) + Δ(x,i)）为 g 4、e 4、c 4、b 4、f 3、d 3、a 3；按假设的平票规则，候选簇是 {i, g, e, c}。l1、l2 和 l(i) 各是多少？', 'Capacity 4, D = 3. The scores of i’s ancestors (l(x) + Δ(x,i)) are g 4, e 4, c 4, b 4, f 3, d 3, a 3; under the assumed tie rule the candidate cluster is {i, g, e, c}. What are l1, l2 and l(i)?'),
    build: () => fields([{ key: 'l1', label: 'l1' }, { key: 'l2', label: 'l2' }, { key: 'l', label: 'l(i)' }]),
    check: a => {
      const e = run().events.find(x => x.kind === 'label' && x.after.node === 'i');
      if (a.l1 !== e.metrics.l1) return { ok: false, message: L('l1 只看簇内的 PI：簇里哪个是 PI？', 'l1 looks only at the PIs inside the cluster: which one is a PI?') };
      if (a.l2 !== e.metrics.l2) return { ok: false, message: L('l2 = 簇外祖先的最大得分 + D。簇外最大的是 b（4）。', 'l2 = the largest score outside the cluster + D. The largest outside is b (4).') };
      if (a.l !== e.metrics.label) return { ok: false, message: L('l(i) = max(l1, l2)。', 'l(i) = max(l1, l2).') };
      return { ok: true, message: L(`l1 = ${e.metrics.l1}（簇内 PI c），l2 = 4 + 3 = ${e.metrics.l2}，l(i) = ${e.metrics.label}。`, `l1 = ${e.metrics.l1} (the PI c inside), l2 = 4 + 3 = ${e.metrics.l2}, l(i) = ${e.metrics.label}.`) };
    },
    hints: [L('簇内的 PI 只有 c。', 'The only PI inside the cluster is c.'), L('簇外最大得分是 b 的 4，跨界加 3。', 'The largest score outside is b’s 4; crossing adds 3.')],
    answer: L('l1 = 4，l2 = 7，l(i) = 7。', 'l1 = 4, l2 = 7, l(i) = 7.'),
    explanation: L('l(v) 是一个时间：在模型内信号到达 v 的最早可能时间。', 'l(v) is a time: the earliest the signal can reach v within the model.')
  },
  {
    id: 'c5', type: L('探索', 'Explore'), difficulty: 'Stretch', objectiveId: 'o5', title: L('复制换来了多少', 'What replication buys'),
    why: L('检查你能否比较允许复制与禁止复制时的结果。', 'Checks that you can compare the results with and without replication.'),
    task: L('候选 DAG、容量 4、D = 3。RW（允许复制）的最大延迟是多少？如果禁止复制，穷举得到的最好最大延迟是多少？', 'Candidate DAG, capacity 4, D = 3. What is RW’s largest delay (replication allowed)? Without replication, what is the best largest delay found by exhaustive search?'),
    build: () => fields([{ key: 'rw', label: L('RW（允许复制）', 'RW (replication allowed)') }, { key: 'nr', label: L('禁止复制的最好值', 'Best without replication') }]),
    check: a => {
      const r = run().result, nr = RW.evaluatePartition(RW.CANDIDATE_DAG, NO_REPLICATION_BEST);
      if (a.rw !== r.maxDelay) return { ok: false, message: L('看两个 PO 的到达时间。', 'Look at the arrival times of the two POs.') };
      if (a.nr !== nr.maxDelay) return { ok: false, message: L('不能复制时，关键路径至少要多跨一次边界。', 'Without replication the critical path must cross at least once more.') };
      return { ok: true, message: L(`允许复制：${r.maxDelay}（${r.instanceCount} 个实例）；禁止复制最好 ${nr.maxDelay}（例如 ${NO_REPLICATION_BEST.map(c => c.join('')).join(' | ')}）。`, `With replication: ${r.maxDelay} (${r.instanceCount} instances); the best without is ${nr.maxDelay} (for example ${NO_REPLICATION_BEST.map(c => c.join('')).join(' | ')}).`) };
    },
    hints: [L('RW 的输出延迟等于 l(k) = l(l)。', 'RW’s output delay equals l(k) = l(l).'), L('不复制的最好方案之一是 adfh | bceg | ijkl。', 'One of the best groupings without replication is adfh | bceg | ijkl.')],
    answer: L('8 与 10。', '8 and 10.'),
    explanation: L('“10”由穷举所有容量合法的不复制分组得到（见 scripts/research/rw_no_replication.py），这里用引擎重新评估。RW 的最优性结论只在允许复制时成立。', 'The 10 comes from exhaustively searching every capacity-legal grouping without replication (see scripts/research/rw_no_replication.py) and is re-evaluated here with the engine. RW’s optimality result holds only when replication is allowed.')
  },
  {
    id: 'c6', type: L('解释', 'Explain'), difficulty: 'Stretch', objectiveId: 'o6', title: L('哪些说法站得住', 'Which claims hold up'),
    why: L('检查你能否区分论文结论、本课程的测试与待确认事项。', 'Checks that you can tell the paper’s results, this course’s tests and the open questions apart.'),
    task: L('选出所有正确的说法（可多选）。', 'Choose every correct statement (more than one may be right).'),
    build: () => choice([['rep', L('RW 的延迟最优性以“允许复制”为前提', 'RW’s delay optimality assumes replication is allowed')], ['teacher', L('12 节点候选 DAG 已由教师确认', 'The 12-node candidate DAG has been confirmed by the teacher')], ['proof', L('本课程的测试证明了 RW 最优', 'This course’s tests prove that RW is optimal')], ['multi', L('本模块就是教师目录中的 Multilevel', 'This module is the Multilevel lab in the teacher’s catalogue')], ['tie', L('平票规则是本课程采用的假设', 'The tie rule is an assumption this course makes')]], { multi: true }),
    check: a => {
      const want = ['rep', 'tie'], got = [...a].sort();
      if (got.join() === want.join()) return { ok: true, message: L('对：最优性以允许复制为前提；平票规则是假设。候选图待原作者确认，测试只检查实现一致，本模块不替代 Multilevel。', 'Right: optimality assumes replication, and the tie rule is an assumption. The candidate graph awaits the original author’s confirmation, the tests only check the implementation is consistent, and this module does not replace Multilevel.') };
      const wrong = got.filter(x => !want.includes(x)), miss = want.filter(x => !got.includes(x));
      return { ok: false, message: (wrong.length ? L('有说法不成立。', 'One of your choices does not hold. ') : '') + (miss.length ? L('还漏了正确的说法。', 'A correct statement is missing.') : '') };
    },
    hints: [L('哪些来自论文，哪些是本课程的假设，哪些尚未确认？', 'Which come from the paper, which are this course’s assumptions, and which are unconfirmed?'), L('测试能证明“实现一致”，不能证明“算法最优”。', 'Tests can show the implementation is consistent; they cannot prove the algorithm optimal.')],
    answer: L('“RW 的延迟最优性以允许复制为前提”与“平票规则是本课程采用的假设”。', '“RW’s delay optimality assumes replication is allowed” and “The tie rule is an assumption this course makes”.'),
    explanation: L('把论文结论、实现检查、候选数据与课程映射分开说，是本模块最重要的边界意识。', 'Keeping the paper’s results, the implementation checks, the candidate data and the course mapping apart is the most important sense of limits in this module.')
  }
];
