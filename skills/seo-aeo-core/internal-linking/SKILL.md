---
name: internal-linking
description: "Plan contextual links and verify discovery paths."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, editorial]
    related_skills: []
---

# Internal linking

Improve discovery and reader navigation with exact, contextual link changes. Link-count quotas and anchor repetition are not the goal.

## When to use

Use for orphan important pages, refreshed content, architecture implementation, redirect cleanup or poor customer journeys. Do not perform sitewide anchor replacement without reviewing context.

## Inputs and prerequisites

Allowed domain, URL inventory, canonical and status evidence, topic/page roles and content snapshots. Optional crawl graph and page-level business outcomes. Use internal-link-plan and change-preview-rollback. Sources G08-G09, G15 and B01.

## Procedure

1. **Build the usable graph.** Extract actual source/target pairs from permitted content or a crawl. Retain raw URLs and distinguish navigation, breadcrumbs, body links and image links. Resolve relative references using the correct page base; keep fragments when they identify a useful destination section.
2. **Identify important discovery gaps.** Compare graph coverage to CMS/sitemap/analytics inventory. A page absent from a bounded crawl is a possible orphan, not a proven one. Prioritize business-critical pages and useful reader journeys.
3. **Validate candidate targets.** Check final status, redirects, intended canonical, language and indexability as appropriate. A private utility page can be useful to users without being an SEO target; do not force it into the index.
4. **Select contextual sources.** Choose existing sections where the target genuinely answers a next question. Document the reader benefit. Prefer relevant body context over global boilerplate added solely for ranking signals.
5. **Draft exact anchors and placements.** Supply source URL, paragraph/heading locator, current anchor/target and proposed anchor/target. Anchor text should set accurate expectations when read alone. Use standard crawlable `<a href>` links; image links need appropriate descriptive alternatives.
6. **Check intent and duplication.** Avoid linking to the wrong regional/product variant, unnecessary redirects, broken fragments, every occurrence of a keyword or excessive competing CTAs. Cross-topic links are acceptable when genuinely useful.
7. **Review the batch.** Group by template and failure risk; preview the complete payload/diff, count changes with a tool and provide rollback. Request owner approval for exact external edits, not a generic 'improve links' permission.
8. **Verify approved changes.** Re-fetch source and target, inspect rendered clickability and anchor context, and recompute affected discovery paths. Confirm no link was injected into forms, hidden content or user-generated areas unexpectedly.
9. **Observe useful outcomes.** Track improved reachability and relevant user paths first; search impact is uncertain and may lag. Do not claim PageRank transferred by a particular amount or guarantee ranking movement.

## Artifacts

Versioned CSV link plan, coverage explanation, source/target validation evidence and per-batch change preview. Include omitted candidates and reasons where the target is unavailable, wrong-language or not useful.

## Evidence and unknowns

Raw graph counts depend on crawl coverage and parser behavior. JavaScript-inserted links may need rendered verification. Absence of a link in source HTML does not prove no rendered link; a styled button without href may not be a crawlable navigation link.

## Pitfalls

There is no magical ideal number of links. Do not use keyword-stuffed anchors, hide links for crawlers, build rigid silos that hurt navigation, or add tracking/session parameters to stable internal destinations. Avoid changing all navigation merely because a graph metric is low.

## Verification

Every proposed link has a source locator, useful anchor, valid target and reader rationale; important in-scope pages have a documented discovery route; changed links are read back after approval; measured coverage and remaining unknowns are reported honestly.
