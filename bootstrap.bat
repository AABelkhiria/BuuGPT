@echo off
echo Creating virtual environment...
python -m venv venv

echo Installing requirements...
.\venv\Scripts\pip.exe install -r .\requirements.txt

echo Setup completed.
pause
