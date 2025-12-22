# 🚀 HƯỚNG DẪN CHẠY BOT

File này hướng dẫn cách chạy từng chức năng của bot một cách đơn giản.

---

## 📦 BƯỚC 1: VÀO VIRTUAL ENVIRONMENT

```bash
# Activate venv
source venv/bin/activate

# Kiểm tra Python version (nên dùng python3)
python3 --version
```

**Lưu ý:** Mỗi terminal mới cần activate venv lại.

---

## 🎯 BƯỚC 2: CHẠY CÁC CHỨC NĂNG

### **1. ĐẶT LỆNH 1 (Entry Order)**
```bash
python3 hd_order.py
```
**Chức năng:** Đặt lệnh TRAILING_STOP (Entry) từ sheet "ĐẶT LỆNH (100 MÃ)"

---

### **2. ĐẶT LỆNH 2 & 3 (SL/TP)**
```bash
python3 hd_order_123.py
```
**Chức năng:** Tự động tạo Stop Loss và Take Profit khi position khớp

---

### **3. CẬP NHẬT DỮ LIỆU THỊ TRƯỜNG**
```bash
python3 hd_update_all.py
```
**Chức năng:** Cập nhật 100 mã (50 tăng + 50 giảm) với các chỉ số kỹ thuật

---

### **4. CẬP NHẬT GIÁ HIỆN TẠI**
```bash
python3 hd_update_price.py
```
**Chức năng:** Cập nhật giá realtime vào sheet "100 mã"

---

### **5. TRACK 18 MỨC GIÁ**
```bash
python3 hd_track_30_prices.py
```
**Chức năng:** Track 18 giá gần nhất (nến 1m) cho các mã có leverage

---

### **6. CẬP NHẬT TRẠNG THÁI CHỜ/KHỚP**
```bash
python3 hd_update_cho_va_khop.py
```
**Chức năng:** Cập nhật sheet "Chờ và khớp" với thống kê orders và positions

---

### **7. CẢNH BÁO POSITIONS & ORDERS**
```bash
python3 hd_alert_possition_and_open_order.py
```
**Chức năng:** Gửi Telegram alert về positions và open orders

---

### **8. HỦY LỆNH THEO LỊCH**
```bash
python3 hd_cancel_orders_schedule.py
```
**Chức năng:** Hủy các lệnh chờ quá thời gian (theo config)

---

### **9. BÁO CÁO ĐỊNH KỲ**
```bash
python3 hd_periodic_report.py
```
**Chức năng:** Gửi Telegram báo cáo balance định kỳ

---

### **10. CHUYỂN ĐỔI ISOLATED/CROSSED**
```bash
python3 hd_isolated_crossed_converter.py
```
**Chức năng:** Chuyển đổi margin mode cho positions

---

## 📋 CHẠY TẤT CẢ (Nếu có script)

```bash
# Chạy tất cả modules cùng lúc
./start_all_bots.sh
```

---

## 🔍 XEM LOG

```bash
# Xem log realtime
tail -f hd_order.log

# Xem tất cả lỗi
tail -f error.log

# Xem order log
tail -f order.log
```

---

## 🛑 DỪNG BOT

Nhấn `Ctrl + C` trong terminal đang chạy bot.

---

## ⚙️ CẤU HÌNH

Tất cả cấu hình trong file `config.ini`:
- API keys (Binance)
- Sheet ID (Google Sheets)
- Telegram bot token
- Các delay/interval

---

## 📝 GHI CHÚ

- **Mỗi terminal cần activate venv:** `source venv/bin/activate`
- **Dùng python3:** Tất cả lệnh dùng `python3`
- **Log files:** Mỗi module có log riêng, tất cả lỗi ghi vào `error.log`
- **Order logs:** `hd_order.py` và `hd_order_123.py` ghi vào `order.log`

---

**Tạo:** 2025-12-19  
**Dùng cho:** Python 3.x
