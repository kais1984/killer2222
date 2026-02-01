#!/bin/bash
# RIMAN FASHION ERP - Setup Script for Production

echo "🎭 RIMAN FASHION ERP - Production Setup"
echo "========================================"

# Check Python
echo "✓ Checking Python installation..."
python --version

# Create virtual environment
echo "✓ Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment
echo "✓ Setting up environment..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  .env file created - please configure database credentials"
fi

# Database setup
echo "✓ Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Static files
echo "✓ Collecting static files..."
python manage.py collectstatic --noinput

# Create directories
echo "✓ Creating required directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure .env with your database credentials"
echo "2. Create superuser: python manage.py createsuperuser"
echo "3. Run server: python manage.py runserver"
echo ""
echo "Access the system at: http://localhost:8000"
