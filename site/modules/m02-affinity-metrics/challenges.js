// Module 02 challenges. Every check computes the expected value with engines/affinity.js.
import { choice, fields, orderList, combine } from '../../assets/challenges.js';
import { L } from '../../assets/i18n.js';
import * as AF from '../../engines/affinity.js';
import { G01 } from '../../engines/graph.js';

const shared = () => AF.sharedNeighbors(G01);
const find = (list, u, v) => list.find(p => p.u === u && p.v === v);
const label = p => `${p.u}–${p.v}`;

export const challenges = [
  {
    id: 'c1', type: L('概念', 'Concept'), difficulty: 'Intro', objectiveId: 'o1', title: L('评分不是分组', 'A score is not a grouping'),
    why: L('区分本章的输出（排名）与后续模块的输出（簇）。', 'Tells this module’s output (a ranking) apart from the output of later modules (clusters).'),
    task: L('在 G01 上算完共同邻居评分后，Module 02 的输出是什么？', 'After computing shared-neighbour scores on G01, what is Module 02’s output?'),
    build: () => choice([['rank', L('所有正分节点对的排名列表', 'A ranked list of every pair with a positive score')], ['groups', L('ABC | DE 两个簇', 'Two clusters, ABC | DE')], ['labels', L('每个节点一个标签', 'One label per node')], ['top', L('只有排名第一的 A–B', 'Only the top pair, A–B')]]),
    check: a => a === 'rank' ? { ok: true, message: L('对：本章只给节点对排名。', 'Right: this module only ranks pairs.') }
      : { ok: false, message: a === 'groups' ? L('两个簇是 Module 03 合并之后的结果；评分本身不决定分组。', 'Two clusters are what Module 03’s merging produces; a score does not decide a grouping.') : a === 'labels' ? L('标签是 Module 05 标签传播的概念。', 'Labels belong to Module 05, label propagation.') : L('第一名只是排名的一部分；完整输出是整张排名表。', 'The top pair is only part of the ranking; the full output is the whole ranked list.') },
    hints: [L('想想本章的问题定义里“输出”写的是什么。', 'Look at what the problem definition says under “output”.'), L('输出里有“u < v”和“按分数降序”——这是一张表，不是分组。', 'The output mentions “u < v” and “score descending”: it is a table, not a grouping.')],
    answer: L('所有正分节点对的排名列表。', 'A ranked list of every pair with a positive score.'),
    explanation: L('评分回答“先合并谁”，真正的合并、停止和簇数从 Module 03 开始；标签传播、谱二分、KL/FM 甚至不按“最高分的一对”工作。', 'A score answers “whom to merge first”; the merging itself, the stopping rule and the number of clusters start in Module 03. Label propagation, spectral bisection and KL/FM do not even work by “the top pair”.')
  },
  {
    id: 'c2', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o3', title: L('没有直接边也能评分', 'A score without a direct edge'),
    why: L('检查你会不会漏掉没有直接连线的节点对。', 'Checks that you do not skip pairs with no direct wire.'),
    task: L('G01 中 B 和 D 之间没有边。按共同邻居评分，B–D 的分数是多少？它来自哪个共同邻居？', 'In G01 there is no edge between B and D. By shared neighbours, what is the score of B–D, and which shared neighbour does it come from?'),
    build: () => fields([{ key: 'score', label: L('B–D 分数', 'B–D score') }, { key: 'x', label: L('共同邻居', 'Shared neighbour'), type: 'text', placeholder: L('节点名', 'node name') }]),
    check: a => {
      const p = find(shared(), 'B', 'D');
      if (a.score !== p.score) return { ok: false, message: a.score === 0 ? L('没有直接边只说明直接部分是 0；还要加上经共同邻居的贡献。', 'No direct edge only means the direct part is 0; add what the shared neighbours contribute.') : L('分数不对。直接部分 0，再看 B 和 D 同时连着谁。', 'Not the right score. The direct part is 0; now look at who both B and D are connected to.') };
      if (a.x.trim().toUpperCase() !== p.parts.via[0].x) return { ok: false, message: L('分数对了，但共同邻居写错了：要同时和 B、D 直接相连。', 'The score is right but the shared neighbour is not: it must be directly connected to both B and D.') };
      return { ok: true, message: L(`B–D = 0 + min(w(B,C), w(D,C)) = min(4, 2) = ${p.score}。`, `B–D = 0 + min(w(B,C), w(D,C)) = min(4, 2) = ${p.score}.`) };
    },
    hints: [L('B 的邻居是 A、C；D 的邻居是 C、E。', 'B’s neighbours are A and C; D’s are C and E.'), L('共同邻居只有 C，取 min(w(B,C), w(D,C))。', 'The only shared neighbour is C: take min(w(B,C), w(D,C)).')],
    answer: L('2，来自共同邻居 C。', '2, from the shared neighbour C.'),
    explanation: L('B–D 没有导线，评分并没有“新增连线”，只是承认 B、D 都和 C 相连。完整的共同邻居表有 10 对，这一对排第 7。', 'B–D has no wire; the score adds no wire either, it only recognises that B and D are both connected to C. The full shared-neighbour table has 10 pairs, and this one ranks 7th.')
  },
  {
    id: 'c3', type: L('推演', 'Trace'), difficulty: 'Practice', objectiveId: 'o3', title: L('把 A–C 拆开', 'Take A–C apart'),
    why: L('检查你能否把一个分数分解成直接部分和间接部分。', 'Checks that you can split a score into its direct and indirect parts.'),
    task: L('写出 A–C 共同邻居分数的两个组成部分和总分。', 'Give the two parts of A–C’s shared-neighbour score, and the total.'),
    build: () => fields([{ key: 'direct', label: L('直接部分', 'Direct part') }, { key: 'via', label: L('经共同邻居的部分', 'Part through shared neighbours') }, { key: 'total', label: L('总分', 'Total') }]),
    check: a => {
      const p = find(shared(), 'A', 'C'), via = p.parts.via.reduce((s, c) => s + c.min, 0);
      if (a.direct !== p.parts.direct) return { ok: false, message: L('直接部分就是 A–C 这条边的权重。', 'The direct part is simply the weight of the edge A–C.') };
      if (a.via !== via) return { ok: false, message: a.via === 5 ? L('经 B 的贡献取两条边中较弱的那条：min(5, 4)，不是 5。', 'The contribution through B takes the weaker of the two edges: min(5, 4), not 5.') : L('找出 A 和 C 的共同邻居，取两条边的较小值。', 'Find the shared neighbour of A and C, and take the smaller of its two edges.') };
      if (a.total !== p.score) return { ok: false, message: L('总分 = 直接部分 + 间接部分。', 'Total = direct part + indirect part.') };
      return { ok: true, message: L(`A–C = ${p.parts.direct} + min(5, 4) = ${p.score}。`, `A–C = ${p.parts.direct} + min(5, 4) = ${p.score}.`) };
    },
    hints: [L('直接部分看 A–C 的边权。', 'For the direct part, look at the weight of A–C.'), L('共同邻居是 B；w(A,B)=5、w(C,B)=4。', 'The shared neighbour is B; w(A,B) = 5 and w(C,B) = 4.')],
    answer: L('直接 1，经 B 的 min(5, 4) = 4，总分 5。', 'Direct 1, through B min(5, 4) = 4, total 5.'),
    explanation: L('经过 x 的间接联系只和较弱的那条边一样强，所以用 min。', 'An indirect link through x is only as strong as its weaker edge, hence min.')
  },
  {
    id: 'c4', type: L('探索', 'Explore'), difficulty: 'Practice', objectiveId: 'o4', title: L('换一种评分，第一对是谁', 'A different score, a different first pair'),
    why: L('检查你能否预测换模型后第一对的变化，并用稳定排名处理并列。', 'Checks that you can predict how the first pair changes with the model, and settle ties with the stable ranking.'),
    task: L('在 priority 图（PQR 三角形每边 4，X–Y = 5）上，分别按直接边权和共同邻居，排名第一的节点对是哪一对？', 'On the priority graph (triangle PQR with every edge 4, X–Y = 5), which pair ranks first by direct weight, and which by shared neighbours?'),
    build: () => combine(
      choice([['XY', L('直接边权：X–Y', 'Direct weight: X–Y')], ['PQ', L('直接边权：P–Q', 'Direct weight: P–Q')], ['PR', L('直接边权：P–R', 'Direct weight: P–R')]]),
      choice([['XY', L('共同邻居：X–Y', 'Shared neighbours: X–Y')], ['PQ', L('共同邻居：P–Q', 'Shared neighbours: P–Q')], ['QR', L('共同邻居：Q–R', 'Shared neighbours: Q–R')]])),
    check: ([e, s]) => {
      const te = AF.edgeWeight(AF.PRIORITY_GRAPH)[0], ts = AF.sharedNeighbors(AF.PRIORITY_GRAPH)[0];
      if (e !== te.u + te.v) return { ok: false, message: L('直接边权只看这两点之间的线：最粗的是哪一条？', 'Direct weight looks only at the wire between the two: which is the thickest?') };
      if (s !== ts.u + ts.v) return { ok: false, message: s === 'XY' ? L('X–Y 没有共同邻居，共同邻居分仍是 5；三角形里每对是 4 + 4 = 8。', 'X–Y has no shared neighbour, so its shared-neighbour score stays 5; every pair in the triangle gets 4 + 4 = 8.') : L('P–Q、P–R、Q–R 都是 8，并列时按 u、v 字典序。', 'P–Q, P–R and Q–R are all 8; ties go by u, then v, alphabetically.') };
      return { ok: true, message: L(`直接边权第一 ${label(te)}@${te.score}；共同邻居第一 ${label(ts)}@${ts.score}。`, `First by direct weight: ${label(te)}@${te.score}; first by shared neighbours: ${label(ts)}@${ts.score}.`) };
    },
    hints: [L('共同邻居：三角形中任一对都经过第三个点。', 'Shared neighbours: any pair in the triangle goes through the third node.'), L('三对都是 8 分并列，稳定排名比较 u，再比较 v。', 'All three pairs tie at 8; the stable ranking compares u, then v.')],
    answer: L('直接边权 X–Y@5；共同邻居 P–Q@8（P–Q、P–R、Q–R 并列，字典序取 P–Q）。', 'Direct weight X–Y@5; shared neighbours P–Q@8 (P–Q, P–R and Q–R tie, and P–Q comes first alphabetically).'),
    explanation: L('两种模型回答不同的问题：一个只看单线粗细，一个还看是否属于紧密的小团体。', 'The two models answer different questions: one looks only at how thick a single wire is, the other also at whether the pair belongs to a tight little group.')
  },
  {
    id: 'c5', type: L('实现', 'Implement'), difficulty: 'Practice', objectiveId: 'o2', title: L('手工排出稳定排名', 'Sort the stable ranking by hand'),
    why: L('检查平票规则：分数降序，再按 u、v 字典序。', 'Checks the tie rule: score descending, then u and v alphabetically.'),
    task: L('按“直接边权”的规则，把 G01 的 6 对排好（第一名在最上面）。', 'Rank G01’s six pairs by direct weight (first place at the top).'),
    build: () => orderList(['C–E', 'A–C', 'D–E', 'B–C', 'A–B', 'C–D']),
    check: a => {
      const want = AF.edgeWeight(G01).map(label);
      if (a.join() === want.join()) return { ok: true, message: L('顺序正确：', 'The order is right: ') + want.join(' > ') };
      const k = a.findIndex((x, i) => x !== want[i]);
      return { ok: false, message: L(`第 ${k + 1} 位不对（你放的是 ${a[k]}）。分数相同时，先比较 u，再比较 v。`, `Position ${k + 1} is wrong (you put ${a[k]} there). For equal scores, compare u first, then v.`) };
    },
    hints: [L('先按分数分组：5、5、4、2、1、1。', 'Group by score first: 5, 5, 4, 2, 1, 1.'), L('A–B 与 D–E 都是 5：A < D，所以 A–B 在前；A–C 与 C–E 都是 1：A < C。', 'A–B and D–E are both 5: A < D, so A–B comes first; A–C and C–E are both 1: A < C.')],
    answer: L('A–B、D–E、B–C、C–D、A–C、C–E。', 'A–B, D–E, B–C, C–D, A–C, C–E.'),
    explanation: L('固定平票规则之后，无论边按什么顺序输入，排名都一样——这是 Python 练习里“乱序输入”测试检查的性质。', 'With the tie rule fixed, the ranking is the same whatever order the edges arrive in: the property the code lab’s “shuffled input” check tests.')
  },
  {
    id: 'c6', type: L('探索', 'Explore'), difficulty: 'Stretch', objectiveId: 'o4', title: L('让 X–Y 重新排第一', 'Put X–Y back on top'),
    why: L('检查你能否从公式反推临界值，而不只是读出结果。', 'Checks that you can work back from the formula to a threshold, not just read off a result.'),
    task: L('在 priority 图上用共同邻居评分。把 X–Y 的边权改成多少（最小的整数），它才会排第一？', 'Use shared neighbours on the priority graph. What is the smallest whole-number weight for X–Y that puts it first?'),
    build: () => fields([{ key: 'w', label: L('X–Y 新权重', 'New weight of X–Y') }]),
    check: a => {
      const top = w => { const g = { nodes: AF.PRIORITY_GRAPH.nodes, edges: AF.PRIORITY_GRAPH.edges.map(([u, v, x]) => [u, v, u === 'X' ? w : x]) }; return label(AF.sharedNeighbors(g)[0]); };
      if (!Number.isInteger(a.w) || a.w < 1) return { ok: false, message: L('请输入正整数。', 'Enter a positive whole number.') };
      if (top(a.w) !== 'X–Y') return { ok: false, message: L(`权重 ${a.w} 时第一名仍是 ${top(a.w)}。`, `With weight ${a.w}, first place is still ${top(a.w)}.`) + (a.w === 8 ? L('8 分与 P–Q 并列，平票按名字 P < X。', ' At 8 it ties with P–Q, and the tie goes by name: P < X.') : '') };
      if (top(a.w - 1) === 'X–Y') return { ok: false, message: L(`${a.w} 能让 X–Y 第一，但还有更小的整数也可以。`, `${a.w} puts X–Y first, but a smaller whole number also works.`) };
      return { ok: true, message: L(`X–Y = ${a.w} > 8 时才排第一；等于 8 时平票输给 P–Q。`, `X–Y comes first only at ${a.w} > 8; at 8 it loses the tie to P–Q.`) };
    },
    hints: [L('X–Y 没有共同邻居，它的共同邻居分就等于边权。', 'X–Y has no shared neighbour, so its shared-neighbour score equals its edge weight.'), L('要超过 P–Q 的 8；等于 8 时看平票规则。', 'It has to beat P–Q’s 8; at exactly 8, look at the tie rule.')],
    answer: L('9。', '9.'),
    explanation: L('X–Y 的分数只有直接部分；三角形里每对是 4 + 4 = 8。并列时 P–Q 字典序在前，所以需要 9。可以在上方实验里把 X–Y 改成 8 和 9 验证。', 'X–Y’s score has only a direct part; each pair in the triangle gets 4 + 4 = 8. In a tie P–Q comes first alphabetically, so 9 is needed. Try X–Y at 8 and at 9 in the lab above.')
  },
  {
    id: 'c7', type: L('应用', 'Apply'), difficulty: 'Stretch', objectiveId: 'o5', title: L('宽 net 的稀释', 'Diluting wide nets'),
    why: L('检查 clique 模型的摊薄计算，以及它为什么改变排名。', 'Checks the clique model’s sharing-out, and why it changes the ranking.'),
    task: L('tiny netlist 中，A–B 被两条 5 引脚 net（enable、reset）同时连着，E–F 只被一条两引脚 net 连着。填写三个数。', 'In the tiny netlist, A–B are both on two five-pin nets (enable, reset), while E–F share only one two-pin net. Fill in the three numbers.'),
    build: () => fields([{ key: 'raw', label: L('A–B 按 net 计数', 'A–B by net count') }, { key: 'ab', label: L('A–B 的 pin-count', 'pin-count of A–B') }, { key: 'ef', label: L('E–F 的 pin-count', 'pin-count of E–F') }]),
    check: a => {
      const pc = AF.pinCount(AF.TINY_NETLIST), ab = pc.scores.find(p => p.u === 'A' && p.v === 'B'), ef = pc.scores.find(p => p.u === 'E' && p.v === 'F');
      const raw = pc.raw.find(p => p.u === 'A' && p.v === 'B').score;
      if (a.raw !== raw) return { ok: false, message: L('按 net 计数：A、B 同时出现在几条 net 里？', 'By net count: how many nets contain both A and B?') };
      if (Math.abs(a.ab - ab.score) > 1e-9) return { ok: false, message: L('每条 5 引脚 net 给每一对 w/(|e|−1) = 1/4。', 'Each five-pin net gives every pair w/(|e|−1) = 1/4.') };
      if (Math.abs(a.ef - ef.score) > 1e-9) return { ok: false, message: L('n1 只有 2 个引脚：1/(2−1)。', 'n1 has only 2 pins: 1/(2−1).') };
      return { ok: true, message: L(`计数 A–B = ${raw} 胜过 E–F；摊薄后 E–F = ${ef.score} 胜过 A–B = ${ab.score}。`, `By count, A–B = ${raw} beats E–F; shared out, E–F = ${ef.score} beats A–B = ${ab.score}.`) };
    },
    hints: [L('net 计数不摊薄：两条 net 各算 1。', 'A net count does not share anything out: each net counts 1.'), L('pin-count：w/(|e|−1)，5 引脚 net 每对得 1/4。', 'pin-count: w/(|e|−1), so a five-pin net gives each pair 1/4.')],
    answer: L('计数 2；A–B 的 pin-count 0.5；E–F 的 pin-count 1。', 'Count 2; pin-count of A–B 0.5; pin-count of E–F 1.'),
    explanation: L('一条连着 10 对单元的宽 net 几乎不能说明“A 和 B 特别该在一起”；clique 模型把它摊薄，私有的 E–F 才排第一。图上展开的两两连线只是示意贡献。', 'A wide net that ties 10 pairs of cells says almost nothing about “A and B belonging together in particular”; the clique model shares it out, and the private E–F comes first. The pairwise lines drawn for the net are only illustrative contributions.')
  }
];
