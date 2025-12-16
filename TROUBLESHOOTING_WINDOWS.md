# 🐛 XỬ LÝ LỖI - CỬA SỔ ĐÓNG NGAY

## ❓ Vấn Đề: Cửa sổ Command đóng ngay sau khi chạy .exe

### ✅ Các Module CÓ Chạy Tự Động

Tất cả các module đều có `while True` loop và sẽ chạy liên tục với interval:

- ✅ `hd_order.exe` - Chạy mỗi `delay_vao_lenh` giây (mặc định: 60s)
- ✅ `hd_order_123.exe` - Chạy mỗi `delay_vao_lenh_123` giây (mặc định: 300s)
- ✅ `hd_update_all.exe` - Chạy liên tục
- ✅ `hd_update_price.exe` - Chạy mỗi `delay_update_price` giây (mặc định: 120s)
- ✅ `hd_update_cho_va_khop.exe` - Chạy mỗi `delay_cho_va_khop` giây (mặc định: 600s)
- ✅ `hd_alert_possition_and_open_order.exe` - Chạy mỗi `delay_calert_possition_and_open_order` giây
- ✅ `hd_cancel_orders_schedule.exe` - Chạy theo lịch

---

## 🔍 Nguyên Nhân Cửa Sổ Đóng Ngay

### 1. ❌ Thiếu file `config.ini`

**Lỗi:** Script crash ngay khi import `cst.py` (đọc config.ini)

**Giải pháp:**
```cmd
cd C:\Users\Administrator\Downloads\source04062025\dist_windows
copy config.ini.example config.ini
notepad config.ini
```
Điền thông tin API vào `config.ini`

---

### 2. ❌ Lỗi Import Module

**Lỗi:** Thiếu dependencies hoặc lỗi import

**Giải pháp:** Kiểm tra log file:
- `hd_order.log`
- `error_pumb_dump.log`
- `hd_update_price.log`

---

### 3. ❌ Lỗi API Connection

**Lỗi:** Không kết nối được Binance API

**Giải pháp:**
- Kiểm tra internet
- Kiểm tra API key/secret trong `config.ini`
- Kiểm tra firewall

---

## 🔧 CÁCH KIỂM TRA

### Cách 1: Chạy từ Command Prompt (không double-click)

Mở Command Prompt và chạy:

```cmd
cd C:\path\to\dist_windows
hd_order.exe
```

Cửa sổ sẽ KHÔNG đóng ngay, bạn sẽ thấy lỗi nếu có.

---

### Cách 2: Thêm pause vào cuối script

Tạo file `run_with_pause.bat`:

```batch
@echo off
cd /d "%~dp0"
echo Starting hd_order.exe...
hd_order.exe
echo.
echo Process exited. Press any key to close...
pause >nul
```

---

### Cách 3: Kiểm tra log files

Sau khi chạy .exe, kiểm tra các file log:

```cmd
cd C:\path\to\dist_windows
type hd_order.log
type error_pumb_dump.log
```

---

## ✅ CÁCH CHẠY ĐÚNG

### Bước 1: Chuẩn bị

```cmd
cd C:\Users\Administrator\Downloads\source04062025\dist_windows

REM Copy config nếu chưa có
if not exist config.ini (
    copy config.ini.example config.ini
    echo Đã tạo config.ini, vui lòng chỉnh sửa!
    notepad config.ini
    pause
)
```

### Bước 2: Test từng module

```cmd
REM Test module đơn giản
check_status.exe

REM Test module chính
hd_order.exe
```

Nếu cửa sổ đóng ngay, xem log:
```cmd
type hd_order.log
```

### Bước 3: Chạy tất cả

```cmd
start_all_bots.bat
```

---

## 🛠️ SỬA LỖI THƯỜNG GẶP

### Lỗi: "config.ini not found"

```cmd
copy config.ini.example config.ini
notepad config.ini
```

### Lỗi: "Invalid API key"

- Kiểm tra `key_binance` và `secret_binance` trong `config.ini`
- Đảm bảo không có khoảng trắng thừa
- Kiểm tra API key có quyền Futures trading

### Lỗi: "Google Sheets API error"

- Đảm bảo có file `credentials.json`
- Chạy lần đầu sẽ mở browser để authenticate
- File `token.json` sẽ được tạo sau khi authenticate

### Lỗi: "Module not found"

Các module đã được đóng gói trong .exe, nếu vẫn lỗi:
- Rebuild lại với PyInstaller
- Kiểm tra hidden imports trong build script

---

## 📋 CHECKLIST

Trước khi chạy:

- [ ] File `config.ini` tồn tại
- [ ] Đã điền đầy đủ thông tin trong `config.ini`:
  - [ ] `key_binance` và `secret_binance`
  - [ ] `bot_token` và `chat_id`
  - [ ] `spreadsheet_id`
- [ ] File `credentials.json` tồn tại (cho Google Sheets)
- [ ] Internet connection OK
- [ ] Firewall không chặn

---

## 💡 TIPS

1. **Luôn chạy từ Command Prompt** để xem lỗi
2. **Kiểm tra log files** sau mỗi lần chạy
3. **Test từng module** trước khi chạy tất cả
4. **Dùng `start_all_bots.bat`** để chạy tất cả modules

---

## 🆘 VẪN KHÔNG CHẠY?

1. Chạy từ Command Prompt và copy toàn bộ output
2. Kiểm tra tất cả log files
3. Test với `check_status.exe` trước
4. Kiểm tra Windows Event Viewer

---

**Nếu cửa sổ vẫn đóng ngay, chạy từ Command Prompt để xem lỗi chi tiết!**
