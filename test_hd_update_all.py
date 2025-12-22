"""
File test để kiểm tra các giá trị của một mã cụ thể
Nhập mã và xem tất cả các chỉ số
"""
import sys
import os

# Thêm thư mục hiện tại vào path để import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hd_update_all import (
    exchange, get_bb, calculate_price_range, calculate_high_low_30d,
    calculate_max_increase_decrease_4h, get_bien_do_max
)
from data_collector import get_data_collector
import numpy as np

def test_symbol(symbol):
    """Test và in ra tất cả các giá trị của một symbol"""
    
    # Chuẩn hóa symbol (thêm :USDT nếu chưa có)
    if not symbol.endswith(':USDT'):
        if '/USDT' in symbol:
            symbol = symbol.replace('/USDT', '/USDT:USDT')
        else:
            symbol = symbol + '/USDT:USDT'
    
    pair = symbol.replace(":USDT", "")
    pair_with_colon = symbol
    
    print(f"\n{'='*100}")
    print(f"🧪 TEST SYMBOL: {symbol}")
    print(f"{'='*100}\n")
    
    try:
        # 1. Lấy ticker để có % 24h và giá hiện tại
        ticker = exchange.fetch_ticker(symbol)
        percentage_24h = ticker.get('percentage', 0)
        current_price = ticker.get('last', 0)
        volume_24h = ticker.get('quoteVolume', 0)
        
        print(f"📊 THÔNG TIN CƠ BẢN:")
        print(f"   % 24h: {percentage_24h}%")
        print(f"   Giá trị hiện thời: {current_price}")
        print(f"   Volume 24h: {volume_24h}")
        print()
        
        # 2. Bollinger Bands (1h và 1d)
        print(f"📈 BOLLINGER BANDS:")
        result_bb_array = get_bb(pair, timeframes=['1h', '1d'])
        bb_1h_upper = result_bb_array[0]
        bb_1h_lower = result_bb_array[1]
        bb_1d_upper = result_bb_array[2]
        bb_1d_lower = result_bb_array[3]
        
        print(f"   BB1h trên: {bb_1h_upper:.8f}")
        print(f"   BB1h dưới: {bb_1h_lower:.8f}")
        print(f"   BB1 ngày trên: {bb_1d_upper:.8f}")
        print(f"   BB1 ngày dưới: {bb_1d_lower:.8f}")
        print()
        
        # 3. Biên độ 1h max tăng/giảm tuần (7 ngày)
        print(f"📉 BIÊN ĐỘ 1H TUẦN:")
        max_price_increase_month1, max_price_decrease_month1 = calculate_price_range(pair, 7, '1h')
        max_price_increase_month1 = "" if np.isnan(max_price_increase_month1) else max_price_increase_month1
        max_price_decrease_month1 = "" if np.isnan(max_price_decrease_month1) else max_price_decrease_month1
        
        print(f"   Biên độ 1h max tăng tuần: {max_price_increase_month1}")
        print(f"   Biên độ 1h max giảm tuần: {max_price_decrease_month1}")
        print()
        
        # 4. Giá cao/thấp 40 ngày
        print(f"📊 GIÁ CAO/THẤP 40 NGÀY:")
        high, low = calculate_high_low_30d(symbol)
        print(f"   Max 40 ngày: {high:.8f}")
        print(f"   Min 40 ngày: {low:.8f}")
        print()
        
        # 5. Max tăng/giảm 4h/60 ngày
        print(f"📈 MAX TĂNG/GIẢM 4H/60 NGÀY:")
        increase, decrease = calculate_max_increase_decrease_4h(symbol)
        print(f"   Max tăng 4h/60 ngày: {increase}%")
        print(f"   Max giảm 4h/60 ngày: {decrease}%")
        print()
        
        # 6. BB 1 tuần (Giá Cao Nhất / Giá Thấp Nhất)
        print(f"📊 BOLLINGER BANDS 1 TUẦN:")
        bb_1w = get_bb(pair, timeframes=['1w'])
        bb_1w_upper = bb_1w[0]
        bb_1w_lower = bb_1w[1]
        print(f"   Giá Cao Nhất (BB1w trên): {bb_1w_upper:.8f}")
        print(f"   Giá Thấp Nhất (BB1w dưới): {bb_1w_lower:.8f}")
        print()
        
        # 7. Biên độ 30d tăng/giảm
        print(f"📉 BIÊN ĐỘ 30 NGÀY:")
        bd = get_bien_do_max(pair)
        bd_30d_increase = bd[4] if len(bd) > 4 else ""
        bd_30d_decrease = bd[5] if len(bd) > 5 else ""
        print(f"   Biên độ 30d tăng: {bd_30d_increase}")
        print(f"   Biên độ 30d giảm: {bd_30d_decrease}")
        print()
        
        # 8. RSI 14
        print(f"📊 RSI 14:")
        try:
            ohlcv_rsi = exchange.fetch_ohlcv(pair, '1d', limit=15)
            closes = [x[4] for x in ohlcv_rsi]
            gains = []
            losses = []
            for i in range(1, len(closes)):
                change = closes[i] - closes[i-1]
                gains.append(max(0, change))
                losses.append(max(0, -change))
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))
            rsi_value = round(rsi, 2)
        except:
            rsi_value = "N/A"
        print(f"   RSI 14: {rsi_value}")
        print()
        
        # 9. Min/Min40 (O/K ratio)
        print(f"📊 MIN/MIN40:")
        if low != 0:
            ratio = round((bb_1w_lower / low), 4)
        else:
            ratio = "N/A"
        print(f"   Min/Min40: {ratio}")
        print()
        
        # 10. % đến BB1h trên/dưới
        print(f"📈 KHOẢNG CÁCH ĐẾN BB:")
        if current_price != 0:
            distance_to_bb_up = round(((bb_1h_upper - current_price) / current_price) * 100, 2)
            distance_to_bb_down = round(((current_price - bb_1h_lower) / current_price) * 100, 2)
        else:
            distance_to_bb_up = "N/A"
            distance_to_bb_down = "N/A"
        print(f"   % đến BB1h trên: {distance_to_bb_up}")
        print(f"   % đến BB1h dưới: {distance_to_bb_down}")
        print()
        
        # 11. Volume 1h và 4h
        print(f"📊 VOLUME:")
        try:
            data_collector = get_data_collector(exchange)
            vol_data = data_collector.get_volumes_multi_timeframe(pair, timeframes=['1h', '4h'])
            vol_1h = vol_data.get('1h', 0)
            vol_4h = vol_data.get('4h', 0)
        except Exception as e:
            vol_1h = f"N/A ({e})"
            vol_4h = f"N/A ({e})"
        print(f"   Vol 1h: {vol_1h}")
        print(f"   Vol 4h: {vol_4h}")
        print()
        
        # TỔNG KẾT - In ra dạng bảng
        print(f"{'='*100}")
        print(f"📋 TỔNG KẾT - TẤT CẢ CÁC GIÁ TRỊ:")
        print(f"{'='*100}\n")
        
        results = [
            ("% 24h", percentage_24h),
            ("Giá trị hiện thời", current_price),
            ("BB1h trên", bb_1h_upper),
            ("BB1h dưới", bb_1h_lower),
            ("BB1 ngày trên", bb_1d_upper),
            ("BB1 ngày dưới", bb_1d_lower),
            ("Biên độ 1h max tăng tuần", max_price_increase_month1),
            ("Biên độ 1h max giảm tuần", max_price_decrease_month1),
            ("Max 40 ngày", high),
            ("Min 40 ngày", low),
            ("Max tăng 4h/60 ngày", increase),
            ("Max giảm 4h/60 ngày", decrease),
            ("Giá Cao Nhất (BB1w trên)", bb_1w_upper),
            ("Giá Thấp Nhất (BB1w dưới)", bb_1w_lower),
            ("Biên độ 30d tăng", bd_30d_increase),
            ("Biên độ 30d giảm", bd_30d_decrease),
            ("Volume 24h", volume_24h),
            ("RSI 14", rsi_value),
            ("Min/Min40", ratio),
            ("% đến BB1h trên", distance_to_bb_up),
            ("% đến BB1h dưới", distance_to_bb_down),
            ("Vol 1h", vol_1h),
            ("Vol 4h", vol_4h),
        ]
        
        for label, value in results:
            print(f"{label:30} : {value}")
        
        print(f"\n{'='*100}\n")
        
    except Exception as e:
        print(f"❌ Lỗi khi test symbol {symbol}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Nhập từ command line
        symbol = sys.argv[1]
        test_symbol(symbol)
    else:
        # Nhập từ input
        print("Nhập mã cần test (ví dụ: BTC/USDT hoặc BTC/USDT:USDT):")
        symbol = input().strip()
        if symbol:
            test_symbol(symbol)
        else:
            print("❌ Không có mã nào được nhập!")
