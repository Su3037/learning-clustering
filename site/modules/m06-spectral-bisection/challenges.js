// Module 06 challenges: L, eigenvectors, sweeps and counts all come from engines/spectral.js.
import { choice, fields, combine } from '../../assets/challenges.js';
import * as S from '../../engines/spectral.js';
import { G01 } from '../../engines/graph.js';

const run = () => S.run(G01).result;

export const challenges = [
  {
    id: 'c1', type: '概念', difficulty: 'Intro', objectiveId: 'o2', title: '写出 L 的一行',
    why: '检查你能否从边权直接写出拉普拉斯矩阵，并用“行和为 0”自检。',
    task: '按 A, B, C, D, E 的顺序，写出 G01 拉普拉斯矩阵 L = D − A 中 A 这一行（用逗号分隔五个数）。',
    build: () => fields([{ key: 'row', label: 'A 行', type: 'text', placeholder: '例如 1,2,3,4,5', wide: true }]),
    check: a => {
      const want = S.laplacian(G01).L[0];
      const got = a.row.replace(/[−–]/g, '-').split(/[,\s，]+/).filter(Boolean).map(Number);
      if (got.length !== 5 || got.some(x => !Number.isFinite(x))) return { ok: false, message: '需要 5 个数，用逗号分隔。' };
      if (got[0] !== want[0]) return { ok: false, message: '对角元是 A 的度：与 A 相连的边权之和。' };
      if (got.some((x, i) => x !== want[i])) return { ok: false, message: got.reduce((s, x) => s + x, 0) !== 0 ? '行和不为 0：非对角元应为负的边权。' : '检查 A 与 B、C、D、E 之间各有多大的边权。' };
      return { ok: true, message: `A 行 = ${want.join(', ')}，行和 0。` };
    },
    hints: ['A 的邻居只有 B（5）和 C（1）。', '对角 = 5 + 1；非对角 = −w；没有边的位置为 0。'],
    answer: '6, −5, −1, 0, 0。',
    explanation: '行和为 0 意味着全 1 向量满足 L·1 = 0，所以 λ = 0 总是特征值。'
  },
  {
    id: 'c2', type: '推演', difficulty: 'Intro', objectiveId: 'o5', title: '不在中间切',
    why: '检查你能否在平衡窗口内比较各个切点，而不是默认切在正中间。',
    task: 'Fiedler 排序为 E, D, C, B, A，40/60 窗口（每组 2–3 个）。k = 2 和 k = 3 的 cut 各是多少？应选哪一个？',
    build: () => combine(fields([{ key: 'k2', label: 'k = 2 的 cut' }, { key: 'k3', label: 'k = 3 的 cut' }]), choice([['2', '选 k = 2'], ['3', '选 k = 3（正中间）']])),
    check: ([f, pick]) => {
      const r = run(), s2 = r.sweep.find(s => s.k === 2), s3 = r.sweep.find(s => s.k === 3);
      if (f.k2 !== s2.cut) return { ok: false, message: 'k = 2：左组 E、D，右组 C、B、A——被切断的是哪几条边？' };
      if (f.k3 !== s3.cut) return { ok: false, message: 'k = 3：左组 E、D、C，右组 B、A。' };
      if (+pick !== r.bestK) return { ok: false, message: '两者都在窗口内，选 cut 更小的那个。' };
      return { ok: true, message: `k = 2：cut ${s2.cut}；k = 3：cut ${s3.cut}。选 k = ${r.bestK}，即 ${r.partition.map(p => p.join('')).join(' | ')}。` };
    },
    hints: ['k = 2 时跨组的是 C–D 与 C–E。', 'k = 3 时跨组的是 A–C 与 B–C。'],
    answer: 'k = 2 的 cut 3，k = 3 的 cut 5；选 k = 2。',
    explanation: '“切在正中间”并不更好。扫描每个合法位置，取 cut 最小者。'
  },
  {
    id: 'c3', type: '纠错', difficulty: 'Practice', objectiveId: 'o1', title: '有多少种非空二分',
    why: '检查计数时是否排除了空组、是否去掉了左右重复——原作题库在这里出错。',
    task: '5 个节点分成两组：两组都非空，不区分左右。一共有多少种？',
    build: () => fields([{ key: 'n', label: '种数' }]),
    check: a => {
      const want = S.unlabelledBipartitions(5), ex = S.exhaustiveBisection(G01, { minFraction: 0, maxFraction: 1 }).count;
      if (a.n === want) return { ok: true, message: `(2⁵ − 2) / 2 = ${want}；穷举也数出 ${ex} 种。` };
      return { ok: false, message: a.n === 16 ? '16 把“一组为空、另一组为全集”也算进去了。' : a.n === 30 || a.n === 32 ? '左右交换算同一种：还要除以 2。' : '从 2⁵ 种左右标记出发。' };
    },
    hints: ['每个节点贴“左”或“右”：2⁵ = 32 种。', '去掉“全左”“全右”，再除以 2。'],
    answer: '15。',
    explanation: '原作题库写 16，多算了空组/全集那一种。本课程测试用穷举断言 15。'
  },
  {
    id: 'c4', type: '纠错', difficulty: 'Practice', objectiveId: 'o6', title: '无约束一定切单点吗',
    why: '检查对“无平衡约束时最优总是孤立一个点”这一说法的反驳。',
    task: '在 G01 上不加任何平衡约束（只要两组非空）。孤立一个点的最小 cut 是多少？全局最小 cut 是多少？',
    build: () => fields([{ key: 'single', label: '最小单点 cut' }, { key: 'best', label: '全局最小 cut' }]),
    check: a => {
      const L = S.laplacian(G01).L, single = Math.min(...L.map((r, i) => r[i]));
      const best = S.exhaustiveBisection(G01, { minFraction: 0, maxFraction: 1 }).unconstrained.cut;
      if (a.single !== single) return { ok: false, message: '孤立一个点，被切断的就是它的全部边：cut = 它的度数。' };
      if (a.best !== best) return { ok: false, message: '试试 ABC | DE。' };
      return { ok: true, message: `最小单点 cut ${single}（A 或 E），全局最小 ${best}（ABC | DE）——不是单点。` };
    },
    hints: ['单点 cut = 度数：A 6、B 9、C 8、D 7、E 6。', 'ABC | DE 只切断 C–D 与 C–E。'],
    answer: '最小单点 cut 6；全局最小 3。',
    explanation: '正确的说法是“无约束时可能出现过小的分组”，所以要声明平衡窗口；这张图的无约束最优恰好不是单点。'
  },
  {
    id: 'c5', type: '探索', difficulty: 'Stretch', objectiveId: 'o4', title: '翻号会改变结果吗',
    why: '检查你是否理解特征向量的符号不唯一，以及比较分组时不区分左右。',
    task: '把 Fiedler 向量整体乘以 −1 后重新排序、扫描（同样的 40/60 窗口）。结果的分组会变吗？cut 是多少？',
    build: () => combine(choice([['same', '分组不变（左右互换）'], ['diff', '分组改变']]), fields([{ key: 'cut', label: 'cut' }])),
    check: ([s, f]) => {
      const r = run(), flip = S.run(G01, { vector: r.fiedler.map(x => -x) }).result;
      const key = p => p.map(g => [...g].sort().join('')).sort().join('|');
      const same = key(r.partition) === key(flip.partition);
      if ((s === 'same') !== same) return { ok: false, message: `翻号后排序变为 ${flip.order.join(', ')}：同一刀只是两侧换了名字。` };
      if (f.cut !== flip.cut) return { ok: false, message: '分组没变，cut 也不会变。' };
      return { ok: true, message: `排序反向为 ${flip.order.join(', ')}，仍切出 ${flip.partition.map(p => p.join('')).join(' | ')}，cut ${flip.cut}。` };
    },
    hints: ['若 Lx = λx，则 L(−x) = λ(−x)。', '排序整体反向；k = 3 的位置变成原来 k = 2 的那一刀。'],
    answer: '分组不变；cut 3。',
    explanation: '翻号只交换左右。这也是 Python 检查器里“翻号等价”一项检查的内容。'
  },
  {
    id: 'c6', type: '实现', difficulty: 'Stretch', objectiveId: 'o4', title: '断开的图',
    why: '检查你能否识别 Fiedler 向量失去意义的情形。',
    task: '两个互不相连的三角形（A–B–C 与 D–E–F）。λ2 是多少？这时 Fiedler 排序反映的是什么？',
    build: () => combine(fields([{ key: 'l2', label: 'λ2（保留到整数）' }]), choice([['comp', '只反映哪些点在同一个连通分量'], ['strong', '反映每条边的强弱'], ['balance', '保证两组平衡']])),
    check: ([f, m]) => {
      const r = S.run(S.DISCONNECTED).result;
      if (Math.round(f.l2) !== Math.round(r.eigenvalues[1])) return { ok: false, message: '每个连通分量各贡献一个 λ = 0。' };
      if (m !== 'comp') return { ok: false, message: 'λ2 = 0 的特征空间由“每个分量上取常数”的向量组成。' };
      return { ok: true, message: `λ1 = λ2 = 0（${r.diagnostics.components.length} 个分量）。诊断提示：${r.diagnostics.warnings[0]}` };
    },
    hints: ['全 1 向量在每个分量上分别成立。', '两个分量 → 两个零特征值。'],
    answer: 'λ2 = 0；排序只反映连通分量。',
    explanation: '使用 Fiedler 向量前先检查连通性；本页实验的诊断区会给出同样的警告。'
  }
];
