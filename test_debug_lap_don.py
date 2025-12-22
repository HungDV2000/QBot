"""
Script test debug để tìm hiểu tại sao vẫn bị lặp đơn
Chỉ chạy 1 lần, log chi tiết tất cả orders
"""
import cst
import ccxt
import gg_sheet_factory
from datetime import datetime
import json

# Setup
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
print(f"🔍 DEBUG LẶP ĐƠN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*100}\n")

# Đọc trạng thái và symbols từ sheet
try:
    state_value = gg_sheet_factory.get_dat_lenh("B2:B2")[0][0].strip().upper()
    print(f"📌 Trạng thái: {state_value}\n")
    
    if state_value == "LONG":
        start_row = 55
        end_row = 104
    elif state_value == "SHORT":
        start_row = 4
        end_row = 53
    else:
        print("⚠️ Trạng thái không phải LONG/SHORT, dừng test")
        exit()
    
    # Đọc dữ liệu từ sheet
    don_bay = gg_sheet_factory.get_dat_lenh(f"A{start_row}:D{end_row}")
    
    # Lọc symbols hợp lệ (có leverage khác N và 0)
    valid_symbols = []
    for d in don_bay:
        if len(d) > 1 and d[1] and str(d[1]).strip() not in ["N", "0", ""]:
            try:
                lev = float(str(d[1]).strip())
                if lev > 0:
                    symbol = str(d[0]).strip()
                    leverage = lev
                    callback = d[2] if len(d) > 2 else "N/A"
                    activation = d[3] if len(d) > 3 else "N/A"
                    valid_symbols.append({
                        'symbol': symbol,
                        'leverage': leverage,
                        'callback': callback,
                        'activation': activation
                    })
            except:
                pass
    
    print(f"📋 Tìm thấy {len(valid_symbols)} symbols hợp lệ từ sheet:")
    for i, sym in enumerate(valid_symbols[:10], 1):  # Chỉ show 10 đầu tiên
        print(f"   [{i}] {sym['symbol']} - Leverage: {sym['leverage']}x, Callback: {sym['callback']}, Activation: {sym['activation']}")
    if len(valid_symbols) > 10:
        print(f"   ... và {len(valid_symbols) - 10} symbols khác")
    print()

except Exception as e:
    print(f"❌ Lỗi đọc sheet: {e}")
    exit()

# Lấy tất cả open orders
print(f"{'='*100}")
print(f"📥 ĐANG LẤY TẤT CẢ OPEN ORDERS...")
print(f"{'='*100}\n")

try:
    all_open_orders = exchange.fetch_open_orders()
    print(f"✅ Lấy được {len(all_open_orders)} orders\n")
    
    if not all_open_orders:
        print("ℹ️  Không có orders nào đang pending\n")
    else:
        # Phân loại orders
        trailing_stop_orders = []
        other_orders = []
        
        for order in all_open_orders:
            info = order.get('info', {})
            order_id = order.get('id', 'N/A')
            symbol = order.get('symbol', 'N/A')
            algo_id = info.get('algoId', None)
            
            # Check nhiều trường để detect TRAILING_STOP
            order_type = order.get('type', '')
            order_type_info = info.get('orderType', '')
            algo_type = info.get('algoType', '')
            order_type_raw = info.get('type', '')
            
            # Kiểm tra tất cả các trường có chứa "TRAILING"
            is_trailing = (
                'TRAILING' in str(order_type).upper() or
                'TRAILING' in str(order_type_info).upper() or
                'TRAILING' in str(algo_type).upper() or
                'TRAILING' in str(order_type_raw).upper()
            )
            
            # Hoặc kiểm tra nếu có algoId (đây là algo order)
            # VP = Volume Participation (Binance's TRAILING_STOP)
            is_algo_trailing = (algo_id is not None and algo_type == 'VP')
            
            order_detail = {
                'symbol': symbol,
                'order_id': order_id,
                'algo_id': algo_id,
                'type': order_type,
                'order_type_info': order_type_info,
                'algo_type': algo_type,
                'order_type_raw': order_type_raw,
                'activation_price': info.get('activatePrice', 'N/A'),
                'callback_rate': info.get('callbackRate', 'N/A'),
                'side': order.get('side', 'N/A'),
                'status': order.get('status', 'N/A'),
                'is_trailing': is_trailing,
                'is_algo_trailing': is_algo_trailing
            }
            
            if is_trailing or is_algo_trailing:
                trailing_stop_orders.append(order_detail)
            else:
                other_orders.append(order_detail)
        
        # In kết quả TRAILING_STOP orders
        print(f"{'='*100}")
        print(f"🎯 TRAILING_STOP ORDERS ({len(trailing_stop_orders)} orders):")
        print(f"{'='*100}\n")
        
        if trailing_stop_orders:
            for i, order in enumerate(trailing_stop_orders, 1):
                print(f"[{i}] {order['symbol']}")
                print(f"    Order ID: {order['order_id']}")
                print(f"    Algo ID: {order['algo_id']}")
                print(f"    Type: {order['type']}")
                print(f"    Order Type Info: {order['order_type_info']}")
                print(f"    Algo Type: {order['algo_type']}")
                print(f"    Order Type Raw: {order['order_type_raw']}")
                print(f"    Activation Price: {order['activation_price']}")
                print(f"    Callback Rate: {order['callback_rate']}")
                print(f"    Side: {order['side']}")
                print(f"    Status: {order['status']}")
                print(f"    ✅ Is Trailing (keyword check): {order['is_trailing']}")
                print(f"    ✅ Is Algo Trailing (VP check): {order['is_algo_trailing']}")
                print()
        else:
            print("ℹ️  Không có TRAILING_STOP orders\n")
        
        # In kết quả Other orders
        if other_orders:
            print(f"{'='*100}")
            print(f"📋 OTHER ORDERS ({len(other_orders)} orders):")
            print(f"{'='*100}\n")
            
            for i, order in enumerate(other_orders, 1):
                print(f"[{i}] {order['symbol']} - Type: {order['type']} - Order ID: {order['order_id']}")
            print()
        
        # Kiểm tra xem có symbols nào bị lặp đơn không
        print(f"{'='*100}")
        print(f"🔍 KIỂM TRA LẶP ĐƠN:")
        print(f"{'='*100}\n")
        
        # Nhóm TRAILING_STOP orders theo symbol
        symbol_orders = {}
        for order in trailing_stop_orders:
            sym = order['symbol']
            if sym not in symbol_orders:
                symbol_orders[sym] = []
            symbol_orders[sym].append(order)
        
        duplicates_found = False
        for symbol, orders in symbol_orders.items():
            if len(orders) > 1:
                duplicates_found = True
                print(f"❌ {symbol}: Có {len(orders)} TRAILING_STOP orders trùng lặp!")
                for j, order in enumerate(orders, 1):
                    print(f"   [{j}] Order ID: {order['order_id']}, Algo ID: {order['algo_id']}, Activation: {order['activation_price']}, Callback: {order['callback_rate']}")
                print()
        
        if not duplicates_found:
            print("✅ KHÔNG CÓ SYMBOLS NÀO BỊ LẶP ĐƠN!\n")
        
        # TEST: Kiểm tra từng symbol trong sheet xem bot có detect được order pending không?
        print(f"{'='*100}")
        print(f"🧪 TEST LOGIC has_pending_trailing_stop_order():")
        print(f"{'='*100}\n")
        
        print(f"Kiểm tra từng symbol trong sheet xem bot có detect được order pending không?\n")
        
        # Tạo map symbol -> orders để tra cứu nhanh
        symbol_order_map = {}
        for order in all_open_orders:
            sym = order.get('symbol', '')
            if sym not in symbol_order_map:
                symbol_order_map[sym] = []
            symbol_order_map[sym].append(order)
        
        test_results = []
        for sym_data in valid_symbols[:20]:  # Test 20 symbols đầu tiên
            symbol = sym_data['symbol']
            
            # Simulate logic của has_pending_trailing_stop_order()
            has_pending = False
            detected_order = None
            
            if symbol in symbol_order_map:
                for order in symbol_order_map[symbol]:
                    info = order.get('info', {})
                    algo_id = info.get('algoId', None)
                    
                    order_type = order.get('type', '')
                    order_type_info = info.get('orderType', '')
                    algo_type = info.get('algoType', '')
                    order_type_raw = info.get('type', '')
                    
                    is_trailing = (
                        'TRAILING' in str(order_type).upper() or
                        'TRAILING' in str(order_type_info).upper() or
                        'TRAILING' in str(algo_type).upper() or
                        'TRAILING' in str(order_type_raw).upper()
                    )
                    
                    is_algo_trailing = (algo_id is not None and algo_type == 'VP')
                    
                    if is_trailing or is_algo_trailing:
                        has_pending = True
                        detected_order = {
                            'order_id': order.get('id', 'N/A'),
                            'algo_id': algo_id,
                            'activation': info.get('activatePrice', 'N/A'),
                            'callback': info.get('callbackRate', 'N/A')
                        }
                        break
            
            test_results.append({
                'symbol': symbol,
                'has_pending': has_pending,
                'detected_order': detected_order
            })
        
        # In kết quả test
        pending_count = 0
        no_pending_count = 0
        
        for result in test_results:
            if result['has_pending']:
                pending_count += 1
                print(f"✅ {result['symbol']:15} | Có pending → BOT SẼ BỎ QUA ✓")
                print(f"   Order ID: {result['detected_order']['order_id']}, Algo ID: {result['detected_order']['algo_id']}, Activation: {result['detected_order']['activation']}, Callback: {result['detected_order']['callback']}")
            else:
                no_pending_count += 1
                print(f"⚠️  {result['symbol']:15} | Không có pending → BOT SẼ ĐẶT LỆNH ❌")
        
        print(f"\n📊 KẾT QUẢ TEST:")
        print(f"   - Có pending (sẽ bỏ qua): {pending_count}")
        print(f"   - Không có pending (sẽ đặt lệnh): {no_pending_count}\n")
        
        # Lưu full data vào file JSON để phân tích
        output_file = f"debug_orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'state': state_value,
                'total_orders': len(all_open_orders),
                'trailing_stop_orders': trailing_stop_orders,
                'other_orders': other_orders,
                'test_results': test_results,
                'valid_symbols_from_sheet': valid_symbols
            }, f, indent=2, ensure_ascii=False)
        
        print(f"{'='*100}")
        print(f"💾 ĐÃ LƯU FULL DATA VÀO FILE: {output_file}")
        print(f"{'='*100}\n")

except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()

print(f"{'='*100}")
print(f"🎯 KẾT LUẬN:")
print(f"{'='*100}\n")

print("""
Nếu thấy:
  - "✅ KHÔNG CÓ SYMBOLS NÀO BỊ LẶP ĐƠN" → Hiện tại không lặp
  - "❌ Có X orders trùng lặp" → ĐANG BỊ LẶP ĐƠN!

Nếu test cho thấy:
  - "Có pending → BOT SẼ BỎ QUA ✓" → Logic ĐÚNG, bot sẽ không đặt lại
  - "Không có pending → BOT SẼ ĐẶT LỆNH" → Bot SẼ ĐẶT LỆNH cho symbol này

Nếu bot VẪN đặt lệnh cho symbols đã có pending:
  → fetch_open_orders() KHÔNG TRẢ VỀ đủ nhanh
  → Cần tăng delay giữa các lần chạy
  → Hoặc Binance API đang delay sync

Kiểm tra file JSON để xem chi tiết full data!
""")

print(f"\n✅ HOÀN TẤT TEST!\n")
