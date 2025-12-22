"""
Script test để kiểm tra lấy danh sách Conditional (Algo) orders từ Binance
Test cả open orders và order history (cancelled/filled)
"""
import cst
import ccxt
from datetime import datetime
import sys
import os

# Class để ghi log vào cả console và file
class TeeOutput:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log_file = open(file_path, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()  # Đảm bảo ghi ngay vào file
    
    def flush(self):
        self.terminal.flush()
        self.log_file.flush()
    
    def close(self):
        if self.log_file:
            self.log_file.close()

# Tạo tên file log với format: test_DD_MM_YYYY_HH_MM_SS.txt
now = datetime.now()
log_filename = f"test_{now.strftime('%d_%m_%Y_%H_%M_%S')}.txt"
log_file_path = os.path.join(os.path.dirname(__file__), log_filename)

# Thiết lập log file
tee = TeeOutput(log_file_path)
sys.stdout = tee

print(f"📝 Log file: {log_filename}\n")

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'enableRateLimit': True,  
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {
        'defaultType': 'future',
        'warnOnFetchOpenOrdersWithoutSymbol': False
    }
})
exchange.setSandboxMode(False)

def is_trailing_stop_order(order):
    """Kiểm tra order có phải TRAILING_STOP không"""
    info = order.get('info', {})
    order_type = order.get('type', '').lower()
    algo_type = info.get('algoType', '')
    
    return (
        'trailing' in order_type or
        algo_type == 'VP' or
        order_type == 'trailing_stop_market'
    )

def format_order_info(order):
    """Format thông tin order để hiển thị"""
    info = order.get('info', {})
    return {
        'id': order.get('id', 'N/A'),
        'symbol': order.get('symbol', 'N/A'),
        'type': order.get('type', 'N/A'),
        'side': order.get('side', 'N/A'),
        'status': order.get('status', 'N/A'),
        'algoId': info.get('algoId', 'N/A'),
        'algoType': info.get('algoType', 'N/A'),
        'activatePrice': info.get('activatePrice', 'N/A'),
        'callbackRate': info.get('callbackRate', 'N/A'),
        'algoStatus': info.get('algoStatus', 'N/A'),
        'quantity': info.get('quantity', 'N/A'),
        'createTime': info.get('createTime', 'N/A')
    }

print(f"\n{'='*100}")
print(f"🔍 TEST LẤY CONDITIONAL ORDERS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*100}\n")

# ============================================================================
# TEST 1: Lấy OPEN ORDERS (Conditional)
# ============================================================================
print("📋 TEST 1: Lấy OPEN CONDITIONAL ORDERS\n")
print("-" * 100)

try:
    print("[STEP 1.1] Gọi fetch_open_orders() không chỉ định symbol...")
    all_open_orders = exchange.fetch_open_orders()
    print(f"✅ Thành công! Tổng số open orders: {len(all_open_orders) if all_open_orders else 0}")
    
    if all_open_orders:
        conditional_orders = []
        basic_orders = []
        
        for order in all_open_orders:
            info = order.get('info', {})
            algo_id = info.get('algoId', None)
            algo_type = info.get('algoType', None)
            activate_price = info.get('activatePrice', None)
            order_type = order.get('type', '').lower()
            
            # Phân loại Conditional vs Basic
            is_conditional = (
                algo_id is not None or
                'trailing' in order_type or
                activate_price is not None or
                algo_type is not None
            )
            
            if is_conditional:
                conditional_orders.append(order)
            else:
                basic_orders.append(order)
        
        print(f"\n📊 PHÂN LOẠI:")
        print(f"  - Conditional Orders: {len(conditional_orders)}")
        print(f"  - Basic Orders: {len(basic_orders)}")
        
        if conditional_orders:
            print(f"\n🔵 CONDITIONAL ORDERS ({len(conditional_orders)} orders):")
            for idx, order in enumerate(conditional_orders, 1):
                order_info = format_order_info(order)
                is_trailing = is_trailing_stop_order(order)
                trailing_marker = " [TRAILING_STOP]" if is_trailing else ""
                
                print(f"\n  [{idx}] {order_info['symbol']}{trailing_marker}")
                print(f"      Order ID: {order_info['id']}")
                print(f"      Algo ID: {order_info['algoId']}")
                print(f"      Type: {order_info['type']} | AlgoType: {order_info['algoType']}")
                print(f"      Side: {order_info['side']} | Status: {order_info['status']}")
                print(f"      Activation Price: {order_info['activatePrice']}")
                print(f"      Callback Rate: {order_info['callbackRate']}")
                print(f"      Algo Status: {order_info['algoStatus']}")
                print(f"      Quantity: {order_info['quantity']}")
        else:
            print("\n⚠️  Không tìm thấy Conditional orders nào trong open orders")
    else:
        print("\n⚠️  Không có open orders nào")
        
except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 2: Lấy orders theo SYMBOL cụ thể
# ============================================================================
print(f"\n\n{'='*100}")
print("📋 TEST 2: Lấy orders theo SYMBOL cụ thể\n")
print("-" * 100)

test_symbols = ['EPT/USDT', 'FUN/USDT', 'VELODROME/USDT', 'AIOT/USDT', 'CELO/USDT']

for symbol in test_symbols:
    print(f"\n🔍 Kiểm tra {symbol}:")
    try:
        symbol_orders = exchange.fetch_open_orders(symbol)
        if symbol_orders:
            conditional_count = sum(1 for o in symbol_orders if is_trailing_stop_order(o))
            print(f"  ✅ Tìm thấy {len(symbol_orders)} orders, trong đó {conditional_count} là TRAILING_STOP")
            
            for order in symbol_orders:
                if is_trailing_stop_order(order):
                    order_info = format_order_info(order)
                    print(f"    - Order ID: {order_info['id']}, Status: {order_info['status']}, Activation: {order_info['activatePrice']}")
        else:
            print(f"  ⚠️  Không có open orders cho {symbol}")
    except Exception as e:
        print(f"  ❌ Lỗi khi lấy orders cho {symbol}: {e}")

# ============================================================================
# TEST 3: Thử lấy ORDER HISTORY (cancelled/filled orders)
# ============================================================================
print(f"\n\n{'='*100}")
print("📋 TEST 3: Thử lấy ORDER HISTORY (Cancelled/Filled orders)\n")
print("-" * 100)

try:
    print("[STEP 3.1] Gọi fetch_orders() để lấy order history...")
    # fetch_orders() có thể lấy cả open và closed orders
    # Nhưng có thể không hỗ trợ cho algo orders
    all_orders = exchange.fetch_orders(limit=50)
    print(f"✅ Thành công! Tổng số orders (history): {len(all_orders) if all_orders else 0}")
    
    if all_orders:
        cancelled_conditional = []
        filled_conditional = []
        
        for order in all_orders:
            if is_trailing_stop_order(order):
                status = order.get('status', '').lower()
                if 'cancel' in status or status == 'canceled':
                    cancelled_conditional.append(order)
                elif status == 'closed' or status == 'filled':
                    filled_conditional.append(order)
        
        print(f"\n📊 CONDITIONAL ORDERS trong history:")
        print(f"  - Cancelled: {len(cancelled_conditional)}")
        print(f"  - Filled: {len(filled_conditional)}")
        
        if cancelled_conditional:
            print(f"\n🔴 CANCELLED CONDITIONAL ORDERS ({len(cancelled_conditional)} orders):")
            for idx, order in enumerate(cancelled_conditional[:10], 1):  # Chỉ hiển thị 10 đầu tiên
                order_info = format_order_info(order)
                print(f"  [{idx}] {order_info['symbol']} - Order ID: {order_info['id']}, Algo ID: {order_info['algoId']}")
        
        if filled_conditional:
            print(f"\n🟢 FILLED CONDITIONAL ORDERS ({len(filled_conditional)} orders):")
            for idx, order in enumerate(filled_conditional[:10], 1):  # Chỉ hiển thị 10 đầu tiên
                order_info = format_order_info(order)
                print(f"  [{idx}] {order_info['symbol']} - Order ID: {order_info['id']}, Algo ID: {order_info['algoId']}")
    
except Exception as e:
    print(f"❌ Lỗi khi lấy order history: {e}")
    print("💡 Lưu ý: fetch_orders() có thể không hỗ trợ algo orders, chỉ hỗ trợ basic orders")

# ============================================================================
# TEST 4: Thử dùng fetch_closed_orders()
# ============================================================================
print(f"\n\n{'='*100}")
print("📋 TEST 4: Thử dùng fetch_closed_orders()\n")
print("-" * 100)

try:
    print("[STEP 4.1] Gọi fetch_closed_orders()...")
    closed_orders = exchange.fetch_closed_orders(limit=50)
    print(f"✅ Thành công! Tổng số closed orders: {len(closed_orders) if closed_orders else 0}")
    
    if closed_orders:
        conditional_closed = [o for o in closed_orders if is_trailing_stop_order(o)]
        print(f"  - Conditional orders trong closed orders: {len(conditional_closed)}")
        
        if conditional_closed:
            print(f"\n🟡 CONDITIONAL ORDERS trong closed orders ({len(conditional_closed)} orders):")
            for idx, order in enumerate(conditional_closed[:10], 1):
                order_info = format_order_info(order)
                print(f"  [{idx}] {order_info['symbol']} - Order ID: {order_info['id']}, Status: {order_info['status']}, Algo ID: {order_info['algoId']}")
    
except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*100}")
print(f"✅ Hoàn thành test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*100}\n")
print(f"📝 Kết quả đã được lưu vào: {log_filename}\n")

# Đóng file log
tee.close()
sys.stdout = tee.terminal
