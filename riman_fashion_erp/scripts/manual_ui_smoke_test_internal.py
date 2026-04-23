import os
import sys
import django

# configure Django settings
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riman_erp.settings')
django.setup()

from django.test import Client

client = Client()
paths = {
    '/': 'Dashboard',
    '/templates/': 'Template Library',
    '/templates/upload/': 'Upload',
    '/hr/': 'Human Resources',
    '/static/vendor/feather.min.js': 'feather.replace'
}

ok = True
for path, marker in paths.items():
    # use explicit HTTP_HOST to avoid DisallowedHost when running via test client
    # follow redirects to reach login page if present
    resp = client.get(path, HTTP_HOST='127.0.0.1', follow=True)
    # handle FileResponse (streaming) vs regular responses
    body_len = None
    text = ''
    try:
        body = resp.content
        body_len = len(body)
        try:
            text = body.decode('utf-8')
        except Exception:
            text = ''
    except Exception:
        # streaming response (FileResponse). try reading small piece from streaming_content
        try:
            chunks = []
            it = resp.streaming_content
            for i, c in enumerate(it):
                chunks.append(c)
                if i >= 4:
                    break
            sample = b"".join(chunks)
            body_len = 'streaming'
            try:
                text = sample.decode('utf-8', errors='ignore')
            except Exception:
                text = ''
        except Exception:
            body_len = 'unknown'
            text = ''

    print(f"GET {path} -> {resp.status_code} (final), redirects: {len(resp.redirect_chain)} => {body_len} bytes)")
    if resp.status_code != 200:
        print("  ❌ status", resp.status_code)
        ok = False
    else:
        if marker and marker not in text:
            print(f"  ⚠️ marker '{marker}' not found (content may be login page)")
        else:
            print(f"  ✅ marker '{marker}' found")

sys.exit(0 if ok else 1)
