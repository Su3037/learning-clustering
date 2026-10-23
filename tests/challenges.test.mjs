// Every challenge must accept its official answer and reject at least one plausible wrong answer.
// Answers are written in the same shape the page controls produce (choice → value, fields → object,
// orderList → array, combine → array of parts, graphPick edges → ['C|D', ...]).
import test from 'node:test';
import assert from 'node:assert/strict';

const CASES = {
  'm02-affinity-metrics': {
    c1: ['rank', 'groups'], c2: [{ score: 2, x: 'C' }, { score: 0, x: 'C' }], c3: [{ direct: 1, via: 4, total: 5 }, { direct: 1, via: 5, total: 6 }],
    c4: [['XY', 'PQ'], ['XY', 'XY']], c5: [['A–B', 'D–E', 'B–C', 'C–D', 'A–C', 'C–E'], ['D–E', 'A–B', 'B–C', 'C–D', 'A–C', 'C–E']],
    c6: [{ w: 9 }, { w: 8 }], c7: [{ raw: 2, ab: 0.5, ef: 1 }, { raw: 2, ab: 2, ef: 1 }]
  },
  'm03-greedy-pair-merge': {
    c1: ['AB', 'AC'], c2: [[{ aff: 5 }, 'ABC'], [{ aff: 4 }, 'ABC']], c3: [['C|D', 'C|E'], ['C|D']], c4: [[{ n: 3, cut: 8 }, 'no'], [{ n: 2, cut: 3 }, 'yes']],
    c5: ['m1', 'm5'], c6: [['RS', 'QRS'], ['PQ', 'QRS']]
  },
  'm04-size-constrained-agglomerative': {
    c1: [['cy', 'tn'], ['cn', 'tn']], c2: ['DE', 'ABC'], c3: [[{ lb: 3 }, 'no'], [{ lb: 2 }, 'yes']], c4: [['greedy-stuck', { g: 'AC|BD' }], ['infeasible-by-bound', { g: 'AC|BD' }]],
    c5: [{ greedy: 18, best: 11 }, { greedy: 18, best: 18 }], c6: [{ g: 'AB|CDE', cut: 5 }, { g: 'ABC|DE', cut: 3 }]
  },
  'm05-label-propagation': {
    c1: ['label', 'rename'], c2: [{ B: 5, D: 2, E: 1 }, { B: 2, D: 2, E: 1 }], c3: [{ rounds: 2, cut: 3 }, { rounds: 1, cut: 3 }],
    c4: [['sync', 'cycle'], ['sync', 'stable']], c5: [{ g: 'AB|CDE', cut: 5 }, { g: 'ABC|DE', cut: 3 }], c6: [['same', { rounds: 3 }], ['diff', { rounds: 3 }]]
  },
  'm06-spectral-bisection': {
    c1: [{ row: '6,-5,-1,0,0' }, { row: '6,5,1,0,0' }], c2: [[{ k2: 3, k3: 5 }, '2'], [{ k2: 3, k3: 5 }, '3']], c3: [{ n: 15 }, { n: 16 }],
    c4: [{ single: 6, best: 3 }, { single: 6, best: 6 }], c5: [['same', { cut: 3 }], ['diff', { cut: 3 }]], c6: [[{ l2: 0 }, 'comp'], [{ l2: 0 }, 'strong']]
  },
  'm07-kernighan-lin': {
    c1: [{ A: 6, D: 3 }, { A: 6, D: 5 }], c2: [['AD', { g: 9 }], ['ED', { g: 9 }]], c3: [['go', { cut: 11 }, 'no'], ['stop', { cut: 3 }, 'acc']],
    c4: [{ k1: 1, k2: 0 }, { k1: 2, k2: 0 }], c5: [[{ g: -1 }, 'twice'], [{ g: 9 }, 'none']], c6: [{ cut: 8, g: 5 }, { cut: 12, g: 9 }]
  },
  'm08-fiduccia-mattheyses': {
    c1: [['D', 'bal'], ['A', 'bal']], c2: [{ fs: 5, te: 2, g: 3 }, { fs: 5, te: 0, g: 5 }], c3: [{ k: 2, cut: 3 }, { k: 5, cut: 12 }],
    c4: [[{ cut: 18, gE: 10 }, 'legal'], [{ cut: 9, gE: 10 }, 'legal']], c5: [{ hill: 6, fm: 4 }, { hill: 6, fm: 6 }], c6: [{ a: 0, d: 3 }, { a: -1, d: 3 }]
  },
  'm09-rajaraman-wong': {
    c1: ['delay', 'cut'], c2: [{ one: 7, two: 10 }, { one: 5, two: 6 }], c3: [{ b: 3, all: 20 }, { b: 1, all: 12 }],
    c4: [{ l1: 4, l2: 7, l: 7 }, { l1: 4, l2: 4, l: 4 }], c5: [{ rw: 8, nr: 10 }, { rw: 8, nr: 8 }], c6: [['rep', 'tie'], ['rep', 'teacher', 'tie']]
  }
};

for (const [moduleId, cases] of Object.entries(CASES)) {
  test(`${moduleId}: every challenge accepts its answer and rejects a wrong one`, async () => {
    const { challenges } = await import(`../site/modules/${moduleId}/challenges.js`);
    assert.deepEqual(challenges.map(c => c.id).sort(), Object.keys(cases).sort(), 'test covers every challenge');
    for (const c of challenges) {
      const [right, wrong] = cases[c.id];
      const ok = c.check(right), no = c.check(wrong);
      assert.equal(ok.ok, true, `${moduleId}/${c.id} should accept ${JSON.stringify(right)}: ${ok.message}`);
      assert.equal(no.ok, false, `${moduleId}/${c.id} should reject ${JSON.stringify(wrong)}`);
      assert.ok(no.message && no.message.length > 4, `${moduleId}/${c.id} explains the rejection`);
      assert.equal(c.hints.length, 2);
    }
  });
}
