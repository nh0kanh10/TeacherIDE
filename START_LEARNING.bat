@echo off
chcp 65001 >nul
title AI Learning Coach Dashboard (Python 3.11)

echo ===================================================
echo 🚀 KHOI DONG AI LEARNING COACH...
echo ===================================================

:: Chuyen den thu muc chua script
cd /d "%~dp0Scripts"

:: Kiem tra Python 3.11
py -3.11 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [LOI] Khong tim thay Python 3.11!
    echo Vui long cai dat Python 3.11 hoac sua file nay.
    pause
    exit
)

echo ✅ Da tim thay Python 3.11

:: Kiem tra va cai dat dependencies cho Python 3.11
if not exist "..\.ai_coach\installed_py311.flag" (
    echo 📦 Dang cai dat thu vien cho Python 3.11...
    py -3.11 -m pip install -r requirements.txt
    echo. > "..\.ai_coach\installed_py311.flag"
)

:: Kiem tra xem da setup chua
if not exist "..\.ai_coach\config.json" (
    echo ⚙️  He thong chua duoc setup. Dang khoi tao...
    py -3.11 setup.py
    
    echo.
    echo ===================================================
    echo ⚠️  QUAN TRONG: 
    echo Ban can them Gemini API Key vao file: .ai_coach\.env
    echo Sau do chay lai file nay!
    echo ===================================================
    pause
    exit
)

:: Kiem tra user profile
if not exist "..\.ai_coach\user_profile.json" (
    echo 👤 Tao ho so nguoi dung lan dau...
    py -3.11 ai_coach.py --init-profile
)

echo.
echo 📊 Dang khoi dong Web Dashboard...
echo 💡 Nhan Ctrl+C de dung lai.
echo.

:: Chay Streamlit voi Python 3.11
py -3.11 -m streamlit run app.py
