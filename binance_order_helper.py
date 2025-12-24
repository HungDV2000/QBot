"""
Binance Order Helper - Xử lý các loại lệnh với fallback an toàn
Giải quyết lỗi API -4120 và lỗi mất ActivationPrice
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
        Tạo lệnh Trailing Stop: Sử dụng RAW API với tham số đã được chuẩn hóa String.
        """
        logger.info(f"Tạo Trailing Stop: {symbol} {side} {amount} @ {activation_price}, callback={callback_rate}%")
        
        try:
            # 1. CHUẨN HÓA DỮ LIỆU (QUAN TRỌNG NHẤT)
            # Binance yêu cầu số lượng và giá phải là String đúng precision của từng cặp coin
            # Nếu gửi float (vd: 409.00000001), Binance có thể từ chối hoặc lỗi
            market_id = symbol.replace('/', '')
            
            # Chuyển đổi sang string chuẩn theo quy định của sàn
            qty_str = self.exchange.amount_to_precision(symbol, amount)
            price_str = self.exchange.price_to_precision(symbol, activation_price)
            callback_str = str(callback_rate) # '1.0'
            
            # 2. Xây dựng Payload thủ công (Bỏ qua wrapper của CCXT để tránh lỗi map params)
            params = {
                'symbol': market_id,
                'side': side.upper(),
                'type': 'TRAILING_STOP_MARKET',
                'quantity': qty_str,           # Gửi String
                'activationPrice': price_str,  # Gửi String (Bắt buộc để không bị lỗi bằng Entry)
                'callbackRate': callback_str,  # Gửi String
                'workingType': 'CONTRACT_PRICE' 
            }
            
            if reduce_only:
                params['reduceOnly'] = 'true'
            
            logger.info(f"🚀 [RAW API] Đang gửi lệnh: {params}")
            
            # 3. Gửi lệnh trực tiếp vào endpoint /fapi/v1/order
            response = self.exchange.fapiPrivatePostOrder(params)
            
            logger.info(f"✅ Tạo lệnh Trailing Stop thành công: Order ID {response.get('orderId')}")
            
            # 4. Map lại format để code bên ngoài hiểu
            return {
                'id': str(response.get('orderId')),
                'info': response,
                'symbol': symbol,
                'status': 'open'
            }
            
        except Exception as e:
            logger.error(f"❌ [RAW API ERROR] Lỗi tạo Trailing Stop: {e}")
            # Nếu cách Raw này mà lỗi thì do tài khoản/network, throw để bot biết đường dừng
            raise e
    
    # --- CÁC HÀM KHÁC GIỮ NGUYÊN (Chỉ thêm chuẩn hóa log) ---
    
    def create_stop_limit_order(self, symbol, side, amount, stop_price, limit_price, reduce_only=False):
        logger.info(f"Tạo Stop Limit: {symbol} {side} {amount} @ stop={stop_price}")
        params = {'stopPrice': self.exchange.price_to_precision(symbol, stop_price)}
        if reduce_only: params['reduceOnly'] = True
        
        # Chuẩn hóa giá limit và amount
        limit_str = self.exchange.price_to_precision(symbol, limit_price)
        amount_str = self.exchange.amount_to_precision(symbol, amount)
        
        try:
            # Dùng ccxt standard cho lệnh thường (vì nó ổn định với lệnh cơ bản)
            order = self.exchange.create_order(symbol, 'STOP', side, amount_str, limit_str, params)
            logger.info(f"✅ Tạo lệnh Stop Limit thành công: Order ID {order.get('id')}")
            return order
        except Exception as e:
            logger.error(f"❌ Lỗi Stop Limit: {e}")
            raise e
    
    def create_limit_order(self, symbol, side, amount, limit_price, reduce_only=False):
        logger.info(f"Tạo Limit: {symbol} {side} {amount} @ {limit_price}")
        params = {}
        if reduce_only: params['reduceOnly'] = True
        
        limit_str = self.exchange.price_to_precision(symbol, limit_price)
        amount_str = self.exchange.amount_to_precision(symbol, amount)
        
        try:
            order = self.exchange.create_order(symbol, 'LIMIT', side, amount_str, limit_str, params)
            logger.info(f"✅ Tạo Limit thành công: {order.get('id')}")
            return order
        except Exception as e:
            logger.error(f"❌ Lỗi Limit: {e}")
            raise e
    
    def create_market_order(self, symbol, side, amount, reduce_only=False):
        logger.info(f"Tạo Market: {symbol} {side} {amount}")
        params = {}
        if reduce_only: params['reduceOnly'] = True
        
        amount_str = self.exchange.amount_to_precision(symbol, amount)
        
        try:
            order = self.exchange.create_order(symbol, 'MARKET', side, amount_str, params)
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