# 📖 HƯỚNG DẪN CHẠY TỪNG MODULE RIÊNG

Tài liệu này hướng dẫn cách chạy từng module riêng lẻ thay vì chạy `start_all_bots`.

---

## 📋 DANH SÁCH CÁC MODULE

### **1. CRITICAL - Đặt Lệnh (Phải chạy)**

#### **hd_order.py** - Đặt Lệnh 1 (Entry)
**Chức năng:**
- Đọc trạng thái từ B2 (LONG/SHORT/STOP/CHỜ)
- Đặt lệnh TRAILING_STOP cho các mã có Leverage ≠ 0, ≠ N
- Validation: Symbol, Leverage, Activation
- Ghi log vào: `hd_order.log`, `order.log`

**Chạy:**
```bash
# Windows
python hd_order.py

# Linux/macOS
python3 hd_order.py
```

**Delay:** 60s (config: `delay_vao_lenh`)

**Dependencies:**
- `config.ini` (B2, E2)
- Google Sheet: "ĐẶT LỆNH (100 MÃ)"
- Binance API

---

#### **hd_order_123.py** - Đặt Lệnh 2 & 3 (SL/TP)
**Chức năng:**
- Monitor positions đã khớp (chưa có SL/TP)
- Tự động tạo Stop Loss (STOP_LIMIT)
- Tự động tạo Take Profit (TRAILING_STOP)
- Đọc SL/TP từ cột F, G (fallback config.ini)
- Ghi log vào: `hd_order_123.log`, `order.log`

**Chạy:**
```bash
python hd_order_123.py  # Windows
python3 hd_order_123.py # Linux/macOS
```

**Delay:** 300s (config: `delay_vao_lenh_123`)

**Dependencies:**
- `cascade_manager.py`
- `order_state_tracker.py`
- Binance API (positions, orders)

---

### **2. IMPORTANT - Cập Nhật Dữ Liệu**

#### **hd_update_all.py** - Cập Nhật Dữ Liệu Thị Trường
**Chức năng:**
- Cập nhật 50 mã tăng + 50 mã giảm vào "100 mã (50 tăng và 50 giảm)"
- Tính toán: BB, RSI, EMA, High/Low, Funding Rate
- 27 cột dữ liệu
- Ghi log vào: `hd_update_all.log`

**Chạy:**
```bash
python hd_update_all.py
```

**Delay:** 120s (config: `delay_update_all`)

**Dependencies:**
- Binance API (tickers, OHLCV)
- Google Sheet: "100 mã", "list"

---

#### **hd_update_price.py** - Cập Nhật Giá Hiện Tại
**Chức năng:**
- Đọc symbols từ "100 mã (50 tăng và 50 giảm)" (cột A)
- Cập nhật giá vào cột Y của cùng sheet
- Ghi log vào: `hd_update_price.log`

**Chạy:**
```bash
python hd_update_price.py
```

**Delay:** 120s (config: `delay_update_price`)

---

#### **hd_update_cho_va_khop.py** - Cập Nhật Trạng Thái Chờ/Khớp
**Chức năng:**
- Cập nhật sheet "Chờ và khớp"
- Thống kê orders chờ và positions
- Timestamp A4
- Ghi log vào: `hd_update_cho_va_khop.log`

**Chạy:**
```bash
python hd_update_cho_va_khop.py
```

**Delay:** 600s (config: `delay_cho_va_khop`)

---

#### **hd_track_30_prices.py** - Track 18 Mức Giá Gần Nhất
**Chức năng:**
- Track 18 giá gần nhất (nến 1m) cho mã có leverage hợp lệ
- Ghi vào cột I:Z (18 cột, bỏ qua H=Capital)
- Chỉ track mã có B ≠ 0, ≠ N
- Ghi log vào: `hd_track_30_prices.log`

**Chạy:**
```bash
python hd_track_30_prices.py
```

**Delay:** 60s (config: `delay_track_30_prices`)

---

### **3. OPTIONAL - Tiện Ích**

#### **hd_alert_possition_and_open_order.py** - Cảnh Báo Positions
**Chức năng:**
- Gửi Telegram alert về positions và open orders
- Ghi log vào: `hd_alert.log`

**Chạy:**
```bash
python hd_alert_possition_and_open_order.py
```

**Delay:** 120s (config: `delay_calert_possition_and_open_order`)

---

#### **hd_cancel_orders_schedule.py** - Hủy Lệnh Theo Lịch
**Chức năng:**
- Hủy các lệnh chờ quá thời gian
- Ghi log vào: `hd_cancel.log`

**Chạy:**
```bash
python hd_cancel_orders_schedule.py
```

**Config:** `cancel_orders_minutes`

---

#### **hd_periodic_report.py** - Báo Cáo Định Kỳ
**Chức năng:**
- Gửi Telegram báo cáo balance định kỳ
- Ghi log vào: `hd_periodic_report.log`

**Chạy:**
```bash
python hd_periodic_report.py
```

**Delay:** 300s (config: `delay_periodic_report`)

---

## 🎯 KỊCH BẢN CHẠY

### **Scenario 1: CHỈ ĐẶT LỆNH (Tối Thiểu)**

Chỉ chạy 2 module đặt lệnh:

```bash
# Terminal 1
python hd_order.py

# Terminal 2
python hd_order_123.py
```

**Kết quả:** Bot sẽ đặt lệnh và tự động tạo SL/TP, nhưng không cập nhật data.

---

### **Scenario 2: ĐẶT LỆNH + CẬP NHẬT GIÁ**

Chạy đặt lệnh + cập nhật giá realtime:

```bash
# Terminal 1 - Lệnh 1
python hd_order.py

# Terminal 2 - Lệnh 2, 3
python hd_order_123.py

# Terminal 3 - Giá hiện tại
python hd_update_price.py

# Terminal 4 - 18 giá tracking
python hd_track_30_prices.py
```

**Kết quả:** Bot đặt lệnh + cập nhật giá liên tục.

---

### **Scenario 3: FULL (Tương Đương start_all_bots)**

Chạy tất cả 9 modules:

```bash
# Hoặc dùng script
./start_all_bots.sh  # Linux/macOS
start_all_bots.bat   # Windows
```

---

## 📊 LOG FILES

Mỗi module ghi log riêng:

| Module | Log File | Nội dung |
|--------|----------|----------|
| hd_order.py | `hd_order.log`, `order.log` | Lệnh 1 (Entry) |
| hd_order_123.py | `hd_order_123.log`, `order.log` | Lệnh 2, 3 (SL/TP) |
| hd_update_all.py | `hd_update_all.log` | Data thị trường |
| hd_update_price.py | `hd_update_price.log` | Giá hiện tại |
| hd_update_cho_va_khop.py | `hd_update_cho_va_khop.log` | Trạng thái orders |
| hd_track_30_prices.py | `hd_track_30_prices.log` | 18 giá tracking |
| hd_alert... | `hd_alert.log` | Alerts |
| hd_cancel... | `hd_cancel.log` | Cancel orders |
| hd_periodic... | `hd_periodic_report.log` | Reports |
| **TẤT CẢ** | `error.log` | **TẤT CẢ LỖI** (stderr) |

---

## 🔍 XEM LOG

### **Windows:**
```bat
REM Xem log realtime
type hd_order.log

REM Xem error log
type error.log

REM Xem order log
type order.log
```

### **Linux/macOS:**
```bash
# Xem log realtime
tail -f hd_order.log

# Xem tất cả lỗi
tail -f error.log

# Xem order log
tail -f order.log
```

---

## ⚠️ LƯU Ý

1. **Config.ini:** Đảm bảo đã cấu hình đúng API keys và sheet ID
2. **Credentials:** File `credentials.json` phải có trong thư mục
3. **Dependencies:** Đã cài đặt tất cả packages (xem `requirements.txt`)
4. **Binance API:** Kiểm tra API key có quyền đặt lệnh futures
5. **Google Sheet:** Kiểm tra quyền edit cho tài khoản service
6. **Telegram Bot:** Cấu hình `bot_token` và `chat_id` trong config.ini

---

## 🛑 DỪNG MODULE

### **Windows:**
- Đóng cửa sổ CMD của module đó
- Hoặc: `Ctrl + C` trong terminal

### **Linux/macOS:**
```bash
# Tìm PID
ps aux | grep python | grep hd_

# Kill process
kill -9 <PID>

# Hoặc dùng script
./stop_all_bots.sh
```

---

## 📞 HỖ TRỢ

- **Log không hiện:** Kiểm tra `flush=True` trong print statements
- **Lỗi API:** Xem `error.log`
- **Không đặt lệnh:** Kiểm tra B2 (state), cột B (leverage)
- **SL/TP không tạo:** Kiểm tra `hd_order_123.py` có chạy không

---

**Tạo bởi:** QBot Assistant
**Ngày:** 2025-12-18
**Phiên bản:** 2.0
