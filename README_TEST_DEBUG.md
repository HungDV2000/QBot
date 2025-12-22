# 🧪 HƯỚNG DẪN TEST DEBUG LẶP ĐƠN

## 📋 Mục đích

Giúp bạn tự debug và tìm hiểu tại sao bot vẫn bị lặp đơn mặc dù đã có logic kiểm tra.

---

## ⚙️ Setup (Chỉ chạy 1 lần đầu tiên)

### Bước 1: Tạo Virtual Environment

```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/qbot"

# Chạy script setup
chmod +x setup_venv.sh
./setup_venv.sh
```

**Nếu gặp lỗi SSL Certificate:**

```bash
# Tạo venv thủ công
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Cài đặt packages với trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org ccxt pandas numpy google-auth google-auth-oauthlib google-api-python-client aiohttp requests

# Deactivate
deactivate
```

### Bước 2: Kiểm tra cài đặt thành công

```bash
source venv/bin/activate
python -c "import ccxt; print('✅ ccxt OK')"
deactivate
```

---

## 🛠️ Các file test đã tạo

### 1. `test_fetch_orders_simple.py` - Test cơ bản nhất

**Mục đích:**
- Kiểm tra xem `fetch_open_orders()` có trả về algo orders không?
- Hiển thị chi tiết tất cả orders
- Phân biệt Basic orders vs Algo orders

**Cách chạy:**
```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/qbot"

# Activate virtual environment trước
source venv/bin/activate

# Chạy test
python test_fetch_orders_simple.py

# Sau khi xong, deactivate
deactivate
```

**Kết quả mong đợi:**
```
✅ fetch_open_orders() TRẢ VỀ ĐƯỢC ALGO ORDERS!
   Tổng số orders: 10
   Algo orders (Conditional): 6
   Basic orders: 4
```

---

### 2. `test_debug_lap_don.py` - Test chi tiết

**Mục đích:**
- Kiểm tra logic `has_pending_trailing_stop_order()` có hoạt động đúng không
- Phát hiện symbols nào bị lặp đơn
- So sánh symbols trong sheet vs symbols có orders
- Lưu full data vào file JSON

**Cách chạy:**
```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/qbot"

# Activate virtual environment trước
source venv/bin/activate

# Chạy test
python test_debug_lap_don.py

# Sau khi xong, deactivate
deactivate
```

**Kết quả mong đợi:**
```
✅ KHÔNG CÓ SYMBOLS NÀO BỊ LẶP ĐƠN!

TEST LOGIC has_pending_trailing_stop_order():
  ✅ PIPPIN/USDT | Có pending → BOT SẼ BỎ QUA ✓
  ✅ HIPPO/USDT  | Có pending → BOT SẼ BỎ QUA ✓
  ⚠️ AIOT/USDT   | Không có pending → BOT SẼ ĐẶT LỆNH
```

**Output file:**
- `debug_orders_YYYYMMDD_HHMMSS.json` - Full data để phân tích

---

### 3. `test_check_conditional_orders.py` - Test comprehensive

**Mục đích:**
- Liệt kê TẤT CẢ orders (Basic + Conditional)
- Phát hiện symbols bị lặp đơn
- Báo cáo chi tiết từng order

**Cách chạy:**
```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/qbot"

# Activate virtual environment trước
source venv/bin/activate

# Chạy test
python3 test_check_conditional_orders.py

# Sau khi xong, deactivate
deactivate
```

---

## 📊 Quy trình debug

### Bước 1: Chạy bot lần 1
```bash
# Chạy hd_order.py lần 1
python hd_order.py
```

→ Để bot chạy 1 vòng, đợi đến khi thấy "Scan Vào Lệnh" xuất hiện

→ Nhấn Ctrl+C để dừng

### Bước 2: Chạy test ngay sau đó (trong vòng 10 giây)
```bash
python test_fetch_orders_simple.py
```

**Mục đích:** Kiểm tra xem `fetch_open_orders()` có trả về orders vừa đặt không?

**Nếu thấy:**
- ✅ `algo_count > 0` → API hoạt động tốt
- ❌ `algo_count = 0` → API chưa sync, cần đợi lâu hơn

### Bước 3: Chạy test debug chi tiết
```bash
python test_debug_lap_don.py
```

**Kiểm tra:**
- File JSON output có thông tin gì?
- Logic kiểm tra có hoạt động đúng không?
- Symbols nào sẽ bị đặt lại lần sau?

### Bước 4: Chạy bot lần 2
```bash
python hd_order.py
```

→ Để bot chạy 1 vòng

→ **Quan sát:** Symbols nào được đặt lệnh?

**So sánh với kết quả Test Bước 3:**
- Nếu test dự đoán "BOT SẼ BỎ QUA" nhưng bot vẫn đặt → Có vấn đề!
- Nếu test dự đoán "BOT SẼ ĐẶT LỆNH" và bot đặt → OK!

### Bước 5: Chạy test lại để xác nhận
```bash
python test_check_conditional_orders.py
```

**Kiểm tra:**
- Có symbols nào bị lặp đơn không?
- Nếu có → Ghi lại Order ID và Algo ID

---

## 🔍 Các tình huống có thể xảy ra

### Tình huống 1: `fetch_open_orders()` TRẢ VỀ được algo orders

**Log:**
```
✅ fetch_open_orders() TRẢ VỀ ĐƯỢC ALGO ORDERS!
   Algo orders (Conditional): 6
```

**Kết luận:**
- API hoạt động tốt
- Nếu vẫn lặp đơn → Vấn đề ở logic kiểm tra hoặc timing

**Giải pháp:**
- Kiểm tra lại logic trong `has_pending_trailing_stop_order()`
- Tăng delay giữa các lần chạy (cst.delay_vao_lenh)

---

### Tình huống 2: `fetch_open_orders()` KHÔNG TRẢ VỀ algo orders

**Log:**
```
⚠️ fetch_open_orders() KHÔNG TRẢ VỀ ALGO ORDERS!
   Algo orders (Conditional): 0
   (Nhưng trên Binance UI thấy có orders trong tab Conditional)
```

**Kết luận:**
- API có delay sync
- Hoặc CCXT version cũ không hỗ trợ

**Giải pháp:**
- Tăng delay giữa các lần chạy lên 2-3 phút
- Update CCXT: `pip install --upgrade ccxt`
- Hoặc dùng API riêng để lấy algo orders

---

### Tình huống 3: Logic kiểm tra đúng nhưng vẫn lặp

**Log:**
```
Test cho thấy:
  ✅ PIPPIN/USDT | Có pending → BOT SẼ BỎ QUA ✓

Nhưng bot vẫn đặt lệnh cho PIPPIN/USDT!
```

**Kết luận:**
- Race condition: Giữa lúc check và lúc đặt có delay
- API sync chậm

**Giải pháp:**
- Tăng `cst.delay_vao_lenh` lên 120-180 giây (2-3 phút)
- Thêm delay sau mỗi lần đặt lệnh

---

## 📝 Checklist debug

- [ ] Chạy `test_fetch_orders_simple.py` để kiểm tra API trả về algo orders không
- [ ] Nếu có algo orders, kiểm tra xem có `algoId` và `algoType` không
- [ ] Chạy `test_debug_lap_don.py` để kiểm tra logic
- [ ] Xem file JSON output để phân tích chi tiết
- [ ] So sánh kết quả test với hành vi thực tế của bot
- [ ] Nếu vẫn lặp, tăng `cst.delay_vao_lenh` lên 120-180 giây
- [ ] Chạy lại và kiểm tra

---

## 💡 Tips

1. **Chạy test NGAY SAU khi bot đặt lệnh** (trong 10 giây) để kiểm tra API sync
2. **So sánh kết quả test với Binance UI** (tab Conditional) để verify
3. **Lưu lại file JSON** để phân tích sau này
4. **Nếu API delay quá lâu** → Tăng delay giữa các lần chạy

---

## 🎯 Kết luận nhanh

Sau khi chạy test, bạn sẽ biết:

1. **`fetch_open_orders()` có trả về algo orders không?**
   - Có → Logic OK, vấn đề ở timing
   - Không → Vấn đề ở API, cần dùng method khác

2. **Logic kiểm tra có đúng không?**
   - Đúng → Vấn đề ở API sync
   - Sai → Cần sửa logic

3. **Có lặp đơn không?**
   - Có → Tăng delay hoặc sửa logic
   - Không → Mọi thứ OK!

---

**Tác giả:** Claude AI  
**Ngày:** 2025-01-19
