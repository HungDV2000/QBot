# SO SÁNH TÍNH NĂNG: YÊU CẦU vs HIỆN TRẠNG

## 📊 TỔNG QUAN

| Thành phần | Yêu cầu QBot v2.0 | Hiện trạng MVP | Gap | Priority |
|------------|-------------------|----------------|-----|----------|
| **Module lấy dữ liệu** | 47+ cột, tracking, top 50 | ~10 cột cơ bản | 80% thiếu | 🟡 Medium |
| **Module đặt lệnh** | Flow đa lớp, 4 loại lệnh | Flow 1 lớp, 1 loại lệnh | 70% thiếu | 🔴 High |
| **Xử lý lỗi** | 10+ lỗi, retry, verify | Try-catch cơ bản | 90% thiếu | 🔴 High |
| **Telegram** | 8 loại thông báo rich | Text đơn giản | 80% thiếu | 🟢 Low |
| **Kiến trúc** | Modular, scalable | ✅ Tốt | ✅ OK | - |

---

## 🎯 CHI TIẾT TỪNG MODULE

### 1. MODULE LẤY DỮ LIỆU

| # | Tính năng | Yêu cầu | Hiện trạng | File | Status |
|---|-----------|---------|------------|------|--------|
| **1.1** | **Thông tin tài khoản** |
| 1 | Timestamp cập nhật | Ô A1, mỗi lần chạy | ✅ Có | hd_update_all.py:558 | ✅ |
| 2 | Funding Rate | Ô A2, 5 phút/lần | ❌ Không có | - | ❌ TODO |
| 3 | Margin Balance | Ô B2, 5 phút/lần | ✅ Có | hd_update_all.py:526 | ✅ |
| 4 | Wallet Balance | Ô C2, 5 phút/lần | ✅ Có | hd_update_all.py:528 | ✅ |
| 5 | Unrealized PNL | Ô D2, 5 phút/lần | ✅ Có | hd_update_all.py:527 | ✅ |
| **1.2** | **Cấu trúc dữ liệu** |
| 6 | BTC/BTCDOM cố định | Hàng 4-5 | ✅ Có | hd_update_all.py:472 | ✅ |
| 7 | Sắp xếp theo % 24h | Top 50 tăng/giảm | ✅ Có | hd_update_all.py:481 | ✅ |
| 8 | Header row | Hàng 3 | ⚠️ Không rõ ràng | - | ⚠️ TODO |
| **1.3** | **Nhóm 1: Thông tin cơ bản** |
| 9 | Tên cặp mã | Cột A | ✅ Có | hd_update_all.py:413 | ✅ |
| 10 | % thay đổi 24h | Cột B | ✅ Có | hd_update_all.py:414 | ✅ |
| 11 | Giá hiện tại | Cột C, < 1 phút | ✅ Có | hd_update_price.py | ✅ |
| 12 | Thời điểm niêm yết | Cột D | ❌ Không có | - | ❌ TODO |
| **1.4** | **Nhóm 2: Volume** |
| 13 | Volume 15m | Cột 5 | ❌ Có code nhưng không dùng | hd_update_all.py:344 | ⚠️ TODO |
| 14 | Volume 1h | Cột 6 | ❌ Có code nhưng không dùng | hd_update_all.py:344 | ⚠️ TODO |
| 15 | Volume 4h | Cột 7 | ❌ Không có | - | ❌ TODO |
| 16 | Volume 1d | Cột 8 | ❌ Không có | - | ❌ TODO |
| 17 | Volume 1w | Cột 9 | ❌ Không có | - | ❌ TODO |
| **1.5** | **Nhóm 3-8: Bollinger Bands** |
| 18 | BB 15m (upper, lower) | Cột 10-11 | ❌ Không có | - | ❌ TODO |
| 19 | BB 1h (upper, lower) | Cột 14-15 | ✅ Có | hd_update_all.py:418 | ✅ |
| 20 | BB 4h (upper, lower) | Cột 20-21 | ❌ Không có | - | ❌ TODO |
| 21 | BB 1d (upper, lower) | Cột 24-25 | ✅ Có | hd_update_all.py:418 | ✅ |
| 22 | BB 1w (upper, lower) | Cột 28-29 | ⚠️ Có cho BTC/BTCDOM | hd_update_all.py:540 | ⚠️ TODO |
| 23 | BB 1M (upper, lower) | Cột 32-33 | ❌ Không có | - | ❌ TODO |
| 24 | Biên độ BB các timeframes | Cột 12-35 | ⚠️ Có 1h, thiếu còn lại | - | ⚠️ TODO |
| **1.6** | **Nhóm 9: Giá cao/thấp** |
| 25 | High/Low 3 ngày + time | Cột 36-37, 42-43 | ❌ Không có | - | ❌ TODO |
| 26 | High/Low 7 ngày + time | Cột 38-39, 44-45 | ❌ Không có | - | ❌ TODO |
| 27 | High/Low 30 ngày + time | Cột 40-41, 46-47 | ⚠️ Có giá, thiếu time | hd_update_all.py:457 | ⚠️ TODO |
| **1.7** | **Nhóm 10: Biên độ 4h** |
| 28 | Max increase 4h (60d) | Cột riêng | ✅ Có | hd_update_all.py:465 | ✅ |
| 29 | Max decrease 4h (60d) | Cột riêng | ✅ Có | hd_update_all.py:466 | ✅ |
| **1.8** | **Nhóm 11: Chênh lệch** |
| 30 | Chênh lệch LONG vs đáy | Cột 48 | ❓ Cần làm rõ logic | - | ❓ CLARIFY |
| 31 | Chênh lệch SHORT vs đỉnh | Cột 49 | ❓ Cần làm rõ logic | - | ❓ CLARIFY |
| **1.9** | **Tính năng đặc biệt** |
| 32 | Top 50 gần đỉnh 30d | Highlight | ❌ Không có | - | ❌ TODO |
| 33 | Top 50 gần đáy 30d | Highlight | ❌ Không có | - | ❌ TODO |
| 34 | Tracking 30 mức giá | Mỗi phút, 30 điểm | ❌ Không có | - | ❌ TODO |

**Tỷ lệ hoàn thành Module 1: 10/34 = 29%**

---

### 2. MODULE ĐẶT LỆNH

| # | Tính năng | Yêu cầu | Hiện trạng | File | Status |
|---|-----------|---------|------------|------|--------|
| **2.1** | **Cấu trúc Sheet** |
| 35 | A1: Timestamp | Bot cập nhật | ⚠️ Chưa rõ | - | ⚠️ TODO |
| 36 | C1: Trạng thái hệ thống | RUNNING/XÓA CHỜ/XÓA VỊ THẾ/STOP | ⚠️ Chỉ có B2 | hd_order.py:102 | ⚠️ TODO |
| 37 | D1: Số mã đạt điều kiện | Bot tính | ❌ Không có | - | ❌ TODO |
| 38 | Cột B: Số lớp lệnh | User nhập | ❌ Không có | - | ❌ TODO |
| 39 | Cột C: Lệnh vừa khớp | Bot ghi timestamp+ID | ❌ Không có | - | ❌ TODO |
| 40 | Cột D: Mã lệnh hiện tại | 1a, 1b, 1c... | ❌ Không có | - | ❌ TODO |
| 41 | Cột E: Loại lệnh hiện tại | TRAILING/STOP/LIMIT | ❌ Không có | - | ❌ TODO |
| 42 | Cột F: Đòn bẩy đã khớp | Bot ghi | ❌ Không có | - | ❌ TODO |
| 43 | Cột G: Giá vào đã khớp | Bot ghi | ❌ Không có | - | ❌ TODO |
| **2.2** | **Loại lệnh Entry** |
| 44 | TRAILING_STOP Long/Short | Cột I | ✅ Có | hd_order.py:201 | ✅ |
| 45 | STOP_LIMIT Long/Short | Cột I | ❌ Không có | - | ❌ TODO |
| 46 | LIMIT Long/Short | Cột I | ❌ Không có | - | ❌ TODO |
| 47 | MARKET Long/Short | Cột I | ⚠️ Chỉ dùng STOP | hd_order.py:139 | ⚠️ TODO |
| **2.3** | **Loại lệnh Reduce Only** |
| 48 | TRAILING_STOP (reduce) | TP | ✅ Có | hd_order_123.py:205 | ✅ |
| 49 | STOP (reduce) | SL | ✅ Có | hd_order_123.py:164 | ✅ |
| 50 | LIMIT (reduce) | TP cố định | ❌ Không có | - | ❌ TODO |
| **2.4** | **Lệnh quản lý hệ thống** |
| 51 | STOP | Đóng all + Hủy all | ⚠️ Chỉ đóng all | hd_order.py:106 | ⚠️ TODO |
| 52 | XÓA CHỜ | Hủy lệnh pending | ❌ Không có | - | ❌ TODO |
| 53 | XÓA VỊ THẾ | Đóng positions | ❌ Không có | - | ❌ TODO |
| 54 | Hủy đơn lẻ | Theo Order ID | ⚠️ Có nhưng thủ công | hd_cancel_orders_schedule.py | ⚠️ TODO |
| 55 | Đóng vị thế đơn lẻ | Theo symbol | ❌ Không có | - | ❌ TODO |
| **2.5** | **Đọc config từ Sheet** |
| 56 | Đọc số lớp (Cột B) | Max 3-5 lớp | ❌ Không có | - | ❌ TODO |
| 57 | Đọc loại lệnh (Cột I) | TRAILING/STOP/LIMIT | ❌ Không có | - | ❌ TODO |
| 58 | Đọc đòn bẩy (Cột J) | 1-125x | ⚠️ Đọc từ Cột B (cũ) | hd_order.py:232 | ⚠️ TODO |
| 59 | Đọc callback (Cột K) | % | ⚠️ Đọc từ Cột C (cũ) | hd_order.py:242 | ⚠️ TODO |
| 60 | Đọc activation (Cột L) | Giá | ⚠️ Đọc từ Cột D (cũ) | hd_order.py:213 | ⚠️ TODO |
| 61 | Đọc stop price (Cột M) | Giá | ❌ Không có | - | ❌ TODO |
| 62 | Đọc limit price (Cột N) | Giá | ❌ Không có | - | ❌ TODO |
| 63 | Đọc vốn (Cột O) | USDT | ⚠️ Đọc từ Cột H (cũ) | hd_order.py:204 | ⚠️ TODO |

**Tỷ lệ hoàn thành Module 2: 3/29 = 10%**

---

### 3. LOGIC LUỒNG LỆNH

| # | Tính năng | Yêu cầu | Hiện trạng | File | Status |
|---|-----------|---------|------------|------|--------|
| **3.1** | **Flow cơ bản - 1 lớp** |
| 64 | Lệnh Entry (1a) | User đặt | ✅ Có | hd_order.py | ✅ |
| 65 | Auto tạo Stop Loss (1b) | Sau 1a khớp | ✅ Có | hd_order_123.py:158 | ✅ |
| 66 | Auto tạo Take Profit (1c) | Sau 1a khớp | ✅ Có | hd_order_123.py:203 | ✅ |
| 67 | Auto tạo Entry lớp 2 (2a) | Sau 1a khớp | ❌ Không có | - | ❌ TODO |
| **3.2** | **Flow đa lớp** |
| 68 | Cascade: 1a→1b+1c+2a | Auto | ❌ Không có | - | ❌ TODO |
| 69 | Cascade: 2a→2b+2c+3a | Auto | ❌ Không có | - | ❌ TODO |
| 70 | Cascade: 3a→3b+3c | Auto | ❌ Không có | - | ❌ TODO |
| 71 | Cascade: 3a→3b+3c+4a | Nếu max > 3 | ❌ Không có | - | ❌ TODO |
| **3.3** | **Xử lý TP khớp trước** |
| 72 | Hủy SL cùng lớp | 1c khớp → hủy 1b | ❌ Không có | - | ❌ TODO |
| 73 | Hủy Entry lớp tiếp | 1c khớp → hủy 2a | ❌ Không có | - | ❌ TODO |
| **3.4** | **Xử lý SL khớp trước** |
| 74 | Hủy TP cùng lớp | 1b khớp → hủy 1c | ❌ Không có | - | ❌ TODO |
| 75 | Giữ Entry lớp tiếp | 1b khớp → giữ 2a | ❌ Không có | - | ❌ TODO |
| **3.5** | **Nhiều lớp đồng thời** |
| 76 | Tracking nhiều lớp | Lớp 1+2+3 cùng lúc | ❌ Không có | - | ❌ TODO |
| 77 | Đóng từng lớp độc lập | TP/SL của từng lớp | ❌ Không có | - | ❌ TODO |

**Tỷ lệ hoàn thành Module 3: 3/14 = 21%**

---

### 4. XỬ LÝ LỖI VÀ CẢNH BÁO

| # | Tính năng | Yêu cầu | Hiện trạng | File | Status |
|---|-----------|---------|------------|------|--------|
| **4.1** | **Lỗi -4120** |
| 78 | Detect lỗi -4120 | Binance API change | ❌ Không có | - | ❌ TODO |
| 79 | Fallback Algo Order API | Auto chuyển | ❌ Không có | - | ❌ TODO |
| **4.2** | **Reduce Only sót** |
| 80 | Detect lệnh sót | Sau TP/SL | ⚠️ Có cơ bản | hd_alert_possition_and_open_order.py:131 | ⚠️ TODO |
| 81 | Retry 3 lần | Với delay | ❌ Không có | - | ❌ TODO |
| 82 | Verify sau mỗi lần | Check còn không | ❌ Không có | - | ❌ TODO |
| 83 | Telegram alert nếu fail | Sau 3 lần | ❌ Không có | - | ❌ TODO |
| 84 | Check trước entry mới | Đảm bảo không sót | ❌ Không có | - | ❌ TODO |
| **4.3** | **10+ lỗi thường gặp** |
| 85 | Trigger immediately | Skip, không retry | ❌ Không xử lý riêng | - | ❌ TODO |
| 86 | Binance blocked | Telegram + wait 5-10 min | ❌ Không xử lý riêng | - | ❌ TODO |
| 87 | API overload | Delay + retry | ❌ Không xử lý riêng | - | ❌ TODO |
| 88 | Symbol mismatch | Sync lại | ❌ Không xử lý riêng | - | ❌ TODO |
| 89 | Google token expired | Auto refresh | ⚠️ Có trong gg_sheet | gg_sheet_factory.py:31 | ⚠️ OK |
| 90 | Close all failed | Retry 5, alert | ❌ Không xử lý riêng | - | ❌ TODO |
| 91 | Insufficient balance | Skip + notify | ❌ Không xử lý riêng | - | ❌ TODO |
| 92 | Position not found | Skip | ❌ Không xử lý riêng | - | ❌ TODO |
| 93 | Rate limit exceeded | Exponential backoff | ❌ Không xử lý riêng | - | ❌ TODO |
| 94 | Invalid leverage | Dùng max, warn | ❌ Không xử lý riêng | - | ❌ TODO |
| **4.4** | **Retry mechanism** |
| 95 | Exponential backoff | 1s, 2s, 4s | ❌ Không có | - | ❌ TODO |
| 96 | Phân loại retry/skip | Theo loại lỗi | ❌ Không có | - | ❌ TODO |
| 97 | Log mỗi lần retry | Chi tiết | ⚠️ Có log cơ bản | - | ⚠️ TODO |
| **4.5** | **Mức độ cảnh báo** |
| 98 | INFO level | Thông tin thường | ⚠️ Chỉ có ERROR | - | ⚠️ TODO |
| 99 | WARNING level | Cảnh báo nhẹ | ⚠️ Chỉ có ERROR | - | ⚠️ TODO |
| 100 | ERROR level | Lỗi nghiêm trọng | ✅ Có | All files | ✅ |
| 101 | CRITICAL level | Dừng bot | ❌ Không có | - | ❌ TODO |

**Tỷ lệ hoàn thành Module 4: 1/24 = 4%**

---

### 5. TELEGRAM NOTIFICATION

| # | Tính năng | Yêu cầu | Hiện trạng | File | Status |
|---|-----------|---------|------------|------|--------|
| **5.1** | **Loại thông báo** |
| 102 | ✅ Lệnh khớp | Icon + full info | ⚠️ Text đơn giản | hd_order.py:261 | ⚠️ TODO |
| 103 | 🚨 Lỗi đặt lệnh | Code + message | ❌ Không gửi Telegram | - | ❌ TODO |
| 104 | ⛔ API bị chặn | Key + symbol + time | ❌ Không có | - | ❌ TODO |
| 105 | 📊 Báo cáo số dư | Mỗi 1h hoặc PNL>5% | ❌ Không có | - | ❌ TODO |
| 106 | 🛑 Kích hoạt STOP | Trạng thái + PNL | ❌ Không có | - | ❌ TODO |
| 107 | ✅ Hoàn tất STOP | Tổng lãi/lỗ | ❌ Không có | - | ❌ TODO |
| 108 | ⚠️ Reduce Only sót | Order IDs + retry | ❌ Không có | - | ❌ TODO |
| 109 | 🔴 Cảnh báo nghiêm trọng | Yêu cầu can thiệp | ❌ Không có | - | ❌ TODO |
| **5.2** | **Bot commands** |
| 110 | /status | Trạng thái bot | ❌ Không có | - | 🔵 OPTIONAL |
| 111 | /balance | Số dư | ❌ Không có | - | 🔵 OPTIONAL |
| 112 | /positions | Vị thế | ❌ Không có | - | 🔵 OPTIONAL |
| 113 | /orders | Lệnh chờ | ❌ Không có | - | 🔵 OPTIONAL |
| 114 | /stop | Dừng bot | ❌ Không có | - | 🔵 OPTIONAL |
| 115 | /resume | Chạy lại | ❌ Không có | - | 🔵 OPTIONAL |
| 116 | /cancel <symbol> | Hủy lệnh | ❌ Không có | - | 🔵 OPTIONAL |

**Tỷ lệ hoàn thành Module 5: 0/15 = 0%**  
*(Không tính optional items)*

---

## 📈 TỔNG KẾT

### Thống kê tổng thể

| Module | Items | Completed | In Progress | Not Started | % Done |
|--------|-------|-----------|-------------|-------------|---------|
| Module 1: Data | 34 | 10 | 5 | 19 | 29% |
| Module 2: Order | 29 | 3 | 7 | 19 | 10% |
| Module 3: Flow | 14 | 3 | 0 | 11 | 21% |
| Module 4: Error | 24 | 1 | 3 | 20 | 4% |
| Module 5: Telegram | 15 | 0 | 1 | 14 | 0% |
| **TỔNG** | **116** | **17** | **16** | **83** | **15%** |

### Biểu đồ ưu tiên

```
🔴 HIGH PRIORITY (Critical for operation)
├─ Fix API -4120 error
├─ Improve cancel reduce only
├─ Add XÓA CHỜ/XÓA VỊ THẾ commands
├─ Implement cascade logic
└─ Error handling improvements

🟡 MEDIUM PRIORITY (Core features)
├─ Complete 47+ columns data
├─ Add order types (STOP_LIMIT, LIMIT)
├─ Tracking state to sheet
└─ Tracking 30 prices

🟢 LOW PRIORITY (Nice to have)
├─ Rich Telegram notifications
├─ Bot commands 2-way
└─ Code polish
```

### Gap Analysis

**Biggest Gaps:**
1. **Flow đa lớp (cascade logic):** 0% - Core feature hoàn toàn thiếu
2. **Error handling nâng cao:** 4% - Cần cải thiện toàn diện
3. **Data collection đầy đủ:** 29% - Thiếu 24/34 items
4. **Telegram rich format:** 0% - Chỉ có text đơn giản

**Strengths:**
1. ✅ Kiến trúc modular tốt
2. ✅ Core MVP hoạt động (entry + SL/TP)
3. ✅ Google Sheets integration
4. ✅ Multi-threading architecture

---

## 🎯 KHUYẾN NGHỊ

### Phương án 1: Full Implementation (9-15 ngày)
**Mục tiêu:** 100% features theo QBot.md

**Pros:**
- Đạt đầy đủ yêu cầu
- Hệ thống hoàn chỉnh và scalable
- Ít maintenance sau này

**Cons:**
- Mất nhiều thời gian
- Risk cao nếu có blockers

### Phương án 2: MVP+ (5-7 ngày)
**Mục tiêu:** 60-70% features, focus vào critical

**Scope:**
- ✅ Phase 1: Critical fixes (100%)
- ✅ Phase 2: Core features - cascade logic (100%)
- ⚠️ Phase 3: Data collection (50% - chỉ items quan trọng)
- ⚠️ Phase 4: Telegram (30% - basic rich format)
- ❌ Phase 5: Polish (skip)

**Pros:**
- Nhanh hơn
- Focus vào functionality
- Có thể iterate sau

**Cons:**
- Không đầy đủ
- Cần refine sau

### Phương án 3: Phased Rollout (Recommended)
**Mục tiêu:** Triển khai từng phase, test kỹ

**Timeline:**
- Week 1: Phase 1 + 2 (Critical + Core)
- Week 2: Phase 3 (Data)
- Week 3: Phase 4 + 5 (Polish)

**Pros:**
- Giảm risk
- Test kỹ từng phase
- Flexible adjust

**Cons:**
- Tổng thời gian dài hơn

---

*Cập nhật: 15/12/2025*  
*Version: 1.0*

