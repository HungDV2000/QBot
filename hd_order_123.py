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
from pathlib import Path
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

# Tạo thư mục logs/ nếu chưa có
logs_dir = Path('logs')
logs_dir.mkdir(exist_ok=True)

log_timestamp = datetime.now().strftime('%d_%m_%Y_%H_%M_%S')
log_filename = logs_dir / f'hd_order_123_{log_timestamp}.log'

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
order_log_path = logs_dir / 'order.log'
order_handler = logging.FileHandler(order_log_path, encoding='utf-8')
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
    """
    [ĐÃ SỬA CHỮA] Logic đọc Rate thông minh:
    1. Tìm symbol trong Sheet.
    2. Đọc cột F (SL) và G (TP).
    3. Nếu ô trống hoặc bằng 0 -> TỰ ĐỘNG LẤY TỪ CONFIG.
    4. Nếu có số > 0 -> Ưu tiên dùng số trong Sheet.
    """
    # 1. Xác định vùng quét
    if state == STATE_LONG:
        start_row = 55
        end_row = 104
        logger.info(f"🔍 [GET RATE] Quét LONG ({start_row}-{end_row}) cho {symbol}...")
    elif state == STATE_SHORT:
        start_row = 4
        end_row = 53
        logger.info(f"🔍 [GET RATE] Quét SHORT ({start_row}-{end_row}) cho {symbol}...")
    
    # 2. Chuẩn bị giá trị Config mặc định
    def_sl = cst.lenh2_rate_long if state == STATE_LONG else cst.lenh2_rate_short
    def_tp = cst.lenh3_rate_long if state == STATE_LONG else cst.lenh3_rate_short

    try:
        # Đọc dữ liệu từ Sheet
        sheet_dat_lenh = gg_sheet_factory.get_dat_lenh(f"A{start_row}:G{end_row}")
        
        for d in sheet_dat_lenh:
            try:
                if len(d) < 1: continue
                sym = d[0]
                if not sym: continue
                
                # Nếu tìm thấy Symbol
                if is_same_pair(symbol, sym):
                    
                    # --- XỬ LÝ RATE SL (Cột F / Index 5) ---
                    try:
                        val_sl = float(d[5]) if len(d) > 5 and d[5] else 0
                    except: val_sl = 0
                    
                    # --- XỬ LÝ RATE TP (Cột G / Index 6) ---
                    try:
                        val_tp = float(d[6]) if len(d) > 6 and d[6] else 0
                    except: val_tp = 0
                    
                    # --- LOGIC QUYẾT ĐỊNH ---
                    # Nếu Sheet > 0 thì dùng Sheet, ngược lại dùng Config
                    final_sl = val_sl if val_sl > 0 else def_sl
                    final_tp = val_tp if val_tp > 0 else def_tp
                    
                    logger.info(f"   ✅ Tìm thấy {symbol}: Sheet(SL={val_sl}, TP={val_tp}) -> Final(SL={final_sl}, TP={final_tp})")
                    
                    return symbol, final_sl, final_tp

            except Exception:
                continue

    except Exception as e:
        logger.error(f"Lỗi đọc Google Sheet: {e}")

    # Fallback cuối cùng nếu không tìm thấy symbol trong sheet
    logger.info(f"   ⬇️ Không tìm thấy {symbol} trong sheet -> Dùng Full Config: SL={def_sl}, TP={def_tp}")
    return symbol, def_sl, def_tp

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
    try:
        active_orders = get_algo_orders_for_symbol(symbol)
        pending_orders = [o for o in active_orders if o.get('algoStatus') == 'NEW']
        
        if not pending_orders: return True
            
        logger.info(f"Tìm thấy {len(pending_orders)} Algo Orders cần hủy cho {symbol}")
        
        count = 0
        failed_orders = []

        for order in pending_orders:
            algo_id = order.get('algoId')
            if algo_id:
                params = {'symbol': symbol.replace('/', ''), 'algoId': algo_id}
                response = call_binance_api_direct('DELETE', '/fapi/v1/algoOrder', params)
                
                is_success = False
                if response:
                    code = response.get('code')
                    if str(code) == '200': is_success = True
                
                if is_success: count += 1
                else: failed_orders.append(algo_id)

        logger.info(f"Đã hủy thành công {count}/{len(pending_orders)} lệnh Algo cho {symbol}")
        
        if failed_orders:
            msg = f"⚠️ <b>CẢNH BÁO</b>\n\nKhông thể hủy {len(failed_orders)} lệnh Algo của {symbol}."
            telegram_factory.send_tele(msg, cst.chat_id, True, True)
            return False 

        return True
    except Exception as e:
        logger.error(f"Lỗi hủy Algo Orders {symbol}: {e}")
        return False

def has_sl_tp_orders(symbol, exchange):
    try:
        algo_orders = get_algo_orders_for_symbol(symbol)
        try: open_orders = exchange.fetch_open_orders(symbol)
        except: open_orders = []
            
        has_sl = False
        has_tp = False
        
        # --- 1. QUÉT ALGO ORDERS ---
        active_algo_orders = [o for o in algo_orders if o.get('algoStatus', '').upper() == 'NEW']
        
        for order in active_algo_orders:
            algo_type = order.get('algoType', '').upper()
            reduce_only = order.get('reduceOnly', False)
            
            # Lấy callbackRate để phân biệt
            callback_rate = order.get('callbackRate')
            
            # Xử lý giá trị callbackRate an toàn
            callback_val = 0.0
            if callback_rate is not None:
                try:
                    callback_val = float(callback_rate)
                except:
                    callback_val = 0.0

            if reduce_only:
                # == KIỂM TRA TP (Trailing Stop) ==
                if algo_type in ['CONDITIONAL', 'VP', 'TRAILING_STOP_MARKET'] and callback_val > 0:
                    has_tp = True
                
                # == KIỂM TRA SL (Stop Limit/Market) ==
                if algo_type in ['STOP', 'STOP_MARKET', 'STOP_LOSS', 'STOP_LOSS_MARKET', 'STOP_LIMIT']:
                    has_sl = True
                elif algo_type == 'CONDITIONAL' and callback_val == 0:
                    has_sl = True

        # --- 2. QUÉT OPEN ORDERS ---
        if not has_sl:
            for order in open_orders:
                order_type = order.get('type', '').upper()
                info = order.get('info', {})
                reduce_only = order.get('reduceOnly', False) or info.get('reduceOnly', False)
                if order_type in ['STOP', 'STOP_LIMIT', 'STOP_MARKET'] and reduce_only:
                    has_sl = True

        return has_sl, has_tp
        
    except Exception as e:
        logger.error(f"Lỗi check SL/TP: {e}", exc_info=True)
        return False, False

# --- LOGIC CHÍNH ---

def do_it():
    logger.info(f"{datetime.now()}. Scan Vào Lệnh 123 (Verified Mode) -------------------------")
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
                
                # Logic xác định trạng thái
                if has_sl and has_tp:
                    print(f"⏭️  {symbol_formatted} đã ĐỦ SL và TP. Bỏ qua.", flush=True)
                    continue
                
                elif has_sl or has_tp:
                    print(f"♻️  {symbol_formatted} bị LẺ LỆNH (SL={has_sl}, TP={has_tp}). Fix lỗi...", flush=True)
                    logger.warning(f"{symbol_formatted} bị lẻ lệnh. Reset...")
                    try:
                        exchange.cancel_all_orders(symbol_formatted)
                        cancel_all_algo_orders_direct(symbol_formatted)
                        
                        msg = f"🛠 <b>AUTO-FIX</b>\n<b>Mã:</b> {symbol_formatted}\n<b>Trạng thái:</b> Lẻ lệnh -> Đã Reset.\n<b>Hành động:</b> Chờ tạo mới."
                        telegram_factory.send_tele(msg, cst.chat_id, True, True)
                    except Exception as e:
                        print(f"❌ Lỗi hủy lệnh: {e}", flush=True)
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
                
                # Lấy Rate (đã dùng hàm mới an toàn)
                sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, side)
                
                if entry_price <= 0: continue
                # Nếu cả Sheet và Config đều trả về 0 thì mới bỏ qua (hiếm khi xảy ra nếu config đúng)
                if lenh2rate <= 0 and lenh3rate <= 0:
                    logger.warning(f"⚠️ {symbol}: Rate SL/TP đều <= 0. Kiểm tra lại Config.")
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