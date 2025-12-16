# 📦 Build Script: --onedir Mode (giống MAXBirkinCat 207.96)

## 🎯 Mục Đích

Script `build_onedir.py` build các modules thành .exe files với cấu trúc **--onedir** (directory mode), tạo ra cấu trúc giống bản build "MAXBirkinCat 207.96".

## 🔍 Khác Biệt Với Build Scripts Khác

| Script | Mode | Output |
|--------|------|--------|
| `build_simple.py` | `--onefile` | Các file .exe lớn, độc lập |
| `build_windows.py` | `--onefile` | Các file .exe lớn, độc lập + docs |
| **`build_onedir.py`** | **`--onedir`** | **Folder chứa .exe nhỏ + thư viện** ✅ |

## 🚀 Sử Dụng

### Bước 1: Chạy Script

```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/source04062025"
python3 build_onedir.py
```

### Bước 2: Đợi Build Hoàn Tất

Script sẽ:
1. ✅ Kiểm tra yêu cầu (Python, PyInstaller)
2. ✅ Dọn dẹp build cũ
3. ✅ Build từng module (9 modules)
4. ✅ Merge tất cả vào folder `dist_onedir/`
5. ✅ Copy config files
6. ✅ Tạo README.txt

### Bước 3: Kiểm Tra Output

```bash
ls -la dist_onedir/
```

Bạn sẽ thấy:
- Các file .exe (14-20 MB mỗi file)
- Các thư mục thư viện (numpy/, pandas/, telegram_factory/, etc.)
- config.ini.example
- README.txt

## 📁 Cấu Trúc Output

```
dist_onedir/
├── hd_order.exe                           ← File .exe nhỏ (~14 MB)
├── hd_order_123.exe
├── hd_update_all.exe
├── ... (9 file .exe)
│
├── numpy/                                  ← Thư viện Python
├── pandas/
├── telegram_factory/
├── googleapiclient/
├── cryptography/
├── PIL/
├── scipy/
│
├── *.pyd files                            ← Python extensions
├── *.dll files                            ← Windows DLLs
│
├── config.ini.example
└── README.txt
```

## ⚙️ Cấu Hình

### Modules Được Build (9 modules):

- ✅ hd_order.py
- ✅ hd_order_123.py
- ✅ hd_update_all.py
- ✅ hd_update_price.py
- ✅ hd_update_cho_va_khop.py
- ✅ hd_update_danhmuc.py
- ✅ hd_alert_possition_and_open_order.py
- ✅ hd_cancel_orders_schedule.py
- ✅ hd_isolated_crossed_converter.py
- ❌ check_status.py (KHÔNG build - giống MAXBirkinCat 207.96)

### Hidden Imports:

Script tự động include tất cả dependencies cần thiết:
- Local modules (cst, utils, gg_sheet_factory, etc.)
- Google API
- Telegram Bot
- Trading (ccxt)
- Data processing (pandas, numpy, etc.)

## 💡 Ưu Điểm Của --onedir Mode

1. ✅ **Khởi động nhanh** - Không cần extract temp files
2. ✅ **File .exe nhỏ** - 14-20 MB mỗi file (vs 50-150 MB với --onefile)
3. ✅ **Dễ debug** - Có thể xem các thư viện
4. ✅ **Chia sẻ thư viện** - Các modules có thể share libraries

## ⚠️ Lưu Ý

1. **Cần toàn bộ folder** - Không thể chỉ copy 1 file .exe
2. **Giữ nguyên cấu trúc** - Không xóa các subfolders
3. **credentials.json** - Cần tự copy vào `dist_onedir/` (không được tự động copy vì lý do bảo mật)

## 🔧 Tùy Chỉnh

### Thêm/Bỏ Module:

Sửa list `MODULES` trong `build_onedir.py`:

```python
MODULES = [
    "hd_order.py",
    # ... các modules khác
    # "check_status.py",  # Bỏ comment để thêm vào
]
```

### Thêm Hidden Import:

Sửa list `HIDDEN_IMPORTS` trong `build_onedir.py`:

```python
HIDDEN_IMPORTS = [
    # ... existing imports
    'your_new_module',  # Thêm vào đây
]
```

## 📊 So Sánh Kích Thước

| Mode | Kích thước mỗi .exe | Tổng kích thước |
|------|---------------------|-----------------|
| `--onefile` | 50-150 MB | ~500+ MB (tất cả .exe) |
| **`--onedir`** | **14-20 MB** | **~400-500 MB** (toàn bộ folder) |

## 🎯 Kết Quả

Sau khi build, bạn sẽ có folder `dist_onedir/` với cấu trúc **giống hệt** bản build "MAXBirkinCat 207.96":

- ✅ 9 file .exe
- ✅ Thư viện Python được extract
- ✅ Cấu trúc folder giống nhau
- ✅ Có thể deploy trực tiếp

---

**Tạo bởi:** AI Assistant  
**Ngày:** 2025-12-12
