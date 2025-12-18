# HƯỚNG DẪN ĐẶT LỆNH - QBOT V2.0

## 📋 MỤC LỤC

1. [Tổng quan hệ thống đặt lệnh](#1-tổng-quan-hệ-thống-đặt-lệnh)
2. [Cấu trúc Google Sheet](#2-cấu-trúc-google-sheet)
3. [Các loại lệnh hỗ trợ](#3-các-loại-lệnh-hỗ-trợ)
4. [Hướng dẫn đặt lệnh từng loại](#4-hướng-dẫn-đặt-lệnh-từng-loại)
5. [Logic Cascade đa lớp](#5-logic-cascade-đa-lớp)
6. [Các trạng thái hệ thống](#6-các-trạng-thái-hệ-thống)
7. [Ví dụ thực tế](#7-ví-dụ-thực-tế)
8. [Xử lý lỗi & Troubleshooting](#8-xử-lý-lỗi--troubleshooting)

---

## 1. TỔNG QUAN HỆ THỐNG ĐẶT LỆNH

### 1.1. Luồng hoạt động

```
┌─────────────────┐
│ Google Sheet    │  ← User nhập dữ liệu
│ (ĐẶT LỆNH)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  hd_order.py    │  ← Bot scan sheet mỗi X giây
│  (Main Script)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Binance API     │  ← Đặt lệnh lên sàn
│                 │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Cascade Manager │  ← Auto tạo SL/TP khi khớp
│                 │
└─────────────────┘
```

### 1.2. File liên quan

| File                      | Chức năng                                                      |
|---------------------------|----------------------------------------------------------------|
| `hd_order.py`             | Script chính quét sheet và đặt lệnh                            |
| `binance_order_helper.py` | Xử lý các loại lệnh (Trailing Stop, Stop Limit, Limit, Market) |
| `cascade_manager.py`      | Quản lý logic cascade đa lớp (1a→1b+1c+2a)                     |
| `order_state_tracker.py`  | Tracking trạng thái lệnh vào sheet                             |
| `gg_sheet_factory.py`     | Đọc/ghi dữ liệu Google Sheets                                  |

### 1.3. Tần suất quét

Bot quét sheet mỗi **X giây** (cấu hình trong `config.ini` - biến `delay_vao_lenh`)

```ini
# Trong config.ini
delay_vao_lenh = 60  # Quét mỗi 60 giây
```

### 1.4. Cấu hình cấu trúc cột

**Quan trọng:** Bot sử dụng cấu hình trong `config.ini` để xác định cấu trúc cột (không auto-detect):

```ini
# Trong config.ini, hiện tại đang test với cấu trúc đặt lệnh mới (new)
order_column_structure = new  # 'new' hoặc 'old'
```

- `new` = Cấu trúc MỚI (cột I, J, K, L, M, N, O) - Hỗ trợ 4 loại lệnh
- `old` = Cấu trúc CŨ (cột B, C, D, H) - Chỉ hỗ trợ TRAILING_STOP

**Lưu ý:** 
- ✅ Phải khớp với cấu trúc trong Google Sheet
- ✅ Nếu dùng `old` nhưng muốn dùng STOP_LIMIT/LIMIT/MARKET → phải đổi sang `new`

---

## 2. CẤU TRÚC GOOGLE SHEET

### 2.1. Sheet "TEST ĐẶT LỆNH (100 MÃ)"

#### **Ô điều khiển (Control Cells)**

| Ô      | Ý nghĩa             | Giá trị hợp lệ                                          |
|--------|---------------------|---------------------------------------------------------|
| **C1** | Trạng thái hệ thống | `LONG`, `SHORT`, `CHỜ`, `STOP`, `XÓA CHỜ`, `XÓA VỊ THẾ` |
| **E2** | Vốn mặc định (USDT) | Số dương (VD: `100`)                                    |

#### **Vùng lệnh SHORT (Hàng 4-53)**

Dành cho các lệnh SHORT (50 mã)

- Bot quét từ hàng 4 đến hàng 53 khi `C1 = SHORT`
- Mỗi hàng đại diện cho 1 symbol
- Bot sẽ đặt lệnh SELL cho các symbol trong vùng này

#### **Vùng lệnh LONG (Hàng 55-104)**

Dành cho các lệnh LONG (50 mã)

- Bot quét từ hàng 55 đến hàng 104 khi `C1 = LONG`
- Mỗi hàng đại diện cho 1 symbol
- Bot sẽ đặt lệnh BUY cho các symbol trong vùng này

**Lưu ý:** Hàng 54 được bỏ qua (khoảng trống giữa 2 vùng)

---

### 2.2. Bảng tổng hợp nhanh các cột

#### **Bảng so sánh: Cấu trúc CŨ vs MỚI**

| Cột | Cấu trúc CŨ (`old`) | Cấu trúc MỚI (`new`) |
|-----|---------------------|----------------------|
| **A** | Symbol (✅ Bắt buộc) | Symbol (✅ Bắt buộc) |
| **B** | Đòn bẩy (✅ Bắt buộc) | *(Bỏ qua)* |
| **C** | Callback Rate % (✅ Bắt buộc) | Tracking: Lệnh vừa khớp (Bot ghi) |
| **D** | Activation Price (✅ Bắt buộc) | Tracking: Mã lệnh hiện tại (Bot ghi) |
| **E** | *(Tùy chọn)* | Tracking: Loại lệnh (Bot ghi) |
| **F** | *(Tùy chọn)* | Tracking/TP (Bot ghi) |
| **G** | *(Tùy chọn)* | Tracking/Giá vào (Bot ghi) |
| **H** | Vốn USDT (❌ Tùy chọn) | *(Bỏ qua)* |
| **I** | *(Bỏ qua)* | Loại lệnh (✅ Bắt buộc) |
| **J** | *(Bỏ qua)* | Đòn bẩy (✅ Bắt buộc) |
| **K** | *(Bỏ qua)* | Callback Rate % (✅* Bắt buộc với TRAILING_STOP) |
| **L** | *(Bỏ qua)* | Activation Price (✅* Bắt buộc với TRAILING_STOP) |
| **M** | *(Bỏ qua)* | Stop Price (✅** Bắt buộc với STOP_LIMIT) |
| **N** | *(Bỏ qua)* | Limit Price (✅** Bắt buộc với STOP_LIMIT/LIMIT) |
| **O** | *(Bỏ qua)* | Vốn USDT (❌ Tùy chọn) |
| **P-Z** | *(Không dùng cho đặt lệnh)* | *(Không dùng cho đặt lệnh)* |

**Chú thích:**
- ✅* = Bắt buộc với TRAILING_STOP
- ✅** = Bắt buộc với STOP_LIMIT hoặc LIMIT

---

### 2.3. Cấu trúc các cột chi tiết

#### **CẤU TRÚC MỚI (Khuyên dùng)**

| Cột     | Ý nghĩa                     | Bắt buộc | Ví dụ                                            |
|---------|-----------------------------|----------|--------------------------------------------------|
| **A**   | Symbol (Mã coin)            | ✅       | `BTC/USDT:USDT`                                  |
| **B-H** | *(Trống hoặc dữ liệu khác)* | ❌       | -                                                |
| **I**   | Loại lệnh                   | ✅       | `TRAILING_STOP`, `STOP_LIMIT`, `LIMIT`, `MARKET` |
| **J**   | Đòn bẩy (Leverage)          | ✅       | `10` (10x), `20` (20x)                           |
| **K**   | Callback Rate (%)           | ✅*      | `1` (1%), `2` (2%)                               |
| **L**   | Activation Price            | ✅*      | `43000`                                          |
| **M**   | Stop Price                  | ✅**     | `42500`                                          |
| **N**   | Limit Price                 | ✅**     | `42000`                                          |
| **O**   | Vốn (USDT)                  | ❌       | `200` (nếu trống dùng E2)                        |
| **C-G** | *(Cột tracking tự động)*    | ❌       | Bot ghi                                          |

**Chú thích:**
- ✅* = Bắt buộc với `TRAILING_STOP`
- ✅** = Bắt buộc với `STOP_LIMIT` hoặc `LIMIT`

#### **CẤU TRÚC CŨ (Backward compatible)**

| Cột   | Ý nghĩa          | Bắt buộc  | Ví dụ           |
|-------|------------------|-----------|-----------------|
| **A** | Symbol           | ✅        | `BTC/USDT:USDT` |
| **B** | Đòn bẩy          | ✅        | `10`            |
| **C** | Callback Rate    | ✅        | `1`             |
| **D** | Activation Price | ✅        | `43000`         |
| **H** | Vốn (USDT)       | ❌        | `200`           |

**⚠️ QUAN TRỌNG - Cấu hình cấu trúc cột:**

Bot **KHÔNG** tự động detect cấu trúc nữa, mà dùng cấu hình trong `config.ini`:

```ini
# Trong config.ini
order_column_structure = new  # 'new' hoặc 'old'
```

**Lý do:**
- ✅ Tránh nhầm lẫn khi có dữ liệu ở cả 2 cột
- ✅ User kiểm soát rõ ràng
- ✅ Đảm bảo đọc đúng cột mong muốn

---

### 📋 **CÁCH XÁC ĐỊNH CẤU TRÚC ĐANG DÙNG:**

#### **Cách 1: Xem config.ini**

Mở file `config.ini` và kiểm tra:

```ini
order_column_structure = new  # ← Đây là cấu trúc đang dùng
```

- `new` = Cấu trúc MỚI (cột I, J, K, L, M, N, O)
- `old` = Cấu trúc CŨ (cột B, C, D, H)

---

#### **Cách 2: Xem log file**

Bot sẽ log cấu trúc đang dùng:

```bash
tail -f hd_order.log | grep "Cấu trúc cột"
```

**Output ví dụ:**
```
2025-01-18 14:30:15 - INFO - Cấu trúc cột: MỚI (từ config) - Symbol: BTC/USDT:USDT, Leverage index: 9, Activation index: 11
```

**Giải thích:**
- `Leverage index: 9` = Đang dùng cột J (cấu trúc MỚI)
- `Leverage index: 1` = Đang dùng cột B (cấu trúc CŨ)

---

#### **Cách 3: Kiểm tra trong Google Sheet**

**Nếu config = `new`:**
- ✅ Phải có dữ liệu ở cột I (loại lệnh), J (đòn bẩy), K (callback), L (activation)
- ✅ Cột B, C, D, H sẽ bị bỏ qua

**Nếu config = `old`:**
- ✅ Phải có dữ liệu ở cột B (đòn bẩy), C (callback), D (activation)
- ✅ Cột I, J, K, L, M, N, O sẽ bị bỏ qua
- ✅ Chỉ hỗ trợ TRAILING_STOP (mặc định)

---

### ⚠️ **LƯU Ý QUAN TRỌNG:**

1. **Phải khớp với Google Sheet:**
   - Config `new` → Sheet phải dùng cột I, J, K, L, M, N, O
   - Config `old` → Sheet phải dùng cột B, C, D, H
   - ⚠️ Nếu không khớp → Bot sẽ đọc sai dữ liệu!

2. **Cấu trúc cũ chỉ hỗ trợ TRAILING_STOP:**
   - Nếu muốn dùng STOP_LIMIT, LIMIT, MARKET → **PHẢI đặt `order_column_structure = new`**
   - Bot sẽ log lỗi nếu dùng `old` với các loại lệnh này

3. **Thay đổi config:**
   - Sửa `config.ini`: `order_column_structure = new` hoặc `old`
   - Lưu file
   - Restart bot để áp dụng

---

### 2.3. Chi tiết các cột trong Sheet "ĐẶT LỆNH (100 MÃ)"

#### **Cột A: Symbol (Mã coin)**

**Chức năng:** Tên cặp giao dịch Futures  
**Bắt buộc:** ✅ Có  
**Ví dụ:** `BTC/USDT:USDT`, `ETH/USDT:USDT`, `PIPPIN/USDT:USDT`

**Lưu ý:**
- Format phải đúng: `SYMBOL/USDT:USDT` (với `:USDT` ở cuối cho Futures)
- Bot sẽ bỏ qua dòng nếu cột A trống

---

#### **Cột B: Đòn bẩy (Cấu trúc CŨ) / Dữ liệu khác (Cấu trúc MỚI)**

**Cấu trúc CŨ (`order_column_structure = old`):**
- **Chức năng:** Đòn bẩy (Leverage) cho lệnh
- **Bắt buộc:** ✅ Có
- **Ví dụ:** `10` (10x), `20` (20x), `50` (50x)
- **Đặc biệt:** Nếu = `N` → Bot sẽ bỏ qua dòng này (không đặt lệnh)

**Cấu trúc MỚI (`order_column_structure = new`):**
- **Chức năng:** Không dùng cho đặt lệnh (có thể chứa dữ liệu khác)
- **Bỏ qua:** Bot không đọc cột này khi dùng cấu trúc mới

---

#### **Cột C: Callback Rate (Cấu trúc CŨ) / Tracking (Cấu trúc MỚI)**

**Cấu trúc CŨ (`order_column_structure = old`):**
- **Chức năng:** Callback Rate (%) cho Trailing Stop
- **Bắt buộc:** ✅ Có (với TRAILING_STOP)
- **Ví dụ:** `1` (1%), `2` (2%), `7.08%`
- **Format:** Có thể có hoặc không có dấu `%` (bot tự động loại bỏ)

**Cấu trúc MỚI (`order_column_structure = new`):**
- **Chức năng:** Tracking - Lệnh vừa khớp (Bot tự động ghi)
- **Nội dung:** Timestamp + Order ID
- **Ví dụ:** `2025-01-15 14:30:25 - Order#12345`

---

#### **Cột D: Activation Price (Cấu trúc CŨ) / Tracking (Cấu trúc MỚI)**

**Cấu trúc CŨ (`order_column_structure = old`):**
- **Chức năng:** Giá kích hoạt (Activation Price) cho Trailing Stop
- **Bắt buộc:** ✅ Có
- **Ví dụ:** `43000`, `5.62269679`, `2500`

**Cấu trúc MỚI (`order_column_structure = new`):**
- **Chức năng:** Tracking - Mã lệnh hiện tại (Bot tự động ghi)
- **Nội dung:** Mã lệnh cascade
- **Ví dụ:** `1a`, `1b`, `1c`, `2a`, `2b`, `2c`, `3a`...

---

#### **Cột E: Tracking / SL (Stop Loss)**

**Cấu trúc CŨ (`order_column_structure = old`):**
- **Chức năng:** Có thể dùng cho dữ liệu khác hoặc tracking

**Cấu trúc MỚI (`order_column_structure = new`):**
- **Chức năng:** Tracking - Loại lệnh đã khớp (Bot tự động ghi)
- **Nội dung:** Loại lệnh
- **Ví dụ:** `TRAILING_STOP`, `STOP_LIMIT`, `LIMIT`, `MARKET`

**Trong sheet thực tế:**
- Có thể hiển thị là "SL" (Stop Loss) trong header
- Có thể chứa giá trị Stop Loss được tính toán hoặc tracking

---

#### **Cột F: TP (Take Profit)**

**Chức năng:** Có thể chứa giá trị Take Profit hoặc tracking  
**Ví dụ:** Giá TP được tính toán, hoặc tracking đòn bẩy đã khớp

**Lưu ý:** Cột này không được sử dụng trực tiếp bởi bot để đặt lệnh, có thể dùng cho tracking hoặc hiển thị

---

#### **Cột G: Mức vốn / Tracking**

**Chức năng:** Có thể chứa mức vốn hoặc tracking  
**Ví dụ:** Giá vào đã khớp (Bot tự động ghi trong cấu trúc mới)

---

#### **Cột H: Vốn USDT (Cấu trúc CŨ) / Dữ liệu khác (Cấu trúc MỚI)**

**Cấu trúc CŨ (`order_column_structure = old`):**
- **Chức năng:** Vốn (Capital) tính bằng USDT cho lệnh này
- **Bắt buộc:** ❌ Không (nếu trống, dùng giá trị từ E2)
- **Ví dụ:** `200`, `150`, `100`

**Cấu trúc MỚI (`order_column_structure = new`):**
- **Chức năng:** Không dùng cho đặt lệnh (có thể chứa dữ liệu khác)

---

#### **Cột I: Loại lệnh (Cấu trúc MỚI)**

**Chức năng:** Loại lệnh muốn đặt  
**Bắt buộc:** ✅ Có (chỉ với cấu trúc MỚI)  
**Giá trị hợp lệ:**
- `TRAILING_STOP` hoặc `TRAILING STOP`
- `STOP_LIMIT` hoặc `STOP LIMIT`
- `LIMIT`
- `MARKET`

**Ví dụ:** `TRAILING_STOP`

**Lưu ý:**
- Nếu trống hoặc không hợp lệ → Mặc định `TRAILING_STOP`
- Không hỗ trợ với cấu trúc CŨ (cấu trúc cũ chỉ có TRAILING_STOP)

---

#### **Cột J: Đòn bẩy (Cấu trúc MỚI)**

**Chức năng:** Đòn bẩy (Leverage) cho lệnh  
**Bắt buộc:** ✅ Có (chỉ với cấu trúc MỚI)  
**Ví dụ:** `10` (10x), `20` (20x), `50` (50x)

**Lưu ý:**
- Phải là số nguyên dương
- Nếu = `N` hoặc không phải số → Bot sẽ bỏ qua dòng này

---

#### **Cột K: Callback Rate (Cấu trúc MỚI)**

**Chức năng:** Callback Rate (%) cho Trailing Stop  
**Bắt buộc:** ✅* Có (với TRAILING_STOP)  
**Ví dụ:** `1` (1%), `2` (2%), `7.08`

**Lưu ý:**
- Chỉ dùng với TRAILING_STOP
- Format: Có thể có hoặc không có dấu `%` (bot tự động loại bỏ)
- Với STOP_LIMIT, LIMIT, MARKET → Không cần (có thể để trống)

---

#### **Cột L: Activation Price (Cấu trúc MỚI)**

**Chức năng:** Giá kích hoạt cho Trailing Stop  
**Bắt buộc:** ✅* Có (với TRAILING_STOP)  
**Ví dụ:** `43000`, `2500`, `5.62269679`

**Lưu ý:**
- Chỉ dùng với TRAILING_STOP
- Với STOP_LIMIT, LIMIT, MARKET → Không cần (có thể để trống)

---

#### **Cột M: Stop Price (Cấu trúc MỚI - STOP_LIMIT)**

**Chức năng:** Giá Stop cho lệnh STOP_LIMIT  
**Bắt buộc:** ✅** Có (với STOP_LIMIT)  
**Ví dụ:** `42500`, `2500`

**Lưu ý:**
- Chỉ dùng với STOP_LIMIT
- Khi giá thị trường chạm Stop Price → Lệnh sẽ kích hoạt và đặt Limit tại Limit Price (cột N)
- Với TRAILING_STOP, LIMIT, MARKET → Không cần (có thể để trống)

---

#### **Cột N: Limit Price (Cấu trúc MỚI - STOP_LIMIT/LIMIT)**

**Chức năng:** Giá Limit cho lệnh STOP_LIMIT hoặc LIMIT  
**Bắt buộc:** ✅** Có (với STOP_LIMIT hoặc LIMIT)  
**Ví dụ:** `42000`, `2495`, `300`

**Lưu ý:**
- **Với STOP_LIMIT:** Là giá Limit sau khi Stop Price kích hoạt
- **Với LIMIT:** Là giá mà lệnh Limit sẽ khớp
- Với TRAILING_STOP, MARKET → Không cần (có thể để trống)

---

#### **Cột O: Vốn USDT (Cấu trúc MỚI)**

**Chức năng:** Vốn (Capital) tính bằng USDT cho lệnh này  
**Bắt buộc:** ❌ Không (nếu trống, dùng giá trị từ E2)  
**Ví dụ:** `200`, `150`, `100`

**Lưu ý:**
- Nếu để trống → Bot sẽ dùng giá trị từ ô E2 (Vốn mặc định)
- Số vốn này sẽ được chia cho giá coin để tính số lượng (amount)

---

#### **Cột P-Z: Dữ liệu tracking/khác**

**Chức năng:** Các cột này không được bot sử dụng trực tiếp để đặt lệnh  
**Nội dung:** Có thể chứa:
- Dữ liệu tracking tự động từ bot
- Dữ liệu thị trường (Volume, Bollinger Bands, High/Low...)
- Các tính toán khác từ sheet formulas

**Lưu ý:** Bot đọc đến cột Z khi scan sheet (`A{start_row}:Z{end_row}`), nhưng chỉ sử dụng các cột được liệt kê ở trên để đặt lệnh.

---

### 2.4. Ví dụ nhập liệu thực tế

#### **Ví dụ 1: Cấu trúc CŨ - Đặt lệnh TRAILING STOP LONG**

| A | B | C | D | H |
|---|---|---|---|---|
| BTC/USDT:USDT | 10 | 1 | 43000 | 200 |

**Giải thích:**
- A: Symbol
- B: Đòn bẩy 10x
- C: Callback 1%
- D: Activation Price 43000
- H: Vốn 200 USDT

---

#### **Ví dụ 2: Cấu trúc MỚI - Đặt lệnh TRAILING STOP LONG**

| A | I | J | K | L | O |
|---|---|---|---|---|---|
| BTC/USDT:USDT | TRAILING_STOP | 10 | 1 | 43000 | 200 |

**Giải thích:**
- A: Symbol
- I: Loại lệnh TRAILING_STOP
- J: Đòn bẩy 10x
- K: Callback 1%
- L: Activation Price 43000
- O: Vốn 200 USDT

---

#### **Ví dụ 3: Cấu trúc MỚI - Đặt lệnh STOP_LIMIT SHORT**

| A | I | J | M | N | O |
|---|---|---|---|---|---|
| ETH/USDT:USDT | STOP_LIMIT | 20 | 2500 | 2495 | 150 |

**Giải thích:**
- A: Symbol
- I: Loại lệnh STOP_LIMIT
- J: Đòn bẩy 20x
- M: Stop Price 2500
- N: Limit Price 2495
- O: Vốn 150 USDT

**Lưu ý:** Với STOP_LIMIT, cột K và L (Callback, Activation) không cần, chỉ cần M và N.

---

### 2.5. Cột tracking tự động (Bot tự ghi)

Bot sẽ tự động ghi các cột tracking sau khi lệnh được đặt (theo cấu trúc MỚI):

| Cột | Nội dung | Ví dụ |
|-----|----------|-------|
| **C** | Lệnh vừa khớp | `2025-01-15 14:30:25 - Order#12345` |
| **D** | Mã lệnh hiện tại | `1a`, `1b`, `1c`, `2a`... |
| **E** | Loại lệnh | `TRAILING_STOP`, `STOP_LIMIT`... |
| **F** | Đòn bẩy đã khớp | `10x` |
| **G** | Giá vào đã khớp | `43125.50` |

**Lưu ý:** Tracking chỉ hoạt động với cấu trúc MỚI. Với cấu trúc CŨ, các cột này có thể được dùng cho mục đích khác.

---

## 3. CÁC LOẠI LỆNH HỖ TRỢ

### 3.1. TRAILING STOP (Khuyên dùng)

**Đặc điểm:**
- Lệnh chờ, chỉ kích hoạt khi giá chạm `Activation Price`
- Sau khi kích hoạt, lệnh "đuổi theo" giá với khoảng cách `Callback Rate`
- Tự động khớp khi giá đảo chiều `Callback Rate` %

**Khi nào dùng:**
- ✅ Entry vào lệnh theo xu hướng
- ✅ Take Profit tự động
- ✅ Tối ưu lợi nhuận khi giá tiếp tục đi đúng xu hướng

**Ưu điểm:**
- Linh hoạt, theo sát giá
- Không bị "bỏ lỡ" khi giá tiếp tục tăng/giảm

**Nhược điểm:**
- Phức tạp hơn các lệnh khác
- Có thể bị "vẩy" trong thị trường sideway

---

### 3.2. STOP LIMIT

**Đặc điểm:**
- Lệnh chờ, kích hoạt khi giá chạm `Stop Price`
- Sau khi kích hoạt, đặt lệnh Limit tại `Limit Price`

**Khi nào dùng:**
- ✅ Stop Loss (cắt lỗ)
- ✅ Entry vào lệnh tại mức giá cụ thể

**Ưu điểm:**
- Đảm bảo giá khớp tại `Limit Price` (hoặc tốt hơn)
- Kiểm soát giá rõ ràng

**Nhược điểm:**
- Có thể không khớp nếu giá vượt quá Limit quá nhanh

---

### 3.3. LIMIT

**Đặc điểm:**
- Lệnh chờ tại một mức giá cụ thể
- Chỉ khớp khi giá chạm `Limit Price`

**Khi nào dùng:**
- ✅ Entry vào lệnh khi giá pullback
- ✅ Mua/bán tại mức giá mong muốn

**Ưu điểm:**
- Đơn giản, dễ hiểu
- Kiểm soát giá tuyệt đối

**Nhược điểm:**
- Có thể bỏ lỡ entry nếu giá không chạm Limit

---

### 3.4. MARKET

**Đặc điểm:**
- Lệnh khớp ngay tại giá thị trường
- Không có giá chờ

**Khi nào dùng:**
- ✅ Entry/Exit khẩn cấp
- ✅ Đóng vị thế nhanh

**Ưu điểm:**
- Đảm bảo 100% khớp ngay
- Nhanh, đơn giản

**Nhược điểm:**
- Giá khớp có thể kém hơn mong đợi (slippage)

---

## 4. HƯỚNG DẪN ĐẶT LỆNH TỪNG LOẠI

### 4.1. Đặt lệnh TRAILING STOP

#### **Bước 1: Chuẩn bị dữ liệu**

```
| A (Symbol)        | I (Loại)      | J (Leverage) | K (Callback) | L (Activation) | O (Vốn) |
|-------------------|---------------|--------------|--------------|----------------|---------|
| BTC/USDT:USDT     | TRAILING_STOP | 10           | 1            | 43000          | 200     |
```

#### **Bước 2: Giải thích các tham số**

- **Symbol:** `BTC/USDT:USDT` - Cặp giao dịch Bitcoin Futures
- **Loại lệnh:** `TRAILING_STOP`
- **Leverage:** `10` = Đòn bẩy 10x
- **Callback Rate:** `1` = 1% (lệnh khớp khi giá đảo chiều 1%)
- **Activation Price:** `43000` = Giá kích hoạt
- **Vốn:** `200` USDT

#### **Bước 3: Kịch bản thực tế**

**Trường hợp LONG:**

1. Giá hiện tại: `42500`
2. Bot tạo lệnh TRAILING STOP **BUY** với Activation = `43000`
3. **Chờ:** Giá tăng lên `43000` → Lệnh **kích hoạt**
4. **Tracking:** Giá tiếp tục tăng → `43500` → `44000`
5. **Khớp:** Giá đảo chiều giảm `1%` (từ `44000` về `43560`) → Lệnh **khớp** tại ~`43560`

**Kết quả:** Entry LONG tại `43560` với đòn bẩy 10x

---

### 4.2. Đặt lệnh STOP LIMIT

#### **Bước 1: Chuẩn bị dữ liệu**

```
| A (Symbol)        | I (Loại)     | J (Leverage) | M (Stop) | N (Limit) | O (Vốn) |
|-------------------|--------------|--------------|----------|-----------|---------|
| ETH/USDT:USDT     | STOP_LIMIT   | 20           | 2500     | 2495      | 150     |
```

#### **Bước 2: Giải thích**

- **Stop Price:** `2500` - Giá kích hoạt
- **Limit Price:** `2495` - Giá lệnh Limit sau khi kích hoạt

#### **Bước 3: Kịch bản (SHORT)**

1. Giá hiện tại: `2550`
2. Bot tạo lệnh STOP LIMIT **SELL** với Stop = `2500`, Limit = `2495`
3. Giá giảm xuống `2500` → Lệnh **kích hoạt**
4. Đặt lệnh Limit SELL tại `2495`
5. Giá tiếp tục giảm, chạm `2495` → Lệnh **khớp**

**Kết quả:** Entry SHORT tại `2495` với đòn bẩy 20x

---

### 4.3. Đặt lệnh LIMIT

#### **Bước 1: Chuẩn bị dữ liệu**

```
| A (Symbol)        | I (Loại) | J (Leverage) | N (Limit) | O (Vốn) |
|-------------------|----------|--------------|-----------|---------|
| BNB/USDT:USDT     | LIMIT    | 15           | 300       | 100     |
```

#### **Bước 2: Kịch bản (LONG)**

1. Giá hiện tại: `310`
2. Bot tạo lệnh LIMIT **BUY** tại `300`
3. **Chờ:** Giá pullback về `300`
4. **Khớp:** Lệnh khớp tại `300`

**Kết quả:** Entry LONG tại `300` với đòn bẩy 15x

---

### 4.4. Đặt lệnh MARKET

#### **Bước 1: Chuẩn bị dữ liệu**

```
| A (Symbol)        | I (Loại) | J (Leverage) | O (Vốn) |
|-------------------|----------|--------------|---------|
| SOL/USDT:USDT     | MARKET   | 10           | 80      |
```

#### **Bước 2: Kịch bản**

1. Bot đọc lệnh MARKET
2. Lập tức tạo lệnh **BUY** hoặc **SELL** (tùy vùng LONG/SHORT) tại giá thị trường
3. Lệnh **khớp ngay**

**Kết quả:** Entry ngay lập tức tại giá thị trường

---

## 5. LOGIC CASCADE ĐA LỚP

### 5.1. Khái niệm

**Cascade = Lệnh tầng bậc tự động**

Khi lệnh Entry (1a, 2a, 3a...) khớp, bot tự động tạo:
- **Stop Loss** (1b, 2b, 3b...)
- **Take Profit** (1c, 2c, 3c...)
- **Entry lớp tiếp theo** (2a, 3a...)

### 5.2. Sơ đồ flow

```
┌────────┐
│  1a    │  ← Entry lớp 1 (User đặt)
│ KHỚP   │
└───┬────┘
    │
    ├──→ Tạo 1b (Stop Loss)
    ├──→ Tạo 1c (Take Profit)
    └──→ Tạo 2a (Entry lớp 2)
         │
         └──→ Khi 2a KHỚP
              ├──→ Tạo 2b (Stop Loss)
              ├──→ Tạo 2c (Take Profit)
              └──→ Tạo 3a (Entry lớp 3)
                   ...
```

### 5.3. Cấu hình Cascade

**Trong config.ini:**

```ini
[CASCADE]
max_layers = 3              # Tối đa 3 lớp (1a→2a→3a)
lenh2_rate = 5              # SL cách Entry 5% (có tính đòn bẩy)
lenh3_rate = 10             # TP kích hoạt tại +10%
lenh3_callback_rate = 1     # TP callback 1%
```

### 5.4. Ví dụ chi tiết

#### **Kịch bản:**

1. User đặt lệnh **1a LONG** BTC tại `43000` (Leverage 10x)
2. **Lệnh 1a khớp** tại `43000`
3. Bot **TỰ ĐỘNG** tạo:
   - **1b (SL):** Stop Loss tại `42785` (giảm 5% so với Entry, tính theo leverage)
     - Công thức: `43000 * (1 - 5% / 10) = 42785`
   - **1c (TP):** Trailing Stop, Activation = `43430` (tăng 10%)
     - Công thức: `43000 * (1 + 10% / 10) = 43430`
     - Callback: 1%
   - **2a (Entry lớp 2):** Trailing Stop mới (nếu config cho phép)

#### **Trường hợp TP khớp:**

4. Giá tăng lên `44000`, sau đó đảo chiều về `43560`
5. **Lệnh 1c (TP) khớp** tại `43560`
6. Bot **TỰ ĐỘNG HỦY:**
   - ✅ Hủy **1b (SL)**
   - ✅ Hủy **2a (Entry lớp 2)** nếu chưa khớp

#### **Trường hợp SL khớp:**

4. Giá giảm xuống `42785`
5. **Lệnh 1b (SL) khớp**
6. Bot **TỰ ĐỘNG HỦY:**
   - ✅ Hủy **1c (TP)**
   - ❌ **KHÔNG** hủy **2a** (vẫn có thể entry lại)

---

## 6. CÁC TRẠNG THÁI HỆ THỐNG

### 6.1. Trạng thái trong ô C1

| Trạng thái | Ý nghĩa | Hành động |
|------------|---------|-----------|
| **CHỜ** | Bot không làm gì | Không quét lệnh |
| **LONG** | Quét vùng LONG (hàng 55-104) | Đặt lệnh BUY |
| **SHORT** | Quét vùng SHORT (hàng 4-53) | Đặt lệnh SELL |
| **STOP** | Dừng tất cả | Đóng vị thế + Hủy lệnh chờ |
| **XÓA CHỜ** | Xóa lệnh chờ | Hủy tất cả pending orders, giữ vị thế |
| **XÓA VỊ THẾ** | Xóa vị thế | Đóng tất cả positions, giữ lệnh chờ |

### 6.2. Chi tiết từng trạng thái

#### **CHỜ**
- Bot chạy nhưng không đặt lệnh mới
- Dùng khi muốn tạm dừng trading

#### **LONG / SHORT**
- Bot quét sheet và đặt lệnh theo hướng đã chọn
- Chỉ đặt lệnh nếu:
  - ✅ Cột J (Leverage) khác `N`
  - ✅ Chưa có vị thế hoặc lệnh chờ cho symbol đó

#### **STOP** (Khẩn cấp)

**Hành động:**

1. Đóng **TẤT CẢ** vị thế đang mở (Market order)
2. Hủy **TẤT CẢ** lệnh chờ
3. Gửi thông báo Telegram

**Khi nào dùng:**
- 🚨 Thị trường đột biến
- 🚨 Rủi ro cao, muốn thoát toàn bộ

**Lưu ý:**
- ⚠️ **KHÔNG THỂ HOÀN TÁC**
- ⚠️ Có thể bị slippage cao

#### **XÓA CHỜ**

**Hành động:**
- Hủy tất cả lệnh chờ (pending orders)
- **KHÔNG** đóng vị thế đang mở

**Khi nào dùng:**
- Muốn reset lệnh chờ mà không ảnh hưởng vị thế
- Thay đổi chiến lược entry

#### **XÓA VỊ THẾ**

**Hành động:**
- Đóng tất cả vị thế đang mở
- **KHÔNG** hủy lệnh chờ

**Khi nào dùng:**
- Muốn thoát vị thế nhưng giữ lệnh chờ
- Chốt lời/lỗ mà vẫn giữ setup entry

---

## 7. VÍ DỤ THỰC TẾ

### 7.1. Ví dụ 1: Đặt lệnh LONG BTC đơn giản

#### **Mục tiêu:**
- Entry LONG BTC khi giá chạm `43000`
- Sử dụng Trailing Stop, đòn bẩy 10x
- Vốn: `200 USDT`

#### **Các bước:**

1. **Mở Google Sheet "ĐẶT LỆNH (100 MÃ)"**

2. **Đặt trạng thái hệ thống:**
   - Ô **C1** = `LONG`
   - Ô **E2** = `200` (vốn mặc định)

3. **Nhập dữ liệu vào vùng LONG (VD: Hàng 55):**

   | A | I | J | K | L | O |
   |---|---|---|---|---|---|
   | BTC/USDT:USDT | TRAILING_STOP | 10 | 1 | 43000 | 200 |

4. **Lưu sheet**

5. **Bot sẽ:**
   - Quét hàng 55
   - Phát hiện lệnh mới (symbol chưa có vị thế/lệnh chờ)
   - Đặt lệnh Trailing Stop BUY với:
     - Activation: `43000`
     - Callback: `1%`
     - Amount: `200 / giá_BTC`
   - Gửi thông báo Telegram: ✅ **LỆNH CHỜ (TRAILING STOP)**

6. **Khi lệnh khớp:**
   - Bot ghi vào cột C-G:
     - C: Timestamp + Order ID
     - D: `1a`
     - E: `TRAILING_STOP`
     - F: `10x`
     - G: Giá khớp thực tế
   - Cascade Manager tự động tạo 1b (SL) + 1c (TP)

---

### 7.2. Ví dụ 2: Đặt nhiều lệnh SHORT

#### **Mục tiêu:**
- Đặt 3 lệnh SHORT cho ETH, BNB, SOL
- Sử dụng Stop Limit
- Đòn bẩy khác nhau

#### **Các bước:**

1. **Đặt C1 = `SHORT`**

2. **Nhập vào vùng SHORT (Hàng 4-6):**

   | A | I | J | M | N | O |
   |---|---|---|---|---|---|
   | ETH/USDT:USDT | STOP_LIMIT | 20 | 2500 | 2495 | 150 |
   | BNB/USDT:USDT | STOP_LIMIT | 15 | 310 | 308 | 100 |
   | SOL/USDT:USDT | STOP_LIMIT | 10 | 95 | 94 | 80 |

3. **Bot sẽ đặt 3 lệnh:**
   - ETH: SELL Stop Limit @ Stop=2500, Limit=2495
   - BNB: SELL Stop Limit @ Stop=310, Limit=308
   - SOL: SELL Stop Limit @ Stop=95, Limit=94

4. **Khi giá chạm Stop Price:**
   - Từng lệnh sẽ chuyển sang Limit
   - Khi khớp → Cascade tạo SL/TP tự động

---

### 7.3. Ví dụ 3: Sử dụng STOP khẩn cấp

#### **Tình huống:**
- Đang có 5 vị thế LONG đang lỗ
- Thị trường crash, muốn thoát toàn bộ

#### **Hành động:**

1. **Đổi C1 = `STOP`**
2. Bot lập tức:
   - Đóng 5 vị thế LONG (Market Sell)
   - Hủy tất cả lệnh chờ
   - Gửi Telegram: ✅ **HOÀN TẤT STOP**
     ```
     Vị thế đã đóng: 5
     Lệnh đã hủy: 10
     Thời gian: 2025-01-15 15:30:45
     ```

---

## 8. XỬ LÝ LỖI & TROUBLESHOOTING

### 8.1. Lỗi thường gặp

#### **Lỗi 1: Bot không đặt lệnh**

**Nguyên nhân:**
- C1 = `CHỜ`
- Symbol đã có vị thế hoặc lệnh chờ
- Cột Leverage = `N` hoặc không phải số
  - **Cấu trúc CŨ:** Cột B = `N`
  - **Cấu trúc MỚI:** Cột J = `N`

**Giải pháp:**
1. Kiểm tra C1 phải là `LONG` hoặc `SHORT`
2. Kiểm tra trên Binance: Có vị thế/lệnh chờ chưa?
3. Đảm bảo cột Leverage là số (VD: `10`)
   - **Cấu trúc CŨ:** Kiểm tra cột B
   - **Cấu trúc MỚI:** Kiểm tra cột J
4. Kiểm tra `config.ini`: `order_column_structure` khớp với cấu trúc trong sheet

---

#### **Lỗi 2: API -4120 (Trailing Stop)**

**Nguyên nhân:**
- Binance thay đổi endpoint cho Trailing Stop

**Giải pháp:**
- ✅ Bot tự động fallback sang Algo Order API
- Không cần can thiệp
- Nếu vẫn lỗi: Check log `hd_order.log`

---

#### **Lỗi 3: Leverage không set được**

**Nguyên nhân:**
- Symbol chưa enable Futures
- Leverage vượt quá max cho phép

**Giải pháp:**
1. Vào Binance Futures → Settings
2. Enable symbol
3. Check max leverage (BTC thường 125x, altcoin 50x-20x)

---

#### **Lỗi 4: Insufficient margin**

**Nguyên nhân:**
- Không đủ USDT trong ví Futures

**Giải pháp:**
1. Chuyển USDT từ Spot → Futures
2. Giảm vốn cột O
3. Giảm đòn bẩy cột J

---

#### **Lỗi 5: Bot không tạo SL/TP tự động**

**Nguyên nhân:**
- Chưa enable Cascade trong config
- Module `hd_order_123.py` chưa chạy

**Giải pháp:**
1. Check `config.ini`:
   ```ini
   [CASCADE]
   enabled = true
   max_layers = 3
   ```
2. Chạy: `python hd_order_123.py`

---

### 8.2. Kiểm tra logs

#### **File log chính:**

```bash
# Log chính
tail -f hd_order.log

# Log cascade
tail -f cascade_manager.log

# Log tất cả
tail -f *.log
```

#### **Ví dụ log thành công:**

```
2025-01-15 14:30:15 - INFO - Scan Vào Lệnh----
2025-01-15 14:30:15 - INFO - Trạng thái: LONG, Vốn mặc định: 200
2025-01-15 14:30:16 - INFO - --- Vào lệnh 1 LONG: BTC/USDT:USDT TRAILING_STOP đòn bẩy: 10
2025-01-15 14:30:17 - INFO - ✅ Lệnh TRAILING_STOP đã được tạo: Order ID 123456
```

---

### 8.3. Debug mode

Để bật debug chi tiết, sửa trong `hd_order.py`:

```python
logging.basicConfig(
    filename='hd_order.log', 
    level=logging.DEBUG,  # Thay INFO → DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 9. TIPS & BEST PRACTICES

### 9.1. Quản lý rủi ro

✅ **Nên:**
- Dùng vốn nhỏ để test (20-50 USDT)
- Đặt Stop Loss rõ ràng
- Không dùng đòn bẩy quá cao (khuyên ≤ 20x)
- Đa dạng hóa (nhiều coin, không all-in 1 lệnh)

❌ **Không nên:**
- All-in 1 lệnh
- Dùng đòn bẩy >50x
- Đặt lệnh khi không hiểu rõ
- Không theo dõi khi có lệnh đang chạy

---

### 9.2. Tối ưu entry

**Trailing Stop:**
- ✅ Dùng cho trend mạnh
- ✅ Callback Rate 1-2% (không quá nhỏ)

**Stop Limit:**
- ✅ Dùng cho entry tại support/resistance
- ✅ Limit Price cách Stop ~0.1-0.3%

**Limit:**
- ✅ Dùng khi chắc chắn giá về mức đó
- ✅ Đặt tại Fibonacci retracement levels

---

### 9.3. Theo dõi bot

**Hàng ngày:**
- Check Telegram notifications
- Xem log nếu có cảnh báo
- Kiểm tra PNL trên Binance

**Hàng tuần:**
- Review chiến lược
- Điều chỉnh config nếu cần
- Backup log files

---

## 10. KẾT LUẬN

### 10.1. Checklist trước khi bắt đầu

- [ ] Đã cài đặt bot đầy đủ
- [ ] Đã config `config.ini` với API keys
- [ ] Đã test Telegram notification
- [ ] Có đủ USDT trong Futures wallet
- [ ] Đã hiểu rõ các loại lệnh
- [ ] Đã test với vốn nhỏ
- [ ] Biết cách sử dụng STOP khẩn cấp

### 10.2. Liên hệ hỗ trợ

**Nếu gặp vấn đề:**

1. Đọc phần [Troubleshooting](#8-xử-lý-lỗi--troubleshooting)
2. Check log files
3. Tham khảo `README.md` và `HUONG_DAN_SU_DUNG.md`
4. Liên hệ developer

---

**Chúc bạn trade hiệu quả! 🚀📈**

*Tài liệu được cập nhật: 2025-01-18*
*Version: QBot v2.0*
