@echo off
echo Activating DMac virtual environment...
call .\dmac_env\Scripts\activate

echo Running security tests...
python test_security.py

echo Press any key to exit...
pause > nul
