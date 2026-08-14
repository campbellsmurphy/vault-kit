#!/usr/bin/env python3
import os, re, sys, json
from collections import defaultdict

# Bump on any change to scan scope, exclusions, or orphan/stub logic so report
# counts stay comparable run-to-run (a bumped version flags a non-comparable baseline).
VERSION = "2026-07-26.1"

# Vault root: argv[1] if given, else the path recorded by install.sh.
_cfg = os.path.expanduser("~/.claude/vault-path")
VAULT = sys.argv[1] if len(sys.argv) > 1 else open(_cfg).read().strip()
SCAN_DIRS = ["01-projects", "02-areas", "03-resources", "04-archive"]
EXCLUDE = {"daily", "00-inbox", "skills"}

# Data namespaces: files here are data rows / archived dumps, not wiki pages.
# Links are still resolved and validity-checked; they are just exempt from
# orphan/stub judgement (they exist to be queried, not linked).
DATA_NAMESPACES = (
    "02-areas/claude-code/reports/",
    "02-areas/claude-code/lint-drafts/",
    "04-archive/",
)
# Filed sources are immutable evidence per the vault contract: data, not wiki pages.
SOURCE_DIR_RE = re.compile(r'(^|/)(sources|source-docs|source-data|raw)/')
def in_data_namespace(rel):
    return any(rel.startswith(d) for d in DATA_NAMESPACES) or bool(SOURCE_DIR_RE.search(rel))

README_ALLOW = {"note-name", "concept", "link", "name"}
AUTOMEM_RE = re.compile(r'^(\.\./)+(user|feedback|project|reference)_[a-z_]+$')

# Collect all md files
all_files = []  # relative paths from VAULT
for d in SCAN_DIRS:
    for root, dirs, files in os.walk(os.path.join(VAULT, d)):
        dirs[:] = [x for x in dirs if x not in EXCLUDE]
        for f in files:
            if f.endswith(".md"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, VAULT)
                all_files.append(rel)

# Whole-vault resolution index (links may point into daily/ etc.).
all_any = set()       # every file relpath (any ext) anywhere in vault
basename_any = defaultdict(list)  # basename(with ext) -> [relpaths]
suffix_index = set()  # normalized path forms (with and without .md) for suffix matching
for root, dirs, files in os.walk(VAULT):
    dirs[:] = [x for x in dirs if x not in (".obsidian", ".git", ".trash")]
    for f in files:
        if f == ".DS_Store": continue
        rp = os.path.relpath(os.path.join(root, f), VAULT)
        all_any.add(rp)
        basename_any[f].append(rp)
        suffix_index.add(rp)
        if rp.endswith(".md"):
            suffix_index.add(rp[:-3])

def suffix_match(target):
    """Obsidian path-suffix match: any file whose path ends with target (with/without .md)."""
    t = target
    cands = set()
    for p in suffix_index:
        if p == t or p.endswith("/" + t):
            cands.add(p[:-3] if p.endswith(".md") else p)
    # also try target+.md form already covered by suffix_index containing noext
    return cands

# stem -> list of relpaths (without .md). scan-dir map for orphan/inbound;
# stem_all spans the whole vault (incl raw/, daily/) for link-validity resolution.
stem_map = defaultdict(list)
stem_all = defaultdict(list)
relpath_set = set()  # scan-dir rel paths without extension
for rel in all_files:
    noext = rel[:-3]
    relpath_set.add(noext)
    stem_map[os.path.basename(noext)].append(noext)
for rp in all_any:
    if rp.endswith('.md'):
        noext = rp[:-3]
        stem_all[os.path.basename(noext)].append(noext)

def strip_code(text):
    # Replace fenced code blocks with equal-length spaces preserving newlines
    def repl_fence(m):
        return ''.join('\n' if c == '\n' else ' ' for c in m.group(0))
    text = re.sub(r'```.*?```', repl_fence, text, flags=re.DOTALL)
    # inline code spans
    def repl_inline(m):
        return ' ' * len(m.group(0))
    text = re.sub(r'`[^`\n]*`', repl_inline, text)
    return text

WIKILINK_RE = re.compile(r'\[\[([^\[\]]+?)\]\]')

inbound = defaultdict(set)   # target noext -> set of source files
broken = []                  # (file, line, target, suggestion)
convention = defaultdict(list)  # file -> list of warnings
ambiguous = []               # (file, line, target, candidates)

def resolve_bare(name, src_rel):
    """Walk up from src dir; nearest match wins; vault-wide fallback; ambiguous if tie."""
    src_dir = os.path.dirname(src_rel)
    cands = stem_all.get(name, [])
    if not cands:
        return None, []
    # compute for each candidate the depth of common ancestor with src_dir
    # nearest = candidate whose directory is closest (longest shared prefix / fewest hops)
    parts_src = src_dir.split(os.sep) if src_dir else []
    best = []
    best_score = float('-inf')
    for c in cands:
        cdir = os.path.dirname(c)
        parts_c = cdir.split(os.sep) if cdir else []
        # shared prefix length
        shared = 0
        for a, b in zip(parts_src, parts_c):
            if a == b: shared += 1
            else: break
        # distance: hops up from src to common ancestor + hops down to candidate
        dist = (len(parts_src) - shared) + (len(parts_c) - shared)
        score = -dist
        if score > best_score:
            best_score = score
            best = [c]
        elif score == best_score:
            best.append(c)
    if len(best) == 1:
        return best[0], best
    return None, best  # ambiguous

for rel in all_files:
    full = os.path.join(VAULT, rel)
    is_readme = os.path.basename(rel) == "README.md"
    try:
        with open(full, encoding="utf-8") as fh:
            raw = fh.read()
    except Exception as e:
        continue
    text = strip_code(raw)
    text = text.replace('\\|', '|')
    lines = text.split('\n')
    for lineno, line in enumerate(lines, 1):
        for m in WIKILINK_RE.finditer(line):
            # citation-marker false positive: [[n]](url) is markdown-link text, not a wikilink
            if m.end() < len(line) and line[m.end()] == '(':
                continue
            inner = m.group(1)
            target = inner.split('|', 1)[0].strip()
            # strip Obsidian heading/block anchor; pure same-page anchors are valid
            target = target.split('#', 1)[0].split('^', 1)[0].strip()
            if not target:
                continue  # same-page anchor link
            # slash command
            if target.startswith('/'):
                if "slash-command" not in [w[0] for w in convention[rel]]:
                    convention[rel].append(("slash-command", target))
                continue
            # auto-memory pattern
            if AUTOMEM_RE.match(target):
                convention[rel].append(("auto-memory", target))
                continue
            # README pseudo-targets
            if is_readme and target in README_ALLOW:
                continue
            is_relative = target.startswith('../') or target.startswith('./')
            if is_relative:
                src_dir = os.path.dirname(rel)
                resolved = os.path.normpath(os.path.join(src_dir, target))
                if resolved.startswith('..') or os.path.isabs(resolved):
                    convention[rel].append(("external", target))
                    continue
                cand_noext = resolved[:-3] if resolved.endswith('.md') else resolved
                if resolved in all_any:
                    if cand_noext in relpath_set:
                        inbound[cand_noext].add(rel)
                elif (resolved + '.md') in all_any:
                    inbound[resolved].add(rel)
                elif cand_noext in relpath_set:
                    inbound[cand_noext].add(rel)
                else:
                    broken.append((rel, lineno, target, "relative path doesn't resolve, check ../ depth"))
            elif '/' in target:
                tnoext = target[:-3] if target.endswith('.md') else target
                # 1) source-relative (Obsidian prefers the nearest match)
                src_dir = os.path.dirname(rel)
                local = os.path.normpath(os.path.join(src_dir, tnoext))
                if local in relpath_set:
                    inbound[local].add(rel)
                elif local in all_any or (local + '.md') in all_any:
                    pass  # non-md local file, valid
                else:
                    # 2) vault-wide suffix match, nearest by directory distance
                    cands = suffix_match(tnoext)
                    if not cands:
                        broken.append((rel, lineno, target, "rename/create/remove"))
                    else:
                        parts_src = src_dir.split(os.sep) if src_dir else []
                        best, best_score = [], float('-inf')
                        for c in cands:
                            pc = os.path.dirname(c).split(os.sep) if os.path.dirname(c) else []
                            shared = 0
                            for a, b in zip(parts_src, pc):
                                if a == b: shared += 1
                                else: break
                            score = -((len(parts_src) - shared) + (len(pc) - shared))
                            if score > best_score: best_score, best = score, [c]
                            elif score == best_score: best.append(c)
                        if len(best) == 1:
                            if best[0] in relpath_set:
                                inbound[best[0]].add(rel)
                        else:
                            md_b = [c for c in best if c in relpath_set]
                            if md_b:
                                ambiguous.append((rel, lineno, target, sorted(md_b)))
            else:
                cand = target[:-3] if target.endswith('.md') else target
                resolved, matches = resolve_bare(cand, rel)
                if resolved:
                    inbound[resolved].add(rel)
                elif len(matches) > 1:
                    ambiguous.append((rel, lineno, target, matches))
                elif target in basename_any:
                    pass  # resolves to a real non-md file (e.g. Foo.pdf), valid
                else:
                    broken.append((rel, lineno, target, "rename/create/remove"))

# Orphans: files with zero inbound (data namespaces exempt)
orphans = [rel for rel in all_files if rel[:-3] not in inbound and not in_data_namespace(rel)]

# Stubs: under 3 sentences, no Sources: block. Count sentences in body (strip frontmatter, headings, code).
def is_stub(rel):
    full = os.path.join(VAULT, rel)
    try:
        with open(full, encoding="utf-8") as fh:
            raw = fh.read()
    except: return False
    if re.search(r'(?im)^sources?\s*:', raw) or re.search(r'(?i)Sources:', raw):
        return False
    body = raw
    # strip frontmatter
    if body.startswith('---'):
        end = body.find('\n---', 3)
        if end != -1:
            body = body[end+4:]
    body = strip_code(body)
    # remove headings, list markers, tables, frontmatter-ish
    txt = []
    for ln in body.split('\n'):
        s = ln.strip()
        if not s: continue
        if s.startswith('#'): continue
        if s.startswith('|'): continue
        if re.match(r'^[-*+]\s', s):
            txt.append(s)
            continue
        txt.append(s)
    joined = ' '.join(txt)
    # count sentences
    sentences = re.split(r'[.!?]+\s', joined)
    sentences = [x for x in sentences if len(x.strip()) > 3]
    wordcount = len(joined.split())
    return len(sentences) < 3 and wordcount < 60

stubs = [rel for rel in all_files if not in_data_namespace(rel) and is_stub(rel)]

out = {
    "scanner_version": VERSION,
    "excluded_dirs": sorted(EXCLUDE),
    "data_namespaces": list(DATA_NAMESPACES),
    "total_files": len(all_files),
    "broken": broken,
    "ambiguous": ambiguous,
    "convention": {k: v for k, v in convention.items()},
    "orphans": orphans,
    "stubs": stubs,
    "orphan_count": len(orphans),
}
print(json.dumps(out, indent=1))
