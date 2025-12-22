import cst
import ccxt
from datetime import datetime
import sys
import os
import time

# ==============================================================================
# 1. CẤU HÌNH LOGGING (GIỮ NGUYÊN CLASS CỦA BẠN)
# ==============================================================================
class TeeOutput:
    def __init__(self, file_path):
        self.terminal = sys.stdout
        self.log_file = open(file_path, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)
        self.log_file.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log_file.flush()
    
    def close(self):
        if self.log_file:
            self.log_file.close()

# Tạo file log
now = datetime.now()
log_filename = f"check_orders_{now.strftime('%d_%m_%Y_%H_%M_%S')}.txt"
log_file_path = os.path.join(os.path.dirname(__file__), log_filename)
tee = TeeOutput(log_file_path)
sys.stdout = tee

# ==============================================================================
# 2. KHỞI TẠO BINANCE FUTURES
# ==============================================================================
print(f"📝 Log file: {log_filename}")
print("🔄 Đang kết nối Binance Futures...")

exchange = ccxt.binance({
    'enableRateLimit': True,
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {
        'defaultType': 'future', 
        'adjustForTimeDifference': True
    }
})

# ==============================================================================
# 3. CÁC HÀM XỬ LÝ API TRỰC TIẾP (CORE)
# ==============================================================================

def clean_symbol(symbol):
    """Chuyển đổi format: CELO/USDT -> CELOUSDT (Bắt buộc cho Algo API)"""
    return symbol.replace('/', '')

def fetch_algo_orders_safe(symbol=None, mode='open'):
    """
    Hàm Wrapper an toàn để gọi Algo API
    mode: 'open' (Lệnh treo) hoặc 'history' (Lịch sử lệnh)
    """
    params = {}
    if symbol:
        params['symbol'] = clean_symbol(symbol)
    
    method = 'GET'
    api_type = 'fapiPrivate' # Futures API Private Signed
    
    try:
        if mode == 'open':
            # Endpoint: /fapi/v1/algo/allOpenOrders
            path = 'algo/allOpenOrders'
        else:
            # Endpoint: /fapi/v1/algo/historicalOrders
            path = 'algo/historicalOrders'
            params['limit'] = 20  # Lấy 20 lệnh gần nhất
            
        # ⚡ QUAN TRỌNG: Gọi trực tiếp request để tránh lỗi AttributeError
        response = exchange.request(path, api_type, method, params)
        
        # Binance Algo luôn trả về dict có key 'data' hoặc list trực tiếp tùy endpoint
        # Thường là: {'code': 200, 'msg': '...', 'data': [...]}
        if isinstance(response, dict) and 'data' in response:
            return response['data']
        elif isinstance(response, list):
            return response
        return []
        
    except Exception as e:
        print(f"   ❌ Lỗi gọi API Algo ({mode}) cho {symbol}: {e}")
        return []

def format_ts(timestamp):
    """Format thời gian từ miliseconds sang chuỗi dễ đọc"""
    if not timestamp: return "N/A"
    return datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d %H:%M:%S')

# ==============================================================================
# 4. CHƯƠNG TRÌNH CHÍNH
# ==============================================================================

test_symbols = ['EPT/USDT', 'FUN/USDT', 'VELODROME/USDT', 'AIOT/USDT', 'CELO/USDT']

print(f"\n{'='*80}")
print(f"🚀 BẮT ĐẦU KIỂM TRA TOÀN DIỆN - {now}")
print(f"{'='*80}\n")

# --- PHẦN 1: KIỂM TRA LỆNH THƯỜNG (LIMIT/MARKET) ---
print("📡 PHẦN 1: CHECK LỆNH THƯỜNG (Standard Open Orders)")
try:
    # fetch_open_orders() dùng cho lệnh thường, không lấy được Trailing Stop
    std_orders = exchange.fetch_open_orders() 
    if std_orders:
        print(f"  ✅ Tìm thấy {len(std_orders)} lệnh thường đang treo.")
        for order in std_orders:
            print(f"    - [{order['symbol']}] {order['type']} {order['side']} | Price: {order['price']}")
    else:
        print("  ⚠️  Không có lệnh Limit/Market thường nào đang treo.")
except Exception as e:
    print(f"  ❌ Lỗi fetch_open_orders: {e}")

# --- PHẦN 2: KIỂM TRA LỆNH ALGO (TRAILING STOP / STRATEGY) ---
print(f"\n📡 PHẦN 2: CHECK LỆNH ALGO (Trailing Stop, Robot...)")

# 2.1 Lấy toàn bộ lệnh Algo đang mở (không cần loop symbol nếu API hỗ trợ all)
print(f"\n  ➤ Kiểm tra Algo Orders đang treo (Open):")
all_open_algo = fetch_algo_orders_safe(mode='open')

if all_open_algo:
    print(f"    ✅ TỔNG CỘNG: {len(all_open_algo)} lệnh Algo đang chạy.")
    for order in all_open_algo:
        s_symbol = order.get('symbol')
        s_id = order.get('algoId')
        s_type = order.get('algoType')
        s_price = order.get('activatePrice', 'N/A')
        print(f"      🔹 [{s_symbol}] ID: {s_id} | Loại: {s_type} | Kích hoạt: {s_price}")
else:
    print("    ⚠️  Không có lệnh Algo nào đang treo.")

# 2.2 Lấy lịch sử theo từng Symbol (Quan trọng để debug lệnh bị Cancel)
print(f"\n  ➤ Kiểm tra Lịch sử Algo (History) theo danh sách:")

for symbol in test_symbols:
    # Delay nhỏ để tránh rate limit
    time.sleep(0.2)
    hist = fetch_algo_orders_safe(symbol, mode='history')
    
    if hist:
        print(f"\n    🔍 Symbol: {symbol} ({len(hist)} bản ghi):")
        # Lọc chỉ lấy 3 lệnh gần nhất để hiển thị cho gọn
        for order in hist[:5]:
            status = order.get('algoStatus')
            # Đổi màu trạng thái để dễ nhìn
            status_icon = "🟢" if status == 'FINISHED' else "🔴" if status == 'CANCELED' else "⚪"
            
            print(f"      {status_icon} Time: {format_ts(order.get('createTime'))}")
            print(f"        ID: {order.get('algoId')} | Type: {order.get('algoType')}")
            print(f"        Status: {status} | Trigger: {order.get('activatePrice')}")
            print(f"        Realized Profit: {order.get('realizedPnl', 0)}")
    else:
        print(f"    ⚠️  {symbol}: Không có lịch sử Algo.")

print(f"\n{'='*80}")
print("✅ HOÀN TẤT KIỂM TRA.")
print(f"📂 Kết quả đã lưu tại: {log_filename}")
print(f"{'='*80}\n")

# Đóng file log trước khi treo terminal
tee.close()

# Giữ Terminal
try:
    if os.name == 'nt': # Windows
        os.system('pause')
    else: # Mac/Linux
        input("💡 Nhấn phím Enter để thoát chương trình...")
except Exception:
    pass