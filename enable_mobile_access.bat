@echo off
echo ========================================================
echo Allowing Utthan Dev Server (Port 5173) in Windows Firewall...
echo ========================================================
netsh advfirewall firewall add rule name="Utthan Dev Server 5173" dir=in action=allow protocol=TCP localport=5173
echo.
echo Done! Your phone can now connect to: http://10.163.9.41:5173/
echo ========================================================
pause
