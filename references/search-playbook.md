# Search operating playbook

## Working contract

Read the confirmed business profile first. Operate read-only or local-draft by default. External changes, including CMS drafts, publishing, future posts, GBP edits, IndexNow submissions, GSC settings, outreach and cron creation/editing, require explicit owner approval of exact payload, destination and time. A request to analyze is not a request to implement. Human-review instructions are behavioral policy, not a sandbox. Limit credentials, mounts and network access independently.

Resolve repository-relative paths from the installed profile or package root, not the caller's arbitrary cwd. Use `read_file`, `search_files`, `web_extract`, `web_search`, `terminal` and `write_file` as appropriate. Optional connected tools must actually exist and be authorized; otherwise work from exports. Store private outputs under `local/`, never overwrite templates. Do not claim a live API integration because a procedure can analyze CSV.

## Decision sequence

1. **Value:** Which customer task, offer, market and business outcome does this serve? If unknown, ask only what blocks the task.
2. **Evidence:** What is observed, on what exact URL/property/date range? Does the source cover the conclusion?
3. **Eligibility:** Can permitted crawlers retrieve and render the intended canonical page? Is the page indexable, snippet-eligible and included under applicable Search Console AI control? Treat actual index selection as a separate observation.
4. **Differentiation:** What original proof, expert explanation, comparison, tool or experience makes the page worth choosing? A rewritten competitor paragraph is not differentiation.
5. **Action:** Repair, improve, consolidate, create, experiment, defer or decline. Prefer fixing an important existing page to manufacturing a new near-duplicate.
6. **Impact:** Name the intended leading signal and business measure. Forecasts are scenarios with explicit assumptions, not rankings promised.
7. **Review:** Produce change preview, exact approval request, verification test and rollback. Stop at draft until approved.
8. **Learning:** Read back approved external changes; distinguish successful deployment from indexing or performance outcomes.

## Evidence vocabulary

- **Observed:** directly inspected with URL/property/export and timestamp.
- **Documented:** official vendor guidance, cited with access date.
- **Inferred:** interpretation of observations, with alternatives and confidence.
- **Hypothesis:** falsifiable expectation with a planned experiment.
- **Unknown:** unavailable, withheld, unmeasured, extraction-limited or contradictory. Never silently replace with zero.
- **Not applicable:** reason recorded, not an excuse to skip a relevant check.

The source ledger carries claims; the audit report carries findings; the change preview carries authorization; the outcome log carries measured results. These are different artifacts.

## Prioritization without fake precision

Classify critical availability/security/indexing blockers before cosmetic improvements. Within a tier compare business value of affected pages, observed reach, confidence, risk, effort and dependencies. If using a numeric score, define scales and compute with a tool. Missing traffic is Unknown, not 'zero opportunity'. Report estimated effort bands as estimates. A high crawler warning count does not automatically mean high business impact.

## Current AEO boundaries

Read source IDs in `references/seo-source-register.md`. G02 rejects special Google AI schema, required llms.txt, forced tiny chunks and manufacturing every query variation. Helpful direct answers are an editorial choice for readers, not a citation formula. G19 now documents separate generative-AI **impression** reporting; do not fabricate AI-specific clicks, CTR, queries or revenue if not available. G20 is an inclusion control, not a ranking boost. Google-Extended is not a Google Search ranking/inclusion control. OpenAI, Anthropic and Perplexity search/training/user-fetch roles must be assessed independently.

Do not combine Google AI impressions, Bing citations, manual answer observations and analytics referrals into a fake cross-platform rank. Each measures a different population. Evidence of appearance is not evidence of influence or incremental revenue.

## Minimum handoff

State objective, scoped properties, evidence window, delivered artifact paths, top decision, unknowns, reviewer, exact next action and permissions not granted. Provide URLs plus selectors/response excerpts for technical findings; provide claim-source mappings for prose. A recipient profile ID must be owner-confirmed. Draft a handoff when routing is unknown; do not broadcast.

## Stop conditions

Stop affected work on unclear domain ownership, credentials in source material, robots/WAF denial, stale approval, payload drift, uncertain remote write, unexpected destination redirect, prohibited tactics, unverified business claims or insufficient qualified review. Keep safe analysis moving and state the smallest missing input. Never solve access failure by inventing metrics or bypassing restrictions.
