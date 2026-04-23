Set-Location "c:\Users\KAIS\Documents\RIAMAN_FASHION_ERP\riman_fashion_erp"
Write-Host "Starting RIMAN Fashion ERP Server..."
Write-Host "Current directory: $(Get-Location)"
python manage.py runserver 0.0.0.0:8000
