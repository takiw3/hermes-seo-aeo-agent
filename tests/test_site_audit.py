"""Offline deterministic tests. No external network is required."""
import importlib.util
import gzip
import io
import json
from pathlib import Path
import sys
import unittest
import subprocess
import tempfile
from unittest.mock import patch, Mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/seo-aeo-core/site-audit/scripts/audit.py'


def load_audit():
    if not SCRIPT.exists():
        raise AssertionError('audit.py implementation is missing')
    spec = importlib.util.spec_from_file_location('site_audit', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ExtractionTests(unittest.TestCase):
    def test_extracts_static_html_signals_without_executing_scripts(self):
        audit = load_audit()
        page = audit.extract_html('''<html lang="en-CA"><head>
        <title>Useful &amp; clear</title><meta name="description" content="An example">
        <meta name="robots" content="noindex, follow">
        <link rel="canonical" href="/primary"><link rel="alternate" hreflang="fr" href="/fr">
        <script type="application/ld+json">{"@type":"Thing","name":"Example"}</script>
        <script type="application/ld+json">{broken}</script></head><body>
        <h1>Hello <em>world</em></h1><h2>Details</h2><a href="/next#part">Next</a>
        <img src="a.png" alt=""><img src="b.png"><img src="c.png" alt="Useful image">
        <script>throw new Error('never execute');</script></body></html>''',
        'https://example.com/', x_robots=['noarchive'])
        self.assertEqual(page['title'], 'Useful & clear')
        self.assertEqual(page['meta_descriptions'], ['An example'])
        self.assertEqual(page['headings'], [{'level': 1, 'text': 'Hello world'}, {'level': 2, 'text': 'Details'}])
        self.assertEqual(page['canonicals'], ['https://example.com/primary'])
        self.assertEqual(page['meta_robots'], [{'agent': 'robots', 'content': 'noindex, follow'}])
        self.assertEqual(page['x_robots'], ['noarchive'])
        self.assertEqual(page['links'], ['https://example.com/next#part'])
        self.assertEqual(page['images'], {'total': 3, 'missing_alt': 1, 'empty_alt': 1})
        self.assertEqual([x['valid_json'] for x in page['json_ld']], [True, False])
        self.assertEqual(page['hreflang'], [{'lang': 'fr', 'url': 'https://example.com/fr'}])
        self.assertEqual(page['lang'], 'en-CA')
        self.assertEqual(page['script_count'], 3)

    def test_html_base_controls_resolution_without_changing_crawl_origin(self):
        audit = load_audit()
        page = audit.extract_html('<base href="https://cdn.example/assets/"><a href="next">x</a><link rel="canonical" href="main">', 'https://example.com/')
        self.assertEqual(page['links'], ['https://cdn.example/assets/next'])
        self.assertEqual(page['canonicals'], ['https://cdn.example/assets/main'])
        self.assertEqual(page['url'], 'https://example.com/')

    def test_extraction_rejects_oversized_or_overcomplex_input(self):
        audit = load_audit()
        for html, reason in (('x' * 1048577, 'html_byte_cap'), ('<div></div>' * 10001, 'html_element_cap')):
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                audit.extract_html(html, 'https://example.com/')


class FindingsTests(unittest.TestCase):
    def test_findings_have_evidence_without_indexing_or_score_claims(self):
        audit = load_audit()
        self.assertTrue(callable(getattr(audit, 'build_report', None)), 'report builder missing')
        pages = [audit.extract_html('<title>Same</title><meta name="description" content="Same copy"><meta name="robots" content="noindex"><img src="x"><script type="application/ld+json">oops</script>', url)
                 for url in ('https://example.com/', 'https://example.com/two')]
        report = audit.build_report(pages, mode='offline')
        codes = {f['code'] for f in report['findings']}
        self.assertTrue({'duplicate_title', 'duplicate_description', 'noindex_directive', 'missing_h1', 'missing_alt', 'invalid_json_ld', 'missing_canonical', 'missing_lang'} <= codes)
        for finding in report['findings']:
            self.assertIn(finding['severity'], ('info', 'warning', 'error'))
            self.assertIn(finding['basis'], ('observed', 'heuristic'))
            self.assertTrue(finding['url'])
            self.assertTrue(finding['evidence'])
            self.assertTrue(finding['recommendation'])
        self.assertNotIn('score', report)
        self.assertIn('Google indexing', ' '.join(report['limitations']))
        self.assertIn('schema', ' '.join(report['manual_checks']).lower())
        self.assertIn('JavaScript', ' '.join(report['manual_checks']))

    def test_noindex_observation_handles_agent_prefix_and_none_whitespace(self):
        audit = load_audit()
        for directive in ('googlebot:noindex', ' none ', 'NOINDEX,follow'):
            with self.subTest(directive=directive):
                page = audit.extract_html('', 'https://example.com/', x_robots=[directive])
                report = audit.build_report([page], mode='offline')
                self.assertIn('noindex_directive', {f['code'] for f in report['findings']})


class URLSafetyTests(unittest.TestCase):
    def test_url_policy_rejects_unsafe_or_ambiguous_crawl_targets(self):
        audit = load_audit()
        self.assertTrue(callable(getattr(audit, 'normalize_url', None)), 'URL policy missing')
        self.assertEqual(audit.normalize_url('https://EXAMPLE.com:443/path#part'), 'https://example.com/path')
        for url in ('http://example.com/', 'https://u:p@example.com/', 'https://example.com/?x=1',
                    'https://example.com:8443/', 'https://example.com/\\\\evil', 'https://example.com/\nfoo',
                    'https://example.com/%2fsecret', 'https://example.com/%2e%2e/secret',
                    'https://example.com/%25secret', 'https://example.com/../secret',
                    'https://example.com./', 'https://example.com/%zz'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                audit.normalize_url(url)
        with self.assertRaises(ValueError):
            audit.normalize_url('https://other.example/', origin='https://example.com')

    def test_all_resolved_addresses_must_be_public_before_any_connection(self):
        audit = load_audit()
        self.assertTrue(callable(getattr(audit, 'validate_addresses', None)), 'IP guard missing')
        self.assertEqual(audit.validate_addresses(['93.184.216.34']), ['93.184.216.34'])
        for ip in ('127.0.0.1', '10.0.0.1', '169.254.169.254', '192.168.1.1', '0.0.0.0',
                   '100.64.0.1', '224.0.0.1', '192.0.2.1', '::1', 'fc00::1', 'fe80::1',
                   '::ffff:127.0.0.1', '64:ff9b::7f00:1', '2002:7f00:1::', '2001:db8::1'):
            with self.subTest(ip=ip), self.assertRaises(ValueError):
                audit.validate_addresses(['93.184.216.34', ip])
        with self.assertRaises(ValueError):
            audit.validate_addresses([])

    def test_cloud_platform_and_special_use_addresses_are_blocked(self):
        audit = load_audit()
        for ip in ('168.63.129.16', '192.0.0.9', '192.0.0.10', '2001:1::1'):
            with self.subTest(ip=ip), self.assertRaises(ValueError):
                audit.validate_addresses([ip])


class TransportTests(unittest.TestCase):
    def request_body(self, body, headers, max_bytes=1024):
        audit = load_audit()
        response = Mock(status=200)
        response.getheaders.return_value = headers
        response.read.side_effect = io.BytesIO(body).read
        conn = Mock()
        conn.getresponse.return_value = response
        with patch.object(audit.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('93.184.216.34', 443))]), \
             patch.object(audit, '_PinnedHTTPS', return_value=conn):
            try:
                return audit._request('https://example.com/', max_bytes=max_bytes)
            finally:
                conn.close.assert_called_once()
                if response.read.called:
                    response.read.assert_called_once_with(max_bytes + 1)

    def test_gzip_response_is_decoded_even_when_identity_was_requested(self):
        body = b'<title>Safe gzip</title>'
        compressed = gzip.compress(body)
        result = self.request_body(compressed, [('Content-Encoding', 'gzip'),
                                               ('Content-Length', str(len(compressed)))])
        self.assertEqual(result['body'], body)
        self.assertEqual(result['status'], 200)

    def test_gzip_decompressed_output_cap_rejects_bombs_and_one_extra_byte(self):
        for size in (1025, 1000000):
            compressed = gzip.compress(b'x' * size)
            self.assertLessEqual(len(compressed), 1024)
            with self.subTest(size=size), self.assertRaisesRegex(ValueError, 'response_byte_cap'):
                self.request_body(compressed, [('Content-Encoding', 'gzip')])

    def test_gzip_truncation_is_rejected_instead_of_returning_partial_body(self):
        compressed = gzip.compress(b'<title>Never partial</title>')
        for cut in range(len(compressed)):
            with self.subTest(cut=cut), self.assertRaisesRegex(ValueError, 'invalid_gzip_response'):
                self.request_body(compressed[:cut], [('Content-Encoding', 'gzip')])

    def test_gzip_trailing_bytes_or_additional_members_are_rejected(self):
        compressed = gzip.compress(b'first')
        for suffix in (b'garbage', b'\x00', gzip.compress(b'second'), gzip.compress(b'')):
            with self.subTest(suffix=suffix), self.assertRaisesRegex(ValueError, 'invalid_gzip_response'):
                self.request_body(compressed + suffix, [('Content-Encoding', 'gzip')])

    def test_duplicate_content_encoding_headers_are_rejected(self):
        for encodings in (('gzip', 'gzip'), ('gzip', 'identity'), ('identity', 'gzip')):
            with self.subTest(encodings=encodings), self.assertRaisesRegex(ValueError, 'ambiguous_content_encoding'):
                self.request_body(gzip.compress(b'payload'),
                                  [('Content-Encoding', value) for value in encodings])

    def test_gzip_compressed_input_has_its_own_cap(self):
        compressed = gzip.compress(b'x' * 1002, compresslevel=0)
        self.assertGreater(len(compressed), 1024)
        for length_headers in ([], [('Content-Length', str(len(compressed)))], [('Content-Length', '1')]):
            with self.subTest(headers=length_headers), self.assertRaisesRegex(ValueError, 'response_byte_cap'):
                self.request_body(compressed, [('Content-Encoding', 'gzip')] + length_headers)

    def test_gzip_checksum_corruption_is_rejected(self):
        compressed = bytearray(gzip.compress(b'checksum'))
        compressed[-8] ^= 1
        with self.assertRaisesRegex(ValueError, 'invalid_gzip_response'):
            self.request_body(bytes(compressed), [('Content-Encoding', 'gzip')])

    def test_unknown_or_stacked_content_encodings_are_rejected(self):
        for encoding in ('br', 'deflate', 'compress', 'x-gzip', 'gzip, gzip', 'gzip, identity'):
            with self.subTest(encoding=encoding), self.assertRaisesRegex(ValueError, 'compressed_response_not_supported'):
                self.request_body(gzip.compress(b'body'), [('Content-Encoding', encoding)])

    def test_identity_and_gzip_accept_exact_output_cap_and_empty_bodies(self):
        for body in (b'', b'x' * 1024):
            for encoding in (None, '', 'identity', 'gzip', ' GZip '):
                headers = [] if encoding is None else [('Content-Encoding', encoding)]
                wire = gzip.compress(body) if encoding and encoding.strip().lower() == 'gzip' else body
                with self.subTest(size=len(body), encoding=encoding):
                    self.assertEqual(self.request_body(wire, headers)['body'], body)

    def test_real_worker_decodes_gzip_within_the_existing_wall_deadline(self):
        audit = load_audit()
        real_run = subprocess.run
        # Mock the network in a real worker; the slow case stalls the decoder
        # to prove decompression stays inside the killable wall-clock budget.
        bootstrap = '''
import gzip, io, runpy, sys, time
from unittest.mock import Mock
worker = runpy.run_path(sys.argv[1])['_worker']
g = worker.__globals__
response = Mock(status=200)
response.getheaders.return_value = [('Content-Encoding', 'gzip')]
response.read.side_effect = io.BytesIO(gzip.compress(b'worker gzip')).read
conn = Mock()
conn.getresponse.return_value = response
g['_PinnedHTTPS'] = Mock(return_value=conn)
g['socket'].getaddrinfo = Mock(return_value=[(2, 1, 6, '', ('93.184.216.34', 443))])
if SLOW:
    g['zlib'].decompressobj = lambda *args: time.sleep(60)
worker()
'''
        for slow in (False, True):
            def run_worker(cmd, **kwargs):
                cmd = list(cmd)
                cmd[3] = bootstrap.replace('SLOW', repr(slow))
                return real_run(cmd, **kwargs)
            with self.subTest(slow=slow), patch.object(audit.subprocess, 'run', side_effect=run_worker):
                if slow:
                    with self.assertRaisesRegex(ValueError, 'request_timeout'):
                        audit.fetch('https://example.com/', timeout=1)
                else:
                    self.assertEqual(audit.fetch('https://example.com/', timeout=5)['body'], b'worker gzip')

    def test_socket_is_pinned_to_validated_ip_with_original_tls_hostname(self):
        audit = load_audit()
        self.assertTrue(callable(getattr(audit, '_request', None)), 'pinned HTTPS transport missing')
        raw, tls, context = Mock(), Mock(), Mock()
        context.wrap_socket.return_value = tls
        response = Mock(status=200)
        response.getheaders.return_value = [('Content-Type', 'text/html')]
        response.read.side_effect = [b'<title>Hi</title>', b'']
        with patch.object(audit.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('93.184.216.34', 443))]) as dns, \
             patch.object(audit.socket, 'socket', return_value=raw), \
             patch.object(audit.ssl, 'create_default_context', return_value=context), \
             patch.object(audit.http.client.HTTPSConnection, 'getresponse', return_value=response), \
             patch.object(audit.http.client.HTTPSConnection, 'request', autospec=True) as request:
            request.side_effect = lambda conn, *args, **kwargs: conn.connect()
            result = audit._request('https://example.com/', max_bytes=1024)
        raw.connect.assert_called_once_with(('93.184.216.34', 443))
        context.wrap_socket.assert_called_once_with(raw, server_hostname='example.com')
        self.assertEqual(dns.call_count, 1)
        self.assertEqual(result['body'], b'<title>Hi</title>')
        headers = request.call_args.kwargs['headers']
        self.assertEqual(headers['Accept-Encoding'], 'identity')
        self.assertNotIn('Cookie', headers)
        self.assertNotIn('Authorization', headers)
        tls.close.assert_called()

    def test_oversized_or_invalid_compressed_responses_are_not_accepted(self):
        audit = load_audit()
        for headers, body in ([('Content-Length', '1025')], b'x'), ([('Content-Encoding', 'gzip')], b'zip'), ([], b'x' * 1025):
            response = Mock(status=200)
            response.getheaders.return_value = headers
            response.read.return_value = body
            conn = Mock()
            conn.getresponse.return_value = response
            with self.subTest(headers=headers), \
                 patch.object(audit.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('93.184.216.34', 443))]), \
                 patch.object(audit, '_PinnedHTTPS', return_value=conn), self.assertRaises(ValueError):
                audit._request('https://example.com/', max_bytes=1024)

    def test_fetch_worker_fails_closed_on_private_ip_and_wall_timeout(self):
        audit = load_audit()
        self.assertTrue(callable(getattr(audit, 'fetch', None)), 'bounded worker missing')
        with self.assertRaisesRegex(ValueError, 'non_public_ip'):
            audit.fetch('https://127.0.0.1/')
        with patch.object(audit.subprocess, 'run', side_effect=audit.subprocess.TimeoutExpired('worker', 1)), \
             self.assertRaisesRegex(ValueError, 'request_timeout'):
            audit.fetch('https://example.com/', timeout=1)
        for budget in (0, -1, 1048577):
            with self.assertRaises(ValueError):
                audit.fetch('https://example.com/', max_bytes=budget)


class FramingTests(unittest.TestCase):
    def request_wire(self, body, headers, max_bytes=1024, reject_before_read=False):
        audit = load_audit()
        wire = (b'HTTP/1.1 200 OK\r\n' +
                ''.join(f'{name}: {value}\r\n' for name, value in headers).encode('ascii') +
                b'\r\n' + body)
        sock = Mock()
        sock.makefile.return_value = io.BytesIO(wire)
        response = audit.http.client.HTTPResponse(sock)
        response.begin()
        conn = Mock()
        conn.getresponse.return_value = response
        with patch.object(audit.socket, 'getaddrinfo', return_value=[(2, 1, 6, '', ('93.184.216.34', 443))]), \
             patch.object(audit, '_PinnedHTTPS', return_value=conn), \
             patch.object(response, 'read', wraps=response.read) as read:
            try:
                return audit._request('https://example.com/robots.txt', max_bytes=max_bytes)
            finally:
                conn.close.assert_called_once()
                if reject_before_read:
                    read.assert_not_called()
                response.close()

    def test_ambiguous_framing_headers_are_rejected_before_read(self):
        cases = [
            [('Content-Length', '3'), ('content-length', '3')],
            [('Content-Length', '3'), ('Content-Length', '4')],
            [('Content-Length', '3, 3')],
            [('Content-Length', '+3')],
            [('Content-Length', '-1')],
            [('Content-Length', '')],
            [('Transfer-Encoding', 'chunked'), ('Content-Length', '3')],
            [('Transfer-Encoding', 'chunked'), ('transfer-encoding', 'chunked')],
            [('Transfer-Encoding', 'gzip, chunked')],
            [('Transfer-Encoding', 'chunked, chunked')],
            [('Transfer-Encoding', 'identity')],
            [('Transfer-Encoding', '')],
        ]
        for headers in cases:
            with self.subTest(headers=headers), self.assertRaises(ValueError):
                self.request_wire(b'3\r\nabc\r\n0\r\n\r\n', headers, reject_before_read=True)

    def test_declared_oversize_is_rejected_before_read(self):
        with self.assertRaisesRegex(ValueError, 'response_byte_cap'):
            self.request_wire(b'x', [('Content-Length', '1025')], reject_before_read=True)

    def test_complete_length_chunked_and_close_delimited_bodies_are_accepted(self):
        for body in (b'', b'x' * 1024, gzip.compress(b'bounded gzip')):
            encoding = [('Content-Encoding', 'gzip')] if body.startswith(b'\x1f\x8b') else []
            expected = gzip.decompress(body) if encoding else body
            chunked = ((f'{len(body):x}\r\n'.encode() + body + b'\r\n') if body else b'') + b'0\r\n\r\n'
            for wire, framing in ((body, []), (body, [('Content-Length', str(len(body)))]),
                                  (chunked, [('Transfer-Encoding', 'chunked')])):
                with self.subTest(size=len(body), framing=framing, encoding=encoding):
                    self.assertEqual(self.request_wire(wire, encoding + framing)['body'], expected)

    def test_incomplete_chunked_bodies_are_not_returned(self):
        audit = load_audit()
        for wire in (b'3\r\nab', b'3\r\nabc\r\n', b'broken\r\nabc\r\n0\r\n\r\n'):
            with self.subTest(wire=wire), self.assertRaises((ValueError, audit.http.client.IncompleteRead)):
                self.request_wire(wire, [('Transfer-Encoding', 'chunked')])

    def test_truncated_robots_blocks_crawl_before_policy_or_html_parsing(self):
        audit = load_audit()
        body = b'User-agent: *\nDisallow: '
        headers = [('Content-Type', 'text/plain'), ('Content-Length', str(len(body) + 7))]
        with patch.object(audit, 'fetch', side_effect=lambda *args, **kwargs: self.request_wire(body, headers)) as fetch, \
             patch.object(audit, 'RobotsPolicy', wraps=audit.RobotsPolicy) as policy, \
             patch.object(audit, 'extract_html', wraps=audit.extract_html) as html, patch('time.sleep'):
            report = audit.audit_site('https://example.com/secret')
        self.assertEqual(report['coverage']['status'], 'blocked')
        self.assertEqual(report['coverage']['stop_reason'], 'robots_unreadable')
        self.assertEqual(report['coverage']['requests_made'], 1)
        self.assertEqual(report['pages'], [])
        fetch.assert_called_once()
        policy.assert_not_called()
        html.assert_not_called()

    def test_declared_length_must_match_raw_body_before_parsing_or_gzip(self):
        cases = [(b'User-agent: *\nDisallow: ', []),
                 (b'<title>Partial</title>', []),
                 (gzip.compress(b'User-agent: *\nDisallow: '), [('Content-Encoding', 'gzip')])]
        for body, headers in cases:
            with self.subTest(headers=headers, body=body), self.assertRaisesRegex(ValueError, 'incomplete_response'):
                self.request_wire(body, headers + [('Content-Length', str(len(body) + 7))])


class RobotsTests(unittest.TestCase):
    def test_escaped_literals_remain_distinct_from_wildcards_and_terminal_anchors(self):
        audit = load_audit()
        cases = [
            ('/path/file-with-a-%2A.html', '/path/file-with-a-*.html', False),
            ('/path/file-with-a-%2a.html', '/path/file-with-a-%2A.html', False),
            ('/path/file-with-a-%2A.html', '/path/file-with-a-name.html', True),
            ('/path/file-with-a-*.html$', '/path/file-with-a-name.html', False),
            ('/path/file-with-a-*.html$', '/path/file-with-a-*.html', False),
            ('/path/file-with-a-*.html$', '/path/file-with-a-name.html/more', True),
            ('/path/foo-%24', '/path/foo-$', False),
            ('/path/foo-%24', '/path/foo-%24', False),
            ('/path/foo-%24', '/path/foo-', True),
            ('/path/foo-%24', '/path/foo-$/more', False),
            ('/path/foo-%24$', '/path/foo-$', False),
            ('/path/foo-%24$', '/path/foo-$/more', True),
            ('/path/foo-$', '/path/foo-', False),
            ('/path/foo-$', '/path/foo-$', True),
            ('/path/foo-$-bar', '/path/foo-$-bar', False),
            ('/path/foo-$-bar', '/path/foo-%24-bar', False),
            ('/path/*%2A%24$', '/path/abc*$', False),
            ('/path/*%2A%24$', '/path/abc*$/more', True),
        ]
        for rule, path, allowed in cases:
            with self.subTest(rule=rule, path=path):
                policy = audit.RobotsPolicy('User-agent: *\nDisallow: ' + rule)
                self.assertEqual(policy.allowed(audit.normalize_url('https://example.com' + path)), allowed)
        policy = audit.RobotsPolicy('User-agent: *\nDisallow: /path/*\nAllow: /path/%2A$')
        self.assertTrue(policy.allowed(audit.normalize_url('https://example.com/path/*')))
        self.assertFalse(policy.allowed(audit.normalize_url('https://example.com/path/other')))

    def test_group_selection_wildcards_and_specificity_are_enforced(self):
        audit = load_audit()
        self.assertTrue(callable(getattr(audit, 'RobotsPolicy', None)), 'robots policy missing')
        policy = audit.RobotsPolicy('''User-agent: *
Disallow: /
User-agent: HermesSEOAudit
Disallow: /private
Allow: /private/public
Disallow: /*.pdf$
Crawl-delay: 2.5
User-agent: HermesSEOAudit
Disallow: /second
''')
        self.assertTrue(policy.allowed('https://example.com/'))
        self.assertFalse(policy.allowed('https://example.com/private'))
        self.assertTrue(policy.allowed('https://example.com/private/public'))
        self.assertFalse(policy.allowed('https://example.com/report.pdf'))
        self.assertTrue(policy.allowed('https://example.com/report.pdf/more'))
        self.assertFalse(policy.allowed('https://example.com/second'))
        self.assertEqual(policy.delay, 2.5)
        self.assertFalse(audit.RobotsPolicy('User-agent: *\nDisallow: /').allowed('https://example.com/'))
        self.assertTrue(audit.RobotsPolicy('User-agent: *\nDisallow: /\nAllow: /').allowed('https://example.com/'))

    def test_ambiguous_robots_is_rejected_not_treated_as_allow(self):
        audit = load_audit()
        for text in ('<html>Access denied</html>', 'Disallow: /private', 'User-agent: *',
                     'User-agent: *\nDissallow: /private', 'User-agent: *\nDisallow: relative',
                     'User-agent: *\nCrawl-delay: NaN', 'User-agent: *\nCrawl-delay: -1',
                     'User-agent: *\nCrawl-delay: 31', 'User-agent: *\nRequest-rate: 1/10',
                     'User-agent: *\nDisallow: /%zz', 'User-agent: *\nDisallow: /a\x00b'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                audit.RobotsPolicy(text)
        self.assertTrue(audit.RobotsPolicy('# empty rules').allowed('https://example.com/'))
        self.assertFalse(audit.RobotsPolicy('User-agent: *\nDisallow: /caf\u00e9').allowed('https://example.com/caf%C3%A9'))
        self.assertFalse(audit.RobotsPolicy('User-agent: *\nDisallow: /%70rivate').allowed('https://example.com/private'))


def response(body='', status=200, content_type='text/html', headers=()):
    return dict(status=status, body=body.encode('utf-8') if isinstance(body, str) else body,
                headers=[('Content-Type', content_type)] + list(headers))


class CrawlTests(unittest.TestCase):
    def test_unreadable_ambiguous_or_redirected_robots_prevents_page_requests(self):
        audit = load_audit()
        self.assertTrue(callable(getattr(audit, 'audit_site', None)), 'crawler missing')
        cases = [response('Not found', 404, 'text/plain'), response('', 403, 'text/plain'),
                 response('', 429, 'text/plain'), response('', 500, 'text/plain'),
                 response('', 301, 'text/plain', [('Location', 'https://other.example/robots.txt')]),
                 response('<html>denied</html>'), response('bad rules', content_type='text/plain'),
                 response(b'\xff', content_type='text/plain'), ValueError('request_timeout')]
        for result in cases:
            with self.subTest(result=result), patch.object(audit, 'fetch') as fetch:
                if isinstance(result, Exception):
                    fetch.side_effect = result
                else:
                    fetch.return_value = result
                report = audit.audit_site('https://example.com/')
                self.assertEqual(fetch.call_count, 1)
                self.assertEqual(fetch.call_args.args[0], 'https://example.com/robots.txt')
                self.assertEqual(report['coverage']['status'], 'blocked')
                self.assertEqual(report['pages'], [])
                self.assertEqual(report['coverage']['robots']['state'], 'unreadable')
                self.assertTrue(report['coverage']['errors'])

    def test_scoped_crawl_checks_robots_before_pages_paces_and_records_skips(self):
        audit = load_audit()
        routes = {
            'https://example.com/robots.txt': response('User-agent: *\nDisallow: /private\nCrawl-delay: 2', content_type='text/plain'),
            'https://example.com/': response('<title>Same</title><a href="/private">x</a><a href="/two">x</a><a href="/two#part">x</a><a href="/?calendar=1">x</a><a href="https://other.example/">x</a>'),
            'https://example.com/two': response('<title>Same</title>', headers=[('X-Robots-Tag', 'googlebot: noindex')]),
        }
        with patch.object(audit, 'fetch', side_effect=lambda url, **kwargs: routes[url]) as fetch, \
             patch('time.sleep') as sleep:
            report = audit.audit_site('https://example.com/')
        self.assertEqual([c.args[0] for c in fetch.call_args_list], list(routes))
        self.assertEqual(len(report['pages']), 2)
        self.assertEqual(report['pages'][1]['x_robots'], ['googlebot: noindex'])
        self.assertIn('duplicate_title', [f['code'] for f in report['findings']])
        self.assertEqual(report['coverage']['status'], 'complete')
        self.assertEqual(report['coverage']['requests_made'], 3)
        self.assertEqual({s['reason'] for s in report['coverage']['skipped']}, {'robots_disallowed', 'query_or_nonstandard_port', 'off_origin'})
        self.assertEqual(sleep.call_count, 2)
        self.assertTrue(all(c.args[0] >= 1.9 for c in sleep.call_args_list))

    def test_page_budget_counts_failed_requests_and_is_validated(self):
        audit = load_audit()
        robots = response('User-agent: *\nDisallow:', content_type='text/plain')
        root = response(''.join(f'<a href="/{i}">{i}</a>' for i in range(8)))
        for cap in (0, 51, -1, True):
            with self.subTest(cap=cap), patch.object(audit, 'fetch'), self.assertRaises(ValueError):
                audit.audit_site('https://example.com/', max_pages=cap)
        with patch.object(audit, 'fetch', side_effect=[robots, root] + [ValueError('request_timeout')] * 8) as fetch, patch('time.sleep'):
            report = audit.audit_site('https://example.com/', max_pages=3)
        self.assertEqual(fetch.call_count, 4)  # robots plus three attempted page URLs
        self.assertEqual(report['coverage']['status'], 'partial')
        self.assertEqual(report['coverage']['stop_reason'], 'page_cap')
        self.assertEqual(len(report['coverage']['errors']), 2)
        self.assertEqual(len(report['coverage']['pending']), 6)
        self.assertEqual(report['coverage']['limits']['max_pages'], 3)

    def test_redirect_targets_are_scoped_and_robots_checked_before_fetch(self):
        audit = load_audit()
        routes = {
            'https://example.com/robots.txt': response('User-agent: *\nDisallow: /private', content_type='text/plain'),
            'https://example.com/': response('<a href="/jump">x</a><a href="/out">x</a><a href="/blocked">x</a>'),
            'https://example.com/jump': response('', 302, headers=[('Location', '/two')]),
            'https://example.com/out': response('', 301, headers=[('Location', 'https://elsewhere.example/')]),
            'https://example.com/blocked': response('', 307, headers=[('Location', '/private')]),
            'https://example.com/two': response('<title>Final</title>'),
        }
        with patch.object(audit, 'fetch', side_effect=lambda url, **kwargs: routes[url]) as fetch, patch('time.sleep'):
            report = audit.audit_site('https://example.com/')
        self.assertEqual([c.args[0] for c in fetch.call_args_list], list(routes))
        self.assertEqual([p['url'] for p in report['pages']], ['https://example.com/', 'https://example.com/two'])
        self.assertEqual(len(report['coverage']['redirects']), 3)
        self.assertIn('off_origin', {s['reason'] for s in report['coverage']['skipped']})
        self.assertIn('robots_disallowed', {s['reason'] for s in report['coverage']['skipped']})

    def test_failed_or_non_html_pages_are_not_analyzed_as_successes(self):
        audit = load_audit()
        robots = response('User-agent: *\nDisallow:', content_type='text/plain')
        for result in (response('<title>Error</title>', 404), response('', 401),
                       response('pdf bytes', content_type='application/pdf'),
                       response('<title>partial</title>', 206)):
            with self.subTest(result=result), patch.object(audit, 'fetch', side_effect=[robots, result]), patch('time.sleep'):
                report = audit.audit_site('https://example.com/')
            self.assertEqual(report['pages'], [])
            self.assertEqual(report['coverage']['status'], 'partial')
            self.assertEqual(report['coverage']['errors'][0]['http_status'], result['status'])

    def test_wall_budget_includes_robots_and_prevents_more_requests(self):
        audit = load_audit()
        robots = response('User-agent: *\nDisallow:', content_type='text/plain')
        with patch.object(audit, 'fetch', return_value=robots) as fetch, \
             patch('time.monotonic', side_effect=[0] + [121] * 50), patch('time.sleep'):
            report = audit.audit_site('https://example.com/')
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(report['coverage']['status'], 'partial')
        self.assertEqual(report['coverage']['stop_reason'], 'wall_time_cap')
        self.assertEqual(report['coverage']['pending'], ['https://example.com/'])

    def test_rate_limit_stops_without_retrying_or_fetching_remaining_pages(self):
        audit = load_audit()
        results = [response('User-agent: *\nDisallow:', content_type='text/plain'),
                   response('<a href="/busy">x</a><a href="/remaining">x</a>'),
                   response('', 429, headers=[('Retry-After', '60')]), response('<title>Must not fetch</title>')]
        with patch.object(audit, 'fetch', side_effect=results) as fetch, patch('time.sleep'):
            report = audit.audit_site('https://example.com/')
        self.assertEqual(fetch.call_count, 3)
        self.assertEqual(report['coverage']['stop_reason'], 'server_backoff')
        self.assertEqual(report['coverage']['pending'], ['https://example.com/remaining'])

    def test_discovery_frontier_has_a_hard_cap(self):
        audit = load_audit()
        results = [response('User-agent: *\nDisallow:', content_type='text/plain'),
                   response(''.join(f'<a href="/p{i}">x</a>' for i in range(1500)))]
        with patch.object(audit, 'fetch', side_effect=results), patch('time.sleep'):
            report = audit.audit_site('https://example.com/', max_pages=1)
        self.assertEqual(len(report['coverage']['pending']), 1000)
        self.assertEqual(report['coverage']['stop_reason'], 'discovery_cap')
        self.assertEqual(report['coverage']['limits']['discovered_links'], 1000)

    def test_robots_disallowed_start_is_blocked_not_successfully_complete(self):
        audit = load_audit()
        with patch.object(audit, 'fetch', return_value=response('User-agent: *\nDisallow: /', content_type='text/plain')) as fetch:
            report = audit.audit_site('https://example.com/')
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(report['coverage']['status'], 'blocked')
        self.assertEqual(report['coverage']['stop_reason'], 'robots_disallowed')
        self.assertEqual(report['coverage']['requests_made'], 1)
        self.assertEqual(report['pages'], [])

    def test_discovery_truncation_is_partial_even_when_frontier_is_empty(self):
        audit = load_audit()
        results = [response('User-agent: *\nDisallow:', content_type='text/plain'),
                   response('<a href="https://other.example/">x</a>' * 1001)]
        with patch.object(audit, 'fetch', side_effect=results), patch('time.sleep'):
            report = audit.audit_site('https://example.com/')
        self.assertEqual(report['coverage']['status'], 'partial')
        self.assertEqual(report['coverage']['stop_reason'], 'discovery_cap')

    def test_unreadable_robots_still_reports_request_counts_and_limits(self):
        audit = load_audit()
        with patch.object(audit, 'fetch', side_effect=ValueError('request_timeout')):
            report = audit.audit_site('https://example.com/', max_pages=4)
        coverage = report['coverage']
        self.assertEqual(coverage.get('requests_made'), 1)
        self.assertEqual(coverage['stop_reason'], 'robots_unreadable')
        self.assertEqual(coverage['pending'], ['https://example.com/'])
        self.assertEqual(coverage['limits']['max_pages'], 4)


class OfflineTests(unittest.TestCase):
    def test_offline_file_api_never_uses_network_or_claims_live_checks(self):
        audit = load_audit()
        self.assertTrue(callable(getattr(audit, 'audit_file', None)), 'offline API missing')
        with patch.object(audit, 'fetch', side_effect=AssertionError('offline must not fetch')):
            report = audit.audit_file(ROOT / 'tests/fixtures/site-audit/example.html', 'https://example.com/service')
        self.assertEqual(report['mode'], 'offline')
        self.assertEqual(report['coverage']['requests_made'], 0)
        self.assertEqual(report['coverage']['robots']['state'], 'not_checked_offline')
        self.assertEqual(report['pages'][0]['title'], 'Example service | Example Company')
        self.assertNotIn('http_status', report['pages'][0])
        self.assertIn('HTTP headers', ' '.join(report['limitations']))


class CLITests(unittest.TestCase):
    def test_offline_cli_writes_json_only_to_a_new_output_file(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests/fixtures/site-audit') as directory:
            target = Path(directory) / 'report.json'
            cmd = [sys.executable, str(SCRIPT), '--html-file', str(ROOT / 'tests/fixtures/site-audit/example.html'),
                   '--base-url', 'https://example.com/service', '--output', str(target)]
            first = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue(target.exists(), 'CLI did not create its report')
            report = json.loads(target.read_text())
            self.assertEqual(report['coverage']['pages_analyzed'], 1)
            self.assertEqual(report['mode'], 'offline')
            original = target.read_bytes()
            second = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(target.read_bytes(), original)
            self.assertIn('exists', second.stderr.lower())

    def test_cli_validates_options_before_work_and_documents_exit_codes(self):
        fixture = str(ROOT / 'tests/fixtures/site-audit/example.html')
        for extra in (['--html-file', fixture, '--base-url', 'https://example.com/', '--max-pages', '51'],
                      ['--url', 'https://127.0.0.1/', '--base-url', 'https://example.com/']):
            with self.subTest(extra=extra), tempfile.TemporaryDirectory(dir=ROOT / 'tests/fixtures/site-audit') as directory:
                target = Path(directory) / 'report.json'
                done = subprocess.run([sys.executable, str(SCRIPT), *extra, '--output', str(target)], capture_output=True, text=True, timeout=20)
                self.assertEqual(done.returncode, 2, done.stderr)
                self.assertFalse(target.exists())
        help_run = subprocess.run([sys.executable, str(SCRIPT), '--help'], capture_output=True, text=True, timeout=10)
        self.assertEqual(help_run.returncode, 0)
        self.assertIn('Exit codes', help_run.stdout)
        self.assertIn('--max-pages', help_run.stdout)

    def test_live_cli_reports_ssrf_block_with_nonzero_status(self):
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests/fixtures/site-audit') as directory:
            target = Path(directory) / 'blocked.json'
            done = subprocess.run([sys.executable, str(SCRIPT), '--url', 'https://127.0.0.1/', '--output', str(target)],
                                  capture_output=True, text=True, timeout=10)
            self.assertEqual(done.returncode, 1, done.stderr)
            report = json.loads(target.read_text())
            self.assertEqual(report['coverage']['status'], 'blocked')
            self.assertIn('non_public_ip', report['coverage']['errors'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
