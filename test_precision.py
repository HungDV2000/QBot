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
            
            # 6. Test làm tròn thực tế
            test_price = 3.9998
            
            print(f"   🧪 TEST: Làm tròn giá {test_price} bằng các phương pháp:", flush=True)
            
            # CCXT price_to_precision
            try:
                rounded_ccxt = exchange.price_to_precision(symbol, test_price)
                print(f"      - CCXT price_to_precision: {rounded_ccxt}", flush=True)
            except Exception as e:
                print(f"      - CCXT price_to_precision: ❌ Lỗi ({e})", flush=True)
            
            # Manual rounding với precision
            if precision_price is not None:
                rounded_manual = round(test_price, int(precision_price))
                print(f"      - round({test_price}, {precision_price}): {rounded_manual}", flush=True)
            
            # Manual rounding với tick_size
            if tick_size:
                from decimal import Decimal, ROUND_DOWN
                test_decimal = Decimal(str(test_price))
                tick_decimal = Decimal(str(tick_size))
                rounded_tick = float((test_decimal / tick_decimal).quantize(Decimal('1'), rounding=ROUND_DOWN) * tick_decimal)
                print(f"      - floor({test_price} / {tick_size}) * {tick_size}: {rounded_tick}", flush=True)
            
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

