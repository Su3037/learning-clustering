// Module 03 challenges: every expected value is computed by engines/merge.js.
import { choice, fields, graphPick, combine } from '../../assets/challenges.js';
import { L } from '../../assets/i18n.js';
import * as M from '../../engines/merge.js';
import { G01, cutEdges } from '../../engines/graph.js';

const run = (opts, g = G01) => M.run(g, opts);
const merges = r => r.events.filter(e => e.kind === 'merge');
const pairs = keys => keys.map(k => k.replace('|', '–')).join(L('、', ', '));

export const challenges = [
  {
    id: 'c1', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o3', title: L('第一步合并哪一对', 'Which pair merges first'),
    why: L('检查数值优先与平票规则：并列时比较成员名字。', 'Checks value first, then the tie rule: on a tie, compare member names.'),
    task: L('G01 从五个单点簇开始。第一步应合并哪一对？', 'G01 starts from five single-node clusters. Which pair should merge first?'),
    build: () => choice([['AB', 'A–B（5）'], ['DE', 'D–E（5）'], ['BC', 'B–C（4）'], ['AC', 'A–C（1）']].map(([v, t]) => [v, L(t, t.replace('（', ' (').replace('）', ')'))])),
    check: a => {
      const d = merges(run({ k: 2 }))[0].decision, want = d.a + d.b;
      if (a === want) return { ok: true, message: L(`A–B 与 D–E 都是 5，比较成员 A < D，选 ${d.a}–${d.b}。`, `A–B and D–E are both 5; comparing members, A < D, so ${d.a}–${d.b}.`) };
      if (a === 'DE') return { ok: false, message: L('D–E 也是 5，但并列时比较成员名字：A 排在 D 前面。', 'D–E is 5 too, but a tie compares member names: A comes before D.') };
      if (a === 'AC') return { ok: false, message: L('这正是原网页字符串比较的错误答案："-1,…" 排在 "-5,…" 前面。按数值，1 远小于 5。', 'That is exactly the original page’s string-comparison mistake: "-1,…" sorts before "-5,…". As numbers, 1 is far below 5.') };
      return { ok: false, message: L('B–C 是 4，不是最大值。', 'B–C is 4, not the largest.') };
    },
    hints: [L('先找最大的亲和度：有两对是 5。', 'Find the largest affinity first: two pairs score 5.'), L('并列时比较两对的成员：[A, B] 与 [D, E]，第一个字母 A < D。', 'On a tie, compare the members: [A, B] against [D, E]; first letters, A < D.')],
    answer: L('A–B。', 'A–B.'),
    explanation: L('选择键 (−5, A, B) 与 (−5, D, E) 第一字段相等，第二字段 A < D。', 'The selection keys (−5, A, B) and (−5, D, E) tie on the first field; on the second, A < D.')
  },
  {
    id: 'c2', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o2', title: L('选出下一对', 'Pick the next pair'),
    why: L('检查收缩后平行边相加，以及并列时的成员比较。', 'Checks that parallel wires add up after a contraction, and the member comparison on a tie.'),
    task: L('A、B 已经合并成 AB。AB 与 C 之间的亲和度是多少？下一步应合并哪一对？', 'A and B have merged into AB. What is the affinity between AB and C, and which pair should merge next?'),
    build: () => combine(fields([{ key: 'aff', label: L('AB–C 的亲和度', 'Affinity of AB–C') }]), choice([['ABC', 'AB–C'], ['DE', 'D–E'], ['CD', 'C–D']])),
    check: ([f, pick]) => {
      const step2 = merges(run({ k: 2 }))[1];
      const abc = step2.candidates.find(c => c.a === 'AB' && c.b === 'C');
      if (f.aff !== abc.affinity) return { ok: false, message: f.aff === 4 ? L('只算了 B–C。A–C 也连到 C：两条平行边要相加。', 'You counted only B–C. A–C also reaches C: the two parallel wires add up.') : L('AB–C 是 A–C 与 B–C 两条边的和。', 'AB–C is the sum of the two wires A–C and B–C.') };
      if (pick !== 'ABC') return { ok: false, message: L('AB–C 与 D–E 都是 5：比较成员 [A, B] 与 [D]，A < D。', 'AB–C and D–E are both 5: compare members [A, B] and [D]; A < D.') };
      return { ok: true, message: L(`AB–C = 1 + 4 = ${abc.affinity}，与 D–E 并列；[A,B] < [D]，合并 AB–C，cut ${step2.metrics.cutBefore} → ${step2.metrics.cut}。`, `AB–C = 1 + 4 = ${abc.affinity}, tying D–E; [A,B] < [D], so AB–C merges, cut ${step2.metrics.cutBefore} → ${step2.metrics.cut}.`) };
    },
    hints: [L('合并后的超节点 AB 连到 C 的边有两条。', 'The merged supernode AB reaches C by two wires.'), L('A–C = 1，B–C = 4；与 D–E = 5 比较时看成员名字。', 'A–C = 1, B–C = 4; against D–E = 5, look at the member names.')],
    answer: L('AB–C = 5；合并 AB–C。', 'AB–C = 5; merge AB–C.'),
    explanation: L('收缩把 A–C、B–C 变成两条平行边，相加为 5。这是原作者 thy031 特别画出的一步。', 'Contraction turns A–C and B–C into two parallel wires that add up to 5. The original author, thy031, drew this step specially.')
  },
  {
    id: 'c3', type: L('探索', 'Explore'), difficulty: 'Practice', objectiveId: 'o4', title: L('画出剩余的 cut', 'Mark the remaining cut'),
    why: L('检查你能否在真实的计算结果上读出哪些边被切断。', 'Checks that you can read off which wires are cut in a real result.'),
    task: L('K = 2、不限容量时，结果是 ABC | DE。请选出所有仍被切断的边。', 'With K = 2 and no capacity, the result is ABC | DE. Select every wire that is still cut.'),
    build: () => graphPick({ graph: G01, positions: G01.positions, mode: 'edges', state: () => {
      const r = run({ k: 2 }).result; return { groups: r.assignment, cut: false };
    }, label: L('点击边按钮选择被切断的边', 'Click the edge buttons to select the cut wires') }),
    check: a => {
      const r = run({ k: 2 }).result, want = cutEdges(G01, r.assignment).map(e => [e.u, e.v].sort().join('|')).sort();
      const got = [...a].sort();
      if (got.join() === want.join()) return { ok: true, message: L(`被切断的是 ${pairs(want)}，cut = ${r.cut}。`, `The cut wires are ${pairs(want)}; cut = ${r.cut}.`) };
      const extra = got.filter(k => !want.includes(k)), miss = want.filter(k => !got.includes(k));
      return { ok: false, message: (extra.length ? L(`${pairs(extra)} 两端在同一组，没有被切断。`, `${pairs(extra)}: both ends are in the same group, so not cut. `) : '') + (miss.length ? L(`还漏了 ${miss.length} 条跨组的边。`, `${miss.length} crossing wire(s) still missing.`) : '') };
    },
    hints: [L('被切断的边：一端在 ABC，另一端在 DE。', 'A cut wire has one end in ABC and the other in DE.'), L('只有 C 连到 D 和 E。', 'Only C reaches D and E.')],
    answer: L('C–D 与 C–E，cut = 2 + 1 = 3。', 'C–D and C–E; cut = 2 + 1 = 3.'),
    explanation: L('每次合并让 cut 下降该次亲和度：18 − 5 − 5 − 5 = 3，剩下的正是 C–D 与 C–E。', 'Each merge lowers the cut by its affinity: 18 − 5 − 5 − 5 = 3, and what remains is exactly C–D and C–E.')
  },
  {
    id: 'c4', type: L('约束', 'Constraint'), difficulty: 'Practice', objectiveId: 'o5', title: L('不能强行凑 K', 'Never force K'),
    why: L('检查你能否区分“合法”与“达到目标”，并读出停止原因。', 'Checks that you can tell “legal” from “target reached”, and read the stop reason.'),
    task: L('容量 C = 2（每个节点大小 1），K = 2。最终有几个簇？cut 是多少？达到 K 了吗？', 'Capacity C = 2 (every node has size 1), K = 2. How many clusters at the end? What is the cut? Is K reached?'),
    build: () => combine(fields([{ key: 'n', label: L('簇数', 'Clusters') }, { key: 'cut', label: 'cut' }]), choice([['yes', L('达到了 K', 'K is reached')], ['no', L('没有达到 K', 'K is not reached')]])),
    check: ([f, reached]) => {
      const r = run({ k: 2, capacity: 2 }).result;
      if (f.n !== r.count) return { ok: false, message: f.n === 2 ? L('只有超容量的合并才能凑出 2 簇——那是非法的。', 'Only an over-capacity merge could make 2 clusters, and that is illegal.') : L('再数一次：AB、C、DE。', 'Count again: AB, C, DE.') };
      if (f.cut !== r.cut) return { ok: false, message: L('数一数 AB、C、DE 之间的边：A–C、B–C、C–D、C–E。', 'Count the wires between AB, C and DE: A–C, B–C, C–D, C–E.') };
      if ((reached === 'yes') !== r.targetReached) return { ok: false, message: L('3 簇 > K = 2：没有达到目标。合法与达到目标是两回事。', '3 clusters > K = 2: the target is not reached. Legal and target reached are two different things.') };
      return { ok: true, message: L(`AB | C | DE：${r.count} 簇，cut ${r.cut}，未达到 K，停止原因 ${r.stopReason}。`, `AB | C | DE: ${r.count} clusters, cut ${r.cut}, K not reached, stop reason ${r.stopReason}.`) };
    },
    hints: [L('第 2 步想合并 AB+C，大小 3 > 2。', 'Step 2 would merge AB+C: size 3 > 2.'), L('合并 D–E 之后，AB+C 和 C+DE 都是 3，没有合法的正亲和度对。', 'After D–E merges, AB+C and C+DE are both 3: no legal positive pair remains.')],
    answer: L('3 簇，cut 8，没有达到 K。', '3 clusters, cut 8, K not reached.'),
    explanation: L('结果合法（每簇 ≤ 2）但没达到 K。下一模块会进一步说明：这里 5 个单位大小装进容量 2 的簇至少需要 ⌈5/2⌉ = 3 簇，所以 K = 2 本来就不可能。', 'The result is legal (every cluster ≤ 2) but K is not reached. The next module goes further: 5 units of size in clusters of capacity 2 need at least ⌈5/2⌉ = 3 clusters, so K = 2 was never possible.')
  },
  {
    id: 'c5', type: L('纠错', 'Debug'), difficulty: 'Stretch', objectiveId: 'o3', title: L('字符串比较选错了谁', 'Whom string comparison picks wrongly'),
    why: L('检查你能否解释原网页错误的机制，而不只是记住正确答案。', 'Checks that you can explain how the original page went wrong, not just remember the right answer.'),
    task: L('原网页用 `cand < best` 比较 [−亲和度, 名字, 名字] 数组。在 [−5, "A", "B"] 与 [−1, "A", "C"] 之间，它会认为哪一个“更小”（从而被选中）？', 'The original page compared [−affinity, name, name] arrays with `cand < best`. Between [−5, "A", "B"] and [−1, "A", "C"], which does it consider “smaller” (and so picks)?'),
    build: () => choice([['m1', L('[−1, "A", "C"]：亲和度 1 的 A–C', '[−1, "A", "C"]: A–C, affinity 1')], ['m5', L('[−5, "A", "B"]：亲和度 5 的 A–B', '[−5, "A", "B"]: A–B, affinity 5')], ['eq', L('两者相等', 'They are equal')]]),
    check: a => {
      const legacy = String([-1, 'A', 'C']) < String([-5, 'A', 'B']);
      const first = merges(run({ k: 2, legacyComparator: true }))[0].decision;
      const cut = run({ k: 2, legacyComparator: true }).result.cut;
      if (a === 'm1' && legacy) return { ok: true, message: L(`"-1,A,C" < "-5,A,B"（字符 1 < 5）。原网页第一步因此合并 ${first.a}–${first.b}@${first.affinity}，最终 cut ${cut}。`, `"-1,A,C" < "-5,A,B" (character 1 < 5). So the original page’s first merge was ${first.a}–${first.b}@${first.affinity}, ending at cut ${cut}.`) };
      return { ok: false, message: L('想一想数组转成字符串后的样子，再逐个字符比较。', 'Picture the arrays turned into strings, then compare them character by character.') };
    },
    hints: [L('数组转成字符串：[−5, "A", "B"] → "-5,A,B"。', 'An array becomes a string: [−5, "A", "B"] → "-5,A,B".'), L('两个字符串的第一个字符都是“-”，第二个字符比较 "1" 与 "5"。', 'Both strings start with "-"; the second characters compare "1" with "5".')],
    answer: L('[−1, "A", "C"]，即 A–C。', '[−1, "A", "C"], that is, A–C.'),
    explanation: L('字符串按字符比较，"1" < "5"，于是亲和度 1 的对被当成更好的。正确做法是逐字段比较：−5 < −1，选 A–B。', 'Strings compare character by character, "1" < "5", so the pair with affinity 1 looks better. The right way compares field by field: −5 < −1, so A–B.')
  },
  {
    id: 'c6', type: L('实现', 'Implement'), difficulty: 'Stretch', objectiveId: 'o6', title: L('多位数与小数', 'Multi-digit and decimal weights'),
    why: L('检查比较器在 10、2.5、2 这样的数值上是否仍按数值工作——只修好五节点图是不够的。', 'Checks that the comparator still works numerically on values like 10, 2.5 and 2: fixing the five-node graph alone is not enough.'),
    task: L('图：P–Q = 2，R–S = 10，Q–R = 2.5，K = 1。按正确的规则，第一步和第二步分别合并哪一对？', 'Graph: P–Q = 2, R–S = 10, Q–R = 2.5, K = 1. Under the correct rule, which pair merges at step 1 and at step 2?'),
    build: () => combine(choice([['PQ', L('第一步 P–Q', 'Step 1: P–Q')], ['RS', L('第一步 R–S', 'Step 1: R–S')], ['QR', L('第一步 Q–R', 'Step 1: Q–R')]]), choice([['PQ2', L('第二步 P–Q', 'Step 2: P–Q')], ['QRS', L('第二步 Q–RS', 'Step 2: Q–RS')]])),
    check: ([a, b]) => {
      const g = { nodes: ['P', 'Q', 'R', 'S'], edges: [['P', 'Q', 2], ['R', 'S', 10], ['Q', 'R', 2.5]] };
      const m = merges(run({ k: 1 }, g));
      if (a !== m[0].decision.a + m[0].decision.b) return { ok: false, message: a === 'PQ' ? L('字符串里 "-2…" 排在 "-10…" 前面，但数值上 10 > 2。', 'As strings, "-2…" sorts before "-10…", but as numbers 10 > 2.') : L('比较三个亲和度：2、10、2.5。', 'Compare the three affinities: 2, 10, 2.5.') };
      const second = m[1].decision.a + m[1].decision.b;
      if ((b === 'QRS') !== (second === 'QRS')) return { ok: false, message: L('RS 合并后，Q–RS = 2.5 与 P–Q = 2 比较。', 'Once RS has merged, compare Q–RS = 2.5 with P–Q = 2.') };
      return { ok: true, message: L(`第一步 R–S@${m[0].decision.affinity}，第二步 ${m[1].decision.a}–${m[1].decision.b}@${m[1].decision.affinity}。`, `Step 1: R–S@${m[0].decision.affinity}; step 2: ${m[1].decision.a}–${m[1].decision.b}@${m[1].decision.affinity}.`) };
    },
    hints: [L('先比较数值：10 > 2.5 > 2。', 'Compare the values first: 10 > 2.5 > 2.'), L('合并 R–S 后，候选是 Q–RS（2.5）与 P–Q（2）。', 'After R–S merges, the candidates are Q–RS (2.5) and P–Q (2).')],
    answer: L('第一步 R–S，第二步 Q–RS。', 'Step 1: R–S; step 2: Q–RS.'),
    explanation: L('这是 Python 练习检查器里的同类回归：数值必须按数值比较，平票才看名字。', 'The Python checker has the same kind of regression test: numbers compare as numbers, and names only break ties.')
  }
];
