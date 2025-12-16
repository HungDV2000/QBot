# **TÀI LIỆU YÊU CẦU QBOT \- TRADING BOT BINANCE FUTURES**

**Phiên bản:** 2.0  
**Ngày cập nhật:** 13/12/2025

---

## **1\. TỔNG QUAN**

QBot là trading bot tự động cho Binance Futures với 3 chức năng chính:

1. **Lấy dữ liệu:** Thu thập dữ liệu thị trường từ Binance và ghi vào Google Sheets (Sheet "Data")  
2. **Đặt lệnh tự động:** Đọc điều kiện từ Google Sheets (Sheet "Order") và thực hiện lệnh  
3. **Giám sát:** Cập nhật trạng thái và cảnh báo qua Telegram

---

## **2\. SHEET DATA \- MODULE LẤY DỮ LIỆU**

### **2.1 Thông tin tài khoản**

**Vị trí và tần suất:**

* Ô A1: Thời gian cập nhật (cập nhật mỗi lần chạy)  
* Ô A2: Funding Rate (5 phút/lần)  
* Ô B2: Margin Balance (5 phút/lần)  
* Ô C2: Wallet Balance (5 phút/lần)  
* Ô D2: Unrealized PNL (5 phút/lần)

### **2.2 Cấu trúc dữ liệu các mã**

**Cấu trúc hàng:**

* Hàng 3: Tiêu đề các cột (tên các chỉ số)  
* Hàng 4: Dữ liệu BTC/USDT (luôn ở vị trí cố định)  
* Hàng 5: Dữ liệu BTCDOM/USDT (luôn ở vị trí cố định)  
* Hàng 6 trở xuống: Các mã khác, sắp xếp theo % tăng/giảm 24h (từ cao xuống thấp)

**Lưu ý:** Mã tăng mạnh nhất ở trên cùng, giảm sâu nhất ở dưới cùng

### **2.3 Danh sách 47+ cột dữ liệu**

**Nhóm 1: Thông tin cơ bản (4 cột)**

1. Tên cặp mã (VD: ETH/USDT)  
2. % thay đổi trong 24h  
3. Giá hiện thời (cập nhật dưới 1 phút \- ưu tiên cao)  
4. Thời điểm niêm yết

**Nhóm 2: Khối lượng giao dịch (5 cột)** 5\. Volume khung 15 phút 6\. Volume khung 1 giờ 7\. Volume khung 4 giờ 8\. Volume khung 1 ngày 9\. Volume khung 1 tuần (mới thêm)

**Nhóm 3: Bollinger Bands khung 15 phút (4 cột)** 10\. Giá trị dải trên Bollinger Band 15p 11\. Giá trị dải dưới Bollinger Band 15p 12\. Biên độ tăng mạnh nhất trong tuần khung 15p 13\. Biên độ giảm mạnh nhất trong tuần khung 15p

**Nhóm 4: Bollinger Bands khung 1 giờ (6 cột)** 14\. Giá trị dải trên Bollinger Band 1h 15\. Giá trị dải dưới Bollinger Band 1h 16\. Biên độ tăng mạnh nhất trong tuần khung 1h 17\. Biên độ giảm mạnh nhất trong tuần khung 1h 18\. Biên độ tăng mạnh nhất trong tháng khung 1h 19\. Biên độ giảm mạnh nhất trong tháng khung 1h

**Nhóm 5: Bollinger Bands khung 4 giờ (4 cột)** 20\. Giá trị dải trên Bollinger Band 4h 21\. Giá trị dải dưới Bollinger Band 4h 22\. Biên độ tăng mạnh nhất trong tuần khung 4h 23\. Biên độ giảm mạnh nhất trong tuần khung 4h

**Nhóm 6: Bollinger Bands khung 1 ngày (4 cột)** 24\. Giá trị dải trên Bollinger Band 1D 25\. Giá trị dải dưới Bollinger Band 1D 26\. Biên độ tăng mạnh nhất trong tháng khung 1D 27\. Biên độ giảm mạnh nhất trong tháng khung 1D

**Nhóm 7: Bollinger Bands khung 1 tuần (4 cột)** 28\. Giá trị dải trên Bollinger Band 1W 29\. Giá trị dải dưới Bollinger Band 1W 30\. Biên độ tăng mạnh nhất trong 3 tháng khung 1W 31\. Biên độ giảm mạnh nhất trong 3 tháng khung 1W

**Nhóm 8: Bollinger Bands khung 1 tháng (4 cột)** 32\. Giá trị dải trên Bollinger Band 1M 33\. Giá trị dải dưới Bollinger Band 1M 34\. Biên độ tăng mạnh nhất trong năm khung 1M 35\. Biên độ giảm mạnh nhất trong năm khung 1M

**Nhóm 9: Giá cao/thấp lịch sử (12 cột)** 36\. Giá cao nhất trong 3 ngày 37\. Thời điểm đạt giá cao nhất trong 3 ngày 38\. Giá cao nhất trong 7 ngày 39\. Thời điểm đạt giá cao nhất trong 7 ngày 40\. Giá cao nhất trong 30 ngày 41\. Thời điểm đạt giá cao nhất trong 30 ngày 42\. Giá thấp nhất trong 3 ngày 43\. Thời điểm đạt giá thấp nhất trong 3 ngày 44\. Giá thấp nhất trong 7 ngày 45\. Thời điểm đạt giá thấp nhất trong 7 ngày 46\. Giá thấp nhất trong 30 ngày 47\. Thời điểm đạt giá thấp nhất trong 30 ngày

**Nhóm 10: Chênh lệch giá kích hoạt (2 cột)** 48\. Chênh lệch giữa giá kích hoạt LONG với đáy gần nhất 49\. Chênh lệch giữa giá kích hoạt SHORT với đỉnh gần nhất

**Lưu ý:** Có thể có thêm các cột khác theo sheet tham khảo `12Jm6lPdYcLysR6ZyrdFVaPZz3y1sS7nniNLHDdeXtaQ`

### **2.4 Tính năng đặc biệt**

**2.4.1 Top 50 mã cực trị**

Bot tự động lọc và đánh dấu:

* Top 50 mã có giá hiện tại gần giá cao nhất 30 ngày  
* Top 50 mã có giá hiện tại gần giá thấp nhất 30 ngày

**2.4.2 Tracking 30 mức giá cho lệnh đã đặt**

Với các mã ở trạng thái "Chờ" hoặc "Khớp":

* Lưu giá đặt lệnh  
* Lưu giá khớp lệnh (nếu đã khớp)  
* Lưu 30 mức giá gần nhất sau khi đặt lệnh  
* Tần suất: Mỗi 1 phút

Ví dụ:

* Đặt lệnh lúc 5:00  
* Hiện tại 10:00  
* Lưu 30 mức giá từ 9:30 đến 10:00 (mỗi phút 1 điểm)

---

## **3\. SHEET ORDER \- MODULE ĐẶT LỆNH**

### **3.1 Thông tin header (Hàng 1-2)**

**Hàng 1:**

* Ô A1: Thời gian cập nhật (do bot cập nhật, 5 phút/lần)  
* Ô C1: Trạng thái hệ thống (RUNNING / XÓA CHỜ / XÓA VỊ THẾ / STOP)  
* Ô D1: Số mã đạt điều kiện

**Hàng 2:**

* Ô A2: API Key Binance (do bot điền)  
* Ô B2: Server endpoint (do bot điền)  
* Hàng 2 còn chứa giá trị chi tiết của Trạng thái và Số mã đạt

### **3.2 Cấu trúc lệnh cho từng mã (Từ hàng 3\)**

**Nhóm cột tracking (do bot cập nhật):**

* Cột A: Tên cặp mã (do user nhập)  
* Cột B: Số lớp lệnh (do user nhập, mặc định 3\)  
* Cột C: Lệnh vừa khớp (bot ghi timestamp \+ Order ID)  
* Cột D: Mã lệnh hiện tại (1a, 1b, 1c, 2a, 2b...)  
* Cột E: Loại lệnh hiện tại (TRAILING STOP / STOP LIMIT / LIMIT \+ Long/Short)  
* Cột F: Đòn bẩy đã khớp  
* Cột G: Giá vào đã khớp

**Nhóm cột lệnh tiếp theo (do user nhập):**

* Cột H: Mã lệnh tiếp theo (1a, 1b, 1c, 2a...)  
* Cột I: Loại lệnh tiếp theo (TRAILING STOP / STOP LIMIT / LIMIT, có thể có "reduce only")  
* Cột J: Đòn bẩy  
* Cột K: Callback % (cho lệnh Trailing Stop)  
* Cột L: Activation Price (giá kích hoạt cho Trailing Stop)  
* Cột M: Stop Price (cho lệnh Stop Limit)  
* Cột N: Limit Price (cho lệnh Limit và Stop Limit)  
* Cột O: Vốn gốc (chưa nhân đòn bẩy)

### **3.3 Các loại lệnh**

**Lệnh Entry (vào vị thế mới):**

* TRAILING STOP Long/Short  
* STOP LIMIT Long/Short  
* LIMIT Long/Short  
* MARKET Long/Short

**Lệnh Reduce Only (đóng vị thế):**

* TRAILING STOP (reduce only) \- dùng cho Take Profit  
* STOP LIMIT (reduce only) \- dùng cho Stop Loss  
* LIMIT (reduce only) \- dùng cho Take Profit cố định

**Lưu ý:** Lệnh Stop Loss và Take Profit luôn có cờ "reduce only", quantity \= 100% vị thế đang giữ

### **3.4 Lệnh quản lý hệ thống**

**Lệnh XÓA CHỜ:**

* Mục đích: Hủy tất cả lệnh chờ khi thị trường biến động bất thường  
* Hành động: Hủy tất cả lệnh pending, giữ nguyên vị thế đang mở  
* Kích hoạt: User đổi ô C1 thành "XÓA CHỜ"

**Lệnh XÓA VỊ THẾ:**

* Mục đích: Đóng tất cả vị thế nhưng giữ lệnh chờ  
* Hành động: Đóng tất cả positions bằng lệnh MARKET, giữ nguyên lệnh chờ  
* Kích hoạt: User đổi ô C1 thành "XÓA VỊ THẾ"

**Lệnh STOP:**

* Mục đích: Dừng hoàn toàn bot khi đạt mục tiêu lãi/lỗ  
* Hành động: Đóng tất cả vị thế \+ Hủy tất cả lệnh chờ \+ Dừng bot  
* Kích hoạt: User đổi ô C1 thành "STOP" hoặc tự động khi đạt điều kiện  
* Cảnh báo: Đây là lệnh nguy hiểm nhất, cần xác nhận kỹ

**Lệnh hủy đơn lẻ:**

* Mục đích: Hủy 1 lệnh chờ cụ thể  
* Tham số: Tên mã \+ Order ID

**Lệnh đóng vị thế đơn lẻ:**

* Mục đích: Đóng vị thế của 1 mã cụ thể  
* Tham số: Tên mã \+ Side (LONG/SHORT)

---

## **4\. LOGIC LUỒNG LỆNH**

### **4.1 Quy ước đặt tên lệnh**

Mã lệnh có dạng: \[Lớp\]\[Loại\]

Ví dụ:

* 1a: Lệnh entry lớp 1  
* 1b: Lệnh Stop Loss lớp 1  
* 1c: Lệnh Take Profit lớp 1  
* 2a: Lệnh entry lớp 2  
* 2b: Lệnh Stop Loss lớp 2  
* 2c: Lệnh Take Profit lớp 2

### **4.2 Flow cơ bản**

**Bước 1: User điền lệnh entry ban đầu (1a)**

* Loại: TRAILING STOP / STOP LIMIT / LIMIT  
* Đòn bẩy, giá kích hoạt, callback, vốn...

**Bước 2: Khi lệnh 1a khớp**

Bot tự động tạo ngay 3 lệnh:

* Lệnh 1b (Stop Loss \- Reduce Only): Cắt lỗ, quantity \= 100% vị thế 1a  
* Lệnh 1c (Take Profit \- Reduce Only): Chốt lời, quantity \= 100% vị thế 1a  
* Lệnh 2a (Entry lớp 2): Entry tiếp theo theo cấu hình user

**Bước 3: Xử lý các trường hợp**

**Trường hợp 1: Khớp 1c (Take Profit) trước**

* Chốt lời thành công  
* Hủy lệnh 1b (không cần Stop Loss nữa)  
* Hủy lệnh 2a (không gia tầng nữa)  
* Kết thúc lớp 1

**Trường hợp 2: Khớp 1b (Stop Loss) trước**

* Cắt lỗ  
* Hủy lệnh 1c (không cần Take Profit nữa)  
* Giữ nguyên lệnh 2a (vẫn có thể entry lớp 2\)  
* Kết thúc lớp 1

**Trường hợp 3: Khớp 2a trước khi 1b hoặc 1c khớp**

* Giữ nguyên lệnh 1b, 1c của lớp 1  
* Tạo thêm lệnh 2b (Stop Loss lớp 2\)  
* Tạo thêm lệnh 2c (Take Profit lớp 2\)  
* Tạo thêm lệnh 3a (Entry lớp 3\)  
* Hiện đang có 2 lớp đồng thời

### **4.3 Flow đa lớp**

**Khi lớp 2 khớp:**

* Tạo lệnh 2b (Stop Loss lớp 2\)  
* Tạo lệnh 2c (Take Profit lớp 2\)  
* Tạo lệnh 3a (Entry lớp 3\)

**Khi lớp 3 khớp:**

* Tạo lệnh 3b (Stop Loss lớp 3\)  
* Tạo lệnh 3c (Take Profit lớp 3\)  
* Nếu số lớp \= 3 thì KHÔNG tạo 4a  
* Nếu số lớp \> 3 thì tạo tiếp lệnh 4a

**Lưu ý quan trọng:** Lớp 2, 3, 4 có thể khớp trước khi lớp 1 đóng

### **4.4 Sơ đồ tổng quát**

1a (Entry)  
│  
Khi 1a khớp → Tạo ngay 1b \+ 1c \+ 2a  
│  
├─ Nếu khớp 1c (TP)  
│  ├─ Hủy 1b  
│  ├─ Hủy 2a  
│  └─ XONG  
│  
├─ Nếu khớp 1b (SL)  
│  ├─ Hủy 1c  
│  └─ Giữ 2a (chờ entry lớp 2\)  
│  
└─ Nếu khớp 2a (trước khi 1b/1c khớp)  
   ├─ Giữ nguyên 1b, 1c  
   ├─ Tạo 2b (SL lớp 2\)  
   ├─ Tạo 2c (TP lớp 2\)  
   └─ Tạo 3a (Entry lớp 3\)

### **4.5 Trường hợp đặc biệt**

**Lệnh 1aa (Chống lỗ):**

* Chưa rõ yêu cầu cụ thể  
* Cần user làm rõ: Lệnh này là gì? Khi nào kích hoạt?

---

## **5\. XỬ LÝ LỖI VÀ CẢNH BÁO**

### **5.1 Lỗi Binance API Code \-4120**

**Mô tả:**

{"code":-4120,"msg":"Order type not supported for this endpoint.   
Please use the Algo Order API endpoints instead."}

**Nguyên nhân:** Binance đã thay đổi endpoint cho lệnh Trailing Stop

**Giải pháp:** Chuyển sang sử dụng Algo Order API cho các lệnh:

* Trailing Stop Market  
* TWAP  
* VP

### **5.2 Lỗi xóa lệnh Reduce Only (NGHIÊM TRỌNG)**

**Hiện trạng:**

* Sau khi khớp TP hoặc SL, các lệnh Reduce Only còn sót lại  
* Lệnh sót làm không thể vào lệnh mới  
* Bot hiện chỉ xóa được một phần, bị dừng tại mã XAI/USDT

**Yêu cầu xử lý:**

**Bước 1: Phát hiện lệnh sót**

* Sau khi khớp TP/SL, kiểm tra có lệnh reduce only còn sót không  
* Ghi log cảnh báo nếu phát hiện

**Bước 2: Xóa triệt để**

* Retry tối đa 3 lần  
* Mỗi lần xóa xong phải verify lại  
* Delay giữa các lần retry  
* Gửi cảnh báo Telegram nếu không xóa được

**Bước 3: Xác nhận trước khi entry mới**

* Kiểm tra không còn lệnh reduce only trước khi đặt lệnh mới  
* Nếu còn sót → Bỏ qua lệnh mới, gửi cảnh báo

**Bước 4: Log chi tiết**

* Ghi log mỗi bước xóa lệnh  
* Ghi log số lượng lệnh trước/sau khi xóa  
* Ghi log Order ID của các lệnh bị sót

### **5.3 Các lỗi thường gặp khác**

**1\. Trigger immediately**

* Nguyên nhân: Giá biến động quá nhanh, lệnh trailing/stop lạc hậu  
* Xử lý: Bỏ qua lệnh, ghi log, không retry

**2\. Binance blocked**

* Nguyên nhân: Mã biến động mạnh bị Binance chặn tạm thời  
* Xử lý: Gửi thông báo Telegram, bỏ qua mã trong 5-10 phút

**3\. API overload**

* Nguyên nhân: Quá nhiều request trong thời gian ngắn  
* Xử lý: Chia nhỏ batch, delay giữa các request, dùng nhiều API key

**4\. Symbol mismatch**

* Nguyên nhân: Binance thêm/bớt mã, dữ liệu không đồng bộ  
* Xử lý: Sync lại danh sách mã, cảnh báo

**5\. Google token expired**

* Nguyên nhân: OAuth token hết hạn  
* Xử lý: Tự động refresh token, nếu fail → dừng bot, cảnh báo

**6\. Close all failed**

* Nguyên nhân: Lỗi khi đóng toàn bộ vị thế  
* Xử lý: Retry 5 lần, gửi cảnh báo khẩn cấp, cần can thiệp thủ công

**7\. Insufficient balance**

* Nguyên nhân: Không đủ margin  
* Xử lý: Bỏ qua lệnh, thông báo

**8\. Position not found**

* Nguyên nhân: Cố đóng position không tồn tại  
* Xử lý: Ghi log, bỏ qua

**9\. Rate limit exceeded**

* Nguyên nhân: Vượt quá giới hạn request/phút  
* Xử lý: Delay với exponential backoff

**10\. Invalid leverage**

* Nguyên nhân: Đòn bẩy không hợp lệ cho mã  
* Xử lý: Dùng leverage tối đa của mã, cảnh báo

### **5.4 Chiến lược retry**

**Các lệnh NÊN retry:**

* Network timeout  
* Rate limit exceeded (với delay)  
* Server error 5xx  
* Cancel order failed

**Các lệnh KHÔNG nên retry:**

* Trigger immediately (giá đã qua)  
* Invalid symbol (mã không tồn tại)  
* Insufficient balance (cần nạp tiền)

**Cơ chế retry:**

* Retry tối đa 3 lần  
* Delay tăng dần (1s, 2s, 4s)  
* Ghi log mỗi lần retry

### **5.5 Mức độ cảnh báo**

* **INFO:** Thông tin bình thường, chỉ ghi log  
* **WARNING:** Cảnh báo nhẹ, ghi log \+ Telegram (tùy chọn)  
* **ERROR:** Lỗi nghiêm trọng, ghi log \+ Telegram alert  
* **CRITICAL:** Cực kỳ nguy hiểm, ghi log \+ Telegram \+ Dừng bot

---

## **6\. TELEGRAM NOTIFICATION**

### **6.1 Các loại thông báo**

**6.1.1 Thông báo lệnh khớp**

Nội dung bao gồm:

* Icon: ✅  
* Tiêu đề: LỆNH KHỚP  
* Tên mã  
* Mã lệnh và loại lệnh  
* Giá vào  
* Đòn bẩy  
* Vốn và giá trị position  
* Thời gian  
* Lệnh tiếp theo đã tạo (1b, 1c, 2a...)

**6.1.2 Thông báo lỗi đặt lệnh**

Nội dung bao gồm:

* Icon: 🚨  
* Tiêu đề: LỖI ĐẶT LỆNH  
* Tên mã  
* Mã lệnh  
* Mã lỗi (code)  
* Chi tiết lỗi (message)  
* Hành động đã thực hiện  
* Thời gian

**6.1.3 Thông báo API bị chặn**

Nội dung bao gồm:

* Icon: ⛔  
* Tiêu đề: BINANCE BLOCKED  
* API Key (hiển thị một phần)  
* Mã bị chặn  
* Lý do  
* Thời gian chờ retry  
* Thời gian

**6.1.4 Báo cáo số dư định kỳ**

Nội dung bao gồm:

* Icon: 📊  
* Tiêu đề: BÁO CÁO SỐ DƯ  
* Wallet Balance  
* Margin Balance  
* Unrealized PNL (số tiền và %)  
* Số vị thế đang mở  
* Số lệnh chờ  
* Thời gian

**6.1.5 Kích hoạt lệnh STOP**

Nội dung bao gồm:

* Icon: 🛑  
* Tiêu đề: LỆNH STOP KÍCH HOẠT  
* Trạng thái: Đang xử lý  
* Số vị thế đang mở  
* Số lệnh chờ  
* PNL hiện tại  
* Thời gian

**6.1.6 Xác nhận hoàn tất STOP**

Nội dung bao gồm:

* Icon: ✅  
* Tiêu đề: HOÀN TẤT STOP  
* Số vị thế đã đóng  
* Số lệnh đã hủy  
* Số dư cuối  
* Tổng lãi/lỗ  
* Thời gian

**6.1.7 Cảnh báo Reduce Only sót**

Nội dung bao gồm:

* Icon: ⚠️  
* Tiêu đề: REDUCE ONLY SÓT  
* Tên mã  
* Số lệnh sót  
* Danh sách Order ID  
* Trạng thái xử lý (đang retry lần X/3)  
* Thời gian

**6.1.8 Cảnh báo nghiêm trọng**

Nội dung bao gồm:

* Icon: 🔴  
* Tiêu đề: CẢNH BÁO NGHIÊM TRỌNG  
* Mô tả vấn đề  
* Yêu cầu can thiệp thủ công  
* Chi tiết lệnh/vị thế liên quan  
* Thời gian

### **6.2 Tần suất thông báo**

* Lệnh khớp: Real-time (mỗi lần có lệnh khớp)  
* Lỗi đặt lệnh: Real-time (mỗi lần có lỗi)  
* Số dư: 1 giờ/lần hoặc khi PNL thay đổi \> 5%  
* Trạng thái bot: 5 phút/lần nếu có thay đổi  
* API blocked: Real-time  
* STOP trigger: Real-time

### **6.3 Bot commands (Tùy chọn)**

Nếu cần tương tác 2 chiều, có thể thêm:

* /status \- Xem trạng thái bot  
* /balance \- Xem số dư tài khoản  
* /positions \- Danh sách vị thế đang giữ  
* /orders \- Danh sách lệnh chờ  
* /stop \- Dừng bot (cần confirm)  
* /resume \- Chạy lại bot  
* /cancel \<symbol\> \- Hủy lệnh chờ của 1 mã

---

## **7\. CÂU HỎI CẦN LÀM RÕ**

### **7.1 Về dữ liệu**

1. Sheet `12Jm6lPdYcLysR6ZyrdFVaPZz3y1sS7nniNLHDdeXtaQ` có thêm cột nào ngoài 47 cột đã liệt kê không?  
2. Có cần thêm chỉ số kỹ thuật nào khác không? (RSI, MACD, EMA...)  
3. Volume Ratio được tính như thế nào?  
4. "Chênh lệch giá kích hoạt" được tính dựa trên lệnh nào? (Lệnh đang chờ? Lệnh vừa khớp?)

### **7.2 Về logic lệnh**

5. Lệnh 1aa (chống lỗ) là gì? Khi nào kích hoạt? Tham số như thế nào?  
6. Mỗi lớp có thể có nhiều lệnh entry với mức giá khác nhau không? Hay 1 lớp \= 1 lệnh entry?  
7. Khi lớp 2 khớp trước khi lớp 1 đóng, nếu sau đó 1c khớp → có cần hủy 2b, 2c không?  
8. Lệnh MARKET dùng khi nào? Có trong flow tự động không hay chỉ dùng thủ công?

### **7.3 Về trạng thái hệ thống**

9. Lệnh STOP có tự động trigger không? Nếu có, điều kiện cụ thể là gì?  
10. STOP có cần confirm không? (Tránh stop nhầm do bug)  
11. Sau khi STOP, có tự động resume được không? Hay phải restart thủ công?

### **7.4 Về API và performance**

12. Dùng bao nhiêu API key? (1 key hay nhiều key để load balancing?)  
13. Có giới hạn số mã tối đa không? (100 mã, 200 mã?)  
14. Có cần hỗ trợ nhiều tài khoản Binance không? Nếu có → mỗi account 1 sheet riêng?

### **7.5 Về Telegram**

15. Telegram chat ID là cá nhân hay group?  
16. Có cần bot commands để tương tác không? (/stop, /status, /balance...)  
17. Tần suất báo cáo số dư cụ thể? (Mỗi giờ? Khi PNL thay đổi \> X%?)

### **7.6 Về chiến lược**

18. Có cần implement chiến lược BNF (panic buying) vào bot không? Hay chỉ là tài liệu tham khảo?  
19. Nếu implement BNF, có cần module tự động phát hiện panic selling không?

---

## **8\. PHỤ LỤC: CHIẾN LƯỢC THAM KHẢO \- TAKASHI KOTEGAWA (BNF)**

**Lưu ý:** Đây là tài liệu tham khảo, không phải yêu cầu implement.

### **8.1 Giới thiệu**

**Thông tin cơ bản:**

* Tên: Takashi Kotegawa  
* Biệt danh: BNF (còn gọi "J-Com man")  
* Thành tích: Biến 13,000 USD thành 150 triệu USD trong 8 năm  
* Thị trường: Chứng khoán Nhật Bản  
* Phong cách: Day trading, counter-trend

### **8.2 Nguyên tắc cốt lõi**

**1\. Mua khi panic \- Bán khi hồi phục**

* Đợi thị trường hoảng loạn, giá rơi mạnh  
* Mua khi người khác bán tháo  
* Bán khi giá hồi về mức cân bằng

**2\. Chỉ trade mã thanh khoản cao**

* Volume lớn  
* Spread hẹp  
* Vào ra nhanh không bị trượt giá

**3\. Counter-trend (Đi ngược đám đông)**

* Mua khi giá rơi 5-10% bất thường  
* Không "bắt dao rơi mù"  
* Dựa trên phân tích volume \+ price action

**4\. Quản trị rủi ro cực chặt**

* Mỗi lệnh chỉ rủi ro 1-2% tài khoản  
* Stop loss rõ ràng, không "ôm hy vọng"  
* Cắt lỗ nhanh, để lãi chạy nhưng không tham

**5\. Giao dịch ngắn hạn**

* Day trading hoặc giữ 1-3 ngày tối đa  
* Tránh rủi ro gap qua đêm

### **8.3 Setup cơ bản**

**Điều kiện vào lệnh:**

**Bước 1: Lọc mã**

* Thanh khoản cao (volume trên trung bình)  
* Biến độ động mạnh  
* Trong watchlist theo dõi

**Bước 2: Chờ panic**

* Giá rơi 5-10% trong thời gian ngắn  
* Volume tăng đột biến  
* Không có tin xấu thật sự nghiêm trọng

**Bước 3: Xác nhận đảo chiều**

* Nến pin bar hoặc engulfing  
* Volume mua tăng tại vùng hỗ trợ  
* Lực bán suy yếu

**Bước 4: Entry**

* Mua tại vùng hỗ trợ vừa test  
* Stop loss dưới đáy gần nhất  
* Risk 1-2% tài khoản

**Bước 5: Exit**

* Take profit khi hồi 1-3% (không tham)  
* Hoặc về gần MA / giá trung bình  
* Chốt sớm tốt hơn giữ lâu

**Ví dụ:**

* Mã ETH/USDT  
* Giá trung bình 7 ngày: $2,000  
* Giá rơi từ $2,000 xuống $1,850 (-7.5%) trong 30 phút  
* Volume tăng 300%  
* → Panic selling  
* Nến tạo long tail tại $1,840, đóng ở $1,860  
* Volume mua tăng đột biến  
* → Entry $1,860  
* Stop loss $1,835  
* Take profit $1,895 \- $1,920 (+2-3%)

### **8.4 Tâm lý \- Phần "thiên tài" của BNF**

**1\. Kỷ luật sắt**

* Tuân thủ stop loss 100%  
* Không revenge trade  
* Chấp nhận ngồi ngoài chờ setup tốt

**2\. Không dự đoán, chỉ phản ứng**

* "Đừng cố đoán thị trường. Hãy nhìn xem nó đang làm gì và hành động theo."

**3\. Sống giản dị**

* Dù giàu vẫn sống khiêm tốn  
* Coi trading là "trò chơi trí tuệ"  
* Không khoe khoang

**4\. Chăm chỉ và cô đơn**

* Thức khuya theo dõi thị trường  
* Ghi chép từng lệnh, rút kinh nghiệm  
* "Trader phòng trọ" huyền thoại

### **8.5 Áp dụng cho Crypto**

**Điểm khác biệt với chứng khoán:**

* Crypto biến động mạnh hơn (10-50% thay vì 5-10%)  
* Giao dịch 24/7 (không có gap qua đêm)  
* Đòn bẩy cao hơn (lên tới 125x)  
* Manipulation cao hơn

**Điều chỉnh:**

* Giảm leverage (10-20x thay vì cao)  
* Stop loss xa hơn (crypto biến động mạnh)  
* Take profit nhỏ hơn (1-3% vẫn đủ với leverage)  
* Cảnh giác với pump/dump giả mạo

**Setup crypto:**

* Điều kiện panic: Giá rơi \> 10% trong 1 giờ  
* Volume \> 500% trung bình  
* Funding rate cực âm (short quá đông)  
* Leverage: 10x  
* Risk: 1% tài khoản  
* Stop loss: 3% (= \-30% với 10x)  
* Take profit: 2% (= \+20% với 10x)

---

## **9\. TỔNG KẾT**

### **9.1 Tóm tắt các module chính**

**Module 1: Lấy dữ liệu (Sheet Data)**

* Lấy thông tin tài khoản (số dư, margin, PNL, funding rate)  
* Lấy 47+ cột dữ liệu cho tất cả các mã  
* BTC và BTCDOM luôn ở vị trí cố định (hàng 4, 5\)  
* Các mã khác sắp xếp theo % 24h  
* Giá hiện tại cập nhật dưới 1 phút  
* Dữ liệu khác cập nhật dưới 5 phút  
* Tính năng đặc biệt: Top 50 mã cực trị, tracking 30 mức giá

**Module 2: Đặt lệnh (Sheet Order)**

* Đọc cấu hình lệnh từ Google Sheets  
* Đặt lệnh tự động (Entry, Stop Loss, Take Profit)  
* Hỗ trợ nhiều loại lệnh (Trailing Stop, Stop Limit, Limit, Market)  
* Logic cascade đa lớp (1a→1b,1c,2a→2b,2c,3a...)  
* Quản lý vị thế tự động  
* Lệnh quản lý hệ thống (Xóa chờ, Xóa vị thế, STOP)

**Module 3: Xử lý lỗi**

* Xử lý lỗi API \-4120 (chuyển sang Algo API)  
* Xóa triệt để lệnh Reduce Only sót  
* Xử lý 10+ loại lỗi thường gặp  
* Retry mechanism với exponential backoff  
* Phân cấp mức độ cảnh báo

**Module 4: Telegram notification**

* Thông báo lệnh khớp  
* Thông báo lỗi chi tiết  
* Báo cáo số dư định kỳ  
* Cảnh báo API blocked  
* Cảnh báo reduce only sót  
* Thông báo STOP trigger  
* Bot commands (tùy chọn)

### **9.2 Điểm quan trọng cần nhớ**

**Về dữ liệu:**

* Giá hiện tại là ưu tiên cao nhất (\< 1 phút)  
* BTC và BTCDOM luôn ở vị trí cố định  
* Có thể có thêm cột ngoài 47 cột đã liệt kê

**Về logic lệnh:**

* Mỗi lớp có 3 lệnh: Entry (a), Stop Loss (b), Take Profit (c)  
* Khi entry khớp → tự động tạo SL \+ TP \+ entry lớp tiếp theo  
* Lớp 2,3,4 có thể khớp trước khi lớp 1 đóng  
* Lệnh SL và TP luôn là reduce only với quantity \= 100% vị thế

**Về xử lý lỗi:**

* Lỗi \-4120 phải chuyển sang Algo API  
* Lệnh Reduce Only sót là lỗi nghiêm trọng, phải xóa triệt để  
* Lệnh STOP là nguy hiểm nhất, cần xác nhận kỹ  
* Có 4 mức cảnh báo: INFO, WARNING, ERROR, CRITICAL

**Về Telegram:**

* Thông báo real-time cho lệnh khớp và lỗi  
* Báo cáo số dư mỗi giờ hoặc khi PNL thay đổi \> 5%  
* Format message rõ ràng với icon và phân cấp

### **9.3 Lưu ý cuối**

**Điểm cần làm rõ trước khi bắt đầu:**

* Có 19 câu hỏi trong mục 7 cần được trả lời  
* Đặc biệt là lệnh 1aa (chống lỗ) chưa rõ  
* Logic xử lý khi nhiều lớp khớp đan xen cần confirm  
* Điều kiện STOP tự động (nếu có) cần xác định

**Cảnh báo:**

* Đây là hệ thống giao dịch thực với tiền thật  
* Cần test kỹ trên Testnet trước  
* Luôn có kill switch để dừng khẩn cấp  
* Monitor 24/7 trong giai đoạn đầu  
* Backup config và logs thường xuyên

**Mục tiêu:**

* Bot chạy ổn định 24/7  
* Xử lý tự động mọi tình huống  
* Cảnh báo kịp thời qua Telegram  
* Không cần giám sát liên tục sau khi stable

---

## **PHỤ LỤC: THUẬT NGỮ**

**Các thuật ngữ tiếng Anh thường dùng:**

* **Leverage:** Đòn bẩy (vay của sàn)  
* **Reduce Only:** Lệnh chỉ đóng vị thế, không mở mới  
* **Entry:** Lệnh vào vị thế (mở position)  
* **Stop Loss (SL):** Lệnh cắt lỗ tự động  
* **Take Profit (TP):** Lệnh chốt lời tự động  
* **Trailing Stop:** Lệnh stop di chuyển theo giá  
* **Callback Rate:** % giá rút lui để kích hoạt trailing stop  
* **Activation Price:** Giá kích hoạt trailing stop  
* **Margin Balance:** Số dư margin (bao gồm PNL)  
* **Wallet Balance:** Số dư ví gốc  
* **Unrealized PNL:** Lãi/lỗ chưa chốt  
* **Funding Rate:** Phí định kỳ giữa long/short  
* **Volume:** Khối lượng giao dịch  
* **Bollinger Band:** Chỉ báo kỹ thuật (dải giá)  
* **Long:** Vị thế mua (cược giá tăng)  
* **Short:** Vị thế bán (cược giá giảm)  
* **Panic Selling:** Bán tháo hoảng loạn  
* **Slippage:** Chênh lệch giá khi khớp lệnh

---

*Tài liệu yêu cầu QBot \- Phiên bản 2.0*  
 *Ngày cập nhật: 13/12/2025*

