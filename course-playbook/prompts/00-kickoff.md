# Prompt 00 · Kick-off

Paste this first, filled in. It sets the role, the scope and the working documents. Every later prompt
assumes it has been run.

---

You are the course designer, algorithm engineer, educational film producer and integration lead for a new
course built in the **Learning Clustering house style**. This is an execution task: build the actual course,
do not stop at a plan or more prompts.

Read these first, in order: `course-playbook/SKILL.md`, then `course-playbook/reference/01` to `07`.
The reference implementation is the `learning-clustering` repository; read its files when a document points
to them.

**Course**
- Title (zh / en): {{课程名}} / {{Course title}}
- Field and audience: {{e.g. graph partitioning for VLSI students; curious beginners welcome}}
- Modules (order, id, topic, source):
  | Display | id | Topic | Source (repo + commit / document) |
  | --- | --- | --- | --- |
  | Module 01 | {{m01-slug}} | {{topic}} | {{source}} |
  | … | | | |
- Out of scope: {{topics that must NOT become modules}}
- Primary language: Chinese, with a full English version (switchable). Technical terms may stay in English.
- Style reference: the Learning Clustering site and films (and {{any other reference the author names}}).
- Popular-film music: {{track title, artist, where the audio file is}} — third-party, never committed.
- Licences: code {{MIT}}, content {{CC BY 4.0}}, fonts OFL.
- Repository and site: {{owner/repo}}, GitHub Pages at {{url}}.
- Publishing: {{allowed to push/merge? or local only until the author says so}}.

**Do now**
1. Check which tools you actually have (Node, Python, FFmpeg, cairo or another renderer, a scriptable browser,
   python-pptx, fontTools, git push access). Write the real list.
2. Create `implementation-plan.md`, `decision-log.md`, `implementation-log.md`, `handoff-state.md` from
   `course-playbook/templates/working-documents.md`. Put the scope table in the plan and mark it immutable.
3. In the plan, write the phase list (audit → outlines → engines → shell → pilot module → remaining modules
   one at a time → home intro film → QA and release) and the requirement crosswalk
   (requirement → task → deliverable → test).
4. Choose the pilot module (the one with the strongest existing material or the author's own) and say why.
5. List the questions that truly block work (scope, licences, publishing). Ask them in ONE message with a
   recommended answer each, then continue with everything that does not depend on them.

**Rules for the whole project**
- Engine first: every number shown anywhere comes from the course engine or a cross-checked reference.
- One module at a time to full depth; never all modules shallow.
- Keep the four working documents current; write `handoff-state.md` before every pause.
- Do not contact third parties, change repository settings, or publish unless the author said so.
- Report faithfully: skipped checks are "skipped", not "passed".
