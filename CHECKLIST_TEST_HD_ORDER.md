# CHECKLIST TEST hd_order.py

## ✅ **KIỂM TRA TRƯỚC KHI TEST**

### 1. Config và Dependencies

- [x] ✅ `config.ini` có `order_column_structure = new` (hoặc `old`)
- [x] ✅ `cst.py` đã đọc config `order_column_structure`
- [x] ✅ API keys đã cấu hình (Binance, Telegram, Google Sheets)
- [x] ✅ `credentials.json` và `token.json` cho Google Sheets đã có
- [ ] ⚠️ Kiểm tra `test_mode = false` nếu muốn đặt lệnh thật
- [ ] ⚠️ Kiểm tra `test_mode = true` nếu chỉ muốn test (chưa implement trong code)

### 2. Google Sheet Setup

- [ ] ✅ Sheet "ĐẶT LỆNH (100 MÃ)" đã tồn tại
- [ ] ✅ Ô C1 có giá trị: `LONG`, `SHORT`, `CHỜ`, `STOP`, `XÓA CHỜ`, hoặc `XÓA VỊ THẾ`
- [ ] ✅ Ô E2 có giá trị vốn mặc định (VD: `372`)
- [ ] ✅ Cấu trúc cột trong sheet khớp với `order_column_structure` trong config:
  - Nếu `new`: Có dữ liệu ở cột I, J, K, L, M, N, O
  - Nếu `old`: Có dữ liệu ở cột B, C, D, H
- [ ] ✅ Ít nhất 1 dòng có symbol hợp lệ (VD: `BTC/USDT:USDT`)

### 3. Binance Account

- [ ] ✅ Tài khoản Binance Futures đã enable
- [ ] ✅ Có đủ USDT trong ví Futures
- [ ] ✅ API key có quyền Futures Trading
- [ ] ✅ Đã test API key hoạt động (có thể test với script nhỏ)

### 4. Code Validation

- [x] ✅ Logic detect cấu trúc dùng config (không auto-detect)
- [x] ✅ Validation leverage != "N" và is_number
- [x] ✅ Validation activation price is_number
- [x] ✅ Error handling cơ bản có
- [x] ✅ Logging đầy đủ
- [ ] ⚠️ **CẦN KIỂM TRA:** Symbol format validation (có thể thêm)

---

## 🚀 **CÁC BƯỚC TEST**

### Bước 1: Test với test_mode (nếu có)

**Lưu ý:** Code hiện tại chưa implement `test_mode`, cần thêm nếu muốn test an toàn.

### Bước 2: Test với cấu trúc CŨ

```ini
# config.ini
order_column_structure = old
```

**Setup Sheet:**
- C1 = `CHỜ` (để an toàn)
- Hàng 4: A4 = `BTC/USDT:USDT`, B4 = `10`, C4 = `1`, D4 = `43000`, H4 = `100`

**Chạy bot:**
```bash
python -u hd_order.py
```

**Kiểm tra:**
- [ ] Bot không đặt lệnh khi C1 = `CHỜ`
- [ ] Đổi C1 = `LONG` hoặc `SHORT`
- [ ] Bot scan và log đúng cấu trúc CŨ
- [ ] Bot không đặt lệnh nếu B4 = `N`

### Bước 3: Test với cấu trúc MỚI

```ini
# config.ini
order_column_structure = new
```

**Setup Sheet:**
- C1 = `CHỜ` (để an toàn)
- Hàng 55: A55 = `BTC/USDT:USDT`, I55 = `TRAILING_STOP`, J55 = `10`, K55 = `1`, L55 = `43000`, O55 = `200`

**Chạy bot:**
```bash
python -u hd_order.py
```

**Kiểm tra:**
- [ ] Bot log: "Cấu trúc cột: MỚI (từ config)"
- [ ] Bot đọc đúng cột J, K, L, O
- [ ] Bot không đặt lệnh nếu J55 = `N`

### Bước 4: Test đặt lệnh thật (CẨN THẬN!)

**Setup an toàn:**
1. Đặt vốn nhỏ (E2 = `20` hoặc O55 = `20`)
2. Đặt đòn bẩy thấp (10x)
3. Test với 1 symbol
4. C1 = `LONG` hoặc `SHORT`

**Chạy:**
```bash
python -u hd_order.py > output.log 2>&1 &
tail -f hd_order.log
```

**Kiểm tra:**
- [ ] Bot tạo lệnh trên Binance
- [ ] Nhận thông báo Telegram
- [ ] Lệnh xuất hiện trong Binance Futures
- [ ] Log file có thông tin đầy đủ

---

## ⚠️ **LƯU Ý QUAN TRỌNG**

### 1. Symbol Validation

Code hiện tại chưa validate format symbol đầy đủ. Nên thêm:

```python
# Kiểm tra symbol có hợp lệ không
if not sym or not sym.strip():
    logger.warning(f"Symbol trống, bỏ qua dòng")
    continue

# Kiểm tra format (nên có /USDT:USDT)
if "/USDT:USDT" not in sym and ":USDT" not in sym:
    logger.warning(f"Symbol format không đúng: {sym}, bỏ qua")
    continue
```

### 2. Test Mode

Code chưa implement test_mode, nên thêm:

```python
if cst.test_mode:
    logger.info(f"[TEST MODE] Sẽ tạo lệnh: {symbol} {order_type_str}")
    continue  # Không tạo lệnh thật
```

### 3. Error Handling

Cần cải thiện error handling cho từng loại lệnh:

```python
except Exception as e:
    logger.error(f"Lỗi khi tạo lệnh {order_type_str} cho {symbol}: {e}")
    import traceback
    traceback.print_exc()
```

### 4. Validation dữ liệu

Cần validate thêm:
- Callback rate phải > 0 và < 100
- Activation price phải > 0
- Capital phải > 0
- Stop price và Limit price phải hợp lý

---

## ✅ **KẾT LUẬN**

**Code đã sẵn sàng test CƠ BẢN**, nhưng nên:

1. ⚠️ **Test với `C1 = CHỜ` trước** để đảm bảo bot không đặt lệnh
2. ⚠️ **Test với vốn nhỏ** (20-50 USDT)
3. ⚠️ **Theo dõi log file** cẩn thận
4. ✅ **Cân nhắc thêm validation** trước khi test thật với số tiền lớn

---

**Ngày tạo:** 2025-01-18  
**Version:** QBot v2.0
