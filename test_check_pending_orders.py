"""
Script test kiểm tra xem symbols nào đã có order TRAILING_STOP pending
Giúp verify logic tránh lặp đơn
"""
import cst
import ccxt
from datetime import datetime

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

def check_pending_orders():
    """Kiểm tra tất cả symbols có order TRAILING_STOP"""
    print(f"\n{'='*100}")
    print(f"🔍 KIỂM TRA LỆNH CHỜ TRAILING_STOP - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*100}\n")
    
    try:
        # Fetch tất cả open orders
        all_orders = exchange.fetch_open_orders()
        
        trailing_stop_orders = []
        other_orders = []
        
        for order in all_orders:
            symbol = order.get('symbol', 'N/A')
            order_id = order.get('id', 'N/A')
            order_type = order.get('type', '')
            order_type_info = order.get('info', {}).get('orderType', '')
            algo_type = order.get('info', {}).get('algoType', '')
            order_type_raw = order.get('info', {}).get('type', '')
            
            # Kiểm tra TRAILING_STOP
            is_trailing = (
                'TRAILING' in str(order_type).upper() or
                'TRAILING' in str(order_type_info).upper() or
                'TRAILING' in str(algo_type).upper() or
                'TRAILING' in str(order_type_raw).upper()
            )
            
            if is_trailing:
                activation_price = order.get('info', {}).get('activatePrice', 'N/A')
                callback_rate = order.get('info', {}).get('callbackRate', 'N/A')
                side = order.get('side', 'N/A')
                
                trailing_stop_orders.append({
                    'symbol': symbol,
                    'id': order_id,
                    'side': side,
                    'activation': activation_price,
                    'callback': callback_rate
                })
            else:
                other_orders.append({
                    'symbol': symbol,
                    'id': order_id,
                    'type': order_type or order_type_info
                })
        
        # In kết quả
        print(f"📊 TỔNG QUAN:")
        print(f"   - Tổng số lệnh chờ: {len(all_orders)}")
        print(f"   - Lệnh TRAILING_STOP: {len(trailing_stop_orders)}")
        print(f"   - Lệnh khác: {len(other_orders)}\n")
        
        if trailing_stop_orders:
            print(f"{'='*100}")
            print(f"✅ CÁC LỆNH TRAILING_STOP ĐANG CHỜ:")
            print(f"{'='*100}\n")
            
            for i, order in enumerate(trailing_stop_orders, 1):
                print(f"[{i}] {order['symbol']}")
                print(f"    Order ID: {order['id']}")
                print(f"    Side: {order['side']}")
                print(f"    Activation Price: {order['activation']}")
                print(f"    Callback Rate: {order['callback']}")
                print()
        else:
            print("⚠️  KHÔNG CÓ LỆNH TRAILING_STOP NÀO ĐANG CHỜ\n")
        
        if other_orders:
            print(f"{'='*100}")
            print(f"📋 CÁC LỆNH KHÁC:")
            print(f"{'='*100}\n")
            
            for i, order in enumerate(other_orders, 1):
                print(f"[{i}] {order['symbol']} - Type: {order['type']} - ID: {order['id']}")
        
        # Kiểm tra duplicate symbols
        symbols = [o['symbol'] for o in trailing_stop_orders]
        duplicates = set([s for s in symbols if symbols.count(s) > 1])
        
        if duplicates:
            print(f"\n{'='*100}")
            print(f"⚠️  CẢNH BÁO: CÓ SYMBOLS BỊ LẶP ĐƠN!")
            print(f"{'='*100}\n")
            
            for symbol in duplicates:
                count = symbols.count(symbol)
                print(f"❌ {symbol}: Có {count} lệnh TRAILING_STOP trùng lặp!")
                
                # In chi tiết các lệnh trùng
                for order in trailing_stop_orders:
                    if order['symbol'] == symbol:
                        print(f"   - Order ID: {order['id']}, Activation: {order['activation']}, Callback: {order['callback']}")
                print()
        else:
            print(f"\n✅ KHÔNG CÓ SYMBOLS BỊ LẶP ĐƠN!\n")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_pending_orders()
    
    print(f"\n{'='*100}")
    print(f"💡 HƯỚNG DẪN:")
    print(f"{'='*100}")
    print(f"1. Nếu thấy '⚠️ CÓ SYMBOLS BỊ LẶP ĐƠN' → Có vấn đề, cần hủy thủ công trên Binance")
    print(f"2. Nếu thấy '✅ KHÔNG CÓ SYMBOLS BỊ LẶP ĐƠN' → Logic tránh lặp đơn đang hoạt động tốt!")
    print(f"3. Chạy lại script này định kỳ để kiểm tra\n")
