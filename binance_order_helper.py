"""
Binance Order Helper - Xử lý các loại lệnh với fallback an toàn
[FIX FINAL v4]: Tuân thủ chính xác tài liệu Algo Order (Conditional)
- Trailing Stop: Dùng Algo API (Conditional)
- SL/TP khác: Dùng Standard API (đang hoạt động tốt)
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
        Tạo lệnh Trailing Stop: Dùng Algo Order API với thông số chuẩn theo tài liệu Conditional Order.
        """
        logger.info(f"Tạo Trailing Stop: {symbol} {side} {amount} @ {activation_price}, callback={callback_rate}%")
        
        try:
            logger.info("🚀 Đang gửi lệnh qua Algo Order API (CONDITIONAL)...")
            order = self._create_trailing_stop_algo_api(
                symbol, side, amount, activation_price, callback_rate, reduce_only
            )
            logger.info(f"✅ Tạo lệnh Trailing Stop thành công (Algo API): ClientID {order.get('id')}")
            return order
            
        except Exception as e_algo:
            logger.error(f"❌ Algo API thất bại: {e_algo}")
            logger.warning("⚠️ Đang thử fallback sang Standard API (CCXT)...")
            
            # Fallback: Thử phương thức CCXT Standard (endpoint /order)
            try:
                # Standard API dùng 'activationPrice' (có đuôi ion)
                str_activation_price = format(Decimal(str(activation_price)), 'f')
                params = {
                    'activationPrice': str_activation_price,
                    'callbackRate': callback_rate,
                }
                if reduce_only:
                    params['reduceOnly'] = True

                order = self.exchange.create_order(
                    symbol=symbol,
                    type='TRAILING_STOP_MARKET',
                    side=side,
                    amount=amount,
                    price=activation_price, 
                    params=params
                )
                logger.info(f"✅ Tạo lệnh Trailing Stop thành công (Fallback CCXT): Order ID {order.get('id')}")
                return order
            except Exception as e_std:
                logger.error(f"❌ Cả 2 phương thức đều thất bại. Lỗi CCXT: {e_std}")
                raise e_std
    
    def _create_trailing_stop_algo_api(
        self,
        symbol: str,
        side: str,
        amount: float,
        activation_price: float,
        callback_rate: float,
        reduce_only: bool
    ) -> Dict:
        """
        [FIXED BASED ON DOCS]:
        - Endpoint: /fapi/v1/algoOrder
        - algoType: 'CONDITIONAL' (Bắt buộc)
        - type: 'TRAILING_STOP_MARKET' (Loại lệnh)
        - activatePrice: (Tên param chuẩn cho Algo, KHÔNG có chữ 'ion')
        """
        binance_symbol = symbol.replace('/', '')
        
        # Cấu trúc params chuẩn theo tài liệu bạn cung cấp
        params = {
            'symbol': binance_symbol,
            'side': side.upper(),
            'algoType': 'CONDITIONAL',       # <--- FIX 1: Phải là CONDITIONAL
            'type': 'TRAILING_STOP_MARKET',  # <--- FIX 2: Loại lệnh nằm ở đây
            'quantity': amount,
            # <--- FIX 3: Dùng 'activatePrice' (không có 'ion') theo tài liệu Algo
            'activatePrice': format(Decimal(str(activation_price)), 'f'),
            'callbackRate': callback_rate,
            'workingType': 'CONTRACT_PRICE'
        }
        
        if reduce_only:
            # Lưu ý: Tài liệu Algo thường yêu cầu reduceOnly là STRING "true"/"false"
            params['reduceOnly'] = 'true'
        
        logger.info(f"📤 Payload gửi đi (Algo API): {params}")
        
        # Gọi Algo Order API
        response = self.exchange.fapiPrivatePostAlgoOrder(params)
        
        # Map response về format chung
        return {
            'id': response.get('clientAlgoId'),
            'orderId': response.get('clientAlgoId'),
            'info': response,
            'symbol': symbol,
            'type': 'TRAILING_STOP_MARKET',
            'side': side,
            'amount': amount,
            'status': 'NEW'
        }
    
    def create_stop_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        stop_price: float,
        limit_price: float,
        reduce_only: bool = False
    ) -> Dict:
        """
        Tạo lệnh Stop Limit (Giữ nguyên Standard API vì đang hoạt động tốt)
        """
        logger.info(f"Tạo Stop Limit: {symbol} {side} {amount} @ stop={stop_price}, limit={limit_price}")
        
        params = {
            'stopPrice': stop_price,
        }
        
        if reduce_only:
            params['reduceOnly'] = True
        
        try:
            # Sử dụng Standard Order endpoint (/fapi/v1/order) thông qua CCXT
            # type='STOP' tương ứng với Stop Limit trên Futures
            order = self.exchange.create_order(
                symbol=symbol,
                type='STOP',
                side=side,
                amount=amount,
                price=limit_price,
                params=params
            )
            logger.info(f"✅ Tạo lệnh Stop Limit thành công: Order ID {order.get('id')}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi tạo lệnh Stop Limit: {e}")
            raise e
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        limit_price: float,
        reduce_only: bool = False
    ) -> Dict:
        """Tạo lệnh Limit"""
        logger.info(f"Tạo Limit: {symbol} {side} {amount} @ {limit_price}")
        
        params = {}
        if reduce_only:
            params['reduceOnly'] = True
        
        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type='LIMIT',
                side=side,
                amount=amount,
                price=limit_price,
                params=params
            )
            logger.info(f"✅ Tạo lệnh Limit thành công: Order ID {order.get('id')}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi tạo lệnh Limit: {e}")
            raise e
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        amount: float,
        reduce_only: bool = False
    ) -> Dict:
        """Tạo lệnh Market"""
        logger.info(f"Tạo Market: {symbol} {side} {amount}")
        
        params = {}
        if reduce_only:
            params['reduceOnly'] = True
        
        try:
            order = self.exchange.create_order(
                symbol=symbol,
                type='MARKET',
                side=side,
                amount=amount,
                params=params
            )
            logger.info(f"✅ Tạo lệnh Market thành công: Order ID {order.get('id')}")
            return order
            
        except Exception as e:
            logger.error(f"❌ Lỗi khi tạo lệnh Market: {e}")
            raise e


def cancel_all_open_orders_with_retry(
    exchange: ccxt.binance,
    symbol: str,
    max_retries: int = 3,
    delay: int = 2
) -> Tuple[bool, int]:
    """Hủy tất cả lệnh chờ với retry mechanism"""
    import time
    
    logger.info(f"Bắt đầu hủy tất cả lệnh chờ cho {symbol}...")
    
    for attempt in range(max_retries):
        try:
            open_orders = exchange.fetch_open_orders(symbol)
            
            if not open_orders:
                logger.info(f"✅ Không còn lệnh chờ cho {symbol}")
                return True, 0
            
            logger.info(f"Phát hiện {len(open_orders)} lệnh chờ, đang hủy... (Lần {attempt + 1}/{max_retries})")
            
            failed_orders = []
            for order in open_orders:
                try:
                    exchange.cancel_order(order['id'], symbol)
                    logger.debug(f"Đã hủy lệnh {order['id']}")
                except Exception as e:
                    logger.warning(f"Không thể hủy lệnh {order['id']}: {e}")
                    failed_orders.append(order['id'])
            
            time.sleep(delay)
            remaining_orders = exchange.fetch_open_orders(symbol)
            
            if len(remaining_orders) == 0:
                logger.info(f"✅ Xác nhận: Đã xóa sạch tất cả lệnh cho {symbol}")
                return True, 0
            else:
                logger.warning(f"⚠️ Còn {len(remaining_orders)} lệnh sót sau lần {attempt + 1}")
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi hủy lệnh (lần {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return False, -1 
    
    try:
        remaining = exchange.fetch_open_orders(symbol)
        logger.critical(f"🔴 NGHIÊM TRỌNG: Không thể xóa {len(remaining)} lệnh cho {symbol} sau {max_retries} lần thử!")
        return False, len(remaining)
    except:
        return False, -1


# Singleton instance
_helper_instance = None

def get_order_helper(exchange: ccxt.binance) -> BinanceOrderHelper:
    global _helper_instance
    if _helper_instance is None:
        _helper_instance = BinanceOrderHelper(exchange)
    return _helper_instance