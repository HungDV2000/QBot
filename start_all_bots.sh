#!/bin/bash

# QBot v2.0 - Start All Bots Script
# Chạy tất cả 11 modules trong background

echo "========================================"
echo "QBot v2.0 - Starting All Modules"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 not found. Please install Python 3.9+"
    exit 1
fi

# Check if in correct directory
if [ ! -f "config.ini" ]; then
    echo "❌ config.ini not found!"
    echo "Are you in the source04062025 directory?"
    exit 1
fi

echo "Starting modules..."

# Module 1: Order Handler (Lệnh 1) - CRITICAL
echo "▶ Starting hd_order.py (Entry Orders)..."
nohup python3 hd_order.py > logs/hd_order.log 2>&1 &
echo "  PID: $!"
sleep 1

# Module 2: Order 123 Handler (Lệnh 2&3) - CRITICAL
echo "▶ Starting hd_order_123.py (SL/TP Orders)..."
nohup python3 hd_order_123.py > logs/hd_order_123.log 2>&1 &
echo "  PID: $!"
sleep 1

# Module 3: Market Data Updater - IMPORTANT
echo "▶ Starting hd_update_all.py (Market Data)..."
nohup python3 hd_update_all.py > logs/hd_update_all.log 2>&1 &
echo "  PID: $!"
sleep 1

# Module 4: Price Updater - IMPORTANT
echo "▶ Starting hd_update_price.py (Prices)..."
nohup python3 hd_update_price.py > logs/hd_update_price.log 2>&1 &
echo "  PID: $!"
sleep 1

# Module 5: Status Updater - IMPORTANT
echo "▶ Starting hd_update_cho_va_khop.py (Status)..."
nohup python3 hd_update_cho_va_khop.py > logs/hd_update_cho_va_khop.log 2>&1 &
echo "  PID: $!"
sleep 1

# Module 6: Alert Handler
echo "▶ Starting hd_alert_possition_and_open_order.py (Alerts)..."
nohup python3 hd_alert_possition_and_open_order.py > logs/hd_alert.log 2>&1 &
echo "  PID: $!"
sleep 1

# Module 7: Cancel Schedule
echo "▶ Starting hd_cancel_orders_schedule.py (Cancel Scheduler)..."
nohup python3 hd_cancel_orders_schedule.py > logs/hd_cancel.log 2>&1 &
echo "  PID: $!"
sleep 1

# Module 8: 30 Prices Tracker - NEW in v2.0
echo "▶ Starting hd_track_30_prices.py (30 Price Points)..."
nohup python3 hd_track_30_prices.py > logs/hd_track_30_prices.log 2>&1 &
echo "  PID: $!"
sleep 1

# Module 9: Periodic Report - NEW in v2.0
echo "▶ Starting hd_periodic_report.py (Periodic Balance Report)..."
nohup python3 hd_periodic_report.py > logs/hd_periodic_report.log 2>&1 &
echo "  PID: $!"

echo ""
echo "========================================"
echo "✅ All 11 modules started!"
echo "========================================"
echo ""
echo "Check status:"
echo "  ps aux | grep python | grep hd_"
echo ""
echo "View logs:"
echo "  tail -f logs/hd_order.log"
echo ""
echo "Stop all:"
echo "  ./stop_all_bots.sh"
echo "========================================"

