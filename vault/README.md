# Vault: a Karpathy style LLM wiki

A second brain in plain markdown. **Obsidian is the reader. Claude is the
maintainer.**

You write fast and rough into `daily/` and `00-inbox/`. The agent files,
cross references, and compiles topic pages into `03-resources/`. You read the
result in Obsidian's graph view.

## The folders

| Folder | Purpose | Who edits |
|---|---|---|
| `daily/` | Append only daily log, one file per day | You |
| `00-inbox/` | Capture zone: fleeting notes, links, Web Clipper output, attachments | You write, agent files |
| `01-projects/` | Active work with an outcome and a deadline | You and agent |
| `02-areas/` | Ongoing responsibilities, no deadline | You and agent |
| `03-resources/` | Topic organised reference material, the wiki itself | Mostly agent |
| `04-archive/` | Done projects, retired areas | You move things in |
| `99-restricted/` | Quarantine for material that must not be surfaced automatically | You |

Each folder has its own README explaining its conventions. Read them.

## The daily workflow

**Morning.** Run `/daily` to scaffold today's log. Skim yesterday's, glance at
`01-projects/`.

**Throughout the day.** Append to `daily/YYYY-MM-DD.md`. Drop fleeting captures
into `00-inbox/`. Web Clipper sends articles there too.

**Every few days.** Run `/process-inbox`. The agent classifies each inbox note,
proposes a destination, and asks before moving.

**On demand.** Run `/lint-wiki`. Finds broken links, orphan pages,
contradictions, gaps. Updates each project and area `index.md`.

**Whenever.** Run `/ingest-url <url>`, or point it at an `00-inbox/` file. The
agent compiles it into the wiki across 5 to 15 pages.

## Confidentiality

Everything in this vault gets read by an LLM. The slash commands ship folder
contents to one, and the `UserPromptSubmit` hook does the same on every prompt
whether you asked it to or not. There is no read of this vault that stays on
this machine.

This vault is configured to hold client material, which makes that fact load
bearing rather than incidental. Before you put anything in it, read `CLAUDE.md`
in this folder (the "Confidentiality" section) and the kit's
`CONFIDENTIALITY.md`. The short version: alias client entities by default, strip
identifiers that survive aliasing, and put anything that cannot be written
usefully without identifying detail into `99-restricted/`.

## What this is not

- Not Zettelkasten. There are no atomic note rules.
- Not PARA by the book. The folders are inspired by it, but the agent's
  compilation is what gives the system its leverage.
- Not "AI only". You still write. The agent's job is the boring part: filing,
  cross referencing, keeping the index current.

## First run checklist

1. Open this folder in Obsidian, via "Open folder as vault".
2. Settings, then Files and links, then set the default location for new
   attachments to `00-inbox/`.
3. Install the Obsidian Web Clipper browser extension and point it at
   `00-inbox/`.
4. Install Claude Code and `cd` into this vault before running slash commands.
5. Read `setup-guide.md` in this folder for the longer walkthrough.

## Top level maps

- [[01-projects/README|Projects]]
- [[02-areas/README|Areas]]
- [[03-resources/README|Resources]]
- [[04-archive/README|Archive]]
