@echo off
REM Launched by Windows Task Scheduler ("ADO Daily To-Do Email", daily 9:00 AM).
REM Fetches ADO items, summarizes with Claude, and emails the digest.
cd /d "%~dp0.."
if not exist logs mkdir logs
echo ===== %date% %time% ===== >> logs\scheduler.log
"C:\Users\PalakGupta\AppData\Local\Microsoft\WindowsApps\python.exe" src\run_daily.py >> logs\scheduler.log 2>&1
