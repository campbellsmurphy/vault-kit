# log.md: wiki activity log

Append only, chronological record of what has been done to the wiki: ingests,
inbox passes, lint runs, notable queries filed back. Newest entries at the
bottom.

**Format.** One entry per line, consistent prefix so it is greppable with plain
tools:

```
## [YYYY-MM-DD] <op> | <detail>
```

`<op>` is one of `ingest`, `process-inbox`, `lint`, `query`, `meta`. Examples:

- `## [2026-04-02] ingest | "Attention Is All You Need" -> 03-resources/topics/transformers/ (8 pages touched)`
- `## [2026-04-03] lint | fixed 3 broken links, flagged 1 contradiction in 02-areas/methodology/`

Quick reads: `grep "^## \[" log.md | tail -5` for the last five, or
`grep "ingest" log.md` for all ingests.

---
