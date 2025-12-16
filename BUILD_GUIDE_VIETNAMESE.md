# 🚀 HƯỚNG DẪN BUILD CHI TIẾT

## 📋 Chuẩn Bị

Bạn đang ở máy macOS và muốn build các file .exe cho Windows.

### Kiểm Tra Python

```bash
python3 --version
```

Cần Python 3.9 trở lên.

### Kiểm Tra PyInstaller

```bash
python3 -m PyInstaller --version
```

Nếu chưa có, cài đặt:

```bash
python3 -m pip install pyinstaller
```

## ⚡ CÁCH 1: Build Tự Động (Khuyến Nghị)

### Bước 1: Mở Terminal

Mở Terminal và cd vào thư mục source:

```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/source04062025"
```

### Bước 2: Chạy Script Build

```bash
python3 build_simple.py
```

Script sẽ:
- ✅ Kiểm tra PyInstaller
- ✅ Dọn dẹp build cũ  
- ✅ Build tất cả 9-10 modules
- ✅ Tạo folder `dist_windows/` với tất cả file cần thiết

### Bước 3: Kiểm Tra Kết Quả

```bash
ls -la dist_windows/
```

Bạn sẽ thấy:
- Các file .exe: `hd_order`, `hd_order_123`, `check_status`, etc.
- File `config.ini.example`

## ⚡ CÁCH 2: Build Từng Module

Nếu cách 1 không hoạt động, build từng module:

```bash
python3 build_one_module.py hd_order.py
python3 build_one_module.py hd_order_123.py
python3 build_one_module.py hd_update_all.py
python3 build_one_module.py hd_update_price.py
python3 build_one_module.py hd_update_cho_va_khop.py
python3 build_one_module.py hd_update_danhmuc.py
python3 build_one_module.py hd_alert_possition_and_open_order.py
python3 build_one_module.py hd_cancel_orders_schedule.py
python3 build_one_module.py check_status.py
```

File .exe sẽ nằm trong folder `dist/`

## ⚡ CÁCH 3: Build Thủ Công (Nếu script lỗi)

### Build 1 module mẫu

```bash
python3 -m PyInstaller \
  --onefile \
  --console \
  --name hd_order \
  --clean \
  --hidden-import cst \
  --hidden-import utils \
  --hidden-import gg_sheet_factory \
  --hidden-import telegram_factory \
  --hidden-import binance_utils \
  --hidden-import google.auth.transport.requests \
  --hidden-import google.oauth2.credentials \
  --hidden-import ccxt \
  --hidden-import telegram \
  --hidden-import pandas \
  hd_order.py
```

Lặp lại cho các module khác.

## 📦 Tạo Package Distribution

### Tạo folder dist_windows

```bash
mkdir -p dist_windows
```

### Copy các file .exe

```bash
cp dist/* dist_windows/
```

### Copy config file

```bash
cp config.ini.example dist_windows/
```

### Tạo batch scripts cho Windows

Tạo file `dist_windows/start_all_bots.bat`:

```batch
@echo off
chcp 65001 >nul
echo Starting all bots...

start "Order Handler" hd_order.exe
timeout /t 2 >nul
start "SL/TP Handler" hd_order_123.exe
timeout /t 2 >nul
start "Market Data" hd_update_all.exe
timeout /t 2 >nul
start "Price Update" hd_update_price.exe
timeout /t 2 >nul
start "Status Update" hd_update_cho_va_khop.exe
timeout /t 2 >nul
start "Alerts" hd_alert_possition_and_open_order.exe
timeout /t 2 >nul
start "Cancel Scheduler" hd_cancel_orders_schedule.exe

echo All bots started!
pause
```

Tạo file `dist_windows/stop_all_bots.bat`:

```batch
@echo off
taskkill /F /IM hd_order.exe 2>nul
taskkill /F /IM hd_order_123.exe 2>nul
taskkill /F /IM hd_update_all.exe 2>nul
taskkill /F /IM hd_update_price.exe 2>nul
taskkill /F /IM hd_update_cho_va_khop.exe 2>nul
taskkill /F /IM hd_alert_possition_and_open_order.exe 2>nul
taskkill /F /IM hd_cancel_orders_schedule.exe 2>nul
echo All bots stopped!
pause
```

## 🐛 Xử Lý Lỗi

### Lỗi: "No module named 'PyInstaller'"

```bash
python3 -m pip install --upgrade pyinstaller
```

### Lỗi: "ModuleNotFoundError"

Thêm `--hidden-import` cho module bị thiếu:

```bash
--hidden-import <module_name>
```

### Lỗi: Script build không có output

Chạy trực tiếp:

```bash
python3 -u build_simple.py 2>&1 | tee build_log.txt
cat build_log.txt
```

### Lỗi: Build failed

Kiểm tra chi tiết:

```bash
ls -la dist/
ls -la build/
```

Xóa cache và thử lại:

```bash
rm -rf build/ dist/ __pycache__/ *.spec
python3 build_simple.py
```

## ✅ Deploy Sang Windows

### Bước 1: Zip folder

```bash
cd dist_windows
zip -r ../qbot_windows.zip .
cd ..
```

Hoặc dùng Finder để nén folder `dist_windows`

### Bước 2: Copy sang Windows

- USB drive
- Google Drive / Dropbox
- Email (nếu file nhỏ)

### Bước 3: Trên Windows

1. Giải nén `qbot_windows.zip`
2. Copy `config.ini.example` thành `config.ini`
3. Điền thông tin vào `config.ini`
4. Đặt file `credentials.json` (Google Sheets API)
5. Double-click `start_all_bots.bat`

## 📊 Kiểm Tra Build Thành Công

```bash
ls -lh dist_windows/

# Bạn sẽ thấy các file như:
# -rwxr-xr-x  1 user  staff    25M  hd_order
# -rwxr-xr-x  1 user  staff    24M  hd_order_123
# -rwxr-xr-x  1 user  staff    26M  hd_update_all
# ...
```

Mỗi file khoảng 20-30 MB là bình thường.

## 💡 Tips

1. **Build mất bao lâu?** 
   - Mỗi module: 30-60 giây
   - Tổng cộng: 5-10 phút

2. **Dung lượng?**
   - Mỗi .exe: 20-30 MB
   - Tổng package: 200-300 MB

3. **Có cần build lại không?**
   - Chỉ khi code thay đổi
   - Nếu chỉ đổi config.ini thì KHÔNG cần build lại

4. **Test trước khi deploy?**
   - Build 1 module test: `python3 build_one_module.py check_status.py`
   - Xem có lỗi không
   - Nếu OK mới build tất cả

## 🆘 Vẫn Không Chạy?

### Kiểm tra lại từ đầu:

```bash
# 1. Check Python
python3 --version

# 2. Check PyInstaller
python3 -m PyInstaller --version

# 3. Check các file tồn tại
ls -la *.py | grep "hd_"

# 4. Test import các module
python3 -c "import cst; print('cst OK')"
python3 -c "import utils; print('utils OK')"

# 5. Build thử 1 module đơn giản
python3 build_one_module.py check_status.py
```

Nếu tất cả đều OK, chạy:

```bash
python3 build_simple.py
```

---

## 📞 Cần Trợ Giúp?

1. Check file log: `build_log.txt` hoặc `build_progress.log`
2. Chạy với verbose: `python3 -u build_simple.py`
3. Test từng bước như trên

**Chúc bạn build thành công! 🎉**
