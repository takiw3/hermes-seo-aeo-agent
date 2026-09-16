---
name: search-measurement
description: "Reconcile search exports with business outcomes."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, evidence]
    related_skills: []
---

# Search measurement from exports or connected tools

Analyze actual GSC, GA4, Bing and business evidence without pretending a connector exists. Preserve metric definitions and data quality before explaining performance changes.

## When to use

Use for baselines, reporting, traffic changes, page prioritization and evaluating approved work. If a live integration is absent, request owner-approved exports and continue locally.

## Inputs and prerequisites

Exact property/account, export files or authorized existing tool, source/date window/timezone, filters, business conversion definition and baseline period. Optional revenue/lead quality exports, change log and AI reports. Use measurement-report, source-ledger and experiment-plan. Sources G17-G19 and B02. No GSC/GA4 API adapter is implied by this skill.

## Procedure

1. **Establish provenance.** Inventory supplied files, collection time, property, date range, report type, dimensions, filters, timezone, currency and extraction limits. Preserve originals; calculate hashes with a tool if needed. Never silently substitute another property's data.
2. **Inspect schema and quality.** Read headers, parse dates/numbers safely, identify duplicates, totals rows, missing values, row caps and incomplete latest days. Exported zeros may encode unavailable dash/tilde values; preserve a caveat if the original UI distinction is lost.
3. **Define comparable grains.** Keep query-page-country-device-date data at its real granularity. Do not sum overlapping exports or average preaggregated CTRs. Recompute CTR from summed clicks/impressions; compute changes and ratios with tools, handling zero denominators as undefined rather than infinite growth.
4. **Normalize URLs conservatively.** Preserve the raw URL, document parameter/trailing-slash rules and create an explicit canonical map. Do not merge distinct products/locales by accident. GSC canonical attribution and GA observed landing URLs can differ.
5. **Reconcile totals.** Count raw, duplicate, excluded and retained rows and compare report totals to computed totals. Query suppression and property-versus-page aggregation may explain differences. Report unresolved gaps; do not force numbers to match.
6. **Separate acquisition and behavior.** Use GSC for search impressions/clicks and GA4 for on-site sessions/key events. For comparable Google organic analysis, record source/medium filters and consent/tagging differences. Clicks are not sessions. GA property timezone can differ from GSC's PT reporting.
7. **Analyze cohorts.** Compare relevant time windows, seasonality, brand/nonbrand definitions, page types, countries/devices and important landing pages. Show volume and qualified outcome changes with uncertainty. Validate tracking breaks before content/ranking explanations.
8. **Report AI surfaces correctly.** G19 documents a separate Google generative-AI impressions report with page/country/date/device dimensions; access is verified in the owner's property or export. Do not fabricate AI-specific clicks, query-level attribution or revenue. Bing citation counts and grounding queries are separate measures, not positions.
9. **Connect to business carefully.** Link permissible landing-page outcomes to qualified leads/orders using defined IDs and privacy controls. Do not join anonymized search queries to individual buyers or allocate query revenue without a supported model. Attribution is descriptive unless a causal design supports more.
10. **Deliver decisions, not just charts.** State largest observed changes, data limitations, plausible causes and next tests/owners. Reporting does not authorize tracking-code edits, uploads, account links or external delivery.

## Artifacts

Completed measurement report, reproducible calculation notes, normalized derivative data, raw-file manifest, discrepancy table and action handoff. Keep customer identifiers out of broadly shared outputs.

## Evidence and unknowns

Missing data is Unknown, not zero. Average position is an aggregate Search metric, not a stable universal rank. Detected AI referrals omit visits where referrer information is absent. GSC AI impressions overlap Web report data; do not add them to Web totals as incremental impressions.

## Pitfalls

Avoid average-of-averages CTR, mixed currencies, mismatched windows, partial-day comparisons, cherry-picked cohorts, treating citation counts as sales and claiming this profile shipped a live API integration.

## Verification

All numerical results come from actual tool calculations; totals and row counts reconcile or have explicit exceptions; filters and metric definitions travel with every chart; conclusions distinguish observation, hypothesis and attribution. A reviewer can reproduce the main finding from the delivered inputs.
