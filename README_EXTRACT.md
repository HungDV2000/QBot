# 🔄 Hướng Dẫn Sử Dụng Script Extract Source Code

**Script:** `extract_from_exe.py`  
**Mục đích:** Extract và decompile source code từ PyInstaller .exe files

---

## 🚀 CÁCH SỬ DỤNG

### Bước 1: Cài đặt công cụ

```bash
pip install uncompyle6
```

Script sẽ tự động tải `pyinstxtractor.py` nếu chưa có.

### Bước 2: Chạy script

#### Extract 1 file .exe:

```bash
python3 extract_from_exe.py "../MAXBirkinCat 207.96/hd_order.exe"
```

#### Extract nhiều file .exe:

```bash
python3 extract_from_exe.py "../MAXBirkinCat 207.96/hd_order.exe" "../MAXBirkinCat 207.96/hd_order_123.exe"
```

#### Extract tất cả .exe trong folder:

```bash
cd "../MAXBirkinCat 207.96"
python3 ../source04062025/extract_from_exe.py *.exe
```

---

## 📋 OUTPUT

Script sẽ tạo:

1. **Folder extracted**: `hd_order.exe_extracted/`
   - Chứa các file được extract từ .exe
   - Có các file .pyc (Python bytecode)

2. **Folder decompiled**: `extracted_source/decompiled_YYYYMMDD_HHMMSS/`
   - Chứa các file .py đã được decompile
   - Giữ nguyên cấu trúc thư mục gốc

3. **File log**: `_failed_files.txt`
   - Danh sách các file không thể decompile

---

## ⚠️ LƯU Ý

### Hạn chế của decompilation:

1. ❌ **Mất comments** - Tất cả comments bị mất
2. ❌ **Mất docstrings** - Có thể mất một phần
3. ❌ **Formatting sai** - Indentation có thể không đúng
4. ❌ **Variable names** - Có thể bị obfuscate hoặc thay đổi
5. ❌ **Syntax errors** - Có thể có lỗi cần fix thủ công

### Những gì có thể extract:

1. ✅ **Logic code** - Functions, classes, flow control
2. ✅ **Business logic** - Có thể đọc và hiểu được
3. ✅ **Structure** - Cấu trúc code

---

## 📊 VÍ DỤ OUTPUT

```
extracted_source/
└── decompiled_20251212_150000/
    ├── hd_order.py
    ├── cst.py
    ├── utils.py
    ├── gg_sheet_factory.py
    ├── telegram_factory.py
    └── _failed_files.txt  (nếu có)
```

---

## 🔧 TROUBLESHOOTING

### Lỗi: "uncompyle6 not found"

```bash
pip install uncompyle6
```

### Lỗi: "pyinstxtractor.py not found"

Script sẽ tự động tải, nhưng nếu lỗi, tải thủ công:
```bash
wget https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py
```

### Lỗi: "No module named ..." khi decompile

Một số file .pyc có thể không decompile được do:
- Python version không match
- Bytecode đã được optimize
- File bị corrupt

→ Xem file `_failed_files.txt` để biết chi tiết

---

## 💡 TIPS

1. **Review code sau khi decompile:**
   - Fix syntax errors
   - Add comments
   - Restore formatting

2. **So sánh với source gốc:**
   - Dùng diff tool để so sánh
   - Tìm các thay đổi không có trong source gốc

3. **Backup trước khi extract:**
   - Giữ source code gốc an toàn
   - Extract chỉ để reference

---

**Tạo bởi:** AI Assistant  
**Ngày:** 2025-12-12
