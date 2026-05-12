@echo off
setlocal EnableExtensions
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
set "BACKEND=%ROOT%\backend"
set "FRONTEND=%ROOT%\frontend"

if not exist "%BACKEND%\manage.py" (
  echo [ERROR] Not found: %BACKEND%\manage.py
  exit /b 1
)
if not exist "%FRONTEND%\package.json" (
  echo [ERROR] Not found: %FRONTEND%\package.json
  exit /b 1
)

echo === Backend: venv, dependencies, migrate, seed_data ===
cd /d "%BACKEND%"
if not exist ".venv" (
  echo Creating .venv...
  python -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip -q
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py seed_data

echo === Frontend: npm install, production build ===
cd /d "%FRONTEND%"
call npm install
call npm run build

echo.
echo === Готово ===
echo Демо-пользователи (пароли см. seed_data): chef_anna, foodie_ivan, cook_maria
echo.
echo Запуск API:    cd backend ^&^& .venv\Scripts\activate ^&^& python manage.py runserver 127.0.0.1:8000
echo Сборка UI:     cd frontend ^&^& npm run preview -- --host 127.0.0.1 --port 4173
echo Разработка UI: cd frontend ^&^& npm run dev
echo.
if "%RUN_SERVERS%"=="1" (
  start "Django API" cmd /k "cd /d \"%BACKEND%\" && call .venv\Scripts\activate.bat && python manage.py runserver 127.0.0.1:8000"
  start "Vite preview" cmd /k "cd /d \"%FRONTEND%\" && npm run preview -- --host 127.0.0.1 --port 4173"
)

endlocal
