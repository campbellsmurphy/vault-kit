---
description: Drain 00-inbox/: classify every capture, file it, update the owning pages, delete the original, log the pass
---

You are draining `00-inbox/`. The inbox is a capture zone, not storage: at the
end of a successful pass it is empty.

## Procedure

1. **Inventory.** List every file in `00-inbox/` (markdown, images, PDFs,
   transcripts, clipped pages). Group related captures into bundles: a link plus
   its screenshots is one item, not three.

2. **Classify each item** into exactly one of:
   - **Correction or update to an existing page.** The capture says something
     the vault already covers, but differently or more recently.
   - **New material for an existing project or area.**
   - **A new project or area.** Propose the folder, do not create it silently.
   - **Source material.** Belongs in the owning project or area's `sources/`
     folder, unedited.
   - **Reference material.** Compile it into `03-resources/` (this is
     `/ingest-url`'s job: invoke that flow rather than reimplementing it).
   - **An action item.** Not vault content. Surface it in the report so it can
     be put wherever tasks live.
   - **Noise.** Propose deletion, do not delete unilaterally.

3. **Review gate.** Present the full classification in one message: item,
   proposed destination, proposed edit. Apply nothing yet. If the run was
   explicitly asked to go end to end without stopping, skip this gate and report
   afterwards instead.

4. **Apply.** For each approved item:
   - Apply corrections directly to the owning page, in that page's voice and
     structure. Do not append a "from the inbox" section.
   - Move source files into the destination's `sources/` folder unchanged.
   - Update the destination folder's `index.md`.
   - Apply the aliasing convention from the vault `CLAUDE.md` to anything
     derived from client work, as you file it. Captures arrive unredacted, so
     this pass is where redaction actually happens.
   - Anything that cannot be usefully aliased goes to `99-restricted/` and is
     reported, not filed into the open vault.

5. **Drain.** Delete each processed original only after its content is committed
   somewhere else. Verify the destination file exists and contains the content
   before deleting the source. Never delete an item you could not classify:
   leave it and report it.

6. **Log.** Append one line to `log.md`:
   `## [YYYY-MM-DD] process-inbox | <n> items: <short summary>`

## Hard rules

- Never write to `daily/`.
- Never edit files already filed under a `sources/` folder.
- Voice or dictation captures are raw transcripts with errors and no
  punctuation. Clean them up before filing, but do not invent detail to fill a
  garbled passage. Mark unclear runs `TBC`.
- Do not fabricate a destination to avoid asking. An unclassifiable item stays
  in the inbox.

## Output

```
## Inbox pass, <today>
### Filed
<item -> destination, one line each>
### Corrections applied
<page -> what changed>
### Restricted
<items routed to 99-restricted/ and why>
### Action items
<not vault content, needs a home>
### Left in the inbox
<item -> why it could not be classified>
```
