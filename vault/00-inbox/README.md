# 00: Inbox

The dump zone. **Anything goes here first**, no filing required.

Fleeting thoughts, half formed ideas, links to read later, scratch notes from a
meeting, a transcribed voice memo. Web Clipper captures and Obsidian attachments
land here too. Speed of capture beats correctness.

## Rules

- Do not agonise over filenames. `quick-note-on-x.md` is fine.
- Do not link, do not tag, do not file. That is `/process-inbox`'s job.
- Drain this folder every few days by running `/process-inbox` from Claude Code.

## What `/process-inbox` does

Reads every capture here (notes, dictations, images, PDFs, link bundles),
applies confirmed corrections directly to the owning vault pages, files source
material next to the pages that cite it, deletes the processed originals, and
logs the pass to `log.md`.

## Confidentiality

The inbox is the highest risk folder in the vault, because captures arrive
unredacted and the consult guard hook walks this folder like any other. Anything
pasted here from client work is in scope for the LLM from the moment it lands,
not from the moment it is filed. If a capture should not be, put it in
`99-restricted/` instead and file it by hand.
