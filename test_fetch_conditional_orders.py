import cst
import ccxt
from datetime import datetime
import sys
import os
import time

# --- CẤU HÌNH LOG ---
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
log_filename = f"scan_conditional_fapi_{now.strftime('%d_%m_%Y_%H_%M_%S')}.txt"
tee = TeeOutput(os.path.join(os.path.dirname(__file__), log_filename))
sys.stdout = tee

# --- KẾT NỐI BINANCE FUTURES (STANDARD) ---
print("🔄 Đang kết nối Binance USDS-M Futures...")
exchange = ccxt.binance({
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {
        'defaultType': 'future',
        'warnOnFetchOpenOrdersWithoutSymbol': False
    }
})

# --- HÀM KIỂM TRA LỆNH ĐIỀU KIỆN ---
def is_conditional_order(order):
    """
    Kiểm tra xem lệnh có phải là Conditional (Trailing, Stop, Take Profit) không
    dựa trên 'type' hoặc 'origType' trong dữ liệu thô (info).
    """
    info = order.get('info', {})
    order_type = info.get('type', '').upper()
    orig_type = info.get('origType', '').upper()
    
    # Danh sách các loại lệnh điều kiện trong Standard Futures
    conditional_types = [
        'TRAILING_STOP_MARKET', 
        'STOP', 'STOP_MARKET', 
        'TAKE_PROFIT', 'TAKE_PROFIT_MARKET'
    ]
    
    if order_type in conditional_types or orig_type in conditional_types:
        return True, order_type
    return False, None

# --- CHẠY QUÉT ---
target_symbols = ['CELO/USDT', 'AIOT/USDT', 'VELODROME/USDT', 'FUN/USDT', 'EPT/USDT']

print(f"\n{'='*80}")
print(f"🚀 QUÉT LỆNH ĐIỀU KIỆN TRONG API CƠ BẢN (Standard Futures)")
print(f"{'='*80}\n")

for symbol in target_symbols:
    print(f"🔍 Kiểm tra Symbol: {symbol}")
    
    # 1. Lấy Lịch sử lệnh (Bao gồm cả Canceled/Filled)
    # LƯU Ý: Conditional Order khi trigger xong hay cancel đều nằm ở đây
    try:
        orders = exchange.fetch_orders(symbol, limit=50)
        found_count = 0
        
        for order in orders:
            is_cond, type_name = is_conditional_order(order)
            if is_cond:
                found_count += 1
                info = order['info']
                status_icon = "🟢" if order['status'] == 'closed' else "🔴" if order['status'] == 'canceled' else "⏳"
                
                # In chi tiết giống ảnh của bạn
                print(f"  {status_icon} [{type_name}] Status: {order['status'].upper()}")
                print(f"      Time: {datetime.fromtimestamp(order['timestamp']/1000)}")
                print(f"      ID: {order['id']}")
                print(f"      Amount: {info.get('origQty')} (USDT estimate: {float(info.get('origQty')) * float(info.get('price', 0) or info.get('activatePrice', 0))})")
                print(f"      ⚡ Trigger Price: {info.get('activatePrice', 'N/A')}")
                print(f"      📉 Callback Rate: {info.get('priceRate', 'N/A')}%")
                print("-" * 40)
        
        if found_count == 0:
            print("  ⚠️  Chỉ tìm thấy lệnh thường (Market/Limit), không có Conditional.")
            
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")

    time.sleep(0.5) # Tránh rate limit

print(f"\n{'='*80}")
print("✅ KẾT THÚC.")
tee.close()
input("Nhấn Enter để thoát...")