# Optional WordPress native scheduling

This integration is optional and OFF by default. It creates **new posts scheduled for the future only**. It has no command to update existing content, publish immediately, delete content, upload media, choose an arbitrary endpoint or method, or configure WordPress itself. Do not enable it until the owner has reviewed the workflow and the target site's configuration.

## Requirements and least privilege

1. Use an owner-controlled, maintained WordPress installation with its REST API and Application Passwords enabled over valid HTTPS. Core Application Passwords were introduced in WordPress 5.6. Confirm current host/plugin compatibility separately.
2. Use a **dedicated Author account**, not an Administrator or Editor. Author can publish/manage its own posts; Contributor cannot publish. If your site uses custom roles, have the site administrator review the required capabilities rather than increasing permissions automatically.
3. The owner creates a new Application Password for this integration in WordPress **Users → Profile → Application Passwords** and stores it privately. Never use the account's main password. Application Passwords are individually revocable but inherit the user's capabilities; they are **not scoped to create-only, future-only, this CLI, or one approved article**. The dedicated Author can still modify/delete its own posts using other clients. This utility's restrictions do not constrain a stolen credential. Consider an independently enforced server-side capability/endpoint policy when stronger restrictions are needed.
4. Confirm the exact final canonical origin, for example `https://blog.yourdomain.com`. Only lowercase ASCII public DNS hostnames, HTTPS, port 443 and root WordPress installations are supported. No IP literals, localhost/private origins, paths, userinfo, query, fragment, trailing slash, or explicit port. Redirecting from one hostname to another is not supported, even on the same site. Do not weaken these restrictions to make setup work.
5. Confirm WordPress's site timezone and server clock. Set up reliable scheduled-post execution with your host as appropriate. This utility does not install a cron job or alter WP-Cron settings.

## Profile-local secrets and explicit enable switch

Use only the **seo-aeo** profile's secrets, never credentials copied from the default or another profile. The Python CLI reads only its process environment; it does not discover profiles, load `.env` files, read Hermes `auth.json`, or fall back to other accounts. `HERMES_HOME` is not proof of environment isolation. Start an owner-controlled shell with the correct profile's secret injection, or enter fresh dedicated credentials there. Do not run this credential entry through the agent or paste secrets into chat.

The integration's environment contract:

| Variable | Purpose |
| --- | --- |
| `SEO_AEO_WP_ORIGIN` | Exact HTTPS origin, identical to reviewed draft origin |
| `SEO_AEO_WP_USERNAME` | Dedicated WordPress Author login |
| `SEO_AEO_WP_APPLICATION_PASSWORD` | Dedicated revocable Application Password |
| `SEO_AEO_WP_ENABLE_SCHEDULING` | Separate per-command safety switch; only literal `1` enables submission |

The owner can export the non-secret origin and enter the login/password without embedding them in shell history:

```bash
export SEO_AEO_WP_ORIGIN='https://blog.yourdomain.com'
read -r -p 'Dedicated WordPress Author login: ' SEO_AEO_WP_USERNAME
export SEO_AEO_WP_USERNAME
read -r -s -p 'WordPress Application Password: ' SEO_AEO_WP_APPLICATION_PASSWORD
export SEO_AEO_WP_APPLICATION_PASSWORD
unset SEO_AEO_WP_ENABLE_SCHEDULING
```

Alternatively, keep the two credentials in a protected profile-local secret store / `.env` managed by the owner and inject them into the process with a trusted mechanism. Do not blindly `source` files supplied by a repository: shell files can execute commands. Keep the origin as owner-controlled configuration and export it deliberately. Keep the enable switch ephemeral, not in the credential file. Supplying credentials alone never enables submission.

After the exact out-of-band approval described in [Scheduling](scheduling.md), the owner runs:

```bash
SEO_AEO_WP_ENABLE_SCHEDULING=1 python3 "$QUEUE" --db "$DB" submit "$ITEM_ID"
unset SEO_AEO_WP_APPLICATION_PASSWORD SEO_AEO_WP_USERNAME
```

CMS credentials are never written into the queue or printed by this utility. Preview output does contain the owner's draft, so do not place secrets in content. HTTP response bodies and exception details are not logged. The one-use approval token is intentionally returned only by `approve`; protect that output.

### Hermes model OAuth is separate

WordPress Application Password authentication is unrelated to Hermes model-provider OAuth. For an independent provider login, use the profile's normal authorization flow, for example `hermes -p seo-aeo auth add <provider>`, with the appropriate provider identifier. Never copy `auth.json`, refresh tokens or credentials from another profile. Official Hermes profiles documentation notes that some model OAuth logins may otherwise be shared via the root credential store; deliberately establish a separate login when separation is required. This CLI never reads those tokens.

## Network and publication safety

- The endpoint is derived as `ORIGIN/wp-json/wp/v2/posts`; the only mutation is `POST` to that exact path.
- DNS is resolved once per submission; **every** returned address must be public. Private, loopback, link-local, multicast, reserved and supported transition-address hazards are rejected. The selected numeric sockaddr is pinned for both POST and read-back. Connection code does not resolve the hostname a second time.
- TLS uses system trust, validates the original hostname, and uses that hostname for SNI and the HTTP Host header. Proxies from environment variables are not used. No redirect is followed. No alternative address is retried, preventing accidental duplicate creation on failover.
- The adapter sends explicit `status: future`, `date_gmt`, title, slug, content, excerpt, closed comments/pings, non-sticky and standard format. Category/author defaults remain WordPress site/account defaults and are outside the editable payload. There are no custom post types or SEO-plugin meta fields.
- A valid `201` creation response is followed by `GET /wp-json/wp/v2/posts/{id}?context=edit`, requiring authenticated raw fields. It verifies the exact numeric ID/type and every supplied field. No success is declared on the POST response alone.
- A timeout, denied response, redirect, oversized/invalid response, plugin rewrite, slug collision or verification failure is terminal `uncertain`. Nothing is automatically resent. Post IDs received before failed verification remain in local status for manual investigation.

Pinning prevents a DNS validation-to-connect rebinding race; it cannot make a malicious owner-configured public server safe or compensate for a compromised OS, trust store, routing, WordPress/plugin stack or credentials. The OS resolver can stall according to system DNS settings; socket operations use a 20-second timeout, not a hard whole-workflow deadline. There is no reliable remote idempotency key in this integration. A process crash or damaged/rolled-back local database requires manual reconciliation.

## WordPress timing limitations

WordPress native scheduling uses **WP-Cron**. By default WP-Cron is checked on page loads, not run continuously. Low traffic, disabled WP-Cron, failed loopbacks, plugin problems or host restrictions can delay a scheduled post. Ask the host/administrator about a reliable system-scheduler trigger and monitoring. Do not claim guaranteed exact-time publication. This CLI verifies the post was in `future` status at submission, not that it eventually went live.

The local five-minute minimum reduces accidental immediate publication, but depends on synchronized local and server clocks and timely processing. If WordPress reports `publish` unexpectedly, verification marks the local item uncertain; it cannot undo the publication. The owner must inspect the CMS immediately. This adapter deliberately has no rollback, deletion or corrective update feature.

## Evidence and validation scope

Official references used for the implementation:

- [WordPress Posts REST API](https://developer.wordpress.org/rest-api/reference/posts/): creation schema, `future`, `date_gmt`, edit-context retrieval and raw fields.
- [Application Passwords](https://developer.wordpress.org/advanced-administration/security/application-passwords/): per-application revocation, Basic authentication over HTTPS and owner setup.
- [Roles and capabilities](https://wordpress.org/documentation/article/roles-and-capabilities/): Author versus Contributor/Editor/Administrator.
- [WP-Cron](https://developer.wordpress.org/plugins/cron/): page-load triggering and delayed scheduled tasks.
- [Hermes profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles/): profile-local configuration/secrets and OAuth handling.

The delivered tests are offline, with synthetic responses and mocked DNS/TLS/HTTP boundaries. They exercise the adapter's real serialization, pinned connection logic, checks, SQLite state machine and CLI, but **not a live WordPress site**. An owner-authorized staging acceptance test with its own dedicated credentials remains necessary before production use. No staging or production mutation was made while building this distribution.
