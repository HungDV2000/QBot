"""
Binance Order Helper - Xử lý các loại lệnh với fallback an toàn
Giải quyết lỗi API -4120 khi Binance thay đổi endpoint cho Trailing Stop
"""

import ccxt
import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple
import os
import sys
from datetime import datetime

# --- CẤU HÌNH LOGGING RA FILE binance_order_helper.txt ---
log_filename = "binance_order_helper.txt"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    try:
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        print(f"📝 [LOG HELPER] Đã kết nối file log: {log_filename}", flush=True)
    except Exception as e:
        print(f"⚠️ [LOG ERROR] Không thể mở file log helper: {e}", flush=True)


class BinanceOrderHelper:
    """Helper class để tạo lệnh Binance với xử lý lỗi tốt hơn"""
    
    def __init__(self, exchange: ccxt.binance):
        self.exchange = exchange
    
    def create_trailing_stop_order(
        self, 
        symbol: str, 
        side: str, 
        amount: float, 
        activation_price: float,
        callback_rate: float,
        reduce_only: bool = False
    ) -> Dict:
        """
        Tạo lệnh Trailing Stop: Dùng DIRECT RAW API (/fapi/v1/order) để đảm bảo activationPrice không bị mất.
        """
        logger.info(f"Tạo Trailing Stop: {symbol} {side} {amount} @ {activation_price}, callback={callback_rate}%")
        
        # [FIX FINAL]: Dùng fapiPrivatePostOrder (Endpoint chuẩn của Futures)
        # Bỏ qua wrapper của CCXT để tự kiểm soát payload
        try:
            # 1. Chuẩn bị Symbol (Bỏ dấu /)
            market_id = symbol.replace('/', '')
            
            # 2. Format giá về String chuẩn (tránh lỗi float)
            str_activation_price = format(Decimal(str(activation_price)), 'f')
            
            # 3. Payload chuẩn của Binance Futures API cho Trailing Stop
            # Tài liệu: https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
            params = {
                'symbol': market_id,
                'side': side.upper(),
                'type': 'TRAILING_STOP_MARKET',
                'quantity': amount,
                'activationPrice': str_activation_price, # QUAN TRỌNG NHẤT
                'callbackRate': callback_rate,           # NUMBER (0.1 - 5.0)
                'workingType': 'CONTRACT_PRICE'          # Kích hoạt theo giá đánh dấu hoặc giá gần nhất (thường là CONTRACT_PRICE)
            }
            
            if reduce_only:
                params['reduceOnly'] = 'true' # Raw API cần string 'true' hoặc boolean true tùy thư viện, gửi string cho chắc
            
            logger.info(f"🚀 [RAW API] Đang gửi lệnh: {params}")
            
            # 4. Gửi lệnh trực tiếp bằng hàm raw của CCXT (bypass logic wrapper)
            response = self.exchange.fapiPrivatePostOrder(params)
            
            logger.info(f"✅ Tạo lệnh Trailing Stop thành công: Order ID {response.get('orderId')}")
            
            # 5. Map lại thành format giống CCXT trả về để code khác không bị lỗi
            return {
                'id': str(response.get('orderId')),
                'info': response,
                'symbol': symbol,
                'status': 'open'
            }
            
        except Exception as e:
            logger.error(f"❌ [RAW API ERROR] Lỗi tạo Trailing Stop: {e}")
            # Nếu Raw API lỗi thì thực sự bó tay, throw exception để bot biết
            raise e
    
    # --- Các hàm khác giữ nguyên nhưng thêm log ---
    
    def create_stop_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        stop_price: float,
        limit_price: float,
        reduce_only: bool = False
    ) -> Dict:
        logger.info(f"Tạo Stop Limit: {symbol} {side} {amount} @ stop={stop_price}, limit={limit_price}")
        params = {'stopPrice': stop_price}
        if reduce_only: params['reduceOnly'] = True
        
        try:
            order = self.exchange.create_order(symbol, 'STOP', side, amount, limit_price, params)
            logger.info(f"✅ Tạo lệnh Stop Limit thành công: Order ID {order.get('id')}")
            return order
        except Exception as e:
            logger.error(f"❌ Lỗi Stop Limit: {e}")
            raise e
    
    def create_limit_order(self, symbol, side, amount, limit_price, reduce_only=False):
        logger.info(f"Tạo Limit: {symbol} {side} {amount} @ {limit_price}")
        params = {}
        if reduce_only: params['reduceOnly'] = True
        try:
            order = self.exchange.create_order(symbol, 'LIMIT', side, amount, limit_price, params)
            logger.info(f"✅ Tạo Limit thành công: {order.get('id')}")
            return order
        except Exception as e:
            logger.error(f"❌ Lỗi Limit: {e}")
            raise e
    
    def create_market_order(self, symbol, side, amount, reduce_only=False):
        logger.info(f"Tạo Market: {symbol} {side} {amount}")
        params = {}
        if reduce_only: params['reduceOnly'] = True
        try:
            order = self.exchange.create_order(symbol, 'MARKET', side, amount, params)
            logger.info(f"✅ Tạo Market thành công: {order.get('id')}")
            return order
        except Exception as e:
            logger.error(f"❌ Lỗi Market: {e}")
            raise e

def cancel_all_open_orders_with_retry(exchange, symbol, max_retries=3, delay=2):
    import time
    logger.info(f"Hủy lệnh chờ cho {symbol}...")
    for attempt in range(max_retries):
        try:
            open_orders = exchange.fetch_open_orders(symbol)
            if not open_orders: return True, 0
            
            for order in open_orders:
                try: exchange.cancel_order(order['id'], symbol)
                except: pass
            time.sleep(delay)
            
            if len(exchange.fetch_open_orders(symbol)) == 0:
                logger.info(f"✅ Đã hủy sạch lệnh {symbol}")
                return True, 0
        except: pass
    return False, -1

# Singleton instance
_helper_instance = None
def get_order_helper(exchange: ccxt.binance) -> BinanceOrderHelper:
    global _helper_instance
    if _helper_instance is None:
        _helper_instance = BinanceOrderHelper(exchange)
    return _helper_instance