# 🚀 HƯỚNG DẪN BUILD NHANH

## 📋 Yêu Cầu

- **Python 3.9+** 
- **macOS/Linux** (để build cho Windows)
- **PyInstaller**

## ⚡ Build Nhanh (3 Bước)

### Bước 1: Cài đặt dependencies

```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

Hoặc thủ công:
```bash
python3 -m pip install pyinstaller
```

### Bước 2: Chạy build

```bash
python3 build_windows.py
```

Script sẽ:
- ✅ Kiểm tra yêu cầu hệ thống
- ✅ Dọn dẹp build cũ
- ✅ Build tất cả modules thành .exe
- ✅ Tạo package distribution hoàn chỉnh

### Bước 3: Lấy kết quả

```bash
ls -la dist_windows/
```

Folder `dist_windows/` chứa:
- ✅ Tất cả file .exe
- ✅ config.ini.example
- ✅ start_all_bots.bat / stop_all_bots.bat
- ✅ README.txt với hướng dẫn chi tiết

## 📦 Deploy Lên Windows

1. Copy toàn bộ folder `dist_windows/` sang máy Windows
2. Đọc file `README.txt`
3. Cấu hình `config.ini`
4. Double-click `start_all_bots.bat`

## 🐛 Nếu Gặp Lỗi

### Lỗi: "PyInstaller not found"
```bash
python3 -m pip install --upgrade pyinstaller
python3 -m PyInstaller --version
```

### Lỗi: "Module not found"
Kiểm tra các file .py có tồn tại:
```bash
ls -la *.py
```

### Build không có output
Kiểm tra Python version:
```bash
python3 --version  # Cần 3.9+
```

### Test build 1 module trước
```bash
python3 build_one_module.py check_status.py
```

## 📊 Output Mẫu

```
====================================================================
  QBOT - WINDOWS BUILD SCRIPT
====================================================================

🔹 Kiểm tra yêu cầu hệ thống...
Python version: 3.11.5
PyInstaller version: 6.3.0
✅ PyInstaller đã cài đặt

🔹 Kiểm tra các module...
  ✓ hd_order.py
  ✓ hd_order_123.py
  ...
✅ Kiểm tra yêu cầu hoàn tất

====================================================================
  BẮT ĐẦU BUILD MODULES
====================================================================

[1/10] Building hd_order.py...
✅ Build thành công: hd_order.py

[2/10] Building hd_order_123.py...
✅ Build thành công: hd_order_123.py

...

====================================================================
  KẾT QUẢ BUILD
====================================================================

✅ Thành công: 10/10

====================================================================
  TẠO DISTRIBUTION PACKAGE
====================================================================

✅ Distribution package hoàn tất

====================================================================
  ✅ BUILD HOÀN TẤT!
====================================================================

📦 Package: /path/to/dist_windows
```

## 🎯 Các Module Được Build

1. `hd_order.exe` - Xử lý đặt lệnh
2. `hd_order_123.exe` - Xử lý SL/TP
3. `hd_update_all.exe` - Cập nhật dữ liệu market
4. `hd_update_price.exe` - Cập nhật giá
5. `hd_update_cho_va_khop.exe` - Cập nhật trạng thái
6. `hd_update_danhmuc.exe` - Cập nhật danh mục
7. `hd_alert_possition_and_open_order.exe` - Cảnh báo
8. `hd_cancel_orders_schedule.exe` - Hủy lệnh định kỳ
9. `hd_isolated_crossed_converter.exe` - Chuyển đổi margin
10. `check_status.exe` - Kiểm tra trạng thái

## 💡 Tips

- Build mất khoảng 2-5 phút tùy máy
- Mỗi .exe khoảng 20-50 MB
- Package hoàn chỉnh khoảng 200-500 MB
- Chỉ cần build 1 lần, sau đó copy sang Windows dùng được

## 📞 Hỗ Trợ

Nếu vẫn gặp vấn đề:
1. Xóa folder `build/`, `dist/`, `__pycache__/`
2. Xóa tất cả file `.spec`
3. Chạy lại `python3 build_windows.py`

---
**Thời gian:** ~5 phút
**Kết quả:** Package sẵn sàng deploy trên Windows
