"""
Script test kiểm tra CONDITIONAL (Algo) orders
Giúp verify logic tránh lặp đơn với Conditional orders
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
        self.log_file = open(file_path, 'a', encoding='utf-8')
    
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

# Thiết lập log file
log_file_path = 'test.txt'
tee = TeeOutput(log_file_path)
sys.stdout = tee

# Ghi header vào file log
print(f"\n{'='*100}")
print(f"🔍 KIỂM TRA ORDERS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*100}\n")

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'enableRateLimit': True,  
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {
        'defaultType': 'future',
        'warnOnFetchOpenOrdersWithoutSymbol': False  # Suppress warning về rate limit
    }
})
exchange.setSandboxMode(False)
print(f"✅ Đã khởi tạo exchange: {exchange_id} (defaultType: future)")

def check_all_orders():
    """Kiểm tra TẤT CẢ orders (Basic + Conditional)"""
    print(f"\n{'='*100}")
    print(f"🔍 KIỂM TRA ORDERS (BASIC + CONDITIONAL) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}\n")
    
    all_symbols = set()
    basic_orders = []
    conditional_orders = []
    
    # BƯỚC 1: Lấy TẤT CẢ ORDERS (chỉ gọi 1 lần)
    print("="*80)
    print("BƯỚC 1: LẤY TẤT CẢ OPEN ORDERS")
    print("="*80)
    try:
        print("📥 [STEP 1.1] Gọi exchange.fetch_open_orders()...")
        all_open_orders = exchange.fetch_open_orders()
        print(f"✅ [STEP 1.2] Lấy được {len(all_open_orders)} orders tổng cộng")
        print(f"📋 [STEP 1.3] Type của all_open_orders: {type(all_open_orders)}")
        print(f"📋 [STEP 1.4] Is list: {isinstance(all_open_orders, list)}")
        if all_open_orders:
            print(f"📋 [STEP 1.5] Sample first order keys: {list(all_open_orders[0].keys()) if all_open_orders else 'N/A'}")
        print()
        
        # BƯỚC 2: Phân loại Basic vs Conditional
        print("="*80)
        print("BƯỚC 2: PHÂN LOẠI ORDERS")
        print("="*80)
        print("📊 [STEP 2.1] Bắt đầu phân loại orders...")
        print(f"📊 [STEP 2.2] Số lượng orders cần xử lý: {len(all_open_orders)}")
        
        for idx, order in enumerate(all_open_orders, 1):
            try:
                info = order.get('info', {})
                
                algo_id = info.get('algoId', None)
                symbol = order.get('symbol', 'N/A')
                order_type = order.get('type', 'N/A')
                activate_price = info.get('activatePrice', None)
                callback_rate = info.get('callbackRate', None)
                price_rate = info.get('priceRate', None)
                algo_type = info.get('algoType', None)
                
                # Chỉ log chi tiết cho 5 orders đầu tiên để debug
                if idx <= 5:
                    print(f"   [ORDER {idx}/{len(all_open_orders)}] {symbol} - Type: {order_type}, algoId: {algo_id}, activatePrice: {activate_price}")
                
                # Logic phân loại: Conditional order nếu có BẤT KỲ dấu hiệu nào sau:
                # 1. Có algoId
                # 2. Type chứa 'trailing' 
                # 3. Có activatePrice (dấu hiệu của algo/conditional order)
                # 4. Có algoType
                is_conditional = (
                    algo_id is not None or
                    'trailing' in str(order_type).lower() or
                    activate_price is not None or
                    algo_type is not None
                )
                
                if is_conditional:
                    # CONDITIONAL ORDER (Algo order)
                    if idx <= 5:
                        print(f"      → ✅ CONDITIONAL ORDER")
                    side = order.get('side', 'N/A')
                    # Dùng callbackRate hoặc priceRate
                    callback_value = callback_rate if callback_rate is not None else price_rate
                    
                    conditional_orders.append({
                        'symbol': symbol,
                        'algoId': algo_id if algo_id is not None else 'N/A',
                        'algoType': algo_type if algo_type is not None else 'N/A',
                        'order_type': order_type,
                        'side': side,
                        'activation': activate_price if activate_price is not None else 'N/A',
                        'callback': callback_value if callback_value is not None else 'N/A',
                        'order_id': order.get('id', 'N/A')
                    })
                    if idx <= 5:
                        print(f"      → AlgoId: {algo_id}, Type: {order_type}, Activation: {activate_price}, Callback: {callback_value}")
                else:
                    # BASIC ORDER
                    if idx <= 5:
                        print(f"      → ✅ BASIC ORDER")
                    order_id = order.get('id', 'N/A')
                    side = order.get('side', 'N/A')
                    price = order.get('price', 'N/A')
                    
                    basic_orders.append({
                        'symbol': symbol,
                        'id': order_id,
                        'type': order_type,
                        'side': side,
                        'price': price
                    })
                
                all_symbols.add(symbol)
            except Exception as e_order:
                print(f"   ❌ [ORDER {idx}] LỖI khi xử lý: {e_order}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n✅ [STEP 2.3] Đã xử lý xong {len(all_open_orders)} orders")
        print(f"   - Basic orders: {len(basic_orders)}")
        print(f"   - Conditional (Algo) orders: {len(conditional_orders)}")
        print(f"   - Tổng số symbols: {len(all_symbols)}\n")
        
    except Exception as e:
        print(f"\n❌ [LỖI] Exception khi lấy orders:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error message: {str(e)}")
        print(f"\n📋 [TRACEBACK]:")
        import traceback
        traceback.print_exc()
        print()
    
    # IN KẾT QUẢ
    print(f"{'='*100}")
    print(f"📊 TỔNG QUAN:")
    print(f"{'='*100}")
    print(f"   - Tổng số symbols: {len(all_symbols)}")
    print(f"   - Basic orders: {len(basic_orders)}")
    print(f"   - Conditional orders: {len(conditional_orders)}")
    print(f"   - Tổng cộng: {len(basic_orders) + len(conditional_orders)} orders\n")
    
    if basic_orders:
        print(f"{'='*100}")
        print(f"✅ BASIC ORDERS (Tab Basic):")
        print(f"{'='*100}\n")
        
        for i, order in enumerate(basic_orders, 1):
            print(f"[{i}] {order['symbol']}")
            print(f"    Order ID: {order['id']}")
            print(f"    Type: {order['type']}")
            print(f"    Side: {order['side']}")
            print(f"    Price: {order['price']}")
            print()
    else:
        print("ℹ️  KHÔNG CÓ BASIC ORDERS\n")
    
    if conditional_orders:
        print(f"{'='*100}")
        print(f"✅ CONDITIONAL ORDERS (Tab Conditional):")
        print(f"{'='*100}\n")
        
        for i, order in enumerate(conditional_orders, 1):
            print(f"[{i}] {order['symbol']}")
            print(f"    Order ID: {order['order_id']}")
            print(f"    Order Type: {order['order_type']}")
            print(f"    Algo ID: {order['algoId']}")
            print(f"    Algo Type: {order['algoType']} {'← VP = TRAILING_STOP' if order['algoType'] == 'VP' else ''}")
            print(f"    Side: {order['side']}")
            print(f"    Activation: {order['activation']}")
            print(f"    Callback: {order['callback']}")
            print()
    else:
        print("ℹ️  KHÔNG CÓ CONDITIONAL ORDERS\n")
    
    # Kiểm tra duplicate symbols
    print(f"{'='*100}")
    print(f"🔍 KIỂM TRA LẶP ĐƠN:")
    print(f"{'='*100}\n")
    
    # Nhóm theo symbol
    symbol_orders = {}
    for order in basic_orders:
        sym = order['symbol']
        if sym not in symbol_orders:
            symbol_orders[sym] = {'basic': [], 'conditional': []}
        symbol_orders[sym]['basic'].append(order)
    
    for order in conditional_orders:
        sym = order['symbol']
        if sym not in symbol_orders:
            symbol_orders[sym] = {'basic': [], 'conditional': []}
        symbol_orders[sym]['conditional'].append(order)
    
    # Tìm symbols có nhiều orders
    duplicates_found = False
    for symbol, orders in symbol_orders.items():
        total = len(orders['basic']) + len(orders['conditional'])
        if total > 1:
            duplicates_found = True
            print(f"⚠️  {symbol}: Có {total} orders!")
            
            if orders['basic']:
                print(f"   - Basic orders ({len(orders['basic'])}):")
                for order in orders['basic']:
                    print(f"      • Order ID: {order['id']}, Type: {order['type']}, Price: {order['price']}")
            
            if orders['conditional']:
                print(f"   - Conditional orders ({len(orders['conditional'])}):")
                for order in orders['conditional']:
                    algo_id = order.get('algoId', 'N/A')
                    algo_type = order.get('algoType', 'N/A')
                    order_type = order.get('order_type', 'N/A')
                    activation = order.get('activation', 'N/A')
                    callback = order.get('callback', 'N/A')
                    print(f"      • Order Type: {order_type}, Algo ID: {algo_id}, AlgoType: {algo_type}, Activation: {activation}, Callback: {callback}")
            print()
    
    if not duplicates_found:
        print("✅ KHÔNG CÓ SYMBOLS BỊ LẶP ĐƠN!\n")
    
    # Kiểm tra cụ thể TRAILING_STOP lặp đơn
    print(f"{'='*100}")
    print(f"🎯 KIỂM TRA TRAILING_STOP LẶP ĐƠN:")
    print(f"{'='*100}\n")
    
    trailing_symbols = {}
    for order in conditional_orders:
        # TRAILING_STOP nếu có 'trailing' trong order_type hoặc algoType = 'VP'
        order_type = order.get('order_type', '')
        algo_type = order.get('algoType', '')
        if 'trailing' in str(order_type).lower() or algo_type == 'VP':
            sym = order['symbol']
            if sym not in trailing_symbols:
                trailing_symbols[sym] = []
            trailing_symbols[sym].append(order)
    
    trailing_duplicates = False
    for symbol, orders in trailing_symbols.items():
        if len(orders) > 1:
            trailing_duplicates = True
            print(f"❌ {symbol}: Có {len(orders)} TRAILING_STOP orders trùng lặp!")
            for i, order in enumerate(orders, 1):
                algo_id = order.get('algoId', 'N/A')
                activation = order.get('activation', 'N/A')
                callback = order.get('callback', 'N/A')
                order_type = order.get('order_type', 'N/A')
                print(f"   [{i}] Order Type: {order_type}, Algo ID: {algo_id}, Activation: {activation}, Callback: {callback}")
            print()
    
    if not trailing_duplicates:
        print("✅ KHÔNG CÓ TRAILING_STOP NÀO BỊ LẶP ĐƠN!\n")

if __name__ == "__main__":
    try:
        check_all_orders()
        
        print(f"\n{'='*100}")
        print(f"💡 HƯỚNG DẪN:")
        print(f"{'='*100}")
        print(f"1. Nếu thấy '⚠️ Có X orders!' → Symbol đó có nhiều orders")
        print(f"2. Nếu thấy '❌ Có X TRAILING_STOP orders trùng lặp!' → Cần hủy thủ công trên Binance")
        print(f"3. Nếu thấy '✅ KHÔNG CÓ LẶP ĐƠN' → Logic mới đã hoạt động tốt!")
        print(f"4. Chạy lại script này định kỳ để kiểm tra")
        print(f"\n💡 NOTE:")
        print(f"   - Conditional/Algo orders được nhận diện bằng: algoId, order_type chứa 'trailing', activatePrice, hoặc algoType")
        print(f"   - TRAILING_STOP orders có order_type = 'trailing_stop_market' hoặc algoType = 'VP'")
        print(f"   - fetch_open_orders() trả về cả Basic và Conditional orders")
        print(f"   - Nhiều TRAILING_STOP orders không có algoId nhưng vẫn là Conditional orders")
        print(f"\n📝 Kết quả đã được ghi vào file: {log_file_path}\n")
    except Exception as e:
        print(f"❌ LỖI KHI CHẠY SCRIPT: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Đóng file log và restore stdout
        sys.stdout = tee.terminal
        tee.close()
