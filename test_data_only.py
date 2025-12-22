"""
File test độc lập - Chỉ test tính toán dữ liệu, không phụ thuộc Google Sheets
"""
import sys
import os
import ccxt
import pandas as pd
import numpy as np
import time
from datetime import datetime, timezone
import configparser

# Đọc config
config = configparser.ConfigParser()
config.read('config.ini')

# Constants từ config
calculate_high_low_day_total = 40
try:
    max_increase_decrease_4h_day_count = int(config.get('global', 'max_increase_decrease_4h_day_count', fallback='60'))
except:
    max_increase_decrease_4h_day_count = 60

# Setup exchange
exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)

# Đọc API keys từ cst hoặc config
try:
    import cst
    api_key = cst.key_binance
    api_secret = cst.secret_binance
except:
    # Fallback: đọc từ file config hoặc environment
    api_key = os.getenv('BINANCE_API_KEY', '')
    api_secret = os.getenv('BINANCE_API_SECRET', '')

exchange = exchange_class({
    'enableRateLimit': True,  
    'apiKey': api_key,
    'secret': api_secret,
    'options': {
        'defaultType': 'future' 
    }
})
exchange.setSandboxMode(False)

# Import data_collector nếu có
try:
    from data_collector import get_data_collector
    USE_DATA_COLLECTOR = True
except:
    USE_DATA_COLLECTOR = False
    print("⚠️ data_collector không có, sẽ bỏ qua Vol 1h/4h")

# ==================== CÁC HÀM TÍNH TOÁN (copy từ hd_update_all.py) ====================

def calculate_max_increase_decrease_4h(pair, timeframe='4h', days=max_increase_decrease_4h_day_count):
    candles_per_day = 24 // 4
    length = days * candles_per_day
    ohlcv_data = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=length)
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['change_percent'] = (df['close'] - df['open']) / df['open'] * 100
    max_increase = round(df['change_percent'].max(), 2)
    max_decrease = round(df['change_percent'].min(), 2)
    return max_increase, max_decrease

def calculate_price_range(pair, num_days, timeframe):
    if timeframe == '15m':
        length = num_days * 24 * 60 / 15  
    elif timeframe == '1h':
        length = num_days * 24  
    elif timeframe == '1d':
        length = num_days  
    length = int(length)
    ohlcv_data = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=length)
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['price_change'] = df['close'] - df['open']
    df['direction'] = df['price_change'].apply(lambda x: 'Tăng' if x > 0 else 'Giảm' if x < 0 else 'Đứng giá')
    max_price = df.apply(lambda row: max(row['close'], row['open']) if row['direction'] == 'Giảm' else min(row['close'], row['open']), axis=1)
    df['amplitude_percent'] = ((df['high'] - df['low']) / max_price) * 100
    amplitude_increase = df[df['direction'] == 'Tăng']['amplitude_percent'].max()
    amplitude_decrease = df[df['direction'] == 'Giảm']['amplitude_percent'].max()
    max_price_increase = round(amplitude_increase, 2)
    max_price_decrease = round(amplitude_decrease, 2)
    return max_price_increase, max_price_decrease

def calculate_high_low_30d(pair, timeframe='1d'):
    num_days = calculate_high_low_day_total
    length = num_days
    ohlcv_data = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=length)
    df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    highest_price = df['high'].max()
    lowest_price = df['low'].min()
    return highest_price, lowest_price

def get_bien_do_max(pair):
    res = []
    max_price_increase_month, max_price_decrease_month = calculate_price_range(pair, 7, '15m')
    res.append(max_price_increase_month)
    res.append(max_price_decrease_month)
    max_price_increase_month1, max_price_decrease_month1 = calculate_price_range(pair, 7, '1h')
    res.append(max_price_increase_month1)
    res.append(max_price_decrease_month1)
    max_price_increase_month2, max_price_decrease_month2 = calculate_price_range(pair, 30, '1d')
    res.append(max_price_increase_month2)
    res.append(max_price_decrease_month2)
    return res

def get_bb(pair, timeframes):
    bb = []
    length = 20
    multiplier = 2
    for timeframe in timeframes:
        ohlcv_data = exchange.fetch_ohlcv(pair, timeframe=timeframe, limit=length)
        closing_prices = [ohlcv[4] for ohlcv in ohlcv_data]
        moving_average = np.mean(closing_prices)
        standard_deviation = np.std(closing_prices)
        upper_band = moving_average + multiplier * standard_deviation
        lower_band = moving_average - multiplier * standard_deviation
        bb.append(upper_band)
        bb.append(lower_band)
    return bb

# ==================== HÀM TEST ====================

def test_symbol(symbol):
    """Test và in ra tất cả các giá trị của một symbol"""
    
    # Chuẩn hóa symbol
    if not symbol.endswith(':USDT'):
        if '/USDT' in symbol:
            symbol = symbol.replace('/USDT', '/USDT:USDT')
        else:
            symbol = symbol + '/USDT:USDT'
    
    pair = symbol.replace(":USDT", "")
    
    print(f"\n{'='*100}")
    print(f"🧪 TEST SYMBOL: {symbol}")
    print(f"{'='*100}\n")
    
    try:
        # 1. Lấy ticker
        print("📥 Đang lấy dữ liệu từ Binance...")
        ticker = exchange.fetch_ticker(symbol)
        percentage_24h = ticker.get('percentage', 0)
        current_price = ticker.get('last', 0)
        volume_24h = ticker.get('quoteVolume', 0)
        print(f"✅ Đã lấy dữ liệu cơ bản\n")
        
        # 2. Bollinger Bands (1h và 1d)
        print("📈 Đang tính Bollinger Bands...")
        result_bb_array = get_bb(pair, timeframes=['1h', '1d'])
        bb_1h_upper = result_bb_array[0]
        bb_1h_lower = result_bb_array[1]
        bb_1d_upper = result_bb_array[2]
        bb_1d_lower = result_bb_array[3]
        
        # 3. BB 1 tuần
        bb_1w = get_bb(pair, timeframes=['1w'])
        bb_1w_upper = bb_1w[0]
        bb_1w_lower = bb_1w[1]
        
        # 4. Biên độ 1h max tăng/giảm tuần
        print("📉 Đang tính biên độ 1h tuần...")
        max_price_increase_month1, max_price_decrease_month1 = calculate_price_range(pair, 7, '1h')
        max_price_increase_month1 = "" if np.isnan(max_price_increase_month1) else max_price_increase_month1
        max_price_decrease_month1 = "" if np.isnan(max_price_decrease_month1) else max_price_decrease_month1
        
        # 5. Giá cao/thấp 40 ngày
        print("📊 Đang tính giá cao/thấp 40 ngày...")
        high, low = calculate_high_low_30d(symbol)
        
        # 6. Max tăng/giảm 4h/60 ngày
        print("📈 Đang tính max tăng/giảm 4h/60 ngày...")
        increase, decrease = calculate_max_increase_decrease_4h(symbol)
        
        # 7. Biên độ 30d
        print("📉 Đang tính biên độ 30d...")
        bd = get_bien_do_max(pair)
        bd_30d_increase = bd[4] if len(bd) > 4 else ""
        bd_30d_decrease = bd[5] if len(bd) > 5 else ""
        
        # 8. RSI 14
        print("📊 Đang tính RSI 14...")
        try:
            ohlcv_rsi = exchange.fetch_ohlcv(pair, '1d', limit=15)
            closes = [x[4] for x in ohlcv_rsi]
            gains = []
            losses = []
            for i in range(1, len(closes)):
                change = closes[i] - closes[i-1]
                gains.append(max(0, change))
                losses.append(max(0, -change))
            avg_gain = np.mean(gains) if gains else 0
            avg_loss = np.mean(losses) if losses else 0
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi_value = round(100 - (100 / (1 + rs)), 2)
        except Exception as e:
            rsi_value = f"N/A ({e})"
        
        # 9. Min/Min40
        if low != 0:
            ratio = round((bb_1w_lower / low), 4)
        else:
            ratio = "N/A"
        
        # 10. % đến BB1h
        if current_price != 0:
            distance_to_bb_up = round(((bb_1h_upper - current_price) / current_price) * 100, 2)
            distance_to_bb_down = round(((current_price - bb_1h_lower) / current_price) * 100, 2)
        else:
            distance_to_bb_up = "N/A"
            distance_to_bb_down = "N/A"
        
        # 11. Volume 1h và 4h
        print("📊 Đang lấy volume 1h/4h...")
        if USE_DATA_COLLECTOR:
            try:
                data_collector = get_data_collector(exchange)
                vol_data = data_collector.get_volumes_multi_timeframe(pair, timeframes=['1h', '4h'])
                vol_1h = vol_data.get('1h', 0)
                vol_4h = vol_data.get('4h', 0)
            except Exception as e:
                vol_1h = f"N/A ({e})"
                vol_4h = f"N/A ({e})"
        else:
            vol_1h = "N/A (data_collector không có)"
            vol_4h = "N/A (data_collector không có)"
        
        print(f"\n{'='*100}")
        print(f"📋 KẾT QUẢ:")
        print(f"{'='*100}\n")
        
        # In ra theo thứ tự
        results = [
            ("% 24h", f"{percentage_24h}%"),
            ("Giá trị hiện thời", f"{current_price:.8f}"),
            ("BB1h trên", f"{bb_1h_upper:.8f}"),
            ("BB1h dưới", f"{bb_1h_lower:.8f}"),
            ("BB1 ngày trên", f"{bb_1d_upper:.8f}"),
            ("BB1 ngày dưới", f"{bb_1d_lower:.8f}"),
            ("Biên độ 1h max tăng tuần", max_price_increase_month1),
            ("Biên độ 1h max giảm tuần", max_price_decrease_month1),
            ("Max 40 ngày", f"{high:.8f}"),
            ("Min 40 ngày", f"{low:.8f}"),
            ("Max tăng 4h/60 ngày", f"{increase}%"),
            ("Max giảm 4h/60 ngày", f"{decrease}%"),
            ("Giá Cao Nhất (BB1w trên)", f"{bb_1w_upper:.8f}"),
            ("Giá Thấp Nhất (BB1w dưới)", f"{bb_1w_lower:.8f}"),
            ("Biên độ 30d tăng", bd_30d_increase),
            ("Biên độ 30d giảm", bd_30d_decrease),
            ("Volume 24h", f"{volume_24h:.2f}"),
            ("RSI 14", rsi_value),
            ("Min/Min40", ratio),
            ("% đến BB1h trên", f"{distance_to_bb_up}%"),
            ("% đến BB1h dưới", f"{distance_to_bb_down}%"),
            ("Vol 1h", vol_1h),
            ("Vol 4h", vol_4h),
        ]
        
        for label, value in results:
            print(f"{label:35} : {value}")
        
        print(f"\n{'='*100}\n")
        
    except Exception as e:
        print(f"❌ Lỗi khi test symbol {symbol}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        test_symbol(symbol)
    else:
        print("Nhập mã cần test (ví dụ: BTC/USDT hoặc BTC/USDT:USDT):")
        symbol = input().strip()
        if symbol:
            test_symbol(symbol)
        else:
            print("❌ Không có mã nào được nhập!")
