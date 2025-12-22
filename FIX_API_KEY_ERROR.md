# 🔧 HƯỚNG DẪN FIX LỖI API KEY

## ❌ Lỗi: `Invalid API-key, IP, or permissions for action.`

Lỗi này xảy ra khi Binance API không chấp nhận API key của bạn.

---

## 🔍 Nguyên nhân có thể:

### 1. **API Key không đúng**
- API key hoặc secret key bị sai
- API key đã bị xóa hoặc thay đổi trên Binance

### 2. **IP không được whitelist**
- Binance API yêu cầu whitelist IP addresses
- IP hiện tại của bạn không có trong danh sách whitelist

### 3. **API Key thiếu quyền**
- API key không có quyền **Futures Trading**
- Cần enable "Enable Futures" trong API settings

---

## ✅ Cách fix:

### Bước 1: Kiểm tra API Key trên Binance

1. Đăng nhập vào [Binance](https://www.binance.com/)
2. Vào **API Management**: `User Center` → `API Management`
3. Tìm API key bạn đang dùng
4. Kiểm tra:
   - ✅ API key còn **active** không?
   - ✅ Đã enable **"Enable Futures"** chưa?
   - ✅ Đã enable **"Enable Reading"** chưa?
   - ✅ Đã enable **"Enable Withdrawals"** (nếu cần) chưa?

### Bước 2: Whitelist IP Address

**QUAN TRỌNG:** Binance có thể yêu cầu whitelist IP!

1. Vào API key settings
2. Tìm phần **"Restrict access to trusted IPs only"**
3. Nếu đã bật, hãy thêm IP hiện tại của bạn:
   - Hoặc tắt tính năng này (không khuyến khích vì kém an toàn)
   - Hoặc thêm IP vào whitelist

**Cách lấy IP hiện tại:**
```bash
# Trên macOS/Linux
curl ifconfig.me

# Hoặc
curl ipinfo.io/ip
```

### Bước 3: Tạo API Key mới (nếu cần)

Nếu API key cũ không dùng được:

1. Tạo API key mới:
   - `User Center` → `API Management` → `Create API`
   - Chọn type: **System generated** (khuyến khích)
   - Label: Đặt tên dễ nhớ (vd: "Trade Bot")

2. Cấu hình permissions:
   - ✅ Enable Reading
   - ✅ Enable Futures (QUAN TRỌNG!)
   - ❌ Enable Withdrawals (chỉ bật nếu cần)

3. IP Restriction:
   - Nếu bật: Thêm IP của server/máy bạn
   - Nếu không bật: Không giới hạn IP (kém an toàn)

4. Lưu lại API key và Secret key (chỉ hiện 1 lần!)

### Bước 4: Cập nhật vào code

API key được lưu trong file `cst.py` hoặc được import từ config:

**Kiểm tra file `cst.py`:**
```python
key_binance = "YOUR_API_KEY_HERE"
secret_binance = "YOUR_SECRET_KEY_HERE"
```

**Cập nhật:**
```python
key_binance = "your_new_api_key"
secret_binance = "your_new_secret_key"
```

---

## 🧪 Test API Key

Sau khi cập nhật, test lại:

```bash
cd "/Users/kcode/Documents/Sources/DeepViewJSC/Trade Bot/qbot"
source venv/bin/activate
python test_fetch_orders_simple.py
```

**Nếu thành công:**
```
✅ Lấy được X orders
✅ fetch_open_orders() TRẢ VỀ ĐƯỢC ALGO ORDERS!
```

**Nếu vẫn lỗi:**
- Kiểm tra lại API key permissions
- Kiểm tra IP whitelist
- Kiểm tra network connection

---

## ⚠️ Lưu ý bảo mật:

1. **KHÔNG commit API key lên Git!**
   - Thêm `cst.py` vào `.gitignore`
   - Hoặc dùng environment variables

2. **Giới hạn permissions:**
   - Chỉ bật permissions cần thiết
   - Không bật "Enable Withdrawals" nếu không cần

3. **IP Whitelist:**
   - Nên bật IP whitelist nếu có IP cố định
   - Không bật nếu IP thay đổi thường xuyên (như home IP)

---

## 📞 Support:

Nếu vẫn không fix được:
1. Kiểm tra [Binance API Documentation](https://binance-docs.github.io/apidocs/spot/en/)
2. Liên hệ Binance Support
3. Kiểm tra log chi tiết để xem lỗi cụ thể

---

**Tác giả:** Claude AI  
**Ngày:** 2025-01-19
