---
name: technical-seo
description: "Diagnose crawl, rendering and indexing failures."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, owner-reviewed]
    related_skills: []
---

# Technical SEO diagnosis

Find the earliest failing stage between discovery, retrieval, rendering, canonical selection and indexing. Implementations are proposed with tests and rollback; a successful deployment is not proof of search recovery.

## When to use

Use for crawl/indexation symptoms, inconsistent canonicals, JavaScript content problems, faceted duplication or template regressions. Do not respond to a traffic drop by changing robots without evidence.

## Inputs and prerequisites

Exact affected URLs, expected behavior, first noticed date, recent change history and business-critical templates. Request permitted robots/sitemap/header snapshots, rendered HTML, URL Inspection evidence and logs when available. Missing account access stays Unknown. Sources G05-G09, G14-G15 and G02; use audit-report and change-preview-rollback templates.

## Procedure

1. **Localize the failure.** Compare affected and unaffected pages by template, path, locale, device and deployment. State whether the symptom is non-discovery, crawl error, unavailable content, alternate canonical or non-indexing. Do not conflate these stages.
2. **Inspect retrieval.** Record initial and final status, redirect chain, content type, response headers and body. Test a representative sample with the permitted browser when rendering matters. Look for server errors, login interstitials, challenge pages or a 200 response carrying error content.
3. **Evaluate crawl controls.** Inspect host-specific robots rules and CDN/WAF behavior. Explain that robots allowance does not ensure crawling and disallow does not reliably deindex. A noindex directive must be retrievable to be processed; sensitive content needs authentication, not a robots entry.
4. **Reconcile canonical signals.** Compare redirects, HTML/header canonical, sitemap inclusion and internal links. Inspect declared versus platform-selected canonical separately. Do not use noindex as a canonical selector or canonicalize materially different useful pages merely to simplify the graph.
5. **Inspect rendered content.** Compare primary text, navigation, canonical and robots before/after JavaScript. Test missing resources, hydration errors and interaction-dependent content. Google can render JavaScript; avoid the blanket assertion that JavaScript content is invisible.
6. **Contain duplicate URL generation.** Identify actual parameter combinations, infinite calendars, filters and pagination. Preserve valuable filter landing pages and navigable product access. Separate crawl-volume control, indexation policy and duplicate consolidation; one blanket robots rule rarely solves all three.
7. **Check discovery artifacts.** Sitemaps should contain intended canonical indexable URLs and honest modification dates; they are discovery hints, not indexing guarantees. Find orphan business pages by comparing crawl, CMS and analytics inventories.
8. **Evaluate experience separately.** Request actual field-performance evidence and inspect mobile usability/accessibility. Lab results explain mechanisms; they do not equal field metrics or guarantee ranking. Record source and collection conditions.
9. **Prepare a minimally scoped fix.** Show exact before/after response or code, affected templates, cache behavior, test cases including negative controls, rollout risk and rollback. Approval covers exact destination, payload and execution time.
10. **Verify in layers.** After approved implementation, read back raw response and rendered behavior; later check crawl/index evidence and trends. Annotate lag. Escalate if the intended fix changes checkout, locale routing or access security.

## Artifacts

Root-cause memo with reproduction steps, affected/unaffected sample, test matrix, change preview and post-change evidence. Include owner and next review trigger for unresolved engine-side processing.

## Evidence and unknowns

A log user agent alone does not prove a vendor crawler. GSC reports can be delayed or aggregate. Lack of an observed crawl is not proof of a block. List alternatives such as demand shifts and measurement defects when technical evidence is inconclusive.

## Pitfalls

Avoid sitewide noindex, mass homepage redirects, aggressive parameter blocking, removing useful resources, invented crawl-budget diagnoses and copying crawler rules between vendors. Keep privacy and search goals distinct.

## Verification

The proposed cause explains the affected cohort and has a falsifiable test; the smallest safe change is specified; high-risk routes have regression tests; any external change has approval, readback and rollback evidence. Indexing/ranking success remains pending unless actually measured.
