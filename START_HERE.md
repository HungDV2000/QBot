# 🚀 BẮT ĐẦU TẠI ĐÂY - HƯỚNG DẪN BUILD NHANH

## ✨ 3 BƯỚC ĐƠN GIẢN

### Bước 1: Mở Terminal

```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/source04062025"
```

### Bước 2: Cài Dependencies (nếu chưa cài)

```bash
python3 -m pip install pyinstaller
```

### Bước 3: Chạy Build

```bash
python3 build_simple.py
```

**Xong!** 🎉

---

## 📦 Kết Quả

Sau khi build xong, kiểm tra:

```bash
ls -la dist_windows/
```

Bạn sẽ thấy các file:
- `hd_order` (hoặc `.exe`)
- `hd_order_123`
- `hd_update_all`
- `check_status`
- ... và các file khác

---

## 🪟 Deploy Lên Windows

1. Copy toàn bộ folder `dist_windows` sang Windows
2. Trong folder đó:
   - Copy `config.ini.example` → `config.ini`
   - Chỉnh sửa `config.ini` với thông tin của bạn
   - Đặt file `credentials.json` (Google Sheets)
3. Double-click `start_all_bots.bat`

---

## 🐛 Nếu Gặp Lỗi

### Lỗi 1: "PyInstaller not found"
```bash
python3 -m pip install pyinstaller
```

### Lỗi 2: Build không có output
Chạy script thủ công và xem output:
```bash
python3 -u build_simple.py 2>&1 | tee build_output.log
cat build_output.log
```

### Lỗi 3: Build từng module riêng
```bash
python3 build_one_module.py check_status.py
python3 build_one_module.py hd_order.py
```

---

## 📖 Đọc Thêm

- `BUILD_GUIDE_VIETNAMESE.md` - Hướng dẫn chi tiết
- `QUICK_BUILD.md` - Quick reference
- `HOW_TO_BUILD.md` - Troubleshooting

---

## 💡 Script Build Có Sẵn

Tôi đã tạo **3 script build** cho bạn:

1. **`build_simple.py`** ⭐ KHUYẾN NGHỊ
   - Đơn giản, dễ debug
   - Build tất cả modules
   - Tạo folder `dist_windows` tự động

2. **`build_windows.py`** 
   - Build script đầy đủ với nhiều features
   - Tạo README tự động
   - Tạo batch scripts

3. **`build_one_module.py`**
   - Build từng module riêng
   - Dùng để test
   - Usage: `python3 build_one_module.py <file.py>`

---

## ⚡ Chạy Ngay

```bash
# Cách nhanh nhất
python3 build_simple.py

# Hoặc đầy đủ
python3 build_windows.py

# Hoặc test 1 module
python3 build_one_module.py check_status.py
```

---

**Chúc bạn build thành công! 🎉**

Nếu có vấn đề, đọc `BUILD_GUIDE_VIETNAMESE.md` để được hướng dẫn chi tiết.
