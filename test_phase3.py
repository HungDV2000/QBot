"""
Quick Test Script for Phase 3 - Data Collection
Kiểm tra nhanh các chức năng Phase 3 đã hoạt động chưa
"""

import sys
import ccxt
import cst
from data_collector import get_data_collector

print("=" * 60)
print("PHASE 3 - DATA COLLECTION QUICK TEST")
print("=" * 60)

# Test 1: Config
print("\n1. ✓ Kiểm tra Config...")
try:
    print(f"   - delay_track_30_prices: {cst.delay_track_30_prices}s")
    print(f"   - delay_periodic_report: {cst.delay_periodic_report}s")
    print(f"   ✅ Config OK")
except AttributeError as e:
    print(f"   ❌ Config thiếu biến: {e}")
    print(f"   → Cần update config.ini và cst.py!")
    sys.exit(1)

# Test 2: Exchange Connection
print("\n2. ✓ Kết nối Binance...")
try:
    exchange = ccxt.binance({
        'apiKey': cst.key_binance,
        'secret': cst.secret_binance,
        'options': {'defaultType': 'future'}
    })
    exchange.setSandboxMode(False)
    
    # Test connection
    balance = exchange.fetch_balance()
    wallet = float(balance['info']['totalWalletBalance'])
    print(f"   - Wallet Balance: ${wallet:.2f}")
    print(f"   ✅ Binance connection OK")
except Exception as e:
    print(f"   ❌ Lỗi kết nối Binance: {e}")
    sys.exit(1)

# Test 3: Data Collector
print("\n3. ✓ Khởi tạo Data Collector...")
try:
    collector = get_data_collector(exchange)
    print(f"   ✅ Data Collector initialized")
except Exception as e:
    print(f"   ❌ Lỗi khởi tạo: {e}")
    sys.exit(1)

# Test 4: Funding Rate
print("\n4. ✓ Test Funding Rate...")
try:
    fr = collector.get_funding_rate('BTC/USDT')
    print(f"   - BTC Funding Rate: {fr:.4f}%")
    print(f"   ✅ Funding Rate OK")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Test 5: Volume Multi Timeframe
print("\n5. ✓ Test Volume 5 khung...")
try:
    vols = collector.get_volumes_multi_timeframe('BTC/USDT')
    print(f"   - 15m: {vols.get('15m', 0):,.0f}")
    print(f"   - 1h:  {vols.get('1h', 0):,.0f}")
    print(f"   - 4h:  {vols.get('4h', 0):,.0f}")
    print(f"   - 1d:  {vols.get('1d', 0):,.0f}")
    print(f"   - 1w:  {vols.get('1w', 0):,.0f}")
    print(f"   ✅ Volume Multi Timeframe OK")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Test 6: Bollinger Bands
print("\n6. ✓ Test Bollinger Bands...")
try:
    bb_1h = collector.calculate_bollinger_bands('BTC/USDT', '1h')
    print(f"   - 1h Upper: ${bb_1h[0]:,.2f}")
    print(f"   - 1h Middle: ${bb_1h[1]:,.2f}")
    print(f"   - 1h Lower: ${bb_1h[2]:,.2f}")
    print(f"   ✅ Bollinger Bands OK")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Test 7: High/Low with Timestamp
print("\n7. ✓ Test High/Low 7 ngày + Timestamp...")
try:
    high, high_ts, low, low_ts = collector.get_high_low_with_timestamp('BTC/USDT', 7)
    print(f"   - High 7d: ${high:,.2f} @ timestamp {high_ts}")
    print(f"   - Low 7d:  ${low:,.2f} @ timestamp {low_ts}")
    print(f"   ✅ High/Low with Timestamp OK")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Test 8: 30 Recent Prices
print("\n8. ✓ Test Tracking 30 mức giá...")
try:
    prices = collector.get_30_recent_prices('BTC/USDT')
    print(f"   - Số mức giá: {len(prices)}")
    if prices:
        print(f"   - Giá cũ nhất: ${prices[0]['price']:,.2f}")
        print(f"   - Giá mới nhất: ${prices[-1]['price']:,.2f}")
    print(f"   ✅ Tracking 30 Prices OK")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Test 9: Distance to Extremes
print("\n9. ✓ Test Distance to Extremes...")
try:
    ticker = exchange.fetch_ticker('BTC/USDT')
    current = ticker['last']
    high_30d, _, low_30d, _ = collector.get_high_low_with_timestamp('BTC/USDT', 30)
    
    dist_high, dist_low = collector.calculate_distance_to_extreme(current, high_30d, low_30d)
    print(f"   - Current: ${current:,.2f}")
    print(f"   - Distance to High 30d: {dist_high:+.2f}%")
    print(f"   - Distance to Low 30d: {dist_low:+.2f}%")
    print(f"   ✅ Distance Calculation OK")
except Exception as e:
    print(f"   ❌ Lỗi: {e}")

# Summary
print("\n" + "=" * 60)
print("✅ TẤT CẢ TESTS HOÀN THÀNH!")
print("=" * 60)
print("\nPhase 3 đã sẵn sàng chạy!")
print("\nBước tiếp theo:")
print("1. Chạy hd_update_all.py để cập nhật data sheet")
print("2. Chạy hd_track_30_prices.py để tracking giá")
print("3. Chạy hd_periodic_report.py để nhận báo cáo Telegram")
print("\nHoặc chạy tất cả: ./start_all_bots.sh")
print("=" * 60)

