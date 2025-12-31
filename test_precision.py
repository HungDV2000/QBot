"""
Test lấy Price Precision từ Binance cho các symbol
"""
import ccxt
import cst
import sys
from datetime import datetime

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

def test_precision():
    print("="*60, flush=True)
    print("🔍 TEST PRICE PRECISION - BINANCE FUTURES", flush=True)
    print("="*60, flush=True)
    print(f"⏰ Thời gian: {datetime.now()}", flush=True)
    print("", flush=True)
    
    # Khởi tạo exchange
    print("⏳ Đang kết nối Binance Futures...", flush=True)
    exchange = ccxt.binance({
        'apiKey': cst.key_binance,
        'secret': cst.secret_binance,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    exchange.setSandboxMode(False)
    
    # Load markets
    print("⏳ Đang tải thông tin thị trường...", flush=True)
    exchange.load_markets(True)
    print("✅ Đã tải xong thông tin thị trường", flush=True)
    print("", flush=True)
    
    # Lấy danh sách positions hiện có
    print("📊 Đang lấy danh sách positions...", flush=True)
    positions = exchange.fetch_positions()
    active_symbols = []
    
    for pos in positions:
        try:
            contracts = float(pos.get('contracts', 0))
            if contracts != 0:
                symbol = pos['symbol']
                active_symbols.append(symbol)
        except:
            pass
    
    print(f"✅ Tìm thấy {len(active_symbols)} position đang mở", flush=True)
    print("", flush=True)
    
    # Test các symbol đang có position
    test_symbols = active_symbols if active_symbols else ['ILV/USDT:USDT', 'BTC/USDT:USDT', 'ETH/USDT:USDT']
    
    # Thêm một số symbol phổ biến để test
    common_symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'BNB/USDT:USDT', 'ILV/USDT:USDT']
    for sym in common_symbols:
        if sym not in test_symbols:
            test_symbols.append(sym)
    
    print("="*60, flush=True)
    print("📋 KẾT QUẢ TEST PRECISION:", flush=True)
    print("="*60, flush=True)
    print("", flush=True)
    
    for symbol in test_symbols:
        print(f"🔹 Symbol: {symbol}", flush=True)
        print("-" * 60, flush=True)
        
        try:
            if symbol not in exchange.markets:
                print(f"   ❌ Không tìm thấy trong markets", flush=True)
                print("", flush=True)
                continue
            
            market = exchange.markets[symbol]
            
            # 1. Lấy precision từ CCXT
            precision_price = market.get('precision', {}).get('price')
            precision_amount = market.get('precision', {}).get('amount')
            
            print(f"   📌 CCXT Precision:", flush=True)
            print(f"      - Price Precision: {precision_price}", flush=True)
            print(f"      - Amount Precision: {precision_amount}", flush=True)
            
            # 2. Lấy limits
            limits = market.get('limits', {})
            price_limits = limits.get('price', {})
            amount_limits = limits.get('amount', {})
            
            tick_size = price_limits.get('min')
            min_amount = amount_limits.get('min')
            
            print(f"   📌 Limits:", flush=True)
            print(f"      - Tick Size (Price Step): {tick_size}", flush=True)
            print(f"      - Min Amount: {min_amount}", flush=True)
            
            # 3. Tính precision từ tick_size (cách cũ - bị lỗi)
            if tick_size:
                import math
                try:
                    precision_from_log = abs(int(math.floor(math.log10(tick_size))))
                    print(f"   📌 Precision từ log10(tick_size): {precision_from_log}", flush=True)
                except:
                    print(f"   ⚠️ Không tính được precision từ log10", flush=True)
                
                # 4. Tính precision từ string (cách mới)
                tick_str = f"{tick_size:.10f}".rstrip('0').rstrip('.')
                if '.' in tick_str:
                    precision_from_str = len(tick_str.split('.')[1])
                else:
                    precision_from_str = 0
                
                print(f"   📌 Precision từ string: {precision_from_str} (Tick String: '{tick_str}')", flush=True)
            
            # 5. Lấy thông tin từ info (raw data từ Binance)
            info = market.get('info', {})
            if info:
                print(f"   📌 Raw Info từ Binance:", flush=True)
                
                # Binance Futures có thể có các field này
                price_precision_raw = info.get('pricePrecision')
                quantity_precision_raw = info.get('quantityPrecision')
                
                if price_precision_raw is not None:
                    print(f"      - pricePrecision: {price_precision_raw}", flush=True)
                if quantity_precision_raw is not None:
                    print(f"      - quantityPrecision: {quantity_precision_raw}", flush=True)
                
                # Filters
                filters = info.get('filters', [])
                for f in filters:
                    if f.get('filterType') == 'PRICE_FILTER':
                        print(f"      - PRICE_FILTER tickSize: {f.get('tickSize')}", flush=True)
                    elif f.get('filterType') == 'LOT_SIZE':
                        print(f"      - LOT_SIZE stepSize: {f.get('stepSize')}", flush=True)
            
            # 6. PHÂN TÍCH SỰ KHÁC BIỆT
            print(f"   🔍 PHÂN TÍCH:", flush=True)
            print(f"      ┌─ CCXT Precision: {precision_price} → Cho phép đến {precision_price} chữ số", flush=True)
            print(f"      └─ Limits Tick Size: {tick_size} → Bước giá thực tế", flush=True)
            
            # Tính precision từ tick_size
            if tick_size:
                tick_str = f"{tick_size:.10f}".rstrip('0').rstrip('.')
                if '.' in tick_str:
                    real_precision = len(tick_str.split('.')[1])
                else:
                    real_precision = 0
                print(f"      └─ Precision từ Tick Size: {real_precision} ('{tick_str}')", flush=True)
            
            print("", flush=True)
            
            # 7. TEST CỤ THỂ: Thử nhiều giá khác nhau
            test_prices = [3.999, 3.9998, 5.714, 5.7145, 5.715, 9.142, 9.1424, 9.1426]
            
            print(f"   🧪 TEST CỤ THỂ: Làm tròn nhiều giá khác nhau", flush=True)
            print(f"   {'Giá gốc':<12} | {'CCXT':<12} | {'Tick Size':<12} | {'Hợp lệ?':<10}", flush=True)
            print(f"   {'-'*12}─┼─{'-'*12}─┼─{'-'*12}─┼─{'-'*10}", flush=True)
            
            from decimal import Decimal, ROUND_DOWN
            
            for test_price in test_prices:
                # CCXT price_to_precision
                try:
                    rounded_ccxt = exchange.price_to_precision(symbol, test_price)
                except:
                    rounded_ccxt = "ERROR"
                
                # Làm tròn với tick_size
                if tick_size:
                    test_decimal = Decimal(str(test_price))
                    tick_decimal = Decimal(str(tick_size))
                    rounded_tick = float((test_decimal / tick_decimal).quantize(Decimal('1'), rounding=ROUND_DOWN) * tick_decimal)
                else:
                    rounded_tick = "N/A"
                
                # Kiểm tra giá có chia hết cho tick_size không
                is_valid = "✅" if tick_size and (test_price % tick_size < 0.0000001) else "❌"
                
                print(f"   {test_price:<12.6f} | {str(rounded_ccxt):<12} | {rounded_tick:<12} | {is_valid:<10}", flush=True)
            
            print("", flush=True)
            
            # 8. GIẢI THÍCH KẾT QUẢ
            print(f"   📝 GIẢI THÍCH:", flush=True)
            if tick_size == 0.01:
                print(f"      ✅ Tick Size = 0.01 → Giá CHỈ có thể: 5.71, 5.72, 5.73...", flush=True)
                print(f"      ❌ Không thể: 5.715, 5.716... (vi phạm bước giá)", flush=True)
            elif tick_size == 0.001:
                print(f"      ✅ Tick Size = 0.001 → Giá có thể: 5.714, 5.715, 5.716...", flush=True)
            
            if precision_price and tick_size:
                if precision_price != tick_size:
                    print(f"      ⚠️ CCXT Precision ({precision_price}) ≠ Tick Size ({tick_size})", flush=True)
                    print(f"      → Nên dùng Limits Tick Size ({tick_size}) để chính xác!", flush=True)
            
            print("", flush=True)
            
        except Exception as e:
            print(f"   ❌ Lỗi: {e}", flush=True)
            import traceback
            traceback.print_exc()
            print("", flush=True)
    
    print("="*60, flush=True)
    print("✅ HOÀN TẤT TEST", flush=True)
    print("="*60, flush=True)

if __name__ == '__main__':
    try:
        test_precision()
    except Exception as e:
        print(f"\n❌ LỖI TỔNG: {e}", flush=True)
        import traceback
        traceback.print_exc()
    
    input("\nẤn Enter để đóng...")

