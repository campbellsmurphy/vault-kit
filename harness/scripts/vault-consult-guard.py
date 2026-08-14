#!/usr/bin/env python3
"""
UserPromptSubmit hook: mandatory vault consultation guard.

Fires on EVERY user prompt (all session types, headless included). Via
additionalContext it injects:

  (a) a non-optional directive to consult the vault before answering anything
      that could relate to the user's own work, notes, projects, clients or
      colleagues, and
  (b) up to MAX_FILES candidate vault files, ranked by relevance to salient
      terms in the prompt, so the real context is surfaced on the same turn.

Without this hook the vault is passive: the model only reads it when it thinks
to. With it, every turn starts from the vault. That single behaviour is most of
what makes the setup work.

Design notes:
  * Fail-open. Any error means emit just the directive (or nothing) and exit 0.
    It NEVER exits 2, so it can never erase or block a prompt.
  * Pure stdlib, search done in-process (os.walk + re). It does NOT shell out
    to `rg`: Claude Code exposes `rg` only as a shell function dispatching to
    ripgrep inside the claude binary, so there is no `rg` binary on PATH for
    subprocess to find. A pure-Python walk is portable and fast (~0.1s over
    ~1000 markdown files) and avoids grep-flavour differences.
  * RESTRICTED_DIR is never walked. See CONFIDENTIALITY.md for what that does
    and, importantly, what it does not do.

Vault root resolution: ~/.claude/vault-path, one absolute path, written by
install.sh. Re-point that file if the vault moves; nothing else needs editing.
"""
import sys
import os
import json
import re
import time

VAULT = ""
try:
    with open(os.path.expanduser("~/.claude/vault-path")) as fh:
        VAULT = fh.read().strip()
except Exception:
    pass

MAX_FILES = 8
FRESH_DAYS = 14            # no vault writes in this long means it may have moved
TIME_BUDGET = 4.0          # seconds; hard stop for the walk
MAX_FILE_BYTES = 300_000   # skip anything larger than a normal note
RESTRICTED_DIR = "99-restricted"
SKIP_DIRS = {".git", ".obsidian", ".trash", "node_modules", RESTRICTED_DIR}

DIRECTIVE = (
    "MANDATORY VAULT CHECK. The vault is the canonical record of this user's "
    "work: engagements, clients, projects, decisions, meetings, people, and "
    "the standing conventions they work by.\n"
    "Before answering, if this prompt could PLAUSIBLY relate to any of the "
    "above, you MUST search the vault and read the relevant files first. Do "
    "not answer from memory or assumption when the vault may hold the real "
    "context. When unsure whether it is relevant, search. Only skip when the "
    "question is clearly generic and has nothing to do with this user's work.\n"
    "Vault path: " + VAULT + "\n"
    "Do not restate vault content verbatim in your synthesis."
)

# Words that make poor search terms.
STOP = set((
    "a an the and or but if then else of to in on at by for with from into over "
    "under about as is are was were be been being this that these those it its you "
    "your i me my we our he she they them his her their do does did done can could "
    "should would will just get got need want make made how what why when where "
    "which who whom whose not no yes please tell show give find help out up so more "
    "most some any all one two very really thing things stuff also than too now new "
    "use using used way ways let lets know think see look have has had here there "
    "still current latest recent again back down off same each other around"
).split())


def salient_terms(prompt):
    words = re.findall(r"[A-Za-z][A-Za-z0-9'\-]{2,}", prompt or "")
    seen, terms = set(), []
    for w in words:
        lw = w.lower()
        if lw in STOP or lw in seen:
            continue
        seen.add(lw)
        terms.append(w)
    # Proper-noun-ish (capitalised) terms first: names, clients, projects.
    terms.sort(key=lambda w: (0 if w[:1].isupper() else 1))
    return terms[:12]


def _weight(term):
    # Rare / specific terms count for more: proper nouns, codes with digits,
    # and long words. Generic short words count for one.
    strong = term[:1].isupper() or any(c.isdigit() for c in term) or len(term) >= 9
    return (3, True) if strong else (1, False)


def search(terms):
    if not terms or not VAULT or not os.path.isdir(VAULT):
        return []
    compiled = []
    for t in terms:
        try:
            # Word-boundary match so "Rust" does not hit "trust"/"crust" and
            # "list" does not hit "listen"/"enlist".
            rx = re.compile(r"\b" + re.escape(t) + r"\b", re.IGNORECASE)
        except re.error:
            continue
        w, strong = _weight(t)
        compiled.append((rx, w, strong))
    if not compiled:
        return []

    deadline = time.time() + TIME_BUDGET
    n = len(compiled)
    df = [0] * n                 # document frequency per term
    records = []                 # (rel, matched_indices, archived)
    scanned = 0
    stop = False
    for root, dirs, files in os.walk(VAULT):
        if stop:
            break
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS]
        for fn in files:
            if not fn.endswith(".md"):
                continue
            if time.time() > deadline:
                stop = True
                break
            fp = os.path.join(root, fn)
            try:
                if os.path.getsize(fp) > MAX_FILE_BYTES:
                    continue
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception:
                continue
            scanned += 1
            matched = tuple(i for i, (rx, _, _) in enumerate(compiled) if rx.search(text))
            if not matched:
                continue
            for i in matched:
                df[i] += 1
            rel = os.path.relpath(fp, VAULT)
            records.append((rel, matched, rel.startswith("04-archive/")))

    if scanned == 0:
        return []
    # Drop terms appearing in too large a share of the vault: for this corpus
    # they behave like stopwords and only add noise (IDF-style pruning). Rare
    # proper nouns (names, client codes) survive and carry the ranking.
    common_cap = max(8, int(0.25 * scanned))
    meaningful = {i for i in range(n) if 0 < df[i] <= common_cap}
    if not meaningful:
        return []

    scored = []
    for rel, matched, archived in records:
        mm = [i for i in matched if i in meaningful]
        if not mm:
            continue
        distinct = len(mm)
        has_strong = any(compiled[i][2] for i in mm)
        # Keep only clear signal: a strong/specific term (name, code, long
        # word), or, for generic-only matches, 3+ distinct terms co-occurring.
        if not has_strong and distinct < 3:
            continue
        score = sum(compiled[i][1] for i in mm)
        if archived:
            score -= 1  # de-prioritise archived material
        scored.append((score, distinct, -len(rel), rel))

    scored.sort(reverse=True)
    return [rel for _, _, _, rel in scored[:MAX_FILES]]


def vault_health():
    """'ok' | 'unset' | 'missing' | 'stale'. Cheap: four stats, no walk.

    A vault that has silently moved is the failure mode that matters, because
    every answer after it is confidently sourced from a dead copy.
    """
    if not VAULT:
        return "unset"
    if not os.path.isdir(VAULT):
        return "missing"
    newest = 0.0
    for probe in ("log.md", "00-inbox", "daily", ".obsidian/workspace.json"):
        try:
            newest = max(newest, os.path.getmtime(os.path.join(VAULT, probe)))
        except OSError:
            pass
    if not newest:
        # Directory exists but no probe file does: a husk left by a move.
        return "missing"
    if time.time() - newest > FRESH_DAYS * 86400:
        return "stale"
    return "ok"


def health_warning(state):
    if state == "unset":
        return ("*** VAULT PATH NOT CONFIGURED: ~/.claude/vault-path is missing "
                "or empty, so no vault is being consulted. Fix it before "
                "answering anything about this user's work. ***")
    if state == "missing":
        head = ("*** VAULT PATH BROKEN: the configured vault path does not "
                "exist on disk. The vault has almost certainly MOVED. ***")
    else:
        head = ("*** VAULT FRESHNESS WARNING: nothing under the configured "
                "vault path has been written in over %d days. The live vault "
                "may have moved, leaving this copy stale. ***" % FRESH_DAYS)
    return head + (
        "\nConfigured path: " + VAULT +
        "\nBefore answering anything about this user's work: verify the real "
        "location on disk, then re-point ~/.claude/vault-path. Do not silently "
        "answer from a stale copy or from memory."
    )


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}
    # Field name has varied across versions; accept either.
    prompt = data.get("user_input") or data.get("prompt") or ""

    context = DIRECTIVE
    try:
        state = vault_health()
    except Exception:
        state = "ok"
    if state != "ok":
        context = health_warning(state) + "\n\n" + context
    try:
        hits = search(salient_terms(prompt))
    except Exception:
        hits = []
    if hits:
        context += (
            "\n\nCandidate vault files matching this prompt (read the relevant "
            "ones before answering; this list is a floor, not a ceiling):\n"
            + "\n".join("  - " + h for h in hits)
        )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": context,
        }
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
