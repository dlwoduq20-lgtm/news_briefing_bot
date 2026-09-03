@echo off
set PYTHON_EXE="C:\Users\dlwod\AppData\Local\Programs\Python\Python310\python.exe"
cd /d "%~dp0"
%PYTHON_EXE% main.py >> run_log.txt 2>&1
