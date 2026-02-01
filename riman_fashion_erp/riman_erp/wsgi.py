"""
WSGI config for RIMAN FASHION ERP project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riman_erp.settings')

application = get_wsgi_application()
