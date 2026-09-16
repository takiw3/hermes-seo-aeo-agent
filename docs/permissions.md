# Permissions and actual capability

| Operation | Default | Boundary |
|---|---|---|
| Bounded public-site audit | Available | User-requested site, robots respected, HTTPS/public addresses only |
| Local research, analysis and content drafts | Available | Approved sources and no fabricated facts |
| Business-profile persistence | Owner confirmation | Exact reviewed business summary in `local/` |
| GSC/GA4/Bing/GBP/Merchant data | Not connected | Owner exports or separately authorized read tools |
| Local editorial queue | Available | Records intent, not remote scheduling |
| WordPress native future post | Disabled | Owner configures credentials; owner runs exact approval and submission |
| Existing CMS page edits/deployment | Not implemented | Reviewed copy/code change set to owner/developer |
| Other CMS publishing | Not implemented | Export/handoff; no fabricated connector |
| Recurring draft/report jobs | None installed | Exact owner opt-in, native Hermes tools and credential isolation |
| Outreach, listings, IndexNow, sitemap submission | No default writes | Separate approval and verified tool; not bundled adapters |
| Paid data, ad spend or purchases | Not authorized | Explicit owner decision |

A request to improve rankings is not blanket write permission. Even creating a draft in a remote CMS is a write. A local cancellation cannot cancel a remote post. An uncertain write is potentially applied and must be manually reconciled before any new attempt.

No helper deploys site patches, changes search-engine controls or logs into owner accounts automatically. The WordPress utility is intentionally an owner-operated execution path. Its local approval tokens enforce a workflow, not verified human identity. An agent with arbitrary same-user filesystem/terminal access could bypass local policies; keep publisher credentials outside its runtime and use OS-level separation if needed.

Hermes manual approval and unattended deny modes apply to commands Hermes classifies as dangerous. They do not make all tools read-only. `terminal.home_mode: profile` changes home resolution but is not filesystem containment. This distinction applies to every claimed permission boundary in the package.

See [scheduling](../references/scheduling.md), [WordPress setup](../references/wordpress-setup.md), and [security](../SECURITY.md).
