import cst
from enum import Enum
import gg_sheet_factory
import threading
import logging
import subprocess
import time
import os
import ccxt
from datetime import datetime
import utils
import binance_utils
import telegram_factory
from pathlib import Path
from binance_order_helper import BinanceOrderHelper, cancel_all_open_orders_with_retry

file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

# Cải thiện logging với timestamp và UTF-8 encoding
logging.basicConfig(
    filename='hd_order.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# Tạo order logger riêng để track tất cả orders
order_logger = logging.getLogger('order')
order_logger.setLevel(logging.INFO)
order_handler = logging.FileHandler('order.log', encoding='utf-8')
order_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
order_logger.addHandler(order_handler)

exchange_id = 'binance'
exchange_class = getattr(ccxt, exchange_id)
exchange = exchange_class({
    'enableRateLimit': True,  
    'apiKey': cst.key_binance,
    'secret': cst.secret_binance,
    'options': {
        'defaultType': 'future',
        'warnOnFetchOpenOrdersWithoutSymbol': False  # Tắt warning để tránh exception
    }
})
exchange.setSandboxMode(False)

# Khởi tạo order helper
order_helper = BinanceOrderHelper(exchange)

def is_same_pair(sym1, sym2):
    sym1 = sym1.replace("/", "").upper().strip()
    sym2 = sym2.replace("/", "").upper().strip()
    if sym1 == sym2:
       return True
    return False


def cancel_all_open_orders(symbol):
    open_orders = exchange.fetch_open_orders(symbol)

    if open_orders:
        for order in open_orders:
            order_id = order['id']
            cancel_result = exchange.cancel_order(order_id, symbol)
            print(f"Hủy lệnh {order_id} kết quả: {cancel_result}")
            msg = f"Đã Hủy lệnh Chờ: {order['symbol']}"
            telegram_factory.send_tele(msg,cst.chat_id, True , True)
    else:
        print(f"Không có lệnh mở nào cho {symbol}")



def has_position(sym):
    """Kiểm tra symbol đã có vị thế (đã vào lệnh) chưa"""
    try:
    balance = exchange.fetch_balance()
        if not balance or 'info' not in balance:
            logger.warning(f"fetch_balance() trả về dữ liệu không hợp lệ cho {sym}")
            return False
        positions = balance['info'].get('positions', [])
    for position in positions:
            symbol = position.get('symbol', '')
            position_amt = position.get('positionAmt', '0')
            if is_same_pair(symbol, sym) and float(position_amt) != 0:
                return True
        return False
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra vị thế cho {sym}: {e}", exc_info=True)
        return False

def has_pending_trailing_stop_order(symbol):
    """
    Kiểm tra symbol đã có order TRAILING_STOP chưa (bất kể pending hay filled)
    Logic: Trùng lặp = cùng 1 mã có nhiều orders cùng loại trong 1 đợt đặt lệnh
    """
    try:
        # Sử dụng fetch_open_orders(symbol) để tránh rate limit và lấy orders cụ thể cho symbol
        symbol_orders = exchange.fetch_open_orders(symbol)
        
        if symbol_orders is None:
            logger.warning(f"fetch_open_orders({symbol}) trả về None")
            return False
        
        if not symbol_orders:
            return False
        
        # Đếm số lượng TRAILING_STOP orders cho symbol này
        # Logic theo test_check_conditional_orders.py: TRAILING_STOP nếu có 'trailing' trong order_type hoặc algoType = 'VP'
        trailing_stop_count = 0
        trailing_stop_details = []
        
        for order in symbol_orders:
            # Lấy thông tin từ order
            info = order.get('info', {})
            order_id = order.get('id', 'N/A')
            algo_id = info.get('algoId', None)
            order_type = order.get('type', '')
            algo_type = info.get('algoType', None)
            activate_price = info.get('activatePrice', None)
            callback_rate = info.get('callbackRate', None)
            price_rate = info.get('priceRate', None)
            
            # Kiểm tra TRAILING_STOP (theo logic test_check_conditional_orders.py):
            # TRAILING_STOP nếu có 'trailing' trong order_type hoặc algoType = 'VP'
            is_trailing_stop = (
                'trailing' in str(order_type).lower() or
                algo_type == 'VP'
            )
            
            if is_trailing_stop:
                trailing_stop_count += 1
                trailing_stop_details.append({
                    'order_id': order_id,
                    'algo_id': algo_id,
                    'order_type': order_type,
                    'algo_type': algo_type,
                    'activation': activate_price,
                    'callback': callback_rate if callback_rate is not None else price_rate,
                    'status': order.get('status', 'N/A')
                })
        
        # Nếu có ít nhất 1 TRAILING_STOP order = đã có order (tránh trùng lặp)
        if trailing_stop_count > 0:
            detail_str = ", ".join([f"Order ID: {d['order_id']}, Type: {d['order_type']}, Status: {d['status']}" 
                                   for d in trailing_stop_details])
            logger.info(f"✅ {symbol} đã có {trailing_stop_count} TRAILING_STOP order(s) - {detail_str}")
            print(f"⏭️  {symbol} đã có {trailing_stop_count} lệnh TRAILING_STOP, bỏ qua", flush=True)
        return True
  
    return False
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra order pending cho {symbol}: {e}", exc_info=True)
        # Khi có lỗi, return False để không block việc đặt lệnh (sẽ tự fail nếu duplicate)
        return False

def execute_command(commands):
    try:
        
        subprocess.run(commands, shell=True, check=True)
    except Exception as e:
        print(e)

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
    
STATE_STOP = "STOP"
STATE_SHORT = "SHORT"
STATE_LONG  = "LONG"
STATE_CHO  = "CHỜ"
LENH_CHO = "LỆNH CHỜ"

def do_it():
  print(f"{datetime.now()}. Scan Vào Lệnh----------------------------------------------------", flush=True)
  logger.info(f"{datetime.now()}. Scan Vào Lệnh----------------------------------------------------")

  # Đọc trạng thái hệ thống từ B2 (theo quy trình thực tế)
  try:
    state_value = gg_sheet_factory.get_dat_lenh("B2:B2")[0][0].strip().upper()
    print(f"📌 Trạng thái: {state_value}", flush=True)
    logger.info(f"Đọc trạng thái từ B2: {state_value}")
  except (IndexError, KeyError):
      state_value = STATE_CHO
    print(f"⚠️ Không đọc được trạng thái B2, mặc định CHỜ", flush=True)
    logger.warning("Không đọc được trạng thái từ B2, mặc định CHỜ")
  
  # Đọc vốn mặc định từ E2
  e2_value = "0"
  try:
    raw_value = gg_sheet_factory.get_dat_lenh("E2:E2")[0][0].strip()
    # Kiểm tra giá trị có phải là lỗi Excel/Sheets không (#DIV/0!, #N/A, #ERROR!, etc.)
    if raw_value.startswith("#") or not is_number(raw_value):
      print(f"⚠️ Giá trị E2 không hợp lệ: '{raw_value}', dùng mặc định 100", flush=True)
      logger.warning(f"Giá trị E2 không hợp lệ: '{raw_value}', dùng mặc định 100")
      e2_value = "100"
    else:
      # Thử convert để đảm bảo là số hợp lệ
      try:
        test_float = float(raw_value)
        if test_float <= 0:
          print(f"⚠️ Giá trị E2 <= 0: '{raw_value}', dùng mặc định 100", flush=True)
          logger.warning(f"Giá trị E2 <= 0: '{raw_value}', dùng mặc định 100")
          e2_value = "100"
        else:
          e2_value = raw_value
          print(f"💰 Vốn mặc định: {e2_value} USDT", flush=True)
          logger.info(f"Vốn mặc định từ E2: {e2_value}")
      except (ValueError, TypeError):
        print(f"⚠️ Không thể convert E2 '{raw_value}' sang số, dùng mặc định 100", flush=True)
        logger.warning(f"Không thể convert E2 '{raw_value}' sang số, dùng mặc định 100")
        e2_value = "100"
  except Exception as e:
    print(f"⚠️ Không đọc được vốn E2: {e}, mặc định 100", flush=True)
    logger.warning(f"Không đọc được vốn mặc định từ E2: {e}")
    e2_value = "100"

  if state_value == STATE_STOP:
    logger.warning("🛑 LỆNH STOP ĐƯỢC KÍCH HOẠT!")
    msg = "🛑 <b>LỆNH STOP KÍCH HOẠT</b>\n\n<b>Trạng thái:</b> Đang xử lý..."
    telegram_factory.send_tele(msg, cst.chat_id, True, True)
    
    # Đóng tất cả vị thế
    positions = exchange.fetch_positions()
    closed_positions = 0
    
    for position in positions:
        if float(position['info']['positionAmt']) != 0:
            symbol = position['symbol']
            amount = float(position['info']['positionAmt'])
            if amount != 0:
                try:
                    if amount > 0:
                        order = exchange.create_market_sell_order(symbol, amount)
                        logger.info(f"✅ Đã đóng vị thế LONG cho {symbol}: {order}")
                    elif amount < 0:
                        order = exchange.create_market_buy_order(symbol, abs(amount))
                        logger.info(f"✅ Đã đóng vị thế SHORT cho {symbol}: {order}")
                    closed_positions += 1
                except Exception as e:
                    logger.error(f"❌ Lỗi khi đóng vị thế {symbol}: {e}")
    
    # Hủy tất cả lệnh chờ
    try:
        all_open_orders = exchange.fetch_open_orders()
        cancelled_orders = 0
        for order in all_open_orders:
            try:
                exchange.cancel_order(order['id'], order['symbol'])
                cancelled_orders += 1
            except Exception as e:
                logger.error(f"Lỗi hủy lệnh {order['id']}: {e}")
        
        msg = f"✅ <b>HOÀN TẤT STOP</b>\n\n<b>Vị thế đã đóng:</b> {closed_positions}\n<b>Lệnh đã hủy:</b> {cancelled_orders}\n<b>Thời gian:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        telegram_factory.send_tele(msg, cst.chat_id, True, True)
        logger.warning("✅ Hoàn tất lệnh STOP")
    except Exception as e:
        logger.critical(f"🔴 Lỗi nghiêm trọng khi thực hiện STOP: {e}")

  elif state_value == "XÓA CHỜ":
    logger.info("🔄 Thực hiện lệnh XÓA CHỜ - Hủy tất cả lệnh pending, giữ vị thế")
    
    try:
        all_open_orders = exchange.fetch_open_orders()
        cancelled_count = 0
        
        for order in all_open_orders:
            try:
                exchange.cancel_order(order['id'], order['symbol'])
                cancelled_count += 1
                logger.info(f"Đã hủy lệnh {order['id']} cho {order['symbol']}")
            except Exception as e:
                logger.error(f"Lỗi hủy lệnh {order['id']}: {e}")
        
        msg = f"✅ <b>ĐÃ HỦY TẤT CẢ LỆNH CHỜ</b>\n\n<b>Số lệnh đã hủy:</b> {cancelled_count}\n<b>Vị thế:</b> Giữ nguyên\n<b>Thời gian:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        telegram_factory.send_tele(msg, cst.chat_id, True, True)
        logger.info(f"✅ Đã hủy {cancelled_count} lệnh chờ")
        
    except Exception as e:
        logger.error(f"❌ Lỗi khi thực hiện XÓA CHỜ: {e}")
        msg = f"🚨 <b>LỖI XÓA CHỜ</b>\n\n<b>Lỗi:</b> {str(e)}"
        telegram_factory.send_tele(msg, cst.chat_id, True, True)

  elif state_value == "XÓA VỊ THẾ":
    logger.info("🔄 Thực hiện lệnh XÓA VỊ THẾ - Đóng tất cả positions, giữ lệnh chờ")
    
    try:
        positions = exchange.fetch_positions()
        closed_count = 0
        
        for position in positions:
            if float(position['info']['positionAmt']) != 0:
                symbol = position['symbol']
                amount = float(position['info']['positionAmt'])
                
                try:
                    if amount > 0:
                        order = exchange.create_market_sell_order(symbol, amount)
                        logger.info(f"Đã đóng vị thế LONG: {symbol}")
                    elif amount < 0:
                        order = exchange.create_market_buy_order(symbol, abs(amount))
                        logger.info(f"Đã đóng vị thế SHORT: {symbol}")
                    closed_count += 1
                except Exception as e:
                    logger.error(f"Lỗi đóng vị thế {symbol}: {e}")
        
        msg = f"✅ <b>ĐÃ ĐÓNG TẤT CẢ VỊ THẾ</b>\n\n<b>Số vị thế đã đóng:</b> {closed_count}\n<b>Lệnh chờ:</b> Giữ nguyên\n<b>Thời gian:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        telegram_factory.send_tele(msg, cst.chat_id, True, True)
        logger.info(f"✅ Đã đóng {closed_count} vị thế")
        
    except Exception as e:
        logger.error(f"❌ Lỗi khi thực hiện XÓA VỊ THẾ: {e}")
        msg = f"🚨 <b>LỖI XÓA VỊ THẾ</b>\n\n<b>Lỗi:</b> {str(e)}"
        telegram_factory.send_tele(msg, cst.chat_id, True, True)

  elif state_value == STATE_CHO:
    print("💤 Trạng thái CHỜ - Không làm gì...", flush=True)
    logger.info("Trạng thái CHỜ - Không làm gì...")
  else:
    
    if state_value == STATE_LONG:
      start_row = 55
      end_row = 104
      type = "BUY"

    elif state_value == STATE_SHORT:
      start_row = 4
      end_row = 53
      type = "SHORT"

    don_bay = gg_sheet_factory.get_dat_lenh(f"A{start_row}:H{end_row}")  # Chỉ cần đọc A-H
    print(f"🔍 Scan {state_value} từ hàng {start_row} đến {end_row}", flush=True)
    logger.info(f"Scan {state_value} từ hàng {start_row} đến {end_row}")
    
    print(f"📊 Đã đọc được {len(don_bay)} dòng từ sheet", flush=True)
    logger.info(f"Đã đọc được {len(don_bay)} dòng từ sheet")
    
    row_count = 0
    for d in don_bay:
        row_count += 1
        print(f"📝 Đang xử lý dòng {row_count}/{len(don_bay)}", flush=True)
        # Cấu trúc CỐ ĐỊNH: A=Symbol, B=Leverage, C=Callback, D=Activation, H=Capital
        # Chỉ hỗ trợ TRAILING_STOP
        leverage_idx = 1    # Cột B
        callback_idx = 2    # Cột C
        activation_idx = 3  # Cột D
        capital_idx = 7     # Cột H
        
        # Validation: B ≠ "N" và B ≠ 0 và B là số hợp lệ
        if len(d) <= leverage_idx or not d[leverage_idx]:
            logger.debug(f"Dòng {row_count}: Không có leverage (cột B), bỏ qua")
            continue
            
        leverage_value = str(d[leverage_idx]).strip()
        
        # Kiểm tra leverage hợp lệ
        if leverage_value == "N" or leverage_value == "0":
            logger.debug(f"Dòng {row_count}: Leverage = '{leverage_value}' (N hoặc 0), bỏ qua")
            continue
        
        if not is_number(leverage_value):
            logger.debug(f"Dòng {row_count}: Leverage = '{leverage_value}' không phải số, bỏ qua")
            continue
            
        try:
            lev_float = float(leverage_value)
            if lev_float <= 0:
                logger.debug(f"Dòng {row_count}: Leverage = {lev_float} <= 0, bỏ qua")
                continue
        except (ValueError, TypeError):
            logger.debug(f"Dòng {row_count}: Lỗi convert leverage '{leverage_value}' sang float, bỏ qua")
            continue
        
        # Kiểm tra activation là số hợp lệ
        if len(d) <= activation_idx or not d[activation_idx]:
            logger.debug(f"Dòng {row_count}: Không có activation price (cột D), bỏ qua")
            continue
        if not is_number(d[activation_idx]):
            logger.debug(f"Dòng {row_count}: Activation price không phải số, bỏ qua")
            continue

        try:
            if len(d) == 0 or not d[0]:
                logger.debug(f"Dòng {row_count}: Không có symbol (cột A), bỏ qua")
                continue
                
            sym = d[0]
            
            # Validate symbol
            if not sym or not str(sym).strip():
                logger.debug(f"Dòng {row_count}: Symbol rỗng, bỏ qua")
                continue
            
            sym = str(sym).strip()
            
            # Bước 1: Kiểm tra symbol đã có VỊ THẾ (đã vào lệnh) chưa
            print(f"🔍 [{row_count}] Kiểm tra vị thế cho {sym}...", flush=True)
            try:
                if has_position(sym):
                    print(f"⏭️  {sym} đã có vị thế, bỏ qua", flush=True)
                    logger.info(f"{sym} Đã có vị thế, bỏ qua")
                    continue
            except Exception as e:
                print(f"⚠️  Lỗi khi kiểm tra vị thế cho {sym}: {e}", flush=True)
                logger.error(f"Lỗi khi kiểm tra vị thế cho {sym}: {e}", exc_info=True)
                continue
        
            # Bước 2: Kiểm tra symbol đã có ORDER TRAILING_STOP pending chưa
            print(f"🔍 [{row_count}] Kiểm tra pending orders cho {sym}...", flush=True)
            try:
                if has_pending_trailing_stop_order(sym):
                    print(f"⏭️  {sym} đã có lệnh chờ TRAILING_STOP, bỏ qua", flush=True)
                    logger.info(f"{sym} Đã có lệnh chờ TRAILING_STOP, bỏ qua")
                    continue
            except Exception as e:
                print(f"⚠️  Lỗi khi kiểm tra pending orders cho {sym}: {e}", flush=True)
                logger.error(f"Lỗi khi kiểm tra pending orders cho {sym}: {e}", exc_info=True)
                continue
            
            print(f"🎯 Vào lệnh 1 {state_value}: {sym} (Leverage {d[leverage_idx]}x)", flush=True)
            logger.info(f"--- Vào lệnh 1 {state_value}: {sym} TRAILING_STOP đòn bẩy: {d[leverage_idx]}")

            # Đọc vốn từ cột H, nếu trống dùng E2
            try:
                capitalMoney = float(e2_value) if e2_value != "0" else 100
            except (ValueError, TypeError):
                print(f"⚠️ Không thể convert e2_value '{e2_value}' sang float, dùng mặc định 100", flush=True)
                logger.warning(f"Không thể convert e2_value '{e2_value}' sang float, dùng mặc định 100")
                capitalMoney = 100
            
            try:
                if len(d) > capital_idx and d[capital_idx]:
                    capital_str = str(d[capital_idx]).strip()
                    # Kiểm tra giá trị có phải là lỗi Excel/Sheets không
                    if capital_str and not capital_str.startswith("#") and is_number(capital_str):
                        capitalMoney = float(capital_str)
                        if capitalMoney <= 0:
                            logger.warning(f"Giá trị vốn từ cột H <= 0: {capitalMoney}, giữ nguyên e2_value")
                            capitalMoney = float(e2_value) if e2_value != "0" else 100
            except (ValueError, TypeError) as e:
                logger.debug(f"Không thể đọc vốn từ cột H: {e}, dùng e2_value")
                pass

            symbol = d[0]
            
            # Xác định side
            if type == "BUY":
                side = "buy"
            elif type == "SELL" or type == "SHORT":
                side = "sell"
            elif type == "COVER":
                side = "buy"

            # Set leverage
            try:
                leverage = int(float(d[leverage_idx]))
                if leverage > 0:
                    exchange.setLeverage(leverage, symbol)
                    logger.info(f"Đã thiết lập đòn bẩy {leverage} cho cặp giao dịch {symbol}")
            except Exception as e:
                print(f"⚠️ Không thể set leverage cho {symbol}: {e}", flush=True)
                logger.warning(f"Không thể set leverage: {e}")
                leverage = 1
                
            # Tính amount
            ticker = exchange.fetch_ticker(symbol)
            lastPrice = ticker["last"]
            amountUsdt = float(capitalMoney)
            amount = amountUsdt / lastPrice
            
            # CHỈ HỖ TRỢ TRAILING STOP (theo quy trình thực tế)
            activation_price_raw = float(str(d[activation_idx]).replace("%", ""))
            
            # Log giá trị raw trước khi làm tròn
            logger.info(f"[ACTIVATION PRICE] {symbol} - Giá gốc từ sheet: {activation_price_raw}")
            print(f"📊 {symbol} - Giá kích hoạt gốc: {activation_price_raw}", flush=True)
            
            # Validate activation_price > 0 TRƯỚC KHI làm tròn
            if activation_price_raw <= 0:
                print(f"⚠️  {symbol}: Activation price = {activation_price_raw} (phải > 0), bỏ qua", flush=True)
                logger.warning(f"{symbol}: Activation price = {activation_price_raw} (phải > 0), bỏ qua")
                continue
            
            # Sử dụng exchange.price_to_precision() để làm tròn đúng theo quy tắc Binance
            try:
                activation_price_str = exchange.price_to_precision(symbol, activation_price_raw)
                activation_price = float(activation_price_str)
                logger.info(f"[ACTIVATION PRICE] {symbol} - Sau khi price_to_precision(): {activation_price} (từ string: '{activation_price_str}')")
                print(f"📊 {symbol} - Giá sau khi làm tròn (price_to_precision): {activation_price}", flush=True)
            except Exception as e:
                # Fallback: dùng round nếu price_to_precision lỗi
                try:
                    precision = binance_utils.get_price_precision(symbol)
                    activation_price = round(activation_price_raw, precision)
                    logger.warning(f"Sử dụng round() fallback cho {symbol}: {e}")
                except Exception as e2:
                    print(f"⚠️  {symbol}: Không thể làm tròn activation price: {e2}, bỏ qua", flush=True)
                    logger.error(f"{symbol}: Không thể làm tròn activation price: {e2}", exc_info=True)
                    continue
            
            # Validate activation_price > 0 SAU KHI làm tròn (có thể bị làm tròn thành 0 nếu quá nhỏ)
            if activation_price <= 0:
                print(f"⚠️  {symbol}: Activation price sau khi làm tròn = {activation_price} (phải > 0), bỏ qua. Giá gốc: {activation_price_raw}", flush=True)
                logger.warning(f"{symbol}: Activation price sau khi làm tròn = {activation_price} (phải > 0), bỏ qua. Giá gốc: {activation_price_raw}")
                continue
            
            callback_rate = float(str(d[callback_idx]).replace("%", ""))
                
            print(f"📤 Tạo Trailing Stop: {symbol} {side} @ {activation_price}, callback={callback_rate}%", flush=True)
                logger.info(f"Tạo Trailing Stop: {symbol} {side} @ {activation_price}, callback={callback_rate}%")
            
                order = order_helper.create_trailing_stop_order(
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    activation_price=activation_price,
                    callback_rate=callback_rate,
                    reduce_only=False
                )
            
            # Log chi tiết order data để debug
            logger.info(f"[ORDER DATA] {symbol} - Order structure: id={order.get('id', 'N/A')}, symbol={order.get('symbol', 'N/A')}, side={order.get('side', 'N/A')}, status={order.get('status', 'N/A')}")
            if 'info' in order and isinstance(order['info'], dict):
                info_keys = list(order['info'].keys())
                logger.info(f"[ORDER DATA] {symbol} - info keys: {info_keys}")
                if 'algoId' in order['info']:
                    logger.info(f"[ORDER DATA] {symbol} - algoId: {order['info']['algoId']}")
                if 'activatePrice' in order['info']:
                    logger.info(f"[ORDER DATA] {symbol} - activatePrice from info: {order['info']['activatePrice']}")
                if 'callbackRate' in order['info']:
                    logger.info(f"[ORDER DATA] {symbol} - callbackRate from info: {order['info']['callbackRate']}")
                if 'algoStatus' in order['info']:
                    logger.info(f"[ORDER DATA] {symbol} - algoStatus: {order['info']['algoStatus']}")
            
                msg = f"✅ <b>LỆNH CHỜ (TRAILING STOP)</b>\n\n<b>Mã:</b> {symbol}\n<b>Side:</b> {type}\n<b>Giá kích hoạt:</b> {activation_price}\n<b>Callback:</b> {callback_rate}%\n<b>Đòn bẩy:</b> {leverage}x\n<b>Vốn:</b> {capitalMoney} USDT"
                
            # Log vào order.log
            order_logger.info(f"LỆNH 1 (Entry) | {symbol} | {type} | Activation: {activation_price} | Callback: {callback_rate}% | Leverage: {leverage}x | Capital: {capitalMoney} USDT | Order ID: {order.get('id', 'N/A')}")
            
            printf(symbol, order)
            print(f"✅ Đã tạo lệnh TRAILING_STOP cho {symbol}", flush=True)
            logger.info(f"✅ Lệnh TRAILING_STOP đã được tạo thành công cho {symbol} (Order ID: {order.get('id', 'N/A')})")
            telegram_factory.send_tele(msg, cst.chat_id, True, True)

        except Exception as e:
            print(f"❌ Lỗi xử lý dòng {row_count} (symbol: {sym if 'sym' in locals() else 'N/A'}): {e}", flush=True)
            logger.error(f"Lỗi khi xử lý dòng {row_count}: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            continue
    
    print(f"✅ Hoàn thành scan {state_value} - Đã xử lý {row_count} dòng", flush=True)
    logger.info(f"Hoàn thành scan {state_value} - Đã xử lý {row_count} dòng")

def printf(name, data):
    """Lưu thông tin order vào file"""
    try:
        print(data, flush=True)
        pathDir = str(Path().absolute()).replace("\\", "/")
        
        # Tìm order ID từ nhiều nguồn có thể (theo thứ tự ưu tiên)
        order_id = None
        
        # Ưu tiên 1: data['id'] (CCXT standard)
        if 'id' in data:
            order_id = str(data['id'])
        
        # Ưu tiên 2: data['info']['algoId'] (Binance algo orders)
        elif 'info' in data and isinstance(data['info'], dict):
            if 'algoId' in data['info']:
                order_id = str(data['info']['algoId'])
            elif 'orderId' in data['info']:
                order_id = str(data['info']['orderId'])
            elif 'id' in data['info']:
                order_id = str(data['info']['id'])
            elif 'order_id' in data['info']:
                order_id = str(data['info']['order_id'])
        
        # Nếu không tìm thấy order ID, dùng timestamp
        if not order_id:
            order_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            logger.warning(f"Không tìm thấy order ID trong response cho {name}, dùng timestamp: {order_id}")
        
        filename = pathDir + "/order/" + str(name) + "/" + str(order_id) + ".txt"
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Ghi file với UTF-8 encoding
        with open(filename, "w", encoding='utf-8') as f:
            f.write(str(data))
            
        except Exception as e:
        logger.error(f"Lỗi trong printf() cho {name}: {e}", exc_info=True)
        print(f"⚠️ Lỗi khi lưu order file cho {name}: {e}", flush=True)    

print(f"🚀 Khởi động bot - Chạy mỗi {cst.delay_vao_lenh} giây", flush=True)
logger.info(f"Khởi động bot - Chạy mỗi {cst.delay_vao_lenh} giây")

while True:
    try:
        do_it()
        print(f"⏳ Chờ {cst.delay_vao_lenh} giây trước lần scan tiếp theo...", flush=True)
        
    except Exception as e:
        print(f"❌ Tổng Lỗi: {e}", flush=True)
        logger.error(f"Tổng lỗi: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        print(f"⏳ Chờ {cst.delay_vao_lenh} giây trước khi thử lại...", flush=True)

    time.sleep(cst.delay_vao_lenh)
