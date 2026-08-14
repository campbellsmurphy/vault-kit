---
description: Fetch a URL (or read a local source file), then compile it into the wiki across multiple pages
argument-hint: <url-or-inbox-path>
---

You are ingesting a source into the wiki.

## Input

Either:

- A URL: fetch it (WebFetch), save the cleaned markdown to `00-inbox/<slug>.md`,
  and file it into the destination project or area's `sources/` folder as part
  of the ingest.
- A local path (something in `00-inbox/`): read it directly, then file it the
  same way.

If WebFetch cannot reach the domain, ask for the page to be clipped with
Obsidian Web Clipper into `00-inbox/`, then re-run against the local path.

## Scope

Read the existing structure of `03-resources/` before writing anything, so new
material lands in the topic folders that already exist rather than duplicating
them under a new name.

## Compilation pass

This is the core of the method: **one ingest touches 5 to 15 pages.**

1. **Identify topics.** What 1 to 4 topics does this source primarily cover? Map
   each to an existing `03-resources/topics/<topic>/` folder, or propose a new
   topic folder.
2. **For each topic:**
   - Find the topic level `index.md`, or create one.
   - Find existing pages on the sub concepts.
   - **Update them** with new claims, examples or counterpoints from the source.
   - **Create new pages** for sub concepts that do not yet exist.
   - Every page touched ends with a `Sources:` section listing the URLs and
     source file paths it draws from. Append, do not replace.
3. **Cross link.** Add wikilinks between every newly touched page and 2 to 5
   related existing pages, bidirectional where it makes sense.
4. **Update topic indexes.** Each `topics/<topic>/index.md` gets a current TL;DR
   and a list of its pages, ordered roughly by importance.

## Confidentiality

If the source is internal or client material rather than a public document,
apply the aliasing convention in the vault `CLAUDE.md` as you compile, and file
the original into the project's `sources/` folder rather than `03-resources/`.
Topic pages stay free of client identifying detail entirely.

## Output

- A diff summary: pages created, pages updated, links added.
- Any contradictions between the new source and existing pages. Flag them, do
  not silently overwrite.
- One or two suggested follow up sources.
- One line appended to `log.md`.

## Quality bar

Every page reads as a standalone note. No "see source for details" hand waves.
If a claim is in the wiki, the wiki explains it.
