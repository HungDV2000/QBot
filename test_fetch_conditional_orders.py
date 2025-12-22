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
                info = order.get('info', {})
                status_icon = "🟢" if order.get('status') == 'closed' else "🔴" if order.get('status') == 'canceled' else "⏳"
                
                # In chi tiết đầy đủ
                print(f"\n  {status_icon} [{type_name}] Status: {order.get('status', 'N/A').upper()}")
                print(f"      {'='*70}")
                
                # Thông tin cơ bản
                print(f"      📅 Time: {datetime.fromtimestamp(order['timestamp']/1000) if order.get('timestamp') else 'N/A'}")
                print(f"      🆔 Order ID: {order.get('id', 'N/A')}")
                print(f"      💱 Symbol: {order.get('symbol', 'N/A')}")
                print(f"      📊 Side: {order.get('side', 'N/A').upper()}")
                
                # Thông tin từ order['info']
                print(f"\n      📋 Chi tiết từ order['info']:")
                print(f"         - orderId: {info.get('orderId', 'N/A')}")
                print(f"         - clientOrderId: {info.get('clientOrderId', 'N/A')}")
                print(f"         - price: {info.get('price', 'N/A')}")
                print(f"         - origQty: {info.get('origQty', 'N/A')}")
                print(f"         - executedQty: {info.get('executedQty', 'N/A')}")
                print(f"         - status: {info.get('status', 'N/A')}")
                print(f"         - timeInForce: {info.get('timeInForce', 'N/A')}")
                print(f"         - type: {info.get('type', 'N/A')}")
                print(f"         - origType: {info.get('origType', 'N/A')}")
                print(f"         - reduceOnly: {info.get('reduceOnly', 'N/A')}")
                print(f"         - closePosition: {info.get('closePosition', 'N/A')}")
                
                # Thông tin đặc biệt cho Conditional Orders
                print(f"\n      ⚡ Thông tin Conditional Order:")
                print(f"         - activatePrice: {info.get('activatePrice', 'N/A')}")
                print(f"         - priceRate: {info.get('priceRate', 'N/A')}")
                print(f"         - priceProtect: {info.get('priceProtect', 'N/A')}")
                print(f"         - stopPrice: {info.get('stopPrice', 'N/A')}")
                print(f"         - workingType: {info.get('workingType', 'N/A')}")
                
                # Thông tin Algo (nếu có)
                if 'algoId' in info or 'algoType' in info:
                    print(f"\n      🤖 Thông tin Algo:")
                    print(f"         - algoId: {info.get('algoId', 'N/A')}")
                    print(f"         - algoType: {info.get('algoType', 'N/A')}")
                    print(f"         - algoStatus: {info.get('algoStatus', 'N/A')}")
                    print(f"         - callbackRate: {info.get('callbackRate', 'N/A')}")
                
                # Timestamps
                print(f"\n      ⏰ Timestamps:")
                if info.get('time'):
                    print(f"         - time (create): {datetime.fromtimestamp(info['time']/1000) if info.get('time') else 'N/A'}")
                if info.get('updateTime'):
                    print(f"         - updateTime: {datetime.fromtimestamp(info['updateTime']/1000) if info.get('updateTime') else 'N/A'}")
                if info.get('createTime'):
                    print(f"         - createTime: {datetime.fromtimestamp(info['createTime']/1000) if info.get('createTime') else 'N/A'}")
                
                # Tính toán USDT value
                try:
                    qty = float(info.get('origQty', 0) or 0)
                    price_val = float(info.get('price', 0) or info.get('activatePrice', 0) or 0)
                    usdt_value = qty * price_val
                    if usdt_value > 0:
                        print(f"\n      💰 Giá trị ước tính: {usdt_value:.8f} USDT (Qty: {qty} × Price: {price_val})")
                except:
                    pass
                
                # Tất cả keys trong info để debug
                print(f"\n      🔍 Tất cả keys trong order['info']: {list(info.keys())}")
                print(f"      {'-'*70}")
        
        if found_count == 0:
            print("  ⚠️  Chỉ tìm thấy lệnh thường (Market/Limit), không có Conditional.")
            
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")

    time.sleep(0.5) # Tránh rate limit

print(f"\n{'='*80}")
print("✅ KẾT THÚC.")
tee.close()
input("Nhấn Enter để thoát...")