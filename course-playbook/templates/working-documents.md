# Working document templates

Copy each block into its own file at the course repository root.

## implementation-plan.md

```markdown
# Implementation plan: {{course}}

Updated: {{date}}. Reference sources: {{paths / links}}.

## 1. Scope (immutable)
| Display | id | Topic | Source | Author | Notes |
| --- | --- | --- | --- | --- | --- |

Not in scope: {{…}}

## 2. Tools actually available (checked {{date}})
| Need | Tool | Version / note |
| --- | --- | --- |

## 3. Architecture and contracts
{{site tree, engine interface, event schema, progress schema, film.json schema}}

## 4. Phases
1. Audit … 8. QA and release (pilot: {{module}}, because {{reason}})

## 5. Requirement crosswalk
| Requirement | Task | Deliverable | Test / check |
| --- | --- | --- | --- |
```

## decision-log.md

```markdown
# Decision log

Format: id · decision · reason · source · can it change. Mark explicit author/teacher requirements as such;
everything else is a design choice.

## Scope
- **D-SCOPE-1** …
## Tech
- **D-TECH-1** …
## Media
- **D-MEDIA-1** …
## Pending (non-blocking)
- …
```

## implementation-log.md

```markdown
# Implementation log

## {{date}} · {{what}}
- Did: …
- Commands: `…` → result
- Measured: …
```

## handoff-state.md

```markdown
# Handoff state

Updated: {{date}}. Branch: {{…}}. Last commit: {{…}}.

## Done
## In progress (exact next action)
## Author decisions so far
## How to continue (commands)
## Do not do
```
