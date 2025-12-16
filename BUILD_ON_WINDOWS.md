# 🪟 HƯỚNG DẪN BUILD TRÊN WINDOWS

## ⚡ QUICK START (3 Bước)

### Bước 1: Cài Python và PyInstaller

Mở **Command Prompt** hoặc **PowerShell** (Run as Administrator):

```cmd
python --version
```

Nếu chưa có Python, tải từ: https://www.python.org/downloads/
- Chọn Python 3.9 hoặc 3.10
- ✅ **Quan trọng:** Khi cài, tick "Add Python to PATH"

Cài PyInstaller:
```cmd
python -m pip install pyinstaller
```

### Bước 2: Chạy Build

Mở Command Prompt, cd vào thư mục source:

```cmd
cd "C:\path\to\source04062025"
python build_simple.py
```

Hoặc dùng script đầy đủ:
```cmd
python build_windows.py
```

### Bước 3: Kiểm Tra Kết Quả

```cmd
dir dist_windows
```

Bạn sẽ thấy các file `.exe`:
- `hd_order.exe`
- `hd_order_123.exe`
- `hd_update_all.exe`
- ... và các file khác

---

## 📋 YÊU CẦU

- **Windows 10/11** (64-bit)
- **Python 3.9+** (khuyến nghị 3.9 hoặc 3.10)
- **PyInstaller** (sẽ được cài tự động)

---

## 🔨 CÁC CÁCH BUILD

### Cách 1: Build Đơn Giản (KHUYẾN NGHỊ)

```cmd
python build_simple.py
```

### Cách 2: Build Đầy Đủ Features

```cmd
python build_windows.py
```

### Cách 3: Build Từng Module

```cmd
python build_one_module.py check_status.py
python build_one_module.py hd_order.py
```

---

## 🐛 XỬ LÝ LỖI

### Lỗi: "python is not recognized"

→ Python chưa được thêm vào PATH. Cài lại Python và tick "Add Python to PATH"

### Lỗi: "No module named 'PyInstaller'"

```cmd
python -m pip install --upgrade pip
python -m pip install pyinstaller
```

### Lỗi: "Module not found"

Cài các dependencies:
```cmd
python -m pip install ccxt pandas numpy python-telegram-bot google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Build thất bại

Xóa cache và thử lại:
```cmd
rmdir /s /q build dist __pycache__
del *.spec
python build_simple.py
```

---

## 📦 SAU KHI BUILD XONG

1. **Kiểm tra folder `dist_windows/`**
   - Sẽ có các file `.exe`
   - File `config.ini.example`
   - File `start_all_bots.bat` và `stop_all_bots.bat`

2. **Cấu hình:**
   - Copy `config.ini.example` → `config.ini`
   - Mở `config.ini` và điền thông tin API
   - Đặt file `credentials.json` (Google Sheets API)

3. **Chạy:**
   - Double-click `start_all_bots.bat`

---

## ⏱️ THỜI GIAN

- Mỗi module: ~30-60 giây
- Tổng cộng: ~5-10 phút

---

## 💡 TIPS

1. **Test trước:** Build 1 module test trước:
   ```cmd
   python build_one_module.py check_status.py
   ```

2. **Nếu lỗi:** Xem output chi tiết để biết module nào lỗi

3. **Dung lượng:** Mỗi .exe khoảng 20-30 MB

---

## 📞 HỖ TRỢ

Nếu gặp vấn đề:
1. Kiểm tra Python version: `python --version` (cần 3.9+)
2. Kiểm tra PyInstaller: `python -m PyInstaller --version`
3. Đọc file `BUILD_GUIDE_VIETNAMESE.md` để được hướng dẫn chi tiết

---

**Chúc bạn build thành công trên Windows! 🚀**
