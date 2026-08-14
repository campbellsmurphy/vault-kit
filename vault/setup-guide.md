# Setup guide

A 15 minute walkthrough from "the kit is cloned" to "running `/ingest-url`
against your first source".

If you ran `install.sh` from the kit, steps 1 and 6 are already done.

## 1. Place the vault

The vault lives wherever `~/.claude/vault-path` says it lives. That file holds a
single absolute path and is the only place the location is configured: the
hooks, the lint scanner and the backup script all read it. If you move the
vault, edit that one file.

Avoid putting the vault inside a cloud synced folder if it holds client
material. Sync clients replicate the folder to a server you may not control, and
that is a separate disclosure from the LLM one.

## 2. Open it as an Obsidian vault

1. Launch Obsidian.
2. "Open folder as vault", then pick the vault folder.
3. Trust the vault when prompted.

## 3. Core Obsidian settings

This method is light on plugins. Set these in **Settings**:

- **Files and links**
  - Default location for new attachments: `00-inbox/`
  - New link format: **Shortest path when possible**
  - Use `[[Wikilinks]]`: on
- **Editor**
  - Spellcheck on, strict line breaks off

## 4. Install the Web Clipper

The Obsidian Web Clipper browser extension is the main on ramp for source
material.

1. Install it from the Chrome Web Store or Firefox Add-ons.
2. Set the destination vault to this vault.
3. Set the destination folder to `00-inbox/`.
4. Filename template: `{{title|kebab}}-{{date}}.md`
5. Enable "Save images locally", so the agent can read them.

Test it: clip one page. It should land in `00-inbox/`.

## 5. Plugins: the minimal set

- **Daily notes** (core, already bundled). Set the folder to `daily/` and the
  date format to `YYYY-MM-DD`.
- **Templater** (optional), if you want to scaffold daily notes without running
  `/daily` from Claude Code.

That is it. Resist Dataview, resist Tasks, resist installing 30 plugins. The
agent does the heavy lifting, and plugins solve a problem you do not have yet.

## 6. Install Claude Code

```bash
brew install --cask claude-code
```

Then, from the vault folder:

```bash
claude
```

You should see the slash commands: `/daily`, `/process-inbox`, `/ingest-url`,
`/lint-wiki`. Try `/daily` first.

Run Claude Code from inside the vault folder. The slash commands assume that is
the working directory.

## 7. Verify the harness

The two hooks are what make this more than a folder of markdown. Check them:

```bash
echo '{"prompt":"what did we decide about the migration"}' | python3 ~/.claude/scripts/vault-consult-guard.py
```

You should get JSON containing the mandatory vault check directive, and once the
vault has content, a list of candidate files. If it warns that the path is unset
or missing, fix `~/.claude/vault-path`.

The link guard only fires at the end of a real turn, so the way to test it is to
ask Claude Code for a vault path in a response and confirm the path comes back
absolute.

## 8. Your first ingest

1. Clip a source you actually want to remember.
2. Confirm it is in `00-inbox/`.
3. Run `claude` from the vault folder.
4. Type `/ingest-url 00-inbox/<that-filename>.md`.
5. Watch it touch 5 to 15 pages in `03-resources/`.
6. Open Obsidian's graph view and look at what was created.

## 9. Rhythm to try for two weeks

- **Morning**: `/daily`, then skim yesterday.
- **As you work**: append to today's log, drop captures into `00-inbox/`.
- **Two or three times a week**: `/process-inbox`.
- **Weekly**: `/lint-wiki`. Read the report, spend 20 minutes on the top items.

If after two weeks you have used the system, layer on whatever is missing. If
you have not, the system is not the problem: capture more.

## 10. Backups

`~/.claude/scripts/vault_git_backup.sh` snapshots the vault into a git dir
outside it. First time setup is in the header of that script. It is local only
and deliberately has no remote. Do not add one for a vault holding client
material without clearing it first.

## Troubleshooting

**Slash commands do not appear.** You were not in the vault folder when you ran
`claude`. `cd` into it. Or `.claude/commands/` was renamed.

**The consult guard surfaces nothing.** Expected while the vault is nearly
empty: it needs content to match against. Confirm it still emits the directive.

**The consult guard warns the vault is stale.** Nothing has been written under
the configured path in over 14 days. Either you have not used it, or the live
vault has moved and you are reading a dead copy. Check before you trust an
answer sourced from it.

**`/lint-wiki` reports the folder READMEs as orphans.** Expected on a fresh
vault: nothing links to them yet, because there are no pages. It resolves itself
as you add content and index pages. Do not "fix" it by linking READMEs to each
other.

**Web Clipper saves to the wrong folder.** Re-pick `00-inbox/` in the extension
settings. Some browsers reset the path on extension updates.

**Graph view is empty.** You need wikilinks to see edges. Run `/process-inbox`
and `/ingest-url` a few times and the graph fills out fast.
