import time
import sys
import requests

BASE = 'http://127.0.0.1:8000'
URLS = {
    '/': 'Dashboard',
    '/templates/': 'Template Library',
    '/templates/upload/': 'Upload',
    '/hr/': 'Human Resources',
    '/static/vendor/feather.min.js': 'feather.replace'
}

# wait for server to accept connections
for attempt in range(1, 11):
    try:
        r = requests.get(BASE + '/', timeout=2)
        if r.status_code == 200:
            print(f"Server is up (attempt {attempt})")
            break
    except Exception as e:
        print(f"Attempt {attempt}: server not ready ({e})")
        time.sleep(0.8)
else:
    print('Server did not start in time', file=sys.stderr)
    sys.exit(2)

ok = True
for path, marker in URLS.items():
    url = BASE + path
    try:
        r = requests.get(url, timeout=5)
        print(f"GET {path} -> {r.status_code} ({len(r.text)} bytes)")
        if r.status_code != 200:
            print(f"  ❌ status {r.status_code}")
            ok = False
            continue
        if marker and marker not in r.text:
            print(f"  ⚠️ marker '{marker}' not found in response")
            # not fatal
        else:
            print(f"  ✅ marker '{marker}' found")
    except Exception as e:
        print(f"GET {path} -> ERROR: {e}")
        ok = False

sys.exit(0 if ok else 1)
