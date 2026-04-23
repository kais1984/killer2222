@echo off
REM RIMAN FASHION ERP - Setup Script for Windows

echo.
echo 🎭 RIMAN FASHION ERP - Production Setup
echo ========================================
echo.

REM Check Python
echo Checking Python installation...
python --version

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Setup environment
echo Setting up environment...
if not exist .env (
    copy .env.example .env
    echo ⚠️  .env file created - please configure database credentials
)

REM Database setup
echo Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Static files
echo Collecting static files...
python manage.py collectstatic --noinput

REM Create directories
echo Creating required directories...
if not exist logs mkdir logs
if not exist media mkdir media
if not exist staticfiles mkdir staticfiles

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Configure .env with your database credentials
echo 2. Create superuser: python manage.py createsuperuser
echo 3. Run server: python manage.py runserver
echo.
echo Access the system at: http://localhost:8000
echo.
pause
