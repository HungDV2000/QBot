# PHASE 3: DATA COLLECTION - READINESS CHECK ✅

## 📊 TỔNG QUAN

Phase 3 đã được implement **81.8% (9/11 items)**. Dưới đây là checklist đầy đủ để bạn chuẩn bị và chạy thử.

---

## ✅ CODE ĐÃ SẴN SÀNG

### 1. **Modules mới đã tạo:**
- ✅ `data_collector.py` (406 dòng) - Thu thập dữ liệu mở rộng
- ✅ `hd_track_30_prices.py` (170 dòng) - Tracking 30 mức giá
- ✅ `hd_update_all.py` (đã update) - Tích hợp data collector

### 2. **Chức năng đã implement:**
- ✅ Funding Rate (Ô A2)
- ✅ Volume 5 khung (15m, 1h, 4h, 1d, 1w)
- ✅ Bollinger Bands 6 khung (15m, 1h, 4h, 1d, 1w, 1M)
- ✅ Biên độ tăng/giảm theo timeframe
- ✅ Giá cao/thấp 3, 7, 30 ngày + timestamp
- ✅ Đánh dấu Top 50 mã gần đỉnh/đáy
- ✅ Tracking 30 mức giá mỗi phút

### 3. **Linter Status:**
- ✅ Không có lỗi linter trong tất cả files Phase 3

---

## ⚙️ CẤU HÌNH CẦN BỔ SUNG

### 1. **Update `config.ini`**

Thêm 2 biến mới vào cuối file:

```ini
# Phase 3: Data Collection
delay_track_30_prices = 60        # 60 giây = 1 phút (tracking giá)
delay_periodic_report = 300       # 300 giây = 5 phút (báo cáo)
```

**File `config.ini` sau khi update:**
```ini
[global]

max_increase_decrease_4h_day_count = 60

lenh2_rate_long = 0.3
lenh2_rate_short = 0.3
lenh3_rate_long = 0.6
lenh3_rate_short = 0.6

lenh3_callback_rate =1
cancel_orders_minutes = 1

is_print_mode = false
top_count= 50
time_gap_do_it = 0
bot_token = 8431813976:AAHtvnWT3ZTLvtgqlaqYOgyQW-l0bVBwqbI
chat_id =  -4654774917

key_name = MAXBirkinCatwin1Pub
key_binance = wtle9sYIRbYyIkSL4PcHTdErzxiSFnk2WGx7AlE0zl4rGy2aE3d185ci4bFzLRUw
secret_binance = IsCzruesnSmnkh2wV5zB5kA3ZChiKAORDiezWY0B5Wj9730KdcQIuOnHDJQ1azHp

spreadsheet_id = 12Jm6lPdYcLysR6ZyrdFVaPZz3y1sS7nniNLHDdeXtaQ
test_mode = false

tab_dat_lenh = ĐẶT LỆNH (100 MÃ)

delay_vao_lenh = 60
delay_vao_lenh_123 = 300
delay_cho_va_khop = 600
delay_calert_possition_and_open_order = 120
delay_update_price = 120
delay_update_all = 120

# Phase 3: Data Collection (THÊM MỚI)
delay_track_30_prices = 60
delay_periodic_report = 300
```

### 2. **Update `cst.py`**

Thêm 2 dòng vào cuối file (sau dòng 33):

```python
# Phase 3 delays
delay_track_30_prices = config.getint('global', 'delay_track_30_prices')
delay_periodic_report = config.getint('global', 'delay_periodic_report')
```

---

## 📋 GOOGLE SHEETS CẦN CHUẨN BỊ

### Sheet "100 mã (50 tăng và 50 giảm)" - DATA SHEET

**Cấu trúc cột mới (thêm vào sau các cột hiện có):**

| Cột | Tên | Mô tả |
|-----|-----|-------|
| **Cột 4** | Listing Date | Thời điểm niêm yết (để trống - không có API) |
| **Cột 5-9** | Volume 15m/1h/4h/1d/1w | Volume 5 khung thời gian |
| **Cột 10+** | Bollinger Bands | 6 khung × 2 giá trị = 12 cột (upper/lower) |
| **Cột 22+** | High/Low + Timestamp | 3 periods × 4 values = 12 cột |
| **Cột cuối** | Top 50 Marker | 🔴 TOP ĐỈNH / 🟢 TOP ĐÁY |

**Tổng cộng:** Thêm **~30 cột mới**

### Sheet "ĐẶT LỆNH (100 MÃ)" - ORDER SHEET

**30 cột tracking giá (H → AK):**
- Mỗi mã có lệnh sẽ có 30 mức giá gần nhất
- Cột H = giá 30 phút trước
- Cột AK = giá hiện tại
- Cập nhật mỗi phút

---

## 🚀 CÁCH CHẠY THỬ

### **Bước 1: Update config**
```bash
# 1. Mở config.ini
# 2. Thêm 2 dòng:
delay_track_30_prices = 60
delay_periodic_report = 300
# 3. Lưu file
```

### **Bước 2: Update cst.py**
```bash
# 1. Mở cst.py
# 2. Thêm 2 dòng cuối file:
delay_track_30_prices = config.getint('global', 'delay_track_30_prices')
delay_periodic_report = config.getint('global', 'delay_periodic_report')
# 3. Lưu file
```

### **Bước 3: Test từng module riêng lẻ**

#### 3.1. Test Data Collector (console test)
```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/source04062025"
python3 -c "
from data_collector import get_data_collector
import ccxt
import cst

exchange = ccxt.binance({
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {'defaultType': 'future'}
})

collector = get_data_collector(exchange)

# Test Funding Rate
fr = collector.get_funding_rate('BTC/USDT')
print(f'Funding Rate: {fr}%')

# Test Volume
vols = collector.get_volumes_multi_timeframe('BTC/USDT')
print(f'Volumes: {vols}')

# Test High/Low
high, high_ts, low, low_ts = collector.get_high_low_with_timestamp('BTC/USDT', 7)
print(f'High 7d: {high}, Low 7d: {low}')
"
```

#### 3.2. Test hd_update_all.py (chạy 1 lần)
```bash
python3 hd_update_all.py
# Kiểm tra:
# - Sheet "100 mã" có cập nhật dữ liệu mới không
# - Có funding rate ở ô A2 không
# - Có Top 50 markers không
```

#### 3.3. Test hd_track_30_prices.py (chạy 1 phút)
```bash
python3 hd_track_30_prices.py
# Ctrl+C sau 2-3 phút
# Kiểm tra:
# - Sheet "ĐẶT LỆNH" cột H→AK có giá không
# - Chỉ tracking các mã có lệnh
```

#### 3.4. Test hd_periodic_report.py (chạy 5 phút)
```bash
python3 hd_periodic_report.py
# Ctrl+C sau 6-7 phút
# Kiểm tra:
# - Telegram có nhận báo cáo số dư không
# - Báo cáo có đúng format không
```

### **Bước 4: Chạy tất cả modules**

#### Trên Windows:
```bash
start_all_bots.bat
```

#### Trên Mac/Linux:
```bash
./start_all_bots.sh
```

**Lưu ý:** Cần update script `start_all_bots` để thêm 2 modules mới:
- `hd_track_30_prices.py`
- `hd_periodic_report.py`

---

## ⚠️ 2 TASKS CHƯA HOÀN THÀNH

### 1. ❌ **Thời điểm niêm yết (SKIP)**
**Lý do:** Binance không cung cấp API  
**Giải pháp:** Để trống cột hoặc dùng CoinGecko API (nếu cần)

### 2. ❓ **Chênh lệch giá kích hoạt LONG/SHORT (CẦN LÀM RÕ)**
**Vấn đề:** Công thức chưa rõ từ QBot.md  
**Cần user trả lời:**
- "Giá kích hoạt" là cột nào trong sheet?
- "Đáy/Đỉnh gần nhất" là trong bao nhiêu ngày?
- Công thức tính: phần trăm hay giá trị tuyệt đối?

**Đề xuất logic mặc định:**
```python
# Cột 48: Chênh lệch LONG (%)
long_diff = ((activation_price_long - low_30d) / low_30d) * 100

# Cột 49: Chênh lệch SHORT (%)  
short_diff = ((high_30d - activation_price_short) / high_30d) * 100
```

Nếu đồng ý với logic này, tôi sẽ implement ngay.

---

## 📦 DEPENDENCIES

**Đã có sẵn trong `requirements.txt`:**
```
ccxt
gspread
oauth2client
pandas
numpy
python-telegram-bot
configparser
```

✅ Không cần cài thêm package nào!

---

## 🔍 KIỂM TRA NHANH

### Checklist trước khi chạy:
- [ ] Đã update `config.ini` (2 biến mới)
- [ ] Đã update `cst.py` (2 dòng cuối)
- [ ] Google Sheets đã có đủ cột cho dữ liệu mới
- [ ] Binance API key còn hoạt động
- [ ] Telegram bot token còn hoạt động
- [ ] Internet connection ổn định

### Nếu gặp lỗi:
1. **ImportError:** Kiểm tra `requirements.txt` và reinstall
2. **Config Error:** Kiểm tra lại syntax trong `config.ini`
3. **Google Sheets Error:** Kiểm tra credentials và spreadsheet_id
4. **Binance API Error:** Kiểm tra API key, rate limits
5. **Telegram Error:** Kiểm tra bot_token và chat_id

---

## 🎯 KẾT LUẬN

**Phase 3 đã sẵn sàng 81.8%!**

**Cần làm ngay:**
1. ✅ Update `config.ini` (2 phút)
2. ✅ Update `cst.py` (1 phút)
3. ✅ Test từng module (15-20 phút)
4. ✅ Chạy tất cả modules (ongoing)

**Có thể bỏ qua:**
- ⚠️ Thời điểm niêm yết (không có API)
- ❓ Chênh lệch giá kích hoạt (chờ user làm rõ)

**Sẵn sàng chạy production sau khi test thành công!** 🚀

---

*Cập nhật: 16/12/2025*

