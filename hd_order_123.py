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
import binance_utils
import telegram_factory
from binance_order_helper import BinanceOrderHelper
from cascade_manager import CascadeManager, get_cascade_manager
from order_state_tracker import OrderStateTracker, get_tracker
from notification_manager import NotificationManager, get_notification_manager

file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

# Cải thiện logging với timestamp
logging.basicConfig(
    filename='hd_order_123.log', 
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Order logger (ghi vào order.log chung)
order_logger = logging.getLogger('order')
order_logger.setLevel(logging.INFO)
order_handler = logging.FileHandler('order.log')
order_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
order_logger.addHandler(order_handler)

STATE_SHORT = "SHORT"
STATE_LONG  = "LONG"
def getLenh23Rate(symbol, state):
    
    if state == STATE_LONG:
        start_row = 55
        end_row = 104

    elif state == STATE_SHORT:
        start_row = 4
        end_row = 53
    sheet_dat_lenh = gg_sheet_factory.get_dat_lenh(f"A{start_row}:G{end_row}")
    
    for d in sheet_dat_lenh:
        try:
            sym = d[0]
            lenh2_rate = float(d[5])
            lenh3_rate = float(d[6])
            
            if(is_same_pair(symbol, sym)):
                return symbol, lenh2_rate, lenh3_rate
            

        except Exception as e:
            
            pass


    
    if state == STATE_LONG:
        return symbol, cst.lenh2_rate_long, cst.lenh3_rate_long
    elif state == STATE_SHORT:
         return symbol, cst.lenh2_rate_short, cst.lenh3_rate_short
    


def is_same_pair(sym1, sym2):
    sym1 = sym1.replace("/", "").upper().strip()
    sym2 = sym2.replace("/", "").upper().strip()
    if sym1 == sym2 :
       print(sym1, sym2)
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
    
def count_decmial_places(number):
    
    number_str = str(number)
    if '.' in number_str:
        return len(number_str.split('.')[1])
    return 0
  
def do_it():
    logger.info(f"{datetime.now()}. Scan Vào Lệnh 123----------------------------------------------------")
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
    
    # Khởi tạo order helper, cascade manager và notification manager
    order_helper = BinanceOrderHelper(exchange)
    cascade_mgr = get_cascade_manager(exchange, order_helper)
    notif_mgr = get_notification_manager(cst.chat_id)
    balance = exchange.fetch_balance()
    positions = balance['info']['positions']
    for position in positions:
        try:
            
            symbol = position['symbol']
            
            
            amount = float(position['positionAmt'])
            if amount !=0:
                print(f"Vị thế: {position}", flush=True)
                orders = exchange.fetch_open_orders(symbol=symbol)
                tong_so_lenh_dang_mo = len(orders)
                
                if tong_so_lenh_dang_mo == 0:
                    # Position mới khớp, chưa có SL/TP
                    symbol = symbol.replace("USDT", "/USDT")
                    
                    position_amt = float(position['positionAmt'])
                    entry_price = float(position['entryPrice'])
                    is_short = position_amt < 0
                    is_long = position_amt > 0
                    leverage = int(position['leverage'])
                    
                    side = STATE_LONG if is_long else STATE_SHORT
                    
                    # Lấy config rate
                    sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, side)
                    logger.info(f"Config cho {symbol}: lenh2rate={lenh2rate}, lenh3rate={lenh3rate}")

                    # Sử dụng cascade manager để tạo SL + TP tự động
                    # Layer 1 vì đây là entry đầu tiên
                    try:
                        result = cascade_mgr.on_entry_filled(
                            symbol=symbol,
                            layer_num=1,
                            entry_price=entry_price,
                            leverage=leverage,
                            position_amt=position_amt,
                            side=side,
                            max_layers=3,  # TODO: Đọc từ sheet
                            lenh2_rate=lenh2rate,
                            lenh3_rate=lenh3rate,
                            lenh3_callback_rate=cst.lenh3_callback_rate,
                            next_layer_config=None  # TODO: Implement lớp 2
                        )
                        
                        # Gửi thông báo thành công
                        sl_order = result.get('sl_order')
                        tp_order = result.get('tp_order')
                        
                        if sl_order and tp_order:
                            # Track state vào Google Sheet
                            tracker = get_tracker(side)
                            start_row = 55 if side == STATE_LONG else 4
                            
                            tracker.update_order_filled(
                                symbol=symbol,
                                order_code="1a",  # Entry lớp 1
                                order_type=f"Entry {side}",
                                leverage=leverage,
                                entry_price=entry_price,
                                order_id=f"POS-{symbol}",  # Position tracking
                                start_row=start_row,
                                end_row=start_row + 49
                            )
                            
                            # Log vào order.log
                            order_logger.info(f"LỆNH 2 (SL) | {symbol} | {side} | Entry: {entry_price} | SL Rate: {lenh2rate} | Order ID: {sl_order.get('id', 'N/A')}")
                            order_logger.info(f"LỆNH 3 (TP) | {symbol} | {side} | Entry: {entry_price} | TP Rate: {lenh3rate} | Callback: {cst.lenh3_callback_rate}% | Order ID: {tp_order.get('id', 'N/A')}")
                            
                            msg = f"✅ <b>ĐÃ TẠO SL + TP CHO LỚP 1</b>\n\n<b>Mã:</b> {symbol}\n<b>Entry Price:</b> {entry_price}\n<b>Leverage:</b> {leverage}x\n<b>SL Order:</b> {sl_order.get('id')}\n<b>TP Order:</b> {tp_order.get('id')}"
                            telegram_factory.send_tele(msg, cst.chat_id, True, True)
                            logger.info(f"✅ Cascade lớp 1 hoàn tất cho {symbol}")
                        else:
                            logger.warning(f"⚠️ Cascade lớp 1 không hoàn toàn: SL={sl_order is not None}, TP={tp_order is not None}")
                            
                    except Exception as e:
                        logger.error(f"❌ Lỗi cascade lớp 1 cho {symbol}: {e}")
                        msg = f"🚨 <b>LỖI TẠO SL/TP</b>\n\n<b>Mã:</b> {symbol}\n<b>Lỗi:</b> {str(e)}"
                        telegram_factory.send_tele(msg, cst.chat_id, True, True)
                        

                        
                        
                        
                        

                        
                        

                        
                        
                                
                        
                        
                        
                        
                        
                        

                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        

                        
                        


        except Exception as e:
            print(f"Một lỗi đã xảy ra: {e}", flush=True)
            logger.error(f"Lỗi xử lý position {symbol}: {e}", exc_info=True)
            import traceback
            traceback.print_exc()






while True:
    try:
        do_it()
        
        
    except Exception as e:
        print(f"Tổng Lỗi: {e}", flush=True)
        logger.error(f"Tổng lỗi: {e}", exc_info=True)
        import traceback
        traceback.print_exc()

    time.sleep(cst.delay_vao_lenh_123)




