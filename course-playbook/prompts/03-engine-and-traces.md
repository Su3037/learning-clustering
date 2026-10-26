# Prompt 03 · Engine, reference and traces

---

Implement the algorithm for **{{Module NN · topic}}** so that one engine drives the lab, the challenges, the
film traces and the tests. Reference files: `site/engines/kl.js`, `python/m07-kernighan-lin/reference.py`,
`scripts/build-traces.mjs`, `tests/engines.test.mjs`, `tests/crosscheck.py`.

1. **JS engine** `site/engines/{{algo}}.js` (ES module, no dependencies, runs in browser and Node):
   - `validate(input)` → list of errors.
   - `run(input, options)` → `{ events, result, status }`. Events are fine-grained (each candidate list,
     trial, commit, lock, rollback, round end) and carry the numbers a learner needs to see.
   - Options cover the variants the lesson discusses (order, tie rule, sync/async, seed, limits).
   - Tie rule and stop reasons are explicit fields. Distinguish every outcome (stable, cycle, limit,
     infeasible, stuck, suboptimal…).
2. **Python reference** `python/{{id}}/reference.py`, standard library only (declare NumPy if needed), written
   independently from the description.
3. **Cross-check** both, step by step, on the course examples and on random inputs.
4. **Tests**: regression values from the outline's acceptance numbers; properties on ~300 random inputs;
   one regression per source error you fixed; exhaustive oracle where cases are small.
5. **Traces**: add the module to `scripts/build-traces.mjs` so `site/data/{{id}}/traces.json` holds the runs
   the films and slides need (main example, variants, counterexamples).

Done when: all tests pass, the cross-check passes, and every acceptance number in `module.md` is confirmed
(update the outline if the engine shows a number was wrong, and record it in the decision log).
