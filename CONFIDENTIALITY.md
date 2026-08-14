# Confidentiality

This vault is configured to hold client material. Read this before you put
anything in it.

## What actually happens to the contents

Three separate mechanisms send vault content to Anthropic's API:

1. **The slash commands.** `/process-inbox`, `/lint-wiki` and `/ingest-url` read
   across folders by design. A lint pass reads most of the vault.
2. **The consult guard hook.** It runs on **every prompt**, walks the vault,
   ranks files against your prompt, and injects the top matches into the model's
   context. You do not invoke it and you are not asked first. That is the point
   of it, and it is also the largest exposure in this setup.
3. **Ordinary agent reads.** Any session where the model opens a file.

There is no read of this vault that stays on the machine. Assume that anything
filed here has already been sent to a model, because within a few prompts on a
related topic, it has been.

Anthropic's commercial terms do not train on API inputs, and the enterprise
posture is a real one. That is a different question from whether you are
permitted to disclose the material at all.

## The questions this setup does not answer for you

These are yours to resolve against your firm's policy and your engagement terms.
They are listed so they are not resolved by omission:

- Whether client confidential information may be sent to a third party LLM
  provider at all, and under which approved tenancy or account.
- Whether your engagement letters or the client's own terms restrict disclosure
  to subprocessors, and whether Anthropic is on the approved list.
- Data residency, if any client requires in-country processing.
- Whether independence, ethics or privacy rules attach to specific engagements
  (listed clients, personal information, health data, market sensitive work).
- Retention and deletion obligations, including for the archive folder and the
  local git snapshots.

If the answer to the first one is no, the aliasing convention below is what lets
you keep most of the value of the vault anyway.

## The aliasing convention

The default posture. Applied by the agent when it files, not requested by you
each time.

**Alias the entity.** `Client A`, `Client B`, on first use and thereafter. The
mapping lives in `99-restricted/client-aliases.md` and nowhere else.

**Strip what survives aliasing.** A note can name no client and still identify
one: ABNs and ACNs, contract and engagement numbers, deal code names, account
numbers, distinctive dollar figures, named individuals at the client, an unusual
combination of industry, geography and size.

**Keep what makes it worth writing.** The methodology, the issue, the reasoning,
the decision, the pattern you want to find again in two years. That is almost
always separable from the identity, and it is the part the wiki compounds.

**Split by folder.** The general lesson goes in `03-resources/topics/`, free of
client detail entirely. The engagement specific record stays in its
`01-projects/` folder, aliased. Anything that cannot be written usefully without
identifying detail goes to `99-restricted/`.

## What `99-restricted/` is, precisely

**It does:**

- Sit outside the consult guard hook's walk, so nothing in it is surfaced
  automatically as a candidate file.
- Sit outside git, so it is not in the local snapshot repo.
- Sit outside the lint scanner's scope, so it is never reported on.

**It does not:**

- Stop an agent reading a file in it when you point at one. You can ask, and it
  will.
- Make the contents safe to send. If you ask for a file in there to be read, it
  goes to the API like anything else.
- Encrypt anything, or change file permissions.

It is a policy marker and a speed bump. If you need a technical control, keep
the material out of the vault entirely: this folder is not one.

## Backups

`vault_git_backup.sh` snapshots the vault into `~/vault.git`, which is local and
has no remote. Do not add one. A private GitHub repo is still a disclosure to
GitHub, and it is the single easiest way to turn a considered decision about
LLM access into an unconsidered one about a hosting provider.

Note the asymmetry: `99-restricted/` is gitignored, so it is the one part of the
vault with no backup. That is deliberate, and it means anything in there is one
disk failure from gone. Back it up somewhere your firm already sanctions.

## Cloud sync

If you put the vault inside iCloud Drive, OneDrive or Dropbox, the contents
replicate to that provider. That is a separate disclosure from the LLM one, to a
different party, and it is easy to do by accident by choosing a convenient
folder. Decide it deliberately.

## The residual risk, stated plainly

The aliasing convention depends on an LLM applying judgment at filing time,
every time. It will sometimes miss something: a name in a pasted quote, a figure
in a screenshot, a filename in a clipped page. The `/lint-wiki` confidentiality
drift check exists to catch that after the fact, which means the material has
already been through the API by the time it is caught.

That risk is inherent to the decision to keep client material in an LLM read
vault. It can be reduced, but not removed, and no configuration in this kit
removes it.
