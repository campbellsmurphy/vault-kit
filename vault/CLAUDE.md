# CLAUDE.md: agent schema for this vault

This is a Karpathy style LLM Wiki: raw sources in, an LLM compiled wiki out. You
(the LLM) do the filing, cross referencing and bookkeeping. The human curates
sources, asks questions, and reads the result in Obsidian.

Read this file first. It is the operating contract. `README.md` is the human
facing version, `setup-guide.md` is the longer walkthrough.

## The three layers

| Layer | Karpathy's model | Here | Who writes |
|---|---|---|---|
| **Raw sources** (immutable) | `raw/` | `00-inbox/` for capture, then filed to a `sources/` folder inside the destination project or area | Human, Web Clipper |
| **The wiki** (compiled) | `wiki/` | `03-resources/` primarily, plus `01-projects/`, `02-areas/`, `04-archive/` | Mostly you |
| **The schema** (config) | `AGENTS.md` | this file plus `.claude/commands/` | You and the human, co-evolved |

Filed source files (anything under `sources/`: exports, transcripts, invoices,
PDFs) are read only fidelity to source. Never edit them. `daily/` is append only
(the human's log). Never rewrite it. Everything else, you maintain.

## Where things live

- `00-inbox/` is the ONLY capture point. Everything gets dumped here first
  (notes, Web Clipper output, attachments, exports). The agent does all the
  filing. Drain it via `/process-inbox`, never leave processed items behind.
- `01-projects/` is active work, one folder per project. Each has an `index.md`
  carrying `status:` frontmatter. Finished or abandoned projects move to
  `04-archive/` as is.
- `02-areas/` is ongoing responsibilities with no end date, one folder per area.
- `03-resources/` is the compiled wiki, organised as `topics/<topic>/`.
- `04-archive/` is done projects and retired areas.
- `99-restricted/` is the quarantine. See Confidentiality below.
- `daily/` is the human's journal only. Agents never write here. Reports go to
  `02-areas/claude-code/reports/`.
- `log.md` is the append only operation log. See Logging below.

## Confidentiality: read this before writing anything

**This vault holds client material.** That is a deliberate decision by its
owner, and it changes how you behave, not whether the material is here.

**What that means mechanically.** The slash commands read vault contents and
ship them to an LLM API. The `UserPromptSubmit` consult guard hook does the same
on every single prompt, unprompted. There is no read of this vault that stays on
the machine. Assume anything filed here has been sent to a model.

**The aliasing convention, applied by default when you file.** Do not wait to be
asked:

- Client entities get an alias on first use and the alias thereafter: `Client A`,
  `Client B`. Keep the alias mapping in `99-restricted/client-aliases.md`, never
  in the open vault.
- Strip identifiers that survive aliasing: ABNs, ACNs, contract numbers, deal
  code names, account numbers, exact dollar figures where the figure alone
  identifies the deal, and named individuals at the client.
- Keep what makes the note useful: the methodology, the issue, the reasoning,
  the decision, the pattern you want to find again in two years.
- If a note cannot be written usefully without identifying detail, it belongs in
  `99-restricted/`, not in the open vault.

**`99-restricted/` is excluded from the consult guard hook's walk and from git.**
Understand precisely what that does and does not do:

- It DOES mean the hook will never surface those files as candidates, so they do
  not leak into context by accident on an unrelated question.
- It DOES mean they are not committed to the local snapshot repo.
- It DOES NOT mean you cannot read them. You can, if the human explicitly points
  you at a file in there. The folder is a policy marker and a speed bump, not a
  technical control.
- It DOES NOT make the material safe to send to a model. If the human asks you
  to read something in `99-restricted/`, that content goes to the API like
  anything else. Say so once, then do as asked.

**Standing checks.** Before filing anything derived from client work, ask
yourself: could this note, read by someone outside the firm, identify the client
or disclose their confidential information? If yes, alias it or restrict it. If
you are unsure, ask rather than filing.

**Never propose lifting the restriction.** Whether a given piece of material can
be in this vault at all is the owner's call against their firm's policy and the
engagement terms. Not yours, and not something to relitigate each session.

## Structure conventions

- **Sources**: file source material into a `sources/` folder inside the owning
  project or area. Filed sources are immutable.
- **Binaries** (PDFs, images, exports) live next to the pages that cite them.
  They cost zero tokens until deliberately opened and do not slow text search.
  Do not centralise them.
- **Linking local files** (PDFs, CSVs, images, notes): always use Obsidian
  wikilinks `[[filename.ext|label]]` by basename, never markdown relative path
  links `[label](sub/dir/file.ext)`. Wikilinks resolve via Obsidian's index
  regardless of folder depth or machine, and auto update on move or rename.
  Markdown relative paths resolve inconsistently and silently break. Keep the
  extension for data files (`[[figures.csv]]`), drop it for notes
  (`[[some-note]]`). External URLs stay normal markdown links.
- **Names**: kebab-case for wiki pages you create. Clipped or exported files
  keep their original names. Prefer `YYYY-MM-DD` prefixes for dated artefacts.
- **Frontmatter**: keep YAML frontmatter (tags, dates, status) on wiki pages.
- Each project, area and topic folder carries its own `index.md`. Update it when
  you add or move pages in that folder. Indexing is per folder, not one global
  catalogue.

## Hard rules

- **Navigate by `index.md` first, treat search as the fallback.** Before
  reaching for a search or a blind grep, read the relevant `index.md` files:
  start at the top level area or project index and walk down. Index files are
  curated navigation hubs and are far more reliable than search, which returns
  zero matches for questions whose subject matter is thoroughly documented,
  because the query phrasing does not match the vault's actual vocabulary.
  Search is for when you already know the vocabulary.
- **Never write to `daily/`.** It is the human's journal. Reports go to
  `02-areas/claude-code/reports/`.
- **Never edit filed source files.** Anything under `sources/` is evidence.
- **No em dashes or en dashes in anything you write**, here or in chat. Use
  commas, full stops, colons or brackets, and rewrite the sentence if none fit.
  Ordinary hyphens in compound words and list markers are fine.
- **Do not fabricate.** Unknowns are `TBC`. If the vault does not have a figure,
  a date or a name, ask. Do not estimate it into existence.
- Cross reference with `[[wikilinks]]`. The graph is the value.

## Operations

Each has a slash command. Use it, do not improvise.

- **Ingest**: `/ingest-url <url-or-inbox-path>`. Fetch or read a source, compile
  it across the wiki (5 to 15 pages), file the source into the destination's
  `sources/`, update the relevant `index.md` files.
- **Process inbox**: `/process-inbox`. Classify every capture, apply confirmed
  corrections to the owning pages, file sources, drain the inbox, log the pass.
- **Lint**: `/lint-wiki`. Broken `[[links]]`, orphans, stubs, contradictions,
  stale claims, gaps. Refresh indexes. Writes a dated report.
- **Daily**: `/daily`. Scaffold today's `daily/YYYY-MM-DD.md`.

**Filing query outputs back in**: when a query produces something worth keeping
(a comparison, an analysis, a synthesis), file it as a wiki page so explorations
compound, exactly like an ingested source.

## Logging

After any ingest, process-inbox or lint pass, append one line to `log.md` at the
vault root using the format documented there:
`## [YYYY-MM-DD] <op> | <detail>`. It is the append only timeline of what has
been done to the wiki, and the one place to see its evolution at a glance.
