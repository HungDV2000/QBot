# 🔍 HƯỚNG DẪN KIỂM TRA DỮ LIỆU VỚI BINANCE

## 📋 Mục lục
1. [Kiểm tra Giá và % 24h](#1-kiểm-tra-giá-và--24h)
2. [Kiểm tra Volume](#2-kiểm-tra-volume)
3. [Kiểm tra Bollinger Bands](#3-kiểm-tra-bollinger-bands)
4. [Kiểm tra High/Low](#4-kiểm-tra-highlow)
5. [Tools test nhanh](#5-tools-test-nhanh)

---

## 1️⃣ Kiểm tra Giá và % 24h

### 📊 Cột kiểm tra:
- **Cột B**: % 24h
- **Cột C**: Giá trị hiện thời

### 🌐 Cách kiểm tra trên Binance:

#### **Cách 1: Binance Web**
1. Truy cập: https://www.binance.com/en/futures/BTCUSDT
2. Thay `BTCUSDT` bằng mã cần kiểm tra
3. So sánh:
   - **Giá**: Góc trên bên trái
   - **% 24h**: Bên cạnh giá (xanh = tăng, đỏ = giảm)

#### **Cách 2: API Test**
```bash
curl "https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=BTCUSDT"
```

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "lastPrice": "42150.50",      // Cột C
  "priceChangePercent": "2.15", // Cột B
  "volume": "12345.67"
}
```

#### **Cách 3: Python**
```python
import ccxt
exchange = ccxt.binance({'options': {'defaultType': 'future'}})
ticker = exchange.fetch_ticker('BTC/USDT:USDT')
print(f"Giá: {ticker['last']}")
print(f"% 24h: {ticker['percentage']}")
```

### ✅ Tiêu chí: Sai lệch < 0.5 USDT và < 0.1%

---

## 2️⃣ Kiểm tra Volume

### 📊 Cột kiểm tra:
- **E**: Vol 15p | **F**: Vol 1h | **G**: Vol 4h | **H**: Vol 1 ngày | **I**: Vol 1 tuần

### 🌐 Cách kiểm tra:

#### **Binance Web + TradingView**
1. Mở chart: https://www.binance.com/en/futures/BTCUSDT
2. Chọn timeframe (15m, 1h, 4h, 1d, 1w)
3. Xem thanh Volume phía dưới chart

#### **API Test**
```bash
curl "https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=1"
```

**Response:** Array `[timestamp, open, high, low, close, volume, closeTime, quoteVolume, ...]`
- Index 7 = **quoteVolume** (USDT) ← Đây là Volume trong sheet

#### **Python**
```python
ohlcv = exchange.fetch_ohlcv('BTC/USDT:USDT', '1h', limit=1)
volume = ohlcv[0][5]  # Base volume
print(f"Vol 1h: {volume}")
```

### ✅ Tiêu chí: Sai lệch < 5%

---

## 3️⃣ Kiểm tra Bollinger Bands

### 📊 Cột kiểm tra:
- **J-K**: BB15p | **L-M**: BB1h | **N-O**: BB4h | **P-Q**: BB1d | **R-S**: BB1w | **T-U**: BB1M

### 🌐 Cách kiểm tra:

#### **TradingView**
1. Mở chart Binance
2. Thêm indicator: **Bollinger Bands** (period=20, stdDev=2)
3. Chọn timeframe (15m, 1h, 4h, 1d, 1w, 1M)
4. Đọc giá trị:
   - **Upper Band** = BB trên
   - **Lower Band** = BB dưới

#### **Python**
```python
import pandas as pd
import numpy as np

ohlcv = exchange.fetch_ohlcv('BTC/USDT:USDT', '1h', limit=100)
df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])

# Tính BB
df['sma'] = df['c'].rolling(20).mean()
df['std'] = df['c'].rolling(20).std()
df['bb_upper'] = df['sma'] + 2 * df['std']
df['bb_lower'] = df['sma'] - 2 * df['std']

print(f"BB1h trên: {df['bb_upper'].iloc[-1]}")
print(f"BB1h dưới: {df['bb_lower'].iloc[-1]}")
```

### ✅ Tiêu chí: Sai lệch < 1 USDT

---

## 4️⃣ Kiểm tra High/Low

### 📊 Cột kiểm tra:
- **X-Y**: Max/Min 30 ngày
- **Z, AB**: Max/Min 3 ngày
- **AD, AF**: Max/Min 7 ngày
- **AH, AJ**: Max/Min 30 ngày chi tiết

### 🌐 Cách kiểm tra:

#### **TradingView**
1. Chọn timeframe **1D** (1 ngày)
2. Zoom để xem 30 nến
3. Dùng tool **Measure (M)**: Kéo từ đáy → đỉnh

#### **Python**
```python
ohlcv = exchange.fetch_ohlcv('BTC/USDT:USDT', '1d', limit=3)
highs = [candle[2] for candle in ohlcv]
lows = [candle[3] for candle in ohlcv]
print(f"Max 3 ngày: {max(highs)}")
print(f"Min 3 ngày: {min(lows)}")
```

### ✅ Tiêu chí: Sai lệch < 0.5 USDT

---

## 5️⃣ Tools test nhanh

### 🛠️ Python Test Script

Tạo file `test_data.py`:

```python
import ccxt
import pandas as pd
import numpy as np

exchange = ccxt.binance({'options': {'defaultType': 'future'}})

def test_all(symbol):
    print(f"\n{'='*50}")
    print(f"KIỂM TRA: {symbol}")
    print(f"{'='*50}")
    
    # 1. Ticker
    ticker = exchange.fetch_ticker(symbol)
    print(f"\n📊 TICKER:")
    print(f"  Giá: {ticker['last']}")
    print(f"  % 24h: {ticker['percentage']}")
    
    # 2. Volume
    for tf in ['15m', '1h', '4h', '1d']:
        ohlcv = exchange.fetch_ohlcv(symbol, tf, limit=1)
        vol = ohlcv[0][5]
        print(f"  Vol {tf}: {vol}")
    
    # 3. BB
    ohlcv = exchange.fetch_ohlcv(symbol, '1h', limit=100)
    df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
    df['sma'] = df['c'].rolling(20).mean()
    df['std'] = df['c'].rolling(20).std()
    df['bb_upper'] = df['sma'] + 2 * df['std']
    df['bb_lower'] = df['sma'] - 2 * df['std']
    print(f"\n🔵 BOLLINGER BANDS 1H:")
    print(f"  BB trên: {df['bb_upper'].iloc[-1]:.2f}")
    print(f"  BB dưới: {df['bb_lower'].iloc[-1]:.2f}")
    
    # 4. High/Low
    for days in [3, 7, 30]:
        ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=days)
        highs = [c[2] for c in ohlcv]
        lows = [c[3] for c in ohlcv]
        print(f"\n📈 HIGH/LOW {days} NGÀY:")
        print(f"  Max: {max(highs):.2f}")
        print(f"  Min: {min(lows):.2f}")

# Test
test_all('BTC/USDT:USDT')
```

**Chạy:**
```bash
python test_data.py
```

---

## 🔄 Workflow kiểm tra

```
1. Chọn ngẫu nhiên 1 mã trong sheet
   ↓
2. So sánh Giá + % 24h với Binance
   ↓
3. Kiểm tra Volume trên chart
   ↓
4. Kiểm tra BB với TradingView indicator
   ↓
5. Đo High/Low với Measure tool
   ↓
6. Chấp nhận nếu sai lệch < ngưỡng
```

---

## ⚠️ Lưu ý

### Dữ liệu sai lệch lớn?
- Mã bị delist/halt
- API rate limit
- Thị trường biến động mạnh
→ Kiểm tra log: `hd_update_all.log`

### Cột trống?
- **AA, AC, AE, AG, AI, AK**: Cố ý trống (tối ưu hóa)
- Cột khác: Kiểm tra log, chạy lại script

---

**File liên quan:**
- `hd_update_all.py` - Script chính
- `data_collector.py` - Hàm lấy dữ liệu
- `gg_sheet_factory.py` - Hàm ghi sheet

**Cập nhật**: 2025-12-17
