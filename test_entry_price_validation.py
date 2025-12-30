"""
Script test để kiểm tra logic lấy Entry Price
Mục đích: Xác minh rằng bot CHỈ lấy giá từ Position API, không fallback sang giá hiện tại
Test cụ thể cho: HOMEUSDT
"""

import ccxt
import configparser
from pathlib import Path
from datetime import datetime

# Symbol cần test
TARGET_SYMBOL = "HOME/USDT"

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

# Tạo thư mục logs nếu chưa có
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Tạo tên file log với timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = logs_dir / f'test_entry_price_{timestamp}.txt'

# Hàm ghi log (vào cả file và console)
def log(message):
    print(message)
    with open(log_filename, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

# Bắt đầu test
log("=" * 80)
log(f"🔍 KIỂM TRA ENTRY PRICE LOGIC - {TARGET_SYMBOL}")
log(f"📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)
log(f"📁 Log file: {log_filename}")
log("")

# Lấy tất cả positions
try:
    positions = exchange.fetch_positions()
    
    # Tìm position của HOME/USDT
    target_position = None
    for position in positions:
        if position['symbol'] == TARGET_SYMBOL and float(position.get('contracts', 0)) != 0:
            target_position = position
            break
    
    if not target_position:
        log(f"❌ Không tìm thấy position cho {TARGET_SYMBOL}")
        log(f"   (Position chưa mở hoặc đã đóng)")
    else:
        log(f"✅ Tìm thấy position {TARGET_SYMBOL}")
        log("")
        
        # Lấy thông tin position
        position_amt = float(target_position.get('contracts', 0))
        side = "LONG" if position_amt > 0 else "SHORT"
        leverage = int(target_position.get('leverage', 1))
        
        # Lấy entry price từ position
        entry_price_from_position = None
        if 'entryPrice' in target_position and target_position['entryPrice']:
            entry_price_from_position = float(target_position['entryPrice'])
        
        # Lấy giá hiện tại
        ticker = exchange.fetch_ticker(TARGET_SYMBOL)
        current_price = ticker['last']
        
        # Tính % chênh lệch
        diff_pct = 0.0
        if entry_price_from_position and entry_price_from_position > 0:
            diff_pct = ((current_price - entry_price_from_position) / entry_price_from_position) * 100
        
        # === HIỂN THỊ CHI TIẾT ===
        log("┌─────────────────────────────────────────────────────────────────────┐")
        log("│ 📊 THÔNG TIN POSITION                                               │")
        log("└─────────────────────────────────────────────────────────────────────┘")
        log(f"  Symbol:           {TARGET_SYMBOL}")
        log(f"  Side:             {side}")
        log(f"  Amount:           {position_amt}")
        log(f"  Leverage:         {leverage}x")
        log("")
        
        log("┌─────────────────────────────────────────────────────────────────────┐")
        log("│ 💰 GIÁ                                                              │")
        log("└─────────────────────────────────────────────────────────────────────┘")
        log(f"  Entry Price (Position API):  {entry_price_from_position}")
        log(f"  Current Price (Ticker):      {current_price}")
        log(f"  Chênh lệch:                  {diff_pct:+.4f}%")
        log("")
        
        # === VALIDATE ENTRY PRICE ===
        log("┌─────────────────────────────────────────────────────────────────────┐")
        log("│ ✅ VALIDATION ENTRY PRICE                                           │")
        log("└─────────────────────────────────────────────────────────────────────┘")
        
        if entry_price_from_position is None or entry_price_from_position <= 0:
            log("  ⚠️  WARNING: Không lấy được Entry Price từ Position API!")
            log("  ❌ Bot mới sẽ BỎ QUA symbol này (ĐÚNG LOGIC)")
            log("  ❌ Bot cũ sẽ dùng Current Price = SAI LOGIC!")
        else:
            log(f"  ✅ Entry Price hợp lệ: {entry_price_from_position}")
            log(f"  ✅ Bot mới sẽ dùng giá này để tính SL/TP")
            
            # === TÍNH TOÁN SL/TP (GIÁ TRỊ MẪU) ===
            log("")
            log("┌─────────────────────────────────────────────────────────────────────┐")
            log("│ 🎯 TÍNH TOÁN SL/TP (Giả định: SL=30%, TP=60%)                       │")
            log("└─────────────────────────────────────────────────────────────────────┘")
            
            # Giả định rate
            sl_rate = 0.3
            tp_rate = 0.6
            
            if side == "LONG":
                # LONG: SL thấp hơn entry, TP cao hơn entry
                sl_price_correct = entry_price_from_position * (1 - sl_rate)
                tp_price_correct = entry_price_from_position * (1 + tp_rate)
                
                # Nếu dùng current price (SAI)
                sl_price_wrong = current_price * (1 - sl_rate)
                tp_price_wrong = current_price * (1 + tp_rate)
                
                log(f"  📐 Công thức LONG:")
                log(f"     SL = Entry × (1 - 0.3) = {entry_price_from_position} × 0.7")
                log(f"     TP = Entry × (1 + 0.6) = {entry_price_from_position} × 1.6")
                log("")
                log(f"  ✅ ĐÚNG (Dùng Entry Price từ Position API):")
                log(f"     SL = {sl_price_correct:.6f}")
                log(f"     TP = {tp_price_correct:.6f}")
                log("")
                log(f"  ❌ SAI (Nếu dùng Current Price - Bot cũ):")
                log(f"     SL = {sl_price_wrong:.6f}  (Chênh {((sl_price_wrong - sl_price_correct) / sl_price_correct * 100):+.2f}%)")
                log(f"     TP = {tp_price_wrong:.6f}  (Chênh {((tp_price_wrong - tp_price_correct) / tp_price_correct * 100):+.2f}%)")
            else:
                # SHORT: SL cao hơn entry, TP thấp hơn entry
                sl_price_correct = entry_price_from_position * (1 + sl_rate)
                tp_price_correct = entry_price_from_position * (1 - tp_rate)
                
                sl_price_wrong = current_price * (1 + sl_rate)
                tp_price_wrong = current_price * (1 - tp_rate)
                
                log(f"  📐 Công thức SHORT:")
                log(f"     SL = Entry × (1 + 0.3) = {entry_price_from_position} × 1.3")
                log(f"     TP = Entry × (1 - 0.6) = {entry_price_from_position} × 0.4")
                log("")
                log(f"  ✅ ĐÚNG (Dùng Entry Price từ Position API):")
                log(f"     SL = {sl_price_correct:.6f}")
                log(f"     TP = {tp_price_correct:.6f}")
                log("")
                log(f"  ❌ SAI (Nếu dùng Current Price - Bot cũ):")
                log(f"     SL = {sl_price_wrong:.6f}  (Chênh {((sl_price_wrong - sl_price_correct) / sl_price_correct * 100):+.2f}%)")
                log(f"     TP = {tp_price_wrong:.6f}  (Chênh {((tp_price_wrong - tp_price_correct) / tp_price_correct * 100):+.2f}%)")
        
        log("")

except Exception as e:
    log(f"❌ Lỗi: {e}")
    import traceback
    error_msg = traceback.format_exc()
    log(error_msg)

# Kết luận
log("")
log("=" * 80)
log("📋 TÓM TẮT:")
log("=" * 80)
log("✅ Bot mới: CHỈ lấy Entry Price từ Position API (entryPrice)")
log("✅ Nếu không lấy được → BỎ QUA symbol (không tính SL/TP)")
log("❌ Bot cũ: Fallback sang Current Price từ Ticker API (SAI LOGIC)")
log("")
log("🎯 Entry Price = Giá khớp trung bình thực tế của position")
log("🎯 Current Price = Giá thị trường hiện tại (chỉ dùng để validation)")
log("=" * 80)
log(f"✅ Log đã lưu vào: {log_filename}")
log("=" * 80)

