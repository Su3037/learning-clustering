# Module {{NN}} {{中文标题}} · Markdown 大纲

> Written before pages, slides and films. Source: {{issue / repo @ commit}}, original author {{name}}.

## 问题定义 · Problem

{{input}} → {{operation}}; each round: {{steps}}; {{selection / acceptance}}; stop when {{condition}}.

## 目标 · Objectives

o1 {{inputs/outputs}} · o2 {{key quantity}} · o3 {{one full run incl. the subtle step}} ·
o4 {{selection / stop}} · o5 {{pseudocode and Python}} · o6 {{limits}}

## 讲解顺序 · Lesson order

`mNN-problem` → `mNN-{{quantity}}` → `mNN-{{round}}` → `mNN-{{selection}}` → `mNN-pseudocode` → `mNN-limits`

## 验收数值 · Acceptance numbers (from `site/engines/{{algo}}.js`)

- Key quantity on the course example: {{values}}
- Round 1: {{step, value, state after}} …; result {{…}}
- Round 2 / stop: {{…}}; stop reason `{{reason}}`
- Variant: {{changed parameter → result}}
- Random tests ({{N}} inputs): {{invariants}}; JS ↔ Python step by step identical

## 影片（四部）· Films

- 科普《{{title}}》（≈ 190 s, {{track}}）: 序 · {{hook}}；一 · {{…}}；二 · {{…}}；三 · {{…}}；四 · {{…}}；尾声
- 精讲《{{title}}》（≈ {{110–150}} s）: 问题；{{quantity}}；{{rule}}；一轮；{{selection}}；停止；小结
- 进阶《{{title}}》（≈ {{130–170}} s）: 一 · 为什么 {{…}}；二 · {{…}}；三 · {{…}}；四 · {{…}}；小结
- 实验演示: recorded from the real page (`video/{{id}}/walkthrough.mjs`): {{what it shows}}

## 课件（{{11–14}} 页）与挑战 · Slides and challenges

Slides: {{titles}}

c1 [推演] {{…}} · c2 [推演] {{…}} · c3 [解释] {{…}} · c4 [决策] {{…}} · c5 [解释] {{…}} · c6 [实现] {{…}}

## 去重 · Dedup

Explained in full here: {{…}}. Only linked (review card) to: {{module / foundations}}.

## 待确认 · Open questions

{{question}} — shown on the page as "pending confirmation" until answered.
