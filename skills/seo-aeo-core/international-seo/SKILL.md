---
name: international-seo
description: "Validate localized pages and reciprocal hreflang."
version: 0.1.0
author: Taki Wong (takiw3), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [seo, aeo, specialization]
    related_skills: []
---

# International SEO and hreflang

Help the right audience reach genuinely localized pages. Hreflang annotations describe equivalent language/region variants; they do not translate a site or guarantee rankings in a market.

## When to use

Use for multilingual expansion, wrong-language landing pages, conflicting regional canonicals or alternate-link regressions. Do not confuse international targeting with local GBP eligibility.

## Inputs and prerequisites

Confirmed supported markets/languages, actual language content, equivalent URL sets, currency/legal/fulfillment differences, native reviewer and current canonical/alternate implementation. Use url-inventory, migration-map and change-preview-rollback. Sources G11, G08, G02-G04; inspect current multi-regional and locale-adaptive guidance if implementing those behaviors.

## Procedure

1. **Verify market capability.** Confirm the business can serve the country and language. A translated lead form without fulfillment, support or legal readiness is not enough. Record localization owner and specialist review needs.
2. **Group genuinely equivalent pages.** Map product/intent equivalents across locales; do not point every translated detail page at another locale's homepage. Missing equivalents remain missing, not fabricated placeholder destinations.
3. **Check actual language and content.** Inspect main text, navigation, forms, checkout, currency, measurements, shipping and policies. Hreflang and HTML lang do not substitute for real localization; Google determines page language from content.
4. **Validate codes and URLs.** Use supported language codes and optional appropriate region/script forms from current docs; no country-only value or invented region. For the UK region use GB, not UK. Use fully qualified URLs and consider a justified x-default fallback.
5. **Reconcile canonical and alternate logic.** Each intended alternate should be accessible and represent the appropriate canonical version. Do not canonicalize all translated content to one language while claiming every translation is intended to index.
6. **Audit reciprocal sets.** Every member lists itself and the relevant other members, with return links. Compare complete sets programmatically when large, report missing edges and invalid destinations. Choose HTML, HTTP header or sitemap implementation deliberately; Google treats them as equivalent and duplicate implementations increase maintenance risk.
7. **Review discovery and routing.** Ensure language selectors use real links and preserve access to alternatives. Inspect redirects and defaults from relevant contexts; automatic routing must not hide variants from users or permitted crawlers. State what geography testing was actually performed.
8. **Draft exact fixes.** Provide cluster-level before/after alternate matrix, canonical decisions, affected templates, cache/CDN implications and native-language QA. Obtain explicit owner approval before URL, redirect, hreflang or content changes.
9. **Verify complete changed clusters.** Re-fetch all changed members, check reciprocity/self-links and destination behavior, then observe country/language landing patterns after search processing. Lack of immediate search movement is not proof the annotations failed.

## Artifacts

Locale-equivalence matrix, code and reciprocity report, native-review checklist, canonical/redirect decisions and exact change preview with rollback.

## Evidence and unknowns

Location simulation is not proof of every user's experience. Regional demand cannot be inferred from another country's volume. Missing translated proof or reviewer approval blocks publication; a technical hreflang audit can still proceed.

## Pitfalls

Avoid country-only tags, UK codes, missing self/return links, redirected/non-equivalent alternates, conflicting sitemap and HTML sets, automatic forced-language redirects and mass machine-translated doorway content without local value.

## Verification

All changed alternate sets reconcile; languages/regions are valid; targets are equivalent and accessible; canonical intent is consistent; localization is human-reviewed where required. Approval, rollback and post-write readback are recorded separately from later Search observations.
