# Before production use

This is a tested profile distribution with deterministic tools, not a guarantee that every model or business integration behaves reliably. Start in research-and-draft mode.

## Owner acceptance

1. Install into a separate profile and configure its own model/provider. Confirm a real chat response, identity and permission limits.
2. Complete the business template using reviewed facts. Confirm allowed domains, language, timezone, claims, original proof and reviewer.
3. Run a small audit. Compare its findings against the source page and a rendered browser. Record blocked pages and manual checks.
4. Review one full content draft for factual accuracy, usefulness, brand fit, sources, originality and regulated claims. Do not infer quality from the presence of an SEO checklist.
5. Evaluate relevant [model scenarios](../evals/acceptance-scenarios.md) with no publisher credentials. Record actual traces and failures.

## Optional WordPress acceptance

Use only a separately authorized staging site and dedicated limited account. The owner must approve both credential setup and the exact test post. The agent does not perform these owner-only operations.

- Confirm the canonical HTTPS root origin, REST compatibility, Author permissions and application-password handling.
- Review the exact article/time preview and one-use approval. Submit only through the documented owner-operated workflow.
- Confirm the read-back receipt matches every approved field and the remote post is actually `future`.
- Verify eventual publication separately against WordPress. A scheduling receipt is not proof of exact-time publication.
- Have the owner clean up the staging post directly; the helper does not implement remote deletion or unscheduling.
- Rehearse ambiguous-outcome recovery without repeating a potentially applied create. Protect the single canonical queue and its backups.

See [scheduling](../references/scheduling.md) and [WordPress setup](../references/wordpress-setup.md). If you cannot establish a safe staging environment, leave submission disabled and use local content exports.

## Optional recurring work

Start with a manual weekly review. Activate draft-only cron only if the owner approves its exact purpose, inputs, outputs, time, cost and boundaries, and publisher credentials are demonstrably absent from that runtime. Read back the job and verify an explicitly authorized test run. Otherwise stay manual.

## Business outcome validation

Set baselines before changes. Use current GSC/Bing/analytics definitions and comparable windows. Separate branded/nonbranded demand where data supports it, record confounders and use qualified leads or profitable purchases where measured. AI citations, impressions, sessions and revenue are different quantities. No comparison or market-leading claim is justified without an actual controlled benchmark.
