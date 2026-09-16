---
name: topical-architecture
description: "Design useful topic coverage and site navigation."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, owner-reviewed]
    related_skills: []
---

# Topical architecture

Design a browsable knowledge and commercial structure around customer tasks. Topic coverage is an editorial model, not a measured Google 'topical authority' score.

## When to use

Use when a growing site has disconnected content, duplicated topic hubs, unclear navigation or a new product/knowledge area. Do not redesign stable URLs simply to fit a fashionable silo diagram.

## Inputs and prerequisites

Confirmed business scope, URL inventory, intent map, navigation/crawl sample, current CMS taxonomy and available expert proof. Use url-inventory, internal-link-plan and content-brief templates. Sources G02-G04, G08-G09, G15 and B01.

## Procedure

1. **Model audience tasks.** Group discovery, evaluation, purchase and implementation/support needs. Distinguish entities and relationships that matter to the reader from a list of keyword strings.
2. **Inventory present coverage.** Classify every known in-scope URL by task, template, locale, canonical and owner. Preserve uncertainty where CMS and crawl coverage disagree; do not call a page orphaned until checking a broader inventory.
3. **Define hub roles.** A hub must help users choose among useful destinations or complete an overview task. A pillar is not valuable merely because it is long. Define what the hub answers, what spokes answer and the next commercial or educational action.
4. **Draw the hierarchy.** Specify navigation labels, parent/child relationships, breadcrumbs and contextual cross-links. Permit cross-topic links when they help readers; artificial sealed silos can hide useful pages.
5. **Detect overlaps and gaps.** Compare sibling page promises and proof. Consolidation candidates need intent/performance/link review, while gaps require a real audience need and original contribution. Defer topics the business cannot substantiate.
6. **Handle scale and taxonomies.** Review tags, filters, archive pagination and faceted URLs for distinct usefulness. Do not index every combination. Preserve discovery paths to details without creating an unbounded crawl space.
7. **Sequence implementation.** Prioritize important existing-page repairs and links before new production. Identify CMS/developer dependencies, content owner and reviewer. Any URL change requires a migration map rather than an unexplained slug rewrite.
8. **Test the experience.** Walk representative customer journeys on mobile and desktop using authorized tools. Can a visitor locate proof, compare options and take the appropriate next step without search? Record actual broken paths and hypothetical friction separately.
9. **Deliver a bounded architecture proposal.** Include the graph/table, page contracts, migration implications and acceptance tests. External navigation, redirects or CMS changes need exact owner approval and readback.

## Artifacts

Architecture table: node ID, customer task, parent, canonical URL, page type, unique promise, source proof, outgoing/incoming links, owner and create/improve/retain decision. Provide a small representative journey test and prioritized brief backlog.

## Evidence and unknowns

Content coverage does not prove expertise; links do not prove authority. Missing analytics changes confidence in prioritization, not whether you can identify a broken navigation path. Label numerical depth thresholds as internal heuristics rather than search-engine requirements.

## Pitfalls

Avoid mass empty hubs, doorway locality branches, cannibalizing service pages with generic guides, global footer keyword links and destroying stable URLs to make a diagram tidy. Keep genuine regional and language variants distinct where users need them.

## Verification

Every proposed indexable node has a unique useful role, accountable owner and discovery path; no important node is intentionally orphaned. Existing URLs have disposition decisions, overlaps are explained and migrations are explicitly separated from content planning.
