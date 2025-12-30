"""
Script liệt kê tất cả positions hiện có và test Entry Price logic
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime

# Tạo thư mục logs
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

# Tạo log file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_filename = logs_dir / f'test_all_positions_{timestamp}.txt'

def log(message):
    print(message, flush=True)
    try:
        with open(log_filename, 'a', encoding='utf-8') as f:
            f.write(message + '\n')
    except:
        pass

# === KHỞI TẠO ===
log("=" * 80)
log("🔍 LIỆT KÊ TẤT CẢ POSITIONS VÀ KIỂM TRA ENTRY PRICE")
log("=" * 80)

try:
    log("📦 Import thư viện...")
    import ccxt
    import configparser
    log("✅ Import thành công")
except ImportError as e:
    log(f"❌ Lỗi import: {e}")
    input("\n⏸️  Nhấn Enter để thoát...")
    sys.exit(1)

# Đọc config
try:
    log("📄 Đọc config.ini...")
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / 'config.ini'
    config.read(config_path, encoding='utf-8')
    
    api_key = None
    secret_key = None
    
    possible_sections = ['global', 'Binance', 'binance', 'DEFAULT']
    possible_key_names = [
        ('key_binance', 'secret_binance'),
        ('api_key', 'secret_key'),
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
        log("❌ Không tìm thấy API key/secret")
        input("\n⏸️  Nhấn Enter để thoát...")
        sys.exit(1)
    
    log("✅ Đọc config thành công")
except Exception as e:
    log(f"❌ Lỗi đọc config: {e}")
    log(traceback.format_exc())
    input("\n⏸️  Nhấn Enter để thoát...")
    sys.exit(1)

# Kết nối Binance
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
    log(f"❌ Lỗi kết nối: {e}")
    log(traceback.format_exc())
    input("\n⏸️  Nhấn Enter để thoát...")
    sys.exit(1)

log("")
log("=" * 80)
log(f"📊 DANH SÁCH POSITIONS HIỆN TẠI")
log(f"📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 80)

# Lấy tất cả positions
try:
    log("📊 Lấy danh sách positions từ Binance...")
    positions = exchange.fetch_positions()
    
    # Lọc positions có amount != 0
    active_positions = [p for p in positions if float(p.get('contracts', 0)) != 0]
    
    log(f"✅ Tìm thấy {len(active_positions)} positions đang mở")
    log("")
    
    if not active_positions:
        log("⚠️  Không có position nào đang mở!")
        log("💡 Mở position trên Binance Futures rồi chạy lại script")
    else:
        # Giả định rate để tính SL/TP
        sl_rate = 0.3
        tp_rate = 0.6
        
        # Duyệt qua từng position
        for idx, position in enumerate(active_positions, 1):
            symbol = position['symbol']
            position_amt = float(position.get('contracts', 0))
            side = "LONG" if position_amt > 0 else "SHORT"
            leverage = int(position.get('leverage', 1))
            
            # Lấy entry price
            entry_price = None
            if 'entryPrice' in position and position['entryPrice']:
                entry_price = float(position['entryPrice'])
            
            # Lấy giá hiện tại
            try:
                ticker = exchange.fetch_ticker(symbol)
                current_price = ticker['last']
            except:
                current_price = None
            
            # Tính % chênh lệch
            diff_pct = 0.0
            if entry_price and current_price:
                diff_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Hiển thị thông tin
            log(f"┌{'─' * 78}┐")
            log(f"│ 📍 POSITION #{idx}: {symbol:<50} ({side:>5}) │")
            log(f"└{'─' * 78}┘")
            log(f"  Amount:           {position_amt}")
            log(f"  Leverage:         {leverage}x")
            log(f"  Entry Price:      {entry_price if entry_price else 'N/A'}")
            log(f"  Current Price:    {current_price if current_price else 'N/A'}")
            if entry_price and current_price:
                log(f"  Chênh lệch:       {diff_pct:+.4f}%")
            
            # Kiểm tra Entry Price
            if entry_price is None or entry_price <= 0:
                log("")
                log("  ❌ CẢNH BÁO: Không lấy được Entry Price!")
                log("  → Bot mới sẽ BỎ QUA symbol này")
                log("  → Bot cũ sẽ dùng Current Price (SAI LOGIC)")
            else:
                log("")
                log("  ✅ Entry Price hợp lệ")
                
                # Tính SL/TP
                if side == "LONG":
                    sl_price = entry_price * (1 - sl_rate)
                    tp_price = entry_price * (1 + tp_rate)
                    
                    log(f"  📐 SL/TP (Giả định: SL=30%, TP=60%):")
                    log(f"     SL = {entry_price} × 0.7  = {sl_price:.6f}")
                    log(f"     TP = {entry_price} × 1.6  = {tp_price:.6f}")
                    
                    if current_price:
                        sl_wrong = current_price * (1 - sl_rate)
                        tp_wrong = current_price * (1 + tp_rate)
                        log(f"  ⚠️  Nếu dùng Current Price (SAI):")
                        log(f"     SL = {current_price} × 0.7  = {sl_wrong:.6f} (Chênh {((sl_wrong - sl_price) / sl_price * 100):+.2f}%)")
                        log(f"     TP = {current_price} × 1.6  = {tp_wrong:.6f} (Chênh {((tp_wrong - tp_price) / tp_price * 100):+.2f}%)")
                else:
                    sl_price = entry_price * (1 + sl_rate)
                    tp_price = entry_price * (1 - tp_rate)
                    
                    log(f"  📐 SL/TP (Giả định: SL=30%, TP=60%):")
                    log(f"     SL = {entry_price} × 1.3  = {sl_price:.6f}")
                    log(f"     TP = {entry_price} × 0.4  = {tp_price:.6f}")
                    
                    if current_price:
                        sl_wrong = current_price * (1 + sl_rate)
                        tp_wrong = current_price * (1 - tp_rate)
                        log(f"  ⚠️  Nếu dùng Current Price (SAI):")
                        log(f"     SL = {current_price} × 1.3  = {sl_wrong:.6f} (Chênh {((sl_wrong - sl_price) / sl_price * 100):+.2f}%)")
                        log(f"     TP = {current_price} × 0.4  = {tp_wrong:.6f} (Chênh {((tp_wrong - tp_price) / tp_price * 100):+.2f}%)")
            
            log("")

except Exception as e:
    log("")
    log(f"❌ LỖI: {e}")
    log(traceback.format_exc())

# Kết luận
log("")
log("=" * 80)
log("📋 TÓM TẮT:")
log("=" * 80)
log("✅ Bot mới: CHỈ lấy Entry Price từ Position API")
log("✅ Nếu không lấy được → BỎ QUA symbol")
log("❌ Bot cũ: Fallback sang Current Price (SAI LOGIC)")
log("")
log("🎯 Entry Price = Giá khớp trung bình thực tế")
log("🎯 Current Price = Giá thị trường hiện tại (chỉ validation)")
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

