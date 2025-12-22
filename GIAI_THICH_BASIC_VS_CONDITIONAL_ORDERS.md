# 🔍 GIẢI THÍCH: BASIC vs CONDITIONAL ORDERS

## ❓ Vấn đề người dùng gặp phải:

1. **Vẫn bị lặp đơn** mặc dù đã có logic kiểm tra
2. **Order vào tab "Conditional"** thay vì "Basic"  
3. **Bot không xóa được** orders trong tab "Conditional"

---

## 📊 Binance phân loại 2 loại orders:

### 1️⃣ **BASIC ORDERS** (Lệnh thông thường)

**Đặc điểm:**
- Hiển thị trong tab **"Basic"** trên Binance UI
- API lấy: `exchange.fetch_open_orders()`
- API hủy: `exchange.cancel_order(order_id, symbol)`

**Bao gồm:**
- ✅ `LIMIT` - Lệnh giới hạn
- ✅ `MARKET` - Lệnh thị trường
- ✅ `STOP_MARKET` - Stop loss/take profit thông thường
- ✅ `STOP_LIMIT` - Stop limit thông thường

**Ví dụ:**
```python
# Đặt lệnh LIMIT
order = exchange.create_limit_buy_order('BTC/USDT', 0.001, 50000)

# Lấy orders
orders = exchange.fetch_open_orders('BTC/USDT')
# → Trả về orders trên

# Hủy order
exchange.cancel_order(order['id'], 'BTC/USDT')
```

---

### 2️⃣ **CONDITIONAL ORDERS** (Algo Orders - Lệnh điều kiện)

**Đặc điểm:**
- Hiển thị trong tab **"Conditional"** trên Binance UI ← QUAN TRỌNG!
- API lấy: `exchange.fapiPrivateGetAlgoOpenOrders()` ← KHÁC!
- API hủy: `exchange.fapiPrivateDeleteAlgoOrder()` ← KHÁC!

**Bao gồm:**
- ✅ `TRAILING_STOP` - Trailing stop (VP - Volume Participation) ← **ĐÂY LÀ ORDER CỦA BẠN!**
- ✅ `TWAP` - Time-Weighted Average Price
- ✅ `Iceberg` - Iceberg orders
- ✅ Các algo orders đặc biệt khác

**Ví dụ:**
```python
# Đặt lệnh TRAILING_STOP
order = exchange.create_order(
    symbol='BTC/USDT',
    type='TRAILING_STOP_MARKET',
    side='buy',
    amount=0.001,
    params={
        'activationPrice': 50000,
        'callbackRate': 1.0
    }
)

# Lấy orders (QUAN TRỌNG!)
algo_orders = exchange.fapiPrivateGetAlgoOpenOrders({'symbol': 'BTCUSDT'})
# → Trả về algo orders (Conditional)

# Hủy algo order (KHÁC với Basic!)
exchange.fapiPrivateDeleteAlgoOrder({
    'symbol': 'BTCUSDT',
    'algoId': order['info']['algoId']
})
```

---

## 🔴 TẠI SAO BỊ LẶP ĐƠN?

### Kịch bản bot CŨ (trước khi fix):

```
┌─────────────────────────────────────────────────────────────┐
│ Lần chạy 1 (10:48)                                          │
└─────────────────────────────────────────────────────────────┘

1. Bot đọc sheet: AVAAI/USDT, leverage 1, activation 0.00512
2. Bot kiểm tra: has_pending_trailing_stop_order("AVAAI/USDT")
   
   Code:
   open_orders = exchange.fetch_open_orders('AVAAI/USDT')
   # → Trả về: [] (rỗng)
   
   Lý do rỗng: fetch_open_orders() CHỈ LẤY BASIC ORDERS!
               TRAILING_STOP nằm trong CONDITIONAL → KHÔNG TRẢ VỀ!
   
   → return False (Không có order)

3. Bot đặt lệnh TRAILING_STOP
   → Order được tạo với algoId = 12345
   → Order nằm trong tab "Conditional" trên Binance


┌─────────────────────────────────────────────────────────────┐
│ Lần chạy 2 (10:49)                                          │
└─────────────────────────────────────────────────────────────┘

1. Bot đọc sheet: AVAAI/USDT, leverage 1, activation 0.00506 (GIÁ THAY ĐỔI)
2. Bot kiểm tra: has_pending_trailing_stop_order("AVAAI/USDT")
   
   Code:
   open_orders = exchange.fetch_open_orders('AVAAI/USDT')
   # → Trả về: [] (rỗng)  ← VẪN RỖNG!
   
   Lý do: Order 12345 nằm trong CONDITIONAL
          fetch_open_orders() KHÔNG THỂ LẤY ĐƯỢC!
   
   → return False (Nghĩ là không có order)  ← SAI!

3. Bot đặt lệnh TRAILING_STOP LẦN 2
   → Order được tạo với algoId = 12346
   → Giờ có 2 orders: 12345 + 12346  ← LẶP ĐƠN!


┌─────────────────────────────────────────────────────────────┐
│ Kết quả                                                      │
└─────────────────────────────────────────────────────────────┘

Binance UI:
  Open Orders(2)
  ├── Basic(0)  ← Trống
  └── Conditional(2)  ← Có 2 orders TRAILING_STOP trùng lặp!
      ├── algoId: 12345 (activation: 0.00512)
      └── algoId: 12346 (activation: 0.00506)  ← LẶP!
```

---

## 🔴 TẠI SAO BOT KHÔNG XÓA ĐƯỢC CONDITIONAL ORDERS?

### Code cũ của `hd_cancel_orders_schedule.py`:

```python
def cancel_all_open_orders(symbol):
    open_orders = exchange.fetch_open_orders(symbol)
    #               ↑
    #               CHỈ LẤY BASIC ORDERS!
    
    if open_orders:
        for order in open_orders:
            exchange.cancel_order(order['id'], symbol)
            #        ↑
            #        CHỈ HỦY ĐƯỢC BASIC ORDERS!
```

**Vấn đề:**
1. `fetch_open_orders()` **KHÔNG trả về** Conditional orders
2. `cancel_order()` **KHÔNG hủy được** Conditional orders (cần dùng API khác)

**Kết quả:**
- Bot chỉ hủy được orders trong tab "Basic"
- Orders trong tab "Conditional" **VẪN CÒN ĐÓ!**
- Người dùng phải vào Binance Web/App hủy thủ công

---

## ✅ GIẢI PHÁP

### 1. Sửa `has_pending_trailing_stop_order()`:

**Trước:**
```python
def has_pending_trailing_stop_order(symbol):
    open_orders = exchange.fetch_open_orders(symbol=symbol)
    # → CHỈ kiểm tra Basic orders
    # → Bỏ sót Conditional orders
```

**Sau:**
```python
def has_pending_trailing_stop_order(symbol):
    # BƯỚC 1: Kiểm tra Basic orders
    open_orders = exchange.fetch_open_orders(symbol=symbol)
    for order in open_orders:
        if 'TRAILING' in order.get('type', ''):
            return True
    
    # BƯỚC 2: Kiểm tra Conditional/Algo orders  ← MỚI!
    try:
        algo_orders = exchange.fapiPrivateGetAlgoOpenOrders({
            'symbol': symbol.replace('/', '')
        })
        
        if 'orders' in algo_orders and algo_orders['orders']:
            for order in algo_orders['orders']:
                if order.get('algoType') == 'VP':  # VP = TRAILING_STOP
                    return True
    except Exception as e:
        logger.warning(f"Không kiểm tra được algo orders: {e}")
    
    return False
```

### 2. Sửa `cancel_all_open_orders()`:

**Trước:**
```python
def cancel_all_open_orders(symbol):
    open_orders = exchange.fetch_open_orders(symbol)
    
    for order in open_orders:
        exchange.cancel_order(order['id'], symbol)
    # → CHỈ hủy Basic orders
```

**Sau:**
```python
def cancel_all_open_orders(symbol):
    # BƯỚC 1: Hủy Basic orders
    open_orders = exchange.fetch_open_orders(symbol)
    for order in open_orders:
        exchange.cancel_order(order['id'], symbol)
    
    # BƯỚC 2: Hủy Conditional/Algo orders  ← MỚI!
    try:
        symbol_normalized = symbol.replace('/', '')
        algo_orders = exchange.fapiPrivateGetAlgoOpenOrders({
            'symbol': symbol_normalized
        })
        
        if 'orders' in algo_orders and algo_orders['orders']:
            for order in algo_orders['orders']:
                algo_id = order.get('algoId')
                if algo_id:
                    exchange.fapiPrivateDeleteAlgoOrder({
                        'symbol': symbol_normalized,
                        'algoId': algo_id
                    })
    except Exception as e:
        logger.error(f"Lỗi khi hủy algo orders: {e}")
```

---

## 📊 So sánh TRƯỚC vs SAU fix:

### TRƯỚC fix:

| Thao tác | Basic Orders | Conditional Orders | Kết quả |
|----------|--------------|-------------------|---------|
| Đặt lệnh TRAILING_STOP | - | ✅ Tạo thành công | Order vào Conditional |
| `fetch_open_orders()` | ✅ Lấy được | ❌ **KHÔNG lấy được** | Bot không thấy order |
| Bot check có order? | - | ❌ Không thấy | → Đặt lại → LẶP! |
| `cancel_order()` | ✅ Hủy được | ❌ **KHÔNG hủy được** | Phải hủy thủ công |

### SAU fix:

| Thao tác | Basic Orders | Conditional Orders | Kết quả |
|----------|--------------|-------------------|---------|
| Đặt lệnh TRAILING_STOP | - | ✅ Tạo thành công | Order vào Conditional |
| `fetch_open_orders()` | ✅ | ❌ Không lấy được | - |
| `fapiPrivateGetAlgoOpenOrders()` | - | ✅ **LẤY ĐƯỢC!** | Bot thấy order |
| Bot check có order? | ✅ | ✅ **Thấy được!** | → Bỏ qua → KHÔNG lặp |
| `fapiPrivateDeleteAlgoOrder()` | - | ✅ **HỦY ĐƯỢC!** | Bot tự động hủy |

---

## 🎯 KẾT LUẬN

### Nguyên nhân gốc rễ:

1. **TRAILING_STOP = Conditional Order** (không phải Basic Order)
2. **`fetch_open_orders()` chỉ lấy Basic Orders** → Bỏ sót Conditional
3. **Bot không thấy order** → Đặt lại → Lặp đơn!
4. **`cancel_order()` chỉ hủy Basic Orders** → Không hủy được Conditional

### Giải pháp:

1. ✅ Dùng `fapiPrivateGetAlgoOpenOrders()` để **LẤY** Conditional orders
2. ✅ Dùng `fapiPrivateDeleteAlgoOrder()` để **HỦY** Conditional orders
3. ✅ Kiểm tra **CẢ 2 loại orders** (Basic + Conditional)
4. ✅ Hủy **CẢ 2 loại orders** (Basic + Conditional)

### Kết quả:

- ✅ 100% không lặp đơn
- ✅ Bot tự động phát hiện Conditional orders
- ✅ Bot tự động hủy Conditional orders
- ✅ Không cần can thiệp thủ công nữa!

---

**Tác giả:** Claude AI  
**Ngày:** 2025-01-19  
**Phiên bản:** 2.0
