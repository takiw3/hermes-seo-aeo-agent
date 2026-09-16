# Make this agent yours

Installation creates a reusable template, not a business strategy with guessed facts. Configure a model using `hermes -p seo-aeo model`, then start `hermes -p seo-aeo chat`.

Begin with:

> My website is [URL]. We sell [offer] to [customer] in [market]. Our priority is [qualified leads/profitable sales/another measurable outcome]. Help me configure my SEO/AEO agent, then recommend the first three actions. Do not publish, connect accounts or create recurring jobs.

The agent uses the [business template](../templates/business-profile.yaml). It asks progressively for:

- Website, offer, audience, countries/languages and real locations.
- Commercial objective, baseline, capacity and review resources.
- Approved claims, first-hand proof, experts, brand voice and CTA.
- CMS, staging site, approved data sources and domain/property boundaries.
- Timezone, owner/reviewer, teammate profile IDs and permission boundaries.

Unknown stays Unknown. The website supplies candidate facts, not permission or verified pricing. A safe bounded audit can start before full intake. After you review and confirm the summary, the agent saves your profile at `local/business-profile.yaml` inside the actual active profile home.

## Customization and updates

Keep owner data and instructions in `local/`; owner-authored skills go outside `skills/seo-aeo-core/`. Updates replace distributed skills, templates, references and SOUL.md. They preserve local state, credentials, memory, sessions and ordinary config overrides. Back up owner data before upgrades. Do not customize the source template or SOUL.md and assume those edits will survive.

No provider credential is inherited or copied from another profile. Connect each private integration deliberately with a separate owner-driven authentication flow. Never send secrets in chat. Public research uses tools already available in your Hermes installation; paid data is not required or silently purchased.

## First useful deliverable

Ask for a bounded audit and a three-action priority list. Every finding should name the page, evidence, likely consequence, proposed fix and verification. Blocked crawling is not a clean bill of health. Request an HTML export or a developer inspection where needed.

Before live use, ask the configured profile to introduce itself and list its permission limits. That response verifies model connectivity, not SEO quality. Review actual sample work before trusting its recommendations.
