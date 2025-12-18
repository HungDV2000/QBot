# QUY TRÌNH ĐẶT LỆNH CHÍNH THỨC - THEO YÊU CẦU USER

## 📋 **XÁC NHẬN HIỂU QUY TRÌNH**

### **PHẦN 1: CẤU TRÚC SHEET VÀ ĐẶT LỆNH 1 (ENTRY)**

#### **1.1. Cấu trúc Sheet**

✅ **Dòng 1:** Bỏ qua (nghiệp vụ thủ công, không liên quan bot)

✅ **Ô điều khiển:**
- **B2:** Trạng thái hệ thống
  - `LONG` = Đặt lệnh MUA (quét vùng Top giảm giá - hàng 55-104)
  - `SHORT` = Đặt lệnh BÁN (quét vùng Top tăng giá - hàng 4-53)
  - `CHỜ` = Bot không làm gì
  - `STOP` = Đóng toàn bộ vị thế + Hủy tất cả lệnh chờ
  
- **E2:** Vốn phân bổ cho mỗi lệnh (USDT)
  - Thay đổi theo từng thời điểm
  - Áp dụng cho tất cả lệnh (trừ khi có giá trị riêng ở cột H)

---

#### **1.2. Logic đặt lệnh 1 (Entry - Trailing Stop)**

**Khi B2 = LONG:**
- Bot quét vùng "Top giảm giá" (VD: hàng 55-104)
- Kiểm tra từng hàng:
  - Nếu **cột B (Leverage) ≠ 0** → Đặt lệnh
  - Nếu **cột B = 0 hoặc "N"** → Bỏ qua

**Thông số lệnh 1 (TRAILING_STOP):**
- **Symbol:** Từ cột A (VD: `AIOT/USDT`)
- **Đòn bẩy:** Từ cột B (VD: `1` = 1x)
- **Callback Rate:** Từ cột C (VD: `2%`)
- **Activation Price:** Từ cột D (VD: `0.08798470376`)
- **Vốn:** Từ cột H, nếu trống thì dùng E2

**Ví dụ cụ thể từ sheet:**
```
Row 55 (giả sử AIOT/USDT):
- A55: AIOT/USDT
- B55: 1 (đòn bẩy 1x)
- C55: 2%
- D55: 0.08798470376

→ Bot đặt lệnh TRAILING_STOP BUY:
  - Symbol: AIOT/USDT:USDT
  - Leverage: 1x
  - Activation: 0.08798470376
  - Callback: 2%
  - Capital: E2 USDT
```

---

### **PHẦN 2: ĐẶT LỆNH 2 & 3 (SAU KHI LỆNH 1 KHỚP)**

#### **2.1. Khi lệnh 1 (Entry) khớp:**

Bot **TỰ ĐỘNG** tạo 2 lệnh:

**Lệnh 2: STOP LOSS (Cắt lỗ)**
- **Loại:** STOP LIMIT
- **Chức năng:** Đóng vị thế khi giá đi ngược kỳ vọng
- **Giá:**
  - **Nếu lệnh 1 là LONG:**
    ```
    SL Price = Giá vào × (1 - lenh2_rate_long)
    SL Price = Giá vào × (1 - 0.3) = Giá vào × 0.7
    ```
    → Cắt lỗ khi giá **giảm 30%**
  
  - **Nếu lệnh 1 là SHORT:**
    ```
    SL Price = Giá vào × (1 + lenh2_rate_short)
    SL Price = Giá vào × (1 + 0.3) = Giá vào × 1.3
    ```
    → Cắt lỗ khi giá **tăng 30%**

**Ví dụ:**
```
Lệnh 1 LONG AIOT khớp @ 0.08798
→ Lệnh 2 (SL): STOP LIMIT SELL @ 0.08798 × 0.7 = 0.06159
```

---

**Lệnh 3: TAKE PROFIT (Chốt lời)**
- **Loại:** TRAILING_STOP
- **Chức năng:** Chốt lời khi giá đi đúng kỳ vọng
- **Activation Price:**
  - **Nếu lệnh 1 là LONG:**
    ```
    TP Activation = Giá vào × (1 + lenh3_rate_long)
    TP Activation = Giá vào × (1 + 0.6) = Giá vào × 1.6
    ```
    → Kích hoạt khi giá **tăng 60%**
  
  - **Nếu lệnh 1 là SHORT:**
    ```
    TP Activation = Giá vào × (1 - lenh3_rate_short)
    TP Activation = Giá vào × (1 - 0.6) = Giá vào × 0.4
    ```
    → Kích hoạt khi giá **giảm 60%**

- **Callback Rate:** 1% (từ `lenh3_callback_rate = 1`)

**Ví dụ:**
```
Lệnh 1 LONG AIOT khớp @ 0.08798
→ Lệnh 3 (TP): TRAILING_STOP SELL
   - Activation: 0.08798 × 1.6 = 0.14077
   - Callback: 1%
```

---

### **PHẦN 3: CẤU HÌNH TRONG CONFIG.INI**

**Config hiện tại:**
```ini
lenh2_rate_long = 0.3      # Cắt lỗ LONG: -30%
lenh2_rate_short = 0.3     # Cắt lỗ SHORT: +30%
lenh3_rate_long = 0.6      # Chốt lời LONG: +60%
lenh3_rate_short = 0.6     # Chốt lời SHORT: -60%
lenh3_callback_rate = 1    # TP callback: 1%
```

**Giải thích:**
- `lenh2_rate = 0.3` = 30% (không phải 0.3%)
- `lenh3_rate = 0.6` = 60% (không phải 0.6%)
- Rate là tỷ lệ (0.3 = 30%), không cần nhân 100

---

### **PHẦN 4: LUỒNG HOÀN CHỈNH**

```
┌──────────────────────────────────────┐
│ B2 = LONG                            │
│ E2 = 1.12 USDT                       │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Quét hàng 55-104 (Top giảm giá)     │
│ Tìm dòng có B ≠ 0 và B ≠ "N"        │
└────────────┬─────────────────────────┘
             │
             ▼ (Tìm thấy: Row 55 - AIOT/USDT)
┌──────────────────────────────────────┐
│ LỆNH 1 (ENTRY)                       │
│ TRAILING_STOP BUY                    │
│ - Symbol: AIOT/USDT                  │
│ - Leverage: 1x (B55)                 │
│ - Activation: 0.08798 (D55)          │
│ - Callback: 2% (C55)                 │
│ - Capital: 1.12 USDT (E2)            │
└────────────┬─────────────────────────┘
             │
             ▼ (Lệnh 1 KHỚP @ 0.08798)
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐    ┌─────────────┐
│ LỆNH 2  │    │  LỆNH 3     │
│ (SL)    │    │  (TP)       │
└─────────┘    └─────────────┘
    │                 │
    ▼                 ▼
STOP LIMIT SELL   TRAILING_STOP SELL
@ 0.06159         Activation: 0.14077
(0.08798 × 0.7)   Callback: 1%
Giảm 30%          (0.08798 × 1.6)
                  Tăng 60%
```

---

## ⚠️ **VẤN ĐỀ VỚI CODE HIỆN TẠI**

### **Vấn đề 1: Config không khớp ❌**

**Config hiện tại:**
```ini
order_column_structure = new  # ← SAI!
```

**Sheet thực tế:** Cấu trúc CŨ (B, C, D, H)

**Giải pháp:** 
```ini
order_column_structure = old  # ← PHẢI SỬA
```

---

### **Vấn đề 2: Validation B ≠ 0 ⚠️**

**Code hiện tại:**
```python
if d[leverage_idx] != "N" and is_number(d[leverage_idx]) ...
```

**Vấn đề:** 
- Check `!= "N"` OK
- Nhưng nếu B = `0` (số 0) → Vẫn pass check
- Yêu cầu: B ≠ 0 (không phải "N" và không phải 0)

**Cần thêm:**
```python
if d[leverage_idx] != "N" and d[leverage_idx] != 0 and is_number(d[leverage_idx]) and float(d[leverage_idx]) > 0 ...
```

---

### **Vấn đề 3: Cascade formula SAI ❌ (QUAN TRỌNG!)**

**Code hiện tại trong `cascade_manager.py`:**

```python
# Lệnh 2 (SL)
if is_long:
    stop_price = entry_price * (1 - lenh2_rate / leverage)  # ← SAI!
else:
    stop_price = entry_price * (1 + lenh2_rate / leverage)  # ← SAI!

# Lệnh 3 (TP)
if is_long:
    activation_price = entry_price * (1 + lenh3_rate / leverage)  # ← SAI!
else:
    activation_price = entry_price * (1 - lenh3_rate / leverage)  # ← SAI!
```

**Công thức ĐÚNG theo yêu cầu:**

```python
# Lệnh 2 (SL)
if is_long:
    stop_price = entry_price * (1 - lenh2_rate)  # Bỏ / leverage
else:
    stop_price = entry_price * (1 + lenh2_rate)  # Bỏ / leverage

# Lệnh 3 (TP)
if is_long:
    activation_price = entry_price * (1 + lenh3_rate)  # Bỏ / leverage
else:
    activation_price = entry_price * (1 - lenh3_rate)  # Bỏ / leverage
```

**Ví dụ so sánh:**

```
Lệnh 1 LONG @ 0.08798, Leverage 1x, Rate 0.3

Code HIỆN TẠI (SAI):
- SL = 0.08798 × (1 - 0.3 / 1) = 0.08798 × 0.7 = 0.06159  ← Đúng với leverage 1x
- Nhưng nếu leverage 10x:
  SL = 0.08798 × (1 - 0.3 / 10) = 0.08798 × 0.97 = 0.08534  ← Chỉ giảm 3%!

Code ĐÚNG (theo yêu cầu):
- SL = 0.08798 × (1 - 0.3) = 0.08798 × 0.7 = 0.06159  ← Luôn giảm 30%
- Không phụ thuộc leverage!
```

---

## ✅ **TÓM TẮT - TÔI ĐÃ HIỂU:**

### **Quy trình đặt lệnh:**

1. ✅ **Lệnh 1 (Entry):** TRAILING_STOP từ sheet (B, C, D, H)
2. ✅ **Lệnh 2 (SL):** STOP LIMIT @ Giá × (1 ± 0.3) = **±30%**
3. ✅ **Lệnh 3 (TP):** TRAILING_STOP @ Activation = Giá × (1 ± 0.6) = **±60%**, Callback 1%

### **Cấu trúc:**
- ✅ Cấu trúc CŨ: B (leverage), C (callback), D (activation), H (capital)
- ✅ Trạng thái: B2 (LONG/SHORT/CHỜ/STOP)
- ✅ Vốn: E2

### **Config:**
- ✅ `lenh2_rate = 0.3` = 30% (cắt lỗ)
- ✅ `lenh3_rate = 0.6` = 60% (chốt lời)
- ✅ `lenh3_callback_rate = 1` = 1% (TP callback)

### **Cần sửa code:**
1. ❌ `config.ini`: `order_column_structure = old`
2. ⚠️ `hd_order.py`: Thêm validation B ≠ 0
3. ❌ `cascade_manager.py`: **Sửa công thức SL/TP (bỏ / leverage)**

---

## 🎯 **CÔNG THỨC ĐÚNG:**

### **Lệnh 2 (Stop Loss):**
```python
if side == 'LONG':
    stop_price = entry_price * (1 - 0.3)  # Giảm 30%
else:  # SHORT
    stop_price = entry_price * (1 + 0.3)  # Tăng 30%
```

### **Lệnh 3 (Take Profit):**
```python
if side == 'LONG':
    tp_activation = entry_price * (1 + 0.6)  # Tăng 60%
else:  # SHORT
    tp_activation = entry_price * (1 - 0.6)  # Giảm 60%

tp_callback = 1  # 1%
```

---

**Bạn xác nhận tôi đã hiểu đúng không? Nếu đúng, tôi sẽ sửa code ngay! 🚀**
