# 🐍 HƯỚNG DẪN SETUP VIRTUAL ENVIRONMENT

**Ngày:** 2025-12-12  
**Mục đích:** Tạo môi trường Python riêng biệt cho project

---

## 🎯 TẠI SAO CẦN VIRTUAL ENVIRONMENT?

- ✅ **Cô lập dependencies** - Không ảnh hưởng Python system-wide
- ✅ **Quản lý packages** - Mỗi project có packages riêng
- ✅ **Tránh conflict** - Không bị xung đột version packages
- ✅ **Dễ reproduce** - Có thể tái tạo môi trường dễ dàng

---

## 📋 QUY TRÌNH SETUP

### Bước 1: Tạo Virtual Environment

#### Trên macOS/Linux:

```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/source04062025"

# Tạo venv
python3 -m venv venv

# Hoặc với Python cụ thể
python3.11 -m venv venv
```

#### Trên Windows:

```bash
cd "C:\Users\Administrator\Downloads\source04062025"

# Tạo venv
python -m venv venv

# Hoặc
py -m venv venv
```

### Bước 2: Activate Virtual Environment

#### Trên macOS/Linux:

```bash
# Activate
source venv/bin/activate

# Hoặc
. venv/bin/activate
```

Sau khi activate, prompt sẽ có `(venv)` ở đầu:
```
(venv) user@computer:source04062025$
```

#### Trên Windows:

```bash
# Activate
venv\Scripts\activate

# Hoặc với PowerShell
venv\Scripts\Activate.ps1
```

Sau khi activate:
```
(venv) C:\Users\Administrator\Downloads\source04062025>
```

### Bước 3: Cài đặt Packages

```bash
# Upgrade pip trước
pip install --upgrade pip

# Cài đặt các packages cần thiết
pip install google-auth google-auth-oauthlib google-api-python-client python-telegram-bot ccxt pandas numpy aiohttp requests pyinstaller uncompyle6
```

### Bước 4: Tạo requirements.txt (tùy chọn)

```bash
# Export packages đã cài
pip freeze > requirements.txt
```

### Bước 5: Sử dụng

```bash
# Chạy scripts trong venv
python3 build_onedir.py
python3 extract_from_exe.py "path/to/file.exe"
```

### Bước 6: Deactivate (khi xong việc)

```bash
deactivate
```

---

## 📁 CẤU TRÚC THỨ MỤC

Sau khi tạo venv, cấu trúc sẽ như sau:

```
source04062025/
├── venv/                    ← Virtual environment folder
│   ├── bin/                 ← Executables (macOS/Linux)
│   │   ├── python
│   │   ├── pip
│   │   └── activate
│   ├── Scripts/             ← Executables (Windows)
│   │   ├── python.exe
│   │   ├── pip.exe
│   │   └── activate.bat
│   ├── lib/                 ← Installed packages
│   └── include/
│
├── build_onedir.py
├── extract_from_exe.py
├── requirements.txt         ← List packages (nên tạo)
└── ...
```

---

## 🔧 TẠO REQUIREMENTS.TXT

### Từ packages đã cài:

```bash
pip freeze > requirements.txt
```

### Hoặc tạo thủ công:

Tạo file `requirements.txt` với nội dung:

```txt
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-api-python-client>=2.0.0
python-telegram-bot>=20.0
ccxt>=4.0.0
pandas>=2.0.0
numpy>=1.24.0
aiohttp>=3.8.0
requests>=2.28.0
pyinstaller>=6.0.0
uncompyle6>=3.8.0
```

### Cài đặt từ requirements.txt:

```bash
pip install -r requirements.txt
```

---

## 📝 WORKFLOW HOÀN CHỈNH

### Lần đầu setup:

```bash
# 1. Tạo venv
python3 -m venv venv

# 2. Activate
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate     # Windows

# 3. Upgrade pip
pip install --upgrade pip

# 4. Cài packages
pip install -r requirements.txt
# hoặc cài thủ công
pip install google-auth google-auth-oauthlib google-api-python-client python-telegram-bot ccxt pandas numpy aiohttp requests pyinstaller uncompyle6
```

### Mỗi lần làm việc:

```bash
# 1. Activate venv
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate     # Windows

# 2. Làm việc
python3 build_onedir.py

# 3. Deactivate khi xong
deactivate
```

---

## 🚀 SCRIPT TỰ ĐỘNG SETUP

Có thể tạo script tự động:

### macOS/Linux: `setup_venv.sh`

```bash
#!/bin/bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install google-auth google-auth-oauthlib google-api-python-client python-telegram-bot ccxt pandas numpy aiohttp requests pyinstaller uncompyle6
echo "✅ Virtual environment đã được setup!"
echo "Để activate: source venv/bin/activate"
```

### Windows: `setup_venv.bat`

```batch
@echo off
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install google-auth google-auth-oauthlib google-api-python-client python-telegram-bot ccxt pandas numpy aiohttp requests pyinstaller uncompyle6
echo ✅ Virtual environment đã được setup!
echo Để activate: venv\Scripts\activate
```

---

## ⚠️ LƯU Ý

### 1. Gitignore

Thêm `venv/` vào `.gitignore`:

```bash
echo "venv/" >> .gitignore
```

### 2. Không commit venv

Virtual environment folder rất lớn, không nên commit vào Git.

### 3. Requirements.txt

✅ **NÊN commit** `requirements.txt` để người khác có thể tái tạo môi trường.

### 4. Python version

Đảm bảo Python version match:
```bash
python3 --version  # Kiểm tra version
```

---

## 🔍 KIỂM TRA

### Kiểm tra venv đã activate:

```bash
which python  # macOS/Linux - phải trỏ đến venv/bin/python
where python  # Windows - phải trỏ đến venv\Scripts\python.exe

# Hoặc
python --version
pip list  # Xem packages đã cài
```

### Kiểm tra packages:

```bash
pip list
pip show <package_name>  # Xem thông tin package cụ thể
```

---

## 🎯 KẾT LUẬN

**Workflow tốt nhất:**

1. ✅ Tạo venv một lần
2. ✅ Activate mỗi khi làm việc
3. ✅ Cài packages trong venv
4. ✅ Tạo requirements.txt
5. ✅ Deactivate khi xong

---

**Tạo bởi:** AI Assistant  
**Ngày:** 2025-12-12
