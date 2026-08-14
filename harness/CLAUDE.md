# Claude Code global preferences

Machine-wide instructions, applied in every project on this machine.

Keep this file short. Bloat is the failure mode: a 500 line preferences file is
read less carefully than a 100 line one, and the rules that matter get diluted
by the ones that do not.

## Vault first: mandatory context check (hook enforced)

The vault at `{{VAULT_PATH}}` is the canonical record of my work: engagements,
clients, projects, decisions, meetings, people, and the conventions I work by.

**Rule:** before answering any question that could plausibly relate to my work,
my projects, my clients, my colleagues, or anything I have written down, search
the vault and read the relevant files first. Do not answer from memory or
assumption when the vault may hold the real context. When unsure whether it is
relevant, search. Only skip when the question is clearly generic.

This is reinforced deterministically on every prompt by the `UserPromptSubmit`
hook `~/.claude/scripts/vault-consult-guard.py`, which injects the directive and
surfaces candidate vault files. Treat the hook output as a floor, not a ceiling:
read beyond the surfaced candidates when the topic warrants.

After searching, briefly flag what you found (file path plus a one line summary)
before using it. Do not silently inject vault content into answers.

**Vault wins on facts.** When the vault and your recollection disagree on a hard
fact (a date, an amount, a name, a status), the vault is authoritative.

**Do not fabricate facts.** The vault uses `TBC` deliberately for unknowns. If
the vault does not have a figure, date, name or fact, ask. Do not infer or
estimate it into existence.

**Read `index.md` first.** Every project and area folder has one. They are
curated navigation hubs and are more reliable than search, because notes use my
shorthand and a plain language query can miss the note that covers it in detail.
Search is for when you already know the vocabulary.

## Confidentiality

See `{{VAULT_PATH}}/CLAUDE.md` for the full handling contract, and read it
before writing anything into the vault. The short version:

- Everything in the vault is agent readable and is shipped to an LLM by the
  slash commands and by the consult guard hook.
- `99-restricted/` is excluded from the hook's walk and from git. Nothing goes
  in there by accident and nothing comes out of there without me saying so.
- Client identifying detail follows the aliasing convention in the vault
  `CLAUDE.md`. Apply it when filing, do not wait to be asked.

## Core principles

### 1. Think before coding

- State your assumptions before writing code. If multiple reasonable
  interpretations exist, present them and ask. Do not guess.
- Surface tradeoffs explicitly when a choice matters. Do not quietly pick.
- Push back when you disagree. Silent agreement is worse than friction.

### 2. Simplicity first

- Minimum code that solves the stated problem. No speculative features, no "we
  might need this later".
- No defensive try/except, validation, or fallbacks for cases that cannot occur.
  Trust internal callers.
- Three similar lines beats a premature abstraction. Do not invent a helper for
  two callers.
- If the change is 100 lines, do not write 1000.

### 3. Surgical changes

- Touch only what the task requires. No drive by refactors, no renaming
  neighbouring variables, no "while I was there" cleanups.
- Do not change comments, formatting, or orthogonal code you did not need to
  touch.
- If you find something else worth fixing, mention it. Do not fix it.

### 4. Goal driven execution

- Restate the task as verifiable success criteria before starting non trivial
  work.
- For longer tasks, plan in checkpoints and report progress at each.
- LLMs are good at looping until criteria are met. Define done, then run.

## Mode awareness

Two distinct modes:

- **Vibe coding**: prototypes, throwaway scripts, exploration. Raises the floor.
  Acceptable to skip tests and specs.
- **Agentic engineering**: anything that ships or persists. Raises the ceiling.
  Requires an explicit spec, diff review, tests, guardrails.

If unsure which applies, ask. Do not drift from vibe into production without
saying so.

## Style

- Terse responses. No preamble, no trailing summary unless asked.
- **No em dashes or en dashes. Anywhere. Ever.** Not in chat, not in drafted
  messages, not in vault pages, not in commit messages, not in code comments.
  Use a comma, a full stop, a colon, or brackets, and rewrite the sentence if
  none of those fit. Ordinary hyphens in compound words and list markers are
  fine. Treat a dash appearing in your output as a defect to fix before sending,
  not a style preference.
- **Every path in a response must be absolute.** Backticks count as links: the
  client auto linkifies bare paths inside inline code, so a relative path in
  backticks is a broken link exactly like a relative href. This governs all
  forms: markdown links, inline code, tables, bullets, prose. Relative paths are
  fine inside vault files (Obsidian resolves those), never in chat output. The
  `Stop` hook `~/.claude/scripts/link-guard.py` enforces this.
- **Verify a file exists on disk before linking it.** Never link a path recalled
  from memory, inferred from a naming pattern, or written to a file you have not
  yet created.
- Put line references in bare backticks (`` `/path/foo.py:27` ``), never inside
  a markdown href. `[x](/path/foo.py:27)` is not a real path.
- Default no comments. Only add them when the *why* is non obvious.
- Default no docs or READMEs unless requested.
- Currency defaults to AUD. Flag USD or any other currency explicitly.
- Metric units and Celsius.

## Anti patterns

- **Silent assumptions**: making up missing context instead of flagging it.
- **Bloat**: abstractions, factories, config layers, helpers not justified by
  current callers.
- **Collateral damage**: editing code, comments, or formatting outside scope.
- **Over defensive code**: try/except wrapping things that cannot fail,
  validation of internal only inputs.
