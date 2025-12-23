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
from notification_manager import NotificationManager, get_notification_manager
import requests
import hmac
import hashlib
import urllib.parse
import sys

# --- CẤU HÌNH HỆ THỐNG & LOGGING ---
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None

file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

log_timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
log_filename = f'hd_order_123_{log_timestamp}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
console_handler.setLevel(logging.INFO)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.propagate = False

order_logger = logging.getLogger('order')
order_logger.setLevel(logging.INFO)
order_handler = logging.FileHandler('order.log', encoding='utf-8')
order_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
order_logger.addHandler(order_handler)

STATE_SHORT = "SHORT"
STATE_LONG  = "LONG"

# --- CÁC HÀM TIỆN ÍCH ---

def is_same_pair(sym1, sym2):
    sym1 = sym1.replace("/", "").upper().strip()
    sym2 = sym2.replace("/", "").upper().strip()
    if sym1 == sym2 :
       return True
    return False

def getLenh23Rate(symbol, state):
    if state == STATE_LONG:
        start_row = 55
        end_row = 104
    elif state == STATE_SHORT:
        start_row = 4
        end_row = 53
    try:
        sheet_dat_lenh = gg_sheet_factory.get_dat_lenh(f"A{start_row}:G{end_row}")
        for d in sheet_dat_lenh:
            try:
                if len(d) < 7: continue
                sym = d[0]
                val_sl = d[5].strip() if d[5] else ""
                val_tp = d[6].strip() if d[6] else ""
                if not val_sl or not val_tp: continue
                lenh2_rate = float(val_sl)
                lenh3_rate = float(val_tp)
                if(is_same_pair(symbol, sym)):
                    return symbol, lenh2_rate, lenh3_rate
            except ValueError: continue 
            except Exception: pass
    except Exception as e:
        logger.error(f"Lỗi đọc Google Sheet: {e}")

    if state == STATE_LONG:
        return symbol, cst.lenh2_rate_long, cst.lenh3_rate_long
    elif state == STATE_SHORT:
         return symbol, cst.lenh2_rate_short, cst.lenh3_rate_short

def call_binance_api_direct(method, endpoint, params=None, api_key=None, secret_key=None):
    base_url = 'https://fapi.binance.com'
    url = f"{base_url}{endpoint}"
    if params is None: params = {}
    if api_key is None: api_key = cst.key_binance
    if secret_key is None: secret_key = cst.secret_binance
    
    params['timestamp'] = int(time.time() * 1000)
    query_string = urllib.parse.urlencode(params)
    signature = hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    params['signature'] = signature
    headers = {'X-MBX-APIKEY': api_key}
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params, headers=headers, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, params=params, headers=headers, timeout=10)
        else:
            return None
            
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Lỗi khi gọi Binance API trực tiếp ({method} {endpoint}): {e}")
        return None

def get_algo_orders_for_symbol(symbol):
    try:
        params = {'symbol': symbol.replace('/', '')}
        response = call_binance_api_direct('GET', '/fapi/v1/allAlgoOrders', params)
        if not response: return []
        if isinstance(response, list): return response
        elif isinstance(response, dict):
            if 'data' in response: return response['data']
            elif response.get('code') == 200: return response
            else: return []
        else: return []
    except Exception as e:
        logger.error(f"Lỗi khi lấy algo orders: {e}", exc_info=True)
        return []

def cancel_all_algo_orders_direct(symbol):
    """
    [FIXED] Hủy từng Algo Order.
    - Sửa lỗi so sánh code '200' vs 200.
    - Thêm cảnh báo Telegram nếu hủy thất bại.
    """
    try:
        active_orders = get_algo_orders_for_symbol(symbol)
        pending_orders = [o for o in active_orders if o.get('algoStatus') == 'NEW']
        
        if not pending_orders:
            return True
            
        logger.info(f"Tìm thấy {len(pending_orders)} Algo Orders cần hủy cho {symbol}")
        
        count = 0
        failed_orders = []

        for order in pending_orders:
            algo_id = order.get('algoId')
            if algo_id:
                params = {
                    'symbol': symbol.replace('/', ''),
                    'algoId': algo_id
                }
                response = call_binance_api_direct('DELETE', '/fapi/v1/algoOrder', params)
                
                # [FIX QUAN TRỌNG] Kiểm tra thành công an toàn hơn (chấp nhận cả int 200 và str '200')
                is_success = False
                if response:
                    code = response.get('code')
                    # Nếu code là 200 hoặc '200' -> OK
                    if str(code) == '200':
                        is_success = True
                
                if is_success:
                    count += 1
                else:
                    failed_orders.append(algo_id)
                    logger.error(f"Lỗi hủy algoId {algo_id}: {response}")

        logger.info(f"Đã hủy thành công {count}/{len(pending_orders)} lệnh Algo cho {symbol}")
        
        # [CẢNH BÁO TELEGRAM] Nếu có lệnh không hủy được
        if failed_orders:
            msg = f"⚠️ <b>CẢNH BÁO KHẨN CẤP</b>\n\n<b>Mã:</b> {symbol}\n<b>Lỗi:</b> Không thể hủy {len(failed_orders)} lệnh Algo (Trailing Stop).\n<b>Hành động:</b> Vui lòng vào app Binance HỦY TAY ngay lập tức để tránh trùng lệnh!"
            telegram_factory.send_tele(msg, cst.chat_id, True, True)
            return False # Báo thất bại để vòng lặp chính không tạo lệnh mới đè lên

        return True
        
    except Exception as e:
        logger.error(f"Lỗi ngoại lệ khi hủy Algo Orders cho {symbol}: {e}")
        return False

def has_sl_tp_orders(symbol, exchange):
    try:
        algo_orders = get_algo_orders_for_symbol(symbol)
        has_sl = False
        has_tp = False
        
        # Check TP (Trailing Stop)
        active_algo_orders = [o for o in algo_orders if o.get('algoStatus', '').upper() == 'NEW']
        for order in active_algo_orders:
            algo_type = order.get('algoType', '').upper()
            reduce_only = order.get('reduceOnly', False)
            if algo_type in ['CONDITIONAL', 'VP'] and reduce_only:
                has_tp = True
        
        # Check SL (Stop Market/Limit)
        try:
            open_orders = exchange.fetch_open_orders(symbol)
            for order in open_orders:
                order_type = order.get('type', '').upper()
                info = order.get('info', {})
                reduce_only = order.get('reduceOnly', False) or info.get('reduceOnly', False)
                if order_type in ['STOP', 'STOP_LIMIT'] and reduce_only:
                    has_sl = True
        except Exception as e:
            logger.warning(f"Không thể lấy open orders: {e}")
        
        return has_sl, has_tp
    except Exception as e:
        logger.error(f"Lỗi check SL/TP: {e}", exc_info=True)
        return False, False

# --- LOGIC CHÍNH ---

def do_it():
    logger.info(f"{datetime.now()}. Scan Vào Lệnh 123 (Auto-Fix Mode) -------------------------")
    exchange_id = 'binance'
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({
        'enableRateLimit': True,  
        'apiKey': cst.key_binance,
        'secret': cst.secret_binance,
        'options': {'defaultType': 'future'}
    })
    exchange.setSandboxMode(False)
    
    order_helper = BinanceOrderHelper(exchange)
    cascade_mgr = get_cascade_manager(exchange, order_helper)
    
    try:
        balance = exchange.fetch_balance()
        positions = balance['info']['positions']
    except Exception as e:
        logger.error(f"Lỗi khi lấy balance/positions: {e}")
        return

    for position in positions:
        try:
            try:
                amount = float(position['positionAmt'])
            except: amount = 0.0

            if amount != 0:
                print(f"🔍 Kiểm tra position: {position['symbol']}, Amount: {amount}", flush=True)
                symbol_formatted = position['symbol'].replace("USDT", "/USDT")
                
                has_sl, has_tp = has_sl_tp_orders(symbol_formatted, exchange)
                
                if has_sl and has_tp:
                    print(f"⏭️  {symbol_formatted} đã ĐỦ SL và TP. Bỏ qua.", flush=True)
                    continue
                
                elif has_sl or has_tp:
                    # [FIXED] Tự động Fix lỗi lẻ lệnh TRIỆT ĐỂ
                    print(f"♻️  {symbol_formatted} bị LẺ LỆNH (SL={has_sl}, TP={has_tp}). Đang làm mới lệnh cho {symbol_formatted}...", flush=True)
                    logger.warning(f"{symbol_formatted} bị lẻ lệnh. Đang hủy lệnh chờ cũ của riêng {symbol_formatted}...")
                    
                    try:
                        # 1. Hủy lệnh thường (SL)
                        exchange.cancel_all_orders(symbol_formatted)
                        # 2. Hủy lệnh Algo (TP - Trailing Stop) - Có check lỗi
                        is_algo_cancelled = cancel_all_algo_orders_direct(symbol_formatted)
                        
                        if is_algo_cancelled:
                            print(f"✅ Đã làm sạch lệnh của {symbol_formatted}. Chờ vòng sau tạo lại.", flush=True)
                            msg = f"🛠 <b>TỰ ĐỘNG SỬA LỖI</b>\n\n<b>Mã:</b> {symbol_formatted}\n<b>Hành động:</b> Đã hủy lệnh chờ cũ.\n<b>Trạng thái:</b> Chờ tạo bộ SL/TP mới."
                            telegram_factory.send_tele(msg, cst.chat_id, True, True)
                        else:
                            print(f"❌ Không thể hủy hết lệnh Algo của {symbol_formatted}. Dừng xử lý mã này.", flush=True)
                        
                    except Exception as e:
                        print(f"❌ Lỗi khi hủy lệnh cũ {symbol_formatted}: {e}", flush=True)
                        logger.error(f"Lỗi cancel_all {symbol_formatted}: {e}")
                    
                    continue 
                
                # --- TẠO LỆNH MỚI ---
                symbol = symbol_formatted
                position_amt = float(position['positionAmt'])
                
                entry_price = None
                if 'entryPrice' in position and position['entryPrice']:
                    try: entry_price = float(position['entryPrice'])
                    except: pass
                
                if entry_price is None or entry_price <= 0:
                    try:
                        ticker = exchange.fetch_ticker(symbol_formatted)
                        entry_price = float(ticker['last'])
                    except: continue
                
                is_long = position_amt > 0
                side = STATE_LONG if is_long else STATE_SHORT
                leverage = int(position.get('leverage', 1))
                
                sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, side)

                if entry_price <= 0 or lenh2rate <= 0 or lenh3rate <= 0:
                    continue

                print(f"🎯 Tạo SL + TP cho {symbol} | Entry: {entry_price} | Side: {side}", flush=True)
                
                try:
                    result = cascade_mgr.on_entry_filled(
                        symbol=symbol,
                        layer_num=1,
                        entry_price=entry_price,
                        leverage=leverage,
                        position_amt=position_amt,
                        side=side,
                        max_layers=3,
                        lenh2_rate=lenh2rate,
                        lenh3_rate=lenh3rate,
                        lenh3_callback_rate=cst.lenh3_callback_rate,
                        next_layer_config=None 
                    )
                    
                    sl_order = result.get('sl_order')
                    tp_order = result.get('tp_order')
                    
                    if sl_order and tp_order:
                        order_logger.info(f"LỆNH 2 (SL) | {symbol} | {side} | Entry: {entry_price}")
                        order_logger.info(f"LỆNH 3 (TP) | {symbol} | {side} | Entry: {entry_price}")
                        
                        msg = f"✅ <b>ĐÃ TẠO SL + TP CHO LỚP 1</b>\n\n<b>Mã:</b> {symbol}\n<b>Entry:</b> {entry_price}\n<b>SL:</b> {sl_order.get('id')}\n<b>TP:</b> {tp_order.get('id')}"
                        telegram_factory.send_tele(msg, cst.chat_id, True, True)
                        logger.info(f"✅ Cascade lớp 1 hoàn tất cho {symbol}")
                    else:
                        logger.warning(f"⚠️ Cascade lớp 1 lỗi")
                        
                except Exception as e:
                    logger.error(f"❌ Lỗi cascade lớp 1 cho {symbol}: {e}", exc_info=True)
                    msg = f"🚨 <b>LỖI TẠO SL/TP</b>\n\n<b>Mã:</b> {symbol}\n<b>Lỗi:</b> {str(e)}"
                    telegram_factory.send_tele(msg, cst.chat_id, True, True)

        except Exception as e:
            logger.error(f"Lỗi xử lý position: {e}")

while True:
    try:
        do_it()
        sys.stdout.flush()
    except Exception as e:
        print(f"Tổng Lỗi: {e}", flush=True)
        logger.error(f"Tổng lỗi: {e}", exc_info=True)
    time.sleep(cst.delay_vao_lenh_123)