"""
Test lấy Price Precision từ Binance cho các symbol
"""
import ccxt
import cst
import sys
import json
from datetime import datetime
from pathlib import Path

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

# Tạo thư mục logs nếu chưa có
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Tạo file log với timestamp
log_timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
log_filename = logs_dir / f'test_precision_{log_timestamp}.txt'

def log(message):
    """Ghi log vào cả console và file"""
    print(message, flush=True)
    with open(log_filename, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

def test_precision():
    log("="*60)
    log("🔍 TEST PRICE PRECISION - BINANCE FUTURES")
    log("="*60)
    log(f"⏰ Thời gian: {datetime.now()}")
    log(f"📁 Log file: {log_filename}")
    log("")
    
    # Khởi tạo exchange
    log("⏳ Đang kết nối Binance Futures...")
    exchange = ccxt.binance({
        'apiKey': cst.key_binance,
        'secret': cst.secret_binance,
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    exchange.setSandboxMode(False)
    
    # Load markets
    log("⏳ Đang tải thông tin thị trường...")
    exchange.load_markets(True)
    log("✅ Đã tải xong thông tin thị trường")
    log("")
    
    # Lấy danh sách positions hiện có
    log("📊 Đang lấy danh sách positions...")
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
    
    log(f"✅ Tìm thấy {len(active_symbols)} position đang mở")
    log("")
    
    # Test các symbol đang có position
    test_symbols = active_symbols if active_symbols else ['ILV/USDT:USDT', 'BTC/USDT:USDT', 'ETH/USDT:USDT']
    
    # Thêm một số symbol phổ biến để test
    common_symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'BNB/USDT:USDT', 'ILV/USDT:USDT']
    for sym in common_symbols:
        if sym not in test_symbols:
            test_symbols.append(sym)
    
    log("="*60)
    log("📋 KẾT QUẢ TEST PRECISION:")
    log("="*60)
    log("")
    
    for symbol in test_symbols:
        log(f"🔹 Symbol: {symbol}")
        log("-" * 60)
        
        try:
            if symbol not in exchange.markets:
                log(f"   ❌ Không tìm thấy trong markets")
                log("")
                continue
            
            market = exchange.markets[symbol]
            
            # [MỚI] In RAW RESPONSE từ Binance
            log(f"   📦 RAW MARKET DATA từ Binance:")
            log(f"   {json.dumps(market.get('info', {}), indent=6, ensure_ascii=False)}")
            log("")
            
            # 1. Lấy precision từ CCXT
            precision_price = market.get('precision', {}).get('price')
            precision_amount = market.get('precision', {}).get('amount')
            
            log(f"   📌 CCXT Precision:")
            log(f"      - Price Precision: {precision_price}")
            log(f"      - Amount Precision: {precision_amount}")
            
            # 2. Lấy limits
            limits = market.get('limits', {})
            price_limits = limits.get('price', {})
            amount_limits = limits.get('amount', {})
            
            tick_size = price_limits.get('min')
            min_amount = amount_limits.get('min')
            
            log(f"   📌 Limits:")
            log(f"      - Tick Size (Price Step): {tick_size}")
            log(f"      - Min Amount: {min_amount}")
            
            # 3. Tính precision từ tick_size (cách cũ - bị lỗi)
            if tick_size:
                import math
                try:
                    precision_from_log = abs(int(math.floor(math.log10(tick_size))))
                    log(f"   📌 Precision từ log10(tick_size): {precision_from_log}")
                except:
                    log(f"   ⚠️ Không tính được precision từ log10")
                
                # 4. Tính precision từ string (cách mới)
                tick_str = f"{tick_size:.10f}".rstrip('0').rstrip('.')
                if '.' in tick_str:
                    precision_from_str = len(tick_str.split('.')[1])
                else:
                    precision_from_str = 0
                
                log(f"   📌 Precision từ string: {precision_from_str} (Tick String: '{tick_str}')")
            
            # 5. Lấy thông tin từ info (raw data từ Binance)
            info = market.get('info', {})
            if info:
                log(f"   📌 Raw Info từ Binance:")
                
                # Binance Futures có thể có các field này
                price_precision_raw = info.get('pricePrecision')
                quantity_precision_raw = info.get('quantityPrecision')
                
                if price_precision_raw is not None:
                    log(f"      - pricePrecision: {price_precision_raw}")
                if quantity_precision_raw is not None:
                    log(f"      - quantityPrecision: {quantity_precision_raw}")
                
                # Filters
                filters = info.get('filters', [])
                for f in filters:
                    if f.get('filterType') == 'PRICE_FILTER':
                        log(f"      - PRICE_FILTER tickSize: {f.get('tickSize')}")
                        log(f"        Full PRICE_FILTER: {json.dumps(f, ensure_ascii=False)}")
                    elif f.get('filterType') == 'LOT_SIZE':
                        log(f"      - LOT_SIZE stepSize: {f.get('stepSize')}")
                        log(f"        Full LOT_SIZE: {json.dumps(f, ensure_ascii=False)}")
            
            # 6. PHÂN TÍCH SỰ KHÁC BIỆT
            log(f"   🔍 PHÂN TÍCH:")
            log(f"      ┌─ CCXT Precision: {precision_price} → Cho phép đến {precision_price} chữ số")
            log(f"      └─ Limits Tick Size: {tick_size} → Bước giá thực tế")
            
            # Tính precision từ tick_size
            if tick_size:
                tick_str = f"{tick_size:.10f}".rstrip('0').rstrip('.')
                if '.' in tick_str:
                    real_precision = len(tick_str.split('.')[1])
                else:
                    real_precision = 0
                log(f"      └─ Precision từ Tick Size: {real_precision} ('{tick_str}')")
            
            log("")
            
            # 7. TEST CỤ THỂ: Thử nhiều giá khác nhau
            test_prices = [3.999, 3.9998, 5.714, 5.7145, 5.715, 9.142, 9.1424, 9.1426]
            
            log(f"   🧪 TEST CỤ THỂ: Làm tròn nhiều giá khác nhau")
            log(f"   {'Giá gốc':<12} | {'CCXT':<12} | {'Tick Size':<12} | {'Hợp lệ?':<10}")
            log(f"   {'-'*12}─┼─{'-'*12}─┼─{'-'*12}─┼─{'-'*10}")
            
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
                
                log(f"   {test_price:<12.6f} | {str(rounded_ccxt):<12} | {rounded_tick:<12} | {is_valid:<10}")
            
            log("")
            
            # 8. GIẢI THÍCH KẾT QUẢ
            log(f"   📝 GIẢI THÍCH:")
            if tick_size == 0.01:
                log(f"      ✅ Tick Size = 0.01 → Giá CHỈ có thể: 5.71, 5.72, 5.73...")
                log(f"      ❌ Không thể: 5.715, 5.716... (vi phạm bước giá)")
            elif tick_size == 0.001:
                log(f"      ✅ Tick Size = 0.001 → Giá có thể: 5.714, 5.715, 5.716...")
            
            if precision_price and tick_size:
                if precision_price != tick_size:
                    log(f"      ⚠️ CCXT Precision ({precision_price}) ≠ Tick Size ({tick_size})")
                    log(f"      → Nên dùng Limits Tick Size ({tick_size}) để chính xác!")
            
            log("")
            
        except Exception as e:
            log(f"   ❌ Lỗi: {e}")
            import traceback
            log(traceback.format_exc())
            log("")
    
    log("="*60)
    log("✅ HOÀN TẤT TEST")
    log("="*60)
    log(f"📁 Kết quả đã được lưu vào: {log_filename}")

if __name__ == '__main__':
    try:
        test_precision()
    except Exception as e:
        log(f"\n❌ LỖI TỔNG: {e}")
        import traceback
        log(traceback.format_exc())
    
    print(f"\n✅ Log đã lưu tại: {log_filename}", flush=True)
    input("\nẤn Enter để đóng...")

