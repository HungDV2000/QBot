# CHECKLIST NÂNG CẤP QBOT LÊN PHIÊN BẢN 2.0

**Ngày tạo:** 14/12/2025  
**Source hiện tại:** MVP v1.0  
**Target:** QBot v2.0 (theo QBot.md)

---

## TỔNG QUAN ĐÁNH GIÁ

| Mục | Tình trạng | Ghi chú |
|-----|------------|---------|
| **Tỷ lệ hoàn thành hiện tại** | ~40-50% | Source code có thể chạy nhưng thiếu nhiều tính năng |
| **Kiến trúc tổng thể** | ✅ Tốt | Kiến trúc modular, dễ mở rộng |
| **Core features** | ⚠️ Cơ bản | Entry + SL/TP tự động hoạt động |
| **Advanced features** | ❌ Thiếu | Flow đa lớp, tracking, error handling nâng cao |

---

## PHẦN 1: MODULE LẤY DỮ LIỆU (SHEET DATA)

### 1.1 Thông tin tài khoản
- [x] ✅ **Có sẵn:** Lấy Margin Balance, Wallet Balance, Unrealized PNL
  - File: `hd_update_all.py` (dòng 525-528)
  - Ghi vào: Hàng 1-2 của sheet
- [ ] ⚠️ **Cần bổ sung:** Funding Rate
  - Hiện tại: Chưa lấy
  - Cần: Fetch funding rate từ Binance API
  - Ghi vào: Ô A2
- [x] ✅ **Có sẵn:** Timestamp cập nhật
  - Ghi vào: Ô A1

**Action Items:**
```python
# TODO: Thêm vào hd_update_all.py
def get_funding_rate(symbol):
    funding_rate = exchange.fetch_funding_rate(symbol)
    return funding_rate['fundingRate']
```

---

### 1.2 Cấu trúc dữ liệu các mã
- [x] ✅ **Có sẵn:** BTC và BTCDOM ở vị trí cố định
  - File: `hd_update_all.py` (dòng 472-473)
  - List: `["BTC/USDT:USDT", "BTCDOM/USDT:USDT"]`
- [x] ✅ **Có sẵn:** Sắp xếp theo % 24h
  - Top 50 giảm + Top 50 tăng
  - File: `hd_update_all.py` (dòng 481-482)
- [ ] ⚠️ **Cần cải thiện:** Header row (hàng 3)
  - Hiện tại: Không có header rõ ràng
  - Cần: Thêm tên cột đầy đủ

---

### 1.3 Danh sách 47+ cột dữ liệu

#### Nhóm 1: Thông tin cơ bản (4 cột)
- [x] ✅ Tên cặp mã
- [x] ✅ % thay đổi 24h
- [x] ✅ Giá hiện tại (cập nhật < 1 phút)
  - File: `hd_update_price.py` - Chạy mỗi 2 phút
- [ ] ❌ Thời điểm niêm yết
  - **Status:** Chưa có
  - **Action:** Fetch từ `exchange.fetch_markets()`, field `info.listingDate`

#### Nhóm 2: Khối lượng giao dịch (5 cột)
- [ ] ❌ Volume 15 phút
- [ ] ❌ Volume 1 giờ
- [ ] ❌ Volume 4 giờ
- [ ] ❌ Volume 1 ngày
- [ ] ❌ Volume 1 tuần
  - **Status:** Có code mẫu ở dòng 344-365 của `hd_update_all.py` nhưng không dùng
  - **Action:** Kích hoạt function `get_volumes()` và tích hợp vào flow chính

**Code cần kích hoạt:**
```python
# Đã có function get_volumes() nhưng chưa gọi trong get_row_result()
# TODO: Thêm vào get_row_result():
volumes = get_volumes(symbol)
row.append(volumes['15m']['volume'])
row.append(volumes['1h']['volume'])
# ... thêm các timeframe khác
```

#### Nhóm 3-8: Bollinger Bands (nhiều khung thời gian)
- [x] ✅ **Có sẵn:** BB 1h, 1d (upper, lower)
  - File: `hd_update_all.py`, dòng 418
  - Function: `get_bb()` dòng 241-269
- [ ] ⚠️ **Thiếu:** BB 15m, 4h, 1w, 1M
  - **Action:** Thêm timeframes vào function `get_bb()`
  
```python
# TODO: Mở rộng trong get_row_result()
result_bb_array = get_bb(pair, timeframes=['15m', '1h', '4h', '1d', '1w', '1M'])
```

#### Nhóm 9: Biên độ dao động
- [x] ✅ **Có sẵn:** Max increase/decrease 7 ngày khung 1h
  - File: `hd_update_all.py`, dòng 423-435
  - Function: `calculate_price_range()`
- [ ] ⚠️ **Cần bổ sung:** Các khung thời gian khác (15m, 4h, 1d, 1w, 1M)
  - Hiện có function nhưng chưa gọi đủ
  - **Action:** Gọi thêm cho các timeframe còn lại

#### Nhóm 10: Giá cao/thấp lịch sử (12 cột)
- [x] ⚠️ **Có một phần:** High/Low 40 ngày
  - File: `hd_update_all.py`, dòng 457-462
  - Function: `calculate_high_low_30d()` (dòng 196-211)
- [ ] ❌ **Thiếu:** Thời điểm đạt giá cao/thấp
  - Hiện tại: Chỉ có giá, không có timestamp
  - **Action:** Modify function để return cả timestamp

```python
# TODO: Cải thiện calculate_high_low_30d()
def calculate_high_low_with_timestamp(pair, timeframe='1d'):
    # ... existing code ...
    highest_idx = df['high'].idxmax()
    lowest_idx = df['low'].idxmin()
    highest_time = df.loc[highest_idx, 'timestamp']
    lowest_time = df.loc[lowest_idx, 'timestamp']
    return highest_price, highest_time, lowest_price, lowest_time
```

- [ ] ❌ **Thiếu:** Giá cao/thấp cho 3 ngày, 7 ngày, 30 ngày riêng biệt
  - **Action:** Tạo 3 functions cho 3 khoảng thời gian

#### Nhóm 11: Biên độ tăng/giảm 4h
- [x] ✅ **Có sẵn:** Max increase/decrease 4h
  - File: `hd_update_all.py`, dòng 465-467
  - Function: `calculate_max_increase_decrease_4h()`

#### Nhóm 12: Chênh lệch giá kích hoạt (2 cột)
- [ ] ❌ **Chưa có:** Chênh lệch giá kích hoạt LONG với đáy
- [ ] ❌ **Chưa có:** Chênh lệch giá kích hoạt SHORT với đỉnh
  - **Status:** Không có trong code hiện tại
  - **Action:** Cần làm rõ logic tính toán với user
  - **Question:** Giá kích hoạt lấy từ đâu? (Từ sheet đặt lệnh?)

---

### 1.4 Tính năng đặc biệt

#### 1.4.1 Top 50 mã cực trị
- [x] ⚠️ **Có một phần:** Sắp xếp Top 50 tăng/giảm
  - File: `hd_update_all.py`, dòng 481-490
- [ ] ❌ **Thiếu:** Đánh dấu mã gần giá cao/thấp 30 ngày
  - Yêu cầu: Highlight các mã có giá hiện tại gần high/low 30d
  - **Action:** Thêm logic so sánh và format cell trong sheet

```python
# TODO: Thêm vào get_row_result()
high_30d, low_30d = calculate_high_low_30d(symbol)
current_price = price
distance_to_high = abs(current_price - high_30d) / high_30d * 100
distance_to_low = abs(current_price - low_30d) / low_30d * 100

# Đánh dấu nếu gần high/low (< 5%)
marker = ""
if distance_to_high < 5:
    marker = "🔴 GẦN ĐỈNH"
elif distance_to_low < 5:
    marker = "🟢 GẦN ĐÁY"
```

#### 1.4.2 Tracking 30 mức giá
- [ ] ❌ **Chưa có:** Lưu 30 mức giá gần nhất cho lệnh đã đặt
  - **Yêu cầu:**
    - Lưu giá đặt lệnh
    - Lưu giá khớp lệnh
    - Lưu 30 điểm giá (mỗi phút 1 điểm)
  - **Status:** Không có trong code hiện tại
  - **Action:** Tạo module mới hoặc thêm vào `hd_update_cho_va_khop.py`

```python
# TODO: Tạo file mới hd_track_30_prices.py
# Hoặc thêm vào hd_update_cho_va_khop.py

from collections import deque

price_history = {}  # {symbol: deque(maxlen=30)}

def track_prices():
    # Đọc danh sách mã đang có lệnh/vị thế
    symbols = get_active_symbols()
    
    for symbol in symbols:
        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']
        
        if symbol not in price_history:
            price_history[symbol] = deque(maxlen=30)
        
        price_history[symbol].append({
            'timestamp': datetime.now(),
            'price': price
        })
    
    # Ghi vào Google Sheet
    update_price_history_to_sheet(price_history)
```

---

## PHẦN 2: MODULE ĐẶT LỆNH (SHEET ORDER)

### 2.1 Cấu trúc Sheet Order

#### Header (Hàng 1-2)
- [ ] ⚠️ **Cần cải thiện:** Thông tin header
  - Hiện tại: Đọc B2 và E2 cho trạng thái
  - Yêu cầu: Thêm A1 (timestamp), C1 (trạng thái hệ thống), D1 (số mã đạt điều kiện)
  - File cần sửa: `hd_order.py`, dòng 102-104

#### Cấu trúc cột tracking (Bot cập nhật)
- [ ] ❌ **Chưa có:** Cột B - Số lớp lệnh
- [ ] ❌ **Chưa có:** Cột C - Lệnh vừa khớp (timestamp + Order ID)
- [ ] ❌ **Chưa có:** Cột D - Mã lệnh hiện tại (1a, 1b, 1c...)
- [ ] ❌ **Chưa có:** Cột E - Loại lệnh hiện tại
- [ ] ❌ **Chưa có:** Cột F - Đòn bẩy đã khớp
- [ ] ❌ **Chưa có:** Cột G - Giá vào đã khớp

**Status:** Code hiện tại không có logic tracking như yêu cầu  
**Action:** Cần refactor toàn bộ module đặt lệnh

---

### 2.2 Các loại lệnh

#### Lệnh Entry (vào vị thế)
- [x] ✅ **Có sẵn:** TRAILING_STOP Long/Short
  - File: `hd_order.py`, dòng 199-262
  - Sử dụng: `TRAILING_STOP_MARKET`
- [ ] ❌ **Thiếu:** STOP_LIMIT Long/Short
- [ ] ❌ **Thiếu:** LIMIT Long/Short  
- [ ] ⚠️ **Có nhưng chỉ dùng thủ công:** MARKET Long/Short
  - Chỉ dùng trong lệnh STOP (đóng toàn bộ)

**Action:** Thêm logic đọc loại lệnh từ sheet và xử lý tương ứng

```python
# TODO: Thêm vào hd_order.py
def create_order_by_type(symbol, order_type, side, amount, params):
    if order_type == "TRAILING_STOP":
        return exchange.create_order(symbol, 'TRAILING_STOP_MARKET', side, amount, None, params)
    elif order_type == "STOP_LIMIT":
        return exchange.create_order(symbol, 'STOP', side, amount, params['limitPrice'], {
            'stopPrice': params['stopPrice']
        })
    elif order_type == "LIMIT":
        return exchange.create_order(symbol, 'LIMIT', side, amount, params['limitPrice'])
    elif order_type == "MARKET":
        return exchange.create_order(symbol, 'MARKET', side, amount)
```

#### Lệnh Reduce Only (đóng vị thế)
- [x] ⚠️ **Có một phần:** TRAILING_STOP (reduce only)
  - File: `hd_order_123.py`, dòng 203-218
  - Dùng cho Take Profit (Lệnh 3)
- [x] ⚠️ **Có một phần:** STOP (reduce only)
  - File: `hd_order_123.py`, dòng 158-180
  - Dùng cho Stop Loss (Lệnh 2)
- [ ] ❌ **Thiếu:** LIMIT (reduce only)
  - Dùng cho Take Profit cố định

---

### 2.3 Lệnh quản lý hệ thống

- [x] ⚠️ **Có một phần:** Lệnh STOP
  - File: `hd_order.py`, dòng 106-144
  - Chức năng: Đóng tất cả vị thế
  - **Vấn đề:** Không hủy lệnh chờ, không dừng bot
  
- [ ] ❌ **Chưa có:** Lệnh XÓA CHỜ
  - Yêu cầu: Hủy tất cả lệnh pending, giữ vị thế
  - **Action:** Thêm xử lý khi C1 = "XÓA CHỜ"

```python
# TODO: Thêm vào hd_order.py trong do_it()
elif b2_value == "XÓA CHỜ":
    print("Hủy tất cả lệnh chờ, giữ vị thế")
    open_orders = exchange.fetch_open_orders()
    for order in open_orders:
        exchange.cancel_order(order['id'], order['symbol'])
    telegram_factory.send_tele("✅ Đã hủy tất cả lệnh chờ", cst.chat_id, True, True)
```

- [ ] ❌ **Chưa có:** Lệnh XÓA VỊ THẾ
  - Yêu cầu: Đóng tất cả positions, giữ lệnh chờ
  - **Action:** Thêm xử lý khi C1 = "XÓA VỊ THẾ"

- [ ] ❌ **Chưa có:** Lệnh hủy đơn lẻ
  - Yêu cầu: Hủy 1 lệnh chờ theo Order ID
  
- [ ] ❌ **Chưa có:** Lệnh đóng vị thế đơn lẻ
  - Yêu cầu: Đóng vị thế 1 mã cụ thể

---

## PHẦN 3: LOGIC LUỒNG LỆNH

### 3.1 Flow cơ bản - 1 lớp
- [x] ✅ **Có sẵn:** Lệnh Entry (1a)
  - File: `hd_order.py`
- [x] ✅ **Có sẵn:** Tự động tạo Stop Loss (1b) + Take Profit (1c)
  - File: `hd_order_123.py`
- [ ] ❌ **Thiếu:** Tự động tạo Entry lớp 2 (2a) sau khi 1a khớp

**Status:** Code chỉ tạo 1b + 1c, không tạo 2a  
**File cần sửa:** `hd_order_123.py`

---

### 3.2 Flow đa lớp - Cascade logic

- [ ] ❌ **Chưa có:** Logic tạo lệnh cascade (1a → 1b+1c+2a → 2b+2c+3a)
  - **Yêu cầu:**
    - Khi 1a khớp → Tạo 1b, 1c, 2a
    - Khi 2a khớp → Tạo 2b, 2c, 3a
    - Khi 3a khớp → Tạo 3b, 3c (và 4a nếu số lớp > 3)
  
- [ ] ❌ **Chưa có:** Xử lý khi TP khớp trước (1c)
  - **Yêu cầu:**
    - Hủy 1b (Stop Loss)
    - Hủy 2a (Entry lớp 2)
    - Kết thúc lớp 1

- [ ] ❌ **Chưa có:** Xử lý khi SL khớp trước (1b)
  - **Yêu cầu:**
    - Hủy 1c (Take Profit)
    - Giữ 2a (vẫn có thể entry lớp 2)

- [ ] ❌ **Chưa có:** Xử lý nhiều lớp đồng thời
  - **Yêu cầu:** Lớp 2, 3 có thể khớp trước khi lớp 1 đóng
  - **Challenge:** Cần tracking state phức tạp

**Action:** Cần viết lại toàn bộ logic trong file mới

```python
# TODO: Tạo file mới hd_order_cascade.py
# Hoặc refactor hd_order_123.py

class LayerManager:
    def __init__(self):
        self.layers = {}  # {symbol: {layer_num: {orders}}}
    
    def on_order_filled(self, order):
        symbol = order['symbol']
        # Xác định đây là lệnh gì (1a, 1b, 1c, 2a,...)
        order_code = self.identify_order_code(order)
        
        if order_code.endswith('a'):  # Entry order
            self.create_sl_tp_and_next_entry(symbol, order)
        elif order_code.endswith('b'):  # Stop Loss
            self.cancel_tp_of_same_layer(symbol, order)
        elif order_code.endswith('c'):  # Take Profit
            self.cancel_sl_and_next_entry_of_same_layer(symbol, order)
```

---

### 3.3 Đọc config từ Sheet

- [ ] ❌ **Chưa có:** Đọc số lớp lệnh từ Cột B
- [ ] ❌ **Chưa có:** Đọc loại lệnh từ Cột I (TRAILING STOP/STOP LIMIT/LIMIT)
- [ ] ❌ **Chưa có:** Đọc Stop Price (Cột M), Limit Price (Cột N)
- [x] ⚠️ **Có một phần:** Đọc đòn bẩy (Cột J)
  - Hiện tại: Đọc từ Cột B (cũ), cần đổi sang Cột J
- [x] ⚠️ **Có một phần:** Đọc Callback % (Cột K)
  - Hiện tại: Đọc từ Cột C (cũ), cần đổi sang Cột K
- [x] ⚠️ **Có một phần:** Đọc Activation Price (Cột L)
  - Hiện tại: Đọc từ Cột D (cũ), cần đổi sang Cột L
- [x] ⚠️ **Có một phần:** Đọc vốn gốc (Cột O)
  - Hiện tại: Đọc từ Cột H (cũ), cần đổi sang Cột O

**Action:** Update mapping cột trong `hd_order.py`

---

## PHẦN 4: XỬ LÝ LỖI VÀ CẢNH BÁO

### 4.1 Lỗi API -4120 (Trailing Stop)

- [ ] ❌ **Chưa xử lý:** Binance API Code -4120
  - **Yêu cầu:** Chuyển sang Algo Order API
  - **Status:** Code hiện tại sẽ bị lỗi khi Binance enforce thay đổi
  - **Action:** Wrap create_order với try-catch và fallback

```python
# TODO: Thêm vào binance_utils.py
def create_trailing_stop_order_safe(exchange, symbol, side, amount, params):
    try:
        # Thử cách cũ
        return exchange.create_order(symbol, 'TRAILING_STOP_MARKET', side, amount, None, params)
    except ccxt.ExchangeError as e:
        if '-4120' in str(e):
            # Chuyển sang Algo Order API
            return exchange.fapiPrivatePostAlgoOrder({
                'symbol': symbol,
                'side': side.upper(),
                'type': 'TRAILING_STOP_MARKET',
                'quantity': amount,
                'activationPrice': params['activationPrice'],
                'callbackRate': params['callbackRate']
            })
        else:
            raise e
```

---

### 4.2 Lỗi Reduce Only sót lại

- [x] ⚠️ **Có một phần:** Hủy lệnh sau khi đóng vị thế
  - File: `hd_alert_possition_and_open_order.py`, dòng 131
  - Function: `cancel_all_open_orders()`
  
- [ ] ❌ **Thiếu:** Retry mechanism với verify
  - **Yêu cầu:**
    - Retry tối đa 3 lần
    - Verify sau mỗi lần xóa
    - Delay giữa các lần
    - Gửi Telegram nếu fail

```python
# TODO: Cải thiện cancel_all_open_orders() trong hd_alert_possition_and_open_order.py
def cancel_all_open_orders_with_retry(symbol, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Lấy danh sách lệnh
            open_orders = exchange.fetch_open_orders(symbol)
            
            if not open_orders:
                print(f"✅ Không còn lệnh chờ cho {symbol}")
                return True
            
            # Hủy từng lệnh
            for order in open_orders:
                exchange.cancel_order(order['id'], symbol)
                print(f"Đã hủy lệnh {order['id']}")
            
            # Delay trước khi verify
            time.sleep(2)
            
            # Verify
            remaining_orders = exchange.fetch_open_orders(symbol)
            if len(remaining_orders) == 0:
                print(f"✅ Xác nhận: Đã xóa sạch lệnh cho {symbol}")
                return True
            else:
                print(f"⚠️ Còn {len(remaining_orders)} lệnh sót, retry lần {attempt+2}/{max_retries}")
                
        except Exception as e:
            print(f"❌ Lỗi khi hủy lệnh: {e}")
    
    # Sau 3 lần vẫn fail
    telegram_factory.send_tele(
        f"🔴 CẢNH BÁO NGHIÊM TRỌNG\nKhông thể xóa lệnh reduce only cho {symbol}\nCần can thiệp thủ công!",
        cst.chat_id, True, True
    )
    return False
```

- [ ] ❌ **Thiếu:** Kiểm tra trước khi entry mới
  - **Yêu cầu:** Đảm bảo không còn lệnh reduce only trước khi đặt lệnh mới
  
```python
# TODO: Thêm vào hd_order.py trước khi đặt lệnh
def check_no_reduce_only_orders(symbol):
    orders = exchange.fetch_open_orders(symbol)
    reduce_only_orders = [o for o in orders if o.get('reduceOnly')]
    
    if reduce_only_orders:
        msg = f"⚠️ Phát hiện {len(reduce_only_orders)} lệnh reduce only sót cho {symbol}. Bỏ qua đặt lệnh mới."
        telegram_factory.send_tele(msg, cst.chat_id, True, True)
        return False
    return True
```

---

### 4.3 Các lỗi thường gặp khác

- [ ] ⚠️ **Cần cải thiện:** Error handling trong các module
  - Hiện tại: Chỉ có try-catch tổng quát
  - Yêu cầu: Xử lý cụ thể từng loại lỗi

**Danh sách lỗi cần xử lý:**
- [ ] Trigger immediately
- [ ] Binance blocked
- [ ] API overload
- [ ] Symbol mismatch
- [ ] Google token expired
- [ ] Close all failed
- [ ] Insufficient balance
- [ ] Position not found
- [ ] Rate limit exceeded
- [ ] Invalid leverage

**Action:** Tạo centralized error handler

```python
# TODO: Tạo file error_handler.py
class ErrorHandler:
    @staticmethod
    def handle_exchange_error(e, context):
        error_msg = str(e)
        
        if "Trigger immediately" in error_msg:
            # Bỏ qua, không retry
            logging.warning(f"Trigger immediately: {context}")
            return "skip"
            
        elif "code=-1102" in error_msg:  # Binance blocked
            telegram_factory.send_tele(
                f"⛔ BINANCE BLOCKED\n{context['symbol']}\nChờ 5 phút",
                cst.chat_id, True, True
            )
            return "wait_5min"
            
        elif "code=-1003" in error_msg:  # API overload
            time.sleep(5)
            return "retry"
            
        # ... xử lý các lỗi khác
```

---

### 4.4 Chiến lược retry

- [ ] ❌ **Chưa có:** Exponential backoff
- [ ] ❌ **Chưa có:** Phân loại lỗi retry vs skip
- [ ] ❌ **Chưa có:** Log chi tiết mỗi lần retry

**Action:** Implement retry decorator

```python
# TODO: Thêm vào utils.py
def retry_with_backoff(max_retries=3, initial_delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    # Kiểm tra có nên retry không
                    if should_skip_retry(e):
                        raise e
                    
                    print(f"Retry {attempt+1}/{max_retries} sau {delay}s")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
        return wrapper
    return decorator

def should_skip_retry(error):
    skip_errors = [
        "Trigger immediately",
        "Invalid symbol",
        "Insufficient balance"
    ]
    return any(err in str(error) for err in skip_errors)
```

---

### 4.5 Mức độ cảnh báo

- [ ] ⚠️ **Cần cải thiện:** Phân cấp logging
  - Hiện tại: Chỉ có logging.error
  - Yêu cầu: INFO, WARNING, ERROR, CRITICAL

**Action:** Update logging config

```python
# TODO: Thêm vào đầu mỗi file
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{__file__}.log'),
        logging.StreamHandler()  # Console output
    ]
)

logger = logging.getLogger(__name__)

# Usage:
logger.info("Đang quét lệnh...")
logger.warning("Phát hiện lệnh reduce only sót")
logger.error("Lỗi khi đặt lệnh")
logger.critical("Hệ thống gặp lỗi nghiêm trọng, dừng bot!")
```

---

## PHẦN 5: TELEGRAM NOTIFICATION

### 5.1 Các loại thông báo

#### 5.1.1 Thông báo lệnh khớp
- [x] ⚠️ **Có cơ bản:** Thông báo đơn giản
  - File: `hd_order.py`, dòng 261-262
  - Hiện tại: "Lệnh 1: đã được tạo: {symbol}"
- [ ] ❌ **Thiếu:** Format đầy đủ theo yêu cầu

**Action:** Nâng cấp message format

```python
# TODO: Tạo telegram_templates.py
def format_order_filled_message(order_info):
    return f"""
✅ <b>LỆNH KHỚP</b>

<b>Mã:</b> {order_info['symbol']}
<b>Mã lệnh:</b> {order_info['order_code']} ({order_info['order_type']})
<b>Giá vào:</b> {order_info['entry_price']}
<b>Đòn bẩy:</b> {order_info['leverage']}x
<b>Vốn:</b> {order_info['capital']} USDT
<b>Giá trị position:</b> {order_info['position_value']} USDT
<b>Thời gian:</b> {order_info['timestamp']}

<b>Lệnh tiếp theo đã tạo:</b> {', '.join(order_info['next_orders'])}
"""
```

#### 5.1.2 Thông báo lỗi đặt lệnh
- [x] ⚠️ **Có cơ bản:** Print lỗi ra console
- [ ] ❌ **Thiếu:** Gửi Telegram với format đầy đủ

**Action:** Thêm Telegram notification cho mọi lỗi

```python
# TODO: Thêm vào error_handler.py
def notify_order_error(symbol, order_code, error):
    msg = f"""
🚨 <b>LỖI ĐẶT LỆNH</b>

<b>Mã:</b> {symbol}
<b>Mã lệnh:</b> {order_code}
<b>Mã lỗi:</b> {error.get('code', 'N/A')}
<b>Chi tiết:</b> {error.get('message', str(error))}
<b>Hành động:</b> {error.get('action', 'Bỏ qua')}
<b>Thời gian:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    telegram_factory.send_tele(msg, cst.chat_id, True, True)
```

#### 5.1.3 Thông báo API bị chặn
- [ ] ❌ **Chưa có**

#### 5.1.4 Báo cáo số dư định kỳ
- [ ] ❌ **Chưa có:** Báo cáo định kỳ tự động
  - **Yêu cầu:** Mỗi giờ hoặc khi PNL thay đổi > 5%

**Action:** Tạo module mới

```python
# TODO: Tạo file hd_report_balance.py
last_pnl = 0
last_report_time = datetime.now()

def check_and_report_balance():
    global last_pnl, last_report_time
    
    balance = exchange.fetch_balance()
    current_pnl = float(balance['info']['totalCrossUnPnl'])
    
    # Kiểm tra điều kiện gửi báo cáo
    time_elapsed = (datetime.now() - last_report_time).total_seconds() / 3600
    pnl_change = abs(current_pnl - last_pnl) / abs(last_pnl) * 100 if last_pnl != 0 else 100
    
    if time_elapsed >= 1 or pnl_change >= 5:
        # Gửi báo cáo
        positions = [p for p in balance['info']['positions'] if float(p['positionAmt']) != 0]
        open_orders = exchange.fetch_open_orders()
        
        msg = f"""
📊 <b>BÁO CÁO SỐ DƯ</b>

<b>Wallet Balance:</b> {balance['info']['totalWalletBalance']} USDT
<b>Margin Balance:</b> {balance['info']['totalMarginBalance']} USDT
<b>Unrealized PNL:</b> {current_pnl} USDT ({pnl_change:+.2f}%)
<b>Số vị thế đang mở:</b> {len(positions)}
<b>Số lệnh chờ:</b> {len(open_orders)}
<b>Thời gian:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        telegram_factory.send_tele(msg, cst.chat_id, True, True)
        
        last_pnl = current_pnl
        last_report_time = datetime.now()

# Chạy trong while loop với delay 5 phút
```

#### 5.1.5-8 Các thông báo khác
- [ ] ❌ Kích hoạt lệnh STOP
- [ ] ❌ Xác nhận hoàn tất STOP
- [ ] ❌ Cảnh báo Reduce Only sót
- [ ] ❌ Cảnh báo nghiêm trọng

**Action:** Tạo templates cho tất cả

---

### 5.2 Tần suất thông báo

- [x] ✅ **Đã có:** Real-time cho lệnh khớp
- [ ] ❌ **Chưa có:** Real-time cho lỗi (chưa gửi Telegram)
- [ ] ❌ **Chưa có:** Định kỳ 1 giờ cho số dư
- [ ] ❌ **Chưa có:** Khi PNL thay đổi > 5%

---

### 5.3 Bot commands (Tùy chọn)

- [ ] 🔵 **Optional:** Tương tác 2 chiều
  - /status, /balance, /positions, /orders, /stop, /resume, /cancel

**Action:** Nếu cần implement, dùng python-telegram-bot với handlers

```python
# TODO: Nếu cần bot commands, tạo telegram_bot_commands.py
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lấy trạng thái bot
    msg = "🤖 Bot đang chạy\n"
    # ... thêm thông tin
    await update.message.reply_text(msg)

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    balance = exchange.fetch_balance()
    msg = f"💰 Số dư: {balance['info']['totalWalletBalance']} USDT"
    await update.message.reply_text(msg)

# ... thêm các commands khác

def start_bot_commands():
    app = Application.builder().token(cst.bot_token).build()
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("balance", balance_command))
    # ... add thêm handlers
    app.run_polling()
```

---

## PHẦN 6: CẢI THIỆN CHUNG

### 6.1 Code Quality

- [ ] ⚠️ **Cần refactor:** Loại bỏ code duplicate
  - Nhiều file có hàm `is_same_pair()`, `is_number()`
  - **Action:** Consolidate vào `utils.py`

- [ ] ⚠️ **Cần cải thiện:** Naming convention
  - Nhiều biến tiếng Việt không dấu: `don_bay`, `lenh2_rate`
  - **Action:** Rename hoặc giữ nguyên nếu user muốn

- [ ] ⚠️ **Cần thêm:** Type hints
  - **Action:** Thêm type hints cho các functions

```python
# TODO: Ví dụ refactor
from typing import List, Dict, Tuple, Optional

def get_price_precision(symbol: str) -> int:
    ...

def calculate_high_low_30d(pair: str, timeframe: str = '1d') -> Tuple[float, float]:
    ...
```

### 6.2 Configuration Management

- [x] ✅ **Tốt:** Đã dùng config.ini
- [ ] ⚠️ **Cần bổ sung:** Thêm configs cho các tính năng mới

**Action:** Update config.ini

```ini
# TODO: Thêm vào config.ini

[logging]
level = INFO
log_dir = ./logs

[telegram]
enable_bot_commands = false
report_balance_hours = 1
report_pnl_threshold_percent = 5

[trading]
enable_multi_layer = true
max_layers = 3
enable_tracking_30_prices = true

[error_handling]
max_retries = 3
retry_delay_seconds = 2
enable_exponential_backoff = true
```

### 6.3 Testing

- [ ] ❌ **Chưa có:** Unit tests
- [ ] ❌ **Chưa có:** Integration tests
- [x] ✅ **Có:** Test mode flag

**Action:** Thêm tests (optional, nếu thời gian cho phép)

```python
# TODO: Tạo tests/test_order_logic.py
import unittest
from hd_order_cascade import LayerManager

class TestLayerManager(unittest.TestCase):
    def test_create_orders_after_1a_filled(self):
        manager = LayerManager()
        order_1a = {'symbol': 'BTC/USDT', 'filled': True}
        
        next_orders = manager.on_order_filled(order_1a)
        
        self.assertEqual(len(next_orders), 3)
        self.assertIn('1b', [o['code'] for o in next_orders])
        self.assertIn('1c', [o['code'] for o in next_orders])
        self.assertIn('2a', [o['code'] for o in next_orders])
```

### 6.4 Documentation

- [x] ✅ **Tốt:** QBot.md rất chi tiết
- [ ] ⚠️ **Cần bổ sung:** Code comments
  - Nhiều functions thiếu docstrings
  
**Action:** Thêm docstrings

```python
# TODO: Ví dụ
def calculate_price_range(pair: str, num_days: int, timeframe: str) -> Tuple[float, float]:
    """
    Tính biên độ tăng/giảm mạnh nhất trong khoảng thời gian.
    
    Args:
        pair: Cặp giao dịch (VD: 'BTC/USDT')
        num_days: Số ngày cần tính
        timeframe: Khung thời gian ('15m', '1h', '1d')
    
    Returns:
        Tuple[max_increase, max_decrease]: Biên độ tăng và giảm (%)
        
    Example:
        >>> max_inc, max_dec = calculate_price_range('BTC/USDT', 7, '1h')
        >>> print(f"Max increase: {max_inc}%")
    """
    ...
```

### 6.5 Monitoring & Observability

- [x] ⚠️ **Có cơ bản:** Logging vào file
- [ ] ❌ **Thiếu:** Metrics tracking
  - Số lệnh thành công/thất bại
  - Thời gian phản hồi API
  - Số lần retry

**Action:** Thêm metrics (optional)

```python
# TODO: Tạo metrics.py
from collections import defaultdict
from datetime import datetime

class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timers = {}
    
    def increment(self, metric_name: str, value: int = 1):
        self.counters[metric_name] += value
    
    def start_timer(self, timer_name: str):
        self.timers[timer_name] = datetime.now()
    
    def stop_timer(self, timer_name: str) -> float:
        if timer_name in self.timers:
            elapsed = (datetime.now() - self.timers[timer_name]).total_seconds()
            del self.timers[timer_name]
            return elapsed
        return 0
    
    def get_summary(self) -> str:
        return f"""
📈 <b>METRICS SUMMARY</b>

<b>Orders placed:</b> {self.counters['orders_placed']}
<b>Orders filled:</b> {self.counters['orders_filled']}
<b>Orders failed:</b> {self.counters['orders_failed']}
<b>API calls:</b> {self.counters['api_calls']}
<b>Errors:</b> {self.counters['errors']}
"""

metrics = Metrics()
```

---

## PHẦN 7: ROADMAP THỰC HIỆN

### Phase 1: Critical Fixes (1-2 ngày)
**Priority: 🔴 HIGH**

- [ ] Fix API -4120 error (Algo Order API)
- [ ] Improve cancel reduce only orders (retry mechanism)
- [ ] Add XÓA CHỜ và XÓA VỊ THẾ commands
- [ ] Improve error handling và logging
- [ ] Update column mapping trong hd_order.py (theo cấu trúc mới)

**Deliverable:** Bot chạy ổn định không bị crash

---

### Phase 2: Core Features (3-5 ngày)
**Priority: 🟡 MEDIUM**

- [ ] Implement cascade logic (1a → 1b+1c+2a → 2b+2c+3a)
- [ ] Add support cho STOP_LIMIT và LIMIT orders
- [ ] Implement tracking state trong Google Sheet (Cột C, D, E, F, G)
- [ ] Add số lớp lệnh config (Cột B)
- [ ] Handle TP/SL logic (hủy lệnh tương ứng)

**Deliverable:** Flow đa lớp hoạt động đúng

---

### Phase 3: Data Collection (2-3 ngày)
**Priority: 🟡 MEDIUM**

- [ ] Add all 47+ columns data
- [ ] Add Funding Rate
- [ ] Add Volume cho các timeframes
- [ ] Add Bollinger Bands đầy đủ
- [ ] Add timestamp cho giá cao/thấp
- [ ] Implement tracking 30 mức giá

**Deliverable:** Sheet Data đầy đủ theo yêu cầu

---

### Phase 4: Notifications (1-2 ngày)
**Priority: 🟢 LOW

- [ ] Rich format Telegram messages với icon
- [ ] Báo cáo số dư định kỳ
- [ ] All notification types theo QBot.md
- [ ] (Optional) Bot commands 2-way

**Deliverable:** Telegram notifications đầy đủ và đẹp

---

### Phase 5: Polish & Testing (2-3 ngày)
**Priority: 🟢 LOW**

- [ ] Code refactoring
- [ ] Add type hints
- [ ] Add docstrings
- [ ] (Optional) Unit tests
- [ ] Performance optimization
- [ ] Documentation updates

**Deliverable:** Code quality cao, sẵn sàng production

---

## TỔNG KẾT

### Thống kê

| Loại | Số lượng | Ghi chú |
|------|----------|---------|
| ✅ Có sẵn và tốt | ~20 items | Core MVP features |
| ⚠️ Có nhưng cần cải thiện | ~25 items | Cần refactor/nâng cấp |
| ❌ Chưa có, cần làm mới | ~60 items | Phần lớn advanced features |
| 🔵 Optional | ~5 items | Nice to have |
| **TỔNG** | **~110 items** | |

### Ước tính thời gian

- **Phase 1 (Critical):** 1-2 ngày (16h)
- **Phase 2 (Core):** 3-5 ngày (40h)
- **Phase 3 (Data):** 2-3 ngày (24h)
- **Phase 4 (Notifications):** 1-2 ngày (16h)
- **Phase 5 (Polish):** 2-3 ngày (24h)

**TỔNG:** 9-15 ngày (120 giờ làm việc)

### Rủi ro

1. **Logic cascade phức tạp:** Có thể mất nhiều thời gian hơn ước tính
2. **Binance API changes:** Có thể phải adapt thêm
3. **Race conditions:** Cần test kỹ với nhiều module chạy đồng thời
4. **Google Sheets rate limits:** Có thể cần optimize số lần gọi API

### Khuyến nghị

1. **Bắt đầu từ Phase 1:** Fix critical bugs trước
2. **Test từng phase:** Đảm bảo stable trước khi sang phase tiếp theo
3. **Testnet:** Dùng Binance Testnet để test logic lệnh
4. **Backup:** Backup code và config thường xuyên
5. **Monitoring:** Monitor logs và Telegram trong quá trình nâng cấp

---

**Prepared by:** AI Assistant  
**Date:** 15/12/2025  
**Version:** 1.0

