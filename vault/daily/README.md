# daily/

**Append only daily log.** One file per day, named `YYYY-MM-DD.md`.

This is the "human memory" pattern: a flat, dated log of what you did, thought,
learned and decided. You write to it through the day, never edit yesterday, and
let the agent build a graph on top of it later.

Agent written reports (lint, sweeps, triage) do **not** live here. They go to
`02-areas/claude-code/reports/`. This folder is yours alone.

## What goes in

- Things you did (meetings, calls, work shipped)
- Things you decided, and why
- Quick thoughts and open questions
- Links to inbox notes you captured today
- Anything in the "later me will want to find this" category

## What does not

- Long form writing. That is a real note in `01-projects/` or `03-resources/`.
- Anything that cannot be aliased. See the vault `CLAUDE.md`.

## Conventions

- New entry every morning or evening. Run `/daily` to scaffold today's file.
- Do not backfill. Yesterday is yesterday.
- Timestamp entries when it helps: `09:14 kicked off the controls walkthrough`.
