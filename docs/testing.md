# Test evidence and release limitations

Assembly checked on 2026-09-16 UTC. This page distinguishes executable tests from model behavior and live platform outcomes.

## Verified execution

| Check | Actual result |
|---|---|
| Full offline suite, Python 3.10.20 | 82 tests passed after review fixes |
| Full offline suite, Python 3.12.13 | 82 tests passed after review fixes |
| Full offline suite, Python 3.13.5 | 82 tests passed after review fixes |
| Independent final code re-review | Passed; 82 regression tests plus 23 independent in-memory checks |
| Repository validation | 0 findings |
| Below-floor install refusal, upstream Hermes 0.19.1 | Full final manifest refused; no profile or alias created |
| Complete-distribution install/update, released Hermes 0.20.0 | Passed, including all 23 skills and installed helper execution |
| Complete-distribution install/update, installed Hermes build | Passed, reported v0.20.5 / upstream 057dcdf2 |
| Owner-state preservation | Exact bytes preserved for credentials, business profile, queue/database, memory, sessions, custom skill and config override sentinels |
| Runtime payload exclusion | No repository-only files or activated jobs leaked |
| Both installed CLI helpers | `--help` executes from installed paths |
| Live public-site crawler smoke | python.org: robots/homepage HTTP200, one analyzed page, 2 requests, no errors; expected partial/page_cap |
| Local editorial CLI smoke | Synthetic template enqueued, exact preview returned, cancelled; no CMS call |
| Draft setup safety | Repeated exclusive-file creation refused; original draft bytes preserved |

The installed environment is not a pristine released 0.20.5 source checkout. The floor test used unmodified upstream v2026.8.3 source with this environment's dependencies, not a fresh full Hermes installation. Detailed identities and the separately observed 0.19.1 refusal are in [reference review](reference-review.md). No broader version matrix is claimed.

The public-site smoke is read-only. A repeat python.org request exposed an unsupported compressed response; the crawler reported zero analyzed pages rather than inventing coverage. Bounded gzip support was added and exercised against the real site: robots and homepage returned 200, one page was analyzed with two requests, no fetch errors, and explicit `partial / page_cap` coverage. This is a one-page transport smoke, not a whole-site SEO result. Independent review additionally found HTTP-framing and escaped robots-character edge cases. Both were fixed with failing-first regression tests; the fresh final reviewer passed the changes and separately exercised 23 in-memory framing/gzip/robots cases.

## Reproduce

```bash
uv run --no-project --with pyyaml python -m unittest discover -s tests -v
uv run --no-project --with pyyaml python scripts/validate.py
uv run --no-project --with pyyaml python scripts/test_install.py --hermes-bin /absolute/path/to/hermes
```

The installer test changes only disposable HOME/HERMES_HOME directories. It runs real install/update commands, checks the installed tools and alias, and compares owner-state sentinels byte for byte. No active business profile was created or changed.

## Not run

- Configured-profile chat/model-backed SEO quality evaluations. [Acceptance scenarios](../evals/acceptance-scenarios.md) are prepared, not scored.
- Live WordPress scheduling, authenticated staging acceptance or eventual publication verification.
- Live GSC/GA4/Bing/GBP data, multi-agent dispatch or messaging delivery.
- Native Windows/macOS testing or compatibility with every Hermes release.
- Remote GitHub install/update and GitHub Actions, pending publication approval.
- Comparative market benchmarks or ranking/citation lift experiments.

All sample business/CMS fixture data is synthetic and explicitly for testing. Unit tests mock network boundaries where noted. Passing tests cannot prove absence of all security issues, model reliability or business outcomes. Independent review is tracked separately from these tool outputs.
