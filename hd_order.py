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

# Cải thiện logging
logging.basicConfig(
    filename='hd_order.log', 
    level=logging.INFO,  # Thay đổi từ ERROR sang INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Khởi tạo order helper
order_helper = BinanceOrderHelper(exchange)

def is_same_pair(sym1, sym2):
    sym1 = sym1.replace("/", "").upper().strip()
    sym2 = sym2.replace("/", "").upper().strip()
    if sym1 == sym2 :
       print(sym1, sym2)
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



def is_opened_order_1(sym):
    
    balance = exchange.fetch_balance()
    positions = balance['info']['positions']
    for position in positions:
        
        symbol = position['symbol']
        if(is_same_pair(symbol,sym) and float(position['positionAmt']) !=0):
            print(position)
            return True
    
    orders = exchange.fetch_open_orders(symbol=sym)
    
    
    

    if(len(orders)>0):
        return True
  
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
  logger.info(f"{datetime.now()}. Scan Vào Lệnh----------------------------------------------------")

  # Đọc trạng thái hệ thống - Support cả C1 (mới) và B2 (cũ) để backward compatible
  try:
    c1_value = gg_sheet_factory.get_dat_lenh("C1:C1")[0][0].strip().upper()
    state_value = c1_value  # Ưu tiên C1
    logger.info(f"Đọc trạng thái từ C1: {state_value}")
  except (IndexError, KeyError):
    # Fallback sang B2 nếu C1 không có
    try:
      b2_value = gg_sheet_factory.get_dat_lenh("B2:B2")[0][0].strip().upper()
      state_value = b2_value
      logger.info(f"Fallback: Đọc trạng thái từ B2: {state_value}")
    except:
      state_value = STATE_CHO
      logger.warning("Không đọc được trạng thái, mặc định CHỜ")
  
  # Đọc vốn mặc định (support cả cũ và mới)
  try:
    e2_value = gg_sheet_factory.get_dat_lenh("E2:E2")[0][0].strip().upper()
  except:
    e2_value = "0"
    logger.warning("Không đọc được vốn mặc định từ E2")
  
  logger.info(f"Trạng thái: {state_value}, Vốn mặc định: {e2_value}")

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

    don_bay = gg_sheet_factory.get_dat_lenh(f"A{start_row}:Z{end_row}")
    logger.info(f"Scan {state_value} từ hàng {start_row} đến {end_row}")
    for d in don_bay:
        
        
        
      
      
      
      
      
    

      # Hỗ trợ cả cấu trúc cũ và mới:
      # Cũ: B=leverage, C=callback, D=activation, H=capital
      # Mới: J=leverage, K=callback, L=activation, O=capital
      
      # Thử đọc từ cấu trúc mới (index 9,10,11,14 = J,K,L,O)
      try:
        leverage_idx = 9 if len(d) > 9 and is_number(d[9]) else 1
        callback_idx = 10 if len(d) > 10 and is_number(d[10]) else 2
        activation_idx = 11 if len(d) > 11 and is_number(d[11]) else 3
        capital_idx = 14 if len(d) > 14 and is_number(d[14]) else 7
      except:
        # Fallback sang cũ
        leverage_idx, callback_idx, activation_idx, capital_idx = 1, 2, 3, 7
      
      if d[leverage_idx] != "N" and is_number(d[leverage_idx]) and is_number(d[activation_idx]):

        try:
            sym = d[0]
            
            if is_opened_order_1(sym):
                logger.info(f"{sym} Đã vào lệnh, bỏ qua")
                continue
        
            # Detect order type từ cột I (index 8) nếu có
            order_type_str = ""
            try:
                if len(d) > 8 and d[8] and str(d[8]).strip():
                    order_type_str = str(d[8]).strip().upper()
            except:
                pass
            
            # Default to TRAILING STOP nếu không có
            if not order_type_str or "TRAILING" in order_type_str:
                order_type_str = "TRAILING_STOP"
            
            logger.info(f"--- Vào lệnh 1 {state_value}: {d[0]} {order_type_str} đòn bẩy: {d[leverage_idx]}")

            capitalMoney = float(e2_value)
            try:
                capitalMoney = float(d[capital_idx])
            except (ValueError, TypeError, IndexError) as e:
                logger.warning(f"Không đọc được vốn từ cột {capital_idx}, dùng mặc định: {e}")

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
                leverage = int(d[leverage_idx])
                if(leverage>0):
                    exchange.setLeverage (leverage, symbol)
                    logger.info(f"Đã thiết lập đòn bẩy {leverage} cho cặp giao dịch {symbol}")
            except Exception as e:
                logger.warning(f"Không thể set leverage: {e}")
                leverage = 1
                
            # Tính amount
            ticker =exchange.fetch_ticker(symbol)
            lastPrice=ticker["last"]
            amountUsdt=float(capitalMoney)
            amount =amountUsdt/lastPrice
            
            # Tạo lệnh theo loại
            order = None
            if "TRAILING" in order_type_str or "TRAILING_STOP" in order_type_str:
                # TRAILING STOP
                activation_price = round(float(d[activation_idx].replace("%", "")), binance_utils.get_price_precision(symbol))
                callback_rate = float(d[callback_idx].replace("%", ""))
                
                logger.info(f"Tạo Trailing Stop: {symbol} {side} @ {activation_price}, callback={callback_rate}%")
                order = order_helper.create_trailing_stop_order(
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    activation_price=activation_price,
                    callback_rate=callback_rate,
                    reduce_only=False
                )
                msg = f"✅ <b>LỆNH CHỜ (TRAILING STOP)</b>\n\n<b>Mã:</b> {symbol}\n<b>Side:</b> {type}\n<b>Giá kích hoạt:</b> {activation_price}\n<b>Callback:</b> {callback_rate}%\n<b>Đòn bẩy:</b> {leverage}x\n<b>Vốn:</b> {capitalMoney} USDT"
                
            elif "STOP_LIMIT" in order_type_str or "STOP LIMIT" in order_type_str:
                # STOP LIMIT
                # Cột M = stop_price (index 12), Cột N = limit_price (index 13)
                stop_price_idx = 12
                limit_price_idx = 13
                
                stop_price = round(float(d[stop_price_idx].replace("%", "")), binance_utils.get_price_precision(symbol))
                limit_price = round(float(d[limit_price_idx].replace("%", "")), binance_utils.get_price_precision(symbol))
                
                logger.info(f"Tạo Stop Limit: {symbol} {side} @ stop={stop_price}, limit={limit_price}")
                order = order_helper.create_stop_limit_order(
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    stop_price=stop_price,
                    limit_price=limit_price,
                    reduce_only=False
                )
                msg = f"✅ <b>LỆNH CHỜ (STOP LIMIT)</b>\n\n<b>Mã:</b> {symbol}\n<b>Side:</b> {type}\n<b>Stop Price:</b> {stop_price}\n<b>Limit Price:</b> {limit_price}\n<b>Đòn bẩy:</b> {leverage}x\n<b>Vốn:</b> {capitalMoney} USDT"
                
            elif "LIMIT" in order_type_str:
                # LIMIT
                # Cột N = limit_price (index 13)
                limit_price_idx = 13
                limit_price = round(float(d[limit_price_idx].replace("%", "")), binance_utils.get_price_precision(symbol))
                
                logger.info(f"Tạo Limit: {symbol} {side} @ {limit_price}")
                order = order_helper.create_limit_order(
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    limit_price=limit_price,
                    reduce_only=False
                )
                msg = f"✅ <b>LỆNH CHỜ (LIMIT)</b>\n\n<b>Mã:</b> {symbol}\n<b>Side:</b> {type}\n<b>Limit Price:</b> {limit_price}\n<b>Đòn bẩy:</b> {leverage}x\n<b>Vốn:</b> {capitalMoney} USDT"
                
            else:
                # MARKET (fallback)
                logger.info(f"Tạo Market: {symbol} {side}")
                order = order_helper.create_market_order(
                    symbol=symbol,
                    side=side,
                    amount=amount,
                    reduce_only=False
                )
                msg = f"✅ <b>LỆNH KHỚP NGAY (MARKET)</b>\n\n<b>Mã:</b> {symbol}\n<b>Side:</b> {type}\n<b>Giá:</b> Market\n<b>Đòn bẩy:</b> {leverage}x\n<b>Vốn:</b> {capitalMoney} USDT"
            
            if order:
                printf(symbol, order)
                logger.info(f"✅ Lệnh {order_type_str} đã được tạo: {order}")
                telegram_factory.send_tele(msg, cst.chat_id, True, True)

            
            
        except Exception as e:
            print(f"Một lỗi đã xảy ra: {e}")
      start_row += 1

def printf(name,data):
    print(data)
    pathDir=str(Path().absolute()).replace("\\","/")
    filename=pathDir+"/order/"+str(name)+"/"+str(data['info']['orderId'])+".txt"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    f = open(filename, "w")
    f.write(str(data))
    f.close()    

while True:
    try:
        do_it()
        
    except Exception as e:
        print("Tổng Lỗi:", e)
        logging.error("Tổng lỗi: %s", str(e))

    time.sleep(cst.delay_vao_lenh)
