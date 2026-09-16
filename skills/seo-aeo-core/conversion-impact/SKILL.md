---
name: conversion-impact
description: "Connect search changes to qualified customer outcomes."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, evidence]
    related_skills: []
---

# Conversion impact of search work

Evaluate whether search work helps the right visitors accomplish a valuable task. More clicks and more citations are not automatically more business value.

## When to use

Use when landing traffic underperforms, prioritizing SEO investments, evaluating content CTAs or designing a search-to-conversion experiment. Do not alter live forms, prices, consent or checkout without approval.

## Inputs and prerequisites

Business goal, confirmed offer, landing pages, conversion/qualification definitions, available analytics/CRM/order exports, baseline dates and recent changes. Use measurement-report, experiment-plan, audit-report and change-preview-rollback. Sources G17, G02-G03; verify current analytics documentation when interpreting a specific event or attribution model.

## Procedure

1. **Define valuable completion.** Specify purchase, qualified inquiry, booking, retained user or another owner-approved outcome. Separate micro-events such as CTA clicks from business outcomes. Identify measurement owner and fulfillment constraints.
2. **Validate instrumentation.** Inspect actual event definitions, duplicate firing, consent/tagging gaps, cross-domain paths, internal/bot traffic and available lead-quality linkage. A broken metric cannot diagnose a broken page. Do not claim data access without a working tool or export.
3. **Segment relevant traffic.** Compare organic landing cohorts by intent, brand/nonbrand where supported, device, country and page type. Keep GA session filters distinct from GSC acquisition metrics. Avoid assigning individual revenue to suppressed query data.
4. **Walk the customer journey.** Inspect mobile and desktop message match, proof, availability, price transparency, CTA clarity, form errors and next steps. Stop before submitting forms, contacting people or purchasing. Save evidence of observed friction.
5. **Separate findings from hypotheses.** 'The button returns 404' is observed; 'simplifying this form will raise qualified leads' is a hypothesis. Prioritize severe task blockers ahead of aesthetic preferences.
6. **Model impact as a scenario.** If needed, calculate outcomes from observed eligible sessions, an explicitly assumed rate change, qualification and unit value. Use tool arithmetic, show ranges and avoid double counting. Unknown rates/values remain Unknown; do not present a scenario as forecast certainty.
7. **Design a defensible test.** Specify unit, assignment, primary qualified outcome, sample/uncertainty, minimum observation window, harm guardrails and stopping rule. Include lead quality, margin, refund rate or accessibility where relevant. Low volume may support qualitative iteration rather than a powered A/B claim.
8. **Prepare exact change approval.** Show copy/UI/event diff, destination, time, risks and rollback. Pricing, privacy/consent and tracking changes require their accountable owner; an SEO brief grants none of these permissions.
9. **Verify and interpret.** Read back approved implementation and validate tracking in an authorized test path. Report effect with uncertainty and concurrent changes. Distinguish attributed outcomes from causal incremental outcomes.

## Artifacts

Journey evidence, metric-definition table, prioritized friction/hypothesis list, reproducible scenario if requested, experiment plan and outcome report. Link the recommendation to business value and customer usefulness.

## Evidence and unknowns

Analytics misses some consent-denied or untracked behavior. AI referrers do not capture all AI-influenced visits. Session conversion rates and user conversion rates have different denominators. Revenue without currency, refund treatment or period is insufficient for ROI.

## Pitfalls

Avoid rewarding low-quality lead volume, promising uplift, treating last-click attribution as causal, changing several variables without acknowledging it, dark patterns, hidden fees or inventing benchmark targets.

## Verification

The outcome definition is owner-confirmed; metrics and calculations are reproducible; observed friction has page evidence; hypotheses are labeled; tests have guardrails; external changes have exact approval/readback. Business impact claims match the strength of the design.
