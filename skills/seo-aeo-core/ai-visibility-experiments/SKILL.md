---
name: ai-visibility-experiments
description: "Test AI visibility with reproducible bounded samples."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, evidence]
    related_skills: []
---

# AI visibility experiments

Measure repeatable observations on named AI products without inventing a universal AI ranking. This skill produces an experiment and a defensible result, including an inconclusive one.

## When to use

Use to test citation accuracy, source appearance, answer completeness or a specific content/access intervention. Do not turn a few favorable screenshots into a cross-platform leaderboard.

## Inputs and prerequisites

Business question, fixed target pages, allowed products/tools, representative customer prompts, locales/languages, baseline and intervention proposal. Use experiment-plan, source-ledger and measurement-report. Sources G02, G19-G20, B01-B02, O01, A01 and P01. Paid tools or repeated automated requests require owner authorization and compliance with provider terms.

## Procedure

1. **Pre-register the decision.** State the hypothesis, treatment, alternative explanation, primary outcome, guardrails and what result would change the business decision. Citation increase without qualified demand may not justify production cost.
2. **Define the panel.** Sample prompts from actual customer tasks and measured research, including unbranded discovery, comparison and factual checks where relevant. Freeze exact wording and selection method before observing results; separate exploratory new prompts from the evaluation panel.
3. **Define observation conditions.** Record product, mode, model/version if exposed, search enabled/disabled, account state, locale, language, date/time and conversation reset method. Unknown model IDs stay Unknown. Fresh sessions reduce carryover but do not remove all personalization.
4. **Plan replication.** Specify repeats across times and matched conditions, valid-run criteria, missing/failed observations and uncertainty method. Product changes, stochastic responses and location variance are confounders, not errors to hide.
5. **Collect baseline evidence.** Preserve complete responses and cited links, not cropped favorable fragments. Record exact target/domain matches, brand mention, clickable citation, relevant recommendation and factual correctness separately. Inspect cited destinations to test actual claim support.
6. **Implement only the approved treatment.** Keep scope small, such as improving an original evidence section on a page. Preview exact payload/destination/time and rollback. No hidden instructions, fake endorsements, mass prompts designed to manipulate systems or deceptive pages.
7. **Collect post-treatment observations.** Follow the same frozen protocol and log concurrent site/product changes, recrawl evidence and timing. Do not discard null responses or failed calls without the preregistered rule.
8. **Analyze with tools.** Define mention/citation rate as runs with the specified event divided by valid eligible runs, while reporting failures separately. Use prompt-level or appropriately clustered uncertainty rather than treating repeated outputs as independent people. Report per-product outcomes; do not pool unlike surfaces into one rank.
9. **Triangulate, not conflate.** Compare manual observations with Google AI impressions, Bing citations and detected referrals where available. These populations differ; agreement adds context, not proof of causality or a shared denominator.
10. **Conclude honestly.** Report effect or descriptive variation, limitations, harms and adopt/repeat/revert/stop recommendation. A before/after design with no control cannot establish that the edit caused the change.

## Artifacts

Preregistered plan, frozen prompt panel, run manifest, full response/citation evidence, coded outcomes, reproducible calculations and result memo. If execution is blocked by access/terms, deliver the plan and blocker, not simulated results.

## Evidence and unknowns

Google AI-report impressions are not full answer text or a citation rank. Bing's sampled grounding queries do not reveal every user's prompt. A brand appearing in model memory differs from retrieval of the owner's page. Treat absent citations and incorrect citations as distinct failure modes.

## Pitfalls

No universal AI rank, cherry-picking, prompt drift mid-test, outcome-based stopping, unsupported causality, unapproved API spend or fabricated screenshots. Do not infer complete market share from a hand-built prompt sample.

## Verification

Every result maps to raw evidence and a valid-run rule; actual counts match the manifest; denominators and replication conditions are explicit; negative and missing results are visible; conclusions remain bounded to the sampled product, time and audience.
