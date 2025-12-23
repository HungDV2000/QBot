import cst
import ccxt
import time
import requests
import hmac
import hashlib
import urllib.parse
import json
import sys
import os

# Cấu hình hiển thị console
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
os.system(f"title CHECK ORDER TOOL")

print("--- TOOL KIỂM TRA CHI TIẾT LỆNH TRÊN BINANCE ---")
symbol_input = input("Nhập mã Coin (ví dụ VELODROME/USDT): ").strip().upper()
if "/" not in symbol_input:
    symbol_input = symbol_input.replace("USDT", "/USDT")

print(f"\n🔍 Đang quét dữ liệu gốc từ sàn cho: {symbol_input}...")

# 1. Kết nối Binance
exchange = ccxt.binance({
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {'defaultType': 'future'}
})

# 2. Hàm gọi API trực tiếp (để lấy dữ liệu thô)
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

# --- PHẦN 1: KIỂM TRA OPEN ORDERS (Lệnh thường) ---
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
            print(f"   - Type (Gốc): {order['info'].get('type')}") 
            print(f"   - ReduceOnly: {order['reduceOnly']}")
            print(f"   - Price: {order['price']}")
            print(f"   - StopPrice: {order['info'].get('stopPrice')}")
except Exception as e:
    print(f"Lỗi lấy Open Orders: {e}")

# --- PHẦN 2: KIỂM TRA ALGO ORDERS (Lệnh điều kiện) ---
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
            print(f"   - AlgoType: {order.get('algoType')}") 
            print(f"   - Symbol: {order.get('symbol')}")
            print(f"   - ReduceOnly: {order.get('reduceOnly')}")
            
            # --- CÁC THÔNG SỐ QUAN TRỌNG ĐỂ PHÂN BIỆT ---
            cb_rate = order.get('callbackRate')
            act_price = order.get('activatePrice')
            stop_price = order.get('stopPrice')
            
            print(f"   👉 callbackRate: {cb_rate} (Quan trọng)")
            print(f"   👉 activatePrice: {act_price}")
            print(f"   👉 stopPrice: {stop_price}")
            
except Exception as e:
    print(f"Lỗi lấy Algo Orders: {e}")

# --- PHẦN 3: GIẢ LẬP LOGIC KIỂM TRA MỚI ---
print(f"\n{'='*20} 3. TEST NHẬN DIỆN SL/TP {'='*20}")

detected_sl = False
detected_tp = False

# Check Algo
for order in active_algos:
    atype = str(order.get('algoType')).upper()
    cb_rate = float(order.get('callbackRate') or 0)
    
    # Logic nhận diện TP (Trailing Stop)
    if atype in ['CONDITIONAL', 'VP', 'TRAILING_STOP_MARKET'] and cb_rate > 0:
        detected_tp = True
        print(f"✅ PHÁT HIỆN TP (Trailing): ID={order.get('algoId')} | Rate={cb_rate}%")
        
    # Logic nhận diện SL (Stop Limit/Market)
    if atype in ['STOP', 'STOP_MARKET', 'STOP_LOSS', 'STOP_LIMIT']:
        detected_sl = True
        print(f"✅ PHÁT HIỆN SL (Type chuẩn): ID={order.get('algoId')}")
    elif atype == 'CONDITIONAL' and cb_rate == 0:
        detected_sl = True
        print(f"✅ PHÁT HIỆN SL (Type Conditional): ID={order.get('algoId')} | Rate=0%")

# Check Open Orders (Dự phòng)
if not detected_sl:
    for order in open_orders:
        otype = str(order['type']).upper()
        if otype in ['STOP', 'STOP_LIMIT', 'STOP_MARKET']:
             detected_sl = True
             print(f"✅ PHÁT HIỆN SL (Trong OpenOrder): ID={order['id']}")

print(f"\n---> KẾT QUẢ: SL={detected_sl} | TP={detected_tp}")

if detected_sl and detected_tp:
    print("🎉 KẾT LUẬN: ĐỦ CẶP LỆNH. (Code mới sẽ chạy NGON)")
else:
    print("⚠️ KẾT LUẬN: VẪN THIẾU/LẺ LỆNH.")

input("\nNhấn Enter để thoát...")