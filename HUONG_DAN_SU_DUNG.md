# HƯỚNG DẪN SỬ DỤNG QBOT V2.0 📚

**Phiên bản:** 2.0  
**Ngày cập nhật:** 16/12/2025  
**Tài liệu:** Tiếng Việt

---

## 📑 MỤC LỤC

1. [Giới thiệu QBot](#giới-thiệu-qbot)
2. [Chuẩn bị trước khi bắt đầu](#chuẩn-bị-trước-khi-bắt-đầu)
3. [Setup Google Sheets](#setup-google-sheets)
4. [Setup Binance API](#setup-binance-api)
5. [Setup Telegram Bot](#setup-telegram-bot)
6. [Cấu hình config.ini](#cấu-hình-configini)
7. [Chạy bot lần đầu](#chạy-bot-lần-đầu)
8. [Cách đặt lệnh](#cách-đặt-lệnh)
9. [Logic luồng lệnh](#logic-luồng-lệnh)
10. [Lệnh quản lý hệ thống](#lệnh-quản-lý-hệ-thống)
11. [Đọc hiểu dữ liệu](#đọc-hiểu-dữ-liệu)
12. [Thông báo Telegram](#thông-báo-telegram)
13. [Xử lý sự cố](#xử-lý-sự-cố)
14. [Các câu hỏi thường gặp](#các-câu-hỏi-thường-gặp)

---

## 🎯 GIỚI THIỆU QBOT

QBot v2.0 là bot trading tự động cho Binance Futures với 3 chức năng chính:

### **1. Lấy dữ liệu thị trường** 📊
- Thu thập 47+ cột dữ liệu từ Binance
- Cập nhật vào Google Sheet "Data" tự động
- Giá real-time (dưới 1 phút)
- Volume, Bollinger Bands, High/Low lịch sử
- Đánh dấu Top 50 mã gần đỉnh/đáy

### **2. Đặt lệnh tự động** 🤖
- Đọc tín hiệu từ Google Sheet "Order"
- Đặt lệnh Entry, Stop Loss, Take Profit tự động
- Logic cascade đa lớp (1a → 1b+1c+2a → 2b+2c+3a)
- Hỗ trợ 4 loại lệnh: TRAILING_STOP, STOP_LIMIT, LIMIT, MARKET

### **3. Giám sát & Thông báo** 📱
- Monitor positions và orders real-time
- Cảnh báo qua Telegram khi có sự kiện
- Báo cáo số dư định kỳ (1h hoặc PNL thay đổi > 5%)
- 8 loại thông báo formatted

---

## 🛠️ CHUẨN BỊ TRƯỚC KHI BẮT ĐẦU

### Phần mềm cần thiết:
- ✅ Python 3.8 trở lên
- ✅ pip (Python package manager)
- ✅ Text editor (VS Code, Sublime Text...)
- ✅ Terminal/CMD

### API Keys cần có:
- ✅ Binance API Key + Secret (Futures Trading enabled)
- ✅ Google Sheets API credentials
- ✅ Telegram Bot Token + Chat ID

### Kiến thức cơ bản:
- ✅ Hiểu cách trade Futures (Long/Short, Leverage, SL/TP)
- ✅ Biết sử dụng Google Sheets cơ bản
- ✅ Biết chạy lệnh Python trong Terminal

---

## 📊 SETUP GOOGLE SHEETS

### Bước 1: Tạo Google Cloud Project

1. Truy cập [Google Cloud Console](https://console.cloud.google.com)
2. Tạo project mới: `QBot-Trading`
3. Enable **Google Sheets API**:
   - Vào "APIs & Services" → "Enable APIs and Services"
   - Tìm "Google Sheets API" → Enable

### Bước 2: Tạo Service Account

1. Vào "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "Service Account"
3. Điền tên: `qbot-service-account`
4. Bỏ qua phần "Grant this service account access to project" (optional)
5. Click "Done"

### Bước 3: Download Credentials

1. Click vào Service Account vừa tạo
2. Vào tab "Keys"
3. Click "Add Key" → "Create new key"
4. Chọn format: **JSON**
5. Download file → đổi tên thành `credentials.json`
6. Copy file vào thư mục `source04062025/`

### Bước 4: Setup Google Sheets

#### **Sheet 1: "Data" - Dữ liệu thị trường**

Cấu trúc:
```
A1: [Timestamp]
A2: Funding Rate    B2: Margin Balance    C2: Wallet Balance    D2: Unrealized PNL

Hàng 3: Tiêu đề các cột (Symbol, %24h, Price, ...)
Hàng 4: BTC/USDT (cố định)
Hàng 5: BTCDOM/USDT (cố định)
Hàng 6+: Các mã khác (tự động sắp xếp theo %24h)
```

**Lưu ý:** Sheet này bot sẽ tự động fill data, không cần điền thủ công.

#### **Sheet 2: "ĐẶT LỆNH (100 MÃ)" - Quản lý lệnh**

Cấu trúc:
```
A1: [Timestamp]         C1: RUNNING         D1: 0
A2: [API Key]           B2: [Server]

Hàng 3+: Các lệnh
```

**Các cột quan trọng:**
- **Cột A:** Tên mã (VD: ETH/USDT) - User điền
- **Cột B:** Số lớp lệnh (3) - User điền
- **Cột C-G:** Bot tự động tracking
- **Cột H:** Mã lệnh tiếp theo (1a, 2a, 1b...) - User điền
- **Cột I:** Loại lệnh (TRAILING STOP Long/Short, STOP LIMIT...) - User điền
- **Cột J:** Leverage (10, 20, 50...) - User điền
- **Cột K:** Callback % (cho Trailing Stop) - User điền
- **Cột L:** Activation Price (giá kích hoạt) - User điền
- **Cột M:** Stop Price (cho Stop Limit) - User điền
- **Cột N:** Limit Price - User điền
- **Cột O:** Vốn gốc (chưa nhân leverage) - User điền

### Bước 5: Share Sheet với Service Account

1. Copy email của Service Account (dạng: `qbot-service-account@...iam.gserviceaccount.com`)
2. Mở Google Sheet
3. Click "Share" → Paste email → Chọn quyền "Editor"
4. Click "Send" (bỏ qua thông báo email)

### Bước 6: Lấy Spreadsheet ID

URL của Google Sheet có dạng:
```
https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit
                                       ^^^^^^^^^^^^^^^^
                                       Copy phần này
```

---

## 🔑 SETUP BINANCE API

### Bước 1: Tạo API Key

1. Đăng nhập [Binance](https://www.binance.com)
2. Vào "Profile" → "API Management"
3. Click "Create API"
4. Chọn loại: **System generated**
5. Điền label: `QBot Trading`
6. Xác thực 2FA

### Bước 2: Configure API Permissions

**⚠️ QUAN TRỌNG:** Chỉ enable đúng các quyền cần thiết

✅ **Enable:**
- ✅ Enable Reading
- ✅ Enable Futures

❌ **KHÔNG enable:**
- ❌ Enable Spot & Margin Trading
- ❌ Enable Withdrawals
- ❌ Enable Internal Transfer

### Bước 3: Whitelist IP (Optional nhưng nên có)

1. Click "Edit restrictions"
2. Chọn "Restrict access to trusted IPs only"
3. Thêm IP của server chạy bot
4. Save

### Bước 4: Lưu API Key & Secret

- **API Key:** Dạng `AbCdEf123456...` (hiển thị trên Binance)
- **Secret Key:** Chỉ hiển thị 1 lần, copy ngay và lưu an toàn

**⚠️ LƯU Ý AN TOÀN:**
- Không share API Secret cho ai
- Không commit lên GitHub
- Backup ở nơi an toàn (password manager)

---

## 📱 SETUP TELEGRAM BOT

### Bước 1: Tạo Bot với BotFather

1. Mở Telegram, tìm [@BotFather](https://t.me/botfather)
2. Gửi lệnh: `/newbot`
3. Đặt tên bot: `QBot Trading`
4. Đặt username: `qbot_trading_bot` (phải kết thúc bằng `_bot`)
5. BotFather sẽ trả về **Bot Token**

**Ví dụ Bot Token:**
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Bước 2: Lấy Chat ID

#### **Option 1: Chat riêng (khuyên dùng)**

1. Tìm bot vừa tạo trên Telegram
2. Gửi message bất kỳ (VD: "Hello")
3. Truy cập URL:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```
4. Tìm `"chat":{"id":123456789,...}`
5. Copy số `123456789` (Chat ID của bạn)

#### **Option 2: Group chat**

1. Tạo group mới
2. Add bot vào group
3. Gửi message bất kỳ trong group
4. Truy cập URL như trên
5. Chat ID của group sẽ là **số âm** (VD: `-987654321`)

### Bước 3: Test Telegram Bot

Chạy lệnh sau để test:
```bash
python3 -c "
import telegram_factory
import cst
telegram_factory.send_tele('🎉 QBot Test Message', cst.chat_id, True, True)
"
```

Nếu nhận được message trên Telegram → Thành công!

---

## ⚙️ CÀI ĐẶT VÀ CẤU HÌNH

### Bước 1: Cài đặt Python dependencies

```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/source04062025"
pip3 install -r requirements.txt
```

### Bước 2: Cấu hình `config.ini`

Copy file mẫu:
```bash
cp config.ini.example config.ini
```

Mở `config.ini` và điền thông tin:

```ini
[global]
# Binance API
key_name = MyBinanceKey
key_binance = YOUR_BINANCE_API_KEY_HERE
secret_binance = YOUR_BINANCE_SECRET_HERE

# Google Sheets
spreadsheet_id = YOUR_SPREADSHEET_ID_HERE
tab_dat_lenh = ĐẶT LỆNH (100 MÃ)

# Telegram
bot_token = YOUR_BOT_TOKEN_HERE
chat_id = YOUR_CHAT_ID_HERE

# Trading Parameters
lenh2_rate_long = 0.3          # Stop Loss %
lenh2_rate_short = 0.3
lenh3_rate_long = 0.6          # Take Profit %
lenh3_rate_short = 0.6
lenh3_callback_rate = 1        # Trailing TP callback %

# Delays (seconds)
delay_vao_lenh = 60            # Entry check interval
delay_vao_lenh_123 = 300       # SL/TP check interval
delay_cho_va_khop = 600        # Status update interval
delay_calert_possition_and_open_order = 120  # Alert interval
delay_update_price = 120       # Price update interval
delay_update_all = 120         # Market data interval
delay_track_30_prices = 60     # 30 prices tracking interval
delay_periodic_report = 300    # Report interval

# Test Mode
test_mode = true   # ⚠️ Set to "false" for real trading
top_count = 50
```

**⚠️ LƯU Ý:**
- `test_mode = true`: Bot sẽ không đặt lệnh thật, chỉ log
- `test_mode = false`: Bot sẽ đặt lệnh thật trên Binance

---

## 🚀 CHẠY BOT LẦN ĐẦU

### Test Mode (An toàn)

**Bước 1:** Kiểm tra config
```bash
python3 -c "import cst; print('Config loaded:', cst.key_name)"
```

**Bước 2:** Test Data Collector
```bash
python3 test_phase3.py
```

Kiểm tra Google Sheet "Data" đã có dữ liệu chưa.

**Bước 3:** Test Entry Order (Test Mode)
```bash
python3 hd_order.py
```

Bot sẽ:
- ✅ Đọc sheet "ĐẶT LỆNH"
- ✅ Log các lệnh sẽ đặt
- ❌ KHÔNG đặt lệnh thật (vì `test_mode = true`)

**Bước 4:** Kiểm tra logs
```bash
tail -f hd_order_123.log
```

### Production Mode (Thật)

**⚠️ CẢNH BÁO:** Đây là trading với tiền thật!

**Bước 1:** Đổi config
```ini
test_mode = false
```

**Bước 2:** Start tất cả modules

**Windows:**
```bash
start_all_bots.bat
```

**Mac/Linux:**
```bash
chmod +x start_all_bots.sh
./start_all_bots.sh
```

**Bước 3:** Kiểm tra processes
```bash
# Mac/Linux
ps aux | grep python | grep hd_

# Windows: Mở Task Manager, tìm "python.exe"
```

**Bước 4:** Monitor logs
```bash
tail -f logs/hd_order.log
tail -f logs/hd_order_123.log
```

---

## 📝 CÁCH ĐẶT LỆNH

### Ví dụ 1: Lệnh Entry đơn giản (TRAILING STOP)

**Tình huống:** Muốn vào Long ETH khi giá vượt $2000, callback 1%

**Điền vào Google Sheet "ĐẶT LỆNH":**

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ETH/USDT | 3 | | | | | | 1a | TRAILING STOP Long | 10 | 1 | 2000 | | | 100 |

**Giải thích:**
- **Cột A:** ETH/USDT
- **Cột B:** 3 lớp
- **Cột H:** 1a (Entry lớp 1)
- **Cột I:** TRAILING STOP Long
- **Cột J:** Leverage 10x
- **Cột K:** Callback 1% (khi giá rút 1% từ đỉnh → khớp)
- **Cột L:** Activation Price $2000 (giá phải vượt $2000 trước)
- **Cột O:** $100 (vốn gốc, chưa nhân leverage)

**Kết quả:**
- Bot sẽ đặt lệnh TRAILING STOP MARKET Long
- Khi giá vượt $2000 → lệnh activate
- Khi giá rút 1% từ đỉnh → lệnh khớp
- Vị thế: $100 × 10 = $1000

### Ví dụ 2: Lệnh STOP LIMIT (Entry dưới giá thị trường)

**Tình huống:** Chờ BTC về $30,000 mới vào Long

**Điền vào Google Sheet:**

| A | B | H | I | J | K | L | M | N | O |
|---|---|---|---|---|---|---|---|---|---|
| BTC/USDT | 3 | 1a | STOP LIMIT Long | 20 | | | 30000 | 30100 | 200 |

**Giải thích:**
- **Cột M:** Stop Price $30,000 (khi giá chạm $30,000 → trigger)
- **Cột N:** Limit Price $30,100 (đặt lệnh mua tại $30,100)
- **Cột J:** Leverage 20x
- **Cột O:** $200 vốn → $4000 position

### Ví dụ 3: Logic cascade tự động

**Bước 1:** User điền lệnh Entry (1a)

| A | B | H | I | J | K | L | O |
|---|---|---|---|---|---|---|---|
| SOL/USDT | 3 | 1a | TRAILING STOP Long | 15 | 1 | 100 | 50 |

**Bước 2:** Lệnh 1a khớp tại $105

Bot tự động tạo 3 lệnh:
- **1b (Stop Loss):** STOP LIMIT reduce only, Stop $102.85 (cắt lỗ 3%)
- **1c (Take Profit):** TRAILING STOP reduce only, Activation $111.3 (chốt lời 6%)
- **2a (Entry lớp 2):** TRAILING STOP Long, Activation $103 (gia tầng khi về 3%)

Google Sheet tự động cập nhật:

| C | D | E | F | G |
|---|---|---|---|---|
| 2025-12-16 10:30:45 - 12345678 | 1a | TRAILING STOP Long | 15 | 105 |

**Bước 3:** Nếu 1c khớp trước (Take Profit)

Bot tự động:
- ✅ Chốt lời 6%
- ✅ Hủy lệnh 1b (không cần SL nữa)
- ✅ Hủy lệnh 2a (không gia tầng nữa)
- 📱 Gửi Telegram: "✅ LỆNH KHỚP - 1c Take Profit..."

**Bước 4:** Nếu 1b khớp trước (Stop Loss)

Bot tự động:
- ✅ Cắt lỗ 3%
- ✅ Hủy lệnh 1c (không cần TP nữa)
- ✅ GIỮ NGUYÊN lệnh 2a (vẫn có thể gia tầng)
- 📱 Gửi Telegram: "🚨 STOP LOSS TRIGGERED..."

---

## 🔄 LOGIC LUỒNG LỆNH

### Flow cơ bản (3 lớp)

```
User điền: 1a (Entry)
    ↓
Bot đặt lệnh 1a
    ↓
1a KHỚP → Bot tự động tạo:
    ├─ 1b (Stop Loss - Reduce Only)
    ├─ 1c (Take Profit - Reduce Only)
    └─ 2a (Entry lớp 2)
    ↓
┌───────────┬─────────────────┬──────────────────┐
│           │                 │                  │
│  1c khớp  │    1b khớp      │    2a khớp       │
│  (TP)     │    (SL)         │    (Entry 2)     │
│    ↓      │      ↓          │       ↓          │
│ Hủy 1b    │   Hủy 1c        │  Giữ 1b, 1c     │
│ Hủy 2a    │   Giữ 2a        │  Tạo 2b (SL)    │
│ XONG      │   Chờ 2a        │  Tạo 2c (TP)    │
│           │                 │  Tạo 3a (Entry 3)│
└───────────┴─────────────────┴──────────────────┘
```

### Quy tắc đặt tên lệnh

- **1a, 2a, 3a:** Entry (vào lệnh mới)
- **1b, 2b, 3b:** Stop Loss (cắt lỗ)
- **1c, 2c, 3c:** Take Profit (chốt lời)

### Trường hợp nhiều lớp đồng thời

**Ví dụ:**
- Lớp 1 đã vào, có 1b, 1c chờ
- 2a khớp → Lớp 2 vào, có 2b, 2c chờ
- 3a khớp → Lớp 3 vào, có 3b, 3c chờ
- **Hiện tại:** 3 lớp đang mở, 6 lệnh pending (1b,1c,2b,2c,3b,3c)

**Nếu 1c khớp (TP lớp 1):**
- ✅ Đóng lớp 1
- ✅ Hủy 1b
- ❌ KHÔNG ảnh hưởng lớp 2, 3

**Nếu 2b khớp (SL lớp 2):**
- ✅ Đóng lớp 2
- ✅ Hủy 2c
- ❌ KHÔNG ảnh hưởng lớp 1, 3

---

## ⚙️ LỆNH QUẢN LÝ HỆ THỐNG

### 1. XÓA CHỜ (Cancel All Pending Orders)

**Mục đích:** Hủy tất cả lệnh chờ, giữ nguyên vị thế đang mở

**Cách dùng:**
1. Vào Google Sheet "ĐẶT LỆNH"
2. Đổi ô **C1** thành: `XÓA CHỜ`
3. Bot sẽ:
   - ✅ Hủy tất cả lệnh pending trên Binance
   - ✅ Giữ nguyên positions đang mở
   - ✅ Gửi Telegram xác nhận
   - ✅ Đổi C1 về `RUNNING`

**Khi nào dùng:**
- Thị trường biến động bất thường
- Muốn tạm dừng đặt lệnh mới
- Cần chỉnh sửa chiến lược

### 2. XÓA VỊ THẾ (Close All Positions)

**Mục đích:** Đóng tất cả vị thế, giữ lệnh chờ

**Cách dùng:**
1. Đổi ô **C1** thành: `XÓA VỊ THẾ`
2. Bot sẽ:
   - ✅ Đóng tất cả positions bằng lệnh MARKET
   - ✅ Giữ nguyên lệnh chờ
   - ✅ Gửi Telegram xác nhận
   - ✅ Đổi C1 về `RUNNING`

**⚠️ CẢNH BÁO:**
- Lệnh này đóng bằng MARKET → có thể bị slippage
- Nên dùng khi thị trường biến động mạnh

### 3. STOP (Stop Bot Completely)

**Mục đích:** Dừng hoàn toàn bot, đóng tất cả

**Cách dùng:**
1. Đổi ô **C1** thành: `STOP`
2. Bot sẽ:
   - ✅ Đóng tất cả positions
   - ✅ Hủy tất cả lệnh chờ
   - ✅ Gửi báo cáo cuối cùng qua Telegram
   - ✅ Dừng bot

**⚠️ LƯU Ý:**
- Đây là lệnh nguy hiểm nhất
- Chỉ dùng khi đạt mục tiêu lãi/lỗ
- Sau STOP, cần restart bot thủ công

### 4. RUNNING (Normal Mode)

**Mặc định:** Bot chạy bình thường

- Đặt lệnh mới nếu có điều kiện
- Monitor positions và orders
- Cập nhật dữ liệu
- Gửi thông báo

---

## 📊 ĐỌC HIỂU DỮ LIỆU

### Sheet "Data" - Thông tin tài khoản (Ô A1-D2)

| | A | B | C | D |
|---|---|---|---|---|
| 1 | 2025-12-16 10:30:45 | | | |
| 2 | Funding: 0.01% | Margin: 5,234.56 | Wallet: 5,000.00 | Unrealized: +234.56 |

**Giải thích:**
- **A1:** Thời gian cập nhật
- **A2:** Funding Rate (phí định kỳ Long/Short)
- **B2:** Margin Balance (bao gồm PNL)
- **C2:** Wallet Balance (số dư gốc)
- **D2:** Unrealized PNL (lãi/lỗ chưa chốt)

### Sheet "Data" - Dữ liệu thị trường (Hàng 3+)

**47+ cột dữ liệu:**

#### Cột 1-4: Thông tin cơ bản
1. Symbol (ETH/USDT)
2. %24h (+5.23%)
3. Price ($2,100.50)
4. ~~Listing Date~~ (skipped)

#### Cột 5-9: Volume
5. Volume 15m
6. Volume 1h
7. Volume 4h
8. Volume 1d
9. Volume 1w

#### Cột 10-35: Bollinger Bands (6 timeframes)
- Mỗi timeframe có: Upper, Lower, Max Up, Max Down

#### Cột 36-47: High/Low lịch sử
- 3 ngày: High, High Time, Low, Low Time
- 7 ngày: High, High Time, Low, Low Time
- 30 ngày: High, High Time, Low, Low Time

#### Cột 48-49: ~~Chênh lệch kích hoạt~~ (skipped)

### Markers đặc biệt

- **🔴 (Red Circle):** Top 50 mã gần đỉnh 30 ngày
- **🟢 (Green Circle):** Top 50 mã gần đáy 30 ngày

**Công thức:**
```python
Distance to high = (price - high_30d) / high_30d * 100
Distance to low = (price - low_30d) / low_30d * 100

Top 50 near high: những mã có distance_to_high nhỏ nhất
Top 50 near low: những mã có distance_to_low nhỏ nhất
```

### Tracking 30 mức giá (Cột H-AK cho mã có lệnh)

**Ví dụ:** ETH/USDT có lệnh đang chờ

Cột H-AK sẽ chứa 30 giá gần nhất (mỗi phút 1 điểm):
```
H: 2100.50  I: 2101.20  J: 2099.80  ...  AK: 2105.30
```

**Mục đích:** Phân tích biến động giá sau khi đặt lệnh

---

## 📱 THÔNG BÁO TELEGRAM

### 1. ✅ Lệnh khớp (Order Filled)

```
✅ LỆNH KHỚP

🔹 Mã: ETH/USDT
🔹 Lệnh: 1a - TRAILING STOP Long
🔹 Giá vào: $2,105.50
🔹 Leverage: 10x
🔹 Vốn: $100 → Position: $1,000
🔹 Thời gian: 2025-12-16 10:30:45

📋 Lệnh tiếp theo đã tạo:
  • 1b (Stop Loss): $2,042.34
  • 1c (Take Profit): $2,231.83
  • 2a (Entry lớp 2): $2,073.41
```

### 2. 🚨 Lỗi đặt lệnh (Order Error)

```
🚨 LỖI ĐẶT LỆNH

🔹 Mã: BTC/USDT
🔹 Lệnh: 2a
🔹 Lỗi: -4120
🔹 Chi tiết: Order type not supported
🔹 Hành động: Chuyển sang Algo API
🔹 Thời gian: 2025-12-16 10:30:45
```

### 3. ⛔ API bị chặn

```
⛔ BINANCE BLOCKED

🔹 API: MyKey_***3456
🔹 Mã: XAI/USDT
🔹 Lý do: Symbol suspended
🔹 Retry sau: 10 phút
🔹 Thời gian: 2025-12-16 10:30:45
```

### 4. 📊 Báo cáo số dư

```
📊 BÁO CÁO SỐ DƯ

💰 Wallet Balance: $5,000.00
💰 Margin Balance: $5,234.56
📈 Unrealized PNL: +$234.56 (+4.69%)

📍 Vị thế đang mở: 3
📋 Lệnh chờ: 6

🕐 Thời gian: 2025-12-16 10:30:45
```

**Tần suất:**
- Mỗi 1 giờ
- Hoặc khi PNL thay đổi > 5%
- Hoặc bot khởi động

### 5. 🛑 Kích hoạt STOP

```
🛑 LỆNH STOP KÍCH HOẠT

⚠️ Trạng thái: Đang xử lý...

📍 Vị thế đang mở: 3
📋 Lệnh chờ: 6
💰 PNL hiện tại: +$234.56

🕐 Thời gian: 2025-12-16 10:30:45
```

### 6. ✅ Hoàn tất STOP

```
✅ HOÀN TẤT STOP

✅ Đã đóng: 3 positions
✅ Đã hủy: 6 lệnh

💰 Số dư cuối: $5,234.56
📊 Tổng lãi: +$234.56

🕐 Thời gian: 2025-12-16 10:31:00
```

### 7. ⚠️ Reduce Only sót

```
⚠️ REDUCE ONLY SÓT

🔹 Mã: SOL/USDT
🔹 Số lệnh sót: 2
🔹 Order IDs:
  • 12345678
  • 12345679

⚙️ Trạng thái: Đang retry lần 2/3

🕐 Thời gian: 2025-12-16 10:30:45
```

### 8. 🔴 Cảnh báo nghiêm trọng

```
🔴 CẢNH BÁO NGHIÊM TRỌNG

⚠️ Vấn đề: Không thể xóa lệnh Reduce Only sau 3 lần retry

🔹 Mã: XAI/USDT
🔹 Order ID: 12345678
🔹 Loại lệnh: STOP_LIMIT reduce only

❗ YÊU CẦU: Can thiệp thủ công ngay

🕐 Thời gian: 2025-12-16 10:30:45
```

---

## 🛠️ XỬ LÝ SỰ CỐ

### Lỗi 1: Bot không chạy

**Triệu chứng:** Chạy `./start_all_bots.sh` nhưng không có process nào

**Giải pháp:**
```bash
# 1. Kiểm tra Python
python3 --version

# 2. Kiểm tra dependencies
pip3 list | grep ccxt

# 3. Chạy thử 1 module
python3 hd_order.py
# Xem lỗi gì và fix
```

### Lỗi 2: Google Sheets API Error

**Triệu chứng:**
```
gspread.exceptions.APIError: PERMISSION_DENIED
```

**Giải pháp:**
1. Kiểm tra `credentials.json` đúng thư mục
2. Share sheet với Service Account email
3. Enable Google Sheets API
4. Thử lại sau 5 phút (API có thể delay)

### Lỗi 3: Binance API -4120

**Triệu chứng:**
```
{"code":-4120,"msg":"Order type not supported..."}
```

**Giải pháp:**
- ✅ Đã fix trong v2.0
- Bot tự động chuyển sang Algo API
- Nếu vẫn lỗi → Kiểm tra API key có quyền Futures

### Lỗi 4: Telegram không nhận message

**Triệu chứng:** Bot chạy nhưng không có thông báo Telegram

**Giải pháp:**
```bash
# Test Telegram
python3 -c "
import telegram_factory, cst
telegram_factory.send_tele('Test', cst.chat_id, True, True)
"
```

Nếu fail:
1. Kiểm tra `bot_token` đúng
2. Kiểm tra `chat_id` đúng (số âm nếu group)
3. Bot có bị block không? → Unblock

### Lỗi 5: Lệnh Reduce Only không xóa được

**Triệu chứng:** Sau TP/SL khớp, vẫn còn lệnh reduce only sót lại

**Giải pháp:**
- ✅ Đã fix trong v2.0 với retry mechanism
- Bot sẽ retry 3 lần
- Nếu vẫn fail → nhận cảnh báo 🔴 → xóa thủ công trên Binance

### Lỗi 6: Bot dừng giữa chừng

**Triệu chứng:** Process chết sau vài giờ chạy

**Giải pháp:**
```bash
# Kiểm tra logs
tail -n 100 logs/hd_order.log

# Tìm lỗi cuối cùng và fix
# Thường là:
# - Network timeout
# - API rate limit
# - Memory leak (restart định kỳ)
```

**Setup auto-restart với cron (Linux/Mac):**
```bash
crontab -e

# Thêm dòng (kiểm tra mỗi 5 phút):
*/5 * * * * cd /path/to/source04062025 && ./check_and_restart.sh
```

---

## ❓ CÁC CÂU HỎI THƯỜNG GẶP

### Q1: Bot có thể chạy 24/7 không?

**A:** Có, nhưng cần:
- Server/VPS ổn định
- Internet không gián đoạn
- Monitor định kỳ (ít nhất 1 ngày/lần)

### Q2: Tôi có thể chạy nhiều bot cùng lúc không?

**A:** Có, nhưng:
- Mỗi bot cần 1 `config.ini` riêng
- Mỗi bot nên có 1 API key riêng (tránh rate limit)
- Dùng nhiều Google Sheet riêng

### Q3: Leverage tối đa nên dùng bao nhiêu?

**A:** Khuyến nghị:
- Newbie: 5-10x
- Experienced: 10-20x
- Professional: 20-50x
- ⚠️ Không nên > 50x (rủi ro thanh lý cao)

### Q4: Có thể thay đổi Stop Loss / Take Profit % không?

**A:** Có, trong `config.ini`:
```ini
lenh2_rate_long = 0.3    # SL: 3%
lenh3_rate_long = 0.6    # TP: 6%
```

Hoặc điền trực tiếp vào Google Sheet (cột M, N).

### Q5: Bot có hỗ trợ Spot trading không?

**A:** Không, chỉ hỗ trợ Binance Futures.

### Q6: Tôi có thể dừng bot giữa chừng không?

**A:** Có:
```bash
./stop_all_bots.sh
```

Hoặc đổi C1 = `STOP` (sẽ đóng tất cả trước khi dừng).

### Q7: Nếu quên mật khẩu Service Account thì sao?

**A:** Service Account không có mật khẩu, chỉ cần file `credentials.json`. Nếu mất file → tạo Service Account mới.

### Q8: Bot có tự động take profit một phần không?

**A:** Hiện tại chưa, TP luôn đóng 100% position. Có thể bổ sung sau (v2.1).

### Q9: Làm sao biết bot đang chạy đúng?

**A:** Kiểm tra:
- ✅ Telegram nhận báo cáo định kỳ
- ✅ Google Sheet "Data" cập nhật liên tục
- ✅ Logs không có ERROR

### Q10: Tôi nên backup gì?

**A:** Backup:
- `config.ini`
- `credentials.json`
- Logs (định kỳ)
- Google Sheet (export)

---

## 📈 MẸO VÀ THỰC HÀNH TỐT

### 1. Quản lý rủi ro
- ✅ Mỗi lệnh rủi ro tối đa 1-2% tài khoản
- ✅ Không vào quá 3 lệnh cùng lúc (nếu mới)
- ✅ Luôn có Stop Loss
- ✅ Không tham lam với TP

### 2. Chọn mã
- ✅ Ưu tiên mã thanh khoản cao (BTC, ETH, BNB...)
- ✅ Tránh mã mới niêm yết (biến động khó lường)
- ✅ Kiểm tra Funding Rate (tránh mã funding quá cao)

### 3. Thời điểm vào lệnh
- ✅ Tránh vào lệnh khi:
  - Tin tức lớn sắp ra (FOMC, CPI...)
  - Funding settlement (mỗi 8h)
  - Volume thấp bất thường
- ✅ Nên vào lệnh khi:
  - Thị trường ổn định
  - Có tín hiệu rõ ràng
  - Volume tốt

### 4. Monitor và điều chỉnh
- ✅ Kiểm tra bot mỗi ngày (ít nhất)
- ✅ Review logs 1 tuần/lần
- ✅ Điều chỉnh SL/TP dựa trên kết quả
- ✅ Backup config mỗi khi có thay đổi lớn

### 5. Tâm lý
- ✅ Đừng panic khi lỗ (SL đã định sẵn)
- ✅ Đừng tham khi lãi (TP đã định sẵn)
- ✅ Tin tưởng hệ thống (đã test kỹ)
- ✅ Sẵn sàng học hỏi và cải thiện

---

## 🎓 HỌC THÊM

### Tài liệu tham khảo:
- **QBot.md:** Requirements đầy đủ
- **QUICK_CHECKLIST.md:** Progress tracking
- **PHASE3_READINESS.md:** Phase 3 setup
- **README.md:** Technical documentation

### Binance Docs:
- [Futures API](https://binance-docs.github.io/apidocs/futures/en/)
- [Algo Order API](https://binance-docs.github.io/apidocs/futures/en/#new-order-using-stp-trade)
- [Trailing Stop Guide](https://www.binance.com/en/support/faq/trailing-stop-order-guide-360042299292)

### Google Sheets API:
- [Python Quickstart](https://developers.google.com/sheets/api/quickstart/python)
- [gspread Documentation](https://docs.gspread.org/)

### Telegram Bot:
- [Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot](https://python-telegram-bot.org/)

---

## 📞 HỖ TRỢ

**Vấn đề kỹ thuật:**
- Kiểm tra logs: `logs/`
- Xem `TROUBLESHOOTING_*.md`
- Tạo issue với đầy đủ logs và config (đã che API keys)

**Góp ý và yêu cầu tính năng mới:**
- Tham khảo `QBot.md` section 7 (Questions)
- Liên hệ team dev

---

## ⚠️ DISCLAIMER

- **Rủi ro tài chính:** Trading Futures là rủi ro cao, có thể mất toàn bộ vốn
- **Không đảm bảo lợi nhuận:** Bot chỉ là công cụ, không đảm bảo kiếm tiền
- **Tự chịu trách nhiệm:** Mọi quyết định trading là của bạn
- **Test kỹ trước:** Luôn dùng `test_mode = true` và Binance Testnet trước
- **Backup thường xuyên:** Config, logs, và Google Sheet
- **Monitor liên tục:** Đặc biệt trong giai đoạn đầu (1-2 tuần)
- **Kill switch:** Luôn biết cách dừng bot khẩn cấp

---

## 📄 PHIÊN BẢN

- **v2.0 (16/12/2025):** 
  - ✅ 100% core features
  - ✅ Cascade logic
  - ✅ Data collection 47+ columns
  - ✅ 8 Telegram notifications
  - ✅ Fix critical bugs

- **v1.0 (trước đây):**
  - Basic order placement
  - Simple monitoring

---

**QBot v2.0 - Trading Thông Minh, Tự Động, An Toàn** 🚀

*Chúc bạn trading thành công!* 💰

---

*Tài liệu được viết bởi QBot Dev Team*  
*Cập nhật lần cuối: 16/12/2025*

