---
name: content-refresh-cannibalization
description: "Refresh stale pages and resolve harmful intent overlap."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, editorial]
    related_skills: []
---

# Content refresh and cannibalization

Choose whether to update, differentiate, merge, retain or retire existing content using actual intent and performance evidence. Two pages sharing a query are not automatically cannibalization.

## When to use

Use for stale facts, declining useful pages, repeated intent overlap, uncertain consolidation or low-value archive cleanup. Do not delete pages merely because they are old or absent from a limited export.

## Inputs and prerequisites

URL inventory, current pages, owner goals, dated GSC/GA4 exports if available, backlinks/referrals, conversions, change history and business/seasonality context. Use audit-report, source-ledger, migration-map and change-preview-rollback. Sources G02-G04, G08-G09, G14 and G17.

## Procedure

1. **Validate the symptom.** Check data windows, seasonality, tagging changes, URL canonicalization and export completeness before attributing decline to content. Record affected cohorts and unaffected comparators.
2. **Inspect the page itself.** Identify outdated facts, broken steps, changed intent, missing evidence, poor task completion or a mismatch between promise and delivery. A fresh date without substantive improvement is not a refresh.
3. **Build the overlap set.** Compare actual audience, intent, offer, stage, geography and questions answered across candidate URLs. Review query/page distributions over time; swapping impressions can reflect intent changes or normal ranking variation.
4. **Distinguish useful plurality from conflict.** A guide and product page may serve different stages; language variants may be necessary. Harmful overlap needs evidence such as indistinguishable page promises, split useful information, inconsistent canonicals or users landing on the wrong experience.
5. **Choose a disposition per URL.** Retain when useful and accurate; refresh when facts/task support are weak; differentiate when distinct tasks were blurred; merge when one stronger page can preserve reader value; retire only when no replacement value exists. Explain the rejected alternatives.
6. **Preserve value during consolidation.** Inventory unique text, proof, assets, links, conversions and external references. Select the destination on task fit and evidence, not simply the shortest slug. Map exact old/new URLs; use relevant redirects rather than a homepage catch-all.
7. **Draft the substantive update.** Reverify time-sensitive claims, preserve useful material, add original proof and improve navigation. Record what changed and why. Do not expand to a word-count target or add synonyms mechanically.
8. **Prepare implementation controls.** Show content diff, metadata/canonical/link/redirect changes, backup, owner approval and rollback. Deletion or redirecting an existing URL is a separate consequential action requiring explicit approval.
9. **Measure after the approved change.** Read back content and redirects immediately. Observe chosen canonicals, query/page allocation, qualified landing outcomes and aggregate cohort performance after an appropriate processing window. Preserve concurrent-change caveats.

## Artifacts

Disposition matrix with evidence and confidence, revised draft, old/new mapping where relevant, change preview and post-change observation plan. Uncertain cases can receive a limited differentiation experiment rather than irreversible consolidation.

## Evidence and unknowns

No traffic in an export may mean truncation, filters, privacy suppression or an unmeasured channel. A decline following an update does not prove the update caused it. Missing backlink/conversion data raises consolidation risk and must be disclosed.

## Pitfalls

Avoid mass deletion to make a site seem fresh, merging distinct intents, losing original evidence, redirect chains, unexplained canonical changes and falsely labeling every multi-URL query as cannibalization.

## Verification

Every affected URL has a justified disposition; unique value and commercial paths are preserved; redirected destinations are relevant; approvals cover destructive actions; deployment and subsequent performance are reported separately. Unresolved measurements remain Unknown.
