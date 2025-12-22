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
        'defaultType': 'future' 
    }
})
exchange.setSandboxMode(False)

def check_all_orders():
    """Kiểm tra TẤT CẢ orders (Basic + Conditional)"""
    print(f"\n{'='*100}")
    print(f"🔍 KIỂM TRA ORDERS (BASIC + CONDITIONAL) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}\n")
    
    all_symbols = set()
    basic_orders = []
    conditional_orders = []
    
    # BƯỚC 1: Lấy TẤT CẢ ORDERS (chỉ gọi 1 lần)
    try:
        print("📥 Đang lấy tất cả Open Orders...")
        all_open_orders = exchange.fetch_open_orders()
        print(f"✅ Lấy được {len(all_open_orders)} orders tổng cộng\n")
        
        # BƯỚC 2: Phân loại Basic vs Conditional
        print("📊 Đang phân loại orders...")
        
        for order in all_open_orders:
            info = order.get('info', {})
            algo_id = info.get('algoId', None)
            symbol = order.get('symbol', 'N/A')
            
            if algo_id is None:
                # BASIC ORDER (không có algoId)
                order_id = order.get('id', 'N/A')
                order_type = order.get('type', 'N/A')
                side = order.get('side', 'N/A')
                price = order.get('price', 'N/A')
                
                basic_orders.append({
                    'symbol': symbol,
                    'id': order_id,
                    'type': order_type,
                    'side': side,
                    'price': price
                })
            else:
                # CONDITIONAL ORDER (có algoId)
                algo_type = info.get('algoType', 'N/A')  # VP = TRAILING_STOP
                side = order.get('side', 'N/A')
                activation_price = info.get('activatePrice', 'N/A')
                callback_rate = info.get('callbackRate', 'N/A')
                
                conditional_orders.append({
                    'symbol': symbol,
                    'algoId': algo_id,
                    'algoType': algo_type,
                    'side': side,
                    'activation': activation_price,
                    'callback': callback_rate,
                    'order_id': order.get('id', 'N/A')
                })
            
            all_symbols.add(symbol)
        
        print(f"   - Basic orders: {len(basic_orders)}")
        print(f"   - Conditional (Algo) orders: {len(conditional_orders)}\n")
    except Exception as e:
        print(f"❌ Lỗi khi lấy orders: {e}\n")
        import traceback
        traceback.print_exc()
    
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
            print(f"    Algo ID: {order['algoId']}")
            print(f"    Type: {order['algoType']} {'← TRAILING_STOP' if order['algoType'] == 'VP' else ''}")
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
                    print(f"      • Algo ID: {order['algoId']}, Type: {order['algoType']}, Activation: {order['activation']}, Callback: {order['callback']}")
            print()
    
    if not duplicates_found:
        print("✅ KHÔNG CÓ SYMBOLS BỊ LẶP ĐƠN!\n")
    
    # Kiểm tra cụ thể TRAILING_STOP lặp đơn
    print(f"{'='*100}")
    print(f"🎯 KIỂM TRA TRAILING_STOP LẶP ĐƠN:")
    print(f"{'='*100}\n")
    
    trailing_symbols = {}
    for order in conditional_orders:
        if order['algoType'] == 'VP':  # VP = TRAILING_STOP
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
                print(f"   [{i}] Algo ID: {order['algoId']}, Activation: {order['activation']}, Callback: {order['callback']}")
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
        print(f"   - TRAILING_STOP orders có algoType = 'VP' (Volume Participation)")
        print(f"   - Chúng nằm trong tab 'Conditional' trên Binance UI")
        print(f"   - fetch_open_orders() với defaultType='future' TRẢ VỀ CẢ algo orders!")
        print(f"   - Phân biệt bằng cách check order['info']['algoId'] != None")
        print(f"\n📝 Kết quả đã được ghi vào file: {log_file_path}\n")
    except Exception as e:
        print(f"❌ LỖI KHI CHẠY SCRIPT: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Đóng file log và restore stdout
        sys.stdout = tee.terminal
        tee.close()
