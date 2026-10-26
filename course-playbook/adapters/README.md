# Using the playbook with different AI tools

The playbook is plain Markdown, so any tool can use it. The pattern is always the same:
**load `SKILL.md` as standing instructions → give the reference file(s) for the step → paste the step's prompt.**
Copy the whole `course-playbook/` folder into the new course's repository first.

## Claude Code

Either install it as a project skill:

```sh
mkdir -p .claude/skills && cp -r course-playbook .claude/skills/course-playbook
```

Claude Code picks up `SKILL.md` (its front matter has `name` and `description`) and loads it when the task
matches. Or keep the folder where it is and add one line to the repository's `CLAUDE.md`:

```markdown
When building or changing course content, films or pages, follow course-playbook/SKILL.md and its reference/ files.
```

Then run the prompts in `prompts/` one at a time.

## Claude.ai (web / desktop)

Zip the folder and upload it as a skill (Settings → Capabilities → Skills), or add `SKILL.md` and the
`reference/` files to a Project's knowledge. Paste a prompt from `prompts/` into the chat.

## OpenAI Codex (CLI / cloud)

Codex reads `AGENTS.md` at the repository root. Copy [`AGENTS.snippet.md`](AGENTS.snippet.md) into it
(or append it to an existing `AGENTS.md`). Then give Codex a prompt from `prompts/`.

## Cursor

Copy [`cursor-rule.mdc`](cursor-rule.mdc) to `.cursor/rules/course-playbook.mdc`. It tells Cursor's agent to
follow the playbook for course files. Use the prompts in Agent mode, one module at a time.

## Gemini CLI

Gemini CLI reads `GEMINI.md` at the repository root. Put the same text as `AGENTS.snippet.md` there.

## DeepSeek, Qwen, Kimi, ChatGPT and other chat models

1. Start a new chat. Paste `SKILL.md` as the first message (or the system prompt, if the tool has one) and
   say: "These are standing rules for this whole conversation."
2. Paste the reference file the step needs (each prompt names it), e.g. `reference/03-film-style.md` for films.
3. Paste the prompt from `prompts/`, filled in.
4. Chat models without file or code execution produce text and code; run the code yourself and paste back
   errors and test output. Keep `handoff-state.md` and paste it at the top of every new chat.

## Context-size tips

- `SKILL.md` is the only file every step needs. Reference files are per topic; give only the relevant one.
- One module per session. Resume from `handoff-state.md` instead of a long history.
- Point the agent at the reference repository's real files (engine, film script, lab) as worked examples;
  they show the rules in practice better than any summary.
