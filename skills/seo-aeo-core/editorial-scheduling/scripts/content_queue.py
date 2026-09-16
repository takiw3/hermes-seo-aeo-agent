#!/usr/bin/env python3
"""Owner-controlled, local-first WordPress scheduling. Python 3.10+, stdlib only."""
import argparse
import base64
import getpass
import os
import sys
import hashlib
import http.client
import ipaddress
import socket
import ssl
import json
import re
import secrets
import sqlite3
import uuid
from contextlib import closing
from datetime import datetime, timezone

POSTS = '/wp-json/wp/v2/posts'


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field')
        result[key] = value
    return result


def load_bounded_json(source):
    raw = source.read(524289)
    if len(raw) > 524288:
        raise ValueError('Input exceeds 512 KiB limit')
    return json.loads(raw, object_pairs_hook=unique_object)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def validate_origin(origin):
    # Deliberately narrow: root installation, public DNS name, standard TLS port.
    if not isinstance(origin, str) or not re.fullmatch(r'https://[a-z0-9.-]{3,253}', origin):
        raise ValueError('Origin must be canonical https://public-hostname without port or path')
    labels = origin[8:].split('.')
    if (len(labels) < 2 or not re.fullmatch(r'[a-z]{2,63}', labels[-1])
            or labels[-1] in {'local', 'localhost', 'internal', 'lan', 'home', 'onion', 'test', 'invalid'}
            or any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in labels)):
        raise ValueError('Origin must use a public DNS hostname')
    return origin


def timestamp(value):
    if not isinstance(value, str) or not re.fullmatch(
            r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)', value):
        raise ValueError('Timestamp requires seconds and explicit timezone offset or Z')
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def future(value, now):
    result = timestamp(value)
    if (result - now).total_seconds() < 300:
        raise ValueError('Schedule must be at least five minutes in the future')
    return result


def validate_draft(data, now):
    if not isinstance(data, dict) or set(data) != {'origin', 'scheduled_at', 'title', 'slug', 'content', 'excerpt'}:
        raise ValueError('Draft requires exactly origin, scheduled_at, title, slug, content, excerpt')
    validate_origin(data['origin'])
    scheduled = future(data['scheduled_at'], now)
    for key, limit in [('title', 300), ('slug', 200), ('content', 200000), ('excerpt', 10000)]:
        value = data[key]
        if not isinstance(value, str) or len(value.encode('utf-8')) > limit:
            raise ValueError('Invalid or oversized ' + key)
        if (key != 'excerpt' and not value.strip()) or any(
                ord(c) == 127 or (ord(c) < 32 and (key in {'title', 'slug'} or c not in '\n\t\r')) for c in value):
            raise ValueError('Invalid text in ' + key)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', data['slug']):
        raise ValueError('Slug requires lowercase ASCII words separated by hyphens')
    return scheduled


def make_envelope(data, now):
    scheduled = validate_draft(data, now)
    envelope = {
        'endpoint': data['origin'] + POSTS,
        'scheduled_at': data['scheduled_at'],
        'payload': {key: data[key] for key in ('title', 'slug', 'content', 'excerpt')},
    }
    envelope['payload'].update(status='future', date_gmt=scheduled.strftime('%Y-%m-%dT%H:%M:%S'),
                               comment_status='closed', ping_status='closed', sticky=False, format='standard')
    return envelope


def validate_envelope(envelope, now):
    try:
        endpoint = envelope['endpoint']
        if not endpoint.endswith(POSTS):
            raise ValueError('Invalid endpoint')
        data = {key: envelope['payload'][key] for key in ('title', 'slug', 'content', 'excerpt')}
        data.update(origin=endpoint[:-len(POSTS)], scheduled_at=envelope['scheduled_at'])
        if canonical(make_envelope(data, now)) != canonical(envelope):
            raise ValueError('Invalid envelope')
    except (KeyError, TypeError, AttributeError):
        raise ValueError('Invalid stored envelope') from None


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect a numeric sockaddr once; TLS still checks the original hostname."""
    def __init__(self, host, address, context=None):
        super().__init__(host, port=443, timeout=20, context=context or ssl.create_default_context())
        self.address = address

    def connect(self):
        family, socktype, proto, _, sockaddr = self.address
        raw = socket.socket(family, socktype, proto)
        try:
            raw.settimeout(self.timeout)
            raw.connect(sockaddr)
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise


class WordPressTransport:
    def __init__(self, origin, username, password, resolver=None):
        self.host = validate_origin(origin)[8:]
        if (not isinstance(username, str) or not isinstance(password, str)
                or not 0 < len(username) <= 256 or not 0 < len(password) <= 512 or ':' in username
                or any(ord(c) < 32 or ord(c) == 127 for c in username + password)):
            raise ValueError('Invalid WordPress credentials; values suppressed')
        self.username, self.password = username, password
        addresses = (resolver or socket.getaddrinfo)(self.host, 443, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)
        if not addresses:
            raise ValueError('No public addresses for configured origin')
        for family, socktype, proto, _, sockaddr in addresses:
            ip = ipaddress.ip_address(sockaddr[0])
            if (not ip.is_global or ip.is_multicast or ip.is_reserved
                    or family not in {socket.AF_INET, socket.AF_INET6}
                    or socktype != socket.SOCK_STREAM or sockaddr[1] != 443
                    or (ip.version == 6 and (ip.ipv4_mapped or ip.sixtofour or ip.teredo
                        or ip in ipaddress.ip_network('64:ff9b::/96') or sockaddr[3] != 0))):
                raise ValueError('Origin DNS includes a non-public or unsupported address')
        self.address = addresses[0]

    def request(self, method, path, payload=None):
        if not ((method == 'POST' and path == POSTS and isinstance(payload, dict))
                or (method == 'GET' and re.fullmatch(re.escape(POSTS) + r'/[1-9][0-9]*\?context=edit', path)
                    and payload is None)):
            raise ValueError('Only new posts and exact edit-context read-back are supported')
        body = canonical(payload).encode('utf-8') if payload is not None else None
        if body is not None and len(body) > 524288:
            raise ValueError('Request exceeds 512 KiB limit')
        authorization = base64.b64encode((self.username + ':' + self.password).encode('utf-8')).decode('ascii')
        headers = {'Authorization': 'Basic ' + authorization, 'Content-Type': 'application/json',
                   'Accept': 'application/json', 'Accept-Encoding': 'identity'}
        connection = PinnedHTTPSConnection(self.host, self.address)
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            if response.status != (201 if method == 'POST' else 200):
                raise ValueError('Unexpected HTTP status; redirects and retries are forbidden')
            result = load_bounded_json(response)
            if not isinstance(result, dict):
                raise ValueError('Expected JSON object')
            return result
        finally:
            connection.close()


class Queue:
    def __init__(self, db, clock=None):
        self.db = os.fspath(db)
        if not self.db or self.db == ':memory:' or self.db.startswith('file:'):
            raise ValueError('Explicit persistent SQLite file path required')
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        with closing(self.connect()) as con, con:
            con.execute('''CREATE TABLE IF NOT EXISTS items (
                id TEXT PRIMARY KEY, envelope TEXT NOT NULL, state TEXT NOT NULL,
                approval_hash TEXT, approved_digest TEXT, expires TEXT,
                remote_id INTEGER, note TEXT)''')

    def connect(self):
        con = sqlite3.connect(self.db, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    def enqueue(self, data):
        envelope = make_envelope(data, self.clock())
        item_id = uuid.uuid4().hex
        with closing(self.connect()) as con, con:
            con.execute('INSERT INTO items(id,envelope,state) VALUES(?,?,?)',
                        (item_id, canonical(envelope), 'draft'))
        return item_id

    def approve(self, item_id, expected_digest, expires):
        expiry = timestamp(expires)
        if not 0 < (expiry - self.clock()).total_seconds() <= 86400:
            raise ValueError('Approval expiry must be within the next 24 hours')
        token = secrets.token_hex(32)
        with closing(self.connect()) as con, con:
            con.execute('BEGIN IMMEDIATE')
            row = self.row(con, item_id)
            envelope = json.loads(row['envelope'])
            validate_envelope(envelope, self.clock())
            if row['state'] != 'draft' or expected_digest != digest(envelope):
                raise ValueError('Approval requires a draft and its exact preview SHA256')
            con.execute('UPDATE items SET state=?,approval_hash=?,approved_digest=?,expires=? WHERE id=?',
                        ('approved', hashlib.sha256(token.encode()).hexdigest(), expected_digest,
                         expiry.isoformat(), item_id))
        return token

    def submit(self, item_id, token, *, env, transport=None):
        if env.get('SEO_AEO_WP_ENABLE_SCHEDULING') != '1':
            raise ValueError('Native scheduling is OFF; owner must explicitly enable it')
        origin = validate_origin(env.get('SEO_AEO_WP_ORIGIN'))
        if not env.get('SEO_AEO_WP_USERNAME') or not env.get('SEO_AEO_WP_APPLICATION_PASSWORD'):
            raise ValueError('Profile-specific WordPress credentials are required')
        with closing(self.connect()) as con, con:
            con.execute('BEGIN IMMEDIATE')
            row = self.row(con, item_id)
            envelope = json.loads(row['envelope'])
            if (row['state'] != 'approved' or not isinstance(token, str)
                    or not secrets.compare_digest(row['approval_hash'] or '', hashlib.sha256(token.encode()).hexdigest())
                    or row['approved_digest'] != digest(envelope)
                    or timestamp(row['expires']) <= self.clock()
                    or envelope['endpoint'] != origin + POSTS):
                raise ValueError('Exact, unexpired, unused approval and matching configured origin required')
            if transport is None:
                transport = WordPressTransport(origin, env['SEO_AEO_WP_USERNAME'], env['SEO_AEO_WP_APPLICATION_PASSWORD'])
            validate_envelope(envelope, self.clock())
            if timestamp(row['expires']) <= self.clock():
                raise ValueError('Approval expired during preflight')
            con.execute('UPDATE items SET state=?,approval_hash=NULL WHERE id=?', ('in_flight', item_id))
        try:
            created = transport.request('POST', POSTS, envelope['payload'])
            remote_id = created['id']
            if type(remote_id) is not int or not 0 < remote_id <= 9223372036854775807:
                raise ValueError('Invalid new post id')
            with closing(self.connect()) as con, con:
                con.execute('UPDATE items SET remote_id=? WHERE id=?', (remote_id, item_id))
            remote = transport.request('GET', POSTS + '/' + str(remote_id) + '?context=edit')
            if type(remote['id']) is not int or remote['id'] != remote_id or remote['type'] != 'post':
                raise ValueError('Unexpected read-back target')
            for field, value in envelope['payload'].items():
                actual = remote[field]['raw'] if field in {'title', 'content', 'excerpt'} else remote[field]
                if type(actual) is not type(value) or actual != value:
                    raise ValueError('Read-back differs from approved payload')
            with closing(self.connect()) as con, con:
                con.execute('UPDATE items SET state=? WHERE id=?', ('scheduled', item_id))
        except Exception:
            # Even a rejected HTTP request may have reached a plugin/proxy. Never retry a POST.
            with closing(self.connect()) as con, con:
                con.execute('UPDATE items SET state=?,note=? WHERE id=?',
                            ('uncertain', 'Inspect CMS manually. Do not retry or requeue automatically.', item_id))
            raise ValueError('Submission uncertain; inspect CMS manually; no retries permitted') from None
        return self.preview(item_id)

    def cancel(self, item_id):
        with closing(self.connect()) as con, con:
            con.execute('BEGIN IMMEDIATE')
            if self.row(con, item_id)['state'] not in {'draft', 'approved'}:
                raise ValueError('Only unsubmitted drafts or approvals may be cancelled locally')
            con.execute('UPDATE items SET state=?,approval_hash=NULL WHERE id=?', ('cancelled', item_id))

    def status(self):
        with closing(self.connect()) as con:
            rows = con.execute('SELECT id,state,envelope,remote_id,note,expires FROM items ORDER BY rowid').fetchall()
        return [{'id': r['id'], 'state': r['state'], 'scheduled_at': json.loads(r['envelope'])['scheduled_at'],
                 'remote_id': r['remote_id'], 'note': r['note'], 'approval_expires': r['expires']} for r in rows]

    def due(self):
        return [r for r in self.status() if r['state'] in {'draft', 'approved'}
                and timestamp(r['scheduled_at']) <= self.clock()]

    @staticmethod
    def row(con, item_id):
        row = con.execute('SELECT * FROM items WHERE id=?', (item_id,)).fetchone()
        if row is None:
            raise ValueError('Unknown item')
        return row

    def preview(self, item_id):
        with closing(self.connect()) as con:
            row = self.row(con, item_id)
        envelope = json.loads(row['envelope'])
        return {'id': row['id'], 'state': row['state'], 'envelope': envelope, 'sha256': digest(envelope)}


def main(argv=None):
    parser = argparse.ArgumentParser(description='Local content queue. No CMS calls except explicit submit. '
                                     'Agents must never self-approve; owner approval is out-of-band.')
    parser.add_argument('--db', required=True, help='Explicit SQLite path in a private owner directory')
    commands = parser.add_subparsers(dest='command', required=True)
    enqueue = commands.add_parser('enqueue', help='Store a draft locally; does not contact WordPress')
    enqueue.add_argument('--json', required=True, help='Draft JSON file')
    preview = commands.add_parser('preview', help='Show exact destination, time, payload, canonical envelope hash')
    preview.add_argument('id')
    approve = commands.add_parser('approve', help='OWNER ONLY: bind one use to exact reviewed preview')
    approve.add_argument('id')
    approve.add_argument('--sha256', required=True)
    approve.add_argument('--expires', required=True, help='Aware ISO timestamp, no more than 24 hours ahead')
    approve.add_argument('--owner-confirm', required=True, action='store_true', help='Owner confirms exact preview')
    submit = commands.add_parser('submit', help='Create one future post NOW, then verify; never run when due')
    submit.add_argument('id')
    submit.add_argument('--approval-stdin', action='store_true', help='Read one-use token from stdin instead of hidden prompt')
    cancel = commands.add_parser('cancel', help='Cancel local draft/approval only, never a CMS post')
    cancel.add_argument('id')
    commands.add_parser('status', help='List local states; does not poll the CMS')
    commands.add_parser('due', help='List missed local draft/approval deadlines; never publish them')
    args = parser.parse_args(argv)
    os.umask(0o077)
    try:
        queue = Queue(args.db)
        if args.command == 'enqueue':
            with open(args.json, 'rb') as source:
                data = load_bounded_json(source)
            result = queue.preview(queue.enqueue(data))
        elif args.command == 'preview':
            result = queue.preview(args.id)
        elif args.command == 'approve':
            result = {'id': args.id, 'approval_token': queue.approve(args.id, args.sha256, args.expires)}
        elif args.command == 'submit':
            token = sys.stdin.readline(66).strip() if args.approval_stdin else getpass.getpass('One-use owner approval token: ')
            result = queue.submit(args.id, token, env=os.environ)
        elif args.command == 'cancel':
            queue.cancel(args.id)
            result = queue.preview(args.id)
        else:
            result = queue.status() if args.command == 'status' else queue.due()
        print(canonical(result))
        return 0
    except (ValueError, OSError, sqlite3.Error, EOFError):
        # Never echo credentials, remote response bodies or exception strings.
        print('Operation rejected or uncertain. Check input, approval, configuration and local status. '
              'If in_flight/uncertain, inspect CMS manually; do not retry.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
