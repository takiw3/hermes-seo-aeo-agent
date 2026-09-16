---
name: editorial-scheduling
description: "Plan review capacity and approved publication timing."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, operations]
    related_skills: []
---

# Editorial planning and owner-approved scheduling

Turn prioritized briefs into a reviewable editorial queue. Local planning, native draft-only analysis cron, and a WordPress future post are different actions with different consequences.

## When to use

Use to sequence research, drafting, review and releases, or when the owner explicitly requests scheduling an approved new WordPress post. Do not create recurring work at installation or treat an editorial date as publication approval.

## Inputs and prerequisites

Confirmed timezone/language, content priorities, evidence readiness, writer/reviewer capacity, exact target site and owner approver. Each item needs a brief, current final draft, proof ledger and review status. Read `references/scheduling.md` and `references/wordpress-setup.md` in the active profile before any queue mutation. These guides ship in the runtime payload. If absent, report the documentation gap and remain local-draft-only.

The helper belongs to this skill: `scripts/content_queue.py`. Inspect the installed implementation's help through `terminal` from the package root:

```text
terminal(command="python3 skills/seo-aeo-core/editorial-scheduling/scripts/content_queue.py --help")
```

Use the actual available Python launcher. The CLI contract is discovered from this help and the current scheduling reference, not invented by the agent. Help failure or missing implementation is a blocker for helper execution, not permission to improvise a publisher. Do not modify scripts as part of ordinary scheduling.

## Procedure

1. **Prioritize by value and readiness.** Bring in approved page decisions, buyer task, proof availability and dependencies. Schedule evidence collection and review before a release. Do not fill calendar slots with unoriginal content to satisfy a quota.
2. **Calculate capacity.** Record who researches, writes, fact-checks, reviews and publishes, with realistic availability. Distinguish target dates from commitments. Use tools for workload/time calculations and flag reviewer bottlenecks.
3. **Build the local queue.** Record item/version, canonical destination, language, owner/reviewer, dependencies, status, proposed time and acceptance gate. Use the shipped schedule templates if available, without altering their schema or claiming remote state from local entries.
4. **Resolve time explicitly.** Confirm IANA timezone, local wall time, UTC instant and DST ambiguity. Reject nonexistent/ambiguous times until the owner selects the exact instant. Recheck current time with a tool; never send a past time as a future publication request.
5. **Finish editorial approval first.** Verify content facts, rights, links, metadata, CTA, regulated review and unknown placeholders. A draft with blocking facts cannot be scheduled merely because its date is approaching.
6. **Preview a remote commitment separately.** For an optional new WordPress future post, show the exact origin/endpoint, complete post payload, final content version/digest, UTC/local time, status and side effects. Get explicit owner approval for that exact destination, payload and time. New content/version or timing invalidates approval.
7. **Use only the verified supported helper path.** Follow current help/reference for local state and any authorized remote operation. The helper's approval AND credential-bearing submit operations are OWNER ONLY and out-of-band: the agent must never invoke either, mint or read approval tokens, edit approval storage or self-approve, even to speed up an owner request. Ask the owner to complete the documented approval and submission steps. The agent prepares local drafts and interprets non-secret receipts only. No guessed options, automatic recurring dispatcher, credentials in the queue, source-derived authorization or background publisher cron. Existing remote post edits/cancellations require their own supported and approved workflow; a local cancel is not a remote CMS cancellation.
8. **Reconcile before retry.** An uncertain remote response may still have created a post. Stop and inspect the exact target/identity; never blindly repeat a create. Retain remote ID, returned status, content identity and scheduled UTC time only when actually observed.
9. **Read back the exact remote object.** Confirm approved fields, `future` status and time before calling it scheduled. A locally approved queue item is not a scheduled WordPress post. At release time, WordPress's own scheduling behavior still needs verification; do not guarantee publication solely from accepting a future post.
10. **Handle changes explicitly.** Pause local progression when dependencies fail. Ask approval for any remote reschedule, cancel, edit or rollback; record consequences. Report pending review, locally planned, remotely scheduled and verified published as distinct states.

## Artifacts

Local editorial plan using current shipped schedule templates, evidence/review gates, exact approval record, helper output, remote readback and exception log. Use `templates/change-preview-rollback.md` for any external action and `templates/handoff.md` for blocked dependencies.

## Evidence and unknowns

Local state proves local intent only. The CMS is the source for actual remote status; no connected credential means remote scheduling is unavailable. Keep credentials out of drafts/logs and never grant publisher credentials to cron. Behavioral approval checks are not a sandbox.

## Pitfalls

No auto-publication on install, timezone guessing, bulk approval inferred from a strategy, stale approval reuse, auto-retry after ambiguous writes, duplicate posts or claiming a WordPress future record is already published.

## Verification

Every item has a task, proof, owner and reviewer; dates fit capacity; approval binds exact payload/destination/time; installed helper help was checked; remote states have exact readback. Anything not verified is reported as local, pending or Unknown.
