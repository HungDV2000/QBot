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
        import traceback
        traceback.print_exc()

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
    print("💡 Lưu ý: fetch_orders() cần symbol argument, sẽ test với từng symbol...")
    import traceback
    traceback.print_exc()
    
    # Thử với từng symbol cụ thể
    print(f"\n[STEP 3.2] Thử lấy order history cho từng symbol:")
    for symbol in test_symbols:
        try:
            print(f"\n  🔍 {symbol}:")
            symbol_history = exchange.fetch_orders(symbol, limit=20)
            print(f"    - Tổng số orders (history): {len(symbol_history) if symbol_history else 0}")
            
            if symbol_history:
                # Log sample order để xem structure
                if len(symbol_history) > 0:
                    sample = symbol_history[0]
                    print(f"    - Sample order keys: {list(sample.keys())}")
                    if 'info' in sample:
                        print(f"    - Sample order['info'] keys: {list(sample['info'].keys())}")
                
                conditional_in_history = [o for o in symbol_history if is_trailing_stop_order(o)]
                print(f"    - Conditional orders (detected): {len(conditional_in_history)}")
                
                cancelled_cond = [o for o in conditional_in_history if 'cancel' in o.get('status', '').lower() or o.get('status', '').lower() == 'canceled']
                filled_cond = [o for o in conditional_in_history if o.get('status', '').lower() in ['closed', 'filled', 'finished']]
                
                if cancelled_cond or filled_cond:
                    print(f"    - Cancelled: {len(cancelled_cond)}")
                    print(f"    - Filled/Finished: {len(filled_cond)}")
                    
                    if cancelled_cond:
                        for order in cancelled_cond[:5]:  # Hiển thị 5 đầu tiên
                            order_info = format_order_info(order)
                            print(f"      🔴 Cancelled: Order ID {order_info['id']}, Algo ID {order_info['algoId']}, Status: {order_info['status']}")
                    
                    if filled_cond:
                        for order in filled_cond[:5]:
                            order_info = format_order_info(order)
                            print(f"      🟢 Filled: Order ID {order_info['id']}, Algo ID {order_info['algoId']}, Status: {order_info['status']}")
                else:
                    print(f"    ⚠️  Không tìm thấy conditional orders (cancelled/filled) trong history")
            else:
                print(f"    ⚠️  Không có orders trong history")
        except Exception as e2:
            print(f"  ❌ {symbol}: {e2}")
            import traceback
            traceback.print_exc()

# ============================================================================
# TEST 4: Thử dùng fetch_closed_orders()
# ============================================================================
print(f"\n\n{'='*100}")
print("📋 TEST 4: Thử dùng fetch_closed_orders()\n")
print("-" * 100)

try:
    print("[STEP 4.1] Gọi fetch_closed_orders() cần symbol argument, sẽ test với từng symbol...")
    
    total_closed_conditional = []
    for symbol in test_symbols:
        try:
            print(f"\n  🔍 {symbol}:")
            symbol_closed = exchange.fetch_closed_orders(symbol, limit=20)
            print(f"    - Tổng số closed orders: {len(symbol_closed) if symbol_closed else 0}")
            
            if symbol_closed:
                # Log sample order để xem structure
                if len(symbol_closed) > 0:
                    sample = symbol_closed[0]
                    print(f"    - Sample closed order keys: {list(sample.keys())}")
                    if 'info' in sample:
                        print(f"    - Sample closed order['info'] keys: {list(sample['info'].keys())}")
                
                conditional_closed = [o for o in symbol_closed if is_trailing_stop_order(o)]
                total_closed_conditional.extend(conditional_closed)
                print(f"    - Conditional orders (detected): {len(conditional_closed)}")
                
                if conditional_closed:
                    for order in conditional_closed[:3]:  # Hiển thị 3 đầu tiên
                        order_info = format_order_info(order)
                        print(f"      - Order ID: {order_info['id']}, Status: {order_info['status']}, Algo ID: {order_info['algoId']}")
                else:
                    print(f"    ⚠️  Không tìm thấy conditional orders trong closed orders")
            else:
                print(f"    ⚠️  Không có closed orders")
        except Exception as e2:
            print(f"  ❌ {symbol}: {e2}")
            import traceback
            traceback.print_exc()
    
    if total_closed_conditional:
        print(f"\n✅ Tổng số conditional orders trong closed orders: {len(total_closed_conditional)}")
    else:
        print(f"\n⚠️  Không tìm thấy conditional orders trong closed orders")
    
except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 5: Thử dùng Binance API trực tiếp để lấy algo orders history
# ============================================================================
print(f"\n\n{'='*100}")
print("📋 TEST 5: Thử dùng Binance API trực tiếp (fapiPrivateGetAlgoOrdersHistory)\n")
print("-" * 100)

try:
    print("[STEP 5.1] Gọi Binance API trực tiếp để lấy algo orders history...")
    
    # Sử dụng exchange.apiCall() hoặc exchange.privateGet() để gọi Binance API trực tiếp
    # Endpoint: GET /fapi/v1/algo/ordersHistory
    # Docs: https://binance-docs.github.io/apidocs/futures/en/#algo-orders-history-user_data
    
    for symbol in test_symbols:
        try:
            print(f"\n  🔍 {symbol}:")
            # Chuyển symbol format: EPT/USDT -> EPTUSDT
            binance_symbol = symbol.replace('/', '')
            
            # Gọi API trực tiếp
            params = {
                'symbol': binance_symbol,
                'limit': 20
            }
            
            # Sử dụng privateGet cho futures API
            algo_orders_history = exchange.private_get_algo_orders_history(params)
            
            if algo_orders_history and 'data' in algo_orders_history:
                orders_data = algo_orders_history['data']
                print(f"    ✅ Tìm thấy {len(orders_data)} algo orders trong history")
                
                cancelled_algo = [o for o in orders_data if o.get('algoStatus', '').upper() == 'CANCELED']
                finished_algo = [o for o in orders_data if o.get('algoStatus', '').upper() == 'FINISHED']
                
                print(f"    - Cancelled: {len(cancelled_algo)}")
                print(f"    - Finished: {len(finished_algo)}")
                
                if cancelled_algo:
                    print(f"\n    🔴 CANCELLED ALGO ORDERS ({len(cancelled_algo)} orders):")
                    for idx, order in enumerate(cancelled_algo[:5], 1):
                        algo_id = order.get('algoId', 'N/A')
                        order_type = order.get('algoType', 'N/A')
                        activate_price = order.get('activatePrice', 'N/A')
                        callback_rate = order.get('callbackRate', 'N/A')
                        create_time = order.get('createTime', 'N/A')
                        print(f"      [{idx}] Algo ID: {algo_id}, Type: {order_type}, Activation: {activate_price}, Callback: {callback_rate}")
                
                if finished_algo:
                    print(f"\n    🟢 FINISHED ALGO ORDERS ({len(finished_algo)} orders):")
                    for idx, order in enumerate(finished_algo[:5], 1):
                        algo_id = order.get('algoId', 'N/A')
                        order_type = order.get('algoType', 'N/A')
                        activate_price = order.get('activatePrice', 'N/A')
                        print(f"      [{idx}] Algo ID: {algo_id}, Type: {order_type}, Activation: {activate_price}")
            elif algo_orders_history:
                print(f"    ⚠️  Response không có key 'data': {list(algo_orders_history.keys())}")
            else:
                print(f"    ⚠️  Không có algo orders trong history")
        except AttributeError:
            print(f"  ⚠️  {symbol}: API method không tồn tại, thử cách khác...")
            # Thử dùng apiCall trực tiếp
            try:
                method = 'fapiPrivateGetAlgoOrdersHistory'
                params = {'symbol': symbol.replace('/', ''), 'limit': 20}
                result = exchange.apiCall(method, params) if hasattr(exchange, 'apiCall') else None
                if result:
                    print(f"    ✅ Dùng apiCall(): {len(result.get('data', []))} orders")
            except Exception as e3:
                print(f"  ❌ {symbol}: Không thể gọi API trực tiếp - {e3}")
        except Exception as e2:
            print(f"  ❌ {symbol}: {e2}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"❌ Lỗi khi gọi Binance API trực tiếp: {e}")
    print("💡 Có thể API endpoint này không có trong CCXT, cần dùng Binance SDK hoặc requests trực tiếp")
    import traceback
    traceback.print_exc()

print(f"\n{'='*100}")
print(f"✅ Hoàn thành test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*100}\n")
print(f"📝 Kết quả đã được lưu vào: {log_filename}\n")

# Đóng file log
tee.close()
sys.stdout = tee.terminal
