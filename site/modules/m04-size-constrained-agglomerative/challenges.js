// Module 04 challenges: answers come from engines/merge.js (run, exhaustive oracle, diagnose).
import { choice, fields, combine } from '../../assets/challenges.js';
import { L } from '../../assets/i18n.js';
import * as M from '../../engines/merge.js';
import { G01, cutsize, requireGraph } from '../../engines/graph.js';

const KIND = { 'infeasible-by-bound': L('下界已证明不可能', 'the lower bound proves it impossible'), 'infeasible-by-search': L('穷举也找不到恰好 K 簇的合法划分', 'exhaustive search finds no legal partition into exactly K clusters'), 'greedy-stuck': L('总体可行，但贪心卡住', 'feasible overall, but greedy gets stuck'), 'feasible-suboptimal': L('达到 K，但不是最优', 'K reached, but not optimal'), 'reached-and-optimal-here': L('达到 K，且在这张图上最优', 'K reached, and optimal on this graph') };

/** Parse "AC|BD" into groups; returns null when malformed. */
function parseGroups(s, ids) {
  const groups = s.toUpperCase().replace(/\s/g, '').split('|').filter(Boolean).map(g => g.split(''));
  const flat = groups.flat();
  if (flat.length !== ids.length || new Set(flat).size !== ids.length || flat.some(x => !ids.includes(x))) return null;
  return groups;
}

export const challenges = [
  {
    id: 'c1', type: L('概念', 'Concept'), difficulty: 'Intro', objectiveId: 'o1', title: L('合法与目标是两回事', 'Legal and on target are two different things'),
    why: L('检查你能否把“满足容量”和“达到 K”分开判断。', 'Checks that you judge “within capacity” and “K reached” separately.'),
    task: L('G01、容量 2、K = 2，贪心结果是 AB | C | DE。分别判断：它满足容量吗？它达到 K 了吗？', 'G01, capacity 2, K = 2: greedy gives AB | C | DE. Judge each: is it within capacity? Is K reached?'),
    build: () => combine(choice([['cy', L('满足容量', 'Within capacity')], ['cn', L('违反容量', 'Over capacity')]]), choice([['ty', L('达到了 K', 'K is reached')], ['tn', L('没有达到 K', 'K is not reached')]])),
    check: ([c, t]) => {
      const r = M.run(G01, { k: 2, capacity: 2 }).result;
      if ((c === 'cy') !== r.capacityCompliant) return { ok: false, message: L('逐个看簇的大小：AB = 2、C = 1、DE = 2，都不超过 2。', 'Look at each cluster’s size: AB = 2, C = 1, DE = 2; none is above 2.') };
      if ((t === 'ty') !== r.targetReached) return { ok: false, message: L('实际有 3 个簇，K = 2。', 'There are 3 clusters, and K = 2.') };
      return { ok: true, message: L(`capacityCompliant = ${r.capacityCompliant}，targetReached = ${r.targetReached}，停止原因 ${r.stopReason}。`, `capacityCompliant = ${r.capacityCompliant}, targetReached = ${r.targetReached}, stop reason ${r.stopReason}.`) };
    },
    hints: [L('满足容量只看每个簇的大小。', 'Within capacity looks only at each cluster’s size.'), L('达到 K 只看簇的个数。', 'K reached looks only at the number of clusters.')],
    answer: L('满足容量；没有达到 K。', 'Within capacity; K not reached.'),
    explanation: L('两个判断互相独立。同一个 AB | C | DE 在 K = 3 时就既合法又达到目标。', 'The two judgements are independent. The same AB | C | DE with K = 3 is both legal and on target.')
  },
  {
    id: 'c2', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o2', title: L('被挡住时选谁', 'Whom to pick when blocked'),
    why: L('检查“先筛合法、再选最大”的顺序。', 'Checks the order: filter for legality first, then take the largest.'),
    task: L('容量 2。A、B 已合并为 AB，候选有 AB–C（5，合并后大小 3）、D–E（5，大小 2）、C–D（2，大小 2）、C–E（1，大小 2）。下一步合并哪一对？', 'Capacity 2. A and B have merged into AB; the candidates are AB–C (5, merged size 3), D–E (5, size 2), C–D (2, size 2), C–E (1, size 2). Which pair merges next?'),
    build: () => choice([['ABC', 'AB–C'], ['DE', 'D–E'], ['CD', 'C–D'], ['stop', L('直接停止', 'Stop now')]]),
    check: a => {
      const ev = M.run(G01, { k: 2, capacity: 2 }).events.filter(e => e.kind === 'merge')[1];
      const want = ev.decision.a + ev.decision.b;
      if (a === want) return { ok: true, message: L('AB–C 超容量被排除；剩下合法候选中 D–E 最大。', 'AB–C is over capacity and drops out; among the legal candidates left, D–E is largest.') };
      if (a === 'ABC') return { ok: false, message: L('AB–C 亲和度最大，但大小 3 > 2，不合法。', 'AB–C has the highest affinity, but size 3 > 2: not legal.') };
      if (a === 'stop') return { ok: false, message: L('还有合法的正亲和度对，不该停。', 'Legal positive pairs remain, so do not stop.') };
      return { ok: false, message: L('C–D 合法，但 D–E 也合法且亲和度更大。', 'C–D is legal, but so is D–E, with a higher affinity.') };
    },
    hints: [L('先把超过容量的候选划掉。', 'Cross out the candidates over capacity first.'), L('剩下的 D–E（5）、C–D（2）、C–E（1）中选最大。', 'Take the largest of D–E (5), C–D (2), C–E (1).')],
    answer: L('D–E。', 'D–E.'),
    explanation: L('合法性筛选发生在比较亲和度之前。', 'The legality filter happens before affinities are compared.')
  },
  {
    id: 'c3', type: L('约束', 'Constraint'), difficulty: 'Practice', objectiveId: 'o3', title: L('至少要几个簇', 'At least how many clusters'),
    why: L('检查你能否用下界证明目标不可行。', 'Checks that you can use the lower bound to prove a target infeasible.'),
    task: L('G01 五个节点大小都是 1，容量 C = 2。任何合法分组至少有几个簇？K = 2 可能吗？', 'G01’s five nodes all have size 1, capacity C = 2. At least how many clusters does any legal grouping have? Is K = 2 possible?'),
    build: () => combine(fields([{ key: 'lb', label: L('最少簇数', 'Fewest clusters') }]), choice([['yes', L('K = 2 可能', 'K = 2 is possible')], ['no', L('K = 2 不可能', 'K = 2 is impossible')]])),
    check: ([f, p]) => {
      const ex = M.exhaustive(G01, { k: 2, capacity: 2 });
      if (f.lb !== ex.lowerBoundClusters) return { ok: false, message: L('总大小 5，每簇最多 2：向上取整。', 'Total size 5, at most 2 per cluster: round up.') };
      if ((p === 'yes') !== ex.feasibleAtK) return { ok: false, message: L(`下界 ${ex.lowerBoundClusters} > 2，任何算法都做不到。`, `The lower bound ${ex.lowerBoundClusters} > 2: no algorithm can do it.`) };
      return { ok: true, message: L(`⌈5/2⌉ = ${ex.lowerBoundClusters}；穷举确认最少 ${ex.minFeasibleClusters} 簇，K = 2 不可能。`, `⌈5/2⌉ = ${ex.lowerBoundClusters}; exhaustive search confirms at least ${ex.minFeasibleClusters} clusters, so K = 2 is impossible.`) };
    },
    hints: [L('把 5 个单位装进容量 2 的盒子。', 'Pack 5 units into boxes of capacity 2.'), '⌈5 / 2⌉ = ?'],
    answer: L('至少 3 个簇；K = 2 不可能。', 'At least 3 clusters; K = 2 is impossible.'),
    explanation: L('这时贪心停在 3 簇不是算法的错，而是目标本身不可行。', 'Greedy stopping at 3 clusters here is not the algorithm’s fault: the target itself is infeasible.')
  },
  {
    id: 'c4', type: L('探索', 'Explore'), difficulty: 'Practice', objectiveId: 'o4', title: L('卡住还是不可能', 'Stuck, or impossible?'),
    why: L('检查你能否区分“贪心走进死胡同”与“理论上不可能”，并给出证据。', 'Checks that you can tell “greedy walked into a dead end” from “impossible in principle”, with evidence.'),
    task: L('greedy_trap：A、B 大小 2，C、D 大小 1；C–D = 10，A–C = 4，B–D = 4；容量 3，K = 2。贪心停在 3 簇。这属于哪一类？再写出一个合法的 2 簇分组（如 AC|BD 的格式）。', 'greedy_trap: A and B have size 2, C and D size 1; C–D = 10, A–C = 4, B–D = 4; capacity 3, K = 2. Greedy stops at 3 clusters. Which case is this? Then write a legal 2-cluster grouping (in a form like AC|BD).'),
    build: () => combine(choice([['infeasible-by-bound', L('下界已证明不可能', 'The lower bound proves it impossible')], ['greedy-stuck', L('总体可行，但贪心卡住', 'Feasible overall, but greedy gets stuck')], ['feasible-suboptimal', L('达到 K 但非最优', 'K reached, but not optimal')]]), fields([{ key: 'g', label: L('合法的 2 簇分组', 'A legal 2-cluster grouping'), type: 'text', placeholder: L('例如 AB|CD', 'e.g. AB|CD') }])),
    check: ([kind, f]) => {
      const g = M.M04_GRAPHS.greedy_trap, d = M.diagnose(g, { k: 2, capacity: 3 });
      if (kind !== d.kind) return { ok: false, message: kind === 'infeasible-by-bound' ? L('下界是 ⌈6/3⌉ = 2，并没有排除 K = 2。', 'The lower bound is ⌈6/3⌉ = 2; it does not rule out K = 2.') : L('贪心根本没有达到 K。', 'Greedy did not reach K at all.') };
      const size = { A: 2, B: 2, C: 1, D: 1 };
      const groups = parseGroups(f.g, ['A', 'B', 'C', 'D']);
      if (!groups) return { ok: false, message: L('分组格式不对：用 | 分开两组，每个节点恰好出现一次。', 'The grouping is malformed: separate the two groups with |, and use every node exactly once.') };
      if (groups.length !== 2) return { ok: false, message: L('需要恰好 2 个簇。', 'It needs exactly 2 clusters.') };
      const over = groups.find(gr => gr.reduce((s, x) => s + size[x], 0) > 3);
      if (over) return { ok: false, message: L(`${over.join('')} 的大小超过 3。`, `${over.join('')} is larger than 3.`) };
      const a = {}; groups.forEach((gr, i) => gr.forEach(x => { a[x] = i; }));
      return { ok: true, message: L(`正确：${KIND[d.kind]}。${groups.map(x => x.join('')).join(' | ')} 合法，cut ${cutsize(requireGraph(g), a)}。`, `Right: ${KIND[d.kind]}. ${groups.map(x => x.join('')).join(' | ')} is legal, cut ${cutsize(requireGraph(g), a)}.`) };
    },
    hints: [L('先算下界：总大小 6，容量 3。', 'Work out the lower bound first: total size 6, capacity 3.'), L('A、B 都是 2，只能各带一个大小 1 的节点。', 'A and B are both 2, so each can take only one node of size 1.')],
    answer: L('总体可行，但贪心卡住；例如 AC | BD（cut 10）。', 'Feasible overall, but greedy gets stuck; for example AC | BD (cut 10).'),
    explanation: L('贪心第一步拿走 C–D（10），之后 A、B 都放不进 CD。穷举找到 AC | BD：两簇大小都是 3。停下只说明这条路走不通，不说明问题无解。', 'Greedy’s first step takes C–D (10), and then neither A nor B fits into CD. Exhaustive search finds AC | BD: both clusters have size 3. Stopping only shows that this path is blocked, not that the problem has no solution.')
  },
  {
    id: 'c5', type: L('探索', 'Explore'), difficulty: 'Stretch', objectiveId: 'o5', title: L('合法但差多少', 'Legal, but how much worse'),
    why: L('检查你能否量化“合法但非最优”。', 'Checks that you can put a number on “legal but not optimal”.'),
    task: L('suboptimal：A–B = 10、A–C = 9、B–D = 9、C–D = 1，大小都是 1，容量 2，K = 2。贪心的 cut 是多少？最优的合法 cut 是多少？', 'suboptimal: A–B = 10, A–C = 9, B–D = 9, C–D = 1, every size 1, capacity 2, K = 2. What cut does greedy reach? What is the best legal cut?'),
    build: () => fields([{ key: 'greedy', label: L('贪心 cut', 'Greedy cut') }, { key: 'best', label: L('最优 cut', 'Best cut') }]),
    check: f => {
      const d = M.diagnose(M.M04_GRAPHS.suboptimal, { k: 2, capacity: 2 });
      if (f.greedy !== d.run.result.cut) return { ok: false, message: L('贪心先合并 A–B（10），再合并 C–D：哪些边被切断？', 'Greedy merges A–B (10) first, then C–D: which wires are cut?') };
      if (f.best !== d.oracle.bestCutAtK.cut) return { ok: false, message: L('试试 AC | BD：被切断的是哪两条边？', 'Try AC | BD: which two wires are cut?') };
      return { ok: true, message: L(`贪心 ${d.run.result.labels.join(' | ')}，cut ${d.run.result.cut}；最优 ${d.oracle.bestCutAtK.clusters.map(c => c.join('')).join(' | ')}，cut ${d.oracle.bestCutAtK.cut}。`, `Greedy ${d.run.result.labels.join(' | ')}, cut ${d.run.result.cut}; best ${d.oracle.bestCutAtK.clusters.map(c => c.join('')).join(' | ')}, cut ${d.oracle.bestCutAtK.cut}.`) };
    },
    hints: [L('AB | CD 切断 A–C 与 B–D。', 'AB | CD cuts A–C and B–D.'), L('AC | BD 切断 A–B 与 C–D。', 'AC | BD cuts A–B and C–D.')],
    answer: L('贪心 18；最优 11。', 'Greedy 18; best 11.'),
    explanation: L('贪心先拿了眼前最大的 10，把两条 9 都留在了 cut 里。两个结果都合法、都达到 K，只是质量不同。', 'Greedy took the largest 10 in sight and left both 9s in the cut. Both results are legal and reach K; they differ only in quality.')
  },
  {
    id: 'c6', type: L('应用', 'Apply'), difficulty: 'Stretch', objectiveId: 'o5', title: L('面积不同，结局不同', 'Different areas, different endings'),
    why: L('检查你是否把“大小之和”而不是“节点个数”当作容量依据。', 'Checks that capacity counts the sum of sizes, not the number of nodes.'),
    task: L('把 G01 中 A 的大小改成 2（其他仍为 1），容量 3，K = 2。贪心得到什么分组？cut 是多少？', 'Change A’s size in G01 to 2 (the rest stay 1), capacity 3, K = 2. What grouping does greedy reach, and what is the cut?'),
    build: () => fields([{ key: 'g', label: L('分组', 'Grouping'), type: 'text', placeholder: L('例如 ABC|DE', 'e.g. ABC|DE') }, { key: 'cut', label: 'cut' }]),
    check: f => {
      const g = { nodes: G01.nodes.map(n => ({ id: n.id, size: n.id === 'A' ? 2 : 1 })), edges: G01.edges };
      const r = M.run(g, { k: 2, capacity: 3 }).result;
      const groups = parseGroups(f.g, ['A', 'B', 'C', 'D', 'E']);
      if (!groups) return { ok: false, message: L('分组格式不对：用 | 分开，每个节点恰好出现一次。', 'The grouping is malformed: separate groups with |, and use every node exactly once.') };
      const got = groups.map(x => x.sort().join('')).sort().join('|'), want = r.clusters.map(c => c.join('')).sort().join('|');
      if (got !== want) return { ok: false, message: got === 'ABC|DE' ? L('AB 的大小已经是 3：再加入 C 就是 4 > 3。', 'AB already has size 3: adding C makes 4 > 3.') : L('一步步来：A–B 之后，AB+C 的大小是多少？', 'Step by step: after A–B, what is the size of AB+C?') };
      if (f.cut !== r.cut) return { ok: false, message: L('数一数 AB 与 CDE 之间的边。', 'Count the wires between AB and CDE.') };
      return { ok: true, message: L(`${r.labels.join(' | ')}，cut ${r.cut}（原来是 ABC | DE、cut 3）。`, `${r.labels.join(' | ')}, cut ${r.cut} (it was ABC | DE, cut 3).`) };
    },
    hints: [L('A–B 合并后大小 2 + 1 = 3，已经满了。', 'After A–B merges, the size is 2 + 1 = 3: full.'), L('之后 D–E 合并，再把 C 放进 DE（大小 3）。', 'Then D–E merges, and C goes into DE (size 3).')],
    answer: L('AB | CDE，cut 5。', 'AB | CDE, cut 5.'),
    explanation: L('容量按大小之和计算。面积不同的单元会改变哪些合并合法，从而改变最终分组。', 'Capacity counts the sum of sizes. Cells of different areas change which merges are legal, and so the final grouping.')
  }
];
