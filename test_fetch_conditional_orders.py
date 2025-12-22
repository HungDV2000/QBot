import cst
import ccxt
from datetime import datetime
import sys
import os

# --- Giữ nguyên Class TeeOutput của bạn ---
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

# Thiết lập log
now = datetime.now()
log_filename = f"fix_test_{now.strftime('%d_%m_%Y_%H_%M_%S')}.txt"
log_file_path = os.path.join(os.path.dirname(__file__), log_filename)
tee = TeeOutput(log_file_path)
sys.stdout = tee

# Khởi tạo Exchange
exchange = ccxt.binance({
    'enableRateLimit': True,
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {'defaultType': 'future'}
})

def clean_symbol(symbol):
    """Binance Algo API yêu cầu format CELOUSDT thay vì CELO/USDT"""
    return symbol.replace('/', '')

def get_algo_orders(symbol=None, is_open=True):
    """
    Hàm lõi để lấy lệnh Algo (Trailing Stop, v.v.)
    is_open=True: Lấy lệnh đang treo
    is_open=False: Lấy lịch sử (Finished/Canceled)
    """
    params = {}
    if symbol:
        params['symbol'] = clean_symbol(symbol)
    
    try:
        if is_open:
            # Endpoint: /fapi/v1/algo/allOpenOrders
            response = exchange.fapiPrivateGetAlgoAllOpenOrders(params)
        else:
            # Endpoint: /fapi/v1/algo/historicalOrders
            # Thêm limit để lấy nhiều hơn nếu cần
            params['limit'] = 50 
            response = exchange.fapiPrivateGetAlgoHistoricalOrders(params)
        
        # Binance trả về dạng {"data": [...], "total": 1, "code": 200}
        return response.get('data', []) [cite: 8]
    except Exception as e:
        print(f"  ❌ Lỗi API Algo ({symbol}): {e}")
        return []

print(f"\n{'='*100}")
print(f"🚀 FIX TEST: TRUY VẤN ALGO ORDERS (TRAILING STOP) - {now}")
print(f"{'='*100}\n")

test_symbols = ['EPT/USDT', 'FUN/USDT', 'VELODROME/USDT', 'AIOT/USDT', 'CELO/USDT']

# ============================================================================
# BƯỚC 1: LẤY LỆNH ALGO ĐANG MỞ (OPEN)
# ============================================================================
print("📋 PHẦN 1: KIỂM TRA LỆNH ALGO ĐANG TREO (OPEN)")
print("-" * 100)
open_algo = get_algo_orders(is_open=True)
if open_algo:
    print(f"✅ Tìm thấy {len(open_algo)} lệnh Algo đang đợi kích hoạt:")
    for order in open_algo:
        print(f"  - [{order.get('symbol')}] ID: {order.get('algoId')} | Type: {order.get('algoType')} | Price: {order.get('activatePrice')}")
else:
    print("⚠️ Không có lệnh Algo nào đang mở.")

# ============================================================================
# BƯỚC 2: LẤY LỊCH SỬ LỆNH ALGO (FINISHED / CANCELED)
# ============================================================================
print(f"\n\n📋 PHẦN 2: KIỂM TRA LỊCH SỬ LỆNH ALGO (THEO TỪNG SYMBOL)")
print("-" * 100)

for symbol in test_symbols:
    print(f"\n🔍 Đang truy vấn lịch sử cho {symbol}...")
    history = get_algo_orders(symbol, is_open=False)
    
    if history:
        print(f"  ✅ Tìm thấy {len(history)} lệnh trong lịch sử:")
        for order in history:
            # Mapping trạng thái để dễ đọc
            status = order.get('algoStatus')
            color = "🟢" if status == "FINISHED" else "🔴"
            print(f"    {color} ID: {order.get('algoId')} | Type: {order.get('algoType')} | Status: {status} | Time: {datetime.fromtimestamp(order.get('time')/1000)}")
    else:
        print(f"  ⚠️ Không tìm thấy dữ liệu lịch sử Algo cho {symbol}.")

print(f"\n{'='*100}")
print(f"✅ Hoàn thành test. Kết quả lưu tại: {log_filename}")
print(f"{'='*100}\n")
tee.close()