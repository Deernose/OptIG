@echo off
cd /d %~dp0
pip install -U selenium
python.exe -m pip install --upgrade pip
cls
python "./OptIG.py"
pause
