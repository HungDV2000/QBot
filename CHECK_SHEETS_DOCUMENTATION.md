# 📊 TÀI LIỆU CÁC SHEET TRONG GOOGLE SHEETS

## 🎯 Tổng quan hệ thống

Bot quản lý **5 sheets chính**:
1. **ĐẶT LỆNH (100 MÃ)** - Đặt lệnh tự động
2. **100 mã (50 tăng và 50 giảm)** - Phân tích top 100
3. **Chờ và khớp** - Theo dõi orders
4. **list** - Whitelist mã giao dịch
5. **Danhmuc** - Danh mục mã futures

---

## 1️⃣ SHEET: ĐẶT LỆNH (100 MÃ)

### 📝 Mô tả
Sheet để cấu hình và đặt lệnh tự động dựa trên phân tích từ sheet "100 mã"

### 🔧 Script xử lý
- `hd_order_123.py` hoặc `hd_order.py`
- Đọc cấu hình từ sheet này → Đặt lệnh trên Binance

### 📋 Cấu trúc (Cần xác nhận)
| Cột | Tên | Mô tả | Ví dụ |
|-----|-----|-------|-------|
| A | Symbol | Mã cặp giao dịch | BTC/USDT |
| B | Action | Hành động | BUY/SELL |
| C | Entry Price | Giá vào lệnh | 42000 |
| D | Stop Loss | Giá cắt lỗ | 41000 |
| E | Take Profit | Giá chốt lãi | 43000 |
| F | Quantity | Số lượng | 0.1 |
| G | Status | Trạng thái | PENDING/FILLED |

### ⚙️ Workflow
```
Sheet "100 mã" → Phân tích → Sheet "ĐẶT LỆNH" → Bot đọc → Binance API → Đặt lệnh
```

---

## 2️⃣ SHEET: 100 MÃ (50 TĂNG VÀ 50 GIẢM)

### 📝 Mô tả
Phân tích và hiển thị top 50 mã giảm mạnh nhất + top 50 mã tăng mạnh nhất trong 24h

### 🔧 Script xử lý
- **File**: `hd_update_all.py`
- **Tần suất**: 8 phút/lần (480 giây)
- **Số dòng**: 102 (1 header + 1 account info + 100 mã)

### 📋 Cấu trúc chi tiết (40 cột: A-AN)

#### **Hàng 1: Header + Timestamp**
| Cell | Nội dung | Mô tả |
|------|----------|-------|
| **A1** | `2025-12-17 16:10:41` | Timestamp cập nhật |
| **B1-AN1** | Headers | Tên các cột |

#### **Danh sách các cột**

| Cột | Header | Dữ liệu | Nguồn | Đơn vị |
|-----|--------|---------|-------|--------|
| **A** | *(Timestamp)* | Mã cặp | `ticker['symbol']` | Text |
| **B** | % 24h | % thay đổi 24h | `ticker['percentage']` | % |
| **C** | Giá trị hiện thời | Giá hiện tại | `ticker['last']` | USDT |
| **D** | Niêm yết | Thời gian niêm yết | *(Chưa có)* | - |
| **E** | Vol 15p | Volume 15 phút | `fetch_ohlcv('15m')` | USDT |
| **F** | Vol 1h | Volume 1 giờ | `fetch_ohlcv('1h')` | USDT |
| **G** | Vol 4h | Volume 4 giờ | `fetch_ohlcv('4h')` | USDT |
| **H** | Vol 1 ngày | Volume 1 ngày | `fetch_ohlcv('1d')` | USDT |
| **I** | Vol 1 tuần | Volume 1 tuần | `fetch_ohlcv('1w')` | USDT |
| **J** | BB15p trên | Bollinger Upper 15m | `get_bb('15m')` | USDT |
| **K** | BB15p dưới | Bollinger Lower 15m | `get_bb('15m')` | USDT |
| **L** | BB1h trên | Bollinger Upper 1h | `get_bb('1h')` | USDT |
| **M** | BB1h dưới | Bollinger Lower 1h | `get_bb('1h')` | USDT |
| **N** | BB4h trên | Bollinger Upper 4h | `get_bb('4h')` | USDT |
| **O** | BB4h dưới | Bollinger Lower 4h | `get_bb('4h')` | USDT |
| **P** | BB1 ngày trên | Bollinger Upper 1d | `get_bb('1d')` | USDT |
| **Q** | BB1 ngày dưới | Bollinger Lower 1d | `get_bb('1d')` | USDT |
| **R** | BB1 tuần trên | Bollinger Upper 1w | `get_bb('1w')` | USDT |
| **S** | BB1 tuần dưới | Bollinger Lower 1w | `get_bb('1w')` | USDT |
| **T** | BB1 tháng trên | Bollinger Upper 1M | `get_bb('1M')` | USDT |
| **U** | BB1 tháng dưới | Bollinger Lower 1M | `get_bb('1M')` | USDT |
| **V** | Biên độ 1h max tăng tuần | % tăng max 7 ngày (1h) | `calculate_price_range(7, '1h')` | % |
| **W** | Biên độ 1h max giảm tuần | % giảm max 7 ngày (1h) | `calculate_price_range(7, '1h')` | % |
| **X** | Max 30 ngày | Giá cao nhất 30 ngày | `calculate_high_low_30d()` | USDT |
| **Y** | Min 30 ngày | Giá thấp nhất 30 ngày | `calculate_high_low_30d()` | USDT |
| **Z** | Max 3 ngày | Giá cao nhất 3 ngày | `get_high_low_simple(3)` | USDT |
| **AA** | Thời điểm Max 3 ngày | *(Trống)* | - | - |
| **AB** | Min 3 ngày | Giá thấp nhất 3 ngày | `get_high_low_simple(3)` | USDT |
| **AC** | Thời điểm Min 3 ngày | *(Trống)* | - | - |
| **AD** | Max 7 ngày | Giá cao nhất 7 ngày | `get_high_low_simple(7)` | USDT |
| **AE** | Thời điểm Max 7 ngày | *(Trống)* | - | - |
| **AF** | Min 7 ngày | Giá thấp nhất 7 ngày | `get_high_low_simple(7)` | USDT |
| **AG** | Thời điểm Min 7 ngày | *(Trống)* | - | - |
| **AH** | Max 30 ngày chi tiết | Giá cao nhất 30 ngày | `get_high_low_simple(30)` | USDT |
| **AI** | Thời điểm Max 30 ngày | *(Trống)* | - | - |
| **AJ** | Min 30 ngày chi tiết | Giá thấp nhất 30 ngày | `get_high_low_simple(30)` | USDT |
| **AK** | Thời điểm Min 30 ngày | *(Trống)* | - | - |
| **AL** | Max tăng 4h/60 ngày | % tăng max 60 ngày (4h) | `calculate_max_increase_decrease_4h()` | % |
| **AM** | Max giảm 4h/60 ngày | % giảm max 60 ngày (4h) | `calculate_max_increase_decrease_4h()` | % |
| **AN** | Đánh dấu | Marker top đỉnh/đáy | Logic phân tích | 🔴/🟢 |

### 📊 Ý nghĩa các chỉ số

#### **Bollinger Bands (BB)**
- **BB trên**: Giá vượt → Mua quá nhiều (overbought)
- **BB dưới**: Giá xuống dưới → Bán quá nhiều (oversold)
- **Mục đích**: Xác định điểm vào/ra lệnh

#### **Biên độ (Amplitude)**
- **Max tăng**: Biên độ nến có % tăng cao nhất
- **Max giảm**: Biên độ nến có % giảm cao nhất
- **Mục đích**: Đánh giá độ biến động

#### **High/Low**
- **Max/Min**: Giá cao/thấp nhất trong khoảng thời gian
- **Mục đích**: Set stop loss, take profit

#### **Marker**
- **🔴 TOP ĐỈNH**: Top 50 gần đỉnh (rủi ro cao nếu mua)
- **🟢 TOP ĐÁY**: Top 50 gần đáy (cơ hội mua)

### ⚠️ Lưu ý
- **Cột AA, AC, AE, AG, AI, AK** trống để tối ưu hóa (giảm 600 API calls)
- Data sắp xếp: Top 50 giảm → Top 50 tăng

---

## 3️⃣ SHEET: CHỜ VÀ KHỚP

### 📝 Mô tả
Hiển thị các lệnh đang chờ (pending orders) và đã khớp của tất cả các cặp giao dịch

### 🔧 Script xử lý
- **File**: `hd_update_cho_va_khop.py`
- **Tần suất**: 8 phút/lần (480 giây)

### 📋 Cấu trúc

#### **Hàng 1-4: Metadata**
| Row | Cell | Nội dung | Mô tả |
|-----|------|----------|-------|
| 1 | A1 | Metadata | Thông tin tổng quan |
| 2 | A2 | Metadata | Số lượng orders, symbols... |
| 3 | A3 | Header | Tên các cột |
| 4 | A4 | `2025-12-17 16:12:30` | **Timestamp cập nhật** |

#### **Hàng 5+: Dữ liệu orders**
| Cột | Tên | Mô tả | Ví dụ |
|-----|-----|-------|-------|
| **A** | Symbol | Mã cặp giao dịch | BTC/USDT |
| **B** | Order ID | ID của lệnh | 12345678 |
| **C** | Side | Hướng | BUY/SELL |
| **D** | Type | Loại lệnh | LIMIT/MARKET |
| **E** | Price | Giá đặt | 42000 |
| **F** | Amount | Số lượng | 0.1 |
| **G** | Status | Trạng thái | PENDING/FILLED |
| **H** | Created | Thời gian tạo | 2025-12-17 15:00:00 |

### 🎯 Điều kiện hiển thị
- Chỉ hiển thị symbols có **đúng 1 order pending**
- Loại bỏ symbols có 0 hoặc nhiều hơn 1 order

### ⚙️ Workflow
```
Binance API → fetch_open_orders() → Lọc (1 order/symbol) → Ghi vào sheet
```

---

## 4️⃣ SHEET: LIST (WHITELIST)

### 📝 Mô tả
Danh sách các mã được phép giao dịch (whitelist). Tất cả scripts đều đọc từ đây để lọc mã.

### 🔧 Script đọc
- `gg_sheet_factory.get_white_list()` - Hàm đọc whitelist
- Tất cả scripts khác call hàm này

### 📋 Cấu trúc
```
Cột A: Symbol
───────────────
BTC/USDT
ETH/USDT
SOL/USDT
BNB/USDT
...
```

### 🔧 Logic xử lý
```python
# File: gg_sheet_factory.py
def get_white_list():
    # 1. Đọc tất cả symbols từ cột A
    # 2. Format: BTC/USDT → BTC/USDT:USDT
    # 3. Loại bỏ dòng trống
    # 4. Lọc chỉ lấy mã còn TRADING trên Binance
    return white_list
```

### 📝 Cách sử dụng

#### **Thêm mã mới**
1. Mở sheet "list"
2. Thêm mã vào cột A (VD: `XRP/USDT`)
3. Save → Bot tự động đọc lần chạy tiếp theo

#### **Xóa mã**
1. Xóa dòng trong cột A
2. Save → Bot tự động bỏ qua mã đó

### ⚠️ Lưu ý quan trọng
- ❌ Mã **KHÔNG** có trong "list" → Không được xử lý
- ❌ Mã bị **delist** trên Binance → Tự động bỏ qua
- ✅ Chỉ mã trong "list" **VÀ** đang TRADING → Được xử lý

---

## 5️⃣ SHEET: DANHMUC

### 📝 Mô tả
Liệt kê **TẤT CẢ** các cặp giao dịch futures perpetual đang active trên Binance

### 🔧 Script xử lý
- **File**: `hd_update_danhmuc.py`
- **Tần suất**: Chạy thủ công hoặc theo lịch

### 📋 Cấu trúc
| Cột | Tên | Mô tả | Ví dụ |
|-----|-----|-------|-------|
| **A** | Symbol | Tên cặp | BTCUSDT |
| **B** | Status | Trạng thái | TRADING |
| **C** | Contract Type | Loại hợp đồng | PERPETUAL |
| **D** | Base Asset | Coin gốc | BTC |
| **E** | Quote Asset | Coin định giá | USDT |
| **F** | Launch Date | Ngày niêm yết | 2020-01-01 |

### 🔧 Điều kiện lọc
```python
# Chỉ lấy symbols:
# ✓ status = 'TRADING'
# ✓ symbol.endswith('USDT')
# ✓ contractType = 'PERPETUAL'
```

### 📊 Số lượng
- Tổng: ~300-400 cặp futures perpetual USDT

### 🎯 Mục đích
- Tham khảo danh sách đầy đủ để thêm vào "list"
- Kiểm tra mã có tồn tại trên Binance không
- Discover mã mới niêm yết

---

## 🔄 WORKFLOW TỔNG THỂ

```
┌─────────────┐
│   Sheet     │
│   "list"    │  ← Whitelist (người dùng quản lý)
└──────┬──────┘
       │
       ↓
┌─────────────────────────────────┐
│  Binance API                    │
│  - Fetch tickers                │
│  - Fetch OHLCV                  │
│  - Fetch account                │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  hd_update_all.py               │
│  - Phân tích top 100            │
│  - Tính toán chỉ số             │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  Sheet "100 mã"                 │  ← Dữ liệu phân tích
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  Sheet "ĐẶT LỆNH"              │  ← Cấu hình đặt lệnh
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  hd_order_123.py                │
│  - Đọc cấu hình                 │
│  - Đặt lệnh tự động             │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  Binance API                    │
│  - Create orders                │
└──────┬──────────────────────────┘
       │
       ↓
┌─────────────────────────────────┐
│  Sheet "Chờ và khớp"           │  ← Theo dõi orders
└─────────────────────────────────┘
```

---

## 📞 TÀI LIỆU LIÊN QUAN

| File | Mô tả |
|------|-------|
| `COLUMN_MAPPING_CHECK.md` | Kiểm tra độ khớp header-data |
| `DATA_VERIFICATION_GUIDE.md` | Hướng dẫn check dữ liệu Binance |
| `hd_update_all.py` | Script update sheet "100 mã" |
| `hd_update_cho_va_khop.py` | Script update sheet "Chờ và khớp" |
| `hd_update_danhmuc.py` | Script update sheet "Danhmuc" |
| `gg_sheet_factory.py` | API Google Sheets |
| `data_collector.py` | Hàm lấy dữ liệu Binance |

---

**Cập nhật lần cuối**: 2025-12-17  
**Version**: 1.0
