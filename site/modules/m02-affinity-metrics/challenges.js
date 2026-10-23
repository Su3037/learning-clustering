// Module 02 challenges. Every check computes the expected value with engines/affinity.js.
import { choice, fields, orderList, combine } from '../../assets/challenges.js';
import * as AF from '../../engines/affinity.js';
import { G01 } from '../../engines/graph.js';

const shared = () => AF.sharedNeighbors(G01);
const find = (list, u, v) => list.find(p => p.u === u && p.v === v);
const label = p => `${p.u}–${p.v}`;

export const challenges = [
  {
    id: 'c1', type: '概念', difficulty: 'Intro', objectiveId: 'o1', title: '评分不是分组',
    why: '区分本章的输出（排名）与后续模块的输出（簇）。',
    task: '在 G01 上算完共同邻居评分后，Module 02 的输出是什么？',
    build: () => choice([['rank', '所有正分节点对的排名列表'], ['groups', 'ABC | DE 两个簇'], ['labels', '每个节点一个标签'], ['top', '只有排名第一的 A–B']]),
    check: a => a === 'rank' ? { ok: true, message: '对：本章只给节点对排名。' }
      : { ok: false, message: a === 'groups' ? '两个簇是 Module 03 合并之后的结果；评分本身不决定分组。' : a === 'labels' ? '标签是 Module 05 标签传播的概念。' : '第一名只是排名的一部分；完整输出是整张排名表。' },
    hints: ['想想本章的问题定义里“输出”写的是什么。', '输出里有“u < v”和“按分数降序”——这是一张表，不是分组。'],
    answer: '所有正分节点对的排名列表。',
    explanation: '评分回答“先合并谁”，真正的合并、停止和簇数从 Module 03 开始；标签传播、谱二分、KL/FM 甚至不按“最高分的一对”工作。'
  },
  {
    id: 'c2', type: '推演', difficulty: 'Intro', objectiveId: 'o3', title: '没有直接边也能评分',
    why: '检查你会不会漏掉没有直接连线的节点对。',
    task: 'G01 中 B 和 D 之间没有边。按共同邻居评分，B–D 的分数是多少？它来自哪个共同邻居？',
    build: () => fields([{ key: 'score', label: 'B–D 分数' }, { key: 'x', label: '共同邻居', type: 'text', placeholder: '节点名' }]),
    check: a => {
      const p = find(shared(), 'B', 'D');
      if (a.score !== p.score) return { ok: false, message: a.score === 0 ? '没有直接边只说明直接部分是 0；还要加上经共同邻居的贡献。' : `分数不对。直接部分 0，再看 B 和 D 同时连着谁。` };
      if (a.x.trim().toUpperCase() !== p.parts.via[0].x) return { ok: false, message: '分数对了，但共同邻居写错了：要同时和 B、D 直接相连。' };
      return { ok: true, message: `B–D = 0 + min(w(B,C), w(D,C)) = min(4, 2) = ${p.score}。` };
    },
    hints: ['B 的邻居是 A、C；D 的邻居是 C、E。', '共同邻居只有 C，取 min(w(B,C), w(D,C))。'],
    answer: '2，来自共同邻居 C。',
    explanation: 'B–D 没有导线，评分并没有“新增连线”，只是承认 B、D 都和 C 相连。完整的共同邻居表有 10 对，这一对排第 7。'
  },
  {
    id: 'c3', type: '推演', difficulty: 'Practice', objectiveId: 'o3', title: '把 A–C 拆开',
    why: '检查你能否把一个分数分解成直接部分和间接部分。',
    task: '写出 A–C 共同邻居分数的两个组成部分和总分。',
    build: () => fields([{ key: 'direct', label: '直接部分' }, { key: 'via', label: '经共同邻居的部分' }, { key: 'total', label: '总分' }]),
    check: a => {
      const p = find(shared(), 'A', 'C'), via = p.parts.via.reduce((s, c) => s + c.min, 0);
      if (a.direct !== p.parts.direct) return { ok: false, message: '直接部分就是 A–C 这条边的权重。' };
      if (a.via !== via) return { ok: false, message: a.via === 5 ? '经 B 的贡献取两条边中较弱的那条：min(5, 4)，不是 5。' : '找出 A 和 C 的共同邻居，取两条边的较小值。' };
      if (a.total !== p.score) return { ok: false, message: '总分 = 直接部分 + 间接部分。' };
      return { ok: true, message: `A–C = ${p.parts.direct} + min(5, 4) = ${p.score}。` };
    },
    hints: ['直接部分看 A–C 的边权。', '共同邻居是 B；w(A,B)=5、w(C,B)=4。'],
    answer: '直接 1，经 B 的 min(5, 4) = 4，总分 5。',
    explanation: '经过 x 的间接联系只和较弱的那条边一样强，所以用 min。'
  },
  {
    id: 'c4', type: '探索', difficulty: 'Practice', objectiveId: 'o4', title: '换一种评分，第一对是谁',
    why: '检查你能否预测换模型后第一对的变化，并用稳定排名处理并列。',
    task: '在 priority 图（PQR 三角形每边 4，X–Y = 5）上，分别按直接边权和共同邻居，排名第一的节点对是哪一对？',
    build: () => combine(
      choice([['XY', '直接边权：X–Y'], ['PQ', '直接边权：P–Q'], ['PR', '直接边权：P–R']]),
      choice([['XY', '共同邻居：X–Y'], ['PQ', '共同邻居：P–Q'], ['QR', '共同邻居：Q–R']])),
    check: ([e, s]) => {
      const te = AF.edgeWeight(AF.PRIORITY_GRAPH)[0], ts = AF.sharedNeighbors(AF.PRIORITY_GRAPH)[0];
      if (e !== te.u + te.v) return { ok: false, message: '直接边权只看这两点之间的线：最粗的是哪一条？' };
      if (s !== ts.u + ts.v) return { ok: false, message: s === 'XY' ? 'X–Y 没有共同邻居，共同邻居分仍是 5；三角形里每对是 4 + 4 = 8。' : 'P–Q、P–R、Q–R 都是 8，并列时按 u、v 字典序。' };
      return { ok: true, message: `直接边权第一 ${label(te)}@${te.score}；共同邻居第一 ${label(ts)}@${ts.score}。` };
    },
    hints: ['共同邻居：三角形中任一对都经过第三个点。', '三对都是 8 分并列，稳定排名比较 u，再比较 v。'],
    answer: '直接边权 X–Y@5；共同邻居 P–Q@8（P–Q、P–R、Q–R 并列，字典序取 P–Q）。',
    explanation: '两种模型回答不同的问题：一个只看单线粗细，一个还看是否属于紧密的小团体。'
  },
  {
    id: 'c5', type: '实现', difficulty: 'Practice', objectiveId: 'o2', title: '手工排出稳定排名',
    why: '检查平票规则：分数降序，再按 u、v 字典序。',
    task: '按“直接边权”的规则，把 G01 的 6 对排好（第一名在最上面）。',
    build: () => orderList(['C–E', 'A–C', 'D–E', 'B–C', 'A–B', 'C–D']),
    check: a => {
      const want = AF.edgeWeight(G01).map(label);
      if (a.join() === want.join()) return { ok: true, message: '顺序正确：' + want.join(' > ') };
      const k = a.findIndex((x, i) => x !== want[i]);
      return { ok: false, message: `第 ${k + 1} 位不对（你放的是 ${a[k]}）。分数相同时，先比较 u，再比较 v。` };
    },
    hints: ['先按分数分组：5、5、4、2、1、1。', 'A–B 与 D–E 都是 5：A < D，所以 A–B 在前；A–C 与 C–E 都是 1：A < C。'],
    answer: 'A–B、D–E、B–C、C–D、A–C、C–E。',
    explanation: '固定平票规则之后，无论边按什么顺序输入，排名都一样——这是 Python 练习里“乱序输入”测试检查的性质。'
  },
  {
    id: 'c6', type: '探索', difficulty: 'Stretch', objectiveId: 'o4', title: '让 X–Y 重新排第一',
    why: '检查你能否从公式反推临界值，而不只是读出结果。',
    task: '在 priority 图上用共同邻居评分。把 X–Y 的边权改成多少（最小的整数），它才会排第一？',
    build: () => fields([{ key: 'w', label: 'X–Y 新权重' }]),
    check: a => {
      const top = w => { const g = { nodes: AF.PRIORITY_GRAPH.nodes, edges: AF.PRIORITY_GRAPH.edges.map(([u, v, x]) => [u, v, u === 'X' ? w : x]) }; return label(AF.sharedNeighbors(g)[0]); };
      if (!Number.isInteger(a.w) || a.w < 1) return { ok: false, message: '请输入正整数。' };
      if (top(a.w) !== 'X–Y') return { ok: false, message: `权重 ${a.w} 时第一名仍是 ${top(a.w)}。${a.w === 8 ? '8 分与 P–Q 并列，平票按名字 P < X。' : ''}` };
      if (top(a.w - 1) === 'X–Y') return { ok: false, message: `${a.w} 能让 X–Y 第一，但还有更小的整数也可以。` };
      return { ok: true, message: `X–Y = ${a.w} > 8 时才排第一；等于 8 时平票输给 P–Q。` };
    },
    hints: ['X–Y 没有共同邻居，它的共同邻居分就等于边权。', '要超过 P–Q 的 8；等于 8 时看平票规则。'],
    answer: '9。',
    explanation: 'X–Y 的分数只有直接部分；三角形里每对是 4 + 4 = 8。并列时 P–Q 字典序在前，所以需要 9。可以在上方实验里把 X–Y 改成 8 和 9 验证。'
  },
  {
    id: 'c7', type: '应用', difficulty: 'Stretch', objectiveId: 'o5', title: '宽 net 的稀释',
    why: '检查 clique 模型的摊薄计算，以及它为什么改变排名。',
    task: 'tiny netlist 中，A–B 被两条 5 引脚 net（enable、reset）同时连着，E–F 只被一条两引脚 net 连着。填写三个数。',
    build: () => fields([{ key: 'raw', label: 'A–B 按 net 计数' }, { key: 'ab', label: 'A–B 的 pin-count' }, { key: 'ef', label: 'E–F 的 pin-count' }]),
    check: a => {
      const pc = AF.pinCount(AF.TINY_NETLIST), ab = pc.scores.find(p => p.u === 'A' && p.v === 'B'), ef = pc.scores.find(p => p.u === 'E' && p.v === 'F');
      const raw = pc.raw.find(p => p.u === 'A' && p.v === 'B').score;
      if (a.raw !== raw) return { ok: false, message: '按 net 计数：A、B 同时出现在几条 net 里？' };
      if (Math.abs(a.ab - ab.score) > 1e-9) return { ok: false, message: '每条 5 引脚 net 给每一对 w/(|e|−1) = 1/4。' };
      if (Math.abs(a.ef - ef.score) > 1e-9) return { ok: false, message: 'n1 只有 2 个引脚：1/(2−1)。' };
      return { ok: true, message: `计数 A–B = ${raw} 胜过 E–F；摊薄后 E–F = ${ef.score} 胜过 A–B = ${ab.score}。` };
    },
    hints: ['net 计数不摊薄：两条 net 各算 1。', 'pin-count：w/(|e|−1)，5 引脚 net 每对得 1/4。'],
    answer: '计数 2；A–B 的 pin-count 0.5；E–F 的 pin-count 1。',
    explanation: '一条连着 10 对单元的宽 net 几乎不能说明“A 和 B 特别该在一起”；clique 模型把它摊薄，私有的 E–F 才排第一。图上展开的两两连线只是示意贡献。'
  }
];
