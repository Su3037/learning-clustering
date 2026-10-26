# 07 · Lessons learned

Things that went wrong or were rejected while making Learning Clustering and the author's earlier Label
Propagation film. Read this before starting; each item cost at least one rework cycle.

## Creative direction

- **Bright flat illustration** (cream and sage, cartoon readers, a library) had acceptable rhythm but did not
  feel like a science film. Rejected.
- **Photorealistic generated rooms and chips** felt too real and turned films into slow pans over pictures.
  Rejected.
- **The old dark film** was liked for its atmosphere but disliked for repetition: the same five-node graph,
  similar pictures, the same motion for minutes. Keep the darkness, not the repetition.
- **Forced analogies** (sharing books in a library for label propagation) were called uninteresting and
  logically weak. A concrete, surprising problem is better than an analogy that does not match the mechanism.
- **Generic hooks**: opening every chapter with "what is clustering" was repetitive. Each chapter's hook must
  be about its own algorithm; the field's background is told once on the home page.
- **"Too much popular science"**: a single story film per chapter was not enough for learners who want the
  algorithm itself. Hence concise + advanced + walkthrough alongside the story.
- **Heavy typography**: bold sans headings, pills and boxes looked crowded. Light serif, mono eyebrows,
  hairlines and space looked elegant.
- **Labels by code only** (M02–M09) confused readers. Always show the method's name.

## Music

- The author chose the exact recording (a specific upload of "We Never (Remix)"). Do not substitute a similar
  track, slow it down, or recreate it. Keep the original speed.
- An estimated BPM grid is not a musical analysis. Use measured onsets and listen for phrases, entries,
  silences and the ending; place meaningful events on them.
- Never claim third-party music is covered by the course licence or offer it as a download.

## Process

- **Approving a description is not approving a film.** Show stills and a short real cut before a full render.
- **Doing all chapters at once made them shallow.** Pilot one, then one at a time.
- **Stale docs**: README and site text described a rejected draft as finished. Update every duration, claim
  and link to match what was actually exported.
- **Renderer/storyboard drift**: a storyboard was updated while the renderer still drew the old style.
  Never assume a renderer matches a new plan; check stills.
- **Pushing was blocked** for a while (the GitHub App was not installed on the repo). Work continued locally
  and was delivered as a git bundle; the author installed the app later. Check write access early.
- **Large repo**: eight modules × seven videos is ~600 MB. Fine for Pages, but plan for it.
- **Title text that states a length** ("two-minute film") breaks when the film runs 2:33. Avoid stating
  durations inside films or titles.

## Correctness

- Source submissions contained real algorithm errors (string comparison of arrays, a hill climb sold as FM,
  a missing −2w, stored eigenvectors presented as live). Audit before animating.
- Reconstructed data (a DAG recovered from a video) is labelled "candidate reconstruction" everywhere it
  appears, with its tie rule marked as an assumption.
- Topic/mapping questions that only the instructor can answer (is Lab 09 Multilevel or Rajaraman–Wong?) are
  shown as "pending confirmation" on the page, not silently resolved.
- Ambiguous teacher keywords ("jump", "speed", "tts") are interpreted, recorded as interpretations, and not
  turned into invented quotations.
