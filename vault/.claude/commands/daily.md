---
description: Scaffold today's daily log entry in daily/YYYY-MM-DD.md
---

You are helping maintain an append only daily log.

1. Determine today's date as `YYYY-MM-DD` (use `date` in bash).
2. Check whether `daily/<today>.md` exists.
   - If it does, open it and report what is already there. Do not overwrite.
   - If it does not, create it with this scaffold:

```markdown
# <YYYY-MM-DD>, <Day name>

## Plan
- 

## Log


## Decisions


## Captures
- 

## Links to today's inbox notes

```

3. Show the path to the new file and remind: "Append through the day. Do not
   edit yesterday's entry."
4. If `daily/<yesterday>.md` exists, summarise it in one paragraph.

Never write anything else into `daily/`. Reports go to
`02-areas/claude-code/reports/`.
