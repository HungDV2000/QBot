"""
Tracking 30 Price Levels - Module tracking 30 mức giá gần nhất cho lệnh đã đặt
Chạy mỗi 1 phút để cập nhật giá cho các mã đang ở trạng thái "Chờ" hoặc "Khớp"
"""

import ccxt
import logging
import time
from datetime import datetime
from typing import Dict, List
import cst
import gg_sheet_factory
from data_collector import get_data_collector
import os

file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

# Setup logging
logging.basicConfig(
    filename='hd_track_30_prices.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Setup exchange
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

# Data collector
data_collector = get_data_collector(exchange)


class PriceTracker:
    """Tracking giá cho các mã đã đặt lệnh"""
    
    def __init__(self):
        self.tracked_symbols = {}  # {symbol: {'order_price': ..., 'filled_price': ..., 'prices': []}}
    
    def get_symbols_with_orders(self) -> List[Dict]:
        """
        Lấy danh sách các mã đang có lệnh (Chờ hoặc Khớp)
        
        Returns:
            List[Dict]: Danh sách với keys: symbol, state, order_price, filled_price
        """
        result = []
        
        try:
            # Đọc từ sheet Order (LONG section)
            long_data = gg_sheet_factory.get_dat_lenh("A55:G104")
            for idx, row in enumerate(long_data):
                if len(row) > 0 and row[0]:  # Có symbol
                    symbol = row[0]
                    state = row[3] if len(row) > 3 else ""  # Cột D: Mã lệnh hiện tại
                    
                    # Chỉ track nếu đang có lệnh (1a, 1b, 1c, 2a...)
                    if state and len(state) >= 2:
                        order_price = float(row[6]) if len(row) > 6 and row[6] else 0.0  # Cột G: Giá vào
                        filled_price = order_price if "a" in state else 0.0  # Nếu là entry (1a, 2a) thì có filled price
                        
                        result.append({
                            'symbol': symbol,
                            'state': state,
                            'order_price': order_price,
                            'filled_price': filled_price,
                            'row_num': 55 + idx
                        })
            
            # Đọc từ sheet Order (SHORT section)
            short_data = gg_sheet_factory.get_dat_lenh("A4:G53")
            for idx, row in enumerate(short_data):
                if len(row) > 0 and row[0]:
                    symbol = row[0]
                    state = row[3] if len(row) > 3 else ""
                    
                    if state and len(state) >= 2:
                        order_price = float(row[6]) if len(row) > 6 and row[6] else 0.0
                        filled_price = order_price if "a" in state else 0.0
                        
                        result.append({
                            'symbol': symbol,
                            'state': state,
                            'order_price': order_price,
                            'filled_price': filled_price,
                            'row_num': 4 + idx
                        })
            
            logger.info(f"Tìm thấy {len(result)} mã đang có lệnh")
            return result
            
        except Exception as e:
            logger.error(f"Lỗi lấy danh sách mã có lệnh: {e}")
            return []
    
    def track_prices(self):
        """Track và cập nhật 30 mức giá cho các mã có lệnh"""
        logger.info(f"=== Bắt đầu tracking 30 prices - {datetime.now()} ===")
        
        symbols_with_orders = self.get_symbols_with_orders()
        
        for item in symbols_with_orders:
            symbol = item['symbol']
            row_num = item['row_num']
            
            try:
                # Lấy 30 mức giá gần nhất
                price_data = data_collector.get_30_recent_prices(symbol)
                
                if price_data:
                    # Chuẩn bị dữ liệu để ghi vào sheet
                    # Giả sử cột H trở đi dùng để lưu 30 mức giá
                    # H = price 1, I = price 2, ..., AK = price 30 (30 cột)
                    
                    prices_only = [p['price'] for p in price_data[-30:]]  # Lấy tối đa 30 giá gần nhất
                    
                    # Pad nếu không đủ 30
                    while len(prices_only) < 30:
                        prices_only.insert(0, "")
                    
                    # Update vào sheet (cột H:AK tương ứng 30 prices)
                    # Sử dụng update_multi với array_index là row_num
                    gg_sheet_factory.update_multi(
                        gg_sheet_factory.tab_dat_lenh,
                        row_num,
                        [prices_only],
                        "H"  # Bắt đầu từ cột H
                    )
                    
                    logger.info(f"✅ Đã update 30 prices cho {symbol} tại hàng {row_num}")
                else:
                    logger.warning(f"Không lấy được price data cho {symbol}")
                    
            except Exception as e:
                logger.error(f"Lỗi tracking prices cho {symbol}: {e}")
                continue
        
        logger.info(f"=== Hoàn thành tracking 30 prices ===\n")


def do_it():
    """Main loop"""
    tracker = PriceTracker()
    tracker.track_prices()


if __name__ == "__main__":
    logger.info("🚀 Khởi động module Track 30 Prices")
    
    while True:
        try:
            do_it()
        except Exception as e:
            logger.error(f"Tổng lỗi: {e}")
        
        # Sleep 1 phút
        logger.info(f"Ngủ {cst.delay_track_30_prices if hasattr(cst, 'delay_track_30_prices') else 60}s...")
        time.sleep(getattr(cst, 'delay_track_30_prices', 60))

