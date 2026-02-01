"""
RIMAN FASHION ERP - Django Settings
Production-ready configuration for luxury fashion business management system
"""

import os
from pathlib import Path
import environ
import dj_database_url

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: Secret key for production
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-change-this-in-production')

# Debug mode (False in production)
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Allowed hosts for Heroku and local development
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'corsheaders',
    'django_filters',
    
    # RIMAN FASHION Apps
    'core.apps.CoreConfig',
    'suppliers.apps.SuppliersConfig',
    'inventory.apps.InventoryConfig',
    'sales.apps.SalesConfig',
    'rentals.apps.RentalsConfig',
    'crm.apps.CrmConfig',
    'financeaccounting.apps.FinanceaccountingConfig',
    'accounting.apps.AccountingConfig',
    'reports.apps.ReportsConfig',
    'hr.apps.HrConfig',
    'documents.apps.DocumentsConfig',
    
    # NEW MODULES - Production & Operations
    'production.apps.ProductionConfig',
    'quality.apps.QualityConfig',
    'logistics.apps.LogisticsConfig',
    'support.apps.SupportConfig',
    
    # NEW MODULES - Finance & Analysis
    'finance.apps.FinanceConfig',
    'analytics.apps.AnalyticsConfig',
    
    # NEW MODULES - Organization & Marketing
    'locations.apps.LocationsConfig',
    'marketing.apps.MarketingConfig',
    'barcodes.apps.BarcodesConfig',
    'workflows.apps.WorkflowsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'riman_erp.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'riman_erp.wsgi.application'
 - Heroku compatible
if 'DATABASE_URL' in os.environ:
    DATABASES = {'default': dj_database_url.config()}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
        }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Document upload configuration
# Maximum upload size in bytes (default 5 MB)
DOCUMENT_UPLOAD_MAX_SIZE = env.int('DOCUMENT_UPLOAD_MAX_SIZE', default=5 * 1024 * 1024)
# Allowed file extensions for document uploads
DOCUMENT_ALLOWED_EXTENSIONS = env.list('DOCUMENT_ALLOWED_EXTENSIONS', default=['pdf','docx','doc','xlsx','xls','html','txt'])
# Enforce MIME/content-type sniffing to verify uploads match their extension
DOCUMENTS_ENFORCE_MIME = env.bool('DOCUMENTS_ENFORCE_MIME', default=True)
# Use S3 (or other remote storage) for document file storage when True. Configure DEFAULT_FILE_STORAGE accordingly.
DOCUMENTS_USE_S3 = env.bool('DOCUMENTS_USE_S3', default=False)
# Optional virus scanning (e.g., ClamAV). If True, the system will attempt to call an available scanner.
DOCUMENTS_VIRUS_SCAN = env.bool('DOCUMENTS_VIRUS_SCAN', default=False)
# Use asynchronous scanning (Celery) when True. Requires a configured Celery app and worker.
DOCUMENTS_USE_ASYNC_SCAN = env.bool('DOCUMENTS_USE_ASYNC_SCAN', default=False)
# Whether infected files should be automatically quarantined (disabled) on detection
DOCUMENTS_AUTO_QUARANTINE = env.bool('DOCUMENTS_AUTO_QUARANTINE', default=True)
# Celery configuration (optional guidance). If you use Celery, set the broker URL via CELERY_BROKER_URL env var.
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/0')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=['http://localhost:3000'])
CORS_ALLOW_CREDENTIALS = True

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'riman_erp.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# SECURITY Settings for Production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
