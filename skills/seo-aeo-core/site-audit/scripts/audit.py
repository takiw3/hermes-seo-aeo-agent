#!/usr/bin/env python3
"""Bounded, dependency-free static SEO audit. Python 3.10+."""
from html.parser import HTMLParser
import json
import ipaddress
import re
import socket
import ssl
import http.client
import base64
from pathlib import Path
import subprocess
import sys
import time
import zlib
from collections import deque
from urllib.parse import urljoin, urlsplit, urlunsplit, unquote, quote

USER_AGENT = 'HermesSEOAudit/1.0'
MAX_BYTES = 1024 * 1024


def normalize_url(url, origin=None):
    """Conservative HTTPS-only policy; query URLs and ambiguous paths are not crawled."""
    if not isinstance(url, str) or len(url) > 2048 or any(ord(c) < 33 or ord(c) == 127 for c in url) or '\\' in url:
        raise ValueError('invalid_url')
    p = urlsplit(url)
    if p.scheme != 'https' or not p.hostname or p.username is not None or p.password is not None:
        raise ValueError('https_required_no_credentials')
    if p.port not in (None, 443) or p.query or '?' in url.split('#', 1)[0]:
        raise ValueError('query_or_nonstandard_port')
    host = p.hostname.encode('idna').decode('ascii').lower()
    if host.endswith('.') or '%' in host or not re.fullmatch(r'[a-z0-9.:-]+', host):
        raise ValueError('ambiguous_hostname')
    path = p.path or '/'
    if re.search(r'%(?![0-9a-fA-F]{2})', path) or re.search(r'%(?:2f|5c|25|3f|23|00|0a|0d)', path, re.I):
        raise ValueError('ambiguous_encoded_path')
    decoded = unquote(path, errors='strict')
    if any(part in ('.', '..') for part in decoded.split('/')) or any(ord(c) < 32 or ord(c) == 127 for c in decoded):
        raise ValueError('ambiguous_path')
    path = re.sub(r'%([0-9a-fA-F]{2})', lambda m: chr(int(m[1], 16)) if chr(int(m[1], 16)) in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~' else '%' + m[1].upper(), path)
    path = quote(path, safe="/%:@!$&'()*+,;=-._~")
    authority = '[' + host + ']' if ':' in host else host
    result = urlunsplit(('https', authority, path, '', ''))
    if origin is not None and 'https://' + authority != origin:
        raise ValueError('off_origin')
    return result


def url_origin(url):
    p = urlsplit(url)
    return p.scheme + '://' + p.netloc


def validate_addresses(addresses):
    """Reject the whole DNS answer if ANY address is non-public or transitional."""
    if not addresses:
        raise ValueError('empty_dns_answer')
    validated = []
    for text in addresses:
        ip = ipaddress.ip_address(text)
        if not ip.is_global or ip.is_multicast or ip.is_reserved or ip.is_unspecified or ip.is_loopback or ip.is_link_local:
            raise ValueError('non_public_ip')
        if ip.version == 4 and (ip in ipaddress.ip_network('192.0.0.0/24') or str(ip) == '168.63.129.16'):
            raise ValueError('special_use_ip')
        if ip.version == 6 and ip in ipaddress.ip_network('2001::/23'):
            raise ValueError('special_use_ip')
        if ip.version == 6 and (ip.ipv4_mapped is not None or ip.sixtofour is not None or ip.teredo is not None
                                or ip in ipaddress.ip_network('64:ff9b::/96')
                                or ip in ipaddress.ip_network('64:ff9b:1::/48')):
            raise ValueError('transitional_ipv6')
        validated.append(str(ip))
    return list(dict.fromkeys(validated))


class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host, address):
        super().__init__(host, port=443, timeout=10, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        # Never call create_connection(host): it performs a second DNS lookup.
        ip = ipaddress.ip_address(self.address)
        raw = socket.socket(socket.AF_INET6 if ip.version == 6 else socket.AF_INET, socket.SOCK_STREAM)
        raw.settimeout(self.timeout)
        try:
            raw.connect((self.address, self.port))
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise


def _request(url, max_bytes=MAX_BYTES):
    """One request; identity or bounded gzip, no redirects/proxies/cookies/auth."""
    url = normalize_url(url)
    p = urlsplit(url)
    addresses = validate_addresses([answer[4][0] for answer in socket.getaddrinfo(
        p.hostname, 443, type=socket.SOCK_STREAM)])
    connection = _PinnedHTTPS(p.hostname, addresses[0])
    try:
        connection.request('GET', p.path, headers={
            'User-Agent': USER_AGENT, 'Accept': 'text/html,text/plain;q=0.9',
            'Accept-Encoding': 'identity', 'Connection': 'close',
        })
        response = connection.getresponse()
        headers = response.getheaders()
        lengths = [value for name, value in headers if name.lower() == 'content-length']
        transfers = [value for name, value in headers if name.lower() == 'transfer-encoding']
        # Reject even identical duplicates, comma lists, and TE/CL combinations.
        # Only the single coding recognized by HTTPResponse is supported.
        if (len(lengths) > 1 or len(transfers) > 1 or (lengths and transfers)
                or (transfers and transfers[0].lower() != 'chunked')):
            raise ValueError('ambiguous_response_framing')
        if sum(name.lower() == 'content-encoding' for name, _ in headers) > 1:
            raise ValueError('ambiguous_content_encoding')
        encoding = 'identity'
        for name, value in headers:
            if name.lower() == 'content-length' and (not value.isdigit() or int(value) > max_bytes):
                raise ValueError('response_byte_cap')
            if name.lower() == 'content-encoding':
                encoding = value.strip().lower()
                if encoding not in ('', 'identity', 'gzip'):
                    raise ValueError('compressed_response_not_supported')
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError('response_byte_cap')
        # A bounded HTTPResponse.read() does not raise on Content-Length EOF.
        # Check the encoded body, not the length after gzip decompression.
        for name, value in headers:
            if name.lower() == 'content-length' and len(body) != int(value):
                raise ValueError('incomplete_response')
        if encoding == 'gzip':
            decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
            try:
                # Never use unbounded decompress/flush. The extra byte detects
                # expansion beyond the cap without materializing a gzip bomb.
                body = decoder.decompress(body, max_bytes + 1)
            except zlib.error as exc:
                raise ValueError('invalid_gzip_response') from exc
            if len(body) > max_bytes or decoder.unconsumed_tail:
                raise ValueError('response_byte_cap')
            if not decoder.eof or decoder.unused_data:
                # Require one complete, checksum-verified member and nothing else.
                raise ValueError('invalid_gzip_response')
        return dict(status=response.status, headers=headers, body=body)
    finally:
        connection.close()


def _worker():
    """Private subprocess boundary gives DNS/TLS/slow headers a hard wall timeout."""
    try:
        response = _request(**json.load(sys.stdin))
        response['body'] = base64.b64encode(response['body']).decode('ascii')
    except Exception as exc:
        response = dict(error=type(exc).__name__ + ': ' + str(exc)[:200])
    print(json.dumps(response))


def fetch(url, max_bytes=MAX_BYTES, timeout=15):
    """Fetch once with a killable wall-clock budget, including DNS resolution."""
    url = normalize_url(url)
    if not isinstance(max_bytes, int) or not 1 <= max_bytes <= MAX_BYTES or not 0 < timeout <= 15:
        raise ValueError('invalid_request_budget')
    try:
        completed = subprocess.run(
            [sys.executable, '-I', '-c', "import runpy,sys; runpy.run_path(sys.argv[1])['_worker']()", str(Path(__file__).resolve())],
            input=json.dumps(dict(url=url, max_bytes=max_bytes)), text=True,
            capture_output=True, timeout=timeout, check=True)
        result = json.loads(completed.stdout)
    except subprocess.TimeoutExpired as exc:
        raise ValueError('request_timeout') from exc
    except (subprocess.SubprocessError, OSError, ValueError) as exc:
        raise ValueError('request_worker_failed') from exc
    if 'error' in result:
        raise ValueError(result['error'])
    result['body'] = base64.b64decode(result['body'], validate=True)
    return result


def _wildcard_match(pattern, text):
    """Only '*' is special. Bounded greedy matching avoids regex backtracking DOS."""
    i = j = 0
    star = -1
    resume = 0
    while j < len(text):
        if i < len(pattern) and pattern[i] == '*':
            star, resume = i, j
            i += 1
        elif i < len(pattern) and pattern[i] == text[j]:
            i, j = i + 1, j + 1
        elif star >= 0:
            resume += 1
            i, j = star + 1, resume
        else:
            return False
    return all(c == '*' for c in pattern[i:])


class RobotsPolicy:
    """Conservative subset of robots rules; unsupported syntax will fail closed."""
    def __init__(self, text):
        lines = text.lstrip('\ufeff').splitlines()
        if len(lines) > 1000 or any(len(line) > 2048 for line in lines):
            raise ValueError('robots_complexity_cap')
        groups = []
        agents, rules, delays = [], [], []
        for line in lines:
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            if ':' not in line or any(ord(c) < 32 and c != '\t' for c in line):
                raise ValueError('ambiguous_robots')
            name, value = [part.strip() for part in line.split(':', 1)]
            name = name.lower()
            if name == 'user-agent':
                if not re.fullmatch(r'[a-zA-Z_-]+|\*', value):
                    raise ValueError('ambiguous_robots_agent')
                if rules or delays:
                    groups.append((agents, rules, delays))
                    agents, rules, delays = [], [], []
                agents.append(value.lower())
            elif name in ('allow', 'disallow'):
                if not agents or (value and not value.startswith('/')) or re.search(r'%(?![0-9a-fA-F]{2})', value):
                    raise ValueError('ambiguous_robots_rule')
                value = re.sub(r'%([0-9a-fA-F]{2})', lambda m: chr(int(m[1], 16)) if chr(int(m[1], 16)) in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~' else '%' + m[1].upper(), value)
                rules.append((quote(value, safe="/%:@!$&'()*+,;=?-._~"), name == 'allow'))
            elif name == 'crawl-delay':
                if not agents or not re.fullmatch(r'\d+(?:\.\d+)?', value) or not 0 <= float(value) <= 30:
                    raise ValueError('unsupported_robots_delay')
                delays.append(float(value))
            elif name == 'sitemap':
                if not value.startswith(('https://', 'http://')):
                    raise ValueError('ambiguous_sitemap')
                # Metadata only; sitemaps are not fetched by this bounded crawler.
            else:
                raise ValueError('unsupported_robots_directive: ' + name)
        groups.append((agents, rules, delays))
        if any(a and not r for a, r, d in groups):
            raise ValueError('robots_group_without_rules')
        product = USER_AGENT.split('/')[0].lower()
        specificity = lambda names: max([len(n) for n in names if n != '*' and n in product] or [0 if '*' in names else -1])
        best = max(specificity(a) for a, _, _ in groups)
        self.rules = []
        self.delay = 1.0
        for agents, rules, delays in groups:
            if specificity(agents) == best and best >= 0:
                self.rules.extend((p, allow) for p, allow in rules if p)
                self.delay = max([self.delay] + delays)

    def allowed(self, url):
        path = urlsplit(url).path or '/'
        # RFC 9309 figure 6: target metacharacters are literal octets, not
        # rule operators. Keep their escaped spelling for literal rule matches.
        path = path.replace('*', '%2A').replace('$', '%24')
        matches = []
        for pattern, allow in self.rules:
            end = pattern.endswith('$')
            raw = pattern[:-1] if end else pattern
            # Only a terminal rule '$' is an anchor; interior '$' stays literal.
            match_pattern = raw.replace('$', '%24')
            if _wildcard_match(match_pattern if end else match_pattern + '*', path):
                matches.append((len(raw.replace('*', '').encode('utf-8')), allow))
        return max(matches)[1] if matches else True


def header_values(response, name):
    return [v for k, v in response['headers'] if k.lower() == name.lower()]


def audit_site(url, max_pages=10):
    """Audit a bounded exact HTTPS origin; robots unreadable means no crawl."""
    if type(max_pages) is not int or not 1 <= max_pages <= 50:
        raise ValueError('max_pages_must_be_1_to_50')
    url = normalize_url(url)
    origin = url_origin(url)
    robots_url = origin + '/robots.txt'
    limits = dict(max_pages=max_pages, max_response_bytes=MAX_BYTES, discovered_links=1000,
                  wall_seconds=120, request_seconds=15, robots_bytes=512 * 1024)
    deadline = time.monotonic() + 120
    robots = dict(url=robots_url, state='unreadable')
    try:
        result = fetch(robots_url, max_bytes=512 * 1024)
        robots['http_status'] = result['status']
        types = header_values(result, 'content-type')
        if result['status'] != 200 or len(types) != 1 or types[0].split(';')[0].strip().lower() != 'text/plain':
            raise ValueError('robots_requires_200_text_plain_no_redirect')
        policy = RobotsPolicy(result['body'].decode('utf-8-sig', errors='strict'))
    except (ValueError, OSError) as exc:
        return build_report([], mode='live', status='blocked', robots=robots,
                            errors=[dict(url=robots_url, reason=str(exc))], skipped=[],
                            requests_made=1, pending=[url], redirects=[], limits=limits, stop_reason='robots_unreadable')
    robots['state'] = 'parsed'
    robots['delay_seconds'] = policy.delay
    pages, errors, skipped, redirects = [], [], [], []
    queue, seen = deque([url]), {url}
    requests_made = 1
    last_finished = time.monotonic()
    stop_reason = None
    discovered_links = 0
    while queue and requests_made <= max_pages:
        if time.monotonic() + policy.delay >= deadline:
            stop_reason = 'wall_time_cap'
            break
        current = queue.popleft()
        if not policy.allowed(current):
            skipped.append(dict(url=current, reason='robots_disallowed'))
            continue
        time.sleep(max(0, policy.delay - (time.monotonic() - last_finished)))
        requests_made += 1
        try:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                queue.appendleft(current)
                requests_made -= 1
                stop_reason = 'wall_time_cap'
                break
            result = fetch(current, timeout=min(15, remaining))
            if result['status'] in (301, 302, 303, 307, 308):
                locations = header_values(result, 'location')
                if len(locations) != 1 or not locations[0]:
                    raise ValueError('ambiguous_redirect')
                target = urljoin(current, locations[0])
                redirects.append(dict(url=current, target=target, http_status=result['status']))
                try:
                    target = normalize_url(target, origin=origin)
                except ValueError as exc:
                    skipped.append(dict(url=target, reason=str(exc)))
                else:
                    if target not in seen:
                        seen.add(target)
                        queue.append(target)
                continue
            if result['status'] in (429, 503):
                errors.append(dict(url=current, http_status=result['status'], reason='server_backoff',
                                   retry_after=header_values(result, 'retry-after')))
                stop_reason = 'server_backoff'
                break
            types = header_values(result, 'content-type')
            if result['status'] != 200 or len(types) != 1 or types[0].split(';')[0].strip().lower() != 'text/html':
                errors.append(dict(url=current, http_status=result['status'], reason='requires_200_html'))
                continue
            page = extract_html(result['body'].decode('utf-8', errors='replace'), current,
                                x_robots=header_values(result, 'x-robots-tag'))
            page['http_status'] = result['status']
            pages.append(page)
            for link in page['links']:
                if discovered_links >= 1000:
                    stop_reason = 'discovery_cap'
                    break
                discovered_links += 1
                try:
                    target = normalize_url(link, origin=origin)
                except ValueError as exc:
                    skipped.append(dict(url=link, reason=str(exc)))
                    continue
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
            if stop_reason == 'discovery_cap':
                break
        except (ValueError, OSError) as exc:
            errors.append(dict(url=current, reason=str(exc)))
        finally:
            last_finished = time.monotonic()
    status = 'partial' if queue or errors or stop_reason else 'complete'
    if requests_made == 1 and skipped and not queue:
        status, stop_reason = 'blocked', 'robots_disallowed'
    return build_report(pages, mode='live', status=status, robots=robots,
                        requests_made=requests_made, errors=errors, skipped=skipped, pending=list(queue), redirects=redirects,
                        stop_reason=stop_reason or ('page_cap' if queue else 'queue_exhausted'),
                        limits=limits)


class _HTMLSignals(HTMLParser):
    def __init__(self, url, x_robots):
        super().__init__(convert_charrefs=True)
        self.url = url
        self.elements = 0
        self.data = dict(url=url, title='', titles=[], meta_descriptions=[],
                         headings=[], canonicals=[], meta_robots=[], x_robots=list(x_robots),
                         links=[], images=dict(total=0, missing_alt=0, empty_alt=0),
                         json_ld=[], hreflang=[], lang='', script_count=0)
        self.capture = None
        self.text = []
        self.json_script = False

    def handle_starttag(self, tag, attrs):
        self.elements += 1
        if self.elements > 10000:
            raise ValueError('html_element_cap')
        a = dict(attrs)
        if tag == 'base' and a.get('href') and not getattr(self, 'base_seen', False):
            self.url = urljoin(self.url, a['href'])
            self.base_seen = True
        if tag == 'html':
            self.data['lang'] = a.get('lang') or ''
        if tag == 'title' or tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.capture, self.text = tag, []
        if tag == 'meta':
            name = (a.get('name') or '').lower()
            if name == 'description':
                self.data['meta_descriptions'].append(a.get('content') or '')
            if name in ('robots', 'googlebot', 'bingbot'):
                self.data['meta_robots'].append(dict(agent=name, content=a.get('content') or ''))
        if tag == 'link':
            rel = (a.get('rel') or '').lower().split()
            target = urljoin(self.url, a.get('href') or '')
            if 'canonical' in rel:
                self.data['canonicals'].append(target)
            if 'alternate' in rel and a.get('hreflang'):
                self.data['hreflang'].append(dict(lang=a['hreflang'], url=target))
        if tag == 'a' and a.get('href'):
            self.data['links'].append(urljoin(self.url, a['href']))
        if tag == 'img':
            images = self.data['images']
            images['total'] += 1
            images['missing_alt'] += 'alt' not in a
            images['empty_alt'] += 'alt' in a and not (a['alt'] or '').strip()
        if tag == 'script':
            self.data['script_count'] += 1
            self.json_script = (a.get('type') or '').lower() == 'application/ld+json'
            if self.json_script:
                self.text = []

    def handle_data(self, text):
        if self.capture or self.json_script:
            self.text.append(text)

    def handle_endtag(self, tag):
        if tag == 'script' and self.json_script:
            raw = ''.join(self.text)
            try:
                json.loads(raw, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
                result = dict(valid_json=True)
            except (ValueError, RecursionError) as exc:
                result = dict(valid_json=False, error=str(exc)[:200])
            self.data['json_ld'].append(result)
            self.json_script, self.text = False, []
        if tag == self.capture:
            text = ' '.join(''.join(self.text).split())
            if tag == 'title':
                self.data['titles'].append(text)
                self.data['title'] = self.data['titles'][0]
            else:
                self.data['headings'].append(dict(level=int(tag[1]), text=text))
            self.capture, self.text = None, []


def extract_html(html, url, x_robots=()):
    """Extract source-HTML signals. JSON-LD validity means JSON syntax only."""
    if len(html.encode('utf-8')) > MAX_BYTES:
        raise ValueError('html_byte_cap')
    parser = _HTMLSignals(url, x_robots)
    parser.feed(html)
    parser.close()
    return parser.data


def audit_file(html_file, base_url):
    """Audit one local UTF-8 fixture without DNS, HTTP, or link following."""
    url = normalize_url(base_url)
    with Path(html_file).open('rb') as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('html_byte_cap')
    page = extract_html(raw.decode('utf-8-sig', errors='strict'), url)
    report = build_report([page], mode='offline', status='complete', requests_made=0,
                          robots=dict(state='not_checked_offline'), errors=[], skipped=[], pending=[],
                          stop_reason='offline_single_file', limits=dict(max_response_bytes=MAX_BYTES))
    report['limitations'].append('Offline mode does not check HTTP headers, HTTP status, DNS, redirects, or robots.txt.')
    return report


LIMITATIONS = [
    'Static source HTML only; no JavaScript execution or rendered DOM inspection.',
    'This audit cannot establish Google indexing, rankings, AEO ranking, or Core Web Vitals (CWV).',
    'JSON-LD checks JSON syntax only, not schema correctness or rich-result eligibility.',
    'Findings are observations or heuristics, not a numerical SEO score or proof of indexability.',
    'Coverage is bounded; duplicates refer only to successfully visited pages.',
]
MANUAL_CHECKS = [
    'Compare source HTML with a JavaScript-rendered browser, including blocked JS resources.',
    'Validate schema using Schema.org Validator and Google Rich Results Test externally.',
    'Check Google Search Console URL Inspection for indexing and canonical selection.',
    'Measure real-user CWV and accessibility separately; review empty alt text in context.',
]


def build_report(pages, mode, **coverage):
    """Build evidence-bearing, non-scored findings over the supplied pages."""
    findings = []

    def add(page, code, evidence, recommendation, basis='heuristic', severity='warning'):
        findings.append(dict(url=page['url'], code=code, severity=severity,
                             basis=basis, evidence=evidence, recommendation=recommendation))

    for page in pages:
        for key, code, recommendation in (
            ('title', 'missing_title', 'Add a descriptive, page-specific title.'),
            ('meta_descriptions', 'missing_description', 'Consider a unique description summarizing this page.'),
            ('canonicals', 'missing_canonical', 'Review whether an explicit canonical is appropriate.'),
            ('lang', 'missing_lang', 'Declare the content language on the html element.'),
        ):
            if not page[key]:
                add(page, code, f'No {key} found in source HTML.', recommendation)
        if not any(h['level'] == 1 for h in page['headings']):
            add(page, 'missing_h1', 'No h1 element found in source HTML.', 'Review the main visible heading.')
        if page['images']['missing_alt']:
            add(page, 'missing_alt', dict(page['images']), 'Supply meaningful alt text, or empty alt for decorative images.')
        if any(not block['valid_json'] for block in page['json_ld']):
            add(page, 'invalid_json_ld', page['json_ld'], 'Fix JSON syntax, then validate schema externally.', 'observed', 'error')
        directives = [r['content'] for r in page['meta_robots']] + page['x_robots']
        if any(re.search(r'(?:^|[\s,:])(?:noindex|none)(?:$|[\s,])', value.lower()) for value in directives):
            add(page, 'noindex_directive', directives, 'Review directive intent and agent scope; confirm indexing separately.', 'observed')
    for key, code in (('title', 'duplicate_title'), ('meta_descriptions', 'duplicate_description')):
        values = {}
        for page in pages:
            value = page[key]
            if isinstance(value, list):
                value = value[0] if value else ''
            value = ' '.join(value.casefold().split())
            if value:
                values.setdefault(value, []).append(page)
        for value, matches in values.items():
            if len(matches) > 1:
                for page in matches:
                    add(page, code, dict(normalized_value=value, urls=[p['url'] for p in matches]),
                        'Review whether these visited pages need distinct metadata or consolidation.')
    return dict(format_version=1, mode=mode, pages=pages, findings=findings,
                coverage=dict(pages_analyzed=len(pages), **coverage),
                limitations=list(LIMITATIONS), manual_checks=list(MANUAL_CHECKS))


def main(argv=None):
    """CLI entry point. Existing output files are never overwritten."""
    import argparse
    parser = argparse.ArgumentParser(
        description='Bounded static SEO audit; no numerical score or indexing guarantee.',
        epilog='Exit codes: 0 complete bounded audit, 1 partial/blocked report, 2 input/output error. '
               'Limits: HTTPS port 443 only, 1 MiB/page, 512 KiB robots, 15s/request including DNS, '
               '120s crawl network budget, 1s minimum pacing (honors supported crawl-delay). '
               'Robots requires unambiguous UTF-8 text/plain HTTP 200; redirects/404 also fail closed. '
               'No JS, cookies, auth, proxies, query URLs, or sitemap crawling. '
               'Output is untrusted website-derived data, not instructions.')
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--url', help='Live HTTPS URL, standard port, exact-origin crawl; no queries or credentials.')
    source.add_argument('--html-file', type=Path, help='One local UTF-8 HTML fixture. No network access.')
    parser.add_argument('--base-url', help='Required with --html-file to resolve relative links.')
    parser.add_argument('--max-pages', type=int, default=10, help='Attempted page URLs including redirects/errors: default 10, hard cap 50.')
    parser.add_argument('--output', type=Path, required=True, help='New JSON file; refuses existing files.')
    args = parser.parse_args(argv)
    if not 1 <= args.max_pages <= 50:
        parser.error('--max-pages must be between 1 and 50')
    if bool(args.html_file) != bool(args.base_url):
        parser.error('--base-url is required only with --html-file')
    try:
        if args.output.exists() or args.output.is_symlink():
            raise ValueError('output already exists; choose a new file')
        report = audit_file(args.html_file, args.base_url) if args.html_file else audit_site(args.url, args.max_pages)
        with args.output.open('x', encoding='utf-8') as target:
            json.dump(report, target, ensure_ascii=False, indent=2)
            target.write('\n')
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(dict(output=str(args.output), status=report['coverage']['status'], pages_analyzed=len(report['pages']))))
    return 0 if report['coverage']['status'] == 'complete' else 1


if __name__ == '__main__':
    sys.exit(main())
