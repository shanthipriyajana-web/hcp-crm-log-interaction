@echo off
echo Starting HCP CRM backend...
start "HCP CRM Backend" cmd /k "cd /d D:\hcp-crm\backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Starting HCP CRM frontend...
start "HCP CRM Frontend" cmd /k "cd /d D:\hcp-crm\frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo Opening browser...
start http://localhost:5173

exit