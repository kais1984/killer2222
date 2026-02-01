# RIMAN FASHION ERP - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Environment Setup (1 minute)
```bash
cd riman_fashion_erp
python -m venv venv
source venv/Scripts/activate  # Windows
```

### Step 2: Install Dependencies (2 minutes)
```bash
pip install -r requirements.txt
```

### Step 3: Database Configuration (1 minute)
```bash
# Copy environment template
cp .env.example .env

# Edit .env and set:
# - DATABASE_NAME=riman_fashion_db
# - DATABASE_USER=postgres
# - DATABASE_PASSWORD=your_password
# - DATABASE_HOST=localhost
# - DATABASE_PORT=5432
```

### Step 4: Initialize Database (1 minute)
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### Step 5: Run Server (0.5 minute)
```bash
python manage.py runserver
```

## 📍 Access Points

- **Admin Dashboard**: http://localhost:8000/admin/
- **Main Dashboard**: http://localhost:8000/
- **API Root**: http://localhost:8000/api/

## 📝 Login Credentials

Use the superuser credentials you created during setup.

## ✅ Verification

After starting the server, verify:
1. Admin panel loads at `/admin/`
2. Dashboard loads at `/`
3. API responds at `/api/auth/profile/`

## 🔧 Common Commands

```bash
# Create admin user
python manage.py createsuperuser

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver

# Access Django shell
python manage.py shell

# Create cache table
python manage.py createcachetable
```

## 📊 Next Steps

1. Login to admin panel
2. Configure company settings
3. Add suppliers
4. Create product catalog
5. Add clients
6. Process first order
7. Generate reports

## 🆘 Troubleshooting

### Error: Cannot connect to database
```bash
# Create database first
psql -U postgres -c "CREATE DATABASE riman_fashion_db;"
```

### Error: Static files not found
```bash
python manage.py collectstatic --noinput
```

### Error: Port 8000 already in use
```bash
python manage.py runserver 8001  # Use different port
```

## 📞 Support

For detailed documentation, see README.md

---

**Ready to use! Start the server and begin managing RIMAN FASHION business operations.**
