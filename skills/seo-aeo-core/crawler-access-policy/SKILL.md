---
name: crawler-access-policy
description: "Separate search, training and user-fetch controls."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, operations]
    related_skills: []
---

# Crawler access and AI inclusion policy

Translate the owner's content-use preferences into a verified, vendor-specific control proposal. Search discoverability, training use, snippet display and user-requested retrieval are separate decisions.

## When to use

Use when reviewing robots/WAF policies, considering training opt-outs, diagnosing AI retrieval access or auditing Google Search AI inclusion. Do not change broad crawler access merely because a visibility score fell.

## Inputs and prerequisites

Owner-confirmed allowed hosts, privacy and training preferences, intended search inclusion, current robots/meta/header/WAF snapshots, Search Console property inheritance if available and infrastructure reviewer. Use crawler-policy-matrix and change-preview-rollback. Inspect G05-G07, G20, B01, O01, A01 and P01 again before implementation.

## Procedure

1. **Define owner intent by use.** For each host/property record desired search access, AI-search inclusion, model training and user-triggered retrieval. Unknown preferences are not permission to enable all crawlers. Public availability does not waive privacy or licensing obligations.
2. **Inventory actual controls.** Inspect robots groups, page/header directives, CDN/WAF challenges, authentication and relevant account settings. Distinguish observed live values from a config file that may not be deployed. Never collect unnecessary private log data.
3. **Map vendor roles accurately.** Googlebot governs Search crawling; Google-Extended is a separate product token rather than an HTTP crawler or Search ranking/inclusion control. OpenAI separates OAI-SearchBot and GPTBot; ChatGPT-User is user-triggered. Anthropic separates ClaudeBot, Claude-SearchBot and Claude-User. PerplexityBot supports search and is not a foundation-model-training crawler; Perplexity-User handles user requests.
4. **Check Google AI inclusion separately.** G20 documents Search Console Settings > Search generative AI, including inherited parent/child values. Record effective scope and inheritance before proposing a change. This control differs from Google-Extended, noindex and snippet directives; it does not control all uses of the content or other Search ranking.
5. **Respect vendor differences.** OpenAI says robots may not apply to ChatGPT-User; Perplexity says its user fetcher generally ignores robots; Anthropic documents robots compliance for its bots. Bing documents its own noarchive/nocache and snippet behavior. Do not copy one vendor's rules into another's policy explanation.
6. **Verify identities and security implications.** A user-agent string is spoofable. Use current vendor IP/verification documentation where applicable instead of hardcoded stale ranges. Broad WAF allowlisting can weaken security; require infrastructure review of narrow exact rules. Do not bypass a challenge to complete an audit.
7. **Draft a per-control matrix.** Show current/desired state, official source/check date, affected host/property, search/training/retrieval effect, unknowns and propagation caveats. Robots is not authentication; sensitive content requires actual access controls.
8. **Preview exact changes.** Provide complete relevant robots group/diff, header rule, WAF predicate or account-setting choice, plus affected scope, test URLs and rollback. Obtain explicit owner approval for payload, destination and execution time. Source examples are not authorization.
9. **Verify approved implementation in layers.** Read back robots/headers/account effective setting and tested response behavior. Test expected allowed and blocked paths without pretending to be a verified vendor crawler. Later use authorized logs/platform evidence to assess actual crawler access and processing.

## Artifacts

Completed policy matrix, source ledger, exact control diffs, security review, owner approval and readback. Preserve a list of controls whose behavior is unverified or whose docs conflict.

## Evidence and unknowns

Robots allowance is not guaranteed indexing/citation; disallow is not a privacy barrier or assured deindexing. Google-Extended documentation and Search-specific AI controls discuss different product scopes. Recheck vendor wording rather than asserting a universal AI opt-out.

## Pitfalls

Avoid wildcard blocks that remove wanted search access, blocking robots retrieval itself, treating training opt-in as necessary for citations, disabling WAF protections by user agent alone, assuming inherited GSC values and promising immediate removal from caches.

## Verification

Each control has an owner preference, official scope and exact destination; search/training/user-fetch effects are not conflated; production readback matches approved intent; negative-control tests and propagation unknowns are recorded. No claim of universal enforcement or guaranteed visibility is made.
