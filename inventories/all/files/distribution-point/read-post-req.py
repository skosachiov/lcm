#!/usr/bin/python3
#
# curl --user "user:pass" --request POST --data '{"key":"value"}' https://example.com/cgi-bin/secure/read-post-req.py
# curl --user "user:pass" --request POST --data-binary @file.json https://example.com/cgi-bin/secure/read-post-req.py
#
# curl --user "user:pass" --request POST --data '{"hostname":"name", "key":"value"}' https://example.com/cgi-bin/secure/read-post-req.py

import cgi
import cgitb
import sys
import os
import json
import html
import fcntl

cgitb.enable()

POST_DIR = '/var/www/html/files/post/'
MAX_PAYLOAD_SIZE = 16 * 1024 * 1024

print('Content-type: text/html\n')

try:
    content_length = int(os.environ.get('CONTENT_LENGTH', 0))
    if content_length > MAX_PAYLOAD_SIZE:
        print('ERROR: Payload exceeds maximum size limit')
        sys.exit(1)
    data = sys.stdin.buffer.read(content_length)
except (ValueError, TypeError):
    data = b''

try:
    json_data = json.loads(data.decode('UTF-8'))
except (json.JSONDecodeError, UnicodeDecodeError):
    print('ERROR: invalid JSON input')
    sys.exit(1)

if not isinstance(json_data, dict):
    print('ERROR: JSON payload must be an object')
    sys.exit(1)

ipaddr = html.escape(os.environ.get("REMOTE_ADDR", "unknown"))
raw_name = json_data.get('hostname', json_data.get('username', ipaddr))

safe_name = str(raw_name).replace('/', '_').replace('\\', '_').lower()
safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '-_.')
if not safe_name or safe_name in ('.', '..'):
    safe_name = ipaddr

fname = os.path.join(POST_DIR, safe_name + '.json')
lock_file = fname + '.lock'

try:
    with open(lock_file, 'w') as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)

        d = {}
        if os.path.exists(fname):
            try:
                with open(fname, 'r') as f:
                    d = json.load(f)
                if not isinstance(d, dict):
                    d = {}
            except (json.JSONDecodeError, OSError):
                d = {}

        for k, v in json_data.items():
            if k in d and isinstance(d[k], list) and isinstance(v, list):
                d[k] = list(set(d[k] + v))
            else:
                d[k] = v

        tmp = fname + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(d, f, indent=2)
        os.replace(tmp, fname)

    print('OK')

except Exception as e:
    print('ERROR: File transaction failed')
    sys.exit(1)


