import cst
import ccxt
from datetime import datetime
import sys
import os
import time

# ==============================================================================
# 1. CẤU HÌNH LOGGING
# ==============================================================================
class TeeOutput:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log_file = open(file_path, 'w', encoding='utf-8')
    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()
    def flush(self):
        self.terminal.flush()
        self.log_file.flush()
    def close(self):
        if self.log_file: self.log_file.close()

now = datetime.now()
log_filename = f"scan_trailing_{now.strftime('%d_%m_%Y_%H_%M_%S')}.txt"
log_file_path = os.path.join(os.path.dirname(__file__), log_filename)
tee = TeeOutput(log_file_path)
sys.stdout = tee

# ==============================================================================
# 2. KHỞI TẠO (QUAN TRỌNG)
# ==============================================================================
print(f"📝 Log file: {log_filename}")
print("🔄 Đang kết nối Binance Futures...")

exchange = ccxt.binance({
    'enableRateLimit': True,
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {
        'defaultType': 'future', 
        'adjustForTimeDifference': True,
        # Tắt cảnh báo strict rate limit khi không truyền symbol (dù ta sẽ truyền)
        'warnOnFetchOpenOrdersWithoutSymbol': False 
    }
})

# ==============================================================================
# 3. HÀM XỬ LÝ
# ==============================================================================

def get_trailing_details(order):
    """
    Hàm này "bóc tách" dữ liệu thô để tìm dấu hiệu của Trailing Stop
    """
    info = order.get('info', {})
    
    # 1. Kiểm tra Type
    o_type = info.get('type', '').upper()
    o_orig_type = info.get('origType', '').upper()
    
    is_trailing = 'TRAILING' in o_type or 'TRAILING' in o_orig_type
    
    if not is_trailing:
        return None

    # 2. Lấy thông số kỹ thuật (Trigger, Callback)
    #
    activate_price = info.get('activatePrice', 'N/A') 
    callback_rate = info.get('priceRate', 'N/A')
    
    # Status Mapping
    status_map = {
        'NEW': '⏳ Đang chờ (Active)',
        'CANCELED': '🔴 Đã hủy',
        'FILLED': '🟢 Đã khớp',
        'EXPIRED': '⚪ Hết hạn'
    }
    status_display = status_map.get(info.get('status'), info.get('status'))

    return {
        'id': order['id'],
        'symbol': order['symbol'],
        'side': order['side'],
        'amount': order['amount'],
        'status': status_display,
        'trigger': activate_price,
        'callback': callback_rate,
        'raw_status': info.get('status')
    }

# ==============================================================================
# 4. CHẠY QUÉT
# ==============================================================================
# Danh sách coin bạn đang trade trong ảnh
target_symbols = ['CELO/USDT', 'AIOT/USDT', 'VELODROME/USDT', 'FUN/USDT', 'EPT/USDT']

print(f"\n{'='*80}")
print(f"🚀 BẮT ĐẦU QUÉT TRAILING STOP (Chuẩn API Futures) - {now}")
print(f"{'='*80}\n")

for symbol in target_symbols:
    print(f"🔍 Đang kiểm tra: {symbol}")
    has_data = False
    
    try:
        # BƯỚC 1: LẤY LỆNH ĐANG TREO (OPEN)
        # Sử dụng fetch_open_orders CÓ tham số symbol để tránh lỗi Rate Limit
        open_orders = exchange.fetch_open_orders(symbol)
        
        for order in open_orders:
            details = get_trailing_details(order)
            if details:
                print(f"  ➤ [OPEN] {details['side']} {details['symbol']} | {details['status']}")
                print(f"      ID: {details['id']} | Amount: {details['amount']} USDT")
                print(f"      ⚡ Trigger Price: {details['trigger']} | Callback: {details['callback']}%")
                has_data = True

        # BƯỚC 2: LẤY LỊCH SỬ LỆNH (HISTORY)
        # Trailing Stop đã Hủy/Khớp nằm ở đây
        history_orders = exchange.fetch_orders(symbol, limit=20) # Lấy 20 lệnh gần nhất
        
        count_hist = 0
        for order in history_orders:
            details = get_trailing_details(order)
            if details:
                print(f"  ➤ [HISTORY] {details['side']} {details['symbol']} | {details['status']}")
                print(f"      ID: {details['id']} | Amount: {details['amount']} USDT")
                print(f"      ⚡ Trigger Price: {details['trigger']} | Callback: {details['callback']}%")
                count_hist += 1
                has_data = True
        
        if count_hist > 0:
            print(f"     (Tìm thấy {count_hist} lệnh Trailing Stop trong lịch sử)")

    except Exception as e:
        print(f"  ❌ Lỗi: {e}")

    if not has_data:
        print("  ⚠️  Không tìm thấy lệnh Trailing Stop nào.")
    
    print("-" * 50)
    # Nghỉ 0.2s để tránh spam API
    time.sleep(0.2) 

print(f"\n{'='*80}")
print("✅ HOÀN TẤT.")
print(f"📂 Kết quả lưu tại: {log_filename}")
print(f"{'='*80}\n")

tee.close()

# Giữ terminal không tắt
try:
    if os.name == 'nt': os.system('pause')
    else: input("💡 Nhấn Enter để thoát...")
except: pass