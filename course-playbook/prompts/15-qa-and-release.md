# Prompt 15 · QA, report and release

---

Bring **{{module or course}}** to release. Use `course-playbook/checklists/module-acceptance.md`,
`film-review.md` and `release.md`, and `reference/06-quality-and-tests.md`.

1. Rebuild everything: traces → challenges index → pages → code-lab data → font subset → downloads.
2. Run all tests: Node tests, cross-check, every Python reference against its checker, starters INCOMPLETE.
3. Browser pass under the project subpath, both languages, desktop and 375 px: every section renders, lab
   steps with arrows, code lab runs, challenges check, slides deep links, films play and seek, no console
   errors, storage-failure mode.
4. Films: reading violations 0, durations and chapters match `film.json`, posters, VTT, faststart.
5. Docs: README, build docs, credits and licence notes match what is actually shipped (no stale durations or
   claims). Update `handoff-state.md`.
6. Write the completion report from `templates/completion-report.md`: deliverables with counts, commands and
   real results, fixed source errors, media table, limitations and unchecked items, open questions.
7. Release only as the author allowed: branch + PR, or merge to `main`. CI must be green; then verify the live
   site (fonts 200, films, code lab) and say what was verified live versus locally.
