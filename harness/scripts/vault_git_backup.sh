#!/bin/bash
# Nightly vault snapshot into a git dir OUTSIDE the vault.
#
# Why the git dir is outside: the vault may sit in a synced folder (iCloud,
# OneDrive, Dropbox), and letting a sync client fight git over .git/ objects
# corrupts repos. The vault holds only a .git pointer file; the real git dir
# lives at $GITDIR.
#
# LOCAL ONLY. This never pushes anywhere. If the vault holds client material,
# do not add a remote without clearing it against firm policy first.
#
# Read-only with respect to vault content: add, commit, nothing destructive.
#
# First-time setup (run once, then wire this script into launchd or cron):
#   git init --bare ~/vault.git
#   git --git-dir=~/vault.git config core.bare false
#   git --git-dir=~/vault.git config gc.auto 0
#   printf 'gitdir: %s\n' "$HOME/vault.git" > "$VAULT/.git"
#
# launchd gotcha on macOS: a launchd bash agent may NOT make a cloud-synced
# directory its CWD (git dies with "Unable to read current working directory:
# Operation not permitted") but CAN reach the same files by absolute path. So
# never cd into the vault here; drive git with --git-dir/--work-tree from $HOME.
set -u
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

VAULT="$(cat "$HOME/.claude/vault-path" 2>/dev/null)"
GITDIR="$HOME/vault.git"
GIT=(git --git-dir="$GITDIR" --work-tree="$VAULT")

if [ -z "$VAULT" ] || [ ! -d "$VAULT" ]; then
    echo "$(date +%FT%T) SKIP: vault path unset or missing"
    exit 0
fi

if [ ! -f "$VAULT/.git" ] || [ ! -d "$GITDIR" ]; then
    echo "$(date +%FT%T) SKIP: vault .git pointer or $GITDIR missing (see setup in this file's header)"
    exit 0
fi

cd "$HOME" || exit 0

if ! "${GIT[@]}" add -A; then
    echo "$(date +%FT%T) ERROR: git add failed - nothing committed"
    exit 0
fi

if "${GIT[@]}" diff --cached --quiet; then
    echo "$(date +%FT%T) no changes since last snapshot"
elif "${GIT[@]}" -c commit.gpgsign=false commit -q -m "auto: nightly snapshot $(date +%F)"; then
    echo "$(date +%FT%T) committed $("${GIT[@]}" rev-parse --short HEAD)"
else
    echo "$(date +%FT%T) ERROR: git commit failed"
fi
