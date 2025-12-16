@echo off
REM QBot v2.0 - Start All Bots Script (Windows)
REM Chạy tất cả 11 modules

echo ========================================
echo QBot v2.0 - Starting All Modules (Windows)
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found!
    echo Please install Python 3.9+
    pause
    exit /b 1
)

REM Check if in correct directory
if not exist config.ini (
    echo Error: config.ini not found!
    echo Are you in the source04062025 directory?
    pause
    exit /b 1
)

echo Starting modules...
echo.

REM Module 1: Order Handler (Critical)
echo Starting hd_order.py...
start "QBot - Order Handler" python hd_order.py
timeout /t 2 >nul

REM Module 2: Order 123 Handler (Critical)
echo Starting hd_order_123.py...
start "QBot - SL/TP Handler" python hd_order_123.py
timeout /t 2 >nul

REM Module 3: Market Data Updater
echo Starting hd_update_all.py...
start "QBot - Market Data" python hd_update_all.py
timeout /t 2 >nul

REM Module 4: Price Updater
echo Starting hd_update_price.py...
start "QBot - Price Updater" python hd_update_price.py
timeout /t 2 >nul

REM Module 5: Status Updater
echo Starting hd_update_cho_va_khop.py...
start "QBot - Status Updater" python hd_update_cho_va_khop.py
timeout /t 2 >nul

REM Module 6: Alert Handler
echo Starting hd_alert_possition_and_open_order.py...
start "QBot - Alerts" python hd_alert_possition_and_open_order.py
timeout /t 2 >nul

REM Module 7: Cancel Scheduler
echo Starting hd_cancel_orders_schedule.py...
start "QBot - Cancel Scheduler" python hd_cancel_orders_schedule.py
timeout /t 2 >nul

REM Module 8: 30 Prices Tracker (NEW in v2.0)
echo Starting hd_track_30_prices.py...
start "QBot - 30 Prices Tracker" python hd_track_30_prices.py
timeout /t 2 >nul

REM Module 9: Periodic Report (NEW in v2.0)
echo Starting hd_periodic_report.py...
start "QBot - Periodic Report" python hd_periodic_report.py

echo.
echo ========================================
echo All 11 modules started!
echo ========================================
echo.
echo Check running processes in Task Manager
echo Look for "python.exe" processes
echo.
echo To stop all: Close all CMD windows with "QBot" in title
echo Or use: taskkill /F /FI "WINDOWTITLE eq QBot*"
echo ========================================
pause

