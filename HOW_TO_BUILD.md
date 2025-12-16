# 🔨 Hướng Dẫn Build QBot Cho Windows

## ⚠️ Lưu Ý Quan Trọng

**Nếu script không hiển thị output khi chạy**, hãy làm theo các bước sau:

## 📋 Các Bước Build

### 1. Cài đặt PyInstaller

```bash
python3 -m pip install pyinstaller
```

Kiểm tra đã cài thành công:
```bash
python3 -m PyInstaller --version
```

### 2. Build Một Module Test (Khuyến nghị)

Để test build trước khi build tất cả:

```bash
python3 build_one_module.py check_status.py
```

Nếu thành công, bạn sẽ thấy file `dist/check_status` hoặc `dist/check_status.exe`

### 3. Build Tất Cả Modules

```bash
python3 build_windows.py
```

**Nếu không thấy output**, kiểm tra log file:
```bash
cat build.log
```

Hoặc:
```bash
tail -f build.log
```

### 4. Kiểm Tra Kết Quả

Sau khi build xong:

```bash
# Kiểm tra folder dist
ls -la dist/

# Kiểm tra folder dist_windows (nếu có)
ls -la dist_windows/
```

## 🐛 Troubleshooting

### Script chạy nhưng không có output

1. **Kiểm tra log file:**
   ```bash
   cat build.log
   ```

2. **Chạy với verbose:**
   ```bash
   python3 -u build_windows.py 2>&1 | tee output.txt
   cat output.txt
   ```

3. **Test từng bước:**
   ```bash
   # Test PyInstaller
   python3 -c "import PyInstaller; print(PyInstaller.__version__)"
   
   # Test build một module
   python3 build_one_module.py check_status.py
   ```

### Lỗi "PyInstaller not found"

```bash
# Cài đặt lại
python3 -m pip install --upgrade pyinstaller

# Kiểm tra
python3 -m PyInstaller --version
```

### Lỗi import modules

Đảm bảo đã cài tất cả dependencies:
```bash
python3 -m pip install -r requirements_build.txt
```

## 📦 Sau Khi Build Thành Công

1. Folder `dist/` chứa tất cả file .exe
2. Folder `dist_windows/` (nếu script tạo) chứa package sẵn sàng deploy

Copy folder này sang Windows và chạy!

## 🆘 Vẫn Gặp Vấn Đề?

1. Kiểm tra Python version:
   ```bash
   python3 --version  # Cần 3.9+
   ```

2. Kiểm tra PyInstaller:
   ```bash
   python3 -m PyInstaller --version
   ```

3. Thử build một module đơn giản:
   ```bash
   python3 build_one_module.py check_status.py
   ```

4. Xem log chi tiết:
   ```bash
   python3 build_windows.py > build_output.txt 2>&1
   cat build_output.txt
   ```
