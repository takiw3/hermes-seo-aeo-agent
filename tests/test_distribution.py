"""Offline distribution contract regression tests. All fixtures are synthetic."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
OWNED = ['distribution.yaml', 'profile.yaml', 'SOUL.md', 'config.yaml',
         'templates', 'references', 'skills/seo-aeo-core']


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.put('distribution.yaml', yaml.safe_dump({
            'name': 'seo-aeo', 'version': '1.0.0', 'hermes_requires': '>=0.20.0',
            'description': 'Search research and draft specialist.', 'license': 'MIT',
            'distribution_owned': OWNED}))
        self.put('profile.yaml', 'description: Owns search research and drafts.\ndescription_auto: false\ndisplay_name: SEO/AEO\n')
        self.put('config.yaml', yaml.safe_dump({
            'memory': {'write_approval': True}, 'skills': {'write_approval': True},
            'curator': {'consolidate': False}, 'delegation': {'subagent_auto_approve': False},
            'terminal': {'home_mode': 'profile'},
            'approvals': {'mode': 'manual', 'cron_mode': 'deny', 'single_query_mode': 'deny'}}))
        self.put('SOUL.md', '# Synthetic identity\nResearch and draft only.\n')
        self.put('templates/brief.md', '# Brief\n')
        self.put('references/sources.md', '# Sources\n')
        self.skill('sample')
        self.put('README.md', '# Synthetic repository\n\n| Skill | Produces |\n| --- | --- |\n| [sample](skills/seo-aeo-core/sample/SKILL.md) | Draft brief |\n')

    def put(self, rel, content):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')

    def skill(self, name):
        self.put(f'skills/seo-aeo-core/{name}/SKILL.md',
                 f'---\nname: {name}\ndescription: Use when a synthetic draft is needed.\n---\n# Draft\nMake a draft.\n')

    def validate(self):
        return subprocess.run([sys.executable, str(ROOT/'scripts/validate.py'), '--root', str(self.root)],
                              capture_output=True, text=True, timeout=30)

    def rejects(self, fragment):
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(fragment, result.stdout)

    def test_manifest_rejects_unsafe_ownership(self):
        manifest = yaml.safe_load((self.root/'distribution.yaml').read_text())
        for owned in [OWNED + ['docs'], ['skills'], OWNED + ['../outside'], OWNED + ['/absolute'], OWNED + [OWNED[0]]]:
            with self.subTest(owned=owned):
                self.put('distribution.yaml', yaml.safe_dump(dict(manifest, distribution_owned=owned)))
                self.rejects('manifest')

    def test_config_safety_values_are_structural(self):
        original = yaml.safe_load((self.root/'config.yaml').read_text())
        for section, key in [('memory', 'write_approval'), ('skills', 'write_approval'),
                             ('curator', 'consolidate'), ('delegation', 'subagent_auto_approve'),
                             ('terminal', 'home_mode'), ('approvals', 'mode'),
                             ('approvals', 'cron_mode'), ('approvals', 'single_query_mode')]:
            with self.subTest(section=section, key=key):
                config = yaml.safe_load(yaml.safe_dump(original))
                config[section][key] = 'unsafe'
                self.put('config.yaml', yaml.safe_dump(config))
                self.rejects('config')
        self.put('config.yaml', yaml.safe_dump(dict(original, provider='synthetic-provider')))
        self.rejects('provider-neutral')

    def test_skills_require_valid_frontmatter_names_and_short_descriptions(self):
        path = 'skills/seo-aeo-core/sample/SKILL.md'
        for header in ['name: wrong\ndescription: Use when drafting.',
                       'name: sample\ndescription: ' + 'x'*61,
                       'name: sample\ndescription: [invalid]', 'name: sample']:
            self.put(path, '---\n' + header + '\n---\nBody.\n')
            self.rejects('skill')
        self.skill('sample')
        self.put('skills/seo-aeo-core/other/SKILL.md', (self.root/path).read_text())
        self.rejects('duplicate')

    def test_readme_table_covers_each_skill(self):
        self.put('README.md', '# No skill table\n')
        self.rejects('README')
        self.put('README.md', '| Skill | Produces |\n| --- | --- |\n| sample | A draft |\n')
        self.rejects('README')

    def test_markdown_links_resolve_locally(self):
        self.put('docs/test.md', '[missing](missing.md)\n')
        self.rejects('link')
        self.put('docs/test.md', '[escape](../../outside.md)\n')
        self.rejects('link')
        self.put('docs/test.md', '[ok](../SOUL.md#anchor) [remote](https://example.com) '
                 '[placeholder]({{output_path}}) [local](#anchor)\n')
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_symlinks_and_private_runtime_files_are_rejected(self):
        (self.root/'escape').symlink_to(self.root/'SOUL.md')
        self.rejects('symlink')
        (self.root/'escape').unlink()
        for rel in ['.env', 'auth.json', 'local/queue.json', 'memories/owner.md',
                    'sessions/run.json', 'credentials.json', 'snapshot.sqlite',
                    'nested/google_token.json', 'cron/jobs.json', 'mcp.json']:
            with self.subTest(rel=rel):
                self.put(rel, 'synthetic private state')
                self.rejects('private')
                (self.root/rel).unlink()

    def test_secret_scan_redacts_evidence_without_synthetic_false_positives(self):
        fake = 'gh' + 'p_' + 'Z'*36
        self.put('references/leak.md', fake)
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('secret', result.stdout)
        self.assertNotIn(fake, result.stdout)
        self.put('references/leak.md', 'api_key: YOUR_API_KEY\nExample: synthetic-token\n')
        self.assertEqual(self.validate().returncode, 0)

    def test_manifest_and_profile_identity(self):
        original = yaml.safe_load((self.root/'distribution.yaml').read_text())
        for key, value in [('name', 'wrong'), ('version', 'not-semver'), ('hermes_requires', '>=0.19.1'),
                           ('source', 'synthetic-source'), ('env_requires', [{'name': 'KEY'}])]:
            with self.subTest(key=key):
                self.put('distribution.yaml', yaml.safe_dump(dict(original, **{key: value})))
                self.rejects('manifest')
        self.put('distribution.yaml', yaml.safe_dump(original))
        self.put('profile.yaml', 'description_auto: true\n')
        self.rejects('profile')

    def test_all_yaml_parses_and_duplicate_keys_fail(self):
        self.put('templates/broken.yaml', 'key: [\n')
        self.rejects('yaml')
        self.put('templates/broken.yaml', 'key: first\nkey: second\n')
        self.rejects('yaml')

    def test_runtime_payload_is_present_and_has_no_repo_only_subtrees(self):
        (self.root/'SOUL.md').unlink()
        self.rejects('payload')
        self.put('SOUL.md', '# Synthetic identity\n')
        self.put('templates/tests/private-test.py', '# repository-only\n')
        self.rejects('payload')

    def test_install_environment_does_not_inherit_credentials(self):
        import importlib.util
        path = ROOT/'scripts/test_install.py'
        self.assertTrue(path.is_file(), 'isolated install runner must exist')
        spec = importlib.util.spec_from_file_location('install_checks', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        env = module.isolated_environment(self.root, '/usr/local/bin/hermes')
        self.assertEqual(env['HOME'], str(self.root/'home'))
        self.assertEqual(env['HERMES_HOME'], str(self.root/'hermes-root'))
        self.assertNotIn('OPENAI_API_KEY', env)
        self.assertNotIn('HERMES_PROFILE', env)
        self.assertNotIn('PYTHONPATH', env)
        self.assertEqual(env['GIT_CONFIG_GLOBAL'], '/dev/null')

    def test_ignored_development_cache_links_are_not_repository_links(self):
        self.put('.venv/docs/cache.md', '[not repo](missing.md)\n')
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_non_utf8_document_reports_finding_without_traceback(self):
        (self.root/'skills/seo-aeo-core/sample/SKILL.md').write_bytes(bytes([255, 254]))
        result = self.validate()
        self.assertEqual(result.returncode, 1)
        self.assertIn('file: unreadable', result.stdout)
        self.assertNotIn('Traceback', result.stderr)

    def test_install_refuses_unknown_payload_roots(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('install_roots', ROOT/'scripts/test_install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaisesRegex(RuntimeError, 'allowlist'):
            module.payload_files(self.root, ['../outside'])

    def test_install_rejects_symlinks_before_staging_reads(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location('install_symlinks', ROOT/'scripts/test_install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        (self.root/'escape').symlink_to(self.root/'missing')
        try:
            module.exercise(self.root, '/nonexistent/hermes')
        except Exception as exc:
            self.assertIsInstance(exc, RuntimeError)
            self.assertIn('symlinks', str(exc))
        else:
            self.fail('must reject source symlink before staging')

    def test_live_instance_path_and_generic_credential_assignment(self):
        self.put('references/leak.md', '/home/' + 'synthetic-owner' + '/.hermes/' + 'profiles/client-a')
        self.rejects('private')
        self.put('references/leak.md', 'access_token: ' + 'A1b2'*10 + '\n')
        self.rejects('secret')

    def test_installed_payload_rejects_unknown_repo_only_file(self):
        import importlib.util
        import shutil
        spec = importlib.util.spec_from_file_location('install_payload', ROOT/'scripts/test_install.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.put('authoring-notes.txt', 'not runtime data\n')
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/'installed'
            shutil.copytree(self.root, target)
            (target/'README.md').unlink()
            files = module.payload_files(self.root, OWNED)
            with self.assertRaisesRegex(RuntimeError, 'repository-only'):
                module.verify_payload(target, self.root, files)

    def test_valid_distribution(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
