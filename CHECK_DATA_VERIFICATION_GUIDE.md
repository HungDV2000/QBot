# 🔍 HƯỚNG DẪN KIỂM TRA DỮ LIỆU VỚI BINANCE

## 📋 Mục lục
1. [Kiểm tra Giá và % 24h](#1-kiểm-tra-giá-và--24h)
2. [Kiểm tra Volume](#2-kiểm-tra-volume)
3. [Kiểm tra Bollinger Bands](#3-kiểm-tra-bollinger-bands)
4. [Kiểm tra High/Low](#4-kiểm-tra-highlow)
5. [Kiểm tra Biên độ](#5-kiểm-tra-biên-độ)
6. [Kiểm tra Account Balance](#6-kiểm-tra-account-balance)
7. [Tools hữu ích](#7-tools-hữu-ích)

---

## 1️⃣ Kiểm tra Giá và % 24h

### 📊 Cột kiểm tra:
- **Cột B**: % 24h
- **Cột C**: Giá trị hiện thời

### 🌐 Trên Binance Futures:

#### **Cách 1: Web UI**
1. Truy cập: https://www.binance.com/en/futures/BTCUSDT
2. Thay `BTCUSDT` bằng mã cần kiểm tra (VD: `ETHUSDT`, `SOLUSDT`)
3. Kiểm tra:
   - **Giá**: Hiển thị ở góc trên bên trái
   - **% 24h**: Hiển thị bên cạnh giá (màu xanh = tăng, đỏ = giảm)

#### **Cách 2: API Test**
```bash
# Lấy ticker 24h của BTC/USDT
curl "https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=BTCUSDT"
```

**Response mẫu:**
```json
{
  "symbol": "BTCUSDT",
  "lastPrice": "42150.50",      // ← Cột C: Giá trị hiện thời
  "priceChangePercent": "2.15", // ← Cột B: % 24h
  "volume": "12345.67",
  "quoteVolume": "520123456.78"
}
```

#### **Cách 3: Python Test Script**
```python
import ccxt

exchange = ccxt.binance({'options': {'defaultType': 'future'}})
ticker = exchange.fetch_ticker('BTC/USDT:USDT')

print(f"Giá: {ticker['last']}")           # Cột C
print(f"% 24h: {ticker['percentage']}")   # Cột B
```

### ✅ Tiêu chí đạt:
- Giá sai lệch < 0.5 USDT
- % 24h sai lệch < 0.1%

---

## 2️⃣ Kiểm tra Volume

### 📊 Cột kiểm tra:
- **Cột E**: Vol 15p
- **Cột F**: Vol 1h
- **Cột G**: Vol 4h
- **Cột H**: Vol 1 ngày
- **Cột I**: Vol 1 tuần

### 🌐 Trên Binance Futures:

#### **Cách 1: Web UI + TradingView**
1. Truy cập: https://www.binance.com/en/futures/BTCUSDT
2. Mở chart TradingView
3. Thay đổi timeframe (15m, 1h, 4h, 1d, 1w)
4. Di chuột vào nến cuối cùng → xem Volume (thanh màu xanh/đỏ phía dưới)

#### **Cách 2: API Test**
```bash
# Lấy OHLCV của BTC/USDT - Khung 1h
curl "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=1"
```

**Response mẫu:**
```json
[
  [
    1702809600000,      // Open time
    "42100.00",         // Open
    "42200.00",         // High
    "42050.00",         // Low
    "42150.00",         // Close (giá)
    "12345.67",         // Volume (coin)
    1702813199999,      // Close time
    "520123456.78",     // Quote asset volume (USDT) ← Đây là Volume cột F-I
    1234,               // Number of trades
    "6789.12",          // Taker buy base asset volume
    "286543210.12",     // Taker buy quote asset volume
    "0"
  ]
]
```

#### **Cách 3: Python Test**
```python
import ccxt

exchange = ccxt.binance({'options': {'defaultType': 'future'}})

# Cột F: Vol 1h
ohlcv_1h = exchange.fetch_ohlcv('BTC/USDT:USDT', '1h', limit=1)
volume_1h = ohlcv_1h[0][5]  # Index 5 = volume
print(f"Vol 1h: {volume_1h}")

# Cột H: Vol 1 ngày
ohlcv_1d = exchange.fetch_ohlcv('BTC/USDT:USDT', '1d', limit=1)
volume_1d = ohlcv_1d[0][5]
print(f"Vol 1 ngày: {volume_1d}")
```

### ⚠️ Lưu ý:
- Volume trong sheet là **Quote Volume (USDT)**, không phải Base Volume (Coin)
- API trả về `ohlcv[5]` là volume trong **base asset** → Cần nhân với giá để ra USDT

### ✅ Tiêu chí đạt:
- Volume sai lệch < 5% (do thời điểm lấy dữ liệu khác nhau)

---

## 3️⃣ Kiểm tra Bollinger Bands

### 📊 Cột kiểm tra:
- **Cột J-K**: BB15p trên/dưới
- **Cột L-M**: BB1h trên/dưới
- **Cột N-O**: BB4h trên/dưới
- **Cột P-Q**: BB1 ngày trên/dưới
- **Cột R-S**: BB1 tuần trên/dưới
- **Cột T-U**: BB1 tháng trên/dưới

### 🌐 Trên Binance Futures:

#### **Cách 1: Web UI + TradingView**
1. Truy cập: https://www.binance.com/en/futures/BTCUSDT
2. Mở chart TradingView
3. Thêm indicator: **Bollinger Bands** (Settings: period=20, stdDev=2)
4. Thay đổi timeframe (15m, 1h, 4h, 1d, 1w, 1M)
5. Đọc giá trị BB:
   - **Upper Band** = BB trên (màu xanh)
   - **Lower Band** = BB dưới (màu đỏ)
   - **Middle Band** = SMA(20)

#### **Cách 2: Python Test**
```python
import ccxt
import pandas as pd
import numpy as np

exchange = ccxt.binance({'options': {'defaultType': 'future'}})

# Lấy OHLCV 1h
ohlcv = exchange.fetch_ohlcv('BTC/USDT:USDT', '1h', limit=100)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Tính BB
period = 20
std_dev = 2
df['sma'] = df['close'].rolling(window=period).mean()
df['std'] = df['close'].rolling(window=period).std()
df['bb_upper'] = df['sma'] + (std_dev * df['std'])
df['bb_lower'] = df['sma'] - (std_dev * df['std'])

# Giá trị BB cuối cùng
print(f"BB1h trên: {df['bb_upper'].iloc[-1]}")  # Cột L
print(f"BB1h dưới: {df['bb_lower'].iloc[-1]}")  # Cột M
```

#### **Cách 3: TradingView Script**
```javascript
//@version=5
indicator("BB Check", overlay=true)
[middle, upper, lower] = ta.bb(close, 20, 2)
plot(upper, "Upper", color=color.blue)
plot(lower, "Lower", color=color.red)
plot(middle, "Middle", color=color.orange)

// Di chuột vào nến cuối → xem giá trị upper/lower
```

### ✅ Tiêu chí đạt:
- BB Upper sai lệch < 1 USDT
- BB Lower sai lệch < 1 USDT

---

## 4️⃣ Kiểm tra High/Low

### 📊 Cột kiểm tra:
- **Cột X-Y**: Max/Min 30 ngày (cũ)
- **Cột Z, AB**: Max/Min 3 ngày
- **Cột AD, AF**: Max/Min 7 ngày
- **Cột AH, AJ**: Max/Min 30 ngày (chi tiết)

### 🌐 Trên Binance Futures:

#### **Cách 1: Web UI**
1. Truy cập: https://www.binance.com/en/futures/BTCUSDT
2. Mở chart TradingView
3. Chọn timeframe **1 ngày (1D)**
4. Zoom out để xem 30 nến (30 ngày)
5. Dùng công cụ **Measure** (M) để đo High/Low:
   - Kéo từ đáy → đỉnh trong 3 ngày cuối
   - Kéo từ đáy → đỉnh trong 7 ngày cuối
   - Kéo từ đáy → đỉnh trong 30 ngày cuối

#### **Cách 2: API Test**
```bash
# Lấy OHLCV 3 ngày (1d timeframe)
curl "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1d&limit=3"
```

**Response**: Mảng 3 nến, mỗi nến có `high` và `low`

#### **Cách 3: Python Test**
```python
import ccxt

exchange = ccxt.binance({'options': {'defaultType': 'future'}})

# Lấy OHLCV 3 ngày
ohlcv = exchange.fetch_ohlcv('BTC/USDT:USDT', '1d', limit=3)

highs = [candle[2] for candle in ohlcv]  # Index 2 = high
lows = [candle[3] for candle in ohlcv]   # Index 3 = low

print(f"Max 3 ngày: {max(highs)}")  # Cột Z
print(f"Min 3 ngày: {min(lows)}")   # Cột AB
```

### ✅ Tiêu chí đạt:
- High/Low sai lệch < 0.5 USDT

---

## 5️⃣ Kiểm tra Biên độ

### 📊 Cột kiểm tra:
- **Cột V**: Biên độ 1h max tăng tuần (7 ngày)
- **Cột W**: Biên độ 1h max giảm tuần (7 ngày)
- **Cột AL**: Max tăng 4h/60 ngày
- **Cột AM**: Max giảm 4h/60 ngày

### 🔢 Công thức tính:
```python
# Biên độ tăng = ((high - low) / low) * 100
# Biên độ giảm = ((high - low) / high) * 100

# VD: Trong 7 ngày (khung 1h = 168 nến)
ohlcv_1h = exchange.fetch_ohlcv('BTC/USDT:USDT', '1h', limit=168)
for candle in ohlcv_1h:
    increase = ((candle[2] - candle[3]) / candle[3]) * 100
    decrease = ((candle[2] - candle[3]) / candle[2]) * 100
    
max_increase = max(all_increases)  # Cột V
max_decrease = max(all_decreases)  # Cột W
```

### 🌐 Trên TradingView:

#### **Cách 1: Measure Tool**
1. Chọn timeframe **1h**
2. Zoom để xem 7 ngày (168 nến)
3. Dùng **Measure** (M):
   - Kéo từ low → high của nến có biên độ lớn nhất
   - TradingView tự tính % change

#### **Cách 2: Custom Indicator**
```javascript
//@version=5
indicator("Amplitude Check")
amp_pct = ((high - low) / low) * 100
plot(amp_pct, "Amplitude %", color=color.blue)
label.new(bar_index, amp_pct, str.tostring(amp_pct, "#.##%"), style=label.style_label_down)
```

### ✅ Tiêu chí đạt:
- Biên độ sai lệch < 0.5%

---

## 6️⃣ Kiểm tra Account Balance

### 📊 Vị trí: Không có trong sheet hiện tại
*(Có thể xuất hiện ở các sheet khác như "Chờ và khớp")*

### 🌐 Trên Binance Futures:

#### **Cách 1: Web UI**
1. Login vào Binance
2. Vào **Futures** → **Wallet**
3. Kiểm tra:
   - **Total Margin Balance**: Số dư ký quỹ
   - **Total Wallet Balance**: Số dư ví
   - **Total Unrealized PnL**: Lãi/lỗ chưa chốt

#### **Cách 2: API Test**
```bash
# Cần API Key + Secret
curl -X GET "https://fapi.binance.com/fapi/v2/account" \
  -H "X-MBX-APIKEY: YOUR_API_KEY" \
  --data "timestamp=1702809600000&signature=YOUR_SIGNATURE"
```

#### **Cách 3: Python Test**
```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'YOUR_API_KEY',
    'secret': 'YOUR_SECRET',
    'options': {'defaultType': 'future'}
})

balance = exchange.fetch_balance()
print(f"Total Margin: {balance['info']['totalMarginBalance']}")
print(f"Total Wallet: {balance['info']['totalWalletBalance']}")
print(f"Total PnL: {balance['info']['totalCrossUnPnl']}")
```

### ✅ Tiêu chí đạt:
- Balance sai lệch < 0.01 USDT

---

## 7️⃣ Tools hữu ích

### 🛠️ Binance API Explorer
- **URL**: https://binance-docs.github.io/apidocs/futures/en/
- **Tính năng**: Test API trực tiếp trên web
- **Hướng dẫn**:
  1. Chọn endpoint (VD: `/fapi/v1/ticker/24hr`)
  2. Nhập params (VD: `symbol=BTCUSDT`)
  3. Click "Try it out" → Xem response

### 🛠️ Postman Collection
- **Import**: https://github.com/binance/binance-api-postman
- **Tính năng**: Collection đầy đủ các endpoint Binance
- **Lợi ích**: Test nhanh, save history

### 🛠️ Python Interactive Test
```python
# File: test_binance_data.py
import ccxt
import pandas as pd

exchange = ccxt.binance({'options': {'defaultType': 'future'}})

def test_ticker(symbol):
    ticker = exchange.fetch_ticker(symbol)
    print(f"\n=== {symbol} ===")
    print(f"Giá: {ticker['last']}")
    print(f"% 24h: {ticker['percentage']}")
    print(f"High 24h: {ticker['high']}")
    print(f"Low 24h: {ticker['low']}")

def test_volume(symbol, timeframe):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=1)
    volume = ohlcv[0][5]
    print(f"\nVol {timeframe}: {volume}")

def test_bb(symbol, timeframe):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
    df['sma'] = df['c'].rolling(20).mean()
    df['std'] = df['c'].rolling(20).std()
    df['bb_upper'] = df['sma'] + 2 * df['std']
    df['bb_lower'] = df['sma'] - 2 * df['std']
    print(f"\nBB {timeframe} trên: {df['bb_upper'].iloc[-1]}")
    print(f"BB {timeframe} dưới: {df['bb_lower'].iloc[-1]}")

# Test
test_ticker('BTC/USDT:USDT')
test_volume('BTC/USDT:USDT', '1h')
test_bb('BTC/USDT:USDT', '1h')
```

**Chạy:**
```bash
python test_binance_data.py
```

### 🛠️ Google Sheets Add-on: CRYPTOFINANCE
- **Install**: https://cryptofinance.ai/
- **Tính năng**: Lấy dữ liệu crypto trực tiếp trong Google Sheets
- **Công thức**:
```excel
=CRYPTOFINANCE("BINANCE:BTCUSDT", "price")
=CRYPTOFINANCE("BINANCE:BTCUSDT", "change24h")
=CRYPTOFINANCE("BINANCE:BTCUSDT", "volume24h")
```

---

## 🔄 Workflow kiểm tra toàn diện

```
1. Chọn 1 mã ngẫu nhiên trong sheet (VD: BTC/USDT)
   ↓
2. Kiểm tra Giá + % 24h (Binance Web UI)
   ↓
3. Kiểm tra Volume (TradingView chart)
   ↓
4. Kiểm tra BB (TradingView indicator)
   ↓
5. Kiểm tra High/Low (TradingView measure)
   ↓
6. So sánh với dữ liệu trong sheet
   ↓
7. Chấp nhận nếu sai lệch < ngưỡng cho phép
```

---

## ⚠️ Các trường hợp đặc biệt

### 🔸 Dữ liệu sai lệch lớn (> 5%)
**Nguyên nhân có thể:**
- Mã bị delist hoặc đang tạm dừng giao dịch
- API rate limit → bot không lấy được dữ liệu mới
- Thời điểm lấy dữ liệu khác nhau (thị trường biến động mạnh)

**Cách xử lý:**
1. Kiểm tra log file: `hd_update_all.log`
2. Kiểm tra trạng thái API: https://www.binance.com/en/support/announcement
3. Chạy lại script thủ công để update

### 🔸 Cột trống (no data)
**Nguyên nhân:**
- Mã mới niêm yết, chưa đủ lịch sử (VD: < 30 ngày cho cột "Max 30 ngày")
- API timeout hoặc lỗi
- Đã tối ưu hóa performance (VD: cột timestamp)

**Cách xử lý:**
- Cột AA, AC, AE, AG, AI, AK: **Cố ý để trống** (tối ưu hóa)
- Các cột khác: Kiểm tra log, chạy lại script

### 🔸 Marker không hiển thị (🔴/🟢)
**Nguyên nhân:**
- Mã không thuộc top 50 gần đỉnh/đáy
- Logic phân tích không đủ điều kiện

**Cách xử lý:**
- Kiểm tra logic trong `hd_update_all.py` (line 512-517)
- Mã chỉ có marker nếu thuộc `top_50_near_high` hoặc `top_50_near_low`

---

## 📞 Hỗ trợ

**File liên quan:**
- `hd_update_all.py` - Script chính update sheet "100 mã"
- `data_collector.py` - Các hàm lấy dữ liệu từ Binance
- `gg_sheet_factory.py` - Các hàm ghi vào Google Sheets

**Log files:**
- `hd_update_all.log` - Log lỗi khi chạy script
- Terminal output - Xem realtime khi chạy `python -u hd_update_all.py`

---

**Cập nhật lần cuối**: 2025-12-17
**Version**: 1.0
