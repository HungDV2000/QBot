# 🔧 TROUBLESHOOTING - Extract Script

**Ngày:** 2025-12-12

---

## ⚠️ LỖI THƯỜNG GẶP

### 1. Lỗi: "Module use of python313.dll conflicts with this version of Python"

**Nguyên nhân:**
- Conflict giữa các version Python
- Virtual environment không đúng
- Python interpreter bị lẫn version

**Giải pháp:**

#### Option 1: Tải thủ công pyinstxtractor.py

1. Truy cập: https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py
2. Copy toàn bộ nội dung
3. Tạo file `pyinstxtractor.py` trong thư mục `source04062025`
4. Chạy lại script

#### Option 2: Sửa Python environment

```bash
# Kiểm tra Python version
python --version
py --version

# Tạo venv mới với Python version cụ thể
python3.11 -m venv venv  # Hoặc version bạn có
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate     # Windows

# Cài packages trong venv
pip install uncompyle6 requests
```

#### Option 3: Dùng Python version cụ thể

```bash
# Trên Windows, dùng py launcher với version cụ thể
py -3.11 extract_from_exe.py ...
```

---

### 2. Lỗi: "uncompyle6 not found"

**Giải pháp:**

```bash
pip install uncompyle6
```

Nếu đang dùng venv:
```bash
source venv/bin/activate  # Activate venv trước
pip install uncompyle6
```

---

### 3. Lỗi: "pyinstxtractor.py not found"

**Giải pháp:**

#### Tải thủ công (Khuyến nghị):

1. Mở browser
2. Truy cập: https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py
3. Right-click → Save As
4. Lưu vào thư mục `source04062025` với tên `pyinstxtractor.py`

#### Hoặc dùng curl/wget:

```bash
# macOS/Linux
curl -O https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py

# Windows (với PowerShell)
Invoke-WebRequest -Uri https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py -OutFile pyinstxtractor.py
```

---

### 4. Lỗi khi decompile .pyc files

**Nguyên nhân:**
- Python version không match (file .pyc được compile với version khác)
- Bytecode đã được optimize
- File bị corrupt

**Giải pháp:**

- Xem file `_failed_files.txt` để biết file nào lỗi
- Một số file có thể không decompile được - đây là bình thường
- Thử với decompiler khác: `decompyle3`, `pycdc`

---

## 🎯 WORKFLOW ĐỀ XUẤT

### Bước 1: Setup environment

```bash
# Tạo venv
python3 -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate     # Windows

# Cài packages
pip install uncompyle6 requests
```

### Bước 2: Tải pyinstxtractor.py thủ công

1. Truy cập: https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py
2. Lưu vào `source04062025/pyinstxtractor.py`

### Bước 3: Chạy extract script

```bash
python3 extract_from_exe.py "../MAXBirkinCat 207.96/hd_order.exe"
```

---

## 🔍 DEBUG TIPS

### Kiểm tra Python environment:

```bash
# Xem Python version
python --version

# Xem Python path
python -c "import sys; print(sys.executable)"

# Xem packages đã cài
pip list
```

### Test uncompyle6:

```bash
python -m uncompyle6 --version
```

### Test pyinstxtractor.py:

```bash
python pyinstxtractor.py --help
```

---

## 💡 GIẢI PHÁP NHANH

Nếu gặp lỗi Python version conflict:

1. **Tải pyinstxtractor.py thủ công** (không cần script tải)
2. **Tạo venv mới** với Python version ổn định (3.9-3.11)
3. **Cài packages trong venv**
4. **Chạy script từ venv**

---

**Tạo bởi:** AI Assistant  
**Ngày:** 2025-12-12
