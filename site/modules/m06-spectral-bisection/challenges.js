// Module 06 challenges: L, eigenvectors, sweeps and counts all come from engines/spectral.js.
import { choice, fields, combine } from '../../assets/challenges.js';
import { L } from '../../assets/i18n.js';
import * as S from '../../engines/spectral.js';
import { G01 } from '../../engines/graph.js';

const run = () => S.run(G01).result;

export const challenges = [
  {
    id: 'c1', type: L('概念', 'Concept'), difficulty: 'Intro', objectiveId: 'o2', title: L('写出 L 的一行', 'Write one row of L'),
    why: L('检查你能否从边权直接写出拉普拉斯矩阵，并用“行和为 0”自检。', 'Checks that you can write the Laplacian straight from the edge weights, and check yourself with “every row sums to 0”.'),
    task: L('按 A, B, C, D, E 的顺序，写出 G01 拉普拉斯矩阵 L = D − A 中 A 这一行（用逗号分隔五个数）。', 'In the order A, B, C, D, E, write row A of G01’s Laplacian L = D − A (five numbers separated by commas).'),
    build: () => fields([{ key: 'row', label: L('A 行', 'Row A'), type: 'text', placeholder: L('例如 1,2,3,4,5', 'e.g. 1,2,3,4,5'), wide: true }]),
    check: a => {
      const want = S.laplacian(G01).L[0];
      const got = a.row.replace(/[−–]/g, '-').split(/[,\s，]+/).filter(Boolean).map(Number);
      if (got.length !== 5 || got.some(x => !Number.isFinite(x))) return { ok: false, message: L('需要 5 个数，用逗号分隔。', 'Five numbers are needed, separated by commas.') };
      if (got[0] !== want[0]) return { ok: false, message: L('对角元是 A 的度：与 A 相连的边权之和。', 'The diagonal entry is A’s degree: the total weight of the edges at A.') };
      if (got.some((x, i) => x !== want[i])) return { ok: false, message: got.reduce((s, x) => s + x, 0) !== 0 ? L('行和不为 0：非对角元应为负的边权。', 'The row does not sum to 0: off-diagonal entries are the negated edge weights.') : L('检查 A 与 B、C、D、E 之间各有多大的边权。', 'Check the weight between A and each of B, C, D and E.') };
      return { ok: true, message: L(`A 行 = ${want.join(', ')}，行和 0。`, `Row A = ${want.join(', ')}; it sums to 0.`) };
    },
    hints: [L('A 的邻居只有 B（5）和 C（1）。', 'A’s only neighbours are B (5) and C (1).'), L('对角 = 5 + 1；非对角 = −w；没有边的位置为 0。', 'Diagonal = 5 + 1; off-diagonal = −w; 0 where there is no edge.')],
    answer: L('6, −5, −1, 0, 0。', '6, −5, −1, 0, 0.'),
    explanation: L('行和为 0 意味着全 1 向量满足 L·1 = 0，所以 λ = 0 总是特征值。', 'Rows summing to 0 means the all-ones vector satisfies L·1 = 0, so λ = 0 is always an eigenvalue.')
  },
  {
    id: 'c2', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o5', title: L('不在中间切', 'Not in the middle'),
    why: L('检查你能否在平衡窗口内比较各个切点，而不是默认切在正中间。', 'Checks that you compare every cut point inside the balance window instead of cutting in the middle by default.'),
    task: L('Fiedler 排序为 E, D, C, B, A，40/60 窗口（每组 2–3 个）。k = 2 和 k = 3 的 cut 各是多少？应选哪一个？', 'The Fiedler order is E, D, C, B, A, with a 40/60 window (2–3 per side). What is the cut at k = 2 and at k = 3? Which should you choose?'),
    build: () => combine(fields([{ key: 'k2', label: L('k = 2 的 cut', 'cut at k = 2') }, { key: 'k3', label: L('k = 3 的 cut', 'cut at k = 3') }]), choice([['2', L('选 k = 2', 'choose k = 2')], ['3', L('选 k = 3（正中间）', 'choose k = 3 (the middle)')]])),
    check: ([f, pick]) => {
      const r = run(), s2 = r.sweep.find(s => s.k === 2), s3 = r.sweep.find(s => s.k === 3);
      if (f.k2 !== s2.cut) return { ok: false, message: L('k = 2：左组 E、D，右组 C、B、A——被切断的是哪几条边？', 'k = 2: E and D on the left, C, B and A on the right. Which edges are cut?') };
      if (f.k3 !== s3.cut) return { ok: false, message: L('k = 3：左组 E、D、C，右组 B、A。', 'k = 3: E, D and C on the left, B and A on the right.') };
      if (+pick !== r.bestK) return { ok: false, message: L('两者都在窗口内，选 cut 更小的那个。', 'Both are inside the window: take the smaller cut.') };
      return { ok: true, message: L(`k = 2：cut ${s2.cut}；k = 3：cut ${s3.cut}。选 k = ${r.bestK}，即 ${r.partition.map(p => p.join('')).join(' | ')}。`, `k = 2: cut ${s2.cut}; k = 3: cut ${s3.cut}. Choose k = ${r.bestK}, that is ${r.partition.map(p => p.join('')).join(' | ')}.`) };
    },
    hints: [L('k = 2 时跨组的是 C–D 与 C–E。', 'At k = 2, C–D and C–E cross.'), L('k = 3 时跨组的是 A–C 与 B–C。', 'At k = 3, A–C and B–C cross.')],
    answer: L('k = 2 的 cut 3，k = 3 的 cut 5；选 k = 2。', 'cut 3 at k = 2, cut 5 at k = 3; choose k = 2.'),
    explanation: L('“切在正中间”并不更好。扫描每个合法位置，取 cut 最小者。', '“Cut in the middle” is not better. Sweep every legal position and take the least cut.')
  },
  {
    id: 'c3', type: L('纠错', 'Debug'), difficulty: 'Practice', objectiveId: 'o1', title: L('有多少种非空二分', 'How many non-empty bipartitions'),
    why: L('检查计数时是否排除了空组、是否去掉了左右重复——原作题库在这里出错。', 'Checks that the count excludes an empty side and drops left/right duplicates; the original question bank got this wrong.'),
    task: L('5 个节点分成两组：两组都非空，不区分左右。一共有多少种？', 'Split 5 nodes into two groups, both non-empty, with no difference between left and right. How many ways are there?'),
    build: () => fields([{ key: 'n', label: L('种数', 'Ways') }]),
    check: a => {
      const want = S.unlabelledBipartitions(5), ex = S.exhaustiveBisection(G01, { minFraction: 0, maxFraction: 1 }).count;
      if (a.n === want) return { ok: true, message: L(`(2⁵ − 2) / 2 = ${want}；穷举也数出 ${ex} 种。`, `(2⁵ − 2) / 2 = ${want}; exhaustive search also counts ${ex}.`) };
      return { ok: false, message: a.n === 16 ? L('16 把“一组为空、另一组为全集”也算进去了。', '16 also counts “one side empty, the other everything”.') : a.n === 30 || a.n === 32 ? L('左右交换算同一种：还要除以 2。', 'Swapping left and right is the same split: divide by 2 as well.') : L('从 2⁵ 种左右标记出发。', 'Start from the 2⁵ ways to mark each node left or right.') };
    },
    hints: [L('每个节点贴“左”或“右”：2⁵ = 32 种。', 'Mark each node “left” or “right”: 2⁵ = 32 ways.'), L('去掉“全左”“全右”，再除以 2。', 'Remove “all left” and “all right”, then divide by 2.')],
    answer: L('15。', '15.'),
    explanation: L('原作题库写 16，多算了空组/全集那一种。本课程测试用穷举断言 15。', 'The original question bank says 16, counting the empty/everything split once too often. This course’s tests assert 15 by exhaustive search.')
  },
  {
    id: 'c4', type: L('纠错', 'Debug'), difficulty: 'Practice', objectiveId: 'o6', title: L('无约束一定切单点吗', 'Does no constraint always cut off one node'),
    why: L('检查对“无平衡约束时最优总是孤立一个点”这一说法的反驳。', 'Checks that you can refute the claim “with no balance constraint, the optimum always isolates one node”.'),
    task: L('在 G01 上不加任何平衡约束（只要两组非空）。孤立一个点的最小 cut 是多少？全局最小 cut 是多少？', 'On G01 with no balance constraint (both sides just non-empty), what is the least cut that isolates one node? What is the global least cut?'),
    build: () => fields([{ key: 'single', label: L('最小单点 cut', 'Least single-node cut') }, { key: 'best', label: L('全局最小 cut', 'Global least cut') }]),
    check: a => {
      const Lm = S.laplacian(G01).L, single = Math.min(...Lm.map((r, i) => r[i]));
      const best = S.exhaustiveBisection(G01, { minFraction: 0, maxFraction: 1 }).unconstrained.cut;
      if (a.single !== single) return { ok: false, message: L('孤立一个点，被切断的就是它的全部边：cut = 它的度数。', 'Isolating one node cuts all of its edges: the cut equals its degree.') };
      if (a.best !== best) return { ok: false, message: L('试试 ABC | DE。', 'Try ABC | DE.') };
      return { ok: true, message: L(`最小单点 cut ${single}（A 或 E），全局最小 ${best}（ABC | DE）——不是单点。`, `The least single-node cut is ${single} (A or E); the global least is ${best} (ABC | DE), not a single node.`) };
    },
    hints: [L('单点 cut = 度数：A 6、B 9、C 8、D 7、E 6。', 'Single-node cut = degree: A 6, B 9, C 8, D 7, E 6.'), L('ABC | DE 只切断 C–D 与 C–E。', 'ABC | DE cuts only C–D and C–E.')],
    answer: L('最小单点 cut 6；全局最小 3。', 'Least single-node cut 6; global least 3.'),
    explanation: L('正确的说法是“无约束时可能出现过小的分组”，所以要声明平衡窗口；这张图的无约束最优恰好不是单点。', 'The correct statement is “with no constraint, a group can come out too small”, which is why a balance window is declared; on this graph the unconstrained optimum happens not to be a single node.')
  },
  {
    id: 'c5', type: L('探索', 'Explore'), difficulty: 'Stretch', objectiveId: 'o4', title: L('翻号会改变结果吗', 'Does flipping the sign change the result'),
    why: L('检查你是否理解特征向量的符号不唯一，以及比较分组时不区分左右。', 'Checks that you understand an eigenvector’s sign is not unique, and that groupings are compared without left and right.'),
    task: L('把 Fiedler 向量整体乘以 −1 后重新排序、扫描（同样的 40/60 窗口）。结果的分组会变吗？cut 是多少？', 'Multiply the whole Fiedler vector by −1, then sort and sweep again (same 40/60 window). Does the grouping change? What is the cut?'),
    build: () => combine(choice([['same', L('分组不变（左右互换）', 'Same grouping (sides swapped)')], ['diff', L('分组改变', 'The grouping changes')]]), fields([{ key: 'cut', label: 'cut' }])),
    check: ([s, f]) => {
      const r = run(), flip = S.run(G01, { vector: r.fiedler.map(x => -x) }).result;
      const key = p => p.map(g => [...g].sort().join('')).sort().join('|');
      const same = key(r.partition) === key(flip.partition);
      if ((s === 'same') !== same) return { ok: false, message: L(`翻号后排序变为 ${flip.order.join(', ')}：同一刀只是两侧换了名字。`, `After the flip the order is ${flip.order.join(', ')}: the same cut, with the sides renamed.`) };
      if (f.cut !== flip.cut) return { ok: false, message: L('分组没变，cut 也不会变。', 'The grouping has not changed, so neither has the cut.') };
      return { ok: true, message: L(`排序反向为 ${flip.order.join(', ')}，仍切出 ${flip.partition.map(p => p.join('')).join(' | ')}，cut ${flip.cut}。`, `The order reverses to ${flip.order.join(', ')} and still cuts ${flip.partition.map(p => p.join('')).join(' | ')}, cut ${flip.cut}.`) };
    },
    hints: [L('若 Lx = λx，则 L(−x) = λ(−x)。', 'If Lx = λx, then L(−x) = λ(−x).'), L('排序整体反向；k = 3 的位置变成原来 k = 2 的那一刀。', 'The order reverses; position k = 3 becomes the old cut at k = 2.')],
    answer: L('分组不变；cut 3。', 'Same grouping; cut 3.'),
    explanation: L('翻号只交换左右。这也是 Python 检查器里“翻号等价”一项检查的内容。', 'Flipping only swaps left and right. That is what the “sign flip” check in the Python checker tests.')
  },
  {
    id: 'c6', type: L('实现', 'Implement'), difficulty: 'Stretch', objectiveId: 'o4', title: L('断开的图', 'A disconnected graph'),
    why: L('检查你能否识别 Fiedler 向量失去意义的情形。', 'Checks that you recognise when the Fiedler vector loses its meaning.'),
    task: L('两个互不相连的三角形（A–B–C 与 D–E–F）。λ2 是多少？这时 Fiedler 排序反映的是什么？', 'Two separate triangles (A–B–C and D–E–F). What is λ2? What does the Fiedler order reflect here?'),
    build: () => combine(fields([{ key: 'l2', label: L('λ2（保留到整数）', 'λ2 (to the nearest integer)') }]), choice([['comp', L('只反映哪些点在同一个连通分量', 'only which nodes share a connected component')], ['strong', L('反映每条边的强弱', 'the strength of each edge')], ['balance', L('保证两组平衡', 'that the two sides are balanced')]])),
    check: ([f, m]) => {
      const r = S.run(S.DISCONNECTED).result;
      if (Math.round(f.l2) !== Math.round(r.eigenvalues[1])) return { ok: false, message: L('每个连通分量各贡献一个 λ = 0。', 'Each connected component contributes its own λ = 0.') };
      if (m !== 'comp') return { ok: false, message: L('λ2 = 0 的特征空间由“每个分量上取常数”的向量组成。', 'The eigenspace of λ2 = 0 consists of vectors that are constant on each component.') };
      return { ok: true, message: L(`λ1 = λ2 = 0（${r.diagnostics.components.length} 个分量）。诊断提示：${r.diagnostics.warnings[0]}`, `λ1 = λ2 = 0 (${r.diagnostics.components.length} components). The diagnosis says: ${r.diagnostics.warnings[0]}`) };
    },
    hints: [L('全 1 向量在每个分量上分别成立。', 'The all-ones vector works on each component separately.'), L('两个分量 → 两个零特征值。', 'Two components → two zero eigenvalues.')],
    answer: L('λ2 = 0；排序只反映连通分量。', 'λ2 = 0; the order only reflects the components.'),
    explanation: L('使用 Fiedler 向量前先检查连通性；本页实验的诊断区会给出同样的警告。', 'Check connectivity before using the Fiedler vector; this page’s lab gives the same warning in its diagnostics.')
  }
];
