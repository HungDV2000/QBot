# PHÂN TÍCH CẤU TRÚC ĐẶT LỆNH CŨ

## 📊 **PHÂN TÍCH TỪ HÌNH ẢNH GOOGLE SHEET**

### **1. Tổng quan cấu trúc CŨ**

**Config cần thiết:**
```ini
order_column_structure = old
```

**Các cột sử dụng:**
- **Cột A:** Symbol (Mã coin)
- **Cột B:** Đòn bẩy (Leverage)
- **Cột C:** Callback Rate (%)
- **Cột D:** Activation Price (Giá kích hoạt)
- **Cột H:** Vốn USDT (tùy chọn, nếu trống dùng E2)

---

### **2. Phân tích từng cột trong Sheet**

#### **Cột A: Symbol**

**Ví dụ trong sheet:**
- `ACT/USDT`
- `FIO/USDT`
- `PIPPIN/USDT`
- `BTC/USDT`

**Lưu ý:**
- ⚠️ Format trong sheet: `SYMBOL/USDT` (thiếu `:USDT` ở cuối)
- ✅ Code sẽ chấp nhận format này (Binance API tự động convert)
- ✅ Hoặc có thể thêm `:USDT` để rõ ràng hơn: `BTC/USDT:USDT`

**Validation trong code:**
```python
sym = d[0]
if not sym or not str(sym).strip():
    logger.warning(f"Symbol trống ở dòng, bỏ qua")
    continue
```

---

#### **Cột B: Đòn bẩy (Leverage)**

**Giá trị trong sheet:**
- Tất cả các dòng đều có giá trị: `N`

**Ý nghĩa:**
- `N` = Không đặt lệnh cho symbol này
- Số (VD: `1`, `10`, `20`) = Đòn bẩy x lần

**Logic trong code:**
```python
leverage_idx = 1  # Cột B (index 1) với cấu trúc CŨ

if d[leverage_idx] != "N" and is_number(d[leverage_idx]) and is_number(d[activation_idx]):
    # Chỉ xử lý nếu B != "N" và B là số và D là số
```

**Kết quả từ hình ảnh:**
- ❌ Tất cả dòng có `B = N` → Bot sẽ **BỎ QUA** tất cả các dòng này
- ✅ Để đặt lệnh: Cần thay `N` thành số (VD: `10`)

---

#### **Cột C: Callback Rate (%)**

**Ví dụ trong sheet:**
- `2.90%`
- `0.98%`
- `7.08%`

**Format:**
- ✅ Có thể có hoặc không có dấu `%`
- Code tự động loại bỏ: `d[callback_idx].replace("%", "")`

**Validation:**
- Phải là số (float)
- Thường trong khoảng 0.1% - 10%
- Với `is_number()` check trong code

**Sử dụng:**
- Dùng cho lệnh **TRAILING_STOP**
- Là % mà giá phải đảo chiều để lệnh khớp

---

#### **Cột D: Giá kích hoạt (Activation Price)**

**Ví dụ trong sheet:**
- `0.1472431296`
- `0.05123646464`
- `5.770730698`

**Format:**
- ✅ Số thực (float)
- ⚠️ Không được có dấu `%` (khác với cột C)

**Validation:**
```python
activation_idx = 3  # Cột D (index 3)

if is_number(d[activation_idx]):  # Phải là số
    activation_price = round(
        float(d[activation_idx].replace("%", "")), 
        binance_utils.get_price_precision(symbol)
    )
```

**Sử dụng:**
- Giá mà lệnh Trailing Stop sẽ kích hoạt
- Với LONG: Giá phải tăng lên mức này
- Với SHORT: Giá phải giảm xuống mức này

---

#### **Cột H: Vốn USDT (Mức vốn)**

**Trong hình ảnh:**
- ❌ Tất cả các ô đều **TRỐNG**

**Logic trong code:**
```python
capital_idx = 7  # Cột H (index 7) với cấu trúc CŨ

capitalMoney = float(e2_value)  # Mặc định từ E2
try:
    capitalMoney = float(d[capital_idx])  # Nếu H có giá trị thì dùng
except (ValueError, TypeError, IndexError) as e:
    logger.warning(f"Không đọc được vốn từ cột {capital_idx}, dùng mặc định: {e}")
```

**Kết quả:**
- ✅ Vì cột H trống → Bot sẽ dùng giá trị từ **E2** (Vốn mặc định)
- ✅ Trong hình ảnh: E2 = `1.12` → Tất cả lệnh sẽ dùng 1.12 USDT

**Lưu ý:**
- Có thể để trống để dùng E2 (tiện lợi)
- Hoặc điền giá trị riêng cho từng symbol (linh hoạt hơn)

---

### **3. Các cột khác (không dùng trong cấu trúc CŨ)**

#### **Cột E (SL), F (TP), G:**
- ❌ Không được bot đọc để đặt lệnh
- ✅ Có thể dùng cho tracking hoặc dữ liệu khác
- ✅ Sau khi lệnh khớp, bot có thể ghi tracking vào đây (nhưng hiện tại code chưa implement tracking cho cấu trúc CŨ)

#### **Cột I, J, K, L, M, N, O:**
- ❌ Bỏ qua hoàn toàn với cấu trúc CŨ
- ✅ Chỉ dùng khi `order_column_structure = new`

---

### **4. Logic xử lý trong code**

#### **Bước 1: Xác định cấu trúc**

```python
if cst.order_column_structure == 'new':
    leverage_idx = 9   # Cột J
    callback_idx = 10  # Cột K
    activation_idx = 11 # Cột L
    capital_idx = 14   # Cột O
else:  # 'old'
    leverage_idx = 1   # Cột B
    callback_idx = 2   # Cột C
    activation_idx = 3  # Cột D
    capital_idx = 7    # Cột H
```

#### **Bước 2: Validation**

```python
if d[leverage_idx] != "N" and is_number(d[leverage_idx]) and is_number(d[activation_idx]):
    # Chỉ xử lý nếu:
    # - Leverage != "N"
    # - Leverage là số
    # - Activation Price là số
```

**Với dữ liệu trong hình ảnh:**
- ❌ `d[1]` (B) = `"N"` → Điều kiện `!= "N"` FAIL
- ❌ Bot sẽ **BỎ QUA** tất cả các dòng

#### **Bước 3: Đọc loại lệnh**

```python
if cst.order_column_structure == 'new':
    # Đọc từ cột I (index 8)
    order_type_str = d[8].strip().upper()
else:  # 'old'
    # Mặc định TRAILING_STOP
    order_type_str = "TRAILING_STOP"
```

**Với cấu trúc CŨ:**
- ✅ Luôn là `TRAILING_STOP`
- ❌ Không hỗ trợ STOP_LIMIT, LIMIT, MARKET

#### **Bước 4: Tạo lệnh**

```python
# TRAILING STOP
activation_price = round(float(d[activation_idx].replace("%", "")), precision)
callback_rate = float(d[callback_idx].replace("%", ""))

order = order_helper.create_trailing_stop_order(
    symbol=symbol,
    side=side,  # "buy" hoặc "sell"
    amount=amount,  # Tính từ capitalMoney / lastPrice
    activation_price=activation_price,  # Từ cột D
    callback_rate=callback_rate,  # Từ cột C
    reduce_only=False
)
```

---

### **5. Ví dụ cụ thể từ hình ảnh**

#### **Ví dụ: ACT/USDT (Row 4)**

**Dữ liệu trong sheet:**
- **A4:** `ACT/USDT`
- **B4:** `N` ← **KHÔNG đặt lệnh**
- **C4:** `2.90%`
- **D4:** `0.1472431296`
- **H4:** Trống

**Kết quả:**
- ❌ Bot bỏ qua vì B4 = `N`

**Nếu muốn đặt lệnh:**
- ✅ **B4:** `10` (đòn bẩy 10x)
- ✅ **C4:** `2.90%` (giữ nguyên)
- ✅ **D4:** `0.1472431296` (giữ nguyên)
- ✅ **H4:** Trống (dùng E2 = 1.12 USDT)

**Lệnh sẽ được tạo:**
```
TRAILING_STOP BUY
Symbol: ACT/USDT
Activation: 0.1472431296
Callback: 2.90%
Leverage: 10x
Capital: 1.12 USDT
```

---

### **6. Checklist để đặt lệnh thành công**

✅ **Config:**
- [ ] `order_column_structure = old` trong `config.ini`

✅ **Sheet setup:**
- [ ] C1 hoặc B2 = `LONG` hoặc `SHORT` (không phải `CHỜ`)
- [ ] E2 có giá trị vốn mặc định (VD: `1.12`)

✅ **Dữ liệu mỗi dòng:**
- [ ] Cột A: Symbol hợp lệ (VD: `BTC/USDT`)
- [ ] Cột B: Số nguyên dương (VD: `10`) - **KHÔNG được là `N`**
- [ ] Cột C: Callback Rate số (VD: `2.90` hoặc `2.90%`)
- [ ] Cột D: Activation Price số (VD: `43000`)
- [ ] Cột H: Trống (dùng E2) hoặc số (VD: `200`)

---

### **7. So sánh với cấu trúc MỚI**

| Tính năng | Cấu trúc CŨ | Cấu trúc MỚI |
|-----------|-------------|--------------|
| **Cột Leverage** | B | J |
| **Cột Callback** | C | K |
| **Cột Activation** | D | L |
| **Cột Capital** | H | O |
| **Loại lệnh** | Chỉ TRAILING_STOP | 4 loại: TRAILING_STOP, STOP_LIMIT, LIMIT, MARKET |
| **Cột Loại lệnh** | Không có (mặc định) | I |
| **Cột Stop/Limit** | Không có | M, N |
| **Tracking tự động** | Chưa có | C, D, E, F, G |

---

### **8. Lưu ý quan trọng**

1. ⚠️ **Symbol format:**
   - Sheet: `ACT/USDT`
   - Binance cần: `ACT/USDT:USDT` (cho Futures)
   - Code sẽ xử lý tự động, nhưng nên thêm `:USDT` để rõ ràng

2. ⚠️ **Cột B = "N":**
   - Tất cả các dòng trong hình đều có B = `N`
   - Bot sẽ **KHÔNG đặt lệnh** cho bất kỳ symbol nào
   - Cần thay `N` thành số để đặt lệnh

3. ⚠️ **Vốn:**
   - E2 = `1.12` USDT (rất nhỏ)
   - Phù hợp cho test, nhưng cần tăng lên khi trade thật

4. ⚠️ **Trạng thái:**
   - C1 = `CHỜ` trong hình ảnh
   - Bot sẽ **KHÔNG làm gì** với trạng thái này
   - Cần đổi thành `LONG` hoặc `SHORT` để bot quét lệnh

---

**Ngày phân tích:** 2025-01-18  
**Cấu trúc:** CŨ (`order_column_structure = old`)
