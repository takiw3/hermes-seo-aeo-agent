---
name: structured-data
description: "Validate truthful, currently eligible structured data."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, specialization]
    related_skills: []
---

# Structured data

Design and validate machine-readable descriptions of visible content and real entities. Valid JSON, valid schema vocabulary and eligibility for a search feature are three different tests.

## When to use

Use for new templates, misleading markup, enhancement errors, product data inconsistencies or evaluating whether markup is worthwhile. Do not add schema because someone promises guaranteed AI citations.

## Inputs and prerequisites

Exact page/template, visible content, current JSON-LD/microdata/RDFa, confirmed business/product facts, intended feature and implementation owner. Use source-ledger and change-preview-rollback. Read current official type-specific docs in addition to G10, G16, G21 and G02. No extra API credentials are required for local review; testing tools may need authorized access.

## Procedure

1. **State the desired use.** Identify the visible entity and intended feature. Check whether Google currently supports that rich result and whether the site's page/content qualifies. Schema.org vocabulary availability alone does not establish Google support.
2. **Inspect existing markup.** Inventory all blocks and generators, including theme/plugin duplication. Identify entity IDs, references, types, URLs and conflicting values. Preserve the actual source and rendered versions when JavaScript alters them.
3. **Verify every business fact.** Match organization names, author identity, prices, availability, ratings, location, dates and policies to visible content and owner-approved evidence. Do not invent missing ratings, reviews, awards or credentials.
4. **Choose the smallest accurate model.** Use stable entity references, fully qualified URLs and appropriately connected page/entity nodes. Avoid irrelevant types and multiple competing entities just to maximize validator output. Prefer a maintainable source of truth over duplicate plugins.
5. **Check current eligibility requirements.** Record required and recommended fields from the exact feature guide with access date. Validate type-specific restrictions, page access, image accessibility and content policies. Unknown required facts block deployment rather than receive placeholders.
6. **Validate in layers.** Parse JSON locally with a tool; validate vocabulary/types with an appropriate validator; then use the relevant official rich-result test when available. Record errors and warnings separately. Manually inspect truthfulness because a validator cannot confirm real-world claims.
7. **Prepare the exact change.** Include markup, insertion/removal location, all affected templates, plugin ownership, before/after evidence and rollback. Owner approval must cover the actual production destination and payload.
8. **Verify after approved deployment.** Read back raw and rendered markup, compare visible facts, check duplicate generators and retest. Follow enhancement/indexing evidence later; rich result display is not guaranteed even with a clean test.

## Current feature caveat

As checked 2026-09-16, G21 documents that FAQ rich results stopped appearing starting May 7, 2026 and FAQ documentation was removed in June. Do not repeat the older restricted-government/health eligibility advice. Useful visible FAQs can remain useful content; FAQ markup is not an AEO requirement. G02 says there is no special schema required for Google generative AI features. Recheck current feature support before every new deployment.

## Artifacts

Entity/field provenance table, exact proposed markup and removals, validation results with dates, visible-content parity checklist, change preview and post-deployment test evidence.

## Evidence and unknowns

A local parser can prove syntactic validity, not eligibility. A rich-result test can identify supported types, not guarantee display or accuracy. Missing owner evidence is Unknown; never ship placeholder Unknown strings as product prices, URLs or names.

## Pitfalls

Avoid self-serving fabricated ratings, invisible FAQ answers, stale stock/prices, false authors, keyword stuffing inside properties, unnecessary schema graphs and treating warnings as automatic errors. Keep feature deprecations distinct from general vocabulary validity.

## Verification

Every material field has visible and/or permitted supporting evidence appropriate to the type; the intended feature is currently supported; all validation layers and limits are recorded; approval and exact readback exist for external changes. No ranking or citation promise appears.
