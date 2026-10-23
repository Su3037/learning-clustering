// Module 05 challenges: every check runs engines/lp.js (adapted from the author's own Lab05 engine).
import { choice, fields, combine } from '../../assets/challenges.js';
import * as LP from '../../engines/lp.js';
import { G01, groupsKey } from '../../engines/graph.js';

const golden = () => LP.run(G01);
const norm = s => s.toUpperCase().replace(/[^A-Z|]/g, '').split('|').filter(Boolean).map(p => p.split('').sort().join(',')).sort().join(' | ');

export const challenges = [
  {
    id: 'c1', type: '概念', difficulty: 'Intro', objectiveId: 'o1', title: '名字与标签',
    why: '检查你能否区分节点的身份（名字）和它当前的归属（标签）。',
    task: '第 1 轮之后，节点 C 携带标签 B。下面哪一句说法正确？',
    build: () => choice([['label', 'C 仍是节点 C，只是它的标签变为 B'], ['rename', 'C 改名为 B'], ['merge', 'C 与 B 合并成了一个节点'], ['k', '这说明 K = 2']]),
    check: a => {
      const ev = golden().events.find(e => e.round === 1 && e.node === 'C');
      if (a === 'label' && ev.label === 'B') return { ok: true, message: `C 的票是 ${Object.entries(ev.votes).map(([l, v]) => `${l}=${v}`).join('、')}，标签改为 ${ev.label}；节点名不变。` };
      return { ok: false, message: { rename: '名字是身份，永远不变。', merge: '标签传播不合并任何节点。', k: '标签传播不指定 K；最后有几组由标签自己决定。' }[a] };
    },
    hints: ['本章有没有“合并”这个动作？', '名字是身份，标签是归属。'],
    answer: 'C 仍是节点 C，只是它的标签变为 B。',
    explanation: '分组看“标签相同的节点”。C、A、B 都携带标签 B，所以它们是一组。'
  },
  {
    id: 'c2', type: '推演', difficulty: 'Intro', objectiveId: 'o2', title: 'C 的票数',
    why: '检查按标签“加权”计票，而不是数人头。',
    task: '按 A→E 异步更新，轮到 C 时 A 已改为标签 B、B 仍为 B。C 的票：标签 B、D、E 各得多少？',
    build: () => fields([{ key: 'B', label: 'B' }, { key: 'D', label: 'D' }, { key: 'E', label: 'E' }]),
    check: a => {
      const v = golden().events.find(e => e.round === 1 && e.node === 'C').votes;
      for (const l of ['B', 'D', 'E']) if (a[l] !== v[l]) return { ok: false, message: l === 'B' && a.B === 2 ? '不是数人头：A、B 两个邻居的边权是 1 和 4。' : `标签 ${l} 的票不对：把带这个标签的邻居的边权加起来。` };
      return { ok: true, message: `B = 1 + 4 = ${v.B}，D = ${v.D}，E = ${v.E}：C 选 B。` };
    },
    hints: ['C 的邻居是 A、B、D、E；此时 A、B 都带标签 B。', '标签 B 的票 = w(C,A) + w(C,B)。'],
    answer: 'B = 5，D = 2，E = 1。',
    explanation: '票数是同标签邻居的边权之和。两个邻居带 B，但它们的权重合起来才是 5。'
  },
  {
    id: 'c3', type: '推演', difficulty: 'Practice', objectiveId: 'o3', title: '几轮才算停下',
    why: '检查“零变化确认轮”：一整轮没有任何改变才是 stable。',
    task: 'G01、A→E 异步、平票取小。到 stable 为止共几轮？最终 cut 是多少？',
    build: () => fields([{ key: 'rounds', label: '轮数' }, { key: 'cut', label: 'cut' }]),
    check: a => {
      const r = golden().result;
      if (a.rounds !== r.rounds) return { ok: false, message: a.rounds === 1 ? '第 1 轮有 3 个节点改变；还需要一轮确认零变化。' : '数一数：第几轮才完整地零变化？' };
      if (a.cut !== r.cut) return { ok: false, message: '最终 B/B/B/E/E：被切断的是哪几条边？' };
      return { ok: true, message: `第 1 轮改 3 个，第 2 轮零变化：${r.rounds} 轮，${r.status}，cut ${r.cut}。` };
    },
    hints: ['第 1 轮之后标签是 B B B E E。', '第 2 轮重新检查，全部不变——这一轮也要算。'],
    answer: '2 轮，cut 3。',
    explanation: '只看“这一步没变”不够：后面的节点一改，前面的节点可能又要改。轮数包含这一确认轮。'
  },
  {
    id: 'c4', type: '探索', difficulty: 'Practice', objectiveId: 'o4', title: '找到振荡',
    why: '检查你能否区分 stable 与 cycle，并知道是什么导致振荡。',
    task: '两节点图 A–B（权重 1）。下面哪种设置会振荡？这时应报告哪种状态？',
    build: () => combine(choice([['async', '异步更新'], ['sync', '同步更新'], ['none', '两种都不会']]), choice([['stable', 'stable'], ['cycle', 'cycle'], ['limit', 'limit']])),
    check: ([mode, st]) => {
      const s = LP.run(LP.PRESETS.pair, { mode: 'sync' }).result, a = LP.run(LP.PRESETS.pair, { mode: 'async' }).result;
      if (mode !== 'sync') return { ok: false, message: mode === 'async' ? `异步：A 先改为 B，B 读到的已经是 B——${a.status}。` : `同步会振荡：两者读同一张旧快照，同时交换。` };
      if (st !== s.status) return { ok: false, message: st === 'stable' ? '标签一直在变，不能叫 stable。' : '状态重复出现——这比“到了上限”更具体。' };
      return { ok: true, message: `同步：A、B 每轮交换标签，第 ${s.rounds} 轮回到出现过的状态，报告 ${s.status}。` };
    },
    hints: ['同步：整轮读同一张旧快照，轮末一起提交。', 'A 读到 B、B 读到 A，同时交换；下一轮再换回来。'],
    answer: '同步更新；报告 cycle。',
    explanation: '振荡不是“还没算完”。G01 在同步模式下也会以周期 2 振荡；可以在上方实验把更新方式切到同步验证。'
  },
  {
    id: 'c5', type: '探索', difficulty: 'Stretch', objectiveId: 'o5', title: '加粗一条桥',
    why: '检查改边权后是否从初始标签重新运行，并能读出新的分组。',
    task: '把 G01 的 C–D 改为 10，其他不变，从初始标签重新运行（A→E 异步、平票取小）。分组和 cut 是什么？',
    build: () => fields([{ key: 'g', label: '分组', type: 'text', placeholder: '例如 ABC|DE' }, { key: 'cut', label: 'cut' }]),
    check: a => {
      const h = structuredClone(G01); h.edges.find(e => e.u === 'C' && e.v === 'D').w = 10;
      const r = LP.run(h).result;
      if (norm(a.g) !== r.grouping) return { ok: false, message: norm(a.g) === 'A,B,C | D,E' ? 'C–D = 10 时，轮到 C 的那一刻 D 的标签是什么？再算一次 C 的票。' : '逐个节点重算：注意 D 先改为 D 自己（票 C:10）还是 E？' };
      if (a.cut !== r.cut) return { ok: false, message: '数一数 AB 与 CDE 之间的边。' };
      return { ok: true, message: `${r.grouping}，cut ${r.cut}，${r.rounds} 轮。` };
    },
    hints: ['第 1 轮轮到 C 时：B 票 = 1 + 4 = 5，D 票 = 10。', 'C 跟随 D，D、E 再统一到同一个标签。'],
    answer: 'AB | CDE，cut 5。',
    explanation: '边权变了，投票的结果就变了；比较时要从同一个初始状态重新运行，而不是在旧结果上继续。'
  },
  {
    id: 'c6', type: '实现', difficulty: 'Stretch', objectiveId: 'o6', title: '换个顺序再跑',
    why: '检查你是否按“分组”而不是“标签名”比较结果，并注意到轮数会变。',
    task: '把访问顺序改为 E→D→C→B→A（其他同默认）。和默认顺序相比，分组相同吗？需要几轮？',
    build: () => combine(choice([['same', '分组相同'], ['diff', '分组不同']]), fields([{ key: 'rounds', label: '轮数' }])),
    check: ([same, f]) => {
      const a = golden().result, b = LP.run(G01, { order: ['E', 'D', 'C', 'B', 'A'] }).result;
      const eq = groupsKey(a.labels) === groupsKey(b.labels);
      if ((same === 'same') !== eq) return { ok: false, message: `反序的标签是 ${Object.values(b.labels).join('/')}：看谁和谁在一起，而不是标签叫什么。` };
      if (f.rounds !== b.rounds) return { ok: false, message: '在上方实验里把访问顺序改成 EDCBA 数一数。' };
      return { ok: true, message: `标签 ${Object.values(b.labels).join('/')}，分组仍是 ${b.grouping}，但需要 ${b.rounds} 轮。` };
    },
    hints: ['反序时最后的标签是 A/A/A/D/D。', '分组 ABC | DE 不变；轮数比默认多一轮。'],
    answer: '分组相同（ABC | DE），3 轮。',
    explanation: 'Python 检查器也按分组判断等价；访问顺序是输入的一部分，会影响轮数，在别的图上也可能影响分组。'
  }
];
