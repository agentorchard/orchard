# Licensing

This repository holds three kinds of material with three different owners. They
are licensed separately, because conflating them would either overreach on work
that is not ours or put friction on data that should flow freely.

| Component | Paths | Licence | Why |
| --- | --- | --- | --- |
| Our code | `scripts/`, `.github/` workflows, the Deno wrapper, the egress hook | Apache-2.0 | Patent grant, modification notice, trademark reservation, attribution — see below |
| Registry data | `marketplace.json`, `registry/**`, decision records | CC0-1.0 | A security feed should have no reuse friction |
| Vendored plugins | `plugins/<name>/` | Upstream's licence, unchanged | **Not ours to choose** |

Full texts: [`LICENSE`](../LICENSE) (Apache-2.0), [`LICENSE-DATA`](../LICENSE-DATA)
(CC0-1.0), [`NOTICE`](../NOTICE) (Apache §4(d) attribution).

---

## ⚠ Open blocker: unlicensed upstream plugins

**A plugin published with no licence is not permissively licensed. It is all
rights reserved.** Absent a licence grant, copyright default is that nobody may
copy, modify, or redistribute it. Publishing source publicly is not a licence.
Mirroring such a plugin — which is exactly what this project does — is
infringement, and the fact that the author is unlikely to sue does not make it
lawful.

This is unresolved and it constrains Phase 1 scope.

**Required before any plugin is mirrored:** Tier A CI needs a licence gate,
running before any other check, with three outcomes:

| Detected licence | Outcome |
| --- | --- |
| None | **Reject.** Record a decision record stating the plugin was rejected for absence of a licence grant, not for a security finding. |
| Present but unrecognised | **Hold for human review.** A steward reads the actual terms and decides. Not automatable. |
| Recognised permissive (MIT, BSD-2/3, Apache-2.0, ISC, 0BSD, Unlicense, CC0) | **Proceed** to the security checks. |

Two consequences we should state plainly rather than discover later:

1. **The mirrorable plugin set is smaller than the brief's 276.** Some unknown
   fraction of that population carries no licence file at all. Every one of
   those is excluded on legal grounds before security review even begins.
2. **We do not yet know the real number.** The 276-plugin survey measured
   capabilities, not licences. Until the licence gate has been run across the
   candidate set, any scope figure that implies 276 mirrorable plugins is an
   assumption, and should be labelled as one wherever it appears.

A rejection for "no licence" is not a security judgement about the author's
work, and the decision record must say so explicitly. Under the roles in
[`CLAUDE.md`](../CLAUDE.md), authors are owed correct attribution and licence
compliance; implying that a lawyer-shaped rejection was a malware finding would
breach that.

The remedy is also worth recording: an unlicensed plugin becomes mirrorable the
moment its author adds a licence. Where a plugin is otherwise a good candidate,
the right move is to ask the author, not to route around them.

---

## Why Apache-2.0 for our code

MIT is the reflexive choice and it is shorter. It is the wrong choice here.
Four Apache clauses each do real work in this specific project — not as
boilerplate, but as mechanisms load-bearing for what this marketplace claims to
be.

### §3 — Patent grant

Each contributor grants an express, irrevocable patent licence covering their
contribution. MIT grants no patent rights at all; whatever patent licence it
implies is unwritten and untested.

This matters because the `PreToolUse` egress hook is a novel mechanism, not a
reimplementation of something well-trodden. Novel mechanism plus no express
grant is exactly the shape of a future problem: a contributor, or a company that
later acquires one, holding a patent claim over the thing everyone downstream is
now running. §3 also carries a retaliation clause — sue anyone over the Work's
patents and your own grant terminates — which makes the hook safe to adopt and
costly to weaponise.

### §4(b) — Notice of modified files

> "You must cause any modified files to carry prominent notices stating that You
> changed the files."

**This is the transform model, restated as a licence obligation.** The project's
core operation is taking an upstream plugin and modifying it to run under
declared, runtime-enforced permissions. Marking exactly which files we changed is
not an administrative chore attached to that work — it *is* that work, made
externally auditable. A user comparing our copy against upstream needs to know
which differences are ours.

§4(b) binds anyone downstream to the same discipline. Someone redistributing a
modified agent-orchard must disclose their modifications too. MIT imposes no such
duty, so a downstream party could ship a quietly altered egress hook while our
provenance claims travelled along unchanged.

### §6 — No trademark grant

> "This License does not grant permission to use the trade names, trademarks,
> service marks, or product names of the Licensor."

**The entire trust claim rides on the name.** Users install from here rather than
upstream because of what "agent-orchard" is supposed to mean: SHA-pinned,
reviewed, permission-declared. That reputation is the only thing distinguishing
this mirror from any other copy of the same code.

The concrete threat is a hostile fork that keeps the name — strips the egress
hook, adds a plugin we rejected, and publishes as "agent-orchard" — inheriting
trust it did not earn while users carry the loss. §6 makes the name a reserved
mark that the code licence does not convey. MIT is silent on trademarks, and
silence here is a gap in the one asset that protects users from an impostor.

The limit deserves stating: §6 is a reservation of rights, not an enforcement
mechanism. It preserves a trademark claim; it does not act on its own.

### §4(d) — NOTICE file

> "If the Work includes a 'NOTICE' text file ... You must include a readable copy
> of the attribution notices contained within such NOTICE file."

Attribution to upstream authors is an obligation this project owes under its own
roles, and §4(d) is the standard, machine-checkable place to discharge it. It
turns "we credit the people whose work we mirror" from a stated intention into a
licence term that travels with every redistribution. See [`NOTICE`](../NOTICE).

---

## Why not copyleft

GPL or AGPL would be the instinctive answer to "stop someone taking this and
running". It fails here for four separate reasons, any one of which is
sufficient.

1. **It cannot reach the vendored plugins.** Copyleft binds derivative works of
   code we hold copyright in. We hold no copyright in `plugins/**` — those are
   other people's works, mirrored under their terms. A copyleft licence on our
   code would not attach to them, and if it somehow did, that would be us
   relicensing work we do not own.

2. **It conflicts with mirroring permissive upstreams.** Most of what we mirror
   is MIT or Apache. Distributing a permissively licensed plugin as part of a
   copyleft aggregate invites exactly the combination questions that make
   downstream users' legal teams say no — over a plugin whose author licensed it
   freely and had no such condition in mind.

3. **It deters adoption.** The audience includes people at companies with
   blanket AGPL bans. Losing them costs users their defence and gains nothing.
   The security value here is in being *used*.

4. **It does not stop a hostile fork.** This is the decisive one. An actor
   willing to strip the egress hook and ship malware under our name is not
   deterred by a licence term — they simply ignore it. Copyleft is enforced by
   litigation, after the harm, against someone who by construction does not care.
   It buys users nothing against the threat it appears to address.

What actually protects the name is the trademark reservation in §6 plus the
release mechanics — signed tags, SHA pins, published decision records — that let
a user tell a genuine release from a copy. Licence choice is not a security
control, and treating it as one would be exactly the kind of overstatement
[`CLAUDE.md`](../CLAUDE.md) rules out.

---

## Why CC0 for registry data

`marketplace.json`, `registry/**`, and the decision records — including the
rejection log — are dedicated to the public domain under CC0-1.0. No permission
needed, no attribution required, no licence compatibility to check.

The rejection log is the reason. **A record of which plugins were rejected and
why is a security signal, and its value is proportional to how far it travels.**
Other scanners, dashboards, CI gates, and competing marketplaces should be able
to ingest it without a licence review, and without an attribution string
propagating through every downstream tool that touches it.

Attribution on a security feed buys users nothing. It buys stewards a credit
line — which, under the ordering in [`CLAUDE.md`](../CLAUDE.md), is not a reason
to put friction in front of a user's defence. If a competing marketplace consumes
our entire rejection log and never mentions us, users are safer and the project
has done its job.

CC0 rather than CC-BY or ODbL specifically because share-alike and attribution
terms on a data feed create precisely the aggregation friction that stops
security data from being pooled.

Two limits, stated so nobody relies on more than is there:

- CC0 covers our *compilation and expression* of the data. It does not and cannot
  waive rights in third-party material a record quotes or references.
- A public-domain dedication is not a warranty of accuracy. See below.

---

## What the licences do not promise

Apache-2.0 §7 disclaims all warranties and §8 disclaims liability, in full and in
capital letters. CC0 §4 does the same for the data. Everything in this repository
ships **as is**.

There is a real tension here and it should be named rather than glossed:
[`CLAUDE.md`](../CLAUDE.md) says users install from here because we promised them
a defence, and that promise is the product — while the licence we ship under
disclaims every warranty about it. Both are true. What resolves them is being
exact about what is actually being promised.

**The README, and any other public claim, must describe only what is actually
enforced:**

- plugins are **pinned by SHA**, not tracked by tag;
- changes go through **multi-maintainer PR review**;
- plugins run under **declared permissions**;
- those permissions are **enforced at runtime**.

Each of those is a mechanism that either ran or did not, and can be checked.

**No public claim may imply a guarantee of safety.** Not "safe", not "verified
secure", not "audited" without saying precisely what was audited and by whom, and
no phrasing that invites a user to skip their own judgement. Review reduces risk;
it does not eliminate it. A reviewed, pinned, permission-restricted plugin can
still be malicious — the controls narrow what a malicious one can reach, and that
is a materially different claim from safety.

The failure mode to avoid is a marketing line that promises more than §7 and §8
will stand behind. That gap would be borne entirely by users, who under our own
role ordering come first — which makes overclaiming not a marketing decision but
a security one.

---

## How this is applied

- Source files we author carry an SPDX identifier: `SPDX-License-Identifier: Apache-2.0`.
- Registry data files carry `SPDX-License-Identifier: CC0-1.0` where the format
  permits a comment; where it does not (strict JSON), the dedication is recorded
  here and in `LICENSE-DATA`, and mirrored in a sibling field or adjacent file
  rather than by breaking the format.
- Vendored plugins keep their upstream licence file verbatim, in place. We never
  rewrite, relocate, summarise, or "normalise" an upstream licence.
- Every vendored plugin's detected licence is recorded in its registry entry, so
  that the licence status of the whole marketplace is queryable rather than
  requiring a directory walk.
- Files we modify carry a modification notice, per §4(b).

## Open questions

These are unresolved at the time of writing and are recorded here so they are not
mistaken for settled:

- The licence gate described above is specified but not implemented. No plugin
  should be mirrored before it exists.
- The real count of mirrorable plugins is unknown. See the blocker section.
- Whether a plugin bundling a copyleft dependency can be mirrored at all is not
  yet decided, and needs an answer before the first such candidate arrives.
- Trademark posture beyond §6 — whether "agent-orchard" is registered, and who
  holds it — is undecided. §6 reserves the right; it does not establish one.
