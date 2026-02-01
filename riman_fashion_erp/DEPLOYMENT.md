# RIMAN FASHION ERP - Deployment Guide

## 🚀 Production Deployment

### Pre-Deployment Checklist

- [ ] Set DEBUG=False
- [ ] Generate new SECRET_KEY
- [ ] Configure PostgreSQL database
- [ ] Setup SSL/TLS certificates
- [ ] Configure email backend
- [ ] Setup static file storage
- [ ] Configure media file storage
- [ ] Setup monitoring and logging
- [ ] Configure backups
- [ ] Setup domain and DNS

### Security Configuration

```python
# settings.py for production
DEBUG = False
SECRET_KEY = 'your-very-secure-secret-key'  # Use os.environ.get('SECRET_KEY')

ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
]

# HTTPS Settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME'),
        'USER': os.environ.get('DATABASE_USER'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD'),
        'HOST': os.environ.get('DATABASE_HOST'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}
```

## Deployment Options

### 1. Heroku Deployment

**Procfile**:
```
web: gunicorn riman_erp.wsgi
release: python manage.py migrate
```

**Deploy**:
```bash
heroku create riman-fashion-erp
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
git push heroku main
heroku run python manage.py createsuperuser
```

### 2. AWS EC2 + RDS

**Instance Setup**:
```bash
# Launch EC2 instance (Ubuntu 20.04+)
sudo apt update
sudo apt install -y python3-pip python3-venv postgresql-client

# Clone repository
git clone your-repo-url
cd riman_fashion_erp

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn whitenoise

# Setup RDS PostgreSQL database
# Update .env with RDS connection string

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 riman_erp.wsgi:application
```

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/ubuntu/riman_fashion_erp/staticfiles/;
    }
    
    location /media/ {
        alias /home/ubuntu/riman_fashion_erp/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 3. DigitalOcean App Platform

**app.yaml**:
```yaml
name: riman-fashion-erp
services:
- name: web
  github:
    repo: your-username/riman_fashion_erp
    branch: main
  build_command: pip install -r requirements.txt && python manage.py collectstatic --noinput
  run_command: gunicorn riman_erp.wsgi:application
  http_port: 8000
  envs:
  - key: DEBUG
    value: "False"
  - key: SECRET_KEY
    scope: RUN_TIME
    value: ${SECRET_KEY}
  - key: DATABASE_URL
    scope: RUN_TIME
```

### 4. Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "riman_erp.wsgi:application"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: riman_fashion_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secure_password

  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      DEBUG: "False"
      DATABASE_URL: postgresql://postgres:secure_password@db:5432/riman_fashion_db
    depends_on:
      - db
    command: gunicorn riman_erp.wsgi:application --bind 0.0.0.0:8000

volumes:
  postgres_data:
```

**Deploy with Docker**:
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

## Post-Deployment

### 1. Database Backup Setup

```bash
# Daily automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgres"
DB_NAME="riman_fashion_db"
DB_USER="postgres"

mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql"

pg_dump -U $DB_USER $DB_NAME | gzip > "${BACKUP_FILE}.gz"

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

### 2. Monitoring & Logging

```python
# Configure Sentry for error tracking
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.1,
)

# Configure email alerts
ADMINS = [
    ('Admin Name', 'admin@yourdomain.com'),
]

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

### 3. SSL/TLS Setup with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Verify renewal
sudo certbot renew --dry-run
```

### 4. Database Maintenance

```bash
# Run regular maintenance
psql -U postgres -d riman_fashion_db -c "ANALYZE; VACUUM ANALYZE;"

# Check index usage
psql -U postgres -d riman_fashion_db -c "SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;"

# Monitor connections
psql -U postgres -d riman_fashion_db -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

## Monitoring

### Key Metrics to Monitor
- Response time (target: <500ms)
- Error rate (target: <0.1%)
- Database query time (target: <100ms)
- Server CPU usage (target: <70%)
- Memory usage (target: <80%)
- Disk usage (target: <85%)

### Alerts to Setup
- High error rate
- Database connection errors
- Low disk space
- High CPU/memory usage
- SSL certificate expiration
- Backup failures

## Scaling

### Horizontal Scaling
1. Deploy multiple application instances
2. Setup load balancer (Nginx/HAProxy)
3. Use database connection pooling (PgBouncer)
4. Cache layer with Redis

### Vertical Scaling
1. Increase server resources (CPU/RAM)
2. Optimize database queries
3. Implement caching strategies
4. Use CDN for static files

## Maintenance

### Weekly Tasks
- Monitor error logs
- Check backup integrity
- Review audit logs
- Monitor performance metrics

### Monthly Tasks
- Security updates
- Database optimization
- Certificate renewal verification
- Capacity planning review

### Quarterly Tasks
- Security audit
- Performance review
- Disaster recovery drill
- Database cleanup

---

**Deployment Complete! Your RIMAN FASHION ERP is live and ready.**
