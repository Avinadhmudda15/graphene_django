# Run PowerShell as Administrator (right-click -> Run as administrator)
# Allows other devices on your Wi-Fi to reach Django on port 8000

New-NetFirewallRule -DisplayName "Django Sensore (port 8000)" `
    -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private,Domain `
    -ErrorAction SilentlyContinue

Write-Host "Done. If a rule already existed, you can ignore errors."
Write-Host "Start server with: python manage.py runserver 0.0.0.0:8000"
Write-Host "On this PC use: http://localhost:8000/"
Write-Host "On phone (same Wi-Fi): http://YOUR_PC_IP:8000/  (see ipconfig)"
