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
import requests
import hmac
import hashlib
import urllib.parse

file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

# Tạo tên file log với timestamp: hd_order_123_dd_mm_yyyy_h_m_s.log
log_timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
log_filename = f'hd_order_123_{log_timestamp}.log'

# Cải thiện logging với timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Tạo file handler với tên file động
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Order logger (ghi vào order.log chung)
order_logger = logging.getLogger('order')
order_logger.setLevel(logging.INFO)
order_handler = logging.FileHandler('order.log', encoding='utf-8')
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

def call_binance_api_direct(method, endpoint, params=None, api_key=None, secret_key=None):
    """
    Gọi Binance API trực tiếp bằng requests (để lấy algo orders)
    Tham khảo từ hd_order.py
    """
    base_url = 'https://fapi.binance.com'
    url = f"{base_url}{endpoint}"
    
    if params is None:
        params = {}
    
    if api_key is None:
        api_key = cst.key_binance
    if secret_key is None:
        secret_key = cst.secret_binance
    
    # Thêm timestamp
    params['timestamp'] = int(time.time() * 1000)
    
    # Tạo query string
    query_string = urllib.parse.urlencode(params)
    
    # Tạo signature
    signature = hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    
    # Headers
    headers = {
        'X-MBX-APIKEY': api_key
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Lỗi khi gọi Binance API trực tiếp: {e}")
        return None

def get_algo_orders_for_symbol(symbol):
    """
    Lấy algo orders cho một symbol cụ thể từ Binance API
    Dùng endpoint: /fapi/v1/allAlgoOrders (Query All Algo Orders)
    Trả về: List các algo orders (bao gồm CANCELED, FINISHED, NEW)
    """
    try:
        params = {
            'symbol': symbol.replace('/', '')
        }
        
        response = call_binance_api_direct('GET', '/fapi/v1/allAlgoOrders', params)
        
        if not response:
            return []
        
        # Binance trả về có thể là array hoặc dict
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            if 'data' in response:
                return response['data']
            elif response.get('code') == 200:
                return response
            else:
                logger.warning(f"Response có code khác 200 cho {symbol}: {response}")
                return []
        else:
            logger.warning(f"Response format không đúng cho {symbol}: {type(response)}")
            return []
            
    except Exception as e:
        logger.error(f"Lỗi khi lấy algo orders cho {symbol}: {e}", exc_info=True)
        return []

def has_sl_tp_orders(symbol, exchange):
    """
    Kiểm tra symbol đã có SL/TP orders chưa
    - SL: STOP_LIMIT order (reduceOnly=True)
    - TP: TRAILING_STOP order (reduceOnly=True hoặc algoType='CONDITIONAL')
    
    Trả về: (has_sl, has_tp)
    """
    try:
        # Lấy algo orders từ Binance API
        algo_orders = get_algo_orders_for_symbol(symbol)
        
        has_sl = False
        has_tp = False
        
        # Lọc orders có status=NEW (active)
        active_algo_orders = [o for o in algo_orders if o.get('algoStatus', '').upper() == 'NEW']
        
        for order in active_algo_orders:
            algo_type = order.get('algoType', '').upper()
            reduce_only = order.get('reduceOnly', False)
            
            # TP: TRAILING_STOP (algoType='CONDITIONAL' hoặc 'VP') và reduceOnly
            if algo_type in ['CONDITIONAL', 'VP'] and reduce_only:
                has_tp = True
                logger.debug(f"{symbol}: Tìm thấy TP order (algoType={algo_type})")
        
        # Lấy open orders thông thường (để check SL - STOP_LIMIT)
        try:
            open_orders = exchange.fetch_open_orders(symbol)
            for order in open_orders:
                order_type = order.get('type', '').upper()
                info = order.get('info', {})
                reduce_only = order.get('reduceOnly', False) or info.get('reduceOnly', False)
                
                # SL: STOP_LIMIT hoặc STOP và reduceOnly=True
                if order_type in ['STOP', 'STOP_LIMIT'] and reduce_only:
                    has_sl = True
                    logger.debug(f"{symbol}: Tìm thấy SL order (type={order_type})")
        except Exception as e:
            logger.warning(f"Không thể lấy open orders cho {symbol}: {e}")
        
        return has_sl, has_tp
        
    except Exception as e:
        logger.error(f"Lỗi khi kiểm tra SL/TP orders cho {symbol}: {e}", exc_info=True)
        return False, False

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
            if amount != 0:
                print(f"🔍 Kiểm tra position: {position['symbol']}, Amount: {amount}", flush=True)
                logger.info(f"Kiểm tra position: {position['symbol']}, Amount: {amount}")
                
                # Convert symbol format (BTCUSDT -> BTC/USDT)
                symbol_formatted = position['symbol'].replace("USDT", "/USDT")
                
                # Kiểm tra xem đã có SL/TP orders chưa
                has_sl, has_tp = has_sl_tp_orders(symbol_formatted, exchange)
                
                if has_sl and has_tp:
                    print(f"⏭️  {symbol_formatted} đã có SL và TP, bỏ qua", flush=True)
                    logger.info(f"{symbol_formatted} đã có SL và TP orders, bỏ qua")
                    continue
                elif has_sl or has_tp:
                    print(f"⚠️  {symbol_formatted} chỉ có một phần SL/TP (SL={has_sl}, TP={has_tp}), sẽ tạo lại", flush=True)
                    logger.warning(f"{symbol_formatted} chỉ có một phần SL/TP (SL={has_sl}, TP={has_tp}), sẽ tạo lại")
                
                # Position có vị thế, chưa có đủ SL/TP → Tạo SL + TP
                symbol = symbol_formatted
                
                position_amt = float(position['positionAmt'])
                entry_price = float(position['entryPrice'])
                is_short = position_amt < 0
                is_long = position_amt > 0
                leverage = int(position['leverage'])
                
                side = STATE_LONG if is_long else STATE_SHORT
                
                # Lấy config rate
                sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, side)
                logger.info(f"Config cho {symbol}: lenh2rate={lenh2rate}, lenh3rate={lenh3rate}")

                print(f"🎯 Tạo SL + TP cho {symbol} | Entry: {entry_price} | Side: {side} | Leverage: {leverage}x", flush=True)
                logger.info(f"Tạo SL + TP cho {symbol} | Entry: {entry_price} | Side: {side} | Leverage: {leverage}x")
                
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




