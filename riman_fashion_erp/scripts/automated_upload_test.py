import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','riman_erp.settings')
django.setup()

# Deprecated helper script: automated_upload_test.py
# Replaced by unit tests in documents/tests/test_upload.py
# This file is intentionally left as a placeholder and should not be executed.