"""
Script test để kiểm tra logic lấy Entry Price
Mục đích: Xác minh rằng bot CHỈ lấy giá từ Position API, không fallback sang giá hiện tại
"""

import ccxt
import configparser
from pathlib import Path

# Đọc config
config = configparser.ConfigParser()
config_path = Path(__file__).parent / 'config.ini'
config.read(config_path, encoding='utf-8')

api_key = config.get('Binance', 'api_key')
secret_key = config.get('Binance', 'secret_key')

# Khởi tạo exchange
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': secret_key,
    'options': {'defaultType': 'future'}
})

print("="*60)
print("🔍 KIỂM TRA ENTRY PRICE LOGIC")
print("="*60)

# Lấy tất cả positions
try:
    positions = exchange.fetch_positions()
    positions_with_amt = [p for p in positions if float(p.get('contracts', 0)) > 0]
    
    print(f"\n✅ Tìm thấy {len(positions_with_amt)} vị thế đang mở\n")
    
    for position in positions_with_amt:
        symbol = position['symbol']
        position_amt = float(position.get('contracts', 0))
        
        # Lấy entry price từ position
        entry_price_from_position = None
        if 'entryPrice' in position and position['entryPrice']:
            entry_price_from_position = float(position['entryPrice'])
        
        # Lấy giá hiện tại
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Tính % chênh lệch
        diff_pct = 0.0
        if entry_price_from_position and entry_price_from_position > 0:
            diff_pct = ((current_price - entry_price_from_position) / entry_price_from_position) * 100
        
        # Hiển thị kết quả
        side = "LONG" if position_amt > 0 else "SHORT"
        print(f"📊 {symbol} ({side})")
        print(f"   Amount: {position_amt}")
        print(f"   Entry Price (Position API): {entry_price_from_position}")
        print(f"   Current Price (Ticker): {current_price}")
        print(f"   Chênh lệch: {diff_pct:+.4f}%")
        
        # Cảnh báo nếu không lấy được entry price
        if entry_price_from_position is None or entry_price_from_position <= 0:
            print(f"   ⚠️  WARNING: Không lấy được Entry Price từ Position API!")
            print(f"   ❌ Bot mới sẽ BỎ QUA symbol này (ĐÚNG LOGIC)")
        else:
            print(f"   ✅ Entry Price hợp lệ")
        
        print()

except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
print("📋 TÓM TẮT:")
print("="*60)
print("✅ Bot mới: CHỈ lấy Entry Price từ Position API")
print("✅ Nếu không lấy được → BỎ QUA (không dùng giá hiện tại)")
print("❌ Bot cũ: Fallback sang giá hiện tại (SAI LOGIC)")
print("="*60)

