"""
Test đơn giản: Kiểm tra fetch_open_orders() có trả về algo orders không?
"""
import cst
import ccxt
from datetime import datetime
import json

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'enableRateLimit': True,  
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {
        'defaultType': 'future' 
    }
})
exchange.setSandboxMode(False)

print(f"\n{'='*100}")
print(f"🧪 TEST: fetch_open_orders() CÓ TRẢ VỀ ALGO ORDERS KHÔNG?")
print(f"{'='*100}\n")

# Test 1: Lấy TẤT CẢ open orders
print("📥 Test 1: Lấy TẤT CẢ open orders (không chỉ định symbol)...\n")

all_orders = []  # Khởi tạo để tránh NameError
try:
    all_orders = exchange.fetch_open_orders()
    print(f"✅ Lấy được {len(all_orders)} orders\n")
    
    if all_orders:
        print(f"{'='*100}")
        print(f"📊 PHÂN TÍCH ORDERS:")
        print(f"{'='*100}\n")
        
        for i, order in enumerate(all_orders[:10], 1):  # Chỉ show 10 đầu tiên
            info = order.get('info', {})
            
            print(f"[{i}] {order.get('symbol', 'N/A')}")
            print(f"    Order ID: {order.get('id', 'N/A')}")
            print(f"    Type (CCXT): {order.get('type', 'N/A')}")
            print(f"    Side: {order.get('side', 'N/A')}")
            print(f"    Status: {order.get('status', 'N/A')}")
            
            # Check nếu có algoId
            if 'algoId' in info:
                print(f"    🎯 ALGO ORDER DETECTED!")
                print(f"       - Algo ID: {info.get('algoId', 'N/A')}")
                print(f"       - Algo Type: {info.get('algoType', 'N/A')}")
                print(f"       - Order Type (info): {info.get('orderType', 'N/A')}")
                print(f"       - Activation Price: {info.get('activatePrice', 'N/A')}")
                print(f"       - Callback Rate: {info.get('callbackRate', 'N/A')}")
            
            print()
        
        if len(all_orders) > 10:
            print(f"... và {len(all_orders) - 10} orders khác\n")
        
        # Đếm số algo orders
        algo_count = 0
        basic_count = 0
        
        for order in all_orders:
            if 'algoId' in order.get('info', {}):
                algo_count += 1
            else:
                basic_count += 1
        
        print(f"{'='*100}")
        print(f"📊 TỔNG KẾT:")
        print(f"{'='*100}")
        print(f"   - Tổng số orders: {len(all_orders)}")
        print(f"   - Algo orders (Conditional): {algo_count}")
        print(f"   - Basic orders: {basic_count}\n")
        
        if algo_count > 0:
            print("✅ fetch_open_orders() TRẢ VỀ ĐƯỢC ALGO ORDERS!")
            print("   → Logic kiểm tra nên hoạt động đúng\n")
        else:
            print("⚠️  fetch_open_orders() KHÔNG TRẢ VỀ ALGO ORDERS!")
            print("   → Đây là nguyên nhân gây lặp đơn\n")
    else:
        print("ℹ️  Không có orders nào\n")

except Exception as e:
    print(f"❌ Lỗi: {e}\n")
    import traceback
    traceback.print_exc()

# Test 2: Test với 1 symbol cụ thể (nếu có)
print(f"\n{'='*100}")
print(f"📥 Test 2: Lấy orders của 1 symbol cụ thể...")
print(f"{'='*100}\n")

# Lấy symbol đầu tiên từ all_orders
if all_orders:
    test_symbol = all_orders[0].get('symbol', None)
    if test_symbol:
        print(f"Symbol test: {test_symbol}\n")
        
        try:
            symbol_orders = exchange.fetch_open_orders(symbol=test_symbol)
            print(f"✅ Lấy được {len(symbol_orders)} orders cho {test_symbol}\n")
            
            for order in symbol_orders:
                info = order.get('info', {})
                print(f"Order ID: {order.get('id', 'N/A')}")
                
                if 'algoId' in info:
                    print(f"  → ALGO ORDER!")
                    print(f"     Algo ID: {info.get('algoId')}")
                    print(f"     Algo Type: {info.get('algoType')}")
                else:
                    print(f"  → BASIC ORDER")
                print()
        
        except Exception as e:
            print(f"❌ Lỗi: {e}\n")

print(f"{'='*100}")
print(f"💡 KẾT LUẬN:")
print(f"{'='*100}\n")

print("""
1. Nếu fetch_open_orders() TRẢ VỀ được algo orders (có algoId):
   → Logic kiểm tra PHẢI hoạt động
   → Nếu vẫn lặp đơn → Có vấn đề với timing (API delay)

2. Nếu fetch_open_orders() KHÔNG TRẢ VỀ algo orders:
   → Cần dùng API khác để lấy algo orders
   → Hoặc đợi lâu hơn để API sync

3. Nếu có lặp đơn:
   → Kiểm tra delay giữa các lần chạy (cst.delay_vao_lenh)
   → Có thể cần tăng delay lên 2-3 phút để API sync

Chạy lại script này SAU KHI chạy hd_order.py để xem orders có được
fetch ngay không!
""")

print(f"\n✅ HOÀN TẤT TEST!\n")
