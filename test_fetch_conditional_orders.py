import cst
import ccxt
from datetime import datetime
import sys
import os
import time
import requests
import hmac
import hashlib
import urllib.parse

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
        
        for idx, order in enumerate(orders, 1):
            # In cấu trúc order để debug
            print(f"\n  📦 Order #{idx} - Cấu trúc:")
            print(f"      order keys: {list(order.keys())}")
            if 'info' in order:
                print(f"      order['info'] keys: {list(order.get('info', {}).keys())}")
            
            # In một số giá trị cơ bản từ order
            print(f"      order['id']: {order.get('id', 'N/A')}")
            print(f"      order['symbol']: {order.get('symbol', 'N/A')}")
            print(f"      order['type']: {order.get('type', 'N/A')}")
            print(f"      order['status']: {order.get('status', 'N/A')}")
            if 'info' in order:
                info = order.get('info', {})
                print(f"      order['info']['type']: {info.get('type', 'N/A')}")
                print(f"      order['info']['origType']: {info.get('origType', 'N/A')}")
                print(f"      order['info']['status']: {info.get('status', 'N/A')}")
            
            # Kiểm tra có phải conditional order không
            is_cond, type_name = is_conditional_order(order)
            print(f"      → Is Conditional: {is_cond}, Type: {type_name}")
            
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
                try:
                    if info.get('time'):
                        time_val = info.get('time')
                        if isinstance(time_val, (int, float)):
                            print(f"         - time (create): {datetime.fromtimestamp(time_val/1000)}")
                        else:
                            print(f"         - time (create): {time_val} (raw value)")
                except Exception as e:
                    print(f"         - time (create): Error converting - {e}")
                
                try:
                    if info.get('updateTime'):
                        update_time = info.get('updateTime')
                        if isinstance(update_time, (int, float)):
                            print(f"         - updateTime: {datetime.fromtimestamp(update_time/1000)}")
                        else:
                            print(f"         - updateTime: {update_time} (raw value)")
                except Exception as e:
                    print(f"         - updateTime: Error converting - {e}")
                
                try:
                    if info.get('createTime'):
                        create_time = info.get('createTime')
                        if isinstance(create_time, (int, float)):
                            print(f"         - createTime: {datetime.fromtimestamp(create_time/1000)}")
                        else:
                            print(f"         - createTime: {create_time} (raw value)")
                except Exception as e:
                    print(f"         - createTime: Error converting - {e}")
                
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

# ============================================================================
# TEST 2: Dùng Binance Algo Orders API trực tiếp (cho USDS-M Futures)
# Endpoint: /fapi/v1/algo/...
# ============================================================================
print(f"\n\n{'='*80}")
print("📋 TEST 2: Dùng Binance Algo Orders API (/fapi/v1/algo/...)")
print(f"{'='*80}\n")

def call_binance_api_direct(method, endpoint, params=None):
    """
    Gọi Binance API trực tiếp bằng requests (nếu CCXT không hỗ trợ)
    """
    base_url = 'https://fapi.binance.com'
    url = f"{base_url}{endpoint}"
    
    if params is None:
        params = {}
    
    # Thêm timestamp
    params['timestamp'] = int(time.time() * 1000)
    
    # Tạo query string
    query_string = urllib.parse.urlencode(params)
    
    # Tạo signature
    signature = hmac.new(
        cst.secret_binance.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    
    # Headers
    headers = {
        'X-MBX-APIKEY': cst.key_binance
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  ❌ Lỗi khi gọi API trực tiếp: {e}")
        return None

def get_algo_orders_via_fapi(symbol=None, is_open=True, use_all_algo_orders=False):
    """
    Lấy algo orders qua Binance API
    USDS-M Futures endpoints:
    - Open: /fapi/v1/openAlgoOrders (Current All Algo Open Orders)
    - All: /fapi/v1/allAlgoOrders (Query All Algo Orders - bao gồm cả history)
    """
    try:
        params = {}
        if symbol:
            params['symbol'] = symbol.replace('/', '')
        
        if use_all_algo_orders:
            # Dùng /fapi/v1/allAlgoOrders - Query All Algo Orders
            # Symbol: YES (mandatory)
            # Request weight: 5
            if not symbol:
                print(f"  ⚠️  allAlgoOrders cần symbol (mandatory), bỏ qua")
                return []
            
            # Dùng API trực tiếp vì CCXT có thể không hỗ trợ
            response = call_binance_api_direct('GET', '/fapi/v1/allAlgoOrders', params)
            if response:
                print(f"  ✅ Lấy all algo orders thành công (endpoint: /fapi/v1/allAlgoOrders)")
            else:
                return []
                    
        elif is_open:
            # Lấy open algo orders - /fapi/v1/openAlgoOrders
            # Symbol: NO (optional)
            # Request weight: 1 (single) hoặc 40 (all)
            response = call_binance_api_direct('GET', '/fapi/v1/openAlgoOrders', params)
            if response:
                print(f"  ✅ Lấy open algo orders thành công (endpoint: /fapi/v1/openAlgoOrders)")
            else:
                return []
        else:
            # Thử dùng allAlgoOrders thay vì historicalOrders
            if not symbol:
                print(f"  ⚠️  Cần symbol để lấy historical orders, bỏ qua")
                return []
            response = call_binance_api_direct('GET', '/fapi/v1/allAlgoOrders', params)
            if response:
                print(f"  ✅ Lấy algo orders thành công (endpoint: /fapi/v1/allAlgoOrders)")
            else:
                return []
        
        if not response:
            return []
        
        # Binance trả về có thể là array hoặc dict
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            if 'data' in response:
                return response['data']
            elif response.get('code') == 200:
                # Có thể data nằm trực tiếp
                return response
            else:
                print(f"  ⚠️  Response có code khác 200: {response}")
                return []
        else:
            print(f"  ⚠️  Response format không đúng: {type(response)}")
            return []
            
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return []

# ============================================================================
# TEST 3: Dùng Binance UM Conditional Orders API trực tiếp
# Endpoint: /papi/v1/um/conditional/...
# ============================================================================
print(f"\n\n{'='*80}")
print("📋 TEST 3: Dùng Binance UM Conditional Orders API (/papi/v1/um/conditional/...)")
print(f"{'='*80}\n")

def get_um_conditional_orders_via_api(symbol=None, is_open=True, is_all=True):
    """
    Lấy UM conditional orders qua Binance API trực tiếp
    Unified Margin endpoints:
    - Open Orders (all): /papi/v1/um/conditional/openOrders
    - Open Order (single): /papi/v1/um/conditional/openOrder (cần symbol + strategyId)
    - All Orders: /papi/v1/um/conditional/allOrders
    - Order History: /papi/v1/um/conditional/orderHistory (cần symbol)
    """
    try:
        params = {}
        if symbol:
            params['symbol'] = symbol.replace('/', '')
        
        if is_open:
            if is_all:
                # Lấy tất cả open conditional orders
                # Endpoint: /papi/v1/um/conditional/openOrders
                response = exchange.papiPrivateGetUmConditionalOpenOrders(params)
                print(f"  ✅ Lấy all open UM conditional orders thành công")
            else:
                # Lấy single open order (cần strategyId)
                # Endpoint: /papi/v1/um/conditional/openOrder
                print(f"  ⚠️  openOrder cần strategyId, bỏ qua")
                return []
        else:
            if is_all:
                # Lấy tất cả conditional orders (có thể có startTime, endTime, limit)
                # Endpoint: /papi/v1/um/conditional/allOrders
                params['limit'] = 500  # Default 500, max 1000
                response = exchange.papiPrivateGetUmConditionalAllOrders(params)
                print(f"  ✅ Lấy all UM conditional orders thành công")
            else:
                # Lấy order history (cần symbol)
                # Endpoint: /papi/v1/um/conditional/orderHistory
                if not symbol:
                    print(f"  ⚠️  orderHistory cần symbol, bỏ qua")
                    return []
                response = exchange.papiPrivateGetUmConditionalOrderHistory(params)
                print(f"  ✅ Lấy UM conditional order history thành công")
        
        # Binance trả về có thể là array hoặc dict với 'data' key
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            if 'data' in response:
                return response['data']
            elif 'code' in response and response['code'] == 200:
                # Có thể data nằm trực tiếp trong response
                return response.get('data', [])
            else:
                print(f"  ⚠️  Response format: {list(response.keys())}")
                return []
        else:
            print(f"  ⚠️  Response type không đúng: {type(response)}")
            return []
    except AttributeError as e:
        print(f"  ❌ API method không tồn tại: {e}")
        import traceback
        traceback.print_exc()
        return []
    except Exception as e:
        print(f"  ❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return []

# Test lấy open algo orders (fapi)
print("🔍 TEST 2.1: Lấy Open Algo Orders (/fapi/v1/algo/allOpenOrders)")
open_algo = get_algo_orders_via_fapi(is_open=True)
if open_algo:
    print(f"  📊 Tìm thấy {len(open_algo)} open algo orders:")
    for order in open_algo[:5]:  # Hiển thị 5 đầu tiên
        print(f"    - Symbol: {order.get('symbol', 'N/A')}, AlgoId: {order.get('algoId', 'N/A')}, Type: {order.get('algoType', 'N/A')}, Status: {order.get('algoStatus', 'N/A')}")
else:
    print("  ⚠️  Không có open algo orders")

# Test lấy all algo orders cho từng symbol (fapi) - bao gồm cả history
print(f"\n🔍 TEST 2.2: Lấy All Algo Orders (/fapi/v1/allAlgoOrders) - bao gồm cả history")
print("   Lưu ý: Endpoint này trả về active, CANCELED, TRIGGERED hoặc FINISHED")
print("   Orders > 90 days hoặc CANCELED/EXPIRED no filled > 3 days sẽ không tìm thấy\n")
for symbol in target_symbols:
    print(f"\n  📊 {symbol}:")
    all_algo = get_algo_orders_via_fapi(symbol, is_open=False, use_all_algo_orders=True)
    if all_algo:
        cancelled = [o for o in all_algo if o.get('algoStatus', '').upper() in ['CANCELED', 'EXPIRED']]
        finished = [o for o in all_algo if o.get('algoStatus', '').upper() in ['FINISHED', 'TRIGGERED']]
        active = [o for o in all_algo if o.get('algoStatus', '').upper() == 'NEW']
        
        print(f"    - Tổng số: {len(all_algo)}")
        print(f"    - Active (NEW): {len(active)}")
        print(f"    - Cancelled/Expired: {len(cancelled)}")
        print(f"    - Finished/Triggered: {len(finished)}")
        
        if cancelled:
            print(f"\n    🔴 CANCELLED/EXPIRED ({len(cancelled)} orders):")
            for order in cancelled[:5]:  # Hiển thị 5 đầu tiên
                algo_id = order.get('algoId', 'N/A')
                algo_type = order.get('algoType', 'N/A')
                activate_price = order.get('activatePrice', 'N/A')
                callback_rate = order.get('callbackRate', order.get('priceRate', 'N/A'))
                status = order.get('algoStatus', 'N/A')
                print(f"      - AlgoId: {algo_id}, Type: {algo_type}, Status: {status}")
                print(f"        ActivatePrice: {activate_price}, CallbackRate: {callback_rate}")
                if order.get('time') or order.get('createTime'):
                    time_val = order.get('time') or order.get('createTime')
                    print(f"        Time: {datetime.fromtimestamp(time_val/1000)}")
        
        if finished:
            print(f"\n    🟢 FINISHED/TRIGGERED ({len(finished)} orders):")
            for order in finished[:5]:
                algo_id = order.get('algoId', 'N/A')
                algo_type = order.get('algoType', 'N/A')
                activate_price = order.get('activatePrice', 'N/A')
                status = order.get('algoStatus', 'N/A')
                print(f"      - AlgoId: {algo_id}, Type: {algo_type}, Status: {status}, ActivatePrice: {activate_price}")
                if order.get('time') or order.get('createTime'):
                    time_val = order.get('time') or order.get('createTime')
                    print(f"        Time: {datetime.fromtimestamp(time_val/1000)}")
    else:
        print(f"    ⚠️  Không có algo orders")
    
    time.sleep(0.3)  # Tránh rate limit

# Test lấy open UM conditional orders (papi/um)
print(f"\n🔍 TEST 3.1: Lấy All Open UM Conditional Orders (/papi/v1/um/conditional/openOrders)")
um_open = get_um_conditional_orders_via_api(is_open=True, is_all=True)
if um_open:
    print(f"  📊 Tìm thấy {len(um_open)} open UM conditional orders:")
    for order in um_open[:5]:  # Hiển thị 5 đầu tiên
        strategy_type = order.get('strategyType', order.get('type', 'N/A'))
        strategy_status = order.get('strategyStatus', order.get('status', 'N/A'))
        strategy_id = order.get('strategyId', order.get('id', 'N/A'))
        print(f"    - Symbol: {order.get('symbol', 'N/A')}, StrategyId: {strategy_id}, Type: {strategy_type}, Status: {strategy_status}")
else:
    print("  ⚠️  Không có open UM conditional orders")

# Test lấy all UM conditional orders (papi/um)
print(f"\n🔍 TEST 3.2: Lấy All UM Conditional Orders (/papi/v1/um/conditional/allOrders)")
um_all = get_um_conditional_orders_via_api(is_open=False, is_all=True)
if um_all:
    cancelled_um = [o for o in um_all if o.get('strategyStatus', '').upper() in ['CANCELED', 'EXPIRED']]
    finished_um = [o for o in um_all if o.get('strategyStatus', '').upper() in ['FINISHED', 'TRIGGERED']]
    
    print(f"  📊 Tổng số: {len(um_all)}")
    print(f"    - Cancelled/Expired: {len(cancelled_um)}")
    print(f"    - Finished/Triggered: {len(finished_um)}")
    
    if cancelled_um:
        print(f"\n    🔴 CANCELLED/EXPIRED ({len(cancelled_um)} orders):")
        for order in cancelled_um[:5]:
            print(f"      - Symbol: {order.get('symbol', 'N/A')}, StrategyId: {order.get('strategyId', 'N/A')}, Type: {order.get('strategyType', 'N/A')}")
else:
    print("  ⚠️  Không có UM conditional orders")

# Test lấy UM conditional order history cho từng symbol (papi/um)
print(f"\n🔍 TEST 3.3: Lấy UM Conditional Order History (/papi/v1/um/conditional/orderHistory)")
for symbol in target_symbols:
    print(f"\n  📊 {symbol}:")
    um_history = get_um_conditional_orders_via_api(symbol, is_open=False, is_all=False)
    if um_history:
        cancelled_hist = [o for o in um_history if o.get('strategyStatus', '').upper() in ['CANCELED', 'EXPIRED']]
        finished_hist = [o for o in um_history if o.get('strategyStatus', '').upper() in ['FINISHED', 'TRIGGERED']]
        
        print(f"    - Tổng số: {len(um_history)}")
        print(f"    - Cancelled/Expired: {len(cancelled_hist)}")
        print(f"    - Finished/Triggered: {len(finished_hist)}")
        
        if cancelled_hist:
            print(f"\n    🔴 CANCELLED/EXPIRED ({len(cancelled_hist)} orders):")
            for order in cancelled_hist[:3]:
                strategy_id = order.get('strategyId', 'N/A')
                strategy_type = order.get('strategyType', 'N/A')
                activate_price = order.get('activatePrice', 'N/A')
                price_rate = order.get('priceRate', 'N/A')
                print(f"      - StrategyId: {strategy_id}, Type: {strategy_type}, ActivatePrice: {activate_price}, PriceRate: {price_rate}")
                if order.get('bookTime') or order.get('createTime'):
                    time_val = order.get('bookTime') or order.get('createTime')
                    print(f"        Time: {datetime.fromtimestamp(time_val/1000)}")
    else:
        print(f"    ⚠️  Không có UM conditional order history")
    
    time.sleep(0.3)  # Tránh rate limit

print(f"\n{'='*80}")
print("✅ KẾT THÚC.")
print(f"📝 Log file: {log_filename}")
tee.close()
input("Nhấn Enter để thoát...")