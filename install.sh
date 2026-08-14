#!/bin/bash
# Install the vault kit on this machine.
#
#   ./install.sh [vault-path]      default: ~/vault
#
# Idempotent and non destructive:
#   - existing vault files are never overwritten, only missing ones are added
#   - ~/.claude/CLAUDE.md and ~/.claude/settings.json are backed up before change
#   - the hook block is merged into settings.json, not written over it
#
# What it does:
#   1. creates the vault skeleton at the target path
#   2. records that path in ~/.claude/vault-path (the single source of truth)
#   3. installs the hook and helper scripts into ~/.claude/scripts/
#   4. installs the global CLAUDE.md
#   5. merges the two hooks into ~/.claude/settings.json
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT="${1:-$HOME/vault}"
STAMP="$(date +%Y%m%d-%H%M%S)"

echo "Kit:   $KIT"
echo "Vault: $VAULT"
echo

# 1. Vault skeleton -----------------------------------------------------------
mkdir -p "$VAULT"
# -n never clobbers an existing file. Two passes so dotfiles come along.
cp -Rn "$KIT/vault/." "$VAULT/" 2>/dev/null || true
echo "vault skeleton in place ($(find "$VAULT" -name '*.md' | wc -l | tr -d ' ') markdown files)"

# 2. Vault path ---------------------------------------------------------------
mkdir -p "$HOME/.claude/scripts"
printf '%s\n' "$VAULT" > "$HOME/.claude/vault-path"
echo "wrote ~/.claude/vault-path"

# 3. Scripts ------------------------------------------------------------------
for f in "$KIT"/harness/scripts/*; do
    cp "$f" "$HOME/.claude/scripts/$(basename "$f")"
done
chmod +x "$HOME"/.claude/scripts/vault-consult-guard.py \
         "$HOME"/.claude/scripts/link-guard.py \
         "$HOME"/.claude/scripts/lint_wiki_links.py \
         "$HOME"/.claude/scripts/vault_git_backup.sh
echo "installed hooks and scripts into ~/.claude/scripts/"

# 4. Global CLAUDE.md ---------------------------------------------------------
if [ -f "$HOME/.claude/CLAUDE.md" ]; then
    cp "$HOME/.claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md.bak-$STAMP"
    echo "backed up existing ~/.claude/CLAUDE.md to CLAUDE.md.bak-$STAMP"
fi
sed "s|{{VAULT_PATH}}|$VAULT|g" "$KIT/harness/CLAUDE.md" > "$HOME/.claude/CLAUDE.md"
echo "installed ~/.claude/CLAUDE.md"

# 5. Merge hooks into settings.json -------------------------------------------
python3 - "$HOME" "$KIT" "$STAMP" <<'PY'
import json, os, shutil, sys

home, kit, stamp = sys.argv[1], sys.argv[2], sys.argv[3]
settings_path = os.path.join(home, ".claude", "settings.json")

settings = {}
if os.path.exists(settings_path):
    shutil.copy(settings_path, settings_path + ".bak-" + stamp)
    with open(settings_path) as fh:
        text = fh.read().strip()
    settings = json.loads(text) if text else {}
    print("backed up existing settings.json to settings.json.bak-" + stamp)

with open(os.path.join(kit, "harness", "settings.hooks.json")) as fh:
    new_hooks = json.loads(fh.read().replace("{{HOME}}", home))["hooks"]

hooks = settings.setdefault("hooks", {})
for event, entries in new_hooks.items():
    existing = hooks.setdefault(event, [])
    wanted = entries[0]["hooks"][0]["command"]
    already = any(
        h.get("command") == wanted
        for entry in existing
        for h in entry.get("hooks", [])
    )
    if already:
        print("hook already present for " + event + ", left alone")
    else:
        existing.extend(entries)
        print("added " + event + " hook")

with open(settings_path, "w") as fh:
    json.dump(settings, fh, indent=2)
    fh.write("\n")
PY

echo
echo "Done. Next:"
echo "  1. cd $VAULT && claude       # confirm /daily /process-inbox /ingest-url /lint-wiki appear"
echo "  2. open $VAULT in Obsidian as a vault"
echo "  3. read $KIT/CONFIDENTIALITY.md before putting anything in it"
