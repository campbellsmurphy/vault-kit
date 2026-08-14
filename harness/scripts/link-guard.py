#!/usr/bin/env python3
"""Stop hook: block a response containing an unclickable local path.

Two failure modes, both of which hand you a dead link in chat:

  1. A vault-relative path. The client auto-linkifies bare paths inside inline
     code, so `01-projects/foo.md` in backticks is a broken link exactly like a
     relative markdown href. Relative paths are fine inside vault FILES (the
     Obsidian index resolves those), never in chat output.
  2. An absolute vault path whose target does not exist, usually a path the
     model recalled or inferred rather than verified.

On a hit the hook blocks and tells the model what to fix, so the corrected
response is the first one you see.

Vault root comes from ~/.claude/vault-path (written by install.sh).
"""
import json
import os
import re
import sys
from urllib.parse import unquote

HOME = os.path.expanduser("~")
try:
    with open(os.path.join(HOME, ".claude/vault-path")) as fh:
        VAULT = fh.read().strip()
except Exception:
    VAULT = ""

VAULT_DIRS = ("00-inbox", "01-projects", "02-areas", "03-resources",
              "04-archive", "daily", "99-restricted")

MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CODE_SPAN = re.compile(r"`([^`\n]{3,200})`")
RELATIVE = re.compile(r"^(?:\./)?(?:" + "|".join(VAULT_DIRS) + r")/\S+")
SKIP_SCHEME = ("http://", "https://", "obsidian://", "mailto:", "#")


def candidates(text):
    for href in MD_LINK.findall(text):
        yield href
    for span in CODE_SPAN.findall(text):
        span = span.strip()
        # only path-shaped code spans, not prose or commands
        if " " in span or "/" not in span:
            continue
        yield span


def normalise(raw):
    """Strip decoration the client also strips, so we test what it will open."""
    p = raw.replace("file://", "")
    p = unquote(p).rstrip(".,;:)")
    p = re.sub(r":\d+(?::\d+)?$", "", p)  # trailing :line or :line:col
    return p


def is_vault_path(p):
    return bool(VAULT) and p.startswith(VAULT)


def check(text):
    problems = []
    for raw in candidates(text):
        if raw.startswith(SKIP_SCHEME):
            continue
        p = normalise(raw)
        if RELATIVE.match(p):
            problems.append("RELATIVE (will not resolve): %s  ->  use %s/%s"
                            % (raw, VAULT or "<vault>", p))
        elif p.startswith("/") and is_vault_path(p) and not os.path.exists(p):
            problems.append("MISSING TARGET: %s" % raw)
    return problems


def main():
    payload = json.load(sys.stdin)
    if payload.get("stop_hook_active"):  # already blocked once this turn
        sys.exit(0)
    path = payload.get("transcript_path")
    if not path or not os.path.exists(path):
        sys.exit(0)

    text = ""
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            if rec.get("type") != "assistant":
                continue
            content = rec.get("message", {}).get("content")
            if not isinstance(content, list):
                continue
            blocks = [b.get("text", "") for b in content if b.get("type") == "text"]
            if blocks:
                text = "\n".join(blocks)

    problems = check(text)
    if problems:
        print(json.dumps({
            "decision": "block",
            "reason": "Unclickable local paths in your response. Re-send it with "
                      "these corrected (absolute paths; backticked paths are "
                      "clickable links too):\n- " + "\n- ".join(problems),
        }))
    sys.exit(0)


if __name__ == "__main__":
    main()
