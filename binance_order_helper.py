"""
Binance Order Helper - Xử lý các loại lệnh với fallback an toàn
Giải quyết lỗi API -4120 khi Binance thay đổi endpoint cho Trailing Stop
"""

import ccxt
import logging
from decimal import Decimal
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


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
        Tạo lệnh Trailing Stop với fallback sang Algo Order API nếu cần
        
        Args:
            symbol: Cặp giao dịch (VD: 'BTC/USDT')
            side: 'buy' hoặc 'sell'
            amount: Số lượng
            activation_price: Giá kích hoạt
            callback_rate: Tỷ lệ callback (%)
            reduce_only: True nếu là lệnh reduce only
            
        Returns:
            Dict: Thông tin lệnh đã tạo
            
        Raises:
            Exception: Nếu cả 2 phương thức đều thất bại
        """
        logger.info(f"Tạo Trailing Stop: {symbol} {side} {amount} @ {activation_price}, callback={callback_rate}%")
        
        # Chuẩn bị params
        params = {
            'activationPrice': format(Decimal(str(activation_price)), 'f'),
            'callbackRate': callback_rate,
        }
        
        if reduce_only:
            params['reduceOnly'] = True
        
        # Thử phương thức 1: Standard API (ccxt)
        try:
            logger.debug("Thử tạo lệnh bằng standard API...")
            order = self.exchange.create_order(
                symbol=symbol,
                type='TRAILING_STOP_MARKET',
                side=side,
                amount=amount,
                price=None,
                params=params
            )
            logger.info(f"✅ Tạo lệnh Trailing Stop thành công (standard API): Order ID {order.get('id')}")
            return order
            
        except ccxt.ExchangeError as e:
            error_str = str(e)
            
            # Kiểm tra có phải lỗi -4120 không
            if '-4120' in error_str or 'Algo Order API' in error_str:
                logger.warning(f"⚠️ Lỗi -4120 phát hiện, chuyển sang Algo Order API...")
                
                # Thử phương thức 2: Algo Order API
                try:
                    order = self._create_trailing_stop_algo_api(
                        symbol, side, amount, activation_price, callback_rate, reduce_only
                    )
                    logger.info(f"✅ Tạo lệnh Trailing Stop thành công (Algo API): Order ID {order.get('orderId')}")
                    return order
                    
                except Exception as e2:
                    logger.error(f"❌ Algo Order API cũng thất bại: {e2}")
                    raise Exception(f"Không thể tạo lệnh Trailing Stop: Standard API failed (-4120), Algo API failed: {e2}")
            else:
                # Lỗi khác, không phải -4120
                logger.error(f"❌ Lỗi khi tạo lệnh Trailing Stop: {e}")
                raise e
    
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
        Tạo lệnh Trailing Stop qua Algo Order API (Binance mới)
        
        Returns:
            Dict: Response từ Binance Algo Order API
        """
        # Chuẩn bị symbol cho Binance API (loại bỏ '/')
        binance_symbol = symbol.replace('/', '')
        
        # Chuẩn bị params cho Algo Order API
        params = {
            'symbol': binance_symbol,
            'side': side.upper(),
            'quantity': amount,
            'type': 'TRAILING_STOP_MARKET',
            'activationPrice': format(Decimal(str(activation_price)), 'f'),
            'callbackRate': callback_rate,
        }
        
        if reduce_only:
            params['reduceOnly'] = 'true'
        
        logger.debug(f"Algo Order API params: {params}")
        
        # Gọi Algo Order API
        response = self.exchange.fapiPrivatePostAlgoOrder(params)
        
        # Convert response để tương thích với ccxt format
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
        Tạo lệnh Stop Limit
        
        Args:
            symbol: Cặp giao dịch
            side: 'buy' hoặc 'sell'
            amount: Số lượng
            stop_price: Giá stop
            limit_price: Giá limit
            reduce_only: True nếu là lệnh reduce only
            
        Returns:
            Dict: Thông tin lệnh đã tạo
        """
        logger.info(f"Tạo Stop Limit: {symbol} {side} {amount} @ stop={stop_price}, limit={limit_price}")
        
        params = {
            'stopPrice': stop_price,
        }
        
        if reduce_only:
            params['reduceOnly'] = True
        
        try:
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
        """
        Tạo lệnh Limit
        
        Args:
            symbol: Cặp giao dịch
            side: 'buy' hoặc 'sell'
            amount: Số lượng
            limit_price: Giá limit
            reduce_only: True nếu là lệnh reduce only
            
        Returns:
            Dict: Thông tin lệnh đã tạo
        """
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
        """
        Tạo lệnh Market
        
        Args:
            symbol: Cặp giao dịch
            side: 'buy' hoặc 'sell'
            amount: Số lượng
            reduce_only: True nếu là lệnh reduce only
            
        Returns:
            Dict: Thông tin lệnh đã tạo
        """
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
    """
    Hủy tất cả lệnh chờ với retry mechanism
    
    Args:
        exchange: CCXT exchange instance
        symbol: Symbol để hủy lệnh
        max_retries: Số lần retry tối đa
        delay: Delay giữa các lần retry (giây)
        
    Returns:
        Tuple[success, remaining_orders]: (True/False, số lệnh còn sót)
    """
    import time
    
    logger.info(f"Bắt đầu hủy tất cả lệnh chờ cho {symbol}...")
    
    for attempt in range(max_retries):
        try:
            # Lấy danh sách lệnh chờ
            open_orders = exchange.fetch_open_orders(symbol)
            
            if not open_orders:
                logger.info(f"✅ Không còn lệnh chờ cho {symbol}")
                return True, 0
            
            logger.info(f"Phát hiện {len(open_orders)} lệnh chờ, đang hủy... (Lần {attempt + 1}/{max_retries})")
            
            # Hủy từng lệnh
            failed_orders = []
            for order in open_orders:
                try:
                    exchange.cancel_order(order['id'], symbol)
                    logger.debug(f"Đã hủy lệnh {order['id']}")
                except Exception as e:
                    logger.warning(f"Không thể hủy lệnh {order['id']}: {e}")
                    failed_orders.append(order['id'])
            
            # Delay trước khi verify
            time.sleep(delay)
            
            # Verify: Kiểm tra lại
            remaining_orders = exchange.fetch_open_orders(symbol)
            
            if len(remaining_orders) == 0:
                logger.info(f"✅ Xác nhận: Đã xóa sạch tất cả lệnh cho {symbol}")
                return True, 0
            else:
                logger.warning(f"⚠️ Còn {len(remaining_orders)} lệnh sót sau lần {attempt + 1}")
                
                # Nếu đây là lần cuối, log chi tiết
                if attempt == max_retries - 1:
                    for order in remaining_orders:
                        logger.error(f"Lệnh sót: ID={order['id']}, Type={order.get('type')}, Side={order.get('side')}")
                
        except Exception as e:
            logger.error(f"❌ Lỗi khi hủy lệnh (lần {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                return False, -1  # -1 nghĩa là không biết số lệnh còn lại
    
    # Sau max_retries vẫn còn lệnh sót
    try:
        remaining = exchange.fetch_open_orders(symbol)
        logger.critical(f"🔴 NGHIÊM TRỌNG: Không thể xóa {len(remaining)} lệnh cho {symbol} sau {max_retries} lần thử!")
        return False, len(remaining)
    except:
        return False, -1


# Singleton instance (tùy chọn)
_helper_instance = None

def get_order_helper(exchange: ccxt.binance) -> BinanceOrderHelper:
    """
    Get singleton instance của BinanceOrderHelper
    """
    global _helper_instance
    if _helper_instance is None:
        _helper_instance = BinanceOrderHelper(exchange)
    return _helper_instance

