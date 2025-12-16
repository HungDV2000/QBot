# 🔄 HƯỚNG DẪN REVERSE ENGINEERING TỪ BUILD VỀ SOURCE CODE

**Ngày:** 2025-12-12  
**Mục đích:** Extract source code từ bản build MAXBirkinCat 207.96

---

## ⚠️ LƯU Ý QUAN TRỌNG

**Reverse engineering từ .exe về source code Python:**
- ✅ **Có thể** extract một phần code
- ❌ **KHÔNG hoàn hảo** - code sẽ mất comments, formatting, có thể có lỗi
- ⚠️ **Phức tạp** - cần nhiều công cụ và bước
- 🎯 **Không khuyến khích** - tốt hơn là có source code gốc

---

## 🛠️ CÁC CÔNG CỤ CẦN THIẾT

### 1. **pyinstxtractor** - Extract từ PyInstaller .exe
```bash
pip install pyinstxtractor
```

### 2. **uncompyle6** hoặc **decompyle3** - Decompile .pyc về .py
```bash
pip install uncompyle6
# hoặc
pip install decompyle3
```

### 3. **pycdc** (nếu cần) - Alternative decompiler
```bash
# Cần compile từ source
git clone https://github.com/zrax/pycdc.git
```

---

## 📋 QUY TRÌNH EXTRACT

### Bước 1: Extract PyInstaller Archive

PyInstaller bundle code vào trong .exe file. Cần extract nó ra:

```bash
# Dùng pyinstxtractor
python pyinstxtractor.py hd_order.exe
```

Kết quả: Tạo folder `hd_order.exe_extracted/` chứa:
- `PYZ-00.pyz` - Python bytecode archive
- `PYZ-00.pyz_extracted/` - Các file .pyc (compiled Python)
- Các files khác

### Bước 2: Extract PYZ Archive

```bash
# PyInstaller có thể extract PYZ
python pyinstxtractor.py PYZ-00.pyz
```

### Bước 3: Decompile .pyc về .py

Sau khi có các file `.pyc`, decompile chúng:

```bash
# Dùng uncompyle6
uncompyle6 file.pyc > file.py

# Hoặc dùng decompyle3
decompyle3 file.pyc > file.py
```

### Bước 4: Xử lý các file đã decompile

- ✅ Có được source code (một phần)
- ❌ Mất comments
- ❌ Mất formatting (indentation có thể sai)
- ❌ Variable names có thể bị obfuscate
- ❌ Có thể có lỗi syntax

---

## 🔧 CÔNG CỤ TỰ ĐỘNG

### Option 1: pyinstxtractor + uncompyle6 (Recommended)

```bash
# 1. Cài đặt
pip install pyinstxtractor uncompyle6

# 2. Extract .exe
python pyinstxtractor.py hd_order.exe

# 3. Decompile tất cả .pyc files
find hd_order.exe_extracted -name "*.pyc" -exec uncompyle6 {} \; > output.py
```

### Option 2: Dùng script tự động

Có thể tạo script Python để tự động hóa:

```python
import os
import subprocess
from pathlib import Path

def extract_and_decompile(exe_file):
    # Extract .exe
    subprocess.run(['python', 'pyinstxtractor.py', exe_file])
    
    extracted_dir = Path(f"{exe_file}_extracted")
    
    # Find all .pyc files
    pyc_files = list(extracted_dir.rglob("*.pyc"))
    
    # Decompile each
    for pyc_file in pyc_files:
        py_file = pyc_file.with_suffix('.py')
        subprocess.run(['uncompyle6', str(pyc_file)], 
                      stdout=open(py_file, 'w'))
```

---

## 📊 KẾT QUẢ MONG ĐỢI

### ✅ Có thể extract được:

1. **Cấu trúc code** - functions, classes, logic
2. **Tên biến/functions** - một phần (nếu không bị obfuscate)
3. **Logic business** - có thể đọc được

### ❌ KHÔNG thể hoặc khó extract:

1. **Comments** - Mất hoàn toàn
2. **Docstrings** - Có thể mất một phần
3. **Formatting** - Indentation có thể sai
4. **Variable names** - Có thể bị obfuscate
5. **Import statements** - Có thể thiếu một số

---

## 🎯 SO SÁNH VỚI SOURCE CODE GỐC

### Nếu đã có source code gốc (source04062025):

✅ **TỐT HƠN NHIỀU** để:
- Dùng source code gốc trực tiếp
- Chỉ dùng reverse engineering để:
  - Xác nhận logic
  - Tìm các thay đổi không có trong source gốc
  - Recover các file đã mất

### Nếu KHÔNG có source code gốc:

⚠️ Reverse engineering có thể giúp:
- Hiểu cách code hoạt động
- Extract logic business
- Nhưng sẽ cần rất nhiều thời gian để:
  - Fix syntax errors
  - Restore formatting
  - Add comments
  - Test và debug

---

## 🔍 PHƯƠNG PHÁP THỰC TẾ

### Nếu muốn so sánh MAXBirkinCat 207.96 với source04062025:

1. **Extract từ .exe** để xem:
   - Code logic có giống không
   - Có thay đổi gì so với source gốc
   - Config values

2. **Dùng source code gốc** để:
   - Build lại
   - Maintain
   - Develop

---

## 💡 KHUYẾN NGHỊ

### ✅ Nếu bạn có source code gốc (source04062025):

**KHÔNG CẦN** reverse engineer! Dùng source code gốc trực tiếp.

### ❌ Chỉ reverse engineer nếu:

1. Source code gốc đã mất
2. Muốn kiểm tra xem build có giống source không
3. Muốn recover một file cụ thể

---

## 🚀 CÁCH THỰC HIỆN (Nếu thực sự cần)

### Quick Start:

```bash
# 1. Cài đặt tools
pip install pyinstxtractor uncompyle6

# 2. Download pyinstxtractor.py (nếu chưa có)
wget https://raw.githubusercontent.com/extremecoders-re/pyinstxtractor/master/pyinstxtractor.py

# 3. Extract một file .exe
python pyinstxtractor.py "MAXBirkinCat 207.96/hd_order.exe"

# 4. Tìm file .pyc trong extracted folder
# 5. Decompile
uncompyle6 hd_order.exe_extracted/PYZ-00.pyz_extracted/hd_order.pyc > hd_order_decompiled.py
```

---

## ⚠️ HẠN CHẾ VÀ CẢNH BÁO

1. **Python version**: Decompiler cần match với Python version dùng để build
2. **Bytecode optimization**: Nếu code được optimize, decompile sẽ khó hơn
3. **Obfuscation**: Nếu code bị obfuscate, gần như không thể recover
4. **Thời gian**: Reverse engineering tốn rất nhiều thời gian
5. **Legal**: Đảm bảo bạn có quyền reverse engineer code này

---

## 🎯 KẾT LUẬN

**Với source code gốc (source04062025) đã có:**
- ✅ Dùng source code gốc
- ✅ Build lại từ source
- ❌ KHÔNG cần reverse engineer

**Reverse engineering chỉ hữu ích khi:**
- Source code gốc đã mất
- Cần kiểm tra/recover một phần code cụ thể
- Muốn xác nhận logic trong build

---

**Tạo bởi:** AI Assistant  
**Ngày:** 2025-12-12
