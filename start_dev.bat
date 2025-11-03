@echo off
echo Starting Tree Matching Development Environment...
echo.

echo Starting Backend (Flask)...
start cmd /k "cd backend && python app.py"

timeout /t 3 /nobreak > nul

echo Starting Frontend (Vite)...
start cmd /k "cd frontend && npm run dev"

echo.
echo ================================
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo ================================
echo.
echo Press any key to close this window (servers will keep running)...
pause > nul

