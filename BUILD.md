# BUILD.md: how to build this setup

Written for an agent. If you are an LLM asked to install, rebuild, repair or
extend this vault setup, read this file first, then `CONFIDENTIALITY.md`.

`install.sh` does the mechanical install. This file explains the intent behind
each piece, so you can rebuild it from nothing, port it to another machine, or
extend it without breaking the parts that make it work.

## What this is

A Karpathy style LLM wiki: raw sources in, an LLM compiled wiki out. Plain
markdown in a folder tree, read in Obsidian, maintained by Claude Code.

Three layers, and they are what everything else serves:

| Layer | Content | Who writes |
|---|---|---|
| Raw sources, immutable | `00-inbox/` for capture, then a `sources/` folder inside the owning project or area | Human, Web Clipper |
| The wiki, compiled | `03-resources/` primarily, plus `01-projects/` and `02-areas/` | The agent |
| The schema, config | the vault `CLAUDE.md` plus `.claude/commands/` | Both, co-evolved |

## The four invariants

Everything else is negotiable. These are not, because each one is a thing that
was broken and then fixed.

**1. The vault path is configured in exactly one place.**
`~/.claude/vault-path`, one absolute path, no trailing newline issues. The
consult guard, the link guard, the lint scanner and the backup script all read
it. When the vault moves, one file changes. Do not hardcode the path into a
script, and do not add an env var fallback: two sources of truth means one of
them is silently wrong.

**2. Consultation is enforced by a hook, not by instructions.**
A rule in `CLAUDE.md` saying "check the vault first" is followed most of the
time, and the failures are invisible: the model answers fluently from memory and
nothing indicates it skipped the vault. The `UserPromptSubmit` hook fires on
every prompt regardless, injects the directive, and surfaces ranked candidate
files. That difference (every turn, deterministically, versus most turns, at the
model's discretion) is most of what makes this setup work rather than decorate.

**3. The hook fails open, always.**
It never exits non zero, never blocks a prompt, and swallows every exception. A
context enrichment hook that can eat a prompt is worse than no hook. The one
thing it does loudly is warn when the vault path is missing or has not been
written to in 14 days, because a silently moved vault means every subsequent
answer is confidently sourced from a dead copy.

**4. Chat output uses absolute paths only.**
The client auto linkifies bare paths inside inline code, so a relative path in
backticks is a broken link exactly like a relative href. Relative paths are fine
inside vault files, where Obsidian's index resolves them. The `Stop` hook
enforces this and also catches absolute paths whose target does not exist, which
is the signature of a path the model recalled rather than verified.

## File inventory

```
vault-kit/
  README.md                     human entry point
  BUILD.md                      this file
  CONFIDENTIALITY.md            what reaches the API, and the aliasing convention
  install.sh                    idempotent installer
  vault/                        copied to the vault path, never overwriting
    CLAUDE.md                   the agent contract, the most important file here
    README.md                   human facing overview
    setup-guide.md              longer walkthrough
    log.md                      append only activity log
    .gitignore                  excludes 99-restricted/ from snapshots
    00-inbox/README.md
    01-projects/README.md, index.md
    02-areas/README.md
    03-resources/README.md
    04-archive/README.md
    daily/README.md
    99-restricted/README.md     what the quarantine does and does not do
    .claude/settings.json       vault scoped permissions
    .claude/commands/           daily, ingest-url, process-inbox, lint-wiki
  harness/                      copied to ~/.claude/
    CLAUDE.md                   global preferences, {{VAULT_PATH}} substituted
    settings.hooks.json         hook block, {{HOME}} substituted, merged in
    scripts/vault-consult-guard.py    UserPromptSubmit hook
    scripts/link-guard.py             Stop hook
    scripts/lint_wiki_links.py        deterministic link scanner
    scripts/vault_git_backup.sh       local only snapshot
```

## Build order

If you are rebuilding by hand rather than running `install.sh`, this order
matters: each step depends on the one before.

1. **Create the vault skeleton.** Copy `vault/` to the target path without
   overwriting existing files (`cp -Rn`). The READMEs are not decoration: they
   are how an agent orients in a folder it has not seen, and they carry the
   conventions that keep the tree from degenerating.
2. **Write `~/.claude/vault-path`.** Nothing downstream works until this exists.
3. **Install the scripts** into `~/.claude/scripts/` and make them executable.
4. **Install the global `CLAUDE.md`**, substituting `{{VAULT_PATH}}`. Back up
   any existing one rather than clobbering it.
5. **Merge the hook block** into `~/.claude/settings.json`. Merge, do not
   overwrite: that file holds model choice, permissions and plugin config that
   have nothing to do with this kit. Check for the hook command already being
   present so a second run is a no op.
6. **Verify.** Pipe a JSON prompt into the consult guard and confirm it emits
   the directive:
   ```bash
   echo '{"prompt":"what did we decide about the migration"}' | python3 ~/.claude/scripts/vault-consult-guard.py
   ```

## How the pieces work

### vault-consult-guard.py (UserPromptSubmit)

Extracts salient terms from the prompt (capitalised and long or digit bearing
terms rank first, because names, client codes and project identifiers are what
actually discriminate), walks the vault's markdown, and scores files.

Two ideas do the work:

- **IDF style pruning.** A term appearing in more than a quarter of the vault
  behaves like a stopword for this corpus and is dropped, no matter what the
  generic stopword list says. This is what stops every prompt surfacing the same
  eight files.
- **A signal floor.** A file is only surfaced if it matched a strong term, or at
  least three distinct terms together. Without this the tail is noise, and a
  noisy candidate list trains the reader to ignore the list.

Bounded by a 4 second walk budget and a 300 KB per file cap. `99-restricted/`
and dotfolders are never walked.

### link-guard.py (Stop)

Reads the last assistant message from the transcript, extracts path shaped
markdown hrefs and code spans, and blocks the turn if any is a vault relative
path or an absolute vault path that does not exist on disk. Blocking rather than
warning is deliberate: the corrected response is then the first one the human
sees.

### lint_wiki_links.py

Deterministic, read only, stdlib only, JSON to stdout. Owns broken and ambiguous
wikilink detection, orphans, stubs, convention warnings, code block stripping,
and data namespace exemptions. `/lint-wiki` runs it rather than re-deriving any
of it by hand, because hand derived link scans are where lint reports quietly
start lying.

Vault root from `argv[1]` if given, otherwise `~/.claude/vault-path`. Bump
`VERSION` on any change to scan scope or exclusion logic, so report counts stay
comparable run to run.

### The slash commands

`.claude/commands/` in the vault, so they only load when Claude Code runs from
the vault folder. Each is a procedure, not a hint: numbered steps, an explicit
review gate before applying anything, and a fixed output shape.

`/process-inbox` and `/lint-wiki` are self contained here. In the setup this kit
was extracted from they had grown into skills under `~/.claude/skills/`, which
is the right move once a procedure outgrows one file. If you extend them past
roughly 150 lines, promote them the same way.

## Extending it

- **New slash command**: add it to `vault/.claude/commands/`. Give it numbered
  steps, a review gate, and a defined output block. Say what it must never touch
  (`daily/`, filed `sources/`).
- **New hook**: add it to `harness/settings.hooks.json` and
  `harness/scripts/`. Keep the fail open contract. A hook that can block a
  prompt needs a much stronger justification than a hook that only adds context.
- **New folder convention**: it goes in the vault `CLAUDE.md` under structure
  conventions, and the owning folder's README. Both, or an agent that entered
  via the folder will not see it.
- **Do not** add a `sources/` scan to the lint scanner, add auto apply to the
  lint's judgment tier, or give any command permission to write to `daily/`.

## Confidentiality, in build terms

This vault is configured to hold client material. That decision is the owner's
and is not yours to relitigate, but it changes what you build:

- Filing operations apply the aliasing convention by default, at file time.
  Redaction happens in `/process-inbox`, because that is where unredacted
  captures first get touched.
- `99-restricted/` is excluded from the hook walk, from git and from the lint
  scanner. It is a policy marker, not a control, and the docs say so plainly in
  three places. Do not "improve" them into implying it is a control.
- The backup script is local only and has no remote. Do not add one.

Full reasoning in `CONFIDENTIALITY.md`. Read it before writing anything that
files, copies, syncs or backs up vault content.
