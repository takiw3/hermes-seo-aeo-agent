# Reference repository review

This review informed the SEO/AEO distribution's packaging and safety contract. It is a source review, not a claim that these reference products or their model behaviours were evaluated.

## Sources inspected

All five repositories were read from local checkouts, including manifests, routing metadata, provider-neutral configuration, identity documents, repository validators and install/update tests. Skill counts below are counted `SKILL.md` files in those checkouts, not SEO/AEO requirements.

| Reference | Reviewed commit | Skills | Useful pattern adopted | Deliberate difference |
| --- | --- | ---: | --- | --- |
| [Finance](https://github.com/takiw3/hermes-finance-agent) | `7fbd7d1e897e1498a1c8723d235da19daa1def97` | 29 | Deterministic local artifacts, explicit unexecuted status, local-export boundaries, separate update-preservation tests | SEO/AEO supports bounded public-web research and optional explicitly approved CMS actions; it does not inherit financial controls, schemas or the finance skill set. Its 60-character description limit is stricter than Finance's validator. |
| [Ads](https://github.com/takiw3/hermes-ads-agent) | `57a09e66f5a22416ca04dfa5777ce83765818404` | 34 | Exact path-aware runtime allowlist, source-vs-owner separation, explicit installation floor, installed payload leakage checks | No Google Ads/Meta credentials, advertising mutations, paid-media tool bundles or vendored integrations are copied. |
| [Customer Support](https://github.com/takiw3/hermes-customer-support-agent) | `1da28a6fdb00420acf26d33fb2c9343204e5a79f` | 21 | Stable routing description; default draft mode; credential, local state and custom-skill preservation | Its README exposes optional approved actions while its distribution summary remains read-and-draft. SEO/AEO must state optional execution boundaries consistently and does not copy Gmail/Docs queue semantics as a publishing guarantee. |
| [Marketing](https://github.com/takiw3/hermes-marketing-agent) | `e1ae0b9c61d7136676be229fa39821885627325b` | 17 | Narrow core skill namespace; temporary HOME plus HERMES_HOME outside `~/.hermes`; pristine staging copy; source marker update test | Its remote test path skips update preservation. SEO/AEO's optional remote mode performs install and update and never treats skipped commands as success. |
| [Sales](https://github.com/takiw3/hermes-sales-agent) | `5acc130d325320ddb48ef88168047b5e9dc304b2` | 24 | Source-system evidence, precise permission boundaries, manifest-derived ownership, credential sentinels beyond Hermes' built-in exclusions | Its compatibility script imports released installer modules with stubs and can return zero when no checkout exists. SEO/AEO uses actual CLI commands, fails unavailable prerequisites, and makes no claim about unrun releases. |

## Upstream contract

Authoritative documentation: [Profile distributions](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions) and [Profile commands](https://hermes-agent.nousresearch.com/docs/reference/profile-commands).

The distribution is an explicitly allowlisted profile, not a copy of a live Hermes home. Its runtime roots are `distribution.yaml`, `profile.yaml`, `SOUL.md`, `config.yaml`, `templates`, `references`, and `skills/seo-aeo-core`. All other repository content is authoring or verification material. Root `scripts`, `tests`, `docs`, `examples`, `evals`, CI, README and license must not appear in an installed profile. Runtime scripts inside a shipped skill are intentionally included.

Updates replace distribution-owned artifacts, preserve local `config.yaml` by default, and preserve user-created skill namespaces outside `skills/seo-aeo-core`. Credential protection is not limited to Hermes' hardcoded exclusions: the narrow allowlist protects additional filenames too. Profile isolation is not an operating-system sandbox.

`>=0.20.0` is the **installer ownership floor**, not a claim that every subsequent Hermes release or every optional permission setting has been behaviourally tested. The released `v2026.8.3` source supports path-aware copying. The preceding `v2026.7.30` CLI reports version 0.19.1 and refuses a manifest requiring `>=0.20.0` before installation.

## Verification implementation

- [Repository validator](../scripts/validate.py): real YAML parsing with duplicate-key rejection; exact identity/allowlist and safe defaults; required runtime paths; name-to-directory agreement and unique skill names; descriptions at most 60 characters; a linked `Skill | Produces` README row for every shipped skill; local Markdown links; symlinks, state/credential filenames, known secret shapes and repository-only payload checks.
- [Regression tests](../tests/test_distribution.py): isolated synthetic repository fixtures, exercised through the validator CLI. Tests were added in red/green increments, including unsafe ownership, altered configuration, malformed skill frontmatter, missing README links, broken local links, secret-shaped strings, state files and duplicate YAML keys.
- [Actual installer test](../scripts/test_install.py): temporary HOME and HERMES_HOME, allowlisted environment with no inherited API keys or profile selectors, pristine local source copy, real `hermes profile install --alias --yes`, `info`, `show`, `describe`, alias execution, installed audit and queue `--help`, exact payload/skill comparisons, then real `hermes profile update --yes`. A source version bump and identity marker prove that an update occurred.
- Update sentinels cover `.env`, `auth.json`, additional credential filenames, local business configuration, local JSON queue, SQLite queue, state database, memories, sessions, custom owner skill and configuration overrides. Byte-for-byte comparison is required, and a stale distribution-owned file must disappear.
- `--source-url` additionally repeats a full install/update against a public remote that matches the local release. It changes only the disposable installed identity and proves the update restores the remote source. It does not publish or modify the remote.
- [CI](../.github/workflows/validate.yml): Python 3.10 and 3.12, `unittest` discovery and offline validation, with commit-pinned actions and repository-only PyYAML dependency. CI does not silently install Hermes or claim actual-CLI coverage.

## Reproduce

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/validate.py
python scripts/test_install.py --hermes-bin /path/to/hermes
# Optional, after publishing and reviewing the remote:
python scripts/test_install.py --source-url https://github.com/OWNER/REPOSITORY
```

A missing CLI, failed command, timeout, wrong skill count, missing helper, changed owner sentinel or payload leak is a failure, not a skip. The test never runs chat, invokes a model, publishes, installs an active recurring job or borrows credentials.

## Evidence and scope

The installed environment reports `Hermes Agent v0.20.5 (2026.8.19) · upstream 057dcdf2`. Its installed source is not a git checkout and may include newer changes; this identity must not be described as an untouched 0.20.5 release. Its `hermes_cli/profile_distribution.py` SHA-256 is `76188a4321a515d1194b1fd60519db5df22cde1c58f11333be2c6407e835f97c`.

Released source checkouts independently resolved:

- `v2026.8.3`: commit `3c27eb6234bf91b8ceee9e9071591b31e9b148cb`, CLI version 0.20.0.
- `v2026.7.30`: commit `cc4cab2f592e60a197e796506de9168f74baf3ea`, CLI version 0.19.1.

The complete install/update harness passed against a clearly synthetic distribution fixture on both the installed CLI and released 0.20.0 CLI. That fixture used the actual SEO/AEO audit and queue scripts, not replacements. Checks included installed helper execution, alias version parity, all owner-state sentinels, source version/identity changes, exact skills and repository payload exclusion. The 0.19.1 CLI rejected `>=0.20.0` with exit 1 as expected; a separate readback verified that no profile or alias was created. Both released CLIs used their unmodified source with the existing environment's Python dependencies, not fresh dependency installations.

The early subtask used a synthetic fixture because root files were still being authored. After assembly, the parent reran the full harness against the actual complete distribution on both installer identities; install, update, exact payload, alias, installed helper and preservation checks passed. See `docs/testing.md` for final release acceptance. The GitHub workflow itself has not run locally.

Secret detection is pattern-based, not a privacy certification. It cannot prove the absence of arbitrary private business facts or unknown credential formats. Synthetic regression strings are constructed at runtime rather than placing realistic secrets in this repository. Local-link checks ignore fragments, external schemes, code blocks and template placeholders; they do not fetch external sites. Git history and model behaviour are outside this validator's scope. No broad runtime support matrix or model-behaviour evaluation is claimed.
