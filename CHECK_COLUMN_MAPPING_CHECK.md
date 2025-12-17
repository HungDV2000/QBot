# ✅ KIỂM TRA ĐỘ KHỚP GIỮA TÊN CỘT VÀ DỮ LIỆU

## 📊 Phân tích cấu trúc Sheet "100 mã (50 tăng và 50 giảm)"

### 🔍 Cấu trúc hiện tại:

**Dòng 1 (Header):**
- **A1**: `2025-12-17 16:10:41` (timestamp - KHÔNG có text header)
- **B1-AN1**: Text header các cột dữ liệu

**Dòng 2+ (Data):**
- **A2+**: Mã cặp giao dịch (BTC/USDT, ETH/USDT...)
- **B2+**: % 24h
- **C2+**: Giá
- ... (các cột khác)

---

## ⚠️ VẤN ĐỀ PHÁT HIỆN

### 🔴 Cột A thiếu header text!

| Hiện tại | Đề xuất |
|----------|---------|
| A1 = `2025-12-17 16:10:41` | A1 = `Mã` (header text) |
| A2 = `BTC/USDT` (data) | A2 = `BTC/USDT` (data) |

**Timestamp nên đặt ở đâu?**
- Ý tưởng: Đặt timestamp ở một vị trí khác (VD: merge cells, hoặc cell riêng phía trên)

---

## 📋 BẢNG SO SÁNH CHI TIẾT

### ✅ Phần 1: Cột A-I (Thông tin cơ bản + Volume)

| Cột | Vị trí Header | Text Header hiện tại | Vị trí Data | Data Code | Khớp? |
|-----|---------------|----------------------|-------------|-----------|-------|
| **A** | A1 | *(Timestamp - không có text)* | A2 | `pair` | ❌ **THIẾU HEADER** |
| **B** | B1 | `"% 24h"` | B2 | `percentage` | ✅ |
| **C** | C1 | `"Giá trị hiện thời"` | C2 | `price` | ✅ |
| **D** | D1 | `"Niêm yết"` | D2 | `""` (trống) | ✅ |
| **E** | E1 | `"Vol 15p"` | E2 | `volumes['15m']` | ✅ |
| **F** | F1 | `"Vol 1h"` | F2 | `volumes['1h']` | ✅ |
| **G** | G1 | `"Vol 4h"` | G2 | `volumes['4h']` | ✅ |
| **H** | H1 | `"Vol 1 ngày"` | H2 | `volumes['1d']` | ✅ |
| **I** | I1 | `"Vol 1 tuần"` | I2 | `volumes['1w']` | ✅ |

---

### ✅ Phần 2: Cột J-U (Bollinger Bands - 6 khung)

| Cột | Header | Data | Timeframe | Khớp? |
|-----|--------|------|-----------|-------|
| **J** | `"BB15p trên"` | `bb_array[0]` | 15m upper | ✅ |
| **K** | `"BB15p dưới"` | `bb_array[1]` | 15m lower | ✅ |
| **L** | `"BB1h trên"` | `bb_array[2]` | 1h upper | ✅ |
| **M** | `"BB1h dưới"` | `bb_array[3]` | 1h lower | ✅ |
| **N** | `"BB4h trên"` | `bb_array[4]` | 4h upper | ✅ |
| **O** | `"BB4h dưới"` | `bb_array[5]` | 4h lower | ✅ |
| **P** | `"BB1 ngày trên"` | `bb_array[6]` | 1d upper | ✅ |
| **Q** | `"BB1 ngày dưới"` | `bb_array[7]` | 1d lower | ✅ |
| **R** | `"BB1 tuần trên"` | `bb_array[8]` | 1w upper | ✅ |
| **S** | `"BB1 tuần dưới"` | `bb_array[9]` | 1w lower | ✅ |
| **T** | `"BB1 tháng trên"` | `bb_array[10]` | 1M upper | ✅ |
| **U** | `"BB1 tháng dưới"` | `bb_array[11]` | 1M lower | ✅ |

**Code reference:**
```python
get_bb(pair, timeframes = ['15m', '1h', '4h', '1d', '1w', '1M'])
# Mỗi timeframe → 2 values (upper, lower)
# Tổng: 6 x 2 = 12 values
```

---

### ✅ Phần 3: Cột V-Y (Biên độ + High/Low 30d)

| Cột | Header | Data Code | Khớp? |
|-----|--------|-----------|-------|
| **V** | `"Biên độ 1h max tăng tuần"` | `calculate_price_range(7, '1h')[0]` | ✅ |
| **W** | `"Biên độ 1h max giảm tuần"` | `calculate_price_range(7, '1h')[1]` | ✅ |
| **X** | `"Max 30 ngày"` | `calculate_high_low_30d()[0]` | ✅ |
| **Y** | `"Min 30 ngày"` | `calculate_high_low_30d()[1]` | ✅ |

---

### ✅ Phần 4: Cột Z-AK (High/Low chi tiết 3/7/30 ngày)

| Cột | Header | Data Code | Giá trị | Khớp? |
|-----|--------|-----------|---------|-------|
| **Z** | `"Max 3 ngày"` | `get_high_low_simple(3)[0]` | High 3d | ✅ |
| **AA** | `"Thời điểm Max 3 ngày"` | `""` | **Trống** | ✅ (cố ý) |
| **AB** | `"Min 3 ngày"` | `get_high_low_simple(3)[2]` | Low 3d | ✅ |
| **AC** | `"Thời điểm Min 3 ngày"` | `""` | **Trống** | ✅ (cố ý) |
| **AD** | `"Max 7 ngày"` | `get_high_low_simple(7)[0]` | High 7d | ✅ |
| **AE** | `"Thời điểm Max 7 ngày"` | `""` | **Trống** | ✅ (cố ý) |
| **AF** | `"Min 7 ngày"` | `get_high_low_simple(7)[2]` | Low 7d | ✅ |
| **AG** | `"Thời điểm Min 7 ngày"` | `""` | **Trống** | ✅ (cố ý) |
| **AH** | `"Max 30 ngày chi tiết"` | `get_high_low_simple(30)[0]` | High 30d | ✅ |
| **AI** | `"Thời điểm Max 30 ngày"` | `""` | **Trống** | ✅ (cố ý) |
| **AJ** | `"Min 30 ngày chi tiết"` | `get_high_low_simple(30)[2]` | Low 30d | ✅ |
| **AK** | `"Thời điểm Min 30 ngày"` | `""` | **Trống** | ✅ (cố ý) |

**Ghi chú:** Các cột timestamp (AA, AC, AE, AG, AI, AK) **cố ý để trống** để tối ưu performance (giảm 600 API calls).

---

### ✅ Phần 5: Cột AL-AN (Biên độ 4h + Marker)

| Cột | Header | Data Code | Khớp? |
|-----|--------|-----------|-------|
| **AL** | `"Max tăng 4h/60 ngày"` | `calculate_max_increase_decrease_4h()[0]` | ✅ |
| **AM** | `"Max giảm 4h/60 ngày"` | `calculate_max_increase_decrease_4h()[1]` | ✅ |
| **AN** | `"Đánh dấu"` | `marker` (🔴 TOP ĐỈNH / 🟢 TOP ĐÁY) | ✅ |

---

## 📊 TỔNG KẾT

### ✅ Số liệu:
- **Tổng số cột**: 40 (A-AN)
- **Số cột có header text**: 39 (B-AN)
- **Số cột không có header text**: 1 (A)

### ✅ Độ khớp:
| Phần | Số cột | Khớp | Không khớp |
|------|--------|------|------------|
| A-I (Basic + Volume) | 9 | 8 | 1 (A thiếu header) |
| J-U (Bollinger Bands) | 12 | 12 | 0 |
| V-Y (Biên độ + H/L 30d) | 4 | 4 | 0 |
| Z-AK (High/Low chi tiết) | 12 | 12 | 0 |
| AL-AN (Biên độ 4h + Marker) | 3 | 3 | 0 |
| **TỔNG** | **40** | **39** | **1** |

---

## 🔧 ĐỀ XUẤT SỬA LỖI

### Cách 1: Thêm header "Mã" cho cột A

**Thay đổi logic:**
```python
# Hiện tại:
# A1 = timestamp
# B1-AN1 = headers

# Sửa thành:
# A1 = "Mã" (header text)
# B1-AN1 = headers khác
# Timestamp ghi vào một cell riêng (VD: Z1, hoặc merge A0:AN0 nếu thêm dòng)
```

**Ưu điểm:**
- Rõ ràng, cột A có header như các cột khác
- Dễ đọc, dễ hiểu

**Nhược điểm:**
- Mất vị trí A1 cho timestamp
- Cần tìm vị trí khác cho timestamp

---

### Cách 2: Giữ nguyên, document rõ ràng

**Giải thích:**
- A1 là timestamp của lần cập nhật cuối
- A2+ là dữ liệu mã cặp giao dịch
- Không có text header "Mã" vì A1 dùng cho timestamp

**Ưu điểm:**
- Không cần sửa code
- Timestamp hiển thị rõ ràng ở A1

**Nhược điểm:**
- Không nhất quán (các cột khác đều có header text)

---

### Cách 3: Tách timestamp ra cell riêng (KHUYẾN NGHỊ)

**Thay đổi:**
```python
# Ghi timestamp vào một cell merge phía trên (VD: A0:D0)
# hoặc vào sheet info riêng

# Hàng 1 (A1-AN1): Full headers
header_row = [
    "Mã",                           # A: Symbol
    "% 24h",                        # B: Percentage
    "Giá trị hiện thời",           # C: Price
    ... # các cột khác
]

# Ghi header từ A1
gg_sheet_factory.update_multi(..., [header_row], "A")

# Ghi timestamp vào cell khác (VD: Freeze row 0, ghi A0)
# Hoặc hiển thị trong sheet info riêng
```

**Ưu điểm:**
- Nhất quán: Tất cả cột đều có header text
- Timestamp vẫn hiển thị rõ ràng

**Nhược điểm:**
- Cần sửa code nhiều hơn

---

## 📝 KẾT LUẬN

### ✅ CÁC CỘT TỪ B-AN: **HOÀN TOÀN KHỚP**
- 39 headers khớp với 39 data elements
- Tên cột tiếng Việt rõ ràng
- Logic mapping đúng 100%

### ❌ CỘT A: **THIẾU HEADER TEXT**
- A1 hiện là timestamp (không phải text header)
- A2+ là data (mã cặp giao dịch)
- **Cần quyết định**: Giữ nguyên hay thêm header "Mã"?

---

## 🎯 HÀNH ĐỘNG TIẾP THEO

**Lựa chọn 1**: Giữ nguyên logic hiện tại
- Document rõ: "A1 = timestamp, A2+ = data"
- Không cần sửa code

**Lựa chọn 2**: Thêm header "Mã" cho cột A
- Sửa code để A1 = "Mã"
- Timestamp ghi vào vị trí khác

**Bạn muốn chọn cách nào?** 🤔
