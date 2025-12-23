import cst
import ccxt
import time
import requests
import hmac
import hashlib
import urllib.parse
import json
import sys

# Cấu hình hiển thị
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

print("--- TOOL KIỂM TRA TRẠNG THÁI LỆNH TRÊN BINANCE ---")
symbol_input = input("Nhập mã Coin (ví dụ VELODROME/USDT): ").strip().upper()
if "/" not in symbol_input:
    symbol_input = symbol_input.replace("USDT", "/USDT")

print(f"\n🔍 Đang quét dữ liệu cho: {symbol_input}...")

# 1. Kết nối Binance
exchange = ccxt.binance({
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {'defaultType': 'future'}
})

# 2. Hàm gọi API trực tiếp (để lấy Algo Orders)
def call_binance_api(endpoint, params=None):
    base_url = 'https://fapi.binance.com'
    url = f"{base_url}{endpoint}"
    if params is None: params = {}
    
    params['timestamp'] = int(time.time() * 1000)
    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(
        cst.secret_binance.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': cst.key_binance}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        return response.json()
    except Exception as e:
        print(f"Lỗi gọi API: {e}")
        return []

# --- BƯỚC 1: KIỂM TRA OPEN ORDERS (Lệnh thường) ---
print(f"\n{'='*20} 1. DANH SÁCH OPEN ORDERS (Lệnh thường) {'='*20}")
try:
    open_orders = exchange.fetch_open_orders(symbol_input)
    if len(open_orders) == 0:
        print("❌ Không có Open Order nào.")
    else:
        for i, order in enumerate(open_orders):
            print(f"\n[Open Order #{i+1}]")
            print(f"   - ID: {order['id']}")
            print(f"   - Type (CCXT): {order['type']}")
            print(f"   - Type (Raw): {order['info'].get('type')}") # Quan trọng
            print(f"   - Side: {order['side']}")
            print(f"   - ReduceOnly: {order['reduceOnly']}")
            print(f"   - Status: {order['status']}")
except Exception as e:
    print(f"Lỗi lấy Open Orders: {e}")

# --- BƯỚC 2: KIỂM TRA ALGO ORDERS (Lệnh điều kiện/Trailing) ---
print(f"\n{'='*20} 2. DANH SÁCH ALGO ORDERS (Lệnh điều kiện) {'='*20}")
try:
    algo_params = {'symbol': symbol_input.replace('/', '')}
    algo_orders_raw = call_binance_api('/fapi/v1/allAlgoOrders', algo_params)
    
    # Lọc lệnh đang Active
    active_algos = [o for o in algo_orders_raw if o.get('algoStatus') == 'NEW']
    
    if len(active_algos) == 0:
        print("❌ Không có Algo Order nào đang NEW.")
    else:
        for i, order in enumerate(active_algos):
            print(f"\n[Algo Order #{i+1}]")
            print(f"   - AlgoID: {order.get('algoId')}")
            print(f"   - AlgoType: {order.get('algoType')}") # Cực kỳ quan trọng
            print(f"   - Side: {order.get('side')}")
            print(f"   - ReduceOnly: {order.get('reduceOnly')}")
            print(f"   - Status: {order.get('algoStatus')}")
except Exception as e:
    print(f"Lỗi lấy Algo Orders: {e}")

# --- BƯỚC 3: MÔ PHỎNG LOGIC CHECK CỦA BOT ---
print(f"\n{'='*20} 3. KẾT QUẢ CHECK CỦA BOT HIỆN TẠI {'='*20}")

has_sl = False
has_tp = False

# Check trong Open Orders
for order in open_orders:
    o_type = str(order['type']).upper()
    o_raw_type = str(order['info'].get('type')).upper()
    is_reduce = order['reduceOnly']
    
    # Logic hiện tại của bot (kiểm tra xem khớp không)
    if o_type in ['STOP', 'STOP_LIMIT', 'STOP_MARKET'] and is_reduce:
        has_sl = True
        print(f"✅ Tìm thấy SL trong Open Orders (Type: {o_type})")

# Check trong Algo Orders
for order in active_algos:
    a_type = str(order.get('algoType')).upper()
    is_reduce = order.get('reduceOnly')
    
    if a_type in ['CONDITIONAL', 'VP', 'TRAILING_STOP_MARKET'] and is_reduce:
        has_tp = True
        print(f"✅ Tìm thấy TP trong Algo Orders (Type: {a_type})")
        
    if a_type in ['STOP', 'STOP_MARKET', 'STOP_LOSS', 'STOP_LOSS_MARKET', 'STOP_LIMIT'] and is_reduce:
        has_sl = True
        print(f"✅ Tìm thấy SL trong Algo Orders (Type: {a_type})")

print(f"\n---> KẾT LUẬN CUỐI CÙNG: SL={has_sl} | TP={has_tp}")
if has_sl and has_tp:
    print("🎉 OK: Bot sẽ thấy đủ lệnh -> BỎ QUA (Đúng ý muốn)")
elif has_sl or has_tp:
    print("⚠️  LỖI: Bot thấy lẻ lệnh -> HỦY RỒI TẠO LẠI (Vòng lặp vô tận)")
else:
    print("⚪ TRỐNG: Bot sẽ tạo mới")

input("\nNhấn Enter để thoát...")