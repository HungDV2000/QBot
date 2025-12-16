# 🔨 Hướng Dẫn Build QBot Cho Windows

Hướng dẫn đóng gói QBot thành các file .exe có thể chạy trên Windows mà không cần cài Python.

## 📋 Yêu Cầu

### Trên máy build (macOS/Linux/Windows):
- Python 3.9+
- pip
- PyInstaller

### Cài đặt PyInstaller:
```bash
pip install pyinstaller
```

## 🚀 Cách Build

### Option 1: Sử dụng script tự động (Recommended)

```bash
# Chạy script build
python build_windows.py
```

Script sẽ:
1. ✅ Kiểm tra PyInstaller đã cài đặt
2. 🧹 Dọn dẹp các build cũ
3. 🔨 Build tất cả modules thành .exe
4. 📦 Tạo package distribution
5. 📝 Cập nhật batch scripts

### Option 2: Build từng module thủ công

```bash
# Build một module cụ thể
pyinstaller --onefile --console --name hd_order hd_order.py

# Build với đầy đủ options
pyinstaller \
  --onefile \
  --console \
  --name hd_order \
  --add-data "config.ini.example;." \
  --hidden-import cst \
  --hidden-import gg_sheet_factory \
  --hidden-import telegram_factory \
  --hidden-import binance_utils \
  --hidden-import utils \
  hd_order.py
```

## 📁 Cấu Trúc Sau Khi Build

```
source04062025/
├── build/              # Temporary build files
├── dist/               # Các file .exe
│   ├── hd_order.exe
│   ├── hd_order_123.exe
│   ├── hd_update_all.exe
│   └── ...
├── dist_windows/       # Package distribution (sẵn sàng deploy)
│   ├── *.exe
│   ├── start_all_bots.bat
│   ├── stop_all_bots.bat
│   ├── config.ini.example
│   └── README.txt
└── *.spec              # PyInstaller spec files
```

## 📦 Distribution Package

Sau khi build, folder `dist_windows/` chứa:
- ✅ Tất cả file .exe
- ✅ Batch scripts (đã được cập nhật)
- ✅ Config example
- ✅ README hướng dẫn

**Bước tiếp theo:**
1. Nén folder `dist_windows/` thành ZIP
2. Copy sang máy Windows
3. Giải nén và cấu hình `config.ini`
4. Chạy `start_all_bots.bat`

## ⚙️ Cấu Hình Nâng Cao

### Ẩn console window (GUI mode)

Trong `build_windows.py`, đổi:
```python
'--windowed',  # Không hiển thị console
```

Hoặc trong spec file:
```python
console=False,  # Ẩn console
```

### Thêm icon cho .exe

```bash
pyinstaller --icon=icon.ico --onefile hd_order.py
```

### Tối ưu kích thước file

```bash
# Sử dụng UPX (nếu có)
pyinstaller --upx-dir=/path/to/upx --onefile hd_order.py
```

## 🐛 Xử Lý Lỗi Thường Gặp

### 1. Lỗi "ModuleNotFoundError" sau khi build

**Nguyên nhân:** PyInstaller không tìm thấy một số module

**Giải pháp:** Thêm vào `--hidden-import`:
```python
--hidden-import module_name
```

### 2. Lỗi "FileNotFoundError: config.ini"

**Nguyên nhân:** File config không được copy vào package

**Giải pháp:** Thêm vào `--add-data`:
```bash
--add-data "config.ini.example;."
```

### 3. Lỗi Google Sheets authentication

**Nguyên nhân:** File `credentials.json` không tìm thấy

**Giải pháp:** 
- Đảm bảo `credentials.json` trong cùng folder với .exe
- Hoặc sử dụng absolute path trong code

### 4. Lỗi "Failed to execute script"

**Nguyên nhân:** Có exception khi chạy

**Giải pháp:**
- Build với `--debug` để xem chi tiết lỗi:
  ```bash
  pyinstaller --debug=all hd_order.py
  ```
- Chạy từ command line để xem error message

## 🔍 Kiểm Tra Build

### Test một .exe file:

```bash
# Windows
hd_order.exe

# Hoặc với console để xem output
cmd /k hd_order.exe
```

### Kiểm tra dependencies:

```bash
# Sử dụng Dependency Walker (Windows)
# Hoặc dumpbin (Visual Studio)
dumpbin /dependents hd_order.exe
```

## 📊 So Sánh Kích Thước

| Module | Source (.py) | Built (.exe) | Notes |
|--------|--------------|--------------|-------|
| hd_order.py | ~15 KB | ~20-30 MB | Bao gồm Python runtime |
| hd_order_123.py | ~10 KB | ~20-30 MB | |
| hd_update_all.py | ~20 KB | ~30-40 MB | Có pandas/numpy |

**Lưu ý:** Kích thước lớn vì đã bao gồm Python interpreter và tất cả dependencies.

## 🚀 Tối Ưu Hóa

### 1. Giảm kích thước với virtualenv minimal:

```bash
# Tạo virtualenv mới
python -m venv venv_minimal
source venv_minimal/bin/activate  # Linux/Mac
# hoặc
venv_minimal\Scripts\activate  # Windows

# Chỉ cài packages cần thiết
pip install pyinstaller ccxt pandas numpy python-telegram-bot google-api-python-client

# Build trong virtualenv này
```

### 2. Sử dụng --exclude-module:

```bash
pyinstaller --exclude-module matplotlib --exclude-module tkinter hd_order.py
```

### 3. Build với --onedir thay vì --onefile:

```bash
# --onedir: Tạo folder với nhiều files (nhỏ hơn, load nhanh hơn)
pyinstaller --onedir hd_order.py
```

## 📝 Notes

- ⚠️ **Build trên cùng platform:** Nên build trên Windows để có .exe tương thích tốt nhất
- ✅ **Test trước khi deploy:** Luôn test .exe trên máy Windows khác
- 📦 **Include credentials.json:** Đảm bảo user có file này
- 🔐 **Security:** Không commit .exe files lên Git (có thể rất lớn)

## 🔗 Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [PyInstaller Manual](https://pyinstaller.readthedocs.io/)
- [Troubleshooting Guide](https://pyinstaller.readthedocs.io/en/stable/when-things-go-wrong.html)

---

**Last Updated:** 2025
