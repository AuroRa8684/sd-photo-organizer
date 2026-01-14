@echo off
cd /d C:\Documents\作业\软件设计\sd-photo-organizer\backend
call .\.venv\Scripts\activate.bat
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
