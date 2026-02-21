@echo off
echo ========================================
echo Lifestyle Store - Inicializacao Completa
echo ========================================
echo.

echo [1/3] Instalando dependencias do Backend...
cd backend
if not exist .venv (
    echo Criando ambiente virtual...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
echo Backend pronto!
echo.

echo [2/3] Instalando dependencias do Frontend...
cd ..\frontend
call npm install
echo Frontend pronto!
echo.

echo [3/3] Projeto pronto para uso!
echo.
echo ========================================
echo Para iniciar o projeto:
echo ========================================
echo.
echo Terminal 1 - Backend:
echo   cd backend
echo   .venv\Scripts\activate
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Terminal 3 - Testes:
echo   cd scripts
echo   powershell -File smoke-tests.ps1
echo.
echo ========================================
echo URLs:
echo ========================================
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs (dev only)
echo.
pause
