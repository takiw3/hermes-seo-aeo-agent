---
name: migration-recovery
description: "Plan safe URL migrations and diagnose search losses."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, evidence]
    related_skills: []
---

# Migration planning and recovery

Preserve useful destinations and search continuity during moves, then distinguish expected processing from preventable breakage. Recovery starts with evidence, not mass redirects or repeated reversals.

## When to use

Use for domain/CMS/URL changes, redesigns affecting templates, or an organic traffic loss after deployment. A migration audit does not authorize DNS, hosting or production changes.

## Inputs and prerequisites

Owner-approved scope, old/new inventories, content and asset mappings, critical revenue pages, baseline exports, deployment timeline, backups, technical owner and rollback authority. Use migration-map, audit-report, measurement-report and change-preview-rollback. Sources G14, G08-G09, G11 and G17; re-read the complete official move guide before execution.

## Procedure

1. **Freeze the baseline and scope.** Record domain variants, protocol, subdomains, paths, assets, locale clusters, canonicals, robots/sitemaps and business outcomes. Identify concurrent redesign/content/analytics changes so their effects are not automatically attributed to the domain move.
2. **Build an exhaustive disposition map.** Combine CMS, crawl, sitemaps, analytics, links and logs where permitted. Each known old URL gets an equivalent new URL, justified consolidation, retained destination or genuine removal. Preserve evidence and mark inventory gaps.
3. **Review content equivalence.** Do not send unrelated deleted products/articles to a homepage. Include images, PDFs and other valuable assets. Choose appropriate permanent redirects for moves; validate actual status and final destination rather than assuming CMS behavior.
4. **Prepare new-site consistency.** Align internal links, self/cross canonicals, hreflang, structured-data URLs and sitemaps. Separate staging access protection from launch indexability. List precisely which test noindex or robots restrictions must change at launch.
5. **Test before launch.** Validate representative and high-value routes, redirect chains/loops, response content, mobile rendering, forms and analytics. Large mappings should be checked programmatically; counts must reconcile with the inventory. Keep tests within authorized nonproduction destinations.
6. **Create the release package.** Show exact changes, owner/implementer, execution time/timezone, acceptance thresholds, backups, rollback trigger and rollback side effects. Account-level submissions, DNS changes or Search Console actions require separate explicit approval.
7. **Verify approved deployment.** Read back critical old/new endpoints, redirects, canonical/hreflang/robots and tracking. Check all changed high-risk templates and mapped samples; report actual coverage. Do not declare success solely because the deploy command exited zero.
8. **Investigate losses systematically.** Compare affected cohorts and timeline. Test retrieval/indexability/canonical/tracking failures before assuming an algorithm change. Review available index/crawl evidence, demand seasonality and competitor changes; keep alternative causes visible.
9. **Choose recovery proportional to evidence.** Fix clear regressions with minimal scoped changes. Do not oscillate domains or undo a sound migration merely because visibility is temporarily unsettled. Keep redirects and monitoring for the period justified by current official guidance and business needs.
10. **Report layered completion.** Deployment verified, crawl/index processing pending, search demand observed and business recovery measured are separate statuses. Reassess against the agreed review window rather than guaranteeing a recovery date.

## Artifacts

Versioned URL map, baseline manifest, preflight test record, release/rollback plan, production readback and cohort-based recovery report. Record unmapped URLs and affected business risk explicitly.

## Evidence and unknowns

Search fluctuations can be normal during a move; that does not excuse broken routes. Missing historical exports limits attribution. A server log with no verified bot identity is not definitive Googlebot evidence. Distinguish a tool's sample from complete URL coverage.

## Pitfalls

Avoid irrelevant mass redirects, launching staging noindex, broken asset paths, redirect chains, stale alternates, unverified Change of Address assumptions, losing analytics continuity and claiming fixed rankings immediately after a redirect.

## Verification

Every known in-scope old URL has a disposition; critical routes are tested; launch controls match intent; exact owner approval exists; readback proves deployment; rollback is executable by an authorized operator. Remaining recovery uncertainty is stated, not hidden.
