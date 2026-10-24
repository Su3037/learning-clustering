// Module 05 challenges: every check runs engines/lp.js (adapted from the author's own Lab05 engine).
import { choice, fields, combine } from '../../assets/challenges.js';
import { L } from '../../assets/i18n.js';
import * as LP from '../../engines/lp.js';
import { G01, groupsKey } from '../../engines/graph.js';

const golden = () => LP.run(G01);
const norm = s => s.toUpperCase().replace(/[^A-Z|]/g, '').split('|').filter(Boolean).map(p => p.split('').sort().join(',')).sort().join(' | ');
const list = xs => xs.join(L('、', ', '));

export const challenges = [
  {
    id: 'c1', type: L('概念', 'Concept'), difficulty: 'Intro', objectiveId: 'o1', title: L('名字与标签', 'Names and labels'),
    why: L('检查你能否区分节点的身份（名字）和它当前的归属（标签）。', 'Checks that you can tell a node’s identity (its name) from its current membership (its label).'),
    task: L('第 1 轮之后，节点 C 携带标签 B。下面哪一句说法正确？', 'After round 1, node C carries label B. Which statement is correct?'),
    build: () => choice([['label', L('C 仍是节点 C，只是它的标签变为 B', 'C is still node C; only its label became B')], ['rename', L('C 改名为 B', 'C was renamed B')], ['merge', L('C 与 B 合并成了一个节点', 'C and B merged into one node')], ['k', L('这说明 K = 2', 'This shows K = 2')]]),
    check: a => {
      const ev = golden().events.find(e => e.round === 1 && e.node === 'C');
      if (a === 'label' && ev.label === 'B') return { ok: true, message: L(`C 的票是 ${list(Object.entries(ev.votes).map(([l, v]) => `${l}=${v}`))}，标签改为 ${ev.label}；节点名不变。`, `C’s votes are ${list(Object.entries(ev.votes).map(([l, v]) => `${l}=${v}`))}, so its label becomes ${ev.label}; the node’s name does not change.`) };
      return { ok: false, message: { rename: L('名字是身份，永远不变。', 'A name is identity and never changes.'), merge: L('标签传播不合并任何节点。', 'Label propagation merges no nodes.'), k: L('标签传播不指定 K；最后有几组由标签自己决定。', 'Label propagation does not fix K; the labels decide how many groups there are.') }[a] };
    },
    hints: [L('本章有没有“合并”这个动作？', 'Is there any “merge” step in this module?'), L('名字是身份，标签是归属。', 'A name is identity; a label is membership.')],
    answer: L('C 仍是节点 C，只是它的标签变为 B。', 'C is still node C; only its label became B.'),
    explanation: L('分组看“标签相同的节点”。C、A、B 都携带标签 B，所以它们是一组。', 'Groups are “nodes with the same label”. C, A and B all carry label B, so they form one group.')
  },
  {
    id: 'c2', type: L('推演', 'Trace'), difficulty: 'Intro', objectiveId: 'o2', title: L('C 的票数', 'C’s votes'),
    why: L('检查按标签“加权”计票，而不是数人头。', 'Checks that votes are weighted by label, not counted per neighbour.'),
    task: L('按 A→E 异步更新，轮到 C 时 A 已改为标签 B、B 仍为 B。C 的票：标签 B、D、E 各得多少？', 'Updating asynchronously in the order A→E, by C’s turn A has switched to label B and B is still B. How many votes do labels B, D and E get from C’s neighbours?'),
    build: () => fields([{ key: 'B', label: 'B' }, { key: 'D', label: 'D' }, { key: 'E', label: 'E' }]),
    check: a => {
      const v = golden().events.find(e => e.round === 1 && e.node === 'C').votes;
      for (const l of ['B', 'D', 'E']) if (a[l] !== v[l]) return { ok: false, message: l === 'B' && a.B === 2 ? L('不是数人头：A、B 两个邻居的边权是 1 和 4。', 'Don’t count heads: the edges to neighbours A and B weigh 1 and 4.') : L(`标签 ${l} 的票不对：把带这个标签的邻居的边权加起来。`, `The votes for label ${l} are off: add up the edge weights of the neighbours carrying it.`) };
      return { ok: true, message: L(`B = 1 + 4 = ${v.B}，D = ${v.D}，E = ${v.E}：C 选 B。`, `B = 1 + 4 = ${v.B}, D = ${v.D}, E = ${v.E}: C picks B.`) };
    },
    hints: [L('C 的邻居是 A、B、D、E；此时 A、B 都带标签 B。', 'C’s neighbours are A, B, D and E; right now A and B both carry label B.'), L('标签 B 的票 = w(C,A) + w(C,B)。', 'Votes for label B = w(C,A) + w(C,B).')],
    answer: L('B = 5，D = 2，E = 1。', 'B = 5, D = 2, E = 1.'),
    explanation: L('票数是同标签邻居的边权之和。两个邻居带 B，但它们的权重合起来才是 5。', 'A label’s votes are the sum of the edge weights of the neighbours carrying it. Two neighbours carry B, and together their weights make 5.')
  },
  {
    id: 'c3', type: L('推演', 'Trace'), difficulty: 'Practice', objectiveId: 'o3', title: L('几轮才算停下', 'How many rounds until it stops'),
    why: L('检查“零变化确认轮”：一整轮没有任何改变才是 stable。', 'Checks the confirmation round: only a full round with no change at all is stable.'),
    task: L('G01、A→E 异步、平票取小。到 stable 为止共几轮？最终 cut 是多少？', 'G01, asynchronous A→E, ties to the smaller label. How many rounds until stable, and what is the final cut?'),
    build: () => fields([{ key: 'rounds', label: L('轮数', 'Rounds') }, { key: 'cut', label: 'cut' }]),
    check: a => {
      const r = golden().result;
      if (a.rounds !== r.rounds) return { ok: false, message: a.rounds === 1 ? L('第 1 轮有 3 个节点改变；还需要一轮确认零变化。', 'Three nodes change in round 1; one more round is needed to confirm zero changes.') : L('数一数：第几轮才完整地零变化？', 'Count: in which round does nothing change at all?') };
      if (a.cut !== r.cut) return { ok: false, message: L('最终 B/B/B/E/E：被切断的是哪几条边？', 'Finally B/B/B/E/E: which edges are cut?') };
      return { ok: true, message: L(`第 1 轮改 3 个，第 2 轮零变化：${r.rounds} 轮，${r.status}，cut ${r.cut}。`, `Round 1 changes 3 nodes, round 2 changes none: ${r.rounds} rounds, ${r.status}, cut ${r.cut}.`) };
    },
    hints: [L('第 1 轮之后标签是 B B B E E。', 'After round 1 the labels are B B B E E.'), L('第 2 轮重新检查，全部不变——这一轮也要算。', 'Round 2 checks again and nothing changes; that round counts too.')],
    answer: L('2 轮，cut 3。', '2 rounds, cut 3.'),
    explanation: L('只看“这一步没变”不够：后面的节点一改，前面的节点可能又要改。轮数包含这一确认轮。', '“This step did not change” is not enough: once a later node changes, an earlier one may want to change again. The round count includes the confirmation round.')
  },
  {
    id: 'c4', type: L('探索', 'Explore'), difficulty: 'Practice', objectiveId: 'o4', title: L('找到振荡', 'Find a cycle'),
    why: L('检查你能否区分 stable 与 cycle，并知道是什么导致振荡。', 'Checks that you can tell stable from cycle and know what causes a cycle.'),
    task: L('两节点图 A–B（权重 1）。下面哪种设置会振荡？这时应报告哪种状态？', 'A two-node graph A–B (weight 1). Which setting makes it cycle, and which state should be reported?'),
    build: () => combine(choice([['async', L('异步更新', 'Asynchronous updates')], ['sync', L('同步更新', 'Synchronous updates')], ['none', L('两种都不会', 'Neither')]]), choice([['stable', 'stable'], ['cycle', 'cycle'], ['limit', 'limit']])),
    check: ([mode, st]) => {
      const s = LP.run(LP.PRESETS.pair, { mode: 'sync' }).result, a = LP.run(LP.PRESETS.pair, { mode: 'async' }).result;
      if (mode !== 'sync') return { ok: false, message: mode === 'async' ? L(`异步：A 先改为 B，B 读到的已经是 B——${a.status}。`, `Asynchronous: A switches to B first, and B already sees B: ${a.status}.`) : L('同步会振荡：两者读同一张旧快照，同时交换。', 'Synchronous updates cycle: both read the same old snapshot and swap at the same time.') };
      if (st !== s.status) return { ok: false, message: st === 'stable' ? L('标签一直在变，不能叫 stable。', 'The labels keep changing, so it cannot be called stable.') : L('状态重复出现——这比“到了上限”更具体。', 'A state repeats, which says more than “hit the limit”.') };
      return { ok: true, message: L(`同步：A、B 每轮交换标签，第 ${s.rounds} 轮回到出现过的状态，报告 ${s.status}。`, `Synchronous: A and B swap labels every round; in round ${s.rounds} a state repeats, so it reports ${s.status}.`) };
    },
    hints: [L('同步：整轮读同一张旧快照，轮末一起提交。', 'Synchronous: the whole round reads one old snapshot and commits at the end.'), L('A 读到 B、B 读到 A，同时交换；下一轮再换回来。', 'A sees B and B sees A, so they swap at the same time, then swap back next round.')],
    answer: L('同步更新；报告 cycle。', 'Synchronous updates; report cycle.'),
    explanation: L('振荡不是“还没算完”。G01 在同步模式下也会以周期 2 振荡；可以在上方实验把更新方式切到同步验证。', 'A cycle is not “not finished yet”. G01 also cycles with period 2 under synchronous updates; switch the lab above to synchronous to see it.')
  },
  {
    id: 'c5', type: L('探索', 'Explore'), difficulty: 'Stretch', objectiveId: 'o5', title: L('加粗一条桥', 'Strengthen one bridge'),
    why: L('检查改边权后是否从初始标签重新运行，并能读出新的分组。', 'Checks that after changing a weight you rerun from the initial labels and can read the new grouping.'),
    task: L('把 G01 的 C–D 改为 10，其他不变，从初始标签重新运行（A→E 异步、平票取小）。分组和 cut 是什么？', 'Set C–D in G01 to 10, keep everything else, and rerun from the initial labels (asynchronous A→E, ties to the smaller label). What are the grouping and the cut?'),
    build: () => fields([{ key: 'g', label: L('分组', 'Grouping'), type: 'text', placeholder: L('例如 ABC|DE', 'e.g. ABC|DE') }, { key: 'cut', label: 'cut' }]),
    check: a => {
      const h = structuredClone(G01); h.edges.find(e => e.u === 'C' && e.v === 'D').w = 10;
      const r = LP.run(h).result;
      if (norm(a.g) !== r.grouping) return { ok: false, message: norm(a.g) === 'A,B,C | D,E' ? L('C–D = 10 时，轮到 C 的那一刻 D 的标签是什么？再算一次 C 的票。', 'With C–D = 10, what is D’s label at the moment C is visited? Count C’s votes again.') : L('逐个节点重算：注意 D 先改为 D 自己（票 C:10）还是 E？', 'Recompute node by node: does D first keep its own label (votes C:10) or switch to E?') };
      if (a.cut !== r.cut) return { ok: false, message: L('数一数 AB 与 CDE 之间的边。', 'Count the edges between AB and CDE.') };
      return { ok: true, message: L(`${r.grouping}，cut ${r.cut}，${r.rounds} 轮。`, `${r.grouping}, cut ${r.cut}, ${r.rounds} rounds.`) };
    },
    hints: [L('第 1 轮轮到 C 时：B 票 = 1 + 4 = 5，D 票 = 10。', 'At C’s turn in round 1: votes for B = 1 + 4 = 5, for D = 10.'), L('C 跟随 D，D、E 再统一到同一个标签。', 'C follows D, and then D and E settle on one label.')],
    answer: L('AB | CDE，cut 5。', 'AB | CDE, cut 5.'),
    explanation: L('边权变了，投票的结果就变了；比较时要从同一个初始状态重新运行，而不是在旧结果上继续。', 'When a weight changes, the votes change; to compare, rerun from the same initial state instead of continuing from the old result.')
  },
  {
    id: 'c6', type: L('实现', 'Implement'), difficulty: 'Stretch', objectiveId: 'o6', title: L('换个顺序再跑', 'Run it in another order'),
    why: L('检查你是否按“分组”而不是“标签名”比较结果，并注意到轮数会变。', 'Checks that you compare results by grouping rather than label names, and notice that the round count changes.'),
    task: L('把访问顺序改为 E→D→C→B→A（其他同默认）。和默认顺序相比，分组相同吗？需要几轮？', 'Change the visiting order to E→D→C→B→A (everything else default). Compared with the default order, is the grouping the same? How many rounds does it take?'),
    build: () => combine(choice([['same', L('分组相同', 'Same grouping')], ['diff', L('分组不同', 'Different grouping')]]), fields([{ key: 'rounds', label: L('轮数', 'Rounds') }])),
    check: ([same, f]) => {
      const a = golden().result, b = LP.run(G01, { order: ['E', 'D', 'C', 'B', 'A'] }).result;
      const eq = groupsKey(a.labels) === groupsKey(b.labels);
      if ((same === 'same') !== eq) return { ok: false, message: L(`反序的标签是 ${Object.values(b.labels).join('/')}：看谁和谁在一起，而不是标签叫什么。`, `In reverse order the labels are ${Object.values(b.labels).join('/')}: look at who is together, not at what the labels are called.`) };
      if (f.rounds !== b.rounds) return { ok: false, message: L('在上方实验里把访问顺序改成 EDCBA 数一数。', 'Set the visiting order to E D C B A in the lab above and count.') };
      return { ok: true, message: L(`标签 ${Object.values(b.labels).join('/')}，分组仍是 ${b.grouping}，但需要 ${b.rounds} 轮。`, `Labels ${Object.values(b.labels).join('/')}: the grouping is still ${b.grouping}, but it takes ${b.rounds} rounds.`) };
    },
    hints: [L('反序时最后的标签是 A/A/A/D/D。', 'In reverse order the final labels are A/A/A/D/D.'), L('分组 ABC | DE 不变；轮数比默认多一轮。', 'The grouping ABC | DE stays; it takes one round more than the default.')],
    answer: L('分组相同（ABC | DE），3 轮。', 'Same grouping (ABC | DE), 3 rounds.'),
    explanation: L('Python 检查器也按分组判断等价；访问顺序是输入的一部分，会影响轮数，在别的图上也可能影响分组。', 'The Python checker also compares by grouping. The visiting order is part of the input: it affects the round count, and on other graphs it can affect the grouping too.')
  }
];
