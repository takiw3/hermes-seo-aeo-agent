"""Offline behavior tests; never connect to or mutate a real CMS."""
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import socket
import os
import subprocess
import sys
from unittest.mock import Mock, patch
import unittest
from datetime import datetime, timedelta, timezone

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/seo-aeo-core/editorial-scheduling/scripts/content_queue.py'


def load_module():
    if not SCRIPT.exists():
        return None
    spec = importlib.util.spec_from_file_location('content_queue', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cq = load_module()
NOW = datetime(2030, 1, 1, tzinfo=timezone.utc)


def draft(**changes):
    value = dict(origin='https://example.com', scheduled_at='2030-01-02T09:00:00-05:00',
                 title='Owner reviewed article', slug='owner-reviewed-article',
                 content='<p>Evidence-backed draft.</p>', excerpt='A reviewed summary.')
    value.update(changes)
    return value


ENV = {'SEO_AEO_WP_ENABLE_SCHEDULING': '1', 'SEO_AEO_WP_ORIGIN': 'https://example.com',
       'SEO_AEO_WP_USERNAME': 'dedicated-author', 'SEO_AEO_WP_APPLICATION_PASSWORD': 'test-secret'}


class FakeWordPress:
    """Only transport is simulated; queue/SQLite/approval logic remains real."""
    def __init__(self, before_post=None, failure=None, change=None):
        self.calls = []
        self.before_post, self.failure, self.change = before_post, failure, change
        self.saved = None

    def request(self, method, path, payload=None):
        self.calls.append((method, path, payload))
        if method == 'POST':
            if self.before_post:
                self.before_post()
            if self.failure:
                raise self.failure
            self.saved = dict(payload, id=42, type='post')
            for field in ('title', 'content', 'excerpt'):
                self.saved[field] = {'raw': payload[field], 'rendered': payload[field]}
            return {'id': 42}
        result = json.loads(json.dumps(self.saved))
        if self.change:
            result.update(self.change)
        return result


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / 'queue.sqlite3'

    def queue(self):
        self.assertIsNotNone(cq, 'content queue implementation is missing')
        return cq.Queue(self.db, clock=lambda: NOW)

    def approved(self, queue):
        item_id = queue.enqueue(draft())
        token = queue.approve(item_id, queue.preview(item_id)['sha256'], '2030-01-01T01:00:00Z')
        return item_id, token

    def test_submit_consumes_approval_before_post_and_verifies_exact_target(self):
        queue = self.queue()
        self.assertTrue(hasattr(queue, 'submit'), 'native submission workflow missing')
        item_id, token = self.approved(queue)
        def before_post():
            self.assertEqual(self.queue().preview(item_id)['state'], 'in_flight')
            with self.assertRaises(ValueError):
                queue.cancel(item_id)
            with self.assertRaises(ValueError):
                queue.submit(item_id, token, env=ENV, transport=transport)
        transport = FakeWordPress(before_post=before_post)
        result = queue.submit(item_id, token, env=ENV, transport=transport)
        self.assertEqual(result['state'], 'scheduled')
        self.assertEqual(queue.status()[0]['remote_id'], 42)
        self.assertEqual([(m, p) for m, p, _ in transport.calls], [
            ('POST', '/wp-json/wp/v2/posts'), ('GET', '/wp-json/wp/v2/posts/42?context=edit')])
        self.assertEqual(transport.calls[0][2], queue.preview(item_id)['envelope']['payload'])
        with self.assertRaises(ValueError):
            queue.submit(item_id, token, env=ENV, transport=transport)
        self.assertEqual(len(transport.calls), 2)

    def test_submit_fails_closed_without_exact_live_approval_and_configuration(self):
        queue = self.queue()
        cases = ['off', 'credentials-only', 'missing-secret', 'different-origin', 'bad-token',
                 'expired', 'too-late', 'changed-title', 'changed-time', 'changed-target', 'other-item']
        for case in cases:
            with self.subTest(case=case):
                item_id, token = self.approved(queue)
                env = dict(ENV)
                transport = FakeWordPress()
                target_queue = queue
                if case == 'off': env['SEO_AEO_WP_ENABLE_SCHEDULING'] = 'true'
                if case == 'credentials-only': del env['SEO_AEO_WP_ENABLE_SCHEDULING']
                if case == 'missing-secret': del env['SEO_AEO_WP_APPLICATION_PASSWORD']
                if case == 'different-origin': env['SEO_AEO_WP_ORIGIN'] = 'https://other.com'
                if case == 'bad-token': token = 'wrong'
                if case == 'expired': target_queue = cq.Queue(self.db, clock=lambda: NOW + timedelta(hours=1))
                if case == 'too-late': target_queue = cq.Queue(self.db, clock=lambda: NOW + timedelta(days=2))
                if case.startswith('changed-'):
                    preview = queue.preview(item_id)['envelope']
                    if case == 'changed-title': preview['payload']['title'] = 'Not approved'
                    if case == 'changed-time': preview['scheduled_at'] = '2030-01-03T00:00:00Z'
                    if case == 'changed-target': preview['endpoint'] = 'https://evil.com/wp-json/wp/v2/posts'
                    with closing(queue.connect()) as con, con:
                        con.execute('UPDATE items SET envelope=? WHERE id=?', (json.dumps(preview), item_id))
                if case == 'other-item':
                    _, token = self.approved(queue)
                with self.assertRaises(ValueError):
                    target_queue.submit(item_id, token, env=env, transport=transport)
                self.assertEqual(transport.calls, [])
                self.assertEqual(queue.preview(item_id)['state'], 'approved')

    def test_ambiguous_submission_never_retries_or_exposes_transport_secrets(self):
        queue = self.queue()
        item_id, token = self.approved(queue)
        transport = FakeWordPress(failure=TimeoutError('test-secret Authorization Basic SECRET'))
        with self.assertRaisesRegex(ValueError, 'uncertain') as error:
            queue.submit(item_id, token, env=ENV, transport=transport)
        self.assertNotIn('test-secret', str(error.exception))
        self.assertEqual(queue.preview(item_id)['state'], 'uncertain')
        with self.assertRaises(ValueError):
            queue.submit(item_id, token, env=ENV, transport=transport)
        self.assertEqual(len(transport.calls), 1)
        self.assertNotIn('test-secret', json.dumps(queue.status()))

    def test_any_readback_difference_is_uncertain_not_success(self):
        queue = self.queue()
        changes = [{'status': 'publish'}, {'id': 43}, {'type': 'page'}, {'slug': 'renamed'},
                   {'date_gmt': '2030-01-02T15:00:00'}, {'title': {'raw': 'Changed'}},
                   {'content': {'raw': 'Sanitized'}}, {'excerpt': {'raw': 'Changed'}},
                   {'title': {'rendered': draft()['title']}}, {'sticky': True}]
        for change in changes:
            with self.subTest(change=change):
                item_id, token = self.approved(queue)
                transport = FakeWordPress(change=change)
                with self.assertRaisesRegex(ValueError, 'uncertain'):
                    queue.submit(item_id, token, env=ENV, transport=transport)
                self.assertEqual(queue.preview(item_id)['state'], 'uncertain')
                self.assertEqual(queue.status()[-1]['remote_id'], 42)
                with self.assertRaises(ValueError):
                    queue.submit(item_id, token, env=ENV, transport=transport)
                self.assertEqual(len(transport.calls), 2)

    def test_default_transport_posts_json_then_reads_back_with_same_pinned_origin(self):
        queue = self.queue()
        item_id, token = self.approved(queue)
        self.assertTrue(hasattr(cq.WordPressTransport, 'request'), 'HTTP request implementation missing')
        responses = [Mock(status=201), Mock(status=200)]
        responses[0].read.return_value = b'{"id":42}'
        responses[1].read.return_value = (Path(__file__).parent / 'fixtures/scheduling/wordpress-edit-response.json').read_bytes()
        connections = [Mock(), Mock()]
        for connection, response in zip(connections, responses):
            connection.getresponse.return_value = response
        public = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))
        with patch.object(cq.socket, 'getaddrinfo', return_value=[public]) as dns, \
             patch.object(cq, 'PinnedHTTPSConnection', side_effect=connections) as factory:
            result = queue.submit(item_id, token, env=ENV)
        self.assertEqual(result['state'], 'scheduled')
        self.assertEqual(dns.call_count, 1)
        self.assertEqual(factory.call_count, 2)
        for call in factory.call_args_list:
            self.assertEqual(call.args, ('example.com', public))
        method, path = connections[0].request.call_args.args
        self.assertEqual((method, path), ('POST', '/wp-json/wp/v2/posts'))
        kwargs = connections[0].request.call_args.kwargs
        self.assertEqual(json.loads(kwargs['body']), queue.preview(item_id)['envelope']['payload'])
        self.assertTrue(kwargs['headers']['Authorization'].startswith('Basic '))
        self.assertEqual(connections[1].request.call_args.args, ('GET', '/wp-json/wp/v2/posts/42?context=edit'))
        for connection in connections:
            connection.close.assert_called_once()

    def test_unsafe_stored_payload_cannot_be_approved_even_with_matching_hash(self):
        queue = self.queue()
        for change in ({'status': 'publish'}, {'id': 42}, {'date_gmt': '2020-01-01T00:00:00'},
                       {'content': 'x' * 200001}):
            with self.subTest(change=list(change)):
                item_id = queue.enqueue(draft())
                envelope = queue.preview(item_id)['envelope']
                envelope['payload'].update(change)
                with closing(queue.connect()) as con, con:
                    con.execute('UPDATE items SET envelope=? WHERE id=?', (json.dumps(envelope), item_id))
                with self.assertRaises(ValueError):
                    queue.approve(item_id, queue.preview(item_id)['sha256'], '2030-01-01T01:00:00Z')
        with self.assertRaises(ValueError):
            queue.enqueue(draft(scheduled_at='2030-01-02T09:00:00+00:99'))

    def test_cli_owner_workflow_is_local_by_default_and_requires_explicit_db(self):
        def cli(*args, input=None):
            env = dict(os.environ, **ENV)
            env.pop('SEO_AEO_WP_ENABLE_SCHEDULING', None)
            return subprocess.run([sys.executable, str(SCRIPT), *args], input=input, env=env,
                                  capture_output=True, text=True, timeout=10)
        help_result = cli('--help')
        self.assertIn('enqueue', help_result.stdout)
        self.assertEqual(help_result.returncode, 0)
        self.assertNotEqual(cli('status').returncode, 0)
        self.assertFalse(self.db.exists())
        source = Path(self.tmp.name) / 'draft.json'
        source.write_text(json.dumps(draft(scheduled_at='2099-01-02T09:00:00-05:00')))
        result = cli('--db', str(self.db), 'enqueue', '--json', str(source))
        self.assertEqual(result.returncode, 0, result.stderr)
        item_id = json.loads(result.stdout)['id']
        preview = json.loads(cli('--db', str(self.db), 'preview', item_id).stdout)
        sha = preview['sha256']
        expires = (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0).isoformat()
        args = ('--db', str(self.db), 'approve', item_id, '--sha256', sha, '--expires', expires)
        self.assertNotEqual(cli(*args).returncode, 0)
        approved = cli(*args, '--owner-confirm')
        self.assertEqual(approved.returncode, 0, approved.stderr)
        token = json.loads(approved.stdout)['approval_token']
        blocked = cli('--db', str(self.db), 'submit', item_id, '--approval-stdin', input=token + '\n')
        self.assertNotEqual(blocked.returncode, 0)
        self.assertNotIn('test-secret', blocked.stdout + blocked.stderr)
        self.assertEqual(json.loads(cli('--db', str(self.db), 'status').stdout)[0]['state'], 'approved')
        self.assertEqual(json.loads(cli('--db', str(self.db), 'due').stdout), [])
        self.assertEqual(cli('--db', str(self.db), 'cancel', item_id).returncode, 0)
        self.assertEqual(self.db.stat().st_mode & 0o777, 0o600)

    def test_cli_rejects_oversize_or_duplicate_json_and_nonpersistent_db(self):
        for db in ('', ':memory:'):
            with self.subTest(db=db), self.assertRaises(ValueError):
                cq.Queue(db)
        source = Path(self.tmp.name) / 'draft.json'
        valid = json.dumps(draft(scheduled_at='2099-01-02T09:00:00Z'))
        for text in (' ' * 524288 + valid, valid[:-1] + ', "title": "ambiguous"}'):
            source.write_text(text)
            result = subprocess.run([sys.executable, str(SCRIPT), '--db', str(self.db),
                                     'enqueue', '--json', str(source)], capture_output=True, text=True)
            with self.subTest(size=len(text)):
                self.assertNotEqual(result.returncode, 0)

    def test_concurrent_connections_allow_only_one_post(self):
        first, second = self.queue(), self.queue()
        item_id, token = self.approved(first)
        transport, barrier = FakeWordPress(), threading.Barrier(2)
        def worker(queue):
            barrier.wait(timeout=5)
            try:
                return queue.submit(item_id, token, env=ENV, transport=transport)['state']
            except ValueError:
                return 'rejected'
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(worker, (first, second)))
        self.assertCountEqual(results, ['scheduled', 'rejected'])
        self.assertEqual(sum(method == 'POST' for method, _, _ in transport.calls), 1)

    def test_process_interrupt_leaves_inflight_record_nonretryable(self):
        queue = self.queue()
        item_id, token = self.approved(queue)
        transport = FakeWordPress(failure=KeyboardInterrupt())
        with self.assertRaises(KeyboardInterrupt):
            queue.submit(item_id, token, env=ENV, transport=transport)
        self.assertEqual(queue.preview(item_id)['state'], 'in_flight')
        with self.assertRaises(ValueError):
            queue.submit(item_id, token, env=ENV, transport=transport)
        self.assertEqual(len(transport.calls), 1)

    def test_invalid_created_ids_are_never_used_as_readback_paths(self):
        queue = self.queue()
        for remote_id in (True, -1, 0, '../../users', 'https://evil.com', 2**65):
            with self.subTest(remote_id=remote_id):
                item_id, token = self.approved(queue)
                transport = Mock()
                transport.request.return_value = {'id': remote_id}
                with self.assertRaises(ValueError):
                    queue.submit(item_id, token, env=ENV, transport=transport)
                self.assertEqual(transport.request.call_count, 1)
                self.assertEqual(queue.preview(item_id)['state'], 'uncertain')

    def test_preview_status_due_and_cancel_are_offline_and_cancel_rejects_submission(self):
        queue = self.queue()
        with patch.object(cq.socket, 'getaddrinfo', side_effect=AssertionError('No network allowed')), \
             patch.object(cq, 'WordPressTransport', side_effect=AssertionError('No transport allowed')):
            item_id, token = self.approved(queue)
            queue.preview(item_id)
            queue.status()
            queue.due()
            queue.cancel(item_id)
            with self.assertRaises(ValueError):
                queue.submit(item_id, token, env=ENV)
            with self.assertRaises(ValueError):
                queue.preview('missing-id')

    def test_owner_approval_is_exact_expiring_and_cancelable(self):
        queue = self.queue()
        self.assertTrue(hasattr(queue, 'approve'), 'owner approval workflow missing')
        item_id = queue.enqueue(draft())
        sha = queue.preview(item_id)['sha256']
        with self.assertRaises(ValueError):
            queue.approve(item_id, '0' * 64, '2030-01-01T01:00:00Z')
        for expiry in ('2030-01-01T00:00:00Z', '2030-01-03T00:00:00Z', '2030-01-01T01:00:00'):
            with self.assertRaises(ValueError):
                queue.approve(item_id, sha, expiry)
        token = queue.approve(item_id, sha, '2030-01-01T01:00:00Z')
        self.assertEqual(len(token), 64)
        self.assertNotIn(token.encode(), self.db.read_bytes())
        self.assertEqual(queue.preview(item_id)['state'], 'approved')
        with self.assertRaises(ValueError):
            queue.approve(item_id, sha, '2030-01-01T01:00:00Z')
        self.assertEqual(queue.status()[0]['state'], 'approved')
        self.assertEqual(queue.due(), [])
        late = cq.Queue(self.db, clock=lambda: NOW + timedelta(days=2))
        self.assertEqual(late.due()[0]['id'], item_id)
        queue.cancel(item_id)
        self.assertEqual(queue.preview(item_id)['state'], 'cancelled')
        self.assertEqual(late.due(), [])
        with self.assertRaises(ValueError):
            queue.approve(item_id, sha, '2030-01-01T01:00:00Z')

    def test_invalid_drafts_are_rejected_before_storage(self):
        queue = self.queue()
        invalid = [
            {'origin': origin} for origin in (
                'http://example.com', 'https://user:password@example.com', 'https://127.0.0.1',
                'https://[::1]', 'https://localhost', 'https://internal.local',
                'https://example.com/path', 'https://example.com/', 'https://example.com:444',
                'https://example.com?x=1', 'https://example.com#fragment',
                'https://example.com\\@evil.com', 'https://EXAMPLE.com',
                'https://example.com\n', 'https://2130706433', 'https://a..com')]
        invalid += [{'scheduled_at': stamp} for stamp in (
            '2030-01-02T09:00:00', '2029-12-31T23:59:59Z', '2030-01-01T00:04:59Z',
            '2030-01-02', '2030-01-02T09:00:00.1Z', '2030-99-02T09:00:00Z')]
        invalid += [{'status': 'publish'}, {'endpoint': 'https://evil.com'}, {'title': ''},
                    {'title': 'line\nbreak'}, {'slug': '../admin'}, {'slug': 'BAD SLUG'},
                    {'content': 'a' * 200001}, {'excerpt': 'a' * 10001}, {'title': 1},
                    {'content': 'bad\x00'}, {'content': '\ud800'}]
        for change in invalid:
            with self.subTest(change=repr(change)[:100]), self.assertRaises(ValueError):
                queue.enqueue(draft(**change))
        item_id = queue.enqueue(draft(scheduled_at='2030-01-01T00:05:00Z'))
        self.assertEqual(queue.preview(item_id)['envelope']['payload']['date_gmt'], '2030-01-01T00:05:00')

    def test_enqueue_persists_exact_canonical_preview(self):
        queue = self.queue()
        item_id = queue.enqueue(draft())
        preview = cq.Queue(self.db, clock=lambda: NOW).preview(item_id)
        envelope = preview['envelope']
        self.assertEqual(envelope['endpoint'], 'https://example.com/wp-json/wp/v2/posts')
        self.assertEqual(envelope['scheduled_at'], draft()['scheduled_at'])
        self.assertEqual(envelope['payload'], {
            'title': draft()['title'], 'slug': draft()['slug'], 'content': draft()['content'],
            'excerpt': draft()['excerpt'], 'status': 'future', 'date_gmt': '2030-01-02T14:00:00',
            'comment_status': 'closed', 'ping_status': 'closed', 'sticky': False, 'format': 'standard',
        })
        canonical = json.dumps(envelope, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        self.assertEqual(preview['sha256'], hashlib.sha256(canonical.encode()).hexdigest())
        self.assertEqual(preview['state'], 'draft')
        self.assertEqual(queue.preview(item_id), preview)


class TransportTests(unittest.TestCase):
    def test_every_dns_answer_must_be_public_without_transition_addresses(self):
        public = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))
        for ip in ('127.0.0.1', '10.0.0.1', '169.254.169.254', '192.168.1.2', '172.16.0.1',
                   '0.0.0.0', '100.64.0.1', '224.0.0.1', '240.0.0.1', '::1', 'fc00::1',
                   'fe80::1', '::ffff:127.0.0.1', '64:ff9b::7f00:1', '2002:7f00:1::1'):
            address = ((socket.AF_INET6, socket.SOCK_STREAM, 6, '', (ip, 443, 0, 0)) if ':' in ip
                       else (socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, 443)))
            with self.subTest(ip=ip), self.assertRaises(ValueError):
                cq.WordPressTransport('https://example.com', 'author', 'test-secret',
                                      resolver=lambda *a, **kw: [public, address])
        with self.assertRaises(ValueError):
            cq.WordPressTransport('https://example.com', 'author', 'test-secret', resolver=lambda *a, **kw: [])

    def test_transport_rejects_redirects_wrong_status_oversize_and_arbitrary_routes(self):
        public = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))
        transport = cq.WordPressTransport('https://example.com', 'author', 'test-secret',
                                          resolver=lambda *a, **kw: [public])
        for status, body in [(301, b'{}'), (302, b'{}'), (307, b'{}'), (308, b'{}'), (401, b'{}'),
                             (500, b'{}'), (200, b'{}'), (201, b'x' * 524289), (201, b'[]'), (201, b'not json')]:
            with self.subTest(status=status, size=len(body)):
                connection = Mock()
                response = connection.getresponse.return_value
                response.status, response.read.return_value = status, body
                with patch.object(cq, 'PinnedHTTPSConnection', return_value=connection) as factory:
                    with self.assertRaises(ValueError):
                        transport.request('POST', '/wp-json/wp/v2/posts', {'status': 'future'})
                self.assertEqual(factory.call_count, 1)
                connection.close.assert_called_once()
                if status == 201:
                    response.read.assert_called_once_with(524289)
        for method, path in [('DELETE', '/wp-json/wp/v2/posts/42'), ('POST', '/wp-json/wp/v2/posts/42'),
                             ('POST', 'https://evil.com'), ('GET', '//evil.com'), ('GET', '/wp-json/wp/v2/users')]:
            with self.subTest(method=method, path=path), patch.object(cq, 'PinnedHTTPSConnection') as factory:
                with self.assertRaises(ValueError):
                    transport.request(method, path)
                factory.assert_not_called()

    def test_invalid_credentials_and_oversized_requests_fail_before_connect(self):
        public = (socket.AF_INET, socket.SOCK_STREAM, 6, '', ('93.184.216.34', 443))
        for username, password in [('a:b', 'secret'), ('author', ''), ('author\n', 'secret'),
                                   ('author', 'secret\r\n'), ('author', 'x' * 513)]:
            with self.subTest(username=username), self.assertRaises(ValueError):
                cq.WordPressTransport('https://example.com', username, password, resolver=lambda *a, **kw: [public])
        transport = cq.WordPressTransport('https://example.com', 'author', 'test-secret', resolver=lambda *a, **kw: [public])
        with self.subTest(check='request-size'), patch.object(cq, 'PinnedHTTPSConnection') as factory:
            with self.assertRaises(ValueError):
                transport.request('POST', '/wp-json/wp/v2/posts', {'content': 'x' * 524289})
            self.assertEqual(factory.call_count, 0)
        connection = Mock()
        connection.getresponse.return_value.status = 201
        connection.getresponse.return_value.read.return_value = b'{"id":42,"id":43}'
        with patch.object(cq, 'PinnedHTTPSConnection', return_value=connection), self.assertRaises(ValueError):
            transport.request('POST', '/wp-json/wp/v2/posts', {'status': 'future'})

    def test_pinned_public_socket_preserves_tls_hostname_and_never_reresolves(self):
        self.assertTrue(hasattr(cq, 'WordPressTransport'), 'HTTPS transport missing')
        address = (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('93.184.216.34', 443))
        resolver = Mock(return_value=[address])
        transport = cq.WordPressTransport('https://example.com', 'author', 'test-secret', resolver=resolver)
        self.assertEqual(resolver.call_count, 1)
        raw_socket, tls_socket = Mock(), Mock()
        context = Mock()
        context.wrap_socket.return_value = tls_socket
        with patch.object(cq.socket, 'socket', return_value=raw_socket), \
             patch.object(cq.socket, 'getaddrinfo', side_effect=AssertionError('DNS re-resolution forbidden')):
            connection = cq.PinnedHTTPSConnection('example.com', transport.address, context=context)
            connection.connect()
        raw_socket.connect.assert_called_once_with(('93.184.216.34', 443))
        context.wrap_socket.assert_called_once_with(raw_socket, server_hostname='example.com')
        self.assertIs(connection.sock, tls_socket)


if __name__ == '__main__':
    unittest.main()
