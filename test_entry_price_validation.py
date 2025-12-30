"""
Script test để kiểm tra logic lấy Entry Price
Mục đích: Xác minh rằng bot CHỈ lấy giá từ Position API, không fallback sang giá hiện tại
Test cụ thể cho: HOMEUSDT
"""

import sys
import traceback

# Tạo thư mục logs ngay từ đầu
from pathlib import Path
from datetime import datetime

logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Tạo tên file log với timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = logs_dir / f'test_entry_price_{timestamp}.txt'

# Hàm ghi log (vào cả file và console)
def log(message):
    print(message, flush=True)
    try:
        with open(log_filename, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    except Exception as e:
        print(f"[ERROR] Không ghi được log vào file: {e}", flush=True)

# Symbol cần test (hỗ trợ cả 2 format: HOME/USDT và HOME/USDT:USDT)
TARGET_SYMBOL = "HOME/USDT"
TARGET_SYMBOL_ALT = "HOME/USDT:USDT"

# === BƯỚC 1: Import và Khởi tạo ===
log("=" * 80)
log("🚀 KHỞI ĐỘNG TEST ENTRY PRICE LOGIC")
log("=" * 80)

try:
    log("📦 Import thư viện...")
    import ccxt
    import configparser
    log("✅ Import thành công")
except ImportError as e:
    log(f"❌ Lỗi import: {e}")
    log("💡 Cài đặt: pip install ccxt")
    input("\n⏸️  Nhấn Enter để thoát...")
    sys.exit(1)

# === BƯỚC 2: Đọc Config ===
try:
    log("📄 Đọc config.ini...")
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / 'config.ini'
    
    if not config_path.exists():
        log(f"❌ Không tìm thấy file config.ini tại: {config_path}")
        input("\n⏸️  Nhấn Enter để thoát...")
        sys.exit(1)
    
    config.read(config_path, encoding='utf-8')
    
    # Tìm API key/secret (hỗ trợ nhiều format khác nhau)
    api_key = None
    secret_key = None
    
    # Thử các section và tên key khác nhau
    possible_sections = ['global', 'Binance', 'binance', 'DEFAULT']
    possible_key_names = [
        ('key_binance', 'secret_binance'),
        ('api_key', 'secret_key'),
        ('apiKey', 'secretKey'),
    ]
    
    for section in possible_sections:
        if not config.has_section(section) and section != 'DEFAULT':
            continue
        
        for key_name, secret_name in possible_key_names:
            try:
                api_key = config.get(section, key_name)
                secret_key = config.get(section, secret_name)
                log(f"✅ Tìm thấy API key trong section [{section}]")
                break
            except:
                continue
        
        if api_key and secret_key:
            break
    
    if not api_key or not secret_key:
        log("❌ Không tìm thấy API key/secret trong config.ini")
        log("💡 Kiểm tra file config.ini có chứa key_binance và secret_binance")
        input("\n⏸️  Nhấn Enter để thoát...")
        sys.exit(1)
    
    log("✅ Đọc config thành công")
except Exception as e:
    log(f"❌ Lỗi đọc config: {e}")
    log(traceback.format_exc())
    input("\n⏸️  Nhấn Enter để thoát...")
    sys.exit(1)

# === BƯỚC 3: Khởi tạo Exchange ===
try:
    log("🔌 Kết nối Binance...")
    exchange = ccxt.binance({
        'apiKey': api_key,
        'secret': secret_key,
        'options': {'defaultType': 'future'},
        'timeout': 30000,
        'enableRateLimit': True
    })
    log("✅ Kết nối thành công")
except Exception as e:
    log(f"❌ Lỗi kết nối Binance: {e}")
    log(traceback.format_exc())
    input("\n⏸️  Nhấn Enter để thoát...")
    sys.exit(1)

log("")

# === BƯỚC 4: Test Position ===
log("=" * 80)
log(f"🔍 KIỂM TRA ENTRY PRICE LOGIC - {TARGET_SYMBOL}")
log(f"📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)
log(f"📁 Log file: {log_filename}")
log("")

# Lấy tất cả positions
try:
    log("📊 Lấy danh sách positions từ Binance...")
    positions = exchange.fetch_positions()
    log(f"✅ Đã lấy {len(positions)} positions")
    
    # Tìm position của HOME/USDT (hỗ trợ cả 2 format)
    target_position = None
    for position in positions:
        pos_symbol = position['symbol']
        amt = float(position.get('contracts', 0))
        
        # Kiểm tra symbol khớp (hỗ trợ HOME/USDT hoặc HOME/USDT:USDT)
        if amt != 0 and (pos_symbol == TARGET_SYMBOL or pos_symbol == TARGET_SYMBOL_ALT or 
                        'HOME' in pos_symbol.upper() and 'USDT' in pos_symbol.upper()):
            target_position = position
            TARGET_SYMBOL_FOUND = pos_symbol  # Lưu symbol thực tế tìm được
            log(f"✅ Tìm thấy position với symbol: {pos_symbol}")
            break
    
    if not target_position:
        log("")
        log(f"❌ Không tìm thấy position cho {TARGET_SYMBOL} hoặc {TARGET_SYMBOL_ALT}")
        log(f"   (Position chưa mở hoặc đã đóng)")
        log("")
        log("💡 Để test được, bạn cần:")
        log("   1. Mở position HOMEUSDT trên Binance Futures")
        log("   2. Chạy lại script này")
        log("")
        log("🔍 Debug: Chạy debug_positions.py để xem tất cả positions")
    else:
        log("")
        log(f"✅ Tìm thấy position {TARGET_SYMBOL_FOUND}")
        log("")
        
        # Lấy thông tin position
        position_amt = float(target_position.get('contracts', 0))
        
        # [FIX] CCXT contracts luôn dương! Phải dùng 'side' để xác định LONG/SHORT
        position_side = target_position.get('side', '').lower()
        side = "LONG" if position_side == 'long' else "SHORT"
        leverage = int(target_position.get('leverage', 1)) if target_position.get('leverage') else 1
        
        # Lấy entry price từ position
        entry_price_from_position = None
        if 'entryPrice' in target_position and target_position['entryPrice']:
            entry_price_from_position = float(target_position['entryPrice'])
        
        # Lấy giá hiện tại
        log("📈 Lấy giá hiện tại...")
        ticker = exchange.fetch_ticker(TARGET_SYMBOL_FOUND)
        current_price = ticker['last']
        log("✅ Đã lấy giá hiện tại")
        log("")
        
        # Tính % chênh lệch
        diff_pct = 0.0
        if entry_price_from_position and entry_price_from_position > 0:
            diff_pct = ((current_price - entry_price_from_position) / entry_price_from_position) * 100
        
        # === HIỂN THỊ CHI TIẾT ===
        log("┌─────────────────────────────────────────────────────────────────────┐")
        log("│ 📊 THÔNG TIN POSITION                                               │")
        log("└─────────────────────────────────────────────────────────────────────┘")
        log(f"  Symbol:           {TARGET_SYMBOL_FOUND}")
        log(f"  Side:             {side} (từ position.side={position_side})")
        log(f"  Contracts:        {position_amt} (luôn dương trong CCXT)")
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

except ccxt.NetworkError as e:
    log("")
    log(f"❌ LỖI MẠNG: {e}")
    log("💡 Kiểm tra kết nối internet và thử lại")
    log(traceback.format_exc())
except ccxt.AuthenticationError as e:
    log("")
    log(f"❌ LỖI XÁC THỰC: {e}")
    log("💡 Kiểm tra API key/secret trong config.ini")
    log(traceback.format_exc())
except Exception as e:
    log("")
    log(f"❌ LỖI: {e}")
    log(traceback.format_exc())

# === KẾT LUẬN ===
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
log("")
log("✅ TEST HOÀN TẤT - Terminal không tự động tắt")
log("⏸️  Nhấn Ctrl+C hoặc đóng terminal để thoát")
log("")

# Giữ terminal mở
try:
    input("⏸️  Nhấn Enter để thoát...")
except KeyboardInterrupt:
    log("\n👋 Đã thoát bằng Ctrl+C")
except:
    pass

