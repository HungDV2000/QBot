"""
Cascade Manager - Quản lý logic cascade đa lớp cho QBot
Xử lý flow: 1a → 1b+1c+2a → 2b+2c+3a → ...
"""

import logging
import ccxt
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import gg_sheet_factory
import cst
import binance_utils

logger = logging.getLogger(__name__)


class OrderState:
    """Trạng thái lệnh"""
    WAITING = "CHỜ"         # Lệnh chờ khớp
    FILLED = "KHỚP"         # Lệnh đã khớp
    CANCELLED = "HỦY"       # Lệnh đã hủy
    FAILED = "LỖI"          # Lệnh lỗi


class LayerInfo:
    """Thông tin một lớp lệnh"""
    def __init__(self, layer_num: int, symbol: str):
        self.layer_num = layer_num
        self.symbol = symbol
        self.entry_order = None      # Order 'a' (1a, 2a, 3a...)
        self.sl_order = None          # Order 'b' (1b, 2b, 3b...)
        self.tp_order = None          # Order 'c' (1c, 2c, 3c...)
        self.entry_filled = False
        self.entry_price = None
        self.leverage = None
        self.position_amt = None


class CascadeManager:
    """Quản lý logic cascade đa lớp"""
    
    def __init__(self, exchange: ccxt.binance, order_helper):
        self.exchange = exchange
        self.order_helper = order_helper
        self.layers = {}  # {symbol: {layer_num: LayerInfo}}
    
    def get_or_create_layer(self, symbol: str, layer_num: int) -> LayerInfo:
        """Lấy hoặc tạo mới LayerInfo"""
        if symbol not in self.layers:
            self.layers[symbol] = {}
        
        if layer_num not in self.layers[symbol]:
            self.layers[symbol][layer_num] = LayerInfo(layer_num, symbol)
        
        return self.layers[symbol][layer_num]
    
    def on_entry_filled(
        self,
        symbol: str,
        layer_num: int,
        entry_price: float,
        leverage: int,
        position_amt: float,
        side: str,  # 'LONG' or 'SHORT'
        max_layers: int,
        lenh2_rate: float,
        lenh3_rate: float,
        lenh3_callback_rate: float,
        next_layer_config: Optional[Dict] = None
    ) -> Dict:
        """
        Xử lý khi lệnh entry (1a, 2a, 3a...) được khớp
        Tự động tạo SL + TP + Entry lớp tiếp theo
        
        Returns:
            Dict với keys: 'sl_order', 'tp_order', 'next_entry_order'
        """
        logger.info(f"🎯 Entry lớp {layer_num} đã khớp: {symbol} @ {entry_price}")
        
        # Lưu thông tin lớp
        layer = self.get_or_create_layer(symbol, layer_num)
        layer.entry_filled = True
        layer.entry_price = entry_price
        layer.leverage = leverage
        layer.position_amt = position_amt
        
        result = {
            'sl_order': None,
            'tp_order': None,
            'next_entry_order': None
        }
        
        # 1. Tạo Stop Loss (lệnh b: 1b, 2b, 3b...)
        try:
            sl_order = self._create_stop_loss(
                symbol, layer_num, entry_price, position_amt, 
                side, leverage, lenh2_rate
            )
            layer.sl_order = sl_order
            result['sl_order'] = sl_order
            logger.info(f"✅ Đã tạo SL lớp {layer_num}: Order ID {sl_order.get('id')}")
        except Exception as e:
            logger.error(f"❌ Lỗi tạo SL lớp {layer_num}: {e}")
        
        # 2. Tạo Take Profit (lệnh c: 1c, 2c, 3c...)
        try:
            tp_order = self._create_take_profit(
                symbol, layer_num, entry_price, position_amt,
                side, leverage, lenh3_rate, lenh3_callback_rate
            )
            layer.tp_order = tp_order
            result['tp_order'] = tp_order
            logger.info(f"✅ Đã tạo TP lớp {layer_num}: Order ID {tp_order.get('id')}")
        except Exception as e:
            logger.error(f"❌ Lỗi tạo TP lớp {layer_num}: {e}")
        
        # 3. Tạo Entry lớp tiếp theo (nếu chưa đạt max_layers)
        next_layer_num = layer_num + 1
        if next_layer_num <= max_layers and next_layer_config:
            try:
                next_entry = self._create_next_entry(
                    symbol, next_layer_num, side, next_layer_config
                )
                result['next_entry_order'] = next_entry
                logger.info(f"✅ Đã tạo Entry lớp {next_layer_num}: Order ID {next_entry.get('id')}")
            except Exception as e:
                logger.error(f"❌ Lỗi tạo Entry lớp {next_layer_num}: {e}")
        else:
            logger.info(f"⚠️ Không tạo lớp {next_layer_num} (max_layers={max_layers})")
        
        return result
    
    def _create_stop_loss(
        self,
        symbol: str,
        layer_num: int,
        entry_price: float,
        position_amt: float,
        side: str,
        leverage: int,
        lenh2_rate: float
    ) -> Dict:
        """Tạo lệnh Stop Loss (reduce only)"""
        is_long = (side == 'LONG')
        
        # Tính stop price
        if is_long:
            stop_price = entry_price * (1 - lenh2_rate / leverage)
            order_side = 'sell'
        else:
            stop_price = entry_price * (1 + lenh2_rate / leverage)
            order_side = 'buy'
        
        precision = binance_utils.get_price_precision(symbol)
        stop_price = round(stop_price, precision)
        limit_price = stop_price  # Stop Limit
        
        logger.info(f"Tạo SL {layer_num}{chr(97+1)}: {symbol} {order_side} @ {stop_price}")
        
        order = self.order_helper.create_stop_limit_order(
            symbol=symbol,
            side=order_side,
            amount=abs(position_amt),
            stop_price=stop_price,
            limit_price=limit_price,
            reduce_only=True
        )
        
        return order
    
    def _create_take_profit(
        self,
        symbol: str,
        layer_num: int,
        entry_price: float,
        position_amt: float,
        side: str,
        leverage: int,
        lenh3_rate: float,
        callback_rate: float
    ) -> Dict:
        """Tạo lệnh Take Profit (reduce only, trailing stop)"""
        is_long = (side == 'LONG')
        
        # Tính activation price
        if is_long:
            activation_price = entry_price * (1 + lenh3_rate / leverage)
            order_side = 'sell'
        else:
            activation_price = entry_price * (1 - lenh3_rate / leverage)
            order_side = 'buy'
        
        precision = binance_utils.get_price_precision(symbol)
        activation_price = round(activation_price, precision)
        
        logger.info(f"Tạo TP {layer_num}{chr(97+2)}: {symbol} {order_side} @ {activation_price}, callback={callback_rate}%")
        
        order = self.order_helper.create_trailing_stop_order(
            symbol=symbol,
            side=order_side,
            amount=abs(position_amt),
            activation_price=activation_price,
            callback_rate=callback_rate,
            reduce_only=True
        )
        
        return order
    
    def _create_next_entry(
        self,
        symbol: str,
        layer_num: int,
        side: str,
        config: Dict
    ) -> Dict:
        """Tạo lệnh Entry cho lớp tiếp theo"""
        # Đọc config cho lớp mới
        order_type = config.get('order_type', 'TRAILING_STOP')
        leverage = config.get('leverage', 10)
        callback_rate = config.get('callback_rate', 1.0)
        activation_price = config.get('activation_price')
        stop_price = config.get('stop_price')
        limit_price = config.get('limit_price')
        capital = config.get('capital', 100)
        
        # Set leverage
        try:
            self.exchange.setLeverage(leverage, symbol)
        except Exception as e:
            logger.warning(f"Không thể set leverage: {e}")
        
        # Tính amount
        ticker = self.exchange.fetch_ticker(symbol)
        last_price = ticker['last']
        amount = capital / last_price
        
        order_side = 'buy' if side == 'LONG' else 'sell'
        
        logger.info(f"Tạo Entry {layer_num}a: {symbol} {order_type} {order_side}")
        
        # Tạo lệnh theo loại
        if order_type == 'TRAILING_STOP':
            order = self.order_helper.create_trailing_stop_order(
                symbol=symbol,
                side=order_side,
                amount=amount,
                activation_price=activation_price,
                callback_rate=callback_rate,
                reduce_only=False
            )
        elif order_type == 'STOP_LIMIT':
            order = self.order_helper.create_stop_limit_order(
                symbol=symbol,
                side=order_side,
                amount=amount,
                stop_price=stop_price,
                limit_price=limit_price,
                reduce_only=False
            )
        elif order_type == 'LIMIT':
            order = self.order_helper.create_limit_order(
                symbol=symbol,
                side=order_side,
                amount=amount,
                limit_price=limit_price,
                reduce_only=False
            )
        else:  # MARKET
            order = self.order_helper.create_market_order(
                symbol=symbol,
                side=order_side,
                amount=amount,
                reduce_only=False
            )
        
        return order
    
    def on_tp_filled(self, symbol: str, layer_num: int) -> List[str]:
        """
        Xử lý khi Take Profit khớp
        Hủy SL cùng lớp + Entry lớp tiếp theo
        
        Returns:
            List các Order IDs đã hủy
        """
        logger.info(f"💰 TP lớp {layer_num} đã khớp: {symbol}")
        
        cancelled_orders = []
        
        # 1. Hủy SL cùng lớp
        try:
            layer = self.layers.get(symbol, {}).get(layer_num)
            if layer and layer.sl_order:
                sl_id = layer.sl_order.get('id')
                self.exchange.cancel_order(sl_id, symbol)
                cancelled_orders.append(f"{layer_num}b")
                logger.info(f"✅ Đã hủy SL {layer_num}b")
        except Exception as e:
            logger.error(f"❌ Lỗi hủy SL {layer_num}b: {e}")
        
        # 2. Hủy Entry lớp tiếp theo (nếu có)
        next_layer_num = layer_num + 1
        try:
            next_layer = self.layers.get(symbol, {}).get(next_layer_num)
            if next_layer and next_layer.entry_order and not next_layer.entry_filled:
                entry_id = next_layer.entry_order.get('id')
                self.exchange.cancel_order(entry_id, symbol)
                cancelled_orders.append(f"{next_layer_num}a")
                logger.info(f"✅ Đã hủy Entry {next_layer_num}a")
        except Exception as e:
            logger.error(f"❌ Lỗi hủy Entry {next_layer_num}a: {e}")
        
        return cancelled_orders
    
    def on_sl_filled(self, symbol: str, layer_num: int) -> List[str]:
        """
        Xử lý khi Stop Loss khớp
        Hủy TP cùng lớp, KHÔNG hủy Entry lớp tiếp theo
        
        Returns:
            List các Order IDs đã hủy
        """
        logger.info(f"🛑 SL lớp {layer_num} đã khớp: {symbol}")
        
        cancelled_orders = []
        
        # Hủy TP cùng lớp
        try:
            layer = self.layers.get(symbol, {}).get(layer_num)
            if layer and layer.tp_order:
                tp_id = layer.tp_order.get('id')
                self.exchange.cancel_order(tp_id, symbol)
                cancelled_orders.append(f"{layer_num}c")
                logger.info(f"✅ Đã hủy TP {layer_num}c")
        except Exception as e:
            logger.error(f"❌ Lỗi hủy TP {layer_num}c: {e}")
        
        # KHÔNG hủy Entry lớp tiếp theo - vẫn có thể entry lại
        logger.info(f"ℹ️ Giữ nguyên Entry lớp {layer_num + 1} (vẫn có thể entry)")
        
        return cancelled_orders
    
    def get_layer_info(self, symbol: str, layer_num: int) -> Optional[LayerInfo]:
        """Lấy thông tin một lớp"""
        return self.layers.get(symbol, {}).get(layer_num)
    
    def get_all_layers(self, symbol: str) -> Dict[int, LayerInfo]:
        """Lấy tất cả lớp của một symbol"""
        return self.layers.get(symbol, {})
    
    def clear_symbol(self, symbol: str):
        """Xóa tất cả tracking cho một symbol"""
        if symbol in self.layers:
            del self.layers[symbol]
            logger.info(f"🗑️ Đã xóa tracking cho {symbol}")
    
    def get_max_layer(self, symbol: str) -> int:
        """Lấy số lớp cao nhất đang active"""
        layers = self.layers.get(symbol, {})
        return max(layers.keys()) if layers else 0


# Singleton instance
_cascade_manager = None

def get_cascade_manager(exchange: ccxt.binance, order_helper) -> CascadeManager:
    """Get singleton instance"""
    global _cascade_manager
    if _cascade_manager is None:
        _cascade_manager = CascadeManager(exchange, order_helper)
    return _cascade_manager

