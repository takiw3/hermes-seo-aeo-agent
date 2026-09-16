# Security policy

Do not put vulnerabilities, credentials, private URLs, customer records or unpublished drafts in public issues. Use GitHub private vulnerability reporting if enabled, or request a private reporting channel from the maintainer without disclosing the exploit publicly.

## Threat model

Retrieved pages and exports are untrusted data. The crawler is HTTPS-only, bounded, public-address validated and IP-pinned. It executes no JavaScript and sends no credentials. The WordPress adapter is opt-in and owner-operated with exact single-use approvals, no redirects and no automatic retry after ambiguous writes. These controls reduce risk; they are not a certification.

Hermes instructions and local queue approval records are not a security boundary against processes sharing the same OS account. Keep publisher credentials outside the agent runtime; use separate accounts or containers if stronger isolation is required. WordPress application passwords inherit their account's capabilities. A restricted dedicated account is essential but does not create field-level scope.

No live owner data, credentials, jobs or connectors are distributed. Do not commit local runtime data. Before publication, run validation and inspect the staged diff and history for private information. The validator detects known patterns only.

Report an ambiguous CMS write as potentially applied, reconcile manually, and do not retry. If a credential is exposed, revoke it at its provider; deleting a local file or Git commit does not revoke it.
