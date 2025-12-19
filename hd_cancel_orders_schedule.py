import ccxt
import cst
from pathlib import Path
import time
import telegram_factory
import logging
import os

file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

# Log file riêng (liên quan đến hủy lệnh - xử lý tiền)
logging.basicConfig(
    filename='hd_cancel.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def cancel_all_open_orders(symbol):
    """Hủy TẤT CẢ orders (Basic + Conditional/Algo orders)"""
    total_cancelled = 0
    
    # BƯỚC 1: Hủy Basic orders (LIMIT, MARKET, STOP...)
    try:
        open_orders = exchange.fetch_open_orders(symbol)
        
        if open_orders:
            for order in open_orders:
                try:
                    order_id = order['id']
                    cancel_result = exchange.cancel_order(order_id, symbol)
                    total_cancelled += 1
                    print(f"✅ Hủy Basic order {order_id} kết quả: {cancel_result}", flush=True)
                    logger.info(f"Đã hủy Basic order {order_id} cho {symbol}")
                except Exception as e:
                    logger.error(f"Lỗi khi hủy Basic order {order.get('id', 'N/A')}: {e}")
    except Exception as e:
        logger.error(f"Lỗi khi lấy Basic orders cho {symbol}: {e}")
    
    # BƯỚC 2: Hủy Algo/Conditional orders (TRAILING_STOP...)
    try:
        symbol_normalized = symbol.replace('/', '')  # BTCUSDT thay vì BTC/USDT
        algo_orders = exchange.fapiPrivateGetAlgoOpenOrders({'symbol': symbol_normalized})
        
        if 'orders' in algo_orders and algo_orders['orders']:
            for order in algo_orders['orders']:
                try:
                    algo_id = order.get('algoId')
                    algo_type = order.get('algoType', 'N/A')
                    
                    if algo_id:
                        # Hủy algo order bằng API đặc biệt
                        cancel_result = exchange.fapiPrivateDeleteAlgoOrder({
                            'symbol': symbol_normalized,
                            'algoId': algo_id
                        })
                        
                        total_cancelled += 1
                        print(f"✅ Hủy Algo order (Conditional) {algo_id} [{algo_type}] kết quả: {cancel_result}", flush=True)
                        logger.info(f"Đã hủy Algo order {algo_id} [{algo_type}] cho {symbol}")
                except Exception as e:
                    logger.error(f"Lỗi khi hủy Algo order {order.get('algoId', 'N/A')}: {e}")
    except Exception as e:
        logger.error(f"Lỗi khi lấy/hủy Algo orders cho {symbol}: {e}")
    
    # Thông báo
    if total_cancelled > 0:
        msg = f"✅ Đã hủy {total_cancelled} lệnh chờ theo lịch: {symbol} (bao gồm cả Conditional orders)"
        telegram_factory.send_tele(msg, cst.chat_id, True, True)
        print(f"🧹 Tổng cộng đã hủy {total_cancelled} lệnh cho {symbol}", flush=True)
    else:
        print(f"ℹ️  Không có lệnh mở nào cho {symbol}", flush=True)

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'enableRateLimit': True,  
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {
        'defaultType': 'future' 
    }
})
exchange.setSandboxMode(False)


import gg_sheet_factory
from datetime import datetime

def my_function():
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{current_time}] Hàm đang chạy...", flush=True)
        logger.info(f"[{current_time}] Bắt đầu cancel orders theo lịch")
        
        for symbol in gg_sheet_factory.get_cho_va_khop("A3:A100"):
            if symbol and len(symbol) > 0 and "USDT" in str(symbol[0]):
                print(f"cancel: {symbol[0]}", flush=True)
                cancel_all_open_orders(symbol[0])
    except Exception as e:
        print(f"Lỗi trong my_function: {e}", flush=True)
        logger.error(f"Lỗi trong my_function: {e}", exc_info=True)
    

# Thay thế schedule bằng logic đơn giản với time.sleep
print(f"Bắt đầu chạy...{cst.cancel_orders_minutes} phút một lần")
logger.info(f"Khởi động cancel orders scheduler - chạy mỗi {cst.cancel_orders_minutes} phút")

# Chạy ngay lần đầu
my_function()

# Sau đó chạy theo interval
while True:
    try:
        time.sleep(cst.cancel_orders_minutes * 60)  # Chuyển phút thành giây
        my_function()
    except Exception as e:
        print(f"Lỗi trong vòng lặp cancel orders: {e}", flush=True)
        logger.error(f"Lỗi trong vòng lặp cancel orders: {e}", exc_info=True)
        time.sleep(60)  # Chờ 1 phút trước khi thử lại
