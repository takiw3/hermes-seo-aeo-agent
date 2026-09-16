# Hermes SEO & AEO Agent

**Help the right customers find your business in Google and AI answers. Turn search research into useful content and concrete website improvements.**

A persistent [Hermes](https://hermes-agent.nousresearch.com/docs/) profile named `seo-aeo` for business owners who need an organic-search specialist inside their **TakiGPT AI Agentic Workforce**. It researches, audits, writes, prioritizes and measures. It starts with a blank business template and adapts to your offers, customers, market, voice and goals.

- **Author:** Taki Wong / TakiGPT AI Inc.
- **Profile ID:** `seo-aeo` · **Display name:** SEO & AEO
- **Version:** 1.0.0 · **License:** [MIT](LICENSE)
- **Default mode:** research and local drafts. Optional WordPress scheduling is owner-operated.

SEO improves your eligibility and usefulness in search. AEO (answer engine optimization, often called GEO) focuses on how your business and information can be discovered, understood and cited in AI answers. They share foundations; neither offers guaranteed placement.

## Who it is for

Business owners, entrepreneurs and small teams running service businesses, local businesses, ecommerce stores or B2B companies. Use it as your standalone search specialist or alongside a chief of staff, Marketing, Sales, Support, Ads and Developer profiles.

## What it does for your business

- **Find what is holding your website back.** Audit accessible pages, identify metadata and internal-link issues, review crawl/index signals and produce a prioritized fix list with evidence.
- **Create content worth finding.** Research customer questions and intent; develop briefs and complete original articles, service pages, product/category copy and answer sections with supported claims.
- **Improve AI discoverability without gimmicks.** Build clear, factual, source-worthy information, credible business/entity signals and product-specific crawler policies. Test citations rather than inventing an “AI rank.”
- **Turn recommendations into implementation-ready work.** Produce before/after copy, metadata, schema drafts, link plans and developer change specifications with acceptance tests and rollback.
- **Keep useful content current.** Diagnose overlap and declining pages, prioritize refreshes and organize a reviewable editorial calendar.
- **Connect search work to business value.** Analyze approved search/analytics exports, qualified demand and conversion evidence. Separate measured results from hypotheses.
- **Schedule deliberately.** Prepare a local content queue. An optional adapter lets the owner approve and submit new future-dated WordPress posts. Draft/report routines can be configured through native Hermes cron after separate opt-in.

**No ranking, citation, indexing or revenue guarantees.** “Most capable on the market” is not a substantiated claim. The package is designed for depth, verifiable work and explicit limits, not search manipulation or unattended mass publication.

## Real automation versus guided work

| Capability | What ships |
|---|---|
| Website crawling | Executable HTTPS static-HTML auditor, bounded to one origin, robots-aware, public-IP/TLS-pinned, with evidence and coverage |
| Research and content writing | Focused Hermes skills and templates; requires your configured model and available research tools |
| Local content queue | Executable SQLite queue, canonical content preview, exact digest and state tracking |
| WordPress future posts | Optional owner-operated adapter with expiring single-use approval, one POST attempt and exact remote read-back |
| Recurring content drafts/reviews | Native Hermes cron procedure, configured only with owner approval; no jobs ship or activate |
| GSC, GA4, Bing, GBP, Merchant Center | Export-analysis workflows or your separately connected read tools; no bundled account connector |
| Existing website edits and other CMS platforms | Finished content/change sets and owner/developer handoffs; no generic automatic deployment adapter |

The model writes the content. The deterministic tools crawl and manage the queue. Offline tool tests are not a model-quality benchmark or a live-CMS certification.

## Install

Requires **Hermes 0.20.0+**, Git, and **Python 3.10+** for the included helpers. The installation floor exists for path-aware distribution ownership. Runtime helpers use only Python's standard library. Configure your own model/provider after installation.

```bash
hermes profile install https://github.com/takiw3/hermes-seo-aeo-agent --alias
hermes -p seo-aeo model
hermes -p seo-aeo chat
```

`--alias` is an on/off flag and creates the `seo-aeo` shortcut. Review the manifest when prompted. Use `--yes` only after reviewing and trusting the repository. For a local checkout, use `hermes profile install /absolute/path/to/hermes-seo-aeo-agent --alias`.

Installation copies only identity, config, skills, references and templates into the profile. It does **not** configure a model, copy another agent's credentials, create a bot, connect a CMS, start onboarding, schedule a job or publish anything. An installed profile becomes usable only after model configuration and a successful conversation.

## First conversation

> My website is [URL]. We sell [offer] to [customer] in [market]. Our goal is [qualified leads or profitable sales]. Configure this agent for my business, audit the highest-value pages and recommend the first three actions. Do not publish or schedule anything.

The agent begins with the [business template](templates/business-profile.yaml), learns progressively, and saves your confirmed operating profile under `local/business-profile.yaml`. Unknown facts remain Unknown. You control voice, market, language, timezone, proof, allowed domains, reviewers and teammate IDs. See [onboarding](docs/onboarding.md).

## Example tasks

- “Audit up to 10 accessible pages on [website]. Show evidence, coverage limits, the top issues and exact acceptance tests. Do not change the site.”
- “Using these Search Console exports and our approved offer, map high-value customer intent to existing pages. Separate measured demand from guesses.”
- “Create a complete SEO/AEO article from this approved brief and our original research. Include supported claims, title, description, link suggestions and source ledger. Flag missing proof.”
- “Rewrite this service page for [audience/location] using only verified services and proof. Show before/after copy and useful schema proposals.”
- “Build an AI visibility experiment for our buyer questions across the platforms I can access. Record the exact prompts, date, locale, model/surface and citation evidence.”
- “Create a month of content briefs based on review capacity, not a content quota. Keep everything local.”
- “Prepare this approved WordPress article for [exact future time and timezone]. Show the complete payload and owner-operated approval/submission steps. Do not submit it yourself.”
- “Review this migration plan for redirects, canonicals, hreflang and measurement risks. Give our developer a staged change set and rollback checklist.”

## Included skills

There are **23 focused skills**, each with inputs, procedures, artifacts, pitfalls and verification.

| Skill | Produces |
|---|---|
| [onboarding-business-strategy](skills/seo-aeo-core/onboarding-business-strategy/SKILL.md) | Owner-confirmed operating profile and prioritized search growth plan |
| [site-audit](skills/seo-aeo-core/site-audit/SKILL.md) | Bounded website audit with page evidence, coverage and fix priorities |
| [technical-seo](skills/seo-aeo-core/technical-seo/SKILL.md) | Crawl/indexing, rendering and performance diagnostic change specifications |
| [keyword-intent-mapping](skills/seo-aeo-core/keyword-intent-mapping/SKILL.md) | Buyer-intent map with target pages, proof needs and evidence-labeled demand |
| [topical-architecture](skills/seo-aeo-core/topical-architecture/SKILL.md) | Topic clusters, page roles and navigation architecture without doorway spam |
| [answer-citation-strategy](skills/seo-aeo-core/answer-citation-strategy/SKILL.md) | Answer coverage and first-hand evidence plan for search-backed AI discovery |
| [content-briefs](skills/seo-aeo-core/content-briefs/SKILL.md) | Research-backed page brief, outline, evidence requirements and acceptance checks |
| [source-grounded-content](skills/seo-aeo-core/source-grounded-content/SKILL.md) | Complete original article/page drafts, source ledger, metadata and CTA |
| [content-refresh-cannibalization](skills/seo-aeo-core/content-refresh-cannibalization/SKILL.md) | Refresh/merge/retain decisions with overlap evidence and rollback criteria |
| [internal-linking](skills/seo-aeo-core/internal-linking/SKILL.md) | Exact source-to-target link plan with anchors, placement and relevance |
| [structured-data](skills/seo-aeo-core/structured-data/SKILL.md) | Visible-content-grounded JSON-LD drafts and validation plan |
| [local-business-seo](skills/seo-aeo-core/local-business-seo/SKILL.md) | Accurate location/service-area content and Business Profile improvement plan |
| [ecommerce-product-seo](skills/seo-aeo-core/ecommerce-product-seo/SKILL.md) | Product/category discovery, variants, feeds and structured-data recommendations |
| [international-seo](skills/seo-aeo-core/international-seo/SKILL.md) | Language/region URL and reciprocal hreflang implementation specification |
| [ethical-digital-pr](skills/seo-aeo-core/ethical-digital-pr/SKILL.md) | Original-asset and editorial outreach drafts without bought links or fake authority |
| [search-measurement](skills/seo-aeo-core/search-measurement/SKILL.md) | GSC/GA4/Bing export analysis with definitions, denominators and caveats |
| [ai-visibility-experiments](skills/seo-aeo-core/ai-visibility-experiments/SKILL.md) | Repeatable query/prompt panels and product-specific citation experiments |
| [migration-recovery](skills/seo-aeo-core/migration-recovery/SKILL.md) | URL redirect map, release checklist, monitoring and recovery runbook |
| [conversion-impact](skills/seo-aeo-core/conversion-impact/SKILL.md) | Qualified-demand and conversion analysis, assumptions and experiment proposals |
| [editorial-scheduling](skills/seo-aeo-core/editorial-scheduling/SKILL.md) | Review-capacity calendar, local content queue and owner-approved WordPress package |
| [crawler-access-policy](skills/seo-aeo-core/crawler-access-policy/SKILL.md) | Search/training/retrieval policy matrix and exact owner-reviewed control changes |
| [draft-only-cron](skills/seo-aeo-core/draft-only-cron/SKILL.md) | Opt-in native Hermes drafting/reporting routines with explicit boundaries |
| [weekly-review-handoffs](skills/seo-aeo-core/weekly-review-handoffs/SKILL.md) | Decision-focused search review and redacted specialist handoffs |

## Try the executable tools

From the repository checkout, or the installed profile root after resolving its real path:

```bash
# A bounded public-site audit. Replace the URL with your intended website.
python3 skills/seo-aeo-core/site-audit/scripts/audit.py \
  --url https://www.example.com --max-pages 10 --output audit.json

# Inspect the queue interface. This does not connect WordPress.
python3 skills/seo-aeo-core/editorial-scheduling/scripts/content_queue.py --help
```

The audit output must be a **new file**. The crawler stops on missing, redirected, unreadable or unsupported robots rules rather than bypassing them. It does not crawl queries, HTTP sites, non-443 ports, sitemaps or JavaScript-rendered content. You can analyze an owner-provided HTML file offline; see the [audit guide](skills/seo-aeo-core/site-audit/scripts/README.md).

For scheduling, follow [the complete workflow](references/scheduling.md) and [WordPress setup](references/wordpress-setup.md). A local queue entry is not a remote schedule. A verified `future` post is not a published post. WordPress publication timing depends on its scheduler infrastructure. An uncertain write is never automatically retried.

## Works with your workforce

The profile routes by verified owner-configured teammate IDs, not hardcoded names. Marketing supplies brand/offer truth; Sales supplies lead-quality evidence; Support supplies redacted questions; Dev owns implementation; Ads owns paid media; your chief of staff coordinates priorities.

It also works alone. When a teammate or connector is missing, it gives you the finished artifact instead of inventing a handoff. See [team handoffs](docs/team-handoffs.md).

## Permissions and privacy

Local drafts and approved research are the default. External changes, publishing, recurring jobs, private-data access, spending and outreach require explicit owner approval. WordPress approval and credential-bearing submission remain owner-operated outside the agent. Credentials are not shared across profiles.

**This is not a security sandbox.** Hermes approval settings apply to commands it classifies as dangerous. Profiles on one OS account share filesystem access, and a local approval database cannot authenticate a human against another same-user process. Keep publisher credentials outside the agent runtime; use OS-level isolation for stronger guarantees. See [permissions](docs/permissions.md) and [security](SECURITY.md).

## Update and remove

```bash
hermes profile update seo-aeo
# Destructive: removes your installed profile. Back up owner data first.
hermes profile delete seo-aeo
```

Updates replace only the declared distribution-owned paths. `local/`, credentials, memories, sessions, additional owner skill namespaces and ordinary `config.yaml` overrides are preserved. Do not put custom work under `skills/seo-aeo-core/`, `templates/`, `references/` or SOUL.md and expect it to survive updates. This is a preservation contract tested with sentinels, not a replacement for backups.

## Testing and known limits

See [test evidence](docs/testing.md) for actual execution results, installer identities and what remains untested. Follow [production acceptance](docs/production-readiness.md) before using private accounts or scheduling live content. [Reference review](docs/reference-review.md) records how the five supplied repos informed this distribution. [Search sources](references/seo-source-register.md) distinguishes current official guidance from hypotheses.

No live owner account, publisher credentials, actual business data or activated automation is bundled. No universal rank tracker, paid keyword dataset, JavaScript renderer, full backlink index, arbitrary CMS writer or autonomous publisher is claimed. No model-backed evaluation, live WordPress scheduling or end-to-end multi-agent routing is implied by offline tests.

## Development

```bash
# Use an isolated environment; PyYAML is for repository validation only.
uv run --no-project --with pyyaml python -m unittest discover -s tests -v
uv run --no-project --with pyyaml python scripts/validate.py
uv run --no-project --with pyyaml python scripts/test_install.py
```

See [contributing](CONTRIBUTING.md) and [attribution](THIRD_PARTY_NOTICES.md).

## Build your Agentic Workforce

Learn how to build and operate business AI agents in the [Agentic AI Academy](https://www.skool.com/agenticaiacademy/about).
