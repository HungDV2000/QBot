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
import os
import sys

# --- CẤU HÌNH LOGGING (GHI VÀO 1 FILE DUY NHẤT) ---
log_filename = "cascade_manager.txt"

# Cấu hình logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Kiểm tra handler để tránh duplicate log khi reload
if not logger.handlers:
    try:
        # mode='a': Append (Nối tiếp vào file cũ, không xóa log cũ)
        # encoding='utf-8': Hỗ trợ tiếng Việt
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        
        # Format: Năm-Tháng-Ngày Giờ:Phút:Giây - Mức độ - Nội dung
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        print(f"📝 [LOG] Đã kết nối file log: {log_filename}", flush=True)
    except Exception as e:
        print(f"⚠️ [LOG ERROR] Không thể mở file log: {e}", flush=True)


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
        
        # --- [LOG DEBUG CHI TIẾT VÀO FILE] ---
        logger.info(f"--------------------------------------------------")
        logger.info(f"📐 [TÍNH TOÁN STOP LOSS] {symbol} ({side})")
        logger.info(f"   - Entry Price: {entry_price}")
        logger.info(f"   - Tỷ lệ SL (lenh2_rate): {lenh2_rate}")
        
        # Tính stop price
        if is_long:
            stop_price_raw = entry_price * (1 - lenh2_rate)
            order_side = 'sell'
            logger.info(f"   - Công thức LONG: {entry_price} * (1 - {lenh2_rate}) = {stop_price_raw}")
        else:
            stop_price_raw = entry_price * (1 + lenh2_rate)
            order_side = 'buy'
            logger.info(f"   - Công thức SHORT: {entry_price} * (1 + {lenh2_rate}) = {stop_price_raw}")
        
        # Validate giá trước khi làm tròn
        if stop_price_raw <= 0:
            logger.error(f"   ❌ Lỗi: Giá SL tính ra <= 0 ({stop_price_raw})")
            raise ValueError(f"Stop price tính được = {stop_price_raw} (phải > 0). Entry: {entry_price}, Rate: {lenh2_rate}")
        
        # Làm tròn
        try:
            stop_price_str = self.exchange.price_to_precision(symbol, stop_price_raw)
            stop_price = float(stop_price_str)
            logger.info(f"   - Giá sau làm tròn (Final SL): {stop_price}")
        except Exception as e:
            try:
                precision = binance_utils.get_price_precision(symbol)
                if precision is None or precision < 0:
                    precision = 3
                stop_price = round(stop_price_raw, precision)
                logger.warning(f"   ⚠️ Dùng round() fallback: {stop_price} (Lỗi: {e})")
            except Exception as e2:
                raise ValueError(f"Không thể làm tròn stop_price cho {symbol}: {e2}")
        
        if stop_price <= 0:
            raise ValueError(f"Stop price sau khi làm tròn = {stop_price} (phải > 0). Giá gốc: {stop_price_raw}")
        
        limit_price = stop_price
        
        logger.info(f"   -> Đang gửi lệnh STOP_LIMIT {order_side} giá {stop_price}")
        
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
        
        # --- [LOG DEBUG CHI TIẾT VÀO FILE] ---
        logger.info(f"--------------------------------------------------")
        logger.info(f"📐 [TÍNH TOÁN TAKE PROFIT] {symbol} ({side})")
        logger.info(f"   - Entry Price: {entry_price}")
        logger.info(f"   - Tỷ lệ TP (lenh3_rate): {lenh3_rate}")
        
        # Tính activation price
        if is_long:
            activation_price_raw = entry_price * (1 + lenh3_rate)
            order_side = 'sell'
            logger.info(f"   - Công thức LONG: {entry_price} * (1 + {lenh3_rate}) = {activation_price_raw}")
        else:
            activation_price_raw = entry_price * (1 - lenh3_rate)
            order_side = 'buy'
            logger.info(f"   - Công thức SHORT: {entry_price} * (1 - {lenh3_rate}) = {activation_price_raw}")
        
        # Validate
        if activation_price_raw <= 0:
            logger.error(f"   ❌ Lỗi: Giá TP tính ra <= 0 ({activation_price_raw})")
            raise ValueError(f"Activation price tính được = {activation_price_raw} (phải > 0). Entry: {entry_price}, Rate: {lenh3_rate}")
        
        # Làm tròn
        try:
            activation_price_str = self.exchange.price_to_precision(symbol, activation_price_raw)
            activation_price = float(activation_price_str)
            logger.info(f"   - Giá sau làm tròn (Final TP): {activation_price}")
        except Exception as e:
            try:
                precision = binance_utils.get_price_precision(symbol)
                if precision is None or precision < 0:
                    precision = 3
                activation_price = round(activation_price_raw, precision)
                logger.warning(f"   ⚠️ Dùng round() fallback: {activation_price} (Lỗi: {e})")
            except Exception as e2:
                raise ValueError(f"Không thể làm tròn activation_price cho {symbol}: {e2}")
        
        if activation_price <= 0:
            raise ValueError(f"Activation price sau khi làm tròn = {activation_price} (phải > 0). Giá gốc: {activation_price_raw}")
        
        logger.info(f"   -> Đang gửi lệnh TRAILING_STOP {order_side} giá {activation_price}, callback {callback_rate}%")
        
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