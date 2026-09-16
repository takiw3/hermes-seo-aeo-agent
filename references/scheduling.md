# Owner-controlled content scheduling

This distribution includes a real, local SQLite queue and an optional WordPress native scheduling adapter. It is not a background publisher. Python 3.10+ and the standard library are sufficient. No package install is required.

**Default: local drafts and read-only CMS behavior.** `enqueue`, `preview`, `approve`, `cancel`, `status`, and `due` never contact WordPress. Only explicit `submit` can make a CMS request, and only with a matching, unexpired owner approval plus the separate scheduling enable switch. Even local read commands initialize the queue schema if the explicit database does not exist.

## Owner boundary

The agent may prepare a draft and preview for review. **The agent must never run `approve`, generate its own approval, or treat a previous general instruction as approval for a new payload.** The actual owner reviews the exact content, destination, publication time and preview SHA256, then runs both approval and credential-bearing submission out-of-band in their own terminal. The agent must never execute either operation or read the one-use token. `--owner-confirm` is an acknowledgement, not identity authentication.

The local approval record is a workflow guard, **not a same-user security boundary**. A process with the owner's filesystem/code/environment access can bypass it. For stronger isolation, keep the database and CMS credentials under a separate OS account or owner-operated service that the agent cannot access. Do not grant the agent unattended approval rights. Do not share approval tokens in chat, logs or source control.

## Queue a draft and preview it

Run from the distribution checkout. Set `HERMES_HOME` yourself to the actual **seo-aeo** profile home, not your current/default profile. Nothing here installs or changes a Hermes profile.

```bash
python3 skills/seo-aeo-core/editorial-scheduling/scripts/content_queue.py --help

# Owner verifies this is the intended seo-aeo profile before proceeding.
: "${HERMES_HOME:?Set HERMES_HOME to your actual seo-aeo profile home}"
QUEUE=skills/seo-aeo-core/editorial-scheduling/scripts/content_queue.py
umask 077
mkdir -p "$HERMES_HOME/local/editorial"
DB="$HERMES_HOME/local/editorial/content-queue.sqlite3"
# Choose a new filename for each article. Existing drafts are never overwritten.
DRAFT="$HERMES_HOME/local/editorial/draft-001.json"
python3 -c 'import pathlib,sys; data=pathlib.Path(sys.argv[1]).read_bytes(); f=open(sys.argv[2],"xb"); f.write(data); f.close()' templates/schedule-post.json "$DRAFT"
```

Edit that private `$DRAFT` file manually. If creation reports FileExistsError, choose a new filename; do not overwrite the existing draft. Replace the example origin, content and intended date. No secrets belong in this file. Then:

```bash
python3 "$QUEUE" --db "$DB" enqueue --json "$DRAFT"
read -r -p 'Paste the returned item id: ' ITEM_ID
python3 "$QUEUE" --db "$DB" preview "$ITEM_ID"
python3 "$QUEUE" --db "$DB" status
python3 "$QUEUE" --db "$DB" due
```

The preview contains `envelope.endpoint`, `envelope.scheduled_at`, `envelope.payload` and `sha256`. Its hash is SHA256 of UTF-8 JSON of the entire envelope, with sorted keys, compact separators and unescaped Unicode. That binds the endpoint, original offset-bearing time and exact payload. Changing the draft source file after enqueue does not change the stored snapshot. There is no edit/reschedule command. Cancel and enqueue a new draft to change anything before submission.

### Accepted input

Exactly six fields: `origin`, `scheduled_at`, `title`, `slug`, `content`, `excerpt`. Additional fields, duplicate JSON keys and naive timestamps are rejected. Use `YYYY-MM-DDTHH:MM:SSZ` or an explicit numeric offset, such as `2030-01-02T09:00:00-05:00`. Fractions, timezone names and ambiguous local times without offsets are not accepted. The owner must choose the correct daylight-saving offset for the intended date.

The schedule must be **at least five minutes ahead** at enqueue, approval and immediately before submission. Leave substantially more margin in practice. The adapter sends UTC `date_gmt` without a suffix as WordPress expects, and `status: future`. WordPress derives its site-local `date`. The offset in the original input need not equal the site's display timezone.

Limits: title 300 UTF-8 bytes, slug 200 bytes, content 200,000 bytes, excerpt 10,000 bytes. Slugs are lowercase ASCII words separated by hyphens. Excerpt may be empty; title/content may not. Unsafe control characters are rejected. The complete input file, outgoing JSON body and each response are capped at 512 KiB. HTML is not sanitized locally: the owner must review links, embeds and active content. WordPress sanitization may change the content; exact read-back then fails closed rather than silently approving the change.

## Approve outside the agent

Owner-only commands, after reviewing the **full** latest preview:

```bash
read -r -p 'Paste the exact reviewed preview SHA256: ' SHA256
EXPIRES=$(python3 -c 'from datetime import datetime,timedelta,timezone; print((datetime.now(timezone.utc)+timedelta(minutes=30)).replace(microsecond=0).isoformat())')
python3 "$QUEUE" --db "$DB" approve "$ITEM_ID" \
  --sha256 "$SHA256" --expires "$EXPIRES" --owner-confirm
```

Approval expires at the explicit timestamp, at most 24 hours after approval. The command returns a random one-use `approval_token`; only its hash is stored. The token is bound to this item, hash and expiry. Wrong, expired, changed or replayed approvals fail. An already-approved item cannot be re-approved. For an expired approval, cancel and enqueue/review a new item rather than changing the database.

## Optional native submission

First follow [WordPress setup](wordpress-setup.md). In the owner's credential-bearing terminal:

```bash
# Explicit switch for this command only. Hidden prompt requests the one-use approval token.
SEO_AEO_WP_ENABLE_SCHEDULING=1 python3 "$QUEUE" --db "$DB" submit "$ITEM_ID"
python3 "$QUEUE" --db "$DB" status
```

For an owner-controlled noninteractive wrapper, `submit --approval-stdin` reads the token from stdin; never put CMS secrets or the token in command-line arguments. Do not implement an agent auto-approval wrapper.

**Submit schedules the future post in WordPress now. It does not wait until the publication date.** `due` merely lists unsubmitted draft/approved items whose intended time has passed. It never publishes or submits anything, and overdue items cannot be submitted with their old time. Do not wire `due` to a POST loop.

## States, verification and recovery

- `draft`: local snapshot only.
- `approved`: one unused, expiring owner approval exists.
- `in_flight`: SQLite atomically consumed the approval and committed the state **before** the POST. Concurrent callers cannot send another POST for that item.
- `scheduled`: creation returned a positive numeric ID, and an authenticated GET of that exact ID verified every supplied field, raw title/content/excerpt, UTC date, status `future`, ID and post type. This is a verified scheduling receipt, not a claim the post has published.
- `uncertain`: request error, timeout, malformed response or any read-back difference. The approval stays consumed. **No automatic retry or republish.**
- `cancelled`: local draft/approval cancelled; no CMS operation was performed.

`status` is local, not a live CMS poll. It includes remote ID when received, approval expiry and a generic recovery note. `scheduled` remains a local historical receipt even after WordPress later publishes the post.

```bash
# Only before submission:
python3 "$QUEUE" --db "$DB" cancel "$ITEM_ID"
```

Cancellation never deletes, unschedules or updates a remote post. Once submitted, use WordPress manually if the owner wants changes. A crash, interrupt or disk failure can leave `in_flight` instead of `uncertain`; treat both as potentially created. Inspect the actual CMS, including its scheduled posts, by ID if known and by slug/title/time otherwise. Never reset state or automatically enqueue a replacement. Resolve manually before the owner decides what to do next. This is at-most-one POST attempt per intact local queue item, not distributed exactly-once delivery. Restoring an old database, copying the queue or creating duplicate items can invalidate that protection.

Keep SQLite on a private local disk, not a network share, and use one canonical queue for this workflow. The CLI creates files with a restrictive umask; it does not repair permissions of pre-existing files. Protect private drafts and backups too.

## Tests and limits

```bash
python3 -m unittest discover -s tests -p test_content_queue.py -v
```

Tests use real SQLite, real CLI subprocesses and concurrent queue connections. Network boundaries use mock DNS, sockets/TLS and HTTP responses, including an explicitly synthetic WordPress edit-context fixture. No real WordPress scheduling or live TLS interoperability is claimed. Tests cover exact approval, replay/expiry/tampering, interrupted/ambiguous attempts, concurrency, offline defaults, URL/DNS restrictions, pinned connections, redirects, caps and exact read-back. The five-minute guard relies on the owner's clock and a correctly synchronized WordPress clock; a stalled or misconfigured server can still behave unexpectedly. See WordPress setup for infrastructure and credential risks.
