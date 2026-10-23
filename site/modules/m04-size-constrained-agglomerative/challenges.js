// Module 04 challenges: answers come from engines/merge.js (run, exhaustive oracle, diagnose).
import { choice, fields, combine } from '../../assets/challenges.js';
import * as M from '../../engines/merge.js';
import { G01, cutsize, requireGraph } from '../../engines/graph.js';

const KIND = { 'infeasible-by-bound': '下界已证明不可能', 'infeasible-by-search': '穷举也找不到恰好 K 簇的合法划分', 'greedy-stuck': '总体可行，但贪心卡住', 'feasible-suboptimal': '达到 K，但不是最优', 'reached-and-optimal-here': '达到 K，且在这张图上最优' };

/** Parse "AC|BD" into groups; returns null when malformed. */
function parseGroups(s, ids) {
  const groups = s.toUpperCase().replace(/\s/g, '').split('|').filter(Boolean).map(g => g.split(''));
  const flat = groups.flat();
  if (flat.length !== ids.length || new Set(flat).size !== ids.length || flat.some(x => !ids.includes(x))) return null;
  return groups;
}

export const challenges = [
  {
    id: 'c1', type: '概念', difficulty: 'Intro', objectiveId: 'o1', title: '合法与目标是两回事',
    why: '检查你能否把“满足容量”和“达到 K”分开判断。',
    task: 'G01、容量 2、K = 2，贪心结果是 AB | C | DE。分别判断：它满足容量吗？它达到 K 了吗？',
    build: () => combine(choice([['cy', '满足容量'], ['cn', '违反容量']]), choice([['ty', '达到了 K'], ['tn', '没有达到 K']])),
    check: ([c, t]) => {
      const r = M.run(G01, { k: 2, capacity: 2 }).result;
      if ((c === 'cy') !== r.capacityCompliant) return { ok: false, message: '逐个看簇的大小：AB = 2、C = 1、DE = 2，都不超过 2。' };
      if ((t === 'ty') !== r.targetReached) return { ok: false, message: '实际有 3 个簇，K = 2。' };
      return { ok: true, message: `capacityCompliant = ${r.capacityCompliant}，targetReached = ${r.targetReached}，停止原因 ${r.stopReason}。` };
    },
    hints: ['满足容量只看每个簇的大小。', '达到 K 只看簇的个数。'],
    answer: '满足容量；没有达到 K。',
    explanation: '两个判断互相独立。同一个 AB | C | DE 在 K = 3 时就既合法又达到目标。'
  },
  {
    id: 'c2', type: '推演', difficulty: 'Intro', objectiveId: 'o2', title: '被挡住时选谁',
    why: '检查“先筛合法、再选最大”的顺序。',
    task: '容量 2。A、B 已合并为 AB，候选有 AB–C（5，合并后大小 3）、D–E（5，大小 2）、C–D（2，大小 2）、C–E（1，大小 2）。下一步合并哪一对？',
    build: () => choice([['ABC', 'AB–C'], ['DE', 'D–E'], ['CD', 'C–D'], ['stop', '直接停止']]),
    check: a => {
      const ev = M.run(G01, { k: 2, capacity: 2 }).events.filter(e => e.kind === 'merge')[1];
      const want = ev.decision.a + ev.decision.b;
      if (a === want) return { ok: true, message: 'AB–C 超容量被排除；剩下合法候选中 D–E 最大。' };
      if (a === 'ABC') return { ok: false, message: 'AB–C 亲和度最大，但大小 3 > 2，不合法。' };
      if (a === 'stop') return { ok: false, message: '还有合法的正亲和度对，不该停。' };
      return { ok: false, message: 'C–D 合法，但 D–E 也合法且亲和度更大。' };
    },
    hints: ['先把超过容量的候选划掉。', '剩下的 D–E（5）、C–D（2）、C–E（1）中选最大。'],
    answer: 'D–E。',
    explanation: '合法性筛选发生在比较亲和度之前。'
  },
  {
    id: 'c3', type: '约束', difficulty: 'Practice', objectiveId: 'o3', title: '至少要几个簇',
    why: '检查你能否用下界证明目标不可行。',
    task: 'G01 五个节点大小都是 1，容量 C = 2。任何合法分组至少有几个簇？K = 2 可能吗？',
    build: () => combine(fields([{ key: 'lb', label: '最少簇数' }]), choice([['yes', 'K = 2 可能'], ['no', 'K = 2 不可能']])),
    check: ([f, p]) => {
      const ex = M.exhaustive(G01, { k: 2, capacity: 2 });
      if (f.lb !== ex.lowerBoundClusters) return { ok: false, message: '总大小 5，每簇最多 2：向上取整。' };
      if ((p === 'yes') !== ex.feasibleAtK) return { ok: false, message: `下界 ${ex.lowerBoundClusters} > 2，任何算法都做不到。` };
      return { ok: true, message: `⌈5/2⌉ = ${ex.lowerBoundClusters}；穷举确认最少 ${ex.minFeasibleClusters} 簇，K = 2 不可能。` };
    },
    hints: ['把 5 个单位装进容量 2 的盒子。', '⌈5 / 2⌉ = ?'],
    answer: '至少 3 个簇；K = 2 不可能。',
    explanation: '这时贪心停在 3 簇不是算法的错，而是目标本身不可行。'
  },
  {
    id: 'c4', type: '探索', difficulty: 'Practice', objectiveId: 'o4', title: '卡住还是不可能',
    why: '检查你能否区分“贪心走进死胡同”与“理论上不可能”，并给出证据。',
    task: 'greedy_trap：A、B 大小 2，C、D 大小 1；C–D = 10，A–C = 4，B–D = 4；容量 3，K = 2。贪心停在 3 簇。这属于哪一类？再写出一个合法的 2 簇分组（如 AC|BD 的格式）。',
    build: () => combine(choice([['infeasible-by-bound', '下界已证明不可能'], ['greedy-stuck', '总体可行，但贪心卡住'], ['feasible-suboptimal', '达到 K 但非最优']]), fields([{ key: 'g', label: '合法的 2 簇分组', type: 'text', placeholder: '例如 AB|CD' }])),
    check: ([kind, f]) => {
      const g = M.M04_GRAPHS.greedy_trap, d = M.diagnose(g, { k: 2, capacity: 3 });
      if (kind !== d.kind) return { ok: false, message: kind === 'infeasible-by-bound' ? '下界是 ⌈6/3⌉ = 2，并没有排除 K = 2。' : '贪心根本没有达到 K。' };
      const size = { A: 2, B: 2, C: 1, D: 1 };
      const groups = parseGroups(f.g, ['A', 'B', 'C', 'D']);
      if (!groups) return { ok: false, message: '分组格式不对：用 | 分开两组，每个节点恰好出现一次。' };
      if (groups.length !== 2) return { ok: false, message: '需要恰好 2 个簇。' };
      const over = groups.find(gr => gr.reduce((s, x) => s + size[x], 0) > 3);
      if (over) return { ok: false, message: `${over.join('')} 的大小超过 3。` };
      const a = {}; groups.forEach((gr, i) => gr.forEach(x => { a[x] = i; }));
      return { ok: true, message: `正确：${KIND[d.kind]}。${groups.map(x => x.join('')).join(' | ')} 合法，cut ${cutsize(requireGraph(g), a)}。` };
    },
    hints: ['先算下界：总大小 6，容量 3。', 'A、B 都是 2，只能各带一个大小 1 的节点。'],
    answer: '总体可行，但贪心卡住；例如 AC | BD（cut 10）。',
    explanation: '贪心第一步拿走 C–D（10），之后 A、B 都放不进 CD。穷举找到 AC | BD：两簇大小都是 3。停下只说明这条路走不通，不说明问题无解。'
  },
  {
    id: 'c5', type: '探索', difficulty: 'Stretch', objectiveId: 'o5', title: '合法但差多少',
    why: '检查你能否量化“合法但非最优”。',
    task: 'suboptimal：A–B = 10、A–C = 9、B–D = 9、C–D = 1，大小都是 1，容量 2，K = 2。贪心的 cut 是多少？最优的合法 cut 是多少？',
    build: () => fields([{ key: 'greedy', label: '贪心 cut' }, { key: 'best', label: '最优 cut' }]),
    check: f => {
      const d = M.diagnose(M.M04_GRAPHS.suboptimal, { k: 2, capacity: 2 });
      if (f.greedy !== d.run.result.cut) return { ok: false, message: '贪心先合并 A–B（10），再合并 C–D：哪些边被切断？' };
      if (f.best !== d.oracle.bestCutAtK.cut) return { ok: false, message: '试试 AC | BD：被切断的是哪两条边？' };
      return { ok: true, message: `贪心 ${d.run.result.labels.join(' | ')}，cut ${d.run.result.cut}；最优 ${d.oracle.bestCutAtK.clusters.map(c => c.join('')).join(' | ')}，cut ${d.oracle.bestCutAtK.cut}。` };
    },
    hints: ['AB | CD 切断 A–C 与 B–D。', 'AC | BD 切断 A–B 与 C–D。'],
    answer: '贪心 18；最优 11。',
    explanation: '贪心先拿了眼前最大的 10，把两条 9 都留在了 cut 里。两个结果都合法、都达到 K，只是质量不同。'
  },
  {
    id: 'c6', type: '应用', difficulty: 'Stretch', objectiveId: 'o5', title: '面积不同，结局不同',
    why: '检查你是否把“大小之和”而不是“节点个数”当作容量依据。',
    task: '把 G01 中 A 的大小改成 2（其他仍为 1），容量 3，K = 2。贪心得到什么分组？cut 是多少？',
    build: () => fields([{ key: 'g', label: '分组', type: 'text', placeholder: '例如 ABC|DE' }, { key: 'cut', label: 'cut' }]),
    check: f => {
      const g = { nodes: G01.nodes.map(n => ({ id: n.id, size: n.id === 'A' ? 2 : 1 })), edges: G01.edges };
      const r = M.run(g, { k: 2, capacity: 3 }).result;
      const groups = parseGroups(f.g, ['A', 'B', 'C', 'D', 'E']);
      if (!groups) return { ok: false, message: '分组格式不对：用 | 分开，每个节点恰好出现一次。' };
      const got = groups.map(x => x.sort().join('')).sort().join('|'), want = r.clusters.map(c => c.join('')).sort().join('|');
      if (got !== want) return { ok: false, message: got === 'ABC|DE' ? 'AB 的大小已经是 3：再加入 C 就是 4 > 3。' : '一步步来：A–B 之后，AB+C 的大小是多少？' };
      if (f.cut !== r.cut) return { ok: false, message: '数一数 AB 与 CDE 之间的边。' };
      return { ok: true, message: `${r.labels.join(' | ')}，cut ${r.cut}（原来是 ABC | DE、cut 3）。` };
    },
    hints: ['A–B 合并后大小 2 + 1 = 3，已经满了。', '之后 D–E 合并，再把 C 放进 DE（大小 3）。'],
    answer: 'AB | CDE，cut 5。',
    explanation: '容量按大小之和计算。面积不同的单元会改变哪些合并合法，从而改变最终分组。'
  }
];
