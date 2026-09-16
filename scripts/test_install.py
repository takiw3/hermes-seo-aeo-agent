#!/usr/bin/env python3
"""Actual Hermes CLI integration test, isolated from all live profiles.

Default: pristine local source, actual install/update, no network or model call.
--source-url also runs a second complete install/update against the published
source. It must match this working tree's payload. No command is skipped.
Temporary homes are destroyed on success or failure. Errors exit nonzero.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile

import yaml


REPO_ONLY = ['README.md', 'LICENSE', 'CHANGELOG.md', 'CONTRIBUTING.md',
             'SECURITY.md', '.gitignore', '.github', '.git', 'docs', 'evals',
             'examples', 'scripts', 'tests', 'requirements-dev.txt', 'vendor']


def isolated_environment(base: Path, binary: str) -> dict[str, str]:
    """Allowlist environment, never copy process credentials or profile routing."""
    home, hermes = base/'home', base/'hermes-root'
    home.mkdir(parents=True, exist_ok=True)
    hermes.mkdir(parents=True, exist_ok=True)
    (base/'tmp').mkdir(exist_ok=True)
    return {
        'HOME': str(home), 'HERMES_HOME': str(hermes),
        'PATH': os.pathsep.join([str(Path(binary).parent), '/usr/local/bin', '/usr/bin', '/bin']),
        'XDG_CONFIG_HOME': str(base/'xdg/config'), 'XDG_CACHE_HOME': str(base/'xdg/cache'),
        'XDG_DATA_HOME': str(base/'xdg/data'), 'TMPDIR': str(base/'tmp'),
        'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null',
        'GIT_TERMINAL_PROMPT': '0', 'PYTHONNOUSERSITE': '1',
        'PYTHONDONTWRITEBYTECODE': '1', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
        'NO_COLOR': '1', 'TERM': 'dumb',
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)
    print(f'PASS {message}', flush=True)


def run(command: list[str], env: dict[str, str], cwd: Path) -> str:
    print('RUN ' + ' '.join(command), flush=True)
    result = subprocess.run(command, env=env, cwd=cwd, capture_output=True,
                            text=True, timeout=180, stdin=subprocess.DEVNULL)
    output = result.stdout + result.stderr
    if result.returncode:
        raise RuntimeError(f'Command exited {result.returncode}: {command}\n{output}')
    return re.sub(r'\x1b\[[0-9;]*m', '', output)


def payload_files(source: Path, owned: list[str]) -> set[str]:
    expected = ['distribution.yaml', 'profile.yaml', 'SOUL.md', 'config.yaml',
                'templates', 'references', 'skills/seo-aeo-core']
    require(owned == expected, 'exact runtime allowlist required before reading payload')
    files = set()
    for rel in owned:
        path = source/rel
        require(path.exists(), f'source payload exists: {rel}')
        for entry in path.rglob('*') if path.is_dir() else [path]:
            if entry.is_file() and '__pycache__' not in entry.parts:
                files.add(entry.relative_to(source).as_posix())
    return files


def verify_payload(target: Path, source: Path, files: set[str], custom: bool = False) -> None:
    for rel in sorted(files - {'distribution.yaml', 'config.yaml'}):
        require((target/rel).is_file() and (target/rel).read_bytes() == (source/rel).read_bytes(),
                f'exact installed payload: {rel}')
    expected_skills = {p for p in files if p.endswith('/SKILL.md')}
    if custom:
        expected_skills.add('skills/custom-owner-skill/SKILL.md')
    actual = {p.relative_to(target).as_posix() for p in (target/'skills').rglob('SKILL.md')}
    require(actual == expected_skills, f'exact skill paths/count ({len(actual)})')
    allowed_roots = {Path(rel).parts[0] for rel in files}
    excluded = set(REPO_ONLY) | {p.name for p in source.iterdir() if p.name not in allowed_roots}
    require(not any((target/name).exists() for name in excluded), 'no repository-only payload leaked')
    require(not any(p.is_symlink() for p in target.rglob('*')), 'installed profile contains no symlinks')
    require(not (target/'cron/jobs.json').exists(), 'install/update activates no scheduled jobs')


def exercise(repo: Path, binary: str, source_url: str | None = None) -> None:
    with tempfile.TemporaryDirectory(prefix='hermes-seo-aeo-test-') as tmp:
        base = Path(tmp)
        env = isolated_environment(base, binary)
        require(not Path(env['HERMES_HOME']).is_relative_to(Path(env['HOME'])/'.hermes'),
                'HERMES_HOME is outside temporary ~/.hermes')
        source = base/'pristine-source'
        require(not any(p.is_symlink() for p in repo.rglob('*') if '.git' not in p.parts),
                'source has no symlinks')
        shutil.copytree(repo, source, ignore=shutil.ignore_patterns(
            '.git', '__pycache__', '*.pyc', '.venv', 'venv', '.pytest_cache'))
        manifest = yaml.safe_load((source/'distribution.yaml').read_text())
        name = manifest['name']
        require(name == 'seo-aeo', 'test is scoped to the seo-aeo distribution')
        target = Path(env['HERMES_HOME'])/'profiles'/name
        files = payload_files(source, manifest['distribution_owned'])
        chosen_source = source_url or str(source)
        cli = [binary]
        version_output = run(cli + ['--version'], env, base).strip()
        print(version_output, flush=True)
        print(run(cli + ['profile', 'install', chosen_source, '--alias', '--yes'], env, base), flush=True)
        require(target.is_dir(), 'profile created in temporary HERMES_HOME')
        installed = yaml.safe_load((target/'distribution.yaml').read_text())
        require(installed['source'] == chosen_source, 'installer records exact source provenance')
        require(installed.get('installed_at'), 'installer records installation timestamp')
        require(installed['version'] == manifest['version'], 'manifest version installed')
        require((target/'config.yaml').read_bytes() == (source/'config.yaml').read_bytes(), 'initial config equals source')
        verify_payload(target, source, files)
        info = run(cli + ['profile', 'info', name], env, base)
        require(all(str(v) in info for v in [name, manifest['version'], manifest['hermes_requires'], chosen_source]),
                'profile info reports name/version/minimum/source')
        show = run(cli + ['profile', 'show', name], env, base)
        count = len([f for f in files if f.endswith('/SKILL.md')])
        require(re.search(rf'Skills:?\s+{count}\b', show) is not None, 'profile show reports derived skill count')
        describe = run(cli + ['profile', 'describe', name], env, base)
        description = yaml.safe_load((source/'profile.yaml').read_text())['description']
        require(description.split('.')[0] in describe, 'profile describe reads routing description')
        wrapper = Path(env['HOME'])/'.local/bin'/name
        require(wrapper.is_file() and os.access(wrapper, os.X_OK), 'alias wrapper is executable inside temporary HOME')
        require(re.search(rf'(?:-p|--profile)\s+[\"\']?{re.escape(name)}', wrapper.read_text()) is not None,
                'alias targets the correct profile')
        alias_version = run([str(wrapper), '--version'], env, base).strip()
        require(alias_version.splitlines()[0] == version_output.splitlines()[0],
                'alias executes the same Hermes version under test')
        helpers = ['skills/seo-aeo-core/site-audit/scripts/audit.py',
                   'skills/seo-aeo-core/editorial-scheduling/scripts/content_queue.py']
        for helper in helpers:
            require(helper in files, f'helper is part of installed payload: {helper}')
            help_text = run([sys.executable, str(target/helper), '--help'], env, base)
            require('usage:' in help_text.lower(), f'installed helper --help executes: {helper}')

        # Synthetic data only. No process env or actual owner credential is read.
        sentinels = {
            '.env': 'SYNTHETIC_INSTALL_TEST=owner-value\n',
            'auth.json': '{"synthetic_test_only": true}\n',
            'seo_google_token.json': '{"synthetic_test_only": true}\n',
            'seo_google_client_secret.json': '{"synthetic_test_only": true}\n',
            'memories/test.md': 'synthetic owner memory\n',
            'sessions/test.json': '{"synthetic": "session"}\n',
            'local/business-profile.yaml': 'synthetic_business: owner\n',
            'local/queue.json': '{"synthetic": "queue"}\n',
            'skills/custom-owner-skill/SKILL.md': '---\nname: custom-owner-skill\ndescription: Synthetic owner skill.\n---\nOwner skill.\n',
        }
        for rel, content in sentinels.items():
            path = target/rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        for rel in ['local/queue.sqlite', 'state.db']:
            with sqlite3.connect(target/rel) as connection:
                connection.execute('CREATE TABLE IF NOT EXISTS synthetic_sentinel (value TEXT)')
                connection.execute('INSERT INTO synthetic_sentinel VALUES (?)', ('owner-value',))
        config = yaml.safe_load((target/'config.yaml').read_text())
        config['synthetic_owner_override'] = {'business': 'owner', 'value': 7}
        (target/'config.yaml').write_text(yaml.safe_dump(config, sort_keys=False))
        preserved = {rel: (target/rel).read_bytes() for rel in list(sentinels) + ['local/queue.sqlite', 'state.db', 'config.yaml']}
        (target/'templates/stale-owned-file.md').write_text('must be removed on update\n')
        if source_url:
            # Updating the remote does not require publishing a test revision:
            # damage ONLY this temporary install, then prove CLI restores source.
            (target/'SOUL.md').write_text('synthetic stale installed identity\n')
        else:
            version = [int(x) for x in str(manifest['version']).split('.')]
            version[-1] += 1
            manifest['version'] = '.'.join(map(str, version))
            (source/'distribution.yaml').write_text(yaml.safe_dump(manifest, sort_keys=False))
            with (source/'SOUL.md').open('a') as stream:
                stream.write('\n<!-- synthetic-update-source-marker -->\n')
        print(run(cli + ['profile', 'update', name, '--yes'], env, base), flush=True)
        for rel, content in preserved.items():
            require((target/rel).read_bytes() == content, f'update preserved exact owner bytes: {rel}')
        require(not (target/'templates/stale-owned-file.md').exists(), 'update removes stale distribution-owned files')
        verify_payload(target, source, files, custom=True)
        updated = yaml.safe_load((target/'distribution.yaml').read_text())
        require(updated['version'] == manifest['version'] and updated['source'] == chosen_source,
                'updated manifest retains correct version and source')
        require(str(manifest['version']) in run(cli + ['profile', 'info', name], env, base),
                'CLI info confirms updated version')
        # No provider calls, publishing, real scheduling, or behavioural evals.
        print('PASS actual CLI install/update with no skipped commands', flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--hermes-bin', default='hermes')
    parser.add_argument('--source-url', help='Also test a public remote matching the local release; no commands skipped')
    args = parser.parse_args()
    binary = shutil.which(args.hermes_bin)
    if not binary:
        print('FAIL Hermes CLI unavailable; install/update NOT RUN', file=sys.stderr)
        return 2
    try:
        exercise(args.root.resolve(), str(Path(binary).absolute()))
        if args.source_url:
            exercise(args.root.resolve(), str(Path(binary).absolute()), args.source_url)
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.SubprocessError, yaml.YAMLError) as exc:
        print(f'FAIL {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
