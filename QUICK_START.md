# 🤖 QBot v2.0 - Hướng Dẫn Nhanh

## 📋 CẤU TRÚC & LOGIC

### **1. Cấu Trúc Đặt Lệnh (Google Sheets)**

#### **Sheet: "ĐẶT LỆNH (100 MÃ)"**

```
LONG Section (Hàng 55-104):
├─ A: Symbol (BTC/USDT)
├─ B: Leverage (1-125)
├─ C: Callback Rate (1%)
├─ D: Activation Price (giá kích hoạt)
├─ F: SL Rate (0.3 = 30%)
├─ G: TP Rate (0.6 = 60%)
└─ H: Capital (10 USDT)

SHORT Section (Hàng 4-53): Tương tự
```

#### **Sheet: "100 MÃ (50 TĂNG VÀ 50 GIẢM)"**

**Cập nhật bởi:** `hd_update_all.exe` (mỗi 120s)

```
A1: Timestamp (thời gian cập nhật)
B1-AN1: Headers (39 cột)
A2-AN101: Dữ liệu 100 mã

Các cột chính:
├─ A: Symbol
├─ B: % 24h
├─ C: Giá hiện tại
├─ E-I: Volume (15p, 1h, 4h, 1d, 1w)
├─ J-U: Bollinger Bands (6 khung thời gian)
├─ V-W: Biên độ tăng/giảm tuần
├─ X-Y: Max/Min 30 ngày
├─ Z-AK: Max/Min 3d, 7d, 30d (chi tiết)
├─ AL-AM: Max tăng/giảm 4h trong 60 ngày
└─ AN: Đánh dấu (🔴 TOP ĐỈNH / 🟢 TOP ĐÁY)

Tổng: 40 cột (A-AN) × 100 mã (50 giảm + 50 tăng)
```

#### **Sheet: "CHỜ VÀ KHỚP"**

**Cập nhật bởi:** `hd_update_cho_va_khop.exe` (mỗi 600s)

```
A1-A4: Metadata & Timestamp
Từ hàng 5:
├─ A: Symbol
├─ B: Order ID
├─ C: Side (BUY/SELL)
├─ D: Type (LIMIT/MARKET/STOP)
├─ E: Price
├─ F: Amount
├─ G: Status (PENDING/FILLED)
└─ H: Created Time

Điều kiện: Chỉ hiển thị symbol có đúng 1 order pending
```

#### **Sheet: "LIST" (Whitelist)**

**Đọc bởi:** Tất cả modules

```
Cột A: Symbol cho phép giao dịch
Ví dụ:
BTC/USDT
ETH/USDT
SOL/USDT
...

Logic:
- Không có trong list → KHÔNG xử lý
- Bị delist → Tự động loại bỏ
```

### **2. Flow Đặt Lệnh (Cascade Logic)**

```
Step 1: Entry (Lệnh 1a)
   ↓ TRAILING_STOP @ Activation Price
   ↓ Khớp @ Entry Price (thực tế)
   ↓
Step 2: Auto SL/TP
   ├─ SL (Lệnh 1b): Entry × (1 ± SL_rate)
   └─ TP (Lệnh 1c): Entry × (1 ± TP_rate)
```

**⚠️ QUAN TRỌNG:** SL/TP tính từ **Entry Price** (giá khớp thực tế), KHÔNG phải Activation Price!

### **3. Module Chính**

| Module | Chức Năng | Chu Kỳ |
|--------|-----------|--------|
| `hd_order.exe` | Đặt lệnh Entry (1a) | 60s |
| `hd_order_123.exe` | Tự động SL/TP (1b, 1c) | 300s |
| `hd_alert_possition_and_open_order.exe` | Monitor positions | 120s |
| `hd_update_all.exe` | Cập nhật 47+ columns data | 120s |
| `hd_update_price.exe` | Cập nhật giá | 120s |

---

## 🚀 SETUP & CHẠY

### **Bước 1: Config**

1. Copy `config.ini.example` → `config.ini`
2. Điền thông tin:

```ini
[global]
key_binance = YOUR_API_KEY
secret_binance = YOUR_SECRET_KEY
bot_token = YOUR_TELEGRAM_BOT_TOKEN
chat_id = YOUR_CHAT_ID
spreadsheet_id = YOUR_GOOGLE_SHEETS_ID
test_mode = false
```

### **Bước 2: Google Sheets API**

1. Vào https://console.cloud.google.com
2. Enable "Google Sheets API"
3. Tạo OAuth credentials (Desktop app)
4. Download `credentials.json` → Đặt cùng folder với .exe
5. Lần đầu chạy sẽ mở browser để authenticate

### **Bước 3: Chạy Bot**

**Tất cả:**
```batch
start_all_bots.bat
```

**Từng module:**
- Double-click file `.exe` tương ứng

**Dừng:**
```batch
stop_all_bots.bat
```

---

## 📊 ENTRY PRICE LOGIC (Quan Trọng!)

### **Ví Dụ Thực Tế:**

```
Sheet Activation Price: 0.01629  ← Giá để kích hoạt
        ↓
Binance Trailing Stop BUY @ 0.01629
        ↓ (Giá giảm xuống, trailing...)
        ↓
Entry Price Filled: 0.01644      ← Giá khớp THỰC TẾ
        ↓
SL/TP Calculation:
   SL = 0.01644 × 0.7  = 0.011508 ✅
   TP = 0.01644 × 1.6  = 0.026304 ✅
```

**✅ ĐÚNG:** Dùng Entry Price (0.01644)  
**❌ SAI:** Dùng Activation Price (0.01629) hoặc Current Price

---

## 🔍 KIỂM TRA

### **1. Positions**
- Binance Futures → Tab "Positions"
- Xem Entry Price khớp với log bot

### **2. Logs**
```
logs/
├─ hd_order_{timestamp}.log          ← Entry orders
├─ hd_order_123_{timestamp}.log      ← SL/TP
├─ cascade_manager.txt               ← Tính toán chi tiết
└─ order.log                         ← Tất cả orders
```

### **3. Test Scripts**
```batch
python test_all_positions.py        # Xem tất cả positions
python debug_positions.py            # Debug chi tiết
```

---

## ⚙️ CẤU HÌNH NÂNG CAO

### **Config.ini**
```ini
lenh2_rate_long = 0.3      # SL LONG (30%)
lenh2_rate_short = 0.3     # SL SHORT (30%)
lenh3_rate_long = 0.6      # TP LONG (60%)
lenh3_rate_short = 0.6     # TP SHORT (60%)
lenh3_callback_rate = 1    # TP callback (1%)
```

### **Priority:**
- **Sheet có giá trị** → Dùng Sheet
- **Sheet trống/0** → Dùng Config

---

## 🐛 XỬ LÝ LỖI

| Lỗi | Nguyên Nhân | Giải Pháp |
|-----|-------------|-----------|
| `Invalid symbol status` | Symbol không tradeable | Bot tự động bỏ qua |
| `Order would trigger` | Activation price sai logic | Bot validate và skip |
| `No section: 'Binance'` | Config sai format | Dùng `[global]` section |
| `Token expired` | Google token hết hạn | Xóa `token.json`, chạy lại |

---

## 📌 CHECKLIST

- [ ] Config.ini đã điền đủ thông tin
- [ ] credentials.json đã có (Google Sheets)
- [ ] Test mode = true (lần đầu)
- [ ] Sheet có đúng format (A=Symbol, D=Activation, H=Capital)
- [ ] API key có quyền Futures Trading
- [ ] Telegram bot đã setup

---

## 🎯 LƯU Ý

1. **Entry Price ≠ Activation Price** (do Trailing Stop)
2. **SL/TP luôn tính từ Entry Price** (giá khớp thực tế)
3. **Bot tự động skip** symbol không hợp lệ
4. **Logs ghi rõ** từng bước tính toán
5. **Test kỹ** trước khi chạy thật

---

**📞 Hỗ Trợ:**
- Xem logs trong `logs/` folder
- Check `CHECKLIST_ENTRY_PRICE_VALIDATION.md` để hiểu logic
- Run test scripts để validate

**✅ Ready!** Bot đã sẵn sàng trade với logic chính xác 100%

