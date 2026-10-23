// Module 03 challenges: every expected value is computed by engines/merge.js.
import { choice, fields, graphPick, combine } from '../../assets/challenges.js';
import * as M from '../../engines/merge.js';
import { G01, cutEdges } from '../../engines/graph.js';

const run = (opts, g = G01) => M.run(g, opts);
const merges = r => r.events.filter(e => e.kind === 'merge');
const norm = s => s.toUpperCase().replace(/[^A-Z|]/g, '').split('|').map(p => p.split('').sort().join('')).sort().join('|');

export const challenges = [
  {
    id: 'c1', type: '推演', difficulty: 'Intro', objectiveId: 'o3', title: '第一步合并哪一对',
    why: '检查数值优先与平票规则：并列时比较成员名字。',
    task: 'G01 从五个单点簇开始。第一步应合并哪一对？',
    build: () => choice([['AB', 'A–B（5）'], ['DE', 'D–E（5）'], ['BC', 'B–C（4）'], ['AC', 'A–C（1）']]),
    check: a => {
      const d = merges(run({ k: 2 }))[0].decision, want = d.a + d.b;
      if (a === want) return { ok: true, message: `A–B 与 D–E 都是 5，比较成员 A < D，选 ${d.a}–${d.b}。` };
      if (a === 'DE') return { ok: false, message: 'D–E 也是 5，但并列时比较成员名字：A 排在 D 前面。' };
      if (a === 'AC') return { ok: false, message: '这正是原网页字符串比较的错误答案："-1,…" 排在 "-5,…" 前面。按数值，1 远小于 5。' };
      return { ok: false, message: 'B–C 是 4，不是最大值。' };
    },
    hints: ['先找最大的亲和度：有两对是 5。', '并列时比较两对的成员：[A, B] 与 [D, E]，第一个字母 A < D。'],
    answer: 'A–B。',
    explanation: '选择键 (−5, A, B) 与 (−5, D, E) 第一字段相等，第二字段 A < D。'
  },
  {
    id: 'c2', type: '推演', difficulty: 'Intro', objectiveId: 'o2', title: '选出下一对',
    why: '检查收缩后平行边相加，以及并列时的成员比较。',
    task: 'A、B 已经合并成 AB。AB 与 C 之间的亲和度是多少？下一步应合并哪一对？',
    build: () => combine(fields([{ key: 'aff', label: 'AB–C 的亲和度' }]), choice([['ABC', 'AB–C'], ['DE', 'D–E'], ['CD', 'C–D']])),
    check: ([f, pick]) => {
      const step2 = merges(run({ k: 2 }))[1];
      const abc = step2.candidates.find(c => c.a === 'AB' && c.b === 'C');
      if (f.aff !== abc.affinity) return { ok: false, message: f.aff === 4 ? '只算了 B–C。A–C 也连到 C：两条平行边要相加。' : 'AB–C 是 A–C 与 B–C 两条边的和。' };
      if (pick !== 'ABC') return { ok: false, message: 'AB–C 与 D–E 都是 5：比较成员 [A, B] 与 [D]，A < D。' };
      return { ok: true, message: `AB–C = 1 + 4 = ${abc.affinity}，与 D–E 并列；[A,B] < [D]，合并 AB–C，cut ${step2.metrics.cutBefore} → ${step2.metrics.cut}。` };
    },
    hints: ['合并后的超节点 AB 连到 C 的边有两条。', 'A–C = 1，B–C = 4；与 D–E = 5 比较时看成员名字。'],
    answer: 'AB–C = 5；合并 AB–C。',
    explanation: '收缩把 A–C、B–C 变成两条平行边，相加为 5。这是原作者 thy031 特别画出的一步。'
  },
  {
    id: 'c3', type: '探索', difficulty: 'Practice', objectiveId: 'o4', title: '画出剩余的 cut',
    why: '检查你能否在真实的计算结果上读出哪些边被切断。',
    task: 'K = 2、不限容量时，结果是 ABC | DE。请选出所有仍被切断的边。',
    build: () => graphPick({ graph: G01, positions: G01.positions, mode: 'edges', state: () => {
      const r = run({ k: 2 }).result; return { groups: r.assignment, cut: false };
    }, label: '点击边按钮选择被切断的边' }),
    check: a => {
      const r = run({ k: 2 }).result, want = cutEdges(G01, r.assignment).map(e => [e.u, e.v].sort().join('|')).sort();
      const got = [...a].sort();
      if (got.join() === want.join()) return { ok: true, message: `被切断的是 ${want.map(k => k.replace('|', '–')).join('、')}，cut = ${r.cut}。` };
      const extra = got.filter(k => !want.includes(k)), miss = want.filter(k => !got.includes(k));
      return { ok: false, message: (extra.length ? `${extra.map(k => k.replace('|', '–')).join('、')} 两端在同一组，没有被切断。` : '') + (miss.length ? `还漏了 ${miss.length} 条跨组的边。` : '') };
    },
    hints: ['被切断的边：一端在 ABC，另一端在 DE。', '只有 C 连到 D 和 E。'],
    answer: 'C–D 与 C–E，cut = 2 + 1 = 3。',
    explanation: '每次合并让 cut 下降该次亲和度：18 − 5 − 5 − 5 = 3，剩下的正是 C–D 与 C–E。'
  },
  {
    id: 'c4', type: '约束', difficulty: 'Practice', objectiveId: 'o5', title: '不能强行凑 K',
    why: '检查你能否区分“合法”与“达到目标”，并读出停止原因。',
    task: '容量 C = 2（每个节点大小 1），K = 2。最终有几个簇？cut 是多少？达到 K 了吗？',
    build: () => combine(fields([{ key: 'n', label: '簇数' }, { key: 'cut', label: 'cut' }]), choice([['yes', '达到了 K'], ['no', '没有达到 K']])),
    check: ([f, reached]) => {
      const r = run({ k: 2, capacity: 2 }).result;
      if (f.n !== r.count) return { ok: false, message: f.n === 2 ? '只有超容量的合并才能凑出 2 簇——那是非法的。' : `再数一次：AB、C、DE。` };
      if (f.cut !== r.cut) return { ok: false, message: '数一数 AB、C、DE 之间的边：A–C、B–C、C–D、C–E。' };
      if ((reached === 'yes') !== r.targetReached) return { ok: false, message: '3 簇 > K = 2：没有达到目标。合法与达到目标是两回事。' };
      return { ok: true, message: `AB | C | DE：${r.count} 簇，cut ${r.cut}，未达到 K，停止原因 ${r.stopReason}。` };
    },
    hints: ['第 2 步想合并 AB+C，大小 3 > 2。', '合并 D–E 之后，AB+C 和 C+DE 都是 3，没有合法的正亲和度对。'],
    answer: '3 簇，cut 8，没有达到 K。',
    explanation: '结果合法（每簇 ≤ 2）但没达到 K。下一模块会进一步说明：这里 5 个单位大小装进容量 2 的簇至少需要 ⌈5/2⌉ = 3 簇，所以 K = 2 本来就不可能。'
  },
  {
    id: 'c5', type: '纠错', difficulty: 'Stretch', objectiveId: 'o3', title: '字符串比较选错了谁',
    why: '检查你能否解释原网页错误的机制，而不只是记住正确答案。',
    task: '原网页用 `cand < best` 比较 [−亲和度, 名字, 名字] 数组。在 [−5, "A", "B"] 与 [−1, "A", "C"] 之间，它会认为哪一个“更小”（从而被选中）？',
    build: () => choice([['m1', '[−1, "A", "C"]：亲和度 1 的 A–C'], ['m5', '[−5, "A", "B"]：亲和度 5 的 A–B'], ['eq', '两者相等']]),
    check: a => {
      const legacy = String([-1, 'A', 'C']) < String([-5, 'A', 'B']);
      const first = merges(run({ k: 2, legacyComparator: true }))[0].decision;
      if (a === 'm1' && legacy) return { ok: true, message: `"-1,A,C" < "-5,A,B"（字符 1 < 5）。原网页第一步因此合并 ${first.a}–${first.b}@${first.affinity}，最终 cut ${run({ k: 2, legacyComparator: true }).result.cut}。` };
      return { ok: false, message: '想一想数组转成字符串后的样子，再逐个字符比较。' };
    },
    hints: ['数组转成字符串：[−5, "A", "B"] → "-5,A,B"。', '两个字符串的第一个字符都是“-”，第二个字符比较 "1" 与 "5"。'],
    answer: '[−1, "A", "C"]，即 A–C。',
    explanation: '字符串按字符比较，"1" < "5"，于是亲和度 1 的对被当成更好的。正确做法是逐字段比较：−5 < −1，选 A–B。'
  },
  {
    id: 'c6', type: '实现', difficulty: 'Stretch', objectiveId: 'o6', title: '多位数与小数',
    why: '检查比较器在 10、2.5、2 这样的数值上是否仍按数值工作——只修好五节点图是不够的。',
    task: '图：P–Q = 2，R–S = 10，Q–R = 2.5，K = 1。按正确的规则，第一步和第二步分别合并哪一对？',
    build: () => combine(choice([['PQ', '第一步 P–Q'], ['RS', '第一步 R–S'], ['QR', '第一步 Q–R']]), choice([['PQ2', '第二步 P–Q'], ['QRS', '第二步 Q–RS']])),
    check: ([a, b]) => {
      const g = { nodes: ['P', 'Q', 'R', 'S'], edges: [['P', 'Q', 2], ['R', 'S', 10], ['Q', 'R', 2.5]] };
      const m = merges(run({ k: 1 }, g));
      if (a !== m[0].decision.a + m[0].decision.b) return { ok: false, message: a === 'PQ' ? '字符串里 "-2…" 排在 "-10…" 前面，但数值上 10 > 2。' : '比较三个亲和度：2、10、2.5。' };
      const second = m[1].decision.a + m[1].decision.b;
      if ((b === 'QRS') !== (second === 'QRS')) return { ok: false, message: `RS 合并后，Q–RS = 2.5 与 P–Q = 2 比较。` };
      return { ok: true, message: `第一步 R–S@${m[0].decision.affinity}，第二步 ${m[1].decision.a}–${m[1].decision.b}@${m[1].decision.affinity}。` };
    },
    hints: ['先比较数值：10 > 2.5 > 2。', '合并 R–S 后，候选是 Q–RS（2.5）与 P–Q（2）。'],
    answer: '第一步 R–S，第二步 Q–RS。',
    explanation: '这是 Python 练习检查器里的同类回归：数值必须按数值比较，平票才看名字。'
  }
];
