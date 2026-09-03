# vault-kit

The infrastructure for a Karpathy style LLM wiki, with none of the content.

Plain markdown in a folder tree, read in Obsidian, maintained by Claude Code.
This repo is the scaffolding: the folder skeleton, the agent contract, the slash
commands, the two hooks that make the setup work, and the documentation that
explains it to the next agent.

**It contains no personal or work data.** Every note is a README, a convention,
or a procedure. The skeleton is empty by design.

## Install

```bash
git clone https://github.com/campbellsmurphy/vault-kit ~/code/vault-kit
cd ~/code/vault-kit
./install.sh ~/vault          # or wherever the vault should live
```

Idempotent and non destructive. Existing vault files are never overwritten,
`~/.claude/CLAUDE.md` and `~/.claude/settings.json` are backed up before they
change, and the hook block is merged into settings rather than written over it.
Run it twice and the second run is a no op.

Then:

```bash
cd ~/vault && claude
```

You should see `/daily`, `/process-inbox`, `/ingest-url` and `/lint-wiki`.

## What gets installed

**Into the vault path:**

- The folder skeleton (`00-inbox/`, `01-projects/`, `02-areas/`,
  `03-resources/`, `04-archive/`, `daily/`, `99-restricted/`), each with a
  README carrying its conventions.
- `CLAUDE.md`, the agent contract. The most important file in the vault.
- `README.md` and `setup-guide.md`, the human facing docs.
- `log.md`, the append only activity log.
- `.claude/commands/`, the four slash commands.

**Into `~/.claude/`:**

- `vault-path`, one absolute path, the only place the vault location is
  configured.
- `CLAUDE.md`, global preferences.
- `scripts/vault-consult-guard.py`, the `UserPromptSubmit` hook.
- `scripts/link-guard.py`, the `Stop` hook.
- `scripts/lint_wiki_links.py`, the deterministic link scanner.
- `scripts/vault_git_backup.sh`, local only snapshots.
- The hook wiring, merged into `settings.json`.

## The bit that matters

The consult guard hook. It fires on **every prompt**, injects a mandatory
directive to consult the vault, and surfaces ranked candidate files from it.

Without it, "check the vault first" is an instruction in a preferences file that
gets followed most of the time, and the failures are invisible: the model
answers fluently from memory and nothing tells you it never looked. With it, the
vault is consulted deterministically, every turn, in every session type
including headless.

Everything else in this repo is scaffolding around that.

## Documentation

| File | For | Covers |
|---|---|---|
| `README.md` | you | this |
| `BUILD.md` | an agent | intent, invariants, build order, how each piece works, how to extend it |
| `CONFIDENTIALITY.md` | you, first | what actually reaches the API, the aliasing convention, what the quarantine folder does and does not do |
| `vault/CLAUDE.md` | an agent | the operating contract for the vault itself |
| `vault/setup-guide.md` | you | Obsidian settings, Web Clipper, verification, troubleshooting |

If you are an agent asked to install, repair or extend this: read `BUILD.md`,
then `CONFIDENTIALITY.md`, before touching anything.

## Read this before putting anything in it

This vault is configured to hold client material. Three separate mechanisms send
its contents to an LLM API, one of which runs on every prompt without being
asked. `CONFIDENTIALITY.md` sets out exactly what is exposed, the aliasing
convention that keeps most of the value while reducing the exposure, and the
questions about firm policy and engagement terms that this kit deliberately does
not answer for you.

## What is deliberately not here

- Any note content, from any vault.
- Machine specific config: device IDs, MCP servers, credentials, launchd jobs.
- The skills layer. `/process-inbox` and `/lint-wiki` are self contained
  commands here. Promote them to skills if they outgrow one file.
- A git remote on the backup script. Local only, on purpose.
