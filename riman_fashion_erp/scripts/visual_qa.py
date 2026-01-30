import os
import sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riman_erp.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()
username = 'qauser'
password = 'password123'
user, created = User.objects.get_or_create(username=username, defaults={'email': 'qa@example.com', 'is_staff': True, 'is_superuser': True})
if created:
    user.set_password(password)
    user.save()
    print('Created QA user:', username)
else:
    print('QA user exists')

client = Client()
client.force_login(user)

paths = ['/', '/templates/', '/templates/upload/', '/hr/']
all_ok = True
for p in paths:
    resp = client.get(p, HTTP_HOST='127.0.0.1')
    print(f'GET {p} -> {resp.status_code}')
    text = ''
    try:
        text = resp.content.decode('utf-8')
    except Exception:
        pass
    has_df = 'data-feather' in text
    has_vendor = '/static/vendor/feather.min.js' in text or 'vendor/feather.min.js' in text
    print(f'  has data-feather: {has_df}  vendor script tag: {has_vendor}')
    if not (has_df and has_vendor):
        all_ok = False

# check vendor file served
rv = client.get('/static/vendor/feather.min.js', HTTP_HOST='127.0.0.1')
print('/static/vendor/feather.min.js ->', rv.status_code)
has_replace = False
try:
    text = rv.content.decode('utf-8')
    import re
    has_replace = bool(re.search(r'\bfeather\b', text)) or 'feather.replace' in text or 'exports.feather' in text or 'self.feather' in text
except Exception:
    # try streaming_content for FileResponse
    try:
        text = ''.join(chunk.decode('utf-8', errors='ignore') for chunk in rv.streaming_content)
        import re
        has_replace = bool(re.search(r'\bfeather\b', text)) or 'feather.replace' in text
    except Exception:
        pass
print('  feather present:', has_replace)
if rv.status_code != 200 or not has_replace:
    all_ok = False

print('\nOverall result:', 'OK' if all_ok else 'ISSUES FOUND')
if not all_ok:
    sys.exit(2)
else:
    sys.exit(0)
