# Release checklist

- [ ] Full rebuild: traces → challenge index → pages → code-lab data → font subset → downloads
- [ ] `node --test tests/*.test.mjs` all pass
- [ ] Cross-check passes; every `check.py reference.py` passes; starters INCOMPLETE
- [ ] Only intended files changed (generated timestamps and zips do not churn needlessly)
- [ ] README, build docs, credits, licence notes and completion report match what ships
- [ ] `handoff-state.md` updated
- [ ] Third-party audio, credentials, private research material not in the commit
- [ ] Release path the author approved (PR, or merge to `main`); a saved branch/tag of the previous version exists for big changes
- [ ] CI green (tests gate deploy)
- [ ] Live site checked: home and one module in both languages, fonts load (200), films play and seek, lab steps, code lab loads Python
- [ ] Summary to the author: what changed, link, what was verified live vs locally, decisions made, anything they need to do
