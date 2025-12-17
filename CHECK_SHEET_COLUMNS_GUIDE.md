# 📊 HƯỚNG DẪN CÁC CỘT TRONG GOOGLE SHEETS

## 🎯 Tổng quan các Sheet

Bot quản lý 5 sheets chính trong Google Sheets:
1. **ĐẶT LỆNH (100 MÃ)** - Sheet đặt lệnh tự động
2. **100 mã (50 tăng và 50 giảm)** - Phân tích top 100 mã
3. **Chờ và khớp** - Theo dõi lệnh đang chờ và đã khớp
4. **list** - Danh sách mã cho phép (whitelist)
5. **Danhmuc** - Danh mục các cặp giao dịch

---

## 1️⃣ SHEET: ĐẶT LỆNH (100 MÃ)

**Mục đích**: Đặt lệnh tự động dựa trên dữ liệu phân tích

**Cấu trúc**: *(Cần cập nhật chi tiết sau khi xác nhận)*

**Script cập nhật**: 
- `hd_order_123.py` hoặc `hd_order.py`
- Đọc dữ liệu từ sheet "100 mã" để tự động đặt lệnh

---

## 2️⃣ SHEET: 100 MÃ (50 TĂNG VÀ 50 GIẢM)

**Mục đích**: Phân tích top 50 mã giảm nhiều nhất và top 50 mã tăng nhiều nhất trong 24h

**Script cập nhật**: `hd_update_all.py`

**Tần suất**: Mỗi 8 phút (480 giây)

### 📋 CẤU TRÚC CÁC CỘT (Tổng: 40 cột A-AN)

#### **Hàng 1 (Header)**
| Cột | Tên cột | Mô tả |
|-----|---------|-------|
| **A1** | *(Timestamp)* | Thời gian cập nhật dữ liệu (VD: 2025-12-17 16:10:41) |

#### **Từ hàng 2 trở đi (Dữ liệu)**

| Cột | Header (B1→AN1) | Dữ liệu (A2→AN2...) | Nguồn API | Đơn vị |
|-----|-----------------|---------------------|-----------|--------|
| **A** | *(Không có header)* | Mã cặp giao dịch | `symbol` | Text (VD: BTC/USDT) |
| **B** | % 24h | Phần trăm thay đổi giá 24h | `ticker['percentage']` | % |
| **C** | Giá trị hiện thời | Giá hiện tại của mã | `ticker['last']` | USDT |
| **D** | Niêm yết | Thời điểm niêm yết | *(Chưa có API)* | Trống |
| **E** | Vol 15p | Khối lượng giao dịch 15 phút | `get_volumes_multi_timeframe` | USDT |
| **F** | Vol 1h | Khối lượng giao dịch 1 giờ | `get_volumes_multi_timeframe` | USDT |
| **G** | Vol 4h | Khối lượng giao dịch 4 giờ | `get_volumes_multi_timeframe` | USDT |
| **H** | Vol 1 ngày | Khối lượng giao dịch 1 ngày | `get_volumes_multi_timeframe` | USDT |
| **I** | Vol 1 tuần | Khối lượng giao dịch 1 tuần | `get_volumes_multi_timeframe` | USDT |
| **J** | BB15p trên | Bollinger Band trên (15 phút) | `get_bb('15m')` | USDT |
| **K** | BB15p dưới | Bollinger Band dưới (15 phút) | `get_bb('15m')` | USDT |
| **L** | BB1h trên | Bollinger Band trên (1 giờ) | `get_bb('1h')` | USDT |
| **M** | BB1h dưới | Bollinger Band dưới (1 giờ) | `get_bb('1h')` | USDT |
| **N** | BB4h trên | Bollinger Band trên (4 giờ) | `get_bb('4h')` | USDT |
| **O** | BB4h dưới | Bollinger Band dưới (4 giờ) | `get_bb('4h')` | USDT |
| **P** | BB1 ngày trên | Bollinger Band trên (1 ngày) | `get_bb('1d')` | USDT |
| **Q** | BB1 ngày dưới | Bollinger Band dưới (1 ngày) | `get_bb('1d')` | USDT |
| **R** | BB1 tuần trên | Bollinger Band trên (1 tuần) | `get_bb('1w')` | USDT |
| **S** | BB1 tuần dưới | Bollinger Band dưới (1 tuần) | `get_bb('1w')` | USDT |
| **T** | BB1 tháng trên | Bollinger Band trên (1 tháng) | `get_bb('1M')` | USDT |
| **U** | BB1 tháng dưới | Bollinger Band dưới (1 tháng) | `get_bb('1M')` | USDT |
| **V** | Biên độ 1h max tăng tuần | % tăng max trong 7 ngày (khung 1h) | `calculate_price_range(7, '1h')` | % |
| **W** | Biên độ 1h max giảm tuần | % giảm max trong 7 ngày (khung 1h) | `calculate_price_range(7, '1h')` | % |
| **X** | Max 30 ngày | Giá cao nhất 30 ngày | `calculate_high_low_30d` | USDT |
| **Y** | Min 30 ngày | Giá thấp nhất 30 ngày | `calculate_high_low_30d` | USDT |
| **Z** | Max 3 ngày | Giá cao nhất 3 ngày | `get_high_low_simple(3)` | USDT |
| **AA** | Thời điểm Max 3 ngày | *(Trống - đã tối ưu hóa)* | - | - |
| **AB** | Min 3 ngày | Giá thấp nhất 3 ngày | `get_high_low_simple(3)` | USDT |
| **AC** | Thời điểm Min 3 ngày | *(Trống - đã tối ưu hóa)* | - | - |
| **AD** | Max 7 ngày | Giá cao nhất 7 ngày | `get_high_low_simple(7)` | USDT |
| **AE** | Thời điểm Max 7 ngày | *(Trống - đã tối ưu hóa)* | - | - |
| **AF** | Min 7 ngày | Giá thấp nhất 7 ngày | `get_high_low_simple(7)` | USDT |
| **AG** | Thời điểm Min 7 ngày | *(Trống - đã tối ưu hóa)* | - | - |
| **AH** | Max 30 ngày chi tiết | Giá cao nhất 30 ngày (chi tiết) | `get_high_low_simple(30)` | USDT |
| **AI** | Thời điểm Max 30 ngày | *(Trống - đã tối ưu hóa)* | - | - |
| **AJ** | Min 30 ngày chi tiết | Giá thấp nhất 30 ngày (chi tiết) | `get_high_low_simple(30)` | USDT |
| **AK** | Thời điểm Min 30 ngày | *(Trống - đã tối ưu hóa)* | - | - |
| **AL** | Max tăng 4h/60 ngày | % tăng max trong 60 ngày (khung 4h) | `calculate_max_increase_decrease_4h` | % |
| **AM** | Max giảm 4h/60 ngày | % giảm max trong 60 ngày (khung 4h) | `calculate_max_increase_decrease_4h` | % |
| **AN** | Đánh dấu | Marker top đỉnh/đáy | Logic phân tích | 🔴 TOP ĐỈNH / 🟢 TOP ĐÁY |

### 📝 Ghi chú quan trọng:
- **Các cột AA, AC, AE, AG, AI, AK** (timestamp) hiện **trống** do tối ưu hóa performance
- Trước đây mỗi cột timestamp cần 1 API call riêng → Tốn 600 API calls cho 100 mã
- Hiện tại chỉ lấy giá high/low, giảm xuống còn 300 API calls
- Data được sắp xếp: Top 50 giảm nhiều nhất → Top 50 tăng nhiều nhất

---

## 3️⃣ SHEET: CHỜ VÀ KHỚP

**Mục đích**: Theo dõi các lệnh đang chờ (pending) và đã khớp của các cặp giao dịch

**Script cập nhật**: `hd_update_cho_va_khop.py`

**Tần suất**: Mỗi 8 phút (480 giây)

### 📋 CẤU TRÚC CÁC CỘT

#### **Hàng đầu (Metadata)**
| Cột | Nội dung | Mô tả |
|-----|----------|-------|
| **A1** | Metadata | Thông tin tổng quan |
| **A2** | Metadata | Thông tin bổ sung |
| **A3** | Metadata | Header hoặc note |
| **A4** | Timestamp | Thời gian cập nhật cuối (VD: 2025-12-17 16:12:30) |

#### **Từ hàng 5 trở đi (Dữ liệu)**
| Cột | Tên | Mô tả | Nguồn |
|-----|-----|-------|-------|
| **A** | Symbol | Mã cặp giao dịch | `order['symbol']` |
| **B** | Order ID | ID của lệnh | `order['id']` |
| **C** | Side | Hướng lệnh | BUY/SELL |
| **D** | Type | Loại lệnh | LIMIT/MARKET/STOP |
| **E** | Price | Giá đặt lệnh | USDT |
| **F** | Amount | Số lượng | Coin |
| **G** | Status | Trạng thái | PENDING/FILLED |
| **H** | Created | Thời gian tạo lệnh | Timestamp |

**Điều kiện lọc**: Chỉ hiển thị các symbol có **đúng 1 order pending**

---

## 4️⃣ SHEET: LIST (WHITELIST)

**Mục đích**: Danh sách các mã được phép giao dịch (whitelist)

**Script đọc**: Tất cả các script đều đọc từ sheet này để lọc mã

**Cấu trúc**:
```
Cột A: Symbol (VD: BTC/USDT, ETH/USDT, SOL/USDT)
```

### 🔧 Xử lý logic:
```python
# File: gg_sheet_factory.py - get_white_list()
# - Đọc tất cả mã từ cột A
# - Format: BTC/USDT:USDT (thêm :USDT nếu chưa có)
# - Loại bỏ các dòng trống
# - Chỉ lấy mã còn giao dịch trên Binance (status = TRADING)
```

### ⚠️ Lưu ý:
- Nếu mã không có trong sheet "list" → **KHÔNG được xử lý**
- Nếu mã bị delist (không còn trên Binance) → **Tự động loại bỏ**
- Cập nhật whitelist bằng cách thêm/xóa mã trong cột A

---

## 5️⃣ SHEET: DANHMUC

**Mục đích**: Liệt kê tất cả các cặp giao dịch futures đang active trên Binance

**Script cập nhật**: `hd_update_danhmuc.py`

**Tần suất**: Chạy thủ công hoặc định kỳ

### 📋 CẤU TRÚC CÁC CỘT
| Cột | Tên | Mô tả | Nguồn |
|-----|-----|-------|-------|
| **A** | Symbol | Tên cặp giao dịch | `exchangeInfo['symbols']` |
| **B** | Status | Trạng thái | TRADING/HALT/BREAK |
| **C** | Contract Type | Loại hợp đồng | PERPETUAL |
| **D** | Base Asset | Coin gốc | BTC, ETH, SOL... |
| **E** | Quote Asset | Coin định giá | USDT |

### 🔧 Điều kiện lọc:
```python
# Chỉ lấy các symbol:
# - status = 'TRADING'
# - endswith 'USDT'
# - contractType = 'PERPETUAL'
```

---

## 📊 SO SÁNH HEADER VÀ DỮ LIỆU - SHEET "100 MÃ"

### ✅ Kiểm tra độ khớp:

#### **Header (B1-AN1): 39 cột**
```
B: "% 24h"
C: "Giá trị hiện thời"
D: "Niêm yết"
E-I: "Vol 15p", "Vol 1h", "Vol 4h", "Vol 1 ngày", "Vol 1 tuần" (5 cột)
J-U: BB trên/dưới cho 6 khung (15m, 1h, 4h, 1d, 1w, 1M) (12 cột)
V-W: "Biên độ 1h max tăng tuần", "Biên độ 1h max giảm tuần" (2 cột)
X-Y: "Max 30 ngày", "Min 30 ngày" (2 cột)
Z-AC: Max/Min 3 ngày + timestamp (4 cột)
AD-AG: Max/Min 7 ngày + timestamp (4 cột)
AH-AK: Max/Min 30 ngày chi tiết + timestamp (4 cột)
AL-AM: "Max tăng 4h/60 ngày", "Max giảm 4h/60 ngày" (2 cột)
AN: "Đánh dấu" (1 cột)
```

#### **Dữ liệu (A2-AN2...): 40 cột**
```
A: pair (mã)
B: percentage
C: price
D: "" (niêm yết - trống)
E-I: volumes (5 cột)
J-U: BB array (12 cột)
V-W: max_increase, max_decrease (2 cột)
X-Y: high_30d, low_30d (2 cột)
Z-AC: high_3d, "", low_3d, "" (4 cột)
AD-AG: high_7d, "", low_7d, "" (4 cột)
AH-AK: high_30d, "", low_30d, "" (4 cột)
AL-AM: increase, decrease (2 cột)
AN: marker (1 cột)
```

### ✅ KẾT LUẬN: **KHỚP HOÀN TOÀN**
- Cột A: Mã (không có header, A1 là timestamp)
- Cột B-AN: 39 cột dữ liệu khớp với 39 header
- Tổng: 40 cột (A-AN)

---

## 🔄 WORKFLOW CẬP NHẬT DỮ LIỆU

```
┌─────────────────────────────────────────────┐
│  1. Đọc whitelist từ sheet "list"          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  2. Fetch dữ liệu từ Binance API           │
│     - Tickers (giá, % 24h)                 │
│     - OHLCV (Volume, High/Low)             │
│     - Bollinger Bands                       │
│     - Account info (balance, PnL)          │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  3. Xử lý và tính toán                     │
│     - Sắp xếp top 50 tăng/giảm             │
│     - Tính BB, biên độ, high/low           │
│     - Đánh dấu top đỉnh/đáy                │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  4. Ghi vào Google Sheets                  │
│     - Sheet "100 mã": A1 timestamp         │
│     - B1-AN1: Header                       │
│     - A2-AN101: Dữ liệu 100 mã             │
└─────────────────────────────────────────────┘
```

---

## 📞 Liên hệ hỗ trợ

Nếu có thắc mắc về cấu trúc dữ liệu, vui lòng kiểm tra:
- `hd_update_all.py` - Sheet "100 mã"
- `hd_update_cho_va_khop.py` - Sheet "Chờ và khớp"
- `hd_update_danhmuc.py` - Sheet "Danhmuc"
- `gg_sheet_factory.py` - Các hàm đọc/ghi Google Sheets

---

**Cập nhật lần cuối**: 2025-12-17
**Version**: 1.0
