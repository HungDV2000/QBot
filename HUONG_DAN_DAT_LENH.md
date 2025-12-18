# HƯỚNG DẪN ĐẶT LỆNH - QBOT (THEO QUY TRÌNH THỰC TẾ)

## 📋 MỤC LỤC

1. [Tổng quan hệ thống đặt lệnh](#1-tổng-quan-hệ-thống-đặt-lệnh)
2. [Cấu trúc Google Sheet](#2-cấu-trúc-google-sheet)
3. [Hướng dẫn đặt lệnh](#3-hướng-dẫn-đặt-lệnh)
4. [Logic Cascade (Lệnh 2 & 3 tự động)](#4-logic-cascade-lệnh-2--3-tự-động)
5. [Các trạng thái hệ thống](#5-các-trạng-thái-hệ-thống)
6. [Ví dụ thực tế](#6-ví-dụ-thực-tế)
7. [Xử lý lỗi & Troubleshooting](#7-xử-lý-lỗi--troubleshooting)

---

## 1. TỔNG QUAN HỆ THỐNG ĐẶT LỆNH

### 1.1. Luồng hoạt động

```
┌─────────────────┐
│ Google Sheet    │  ← User nhập dữ liệu (A, B, C, D, H)
│ (ĐẶT LỆNH)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  hd_order.py    │  ← Bot scan sheet mỗi 60s (delay_vao_lenh)
│  (Main Script)  │     Đọc B2 (trạng thái), E2 (vốn)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Binance API     │  ← Đặt lệnh TRAILING_STOP
│                 │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Cascade Manager │  ← Tự động tạo Lệnh 2 (SL) + Lệnh 3 (TP)
│                 │
└─────────────────┘
```

### 1.2. File liên quan

| File                      | Chức năng                                                      |
|---------------------------|----------------------------------------------------------------|
| `hd_order.py`             | Script chính quét sheet và đặt lệnh TRAILING_STOP              |
| `binance_order_helper.py` | Xử lý lệnh Trailing Stop                                       |
| `cascade_manager.py`      | Quản lý logic cascade (Lệnh 1 khớp → Tự động tạo Lệnh 2 & 3)  |
| `gg_sheet_factory.py`     | Đọc/ghi dữ liệu Google Sheets                                  |

### 1.3. Tần suất quét

Bot quét sheet mỗi **60 giây** (mặc định):

```ini
# Trong config.ini
delay_vao_lenh = 60  # Quét mỗi 60 giây
```

---

## 2. CẤU TRÚC GOOGLE SHEET

### 2.1. Sheet "ĐẶT LỆNH (100 MÃ)"

#### **Ô điều khiển (Control Cells)**

| Ô      | Ý nghĩa             | Giá trị hợp lệ                                          |
|--------|---------------------|---------------------------------------------------------|
| **B2** | Trạng thái hệ thống | `LONG`, `SHORT`, `CHỜ`, `STOP`, `XÓA CHỜ`, `XÓA VỊ THẾ` |
| **E2** | Vốn mặc định (USDT) | Số dương (VD: `1.12`)                                   |

#### **Vùng lệnh SHORT (Hàng 4-53)**

- Bot quét từ hàng 4 đến hàng 53 khi `B2 = SHORT`
- Mỗi hàng đại diện cho 1 symbol
- Bot sẽ đặt lệnh SELL cho các symbol trong vùng này

#### **Vùng lệnh LONG (Hàng 55-104)**

- Bot quét từ hàng 55 đến hàng 104 khi `B2 = LONG`
- Mỗi hàng đại diện cho 1 symbol
- Bot sẽ đặt lệnh BUY cho các symbol trong vùng này

**Lưu ý:** Hàng 54 được bỏ qua (khoảng trống giữa 2 vùng)

---

### 2.2. Cấu trúc cột (CỐ ĐỊNH)

| Cột   | Ý nghĩa          | Bắt buộc  | Ví dụ                     | Ghi chú                              |
|-------|------------------|-----------|---------------------------|--------------------------------------|
| **A** | Symbol           | ✅        | `AIOT/USDT`, `BTC/USDT`   | Format: `SYMBOL/USDT` (không `:USDT`) |
| **B** | Đòn bẩy          | ✅        | `1`, `10`, `20`           | Nếu = `N` hoặc `0` → Bỏ qua dòng    |
| **C** | Callback Rate %  | ✅        | `2%`, `1`, `7.08%`        | Có thể có hoặc không có dấu `%`      |
| **D** | Activation Price | ✅        | `0.08798470376`, `43000`  | Giá kích hoạt Trailing Stop          |
| **H** | Vốn (USDT)       | ❌        | `200`, `150`, `100`       | Nếu trống, dùng E2                   |

**⚠️ QUAN TRỌNG:**
- Chỉ hỗ trợ **TRAILING_STOP** (theo quy trình thực tế)
- Không hỗ trợ STOP_LIMIT, LIMIT, MARKET
- Bot chỉ đặt lệnh nếu **B ≠ 0, B ≠ "N", và B là số > 0**

---

### 2.3. Ví dụ nhập liệu

#### **Ví dụ 1: Đặt lệnh LONG AIOT/USDT**

| A | B | C | D | H |
|---|---|---|---|---|
| AIOT/USDT | 1 | 2% | 0.08798470376 | *(trống, dùng E2)* |

**Giải thích:**
- A: Symbol
- B: Đòn bẩy 1x
- C: Callback 2%
- D: Activation Price
- H: Trống → Dùng vốn từ E2

---

#### **Ví dụ 2: Bỏ qua dòng**

| A | B | C | D | H |
|---|---|---|---|---|
| ACT/USDT | N | 2.90% | 0.148041107 | |

**Giải thích:**
- B = `N` → **Bot sẽ BỎ QUA dòng này** (không đặt lệnh)

---

## 3. HƯỚNG DẪN ĐẶT LỆNH

### 3.1. Lệnh 1 (Entry - TRAILING STOP)

**Bước 1: Chuẩn bị dữ liệu**

| A (Symbol)    | B (Leverage) | C (Callback) | D (Activation)   | H (Vốn)  |
|---------------|--------------|--------------|------------------|----------|
| AIOT/USDT     | 1            | 2%           | 0.08798470376    | *(E2)*   |

**Bước 2: Đặt trạng thái**

- Ô **B2** = `LONG` (hoặc `SHORT`)
- Ô **E2** = `1.12` (vốn mặc định)

**Bước 3: Bot sẽ:**

1. Quét hàng 55-104 (nếu LONG) hoặc 4-53 (nếu SHORT)
2. Tìm dòng có **B ≠ 0, B ≠ "N"**
3. Đặt lệnh TRAILING_STOP:
   - Symbol: `AIOT/USDT:USDT`
   - Side: BUY (nếu LONG) hoặc SELL (nếu SHORT)
   - Leverage: 1x
   - Activation: 0.08798470376
   - Callback: 2%
   - Capital: 1.12 USDT (từ E2)
4. Gửi thông báo Telegram

---

### 3.2. Cách hoạt động của TRAILING STOP

**Kịch bản LONG:**

1. Giá hiện tại: `0.087` (thấp hơn Activation)
2. Bot tạo lệnh TRAILING STOP **BUY** với Activation = `0.08798`
3. **Chờ:** Giá tăng lên `0.08798` → Lệnh **kích hoạt**
4. **Tracking:** Giá tiếp tục tăng → `0.089` → `0.090`
5. **Khớp:** Giá đảo chiều giảm `2%` (từ `0.090` về `0.0882`) → Lệnh **khớp** tại ~`0.0882`

**Kết quả:** Entry LONG tại `0.0882` với đòn bẩy 1x

---

## 4. LOGIC CASCADE (LỆNH 2 & 3 TỰ ĐỘNG)

### 4.1. Khái niệm

Khi **Lệnh 1 (Entry) khớp**, bot **TỰ ĐỘNG** tạo:

- **Lệnh 2 (Stop Loss):** STOP LIMIT - Cắt lỗ khi giá đi ngược kỳ vọng
- **Lệnh 3 (Take Profit):** TRAILING_STOP - Chốt lời khi giá đi đúng kỳ vọng

### 4.2. Công thức

**Config trong `config.ini`:**

```ini
lenh2_rate_long = 0.3      # Cắt lỗ LONG: -30%
lenh2_rate_short = 0.3     # Cắt lỗ SHORT: +30%
lenh3_rate_long = 0.6      # Chốt lời LONG: +60%
lenh3_rate_short = 0.6     # Chốt lời SHORT: -60%
lenh3_callback_rate = 1    # TP callback: 1%
```

**Lệnh 2 (Stop Loss):**

```python
# LONG
SL Price = Giá vào × (1 - 0.3) = Giá vào × 0.7   # Giảm 30%

# SHORT
SL Price = Giá vào × (1 + 0.3) = Giá vào × 1.3   # Tăng 30%
```

**Lệnh 3 (Take Profit):**

```python
# LONG
TP Activation = Giá vào × (1 + 0.6) = Giá vào × 1.6   # Tăng 60%
TP Callback = 1%

# SHORT
TP Activation = Giá vào × (1 - 0.6) = Giá vào × 0.4   # Giảm 60%
TP Callback = 1%
```

---

### 4.3. Ví dụ chi tiết

#### **Kịch bản:**

1. User đặt lệnh **LONG AIOT** tại `0.08798` (Leverage 1x)
2. **Lệnh 1 khớp** tại `0.08798`
3. Bot **TỰ ĐỘNG** tạo:
   - **Lệnh 2 (SL):** STOP LIMIT SELL @ `0.08798 × 0.7 = 0.06159` (giảm 30%)
   - **Lệnh 3 (TP):** TRAILING_STOP SELL, Activation = `0.08798 × 1.6 = 0.14077` (tăng 60%), Callback = 1%

#### **Trường hợp TP khớp:**

4. Giá tăng lên `0.15`, sau đó đảo chiều về `0.1485`
5. **Lệnh 3 (TP) khớp** tại `0.1485`
6. Bot **TỰ ĐỘNG HỦY Lệnh 2 (SL)**

**Kết quả:** Chốt lời ~68% (0.1485 / 0.08798 - 1)

#### **Trường hợp SL khớp:**

4. Giá giảm xuống `0.06159`
5. **Lệnh 2 (SL) khớp** tại `0.06159`
6. Bot **TỰ ĐỘNG HỦY Lệnh 3 (TP)**

**Kết quả:** Cắt lỗ -30%

---

## 5. CÁC TRẠNG THÁI HỆ THỐNG

### 5.1. Trạng thái trong ô B2

| Trạng thái | Ý nghĩa | Hành động |
|------------|---------|-----------|
| **CHỜ** | Bot không làm gì | Không quét lệnh |
| **LONG** | Quét vùng LONG (hàng 55-104) | Đặt lệnh BUY |
| **SHORT** | Quét vùng SHORT (hàng 4-53) | Đặt lệnh SELL |
| **STOP** | Dừng tất cả | Đóng vị thế + Hủy lệnh chờ |
| **XÓA CHỜ** | Xóa lệnh chờ | Hủy tất cả pending orders, giữ vị thế |
| **XÓA VỊ THẾ** | Xóa vị thế | Đóng tất cả positions, giữ lệnh chờ |

### 5.2. Chi tiết

#### **CHỜ**
- Bot chạy nhưng không đặt lệnh mới
- Dùng khi muốn tạm dừng trading

#### **LONG / SHORT**
- Bot quét sheet và đặt lệnh theo hướng đã chọn
- Chỉ đặt lệnh nếu:
  - ✅ Cột B (Leverage) ≠ `N`, ≠ `0`, và > 0
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

---

## 6. VÍ DỤ THỰC TẾ

### 6.1. Ví dụ 1: Đặt lệnh LONG AIOT đơn giản

#### **Mục tiêu:**
- Entry LONG AIOT khi giá chạm `0.08798`
- Sử dụng Trailing Stop, đòn bẩy 1x
- Vốn: `1.12 USDT`

#### **Các bước:**

1. **Mở Google Sheet "ĐẶT LỆNH (100 MÃ)"**

2. **Đặt trạng thái:**
   - Ô **B2** = `LONG`
   - Ô **E2** = `1.12`

3. **Nhập dữ liệu vào hàng 55 (ví dụ):**

   | A | B | C | D |
   |---|---|---|---|
   | AIOT/USDT | 1 | 2% | 0.08798470376 |

4. **Lưu sheet**

5. **Bot sẽ (sau tối đa 60s):**
   - Quét hàng 55
   - Phát hiện lệnh mới (symbol chưa có vị thế/lệnh chờ)
   - Đặt lệnh Trailing Stop BUY:
     - Activation: `0.08798470376`
     - Callback: `2%`
     - Amount: `1.12 / 0.087` ~ `12.87` AIOT
   - Gửi Telegram: ✅ **LỆNH CHỜ (TRAILING STOP)**

6. **Khi lệnh khớp:**
   - Cascade Manager tự động tạo Lệnh 2 (SL) + Lệnh 3 (TP)

---

### 6.2. Ví dụ 2: Sử dụng STOP khẩn cấp

#### **Tình huống:**
- Đang có 5 vị thế LONG đang lỗ
- Thị trường crash, muốn thoát toàn bộ

#### **Hành động:**

1. **Đổi B2 = `STOP`**
2. Bot lập tức:
   - Đóng 5 vị thế LONG (Market Sell)
   - Hủy tất cả lệnh chờ
   - Gửi Telegram: ✅ **HOÀN TẤT STOP**

---

## 7. XỬ LÝ LỖI & TROUBLESHOOTING

### 7.1. Lỗi thường gặp

#### **Lỗi 1: Bot không đặt lệnh**

**Nguyên nhân:**
- B2 = `CHỜ`
- Symbol đã có vị thế hoặc lệnh chờ
- Cột B = `N` hoặc `0`

**Giải pháp:**
1. Kiểm tra B2 phải là `LONG` hoặc `SHORT`
2. Kiểm tra trên Binance: Có vị thế/lệnh chờ chưa?
3. Đảm bảo cột B là số > 0 (VD: `1`, `10`)

---

#### **Lỗi 2: API -4120 (Trailing Stop)**

**Giải pháp:**
- ✅ Bot tự động fallback sang Algo Order API
- Không cần can thiệp

---

#### **Lỗi 3: Insufficient margin**

**Giải pháp:**
1. Chuyển USDT từ Spot → Futures
2. Giảm vốn E2 hoặc H
3. Giảm đòn bẩy cột B

---

### 7.2. Kiểm tra logs

```bash
# Log chính
tail -f hd_order.log

# Log cascade
tail -f cascade_manager.log
```

---

## 8. TIPS & BEST PRACTICES

### 8.1. Quản lý rủi ro

✅ **Nên:**
- Dùng vốn nhỏ để test (1-5 USDT)
- Đặt Stop Loss rõ ràng (config lenh2_rate)
- Không dùng đòn bẩy quá cao (≤ 20x)

❌ **Không nên:**
- All-in 1 lệnh
- Dùng đòn bẩy >50x
- Đặt lệnh khi không hiểu rõ

---

## 9. KẾT LUẬN

### 9.1. Checklist

- [ ] Đã cài đặt bot đầy đủ
- [ ] Đã config `config.ini` với API keys
- [ ] Có đủ USDT trong Futures wallet
- [ ] Đã test với vốn nhỏ
- [ ] Biết cách sử dụng STOP khẩn cấp

---

**Chúc bạn trade hiệu quả! 🚀📈**

*Tài liệu được cập nhật: 2025-01-18*
*Version: QBot - Đơn giản hóa (Chỉ TRAILING_STOP)*
