---
description: Health check the vault: broken links, orphans, stubs, stale indexes, contradictions. Writes a dated report.
---

You are running the vault lint. It is read heavy and write light: propose fixes,
get sign off, then apply.

## 1. Run the scanner first

```bash
python3 ~/.claude/scripts/lint_wiki_links.py
```

Deterministic, read only, JSON to stdout. It owns the mechanics of checks 1 to
3: broken and ambiguous wikilinks, convention warnings, orphans, stubs, data
namespace exemptions, code block stripping. **Never re-derive these by hand.**
Run it and interpret the JSON. Pass a vault path as the first argument to point
it somewhere other than the configured vault.

## 2. Mechanical triage

Sort the findings into two tiers:

- **High confidence**: a broken link with exactly one plausible target. Propose
  the concrete fix.
- **Judgment**: no match, several candidate targets, or a convention warning.
  Never resolve an ambiguous link by guessing. Ask.

Remedies:

- **Broken links**: re-target when the intended file is identifiable, otherwise
  rename or remove.
- **Convention warnings**: report once per file, not once per occurrence.
- **Orphans**: suggest one to three places an inbound link belongs.
- **Stubs**: flag expand or delete. Do not decide.

## 3. Editorial checks

- **Index freshness.** Every project and area folder has an `index.md` that
  lists its current pages and states current status. Flag any that are stale
  against the folder's actual contents.
- **Contradictions.** Two pages asserting different things about the same fact.
  Quote both sides. The human arbitrates. Never silently pick a winner.
- **Stale claims.** A statement true as at its date but likely overtaken. Flag
  it with its date rather than rewriting it.
- **Gaps.** A topic referenced repeatedly with no page of its own.
- **Confidentiality drift.** Any page in `03-resources/` carrying client
  identifying detail, any un-aliased client name in the open vault, any wikilink
  pointing into `99-restricted/`. These are defects, report them at the top.

## 4. Review gate

Present everything in one message: proposed fixes by tier, contradictions with
both quotes, editorial flags. Apply nothing yet. Unknowns stay `TBC`, never get
a fabricated resolution.

## 5. Apply approved fixes

One batched pass. Then re-run the scanner and confirm the broken count is zero,
or explain exactly what remains and why.

Never edit `daily/`, `00-inbox/`, or anything under a `sources/` folder.

## 6. Report

Write `02-areas/claude-code/reports/<YYYY-MM-DD>-lint-report.md` (append `-2` for
a second run the same day). Sections in this order: summary counts,
confidentiality drift, broken links, ambiguous links, orphans, stubs, index
freshness, contradictions, stale claims, gaps, applied fixes, open items.

Open the report with the scanner's `VERSION` so run to run deltas stay
comparable.

Append one line to `log.md`, then end with: "Run `/lint-wiki` again after
addressing the high priority items."

## Tone

Specific and actionable. Do not pad the report with process narration. The body
reports the vault's state, not the lint's own existence.
