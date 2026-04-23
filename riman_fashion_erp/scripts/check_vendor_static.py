import requests
try:
    r = requests.get('http://127.0.0.1:8000/static/vendor/feather.min.js', timeout=5)
    print('status', r.status_code)
    print('length', len(r.text))
    print('has replace()', 'feather.replace' in r.text)
except Exception as e:
    print('error', e)
    raise
