# KIỂM TRA CONFIG.INI VS GOOGLE SHEET

## 📊 **PHÂN TÍCH TỪ HÌNH ẢNH:**

### ✅ **1. Tab Name:**
- **Sheet:** `TEST ĐẶT LỆNH (100 MÃ)`
- **Config:** `tab_dat_lenh = TEST ĐẶT LỆNH (100 MÃ)`
- **Kết quả:** ✅ **KHỚP**

---

### ✅ **2. Trạng thái hệ thống:**
- **Sheet:** B2 = `LONG`
- **Code:** Đọc C1 trước, nếu không có → fallback B2
- **Kết quả:** ✅ **OK** (Code sẽ đọc được từ B2)

**Lưu ý:** Nếu muốn rõ ràng hơn, nên đặt giá trị vào C1 thay vì B2.

---

### ✅ **3. Vốn mặc định:**
- **Sheet:** E2 = `1.12`
- **Code:** Đọc từ E2
- **Kết quả:** ✅ **KHỚP**

---

### ⚠️ **4. CẤU TRÚC CỘT - VẤN ĐỀ QUAN TRỌNG!**

**Config hiện tại:**
```ini
order_column_structure = new
```

**Dữ liệu trong Sheet (Row 5 - PIPPIN/USDT):**
- **Cột B:** `1` (có dữ liệu) ← Leverage trong cấu trúc CŨ
- **Cột C:** `7.08%` (có dữ liệu) ← Callback trong cấu trúc CŨ
- **Cột D:** `5.770730698` (có dữ liệu) ← Activation trong cấu trúc CŨ
- **Cột I:** Trống ← Loại lệnh trong cấu trúc MỚI
- **Cột J:** Trống ← Leverage trong cấu trúc MỚI
- **Cột K:** Trống ← Callback trong cấu trúc MỚI
- **Cột L:** Trống ← Activation trong cấu trúc MỚI
- **Cột O:** Trống ← Vốn trong cấu trúc MỚI

**Phân tích:**
- ✅ Sheet đang dùng **CẤU TRÚC CŨ** (dữ liệu ở B, C, D)
- ❌ Config đang set **CẤU TRÚC MỚI** (`order_column_structure = new`)
- ❌ **KHÔNG KHỚP!** Bot sẽ đọc từ cột J, K, L, O (trống) → Bỏ qua dòng này!

---

## 🔧 **GIẢI PHÁP:**

### **Option 1: Đổi config sang cấu trúc CŨ (Khuyên dùng)**

```ini
# config.ini
order_column_structure = old
```

**Ưu điểm:**
- ✅ Khớp với dữ liệu hiện tại trong sheet
- ✅ Không cần chỉnh sửa sheet

**Nhược điểm:**
- ❌ Chỉ hỗ trợ TRAILING_STOP (không có STOP_LIMIT, LIMIT, MARKET)

---

### **Option 2: Điền dữ liệu vào cấu trúc MỚI trong sheet**

Giữ nguyên `order_column_structure = new` và điền dữ liệu vào:

**Ví dụ cho PIPPIN/USDT (Row 5):**
- **Cột A:** `PIPPIN/USDT:USDT` (đã có, nhưng cần thêm `:USDT`)
- **Cột I:** `TRAILING_STOP`
- **Cột J:** `1` (từ B5)
- **Cột K:** `7.08` (từ C5, bỏ dấu %)
- **Cột L:** `5.770730698` (từ D5)
- **Cột O:** `1.12` hoặc để trống (dùng E2)

**Ưu điểm:**
- ✅ Hỗ trợ đầy đủ 4 loại lệnh
- ✅ Có cột tracking (C, D, E, F, G)

**Nhược điểm:**
- ❌ Cần chỉnh sửa lại toàn bộ sheet

---

## ✅ **KHUYẾN NGHỊ:**

**Dựa vào hình ảnh, khuyến nghị:**

### **Nếu sheet đang dùng cấu trúc CŨ (B, C, D):**

```ini
# Sửa config.ini
order_column_structure = old
```

**Và đảm bảo:**
- Cột B: Đòn bẩy (VD: `1`, `10`, `20`)
- Cột C: Callback Rate (VD: `7.08%`, `1`)
- Cột D: Activation Price (VD: `5.770730698`)
- Cột H: Vốn USDT (tùy chọn, nếu trống dùng E2)

---

## ⚠️ **LƯU Ý:**

1. **Phải khớp config với sheet:**
   - Config `new` → Sheet phải có dữ liệu ở I, J, K, L, O
   - Config `old` → Sheet phải có dữ liệu ở B, C, D, H

2. **Kiểm tra trước khi chạy:**
   - Xem log: `tail -f hd_order.log | grep "Cấu trúc cột"`
   - Nếu thấy "Leverage index: 9" nhưng dữ liệu ở cột B → SAI!

3. **Symbol format:**
   - Trong sheet: `PIPPIN/USDT`
   - Bot cần: `PIPPIN/USDT:USDT` (có `:USDT` ở cuối cho Futures)
   - Cần kiểm tra xem symbol có đúng format không

---

**Ngày kiểm tra:** 2025-01-18
