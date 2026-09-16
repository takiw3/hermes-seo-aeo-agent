#!/usr/bin/env python3
"""Offline repository contract validation. Requires PyYAML; never imports Hermes."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote

import yaml

OWNED = ['distribution.yaml', 'profile.yaml', 'SOUL.md', 'config.yaml',
         'templates', 'references', 'skills/seo-aeo-core']


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate YAML keys instead of silently replacing safety settings."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                if key in seen:
                    raise yaml.YAMLError('duplicate mapping key')
                seen.add(key)
            except TypeError as exc:
                raise yaml.YAMLError('non-scalar mapping key') from exc
        return super().construct_mapping(node, deep=deep)


def load_yaml(text):
    return yaml.load(text, Loader=UniqueLoader)


def validate(root: Path) -> list[str]:
    errors = []
    ignored = {'.git', '__pycache__', '.venv', 'venv', '.pytest_cache'}
    paths = [p for p in root.rglob('*') if not ignored.intersection(p.relative_to(root).parts)]
    for path in paths:
        if path.is_symlink():
            errors.append(f'symlink: forbidden: {path.relative_to(root)}')
    if errors:
        return errors  # Never read through a symlink, even a dangling one.
    private_dirs = {'local', 'memories', 'sessions', 'logs', 'cron', 'home', 'workspace', 'profiles'}
    private_names = {'.env', 'auth.json', 'credentials.json', 'mcp.json', 'gateway_state.json',
                     'active_profile', 'processes.json', '.hermes_history'}
    for path in paths:
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if (private_dirs.intersection(rel.parts[:-1]) or path.name in private_names
                or path.name.startswith('.env.') or re.search(r'(?:token|client_secret|oauth_pending)\.json$', path.name)
                or re.search(r'\.(?:db|sqlite|sqlite3)(?:-(?:wal|shm))?$', path.name)):
            errors.append(f'private: credential, state or activation file: {rel}')
        try:
            content = path.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            errors.append(f'file: unreadable or binary file: {rel}')
            continue
        if path.suffix in {'.yaml', '.yml'}:
            try:
                load_yaml(content)
            except yaml.YAMLError:
                errors.append(f'yaml: invalid or duplicate keys: {rel}')
        if re.search(r'(?:/home/[^/\s]+|/Users/[^/\s]+)/\.hermes/(?:profiles|memories|sessions)/', content):
            errors.append(f'private: live instance path in {rel} (value redacted)')
        secret_patterns = [r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{40,}',
                           r'AKIA[0-9A-Z]{16}', r'sk-(?:proj-)?[A-Za-z0-9_-]{32,}',
                           r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                           r'ya29\.[A-Za-z0-9_-]{30,}',
                           r'(?im)^\s*(?:api_key|access_token|refresh_token|client_secret|password)\s*[:=]\s*[\"\']?[A-Za-z0-9_/-]{24,}[\"\']?\s*$']
        if any(re.search(pattern, content) for pattern in secret_patterns):
            errors.append(f'secret: credential-shaped content in {rel} (value redacted)')
    if errors:
        return errors
    for name in ['distribution.yaml', 'profile.yaml', 'config.yaml']:
        try:
            value = load_yaml((root / name).read_text(encoding='utf-8'))
            if not isinstance(value, dict):
                errors.append(f'yaml: mapping required: {name}')
            elif name == 'distribution.yaml':
                if value.get('distribution_owned') != OWNED:
                    errors.append('manifest: distribution_owned must equal the exact runtime allowlist')
                known = {'name', 'version', 'description', 'hermes_requires', 'author', 'license', 'env_requires', 'distribution_owned'}
                if set(value) - known or value.get('name') != 'seo-aeo' or not re.fullmatch(r'\d+\.\d+\.\d+', str(value.get('version', ''))) or value.get('hermes_requires') != '>=0.20.0' or value.get('env_requires'):
                    errors.append('manifest: invalid identity, version, minimum, fields or env requirements')
            elif name == 'profile.yaml':
                if value.get('description_auto') is not False or not isinstance(value.get('description'), str) or not value.get('description', '').strip() or not isinstance(value.get('display_name'), str):
                    errors.append('profile: manual routing description and display name required')
            elif name == 'config.yaml':
                required = {'memory': {'write_approval': True}, 'skills': {'write_approval': True},
                            'curator': {'consolidate': False}, 'delegation': {'subagent_auto_approve': False},
                            'terminal': {'home_mode': 'profile'},
                            'approvals': {'mode': 'manual', 'cron_mode': 'deny', 'single_query_mode': 'deny'}}
                for section, values in required.items():
                    actual = value.get(section, {})
                    for key, expected in values.items():
                        if not isinstance(actual, dict) or type(actual.get(key)) is not type(expected) or actual.get(key) != expected:
                            errors.append(f'config: unsafe or absent {section}.{key}')
                for key in ['model', 'provider', 'cron', 'mcp_servers', 'platforms', 'api_key']:
                    if key in value:
                        errors.append(f'config: provider-neutral inactive defaults forbid {key}')
        except (OSError, yaml.YAMLError):
            errors.append(f'yaml: unreadable or invalid: {name}')
    for rel in OWNED:
        target = root/rel
        if not target.exists() or (target.is_file() and target.stat().st_size == 0):
            errors.append(f'payload: missing or empty {rel}')
        for path in target.rglob('*') if target.is_dir() else []:
            parts = path.relative_to(target).parts
            if set(parts) & {'docs', 'tests', 'evals', 'examples', '.github', 'vendor'} or path.name in {'validate.py', 'test_install.py', 'requirements-dev.txt'}:
                errors.append(f'payload: repository-only content: {path.relative_to(root)}')
    names = set()
    skill_files = sorted((root/'skills/seo-aeo-core').rglob('SKILL.md'))
    if not skill_files:
        errors.append('skills: no shipped skills')
    for path in skill_files:
        body = path.read_text(encoding='utf-8')
        parts = body.split('---', 2) if body.startswith('---\n') else []
        try:
            front = load_yaml(parts[1]) if len(parts) == 3 else None
        except yaml.YAMLError:
            front = None
        if not isinstance(front, dict):
            errors.append(f'skill: invalid frontmatter: {path.relative_to(root)}')
            continue
        name, description = front.get('name'), front.get('description')
        if not isinstance(name, str) or name != path.parent.name or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or len(name) > 64:
            errors.append(f'skill: name/path mismatch: {path.relative_to(root)}')
        if isinstance(name, str):
            if name in names:
                errors.append(f'skill: duplicate name: {path.relative_to(root)}')
            names.add(name)
        if not isinstance(description, str) or not 1 <= len(description) <= 60:
            errors.append(f'skill: description must be 1-60 characters: {path.relative_to(root)}')
        if len(parts) != 3 or not parts[2].strip():
            errors.append(f'skill: empty body: {path.relative_to(root)}')
    readme = (root/'README.md').read_text(encoding='utf-8') if (root/'README.md').is_file() else ''
    table = False
    covered = set()
    for line in readme.splitlines():
        if re.match(r'\s*\|\s*Skill\s*\|\s*Produces\s*\|', line, re.I):
            table = True
            continue
        if table and not line.strip().startswith('|'):
            table = False
        if table:
            columns = line.strip().strip('|').split('|')
            if len(columns) >= 2 and columns[1].strip():
                covered.update(re.findall(r'\]\(([^)#]+)(?:#[^)]*)?\)', columns[0]))
    for path in skill_files:
        if path.relative_to(root).as_posix() not in {x.removeprefix('./') for x in covered}:
            errors.append(f'README: Skill | Produces table must link {path.relative_to(root)}')
    for path in paths:
        if not path.is_file() or path.suffix != '.md':
            continue
        body = path.read_text(encoding='utf-8')
        body = re.sub(r'^```.*?^```[^\n]*', '', body, flags=re.M | re.S)
        links = re.findall(r'\]\(([^)]+)\)', body)
        links += re.findall(r'^\s*\[[^]]+\]:\s*(\S+)', body, re.M)
        for link in links:
            link = link.strip().split(' "', 1)[0].strip('<>')
            if not link or link.startswith(('#', '//')) or re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', link) or any(x in link for x in ['{', '}', '$', '<', '>']):
                continue
            target = (path.parent/unquote(link.split('#', 1)[0].split('?', 1)[0])).resolve()
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f'link: missing or outside repository from {path.relative_to(root)}')
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    for error in errors:
        print(error)
    print(f'Validation: {len(errors)} finding(s)')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
