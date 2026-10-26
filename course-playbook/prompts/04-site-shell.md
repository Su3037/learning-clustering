# Prompt 04 · Course shell, design system and languages

---

Build (or adapt from the reference repo) the static course shell for **{{course}}**. Read
`course-playbook/reference/04-site-design.md`, then `site/assets/course.css`, `site/assets/core.js`,
`site/assets/i18n.js` and `scripts/build-site.mjs` in the reference repo.

Deliver:

1. **Generator**: a small Node script that turns `content/` (JSON + Markdown) into one static HTML page per
   page and module, in Chinese at the root and English under `en/`. Relative paths only.
2. **Design system** per the tokens and type table: warm paper, light serif display (Noto Serif SC /
   Newsreader), Noto Sans SC / Noto Sans text, JetBrains Mono eyebrows and numbers, hairline rules, numbered
   section heads `01 / …`, sticky lesson TOC, dark cinema bands for films and labs. Self-host and subset fonts.
3. **Shared pages**: home (title, intro-film slot, module grid with names and one-line hooks, comparison
   table naming every method, study path), foundations, glossary (zh, en, definition, "do not confuse with"),
   challenge guide, progress (export/import), credits, 404.
4. **Shared components**: language switch (remembers choice, keeps the section), film player with four film
   cards, slides viewer (transcript below the slide), graph view, lab frame, challenge frame, code-lab frame,
   progress store.
5. **Robustness**: 375 px without horizontal scroll, keyboard, reduced motion, storage failure, asset
   failure messages, `.nojekyll`, works under `/<repo>/`.
6. **Site tests** (`tests/site.test.mjs`): links and assets resolve, no CDN, required sections exist,
   font subset coverage, terminology, scope.

Show the author before/after screenshots of the home page and one module page (desktop, phone, English)
before rolling the design out everywhere.
