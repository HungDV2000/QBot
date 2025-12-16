# 🤖 QBot - Trading Bot Build System

Hệ thống build tự động để tạo file .exe cho Windows từ Python source code.

## 📂 Cấu Trúc Dự Án

```
source04062025/
├── 🔧 Build Scripts
│   ├── build_simple.py          ⭐ Script build đơn giản (KHUYẾN NGHỊ)
│   ├── build_windows.py         📦 Script build đầy đủ features
│   ├── build_one_module.py      🔨 Build từng module riêng
│   ├── install_dependencies.sh  📥 Cài dependencies
│   └── create_batch_files.sh    📝 Tạo batch files
│
├── 📖 Documentation
│   ├── START_HERE.md           ⭐ BẮT ĐẦU TẠI ĐÂY
│   ├── BUILD_GUIDE_VIETNAMESE.md  📚 Hướng dẫn chi tiết
│   ├── QUICK_BUILD.md             ⚡ Quick reference
│   └── HOW_TO_BUILD.md            🔧 Troubleshooting
│
├── 🤖 Trading Modules
│   ├── hd_order.py                    # Xử lý đặt lệnh
│   ├── hd_order_123.py                # SL/TP handler
│   ├── hd_update_all.py               # Cập nhật market data
│   ├── hd_update_price.py             # Cập nhật giá
│   ├── hd_update_cho_va_khop.py       # Cập nhật trạng thái
│   ├── hd_update_danhmuc.py           # Cập nhật danh mục
│   ├── hd_alert_possition_and_open_order.py  # Cảnh báo
│   └── hd_cancel_orders_schedule.py   # Hủy lệnh định kỳ
│
├── 🔌 Core Modules
│   ├── cst.py                   # Config constants
│   ├── utils.py                 # Utilities
│   ├── gg_sheet_factory.py      # Google Sheets API
│   ├── telegram_factory.py      # Telegram API
│   └── binance_utils.py         # Binance utilities
│
└── ⚙️ Config
    ├── config.ini               # Config thực tế (không commit)
    └── config.ini.example       # Config mẫu
```

## 🚀 Quick Start

### Cách 1: Build Nhanh (Khuyến Nghị)

```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/source04062025"
python3 build_simple.py
```

### Cách 2: Build Đầy Đủ

```bash
python3 build_windows.py
```

### Cách 3: Build Từng Module

```bash
python3 build_one_module.py hd_order.py
python3 build_one_module.py check_status.py
```

## 📋 Yêu Cầu

- **Python 3.9+**
- **PyInstaller** (`python3 -m pip install pyinstaller`)
- **macOS/Linux** (để build cho Windows)

## 📦 Output

Sau khi build xong:

```
dist_windows/
├── hd_order.exe
├── hd_order_123.exe
├── hd_update_all.exe
├── hd_update_price.exe
├── hd_update_cho_va_khop.exe
├── hd_update_danhmuc.exe
├── hd_alert_possition_and_open_order.exe
├── hd_cancel_orders_schedule.exe
├── check_status.exe
├── config.ini.example
├── start_all_bots.bat
└── stop_all_bots.bat
```

## 🪟 Deploy Lên Windows

1. Copy folder `dist_windows` sang Windows
2. Đổi tên `config.ini.example` → `config.ini`
3. Điền thông tin API vào `config.ini`
4. Đặt file `credentials.json` (Google Sheets API)
5. Chạy `start_all_bots.bat`

## 📖 Documentation

| File | Mô Tả |
|------|-------|
| `START_HERE.md` | Hướng dẫn bắt đầu nhanh ⭐ |
| `BUILD_GUIDE_VIETNAMESE.md` | Hướng dẫn chi tiết từng bước |
| `QUICK_BUILD.md` | Quick reference |
| `HOW_TO_BUILD.md` | Troubleshooting |

## 🔧 Build Scripts

### 1. build_simple.py ⭐

Script đơn giản nhất, dễ debug:

```bash
python3 build_simple.py
```

**Ưu điểm:**
- Đơn giản, dễ đọc
- Output rõ ràng
- Dễ debug khi lỗi

### 2. build_windows.py

Script đầy đủ features:

```bash
python3 build_windows.py
```

**Features:**
- Kiểm tra đầy đủ requirements
- Tạo README tự động
- Tạo batch scripts
- Log chi tiết

### 3. build_one_module.py

Build từng module để test:

```bash
python3 build_one_module.py <module_name.py>
```

**Ví dụ:**
```bash
python3 build_one_module.py check_status.py
python3 build_one_module.py hd_order.py
```

## 🐛 Troubleshooting

### Lỗi: "PyInstaller not found"

```bash
python3 -m pip install --upgrade pyinstaller
python3 -m PyInstaller --version
```

### Lỗi: "No output"

```bash
# Chạy với output
python3 -u build_simple.py 2>&1 | tee build_log.txt
cat build_log.txt
```

### Lỗi: "Module not found"

Đảm bảo tất cả dependencies đã cài:

```bash
python3 -m pip install ccxt pandas numpy telegram python-telegram-bot google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Build thất bại

```bash
# Dọn dẹp và thử lại
rm -rf build/ dist/ __pycache__/ *.spec
python3 build_simple.py
```

## 💡 Tips

1. **Test trước:** Build 1 module test trước khi build tất cả
   ```bash
   python3 build_one_module.py check_status.py
   ```

2. **Thời gian:** Mỗi module mất 30-60s, tổng ~5-10 phút

3. **Dung lượng:** Mỗi .exe khoảng 20-30 MB

4. **Không cần rebuild:** Nếu chỉ đổi config.ini, không cần build lại

5. **Debug:** Nếu build lỗi, kiểm tra file `.spec` để xem config

## 🔒 Bảo Mật

⚠️ **QUAN TRỌNG:**

- KHÔNG commit `config.ini` (chứa API keys)
- KHÔNG commit `credentials.json`, `token.json`
- KHÔNG chia sẻ file .exe build kèm config
- Chỉ chia sẻ folder `dist_windows` KHÔNG có config thật

## 📊 Modules Overview

| Module | Chức Năng | Priority |
|--------|-----------|----------|
| `hd_order.py` | Đặt lệnh mới | ⭐⭐⭐ |
| `hd_order_123.py` | SL/TP handler | ⭐⭐⭐ |
| `hd_update_all.py` | Cập nhật market data | ⭐⭐ |
| `hd_update_price.py` | Cập nhật giá | ⭐⭐ |
| `hd_update_cho_va_khop.py` | Cập nhật trạng thái | ⭐⭐ |
| `hd_update_danhmuc.py` | Cập nhật danh mục | ⭐ |
| `hd_alert_possition_and_open_order.py` | Cảnh báo | ⭐⭐ |
| `hd_cancel_orders_schedule.py` | Hủy lệnh tự động | ⭐ |
| `check_status.py` | Kiểm tra trạng thái | ⭐ |

## 🎯 Workflow

```
1. Viết code Python
   ↓
2. Test code trên macOS
   ↓
3. Build với PyInstaller
   ↓
4. Tạo package distribution
   ↓
5. Deploy sang Windows
   ↓
6. Config và chạy
```

## 📞 Support

Nếu gặp vấn đề:

1. Đọc `BUILD_GUIDE_VIETNAMESE.md`
2. Check logs: `build_log.txt`, `build_progress.log`
3. Test từng bước trong guide
4. Build từng module để xác định module nào lỗi

---

**Build date:** 2025-12-11  
**Version:** 2.0  
**Platform:** macOS → Windows (cross-platform build)
