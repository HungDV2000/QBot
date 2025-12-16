# HƯỚNG DẪN BUILD QBOT V2.0 CHO WINDOWS VPS 🏗️

**Ngày cập nhật:** 16/12/2025  
**Phiên bản:** 2.0  
**Mục tiêu:** Build 12 modules thành .exe files cho Windows VPS

---

## 📋 TỔNG QUAN

Script `build_windows.py` đã được cập nhật đầy đủ cho QBot v2.0 với:
- ✅ 12 modules (thêm 2 modules mới: hd_track_30_prices, hd_periodic_report)
- ✅ 6 helper modules mới trong hidden imports
- ✅ Start/stop scripts cho 11 modules
- ✅ README với tất cả v2.0 features
- ✅ Documentation files bao gồm trong distribution

---

## 🎯 CÁC MODULES SẼ ĐƯỢC BUILD

### Core Trading Modules (3 modules)
1. **hd_order.py** - Entry orders với system commands (XÓA CHỜ, XÓA VỊ THẾ, STOP)
2. **hd_order_123.py** - Auto SL/TP với cascade logic
3. **hd_alert_possition_and_open_order.py** - Monitor positions

### Data Collection Modules (5 modules)
4. **hd_update_all.py** - Market data 47+ columns
5. **hd_update_price.py** - Price updates
6. **hd_update_cho_va_khop.py** - Status updates
7. **hd_update_danhmuc.py** - Category updates
8. **hd_track_30_prices.py** - ⭐ NEW: Track 30 mức giá gần nhất

### Reporting & Monitoring (1 module)
9. **hd_periodic_report.py** - ⭐ NEW: Báo cáo định kỳ (1h hoặc PNL > 5%)

### Utilities (3 modules)
10. **hd_cancel_orders_schedule.py** - Cancel scheduler
11. **hd_isolated_crossed_converter.py** - Margin mode converter
12. **check_status.py** - Status checker

---

## 🔧 HIDDEN IMPORTS ĐÃ CẬP NHẬT

### Local Modules (Core)
- cst, utils, gg_sheet_factory, telegram_factory
- binance_utils, binance_order

### NEW Helper Modules (v2.0) ⭐
- **binance_order_helper** - Algo Order API handler
- **cascade_manager** - Multi-layer cascade logic
- **order_state_tracker** - State tracking to sheets
- **notification_manager** - 8 Telegram notifications
- **data_collector** - Market data collection
- **error_handler** - Centralized error handling

### External Libraries
- Google API (auth, sheets)
- Trading & Telegram (ccxt, telegram)
- Data processing (pandas, numpy, asyncio, aiohttp)

---

## 📦 DISTRIBUTION PACKAGE SẼ BAO GỒM

### Executables (.exe files)
- 12 module .exe files

### Configuration Files
- config.ini.example
- start_all_bots.bat (updated cho 11 modules)
- stop_all_bots.bat (updated)

### Documentation
- ✅ **README.txt** - Quick start guide
- ✅ **README.md** - Technical documentation (500+ lines)
- ✅ **HUONG_DAN_SU_DUNG.md** - User guide tiếng Việt (800+ lines)
- ✅ **PROJECT_COMPLETE.md** - Project summary
- ✅ **QUICK_CHECKLIST.md** - Development tracking

---

## 🚀 CÁCH BUILD TRÊN WINDOWS VPS

### Bước 1: Chuẩn bị Windows VPS

```powershell
# 1. Cài Python 3.9+
# Download từ: https://www.python.org/downloads/

# 2. Kiểm tra Python
python --version

# 3. Cài PyInstaller
python -m pip install pyinstaller

# 4. Cài dependencies
pip install -r requirements.txt
```

### Bước 2: Upload Source Code

```powershell
# Upload toàn bộ folder source04062025 lên VPS
# Có thể dùng:
# - WinSCP
# - FileZilla
# - RDP copy/paste
```

### Bước 3: Chạy Build Script

```powershell
# Mở PowerShell hoặc CMD trong thư mục source04062025
cd C:\path\to\source04062025

# Chạy build script
python build_windows.py
```

### Bước 4: Kiểm tra kết quả

```powershell
# Build sẽ tạo folder dist_windows/ với:
# - 12 file .exe
# - start_all_bots.bat
# - stop_all_bots.bat
# - README.txt
# - 4 documentation files
```

---

## ⏱️ THỜI GIAN BUILD DỰ KIẾN

- **Mỗi module:** 1-2 phút
- **Tổng 12 modules:** 15-25 phút
- **Tạo distribution:** 1-2 phút
- **TỔNG:** ~20-30 phút

---

## 📊 OUTPUT EXPECTED

```
dist_windows/
├── 📁 Core Trading (3 files)
│   ├── hd_order.exe (15-20 MB)
│   ├── hd_order_123.exe (15-20 MB)
│   └── hd_alert_possition_and_open_order.exe (15-20 MB)
│
├── 📁 Data Collection (5 files)
│   ├── hd_update_all.exe (15-20 MB)
│   ├── hd_update_price.exe (12-15 MB)
│   ├── hd_update_cho_va_khop.exe (12-15 MB)
│   ├── hd_update_danhmuc.exe (12-15 MB)
│   └── hd_track_30_prices.exe (15-20 MB) ⭐ NEW
│
├── 📁 Reporting (1 file)
│   └── hd_periodic_report.exe (15-20 MB) ⭐ NEW
│
├── 📁 Utilities (3 files)
│   ├── hd_cancel_orders_schedule.exe (12-15 MB)
│   ├── hd_isolated_crossed_converter.exe (12-15 MB)
│   └── check_status.exe (10-12 MB)
│
├── 📄 Scripts
│   ├── start_all_bots.bat
│   └── stop_all_bots.bat
│
└── 📚 Documentation
    ├── README.txt
    ├── README.md
    ├── HUONG_DAN_SU_DUNG.md
    ├── PROJECT_COMPLETE.md
    ├── QUICK_CHECKLIST.md
    └── config.ini.example

TỔNG DUNG LƯỢNG: ~180-250 MB
```

---

## 🛠️ XỬ LÝ LỖI KHI BUILD

### Lỗi 1: PyInstaller không tìm thấy module

**Triệu chứng:**
```
ModuleNotFoundError: No module named 'cascade_manager'
```

**Giải pháp:**
```powershell
# Kiểm tra file có tồn tại
dir cascade_manager.py

# Nếu thiếu → copy từ source gốc
```

### Lỗi 2: Hidden import không đầy đủ

**Triệu chứng:**
```
ImportError: cannot import name 'xxx'
```

**Giải pháp:**
- Đã được fix trong build_windows.py mới
- Tất cả 6 helper modules đã được thêm vào HIDDEN_IMPORTS

### Lỗi 3: Build failed do thiếu dependencies

**Triệu chứng:**
```
Error loading Python lib...
```

**Giải pháp:**
```powershell
# Cài lại dependencies
pip install -r requirements.txt --force-reinstall
```

### Lỗi 4: .exe file quá lớn

**Lưu ý:** 
- Mỗi .exe ~15-20 MB là bình thường
- PyInstaller đóng gói Python runtime và tất cả dependencies
- Không thể giảm size nhiều hơn

---

## ✅ KIỂM TRA SAU KHI BUILD

### 1. Kiểm tra số lượng files
```powershell
cd dist_windows
dir *.exe
# Phải có 12 files .exe
```

### 2. Test chạy 1 module
```powershell
# Copy config.ini.example thành config.ini
copy config.ini.example config.ini

# Edit config.ini với thông tin thật
notepad config.ini

# Test 1 module (không thật)
check_status.exe
```

### 3. Kiểm tra start script
```powershell
# Xem nội dung start_all_bots.bat
type start_all_bots.bat

# Phải thấy 11 modules (không có check_status)
```

---

## 🎯 SỬ DỤNG SAU KHI BUILD

### Setup lần đầu

1. **Copy config.ini.example → config.ini**
2. **Điền thông tin:**
   - Binance API Key + Secret
   - Telegram Bot Token + Chat ID
   - Google Sheets ID
3. **Tạo credentials.json** (Google Sheets API)
4. **Set test_mode = true** cho lần chạy đầu

### Chạy bot

```powershell
# Chạy tất cả
start_all_bots.bat

# Kiểm tra processes
tasklist | findstr hd_

# Xem logs
type hd_order.log
```

### Dừng bot

```powershell
# Dừng tất cả
stop_all_bots.bat

# Hoặc đóng các cửa sổ CMD
```

---

## 📝 NOTES QUAN TRỌNG

### 1. Không include credentials.json
- File này chứa thông tin nhạy cảm
- User phải tự tạo trên Google Cloud Console
- Không được commit hoặc share

### 2. test_mode flag
- Mặc định = true trong config.ini.example
- User phải đổi thành false khi muốn trade thật
- QUAN TRỌNG để tránh đặt lệnh nhầm

### 3. Logs
- Mỗi module tự tạo file .log riêng
- Logs không bị overwrite, sẽ append
- Nên định kỳ xóa logs cũ (> 7 ngày)

### 4. Windows Defender
- Có thể block .exe files
- Thêm exclusion cho folder dist_windows/
- Hoặc thêm từng .exe file vào whitelist

---

## 🔄 SO SÁNH V1.0 vs V2.0

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| **Modules** | 9-10 | 12 (+2 new) |
| **Helper Modules** | 3 | 9 (+6 new) |
| **Features** | Basic | 38 core items |
| **Documentation** | Minimal | 2000+ lines |
| **Build Script** | Basic | Comprehensive |
| **Distribution** | Exe only | Exe + 5 docs |

---

## 🎉 KẾT LUẬN

Build script `build_windows.py` đã sẵn sàng cho QBot v2.0:

✅ **12 modules** - Bao gồm 2 modules mới (v2.0)  
✅ **6 helper modules** - Hidden imports đầy đủ  
✅ **11-module start script** - Updated batch files  
✅ **Comprehensive README** - Với tất cả v2.0 features  
✅ **5 documentation files** - Trong distribution  
✅ **Production ready** - Sẵn sàng build trên Windows VPS  

---

## 📞 HỖ TRỢ

**Nếu gặp lỗi khi build:**
1. Kiểm tra Python version (>= 3.9)
2. Kiểm tra PyInstaller installed
3. Kiểm tra tất cả 12 modules tồn tại
4. Kiểm tra logs chi tiết trong output
5. Tham khảo phần "Xử lý lỗi" ở trên

**Sau khi build thành công:**
1. Đọc README.txt trong dist_windows/
2. Đọc HUONG_DAN_SU_DUNG.md
3. Setup config.ini
4. Test với test_mode = true
5. Deploy và monitor

---

**QBot v2.0 - Build Script Updated & Ready** 🚀

*Chúc bạn build thành công!* 🎉

