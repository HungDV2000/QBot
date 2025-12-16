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

file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

logging.basicConfig(filename='hd_order_123.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

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
            print(f"Lỗi:getLenh23Rate : {e}")


    
    if state == STATE_LONG:
        return sym, cst.lenh2_rate_long, cst.lenh3_rate_long
    elif state == STATE_SHORT:
         return sym, cst.lenh2_rate_short, cst.lenh3_rate_short
    


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
    print(f"{datetime.now()}. Scan Vào Lệnh 123----------------------------------------------------")
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

    
    positions = exchange.fetch_positions()

    
    positions = [pos for pos in positions if float(pos['contracts']) > 0]

    
    for pos in positions:
        

        position = pos['info']
    
    
    
        try:
            print(position)
            symbol = position['symbol']
            
            
            amount = float(position['positionAmt'])
            if amount !=0:
                print(f"Vị thế: {position}")
                orders = exchange.fetch_open_orders(symbol=symbol)
                tong_so_lenh_dang_mo = len(orders)
                
                if tong_so_lenh_dang_mo == 0:
                    

                    
                    symbol = symbol.replace("USDT", "/USDT")
                    
                    position_amt = float(position['positionAmt'])
                    entry_price = float(position['entryPrice'])
                    
                    

                    is_short = position_amt < 0
                    is_long = position_amt > 0
                    lv = pos['notional']/pos['initialMargin']
                    if lv:
                        leverage = int(lv)
                    else:
                        leverage = 1

                    
                    try:
                        if(leverage>0):
                            exchange.setLeverage (leverage, symbol)
                            print(f"Đã thiết lập đòn bẩy {leverage} cho cặp giao dịch {symbol}")
                    except Exception as e:
                        print()

                    if is_long:
                        sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, STATE_LONG)
                        print(sb, lenh2rate, lenh3rate)
                        
                        limit_price  = entry_price*(1 - lenh2rate / leverage)

                        stop_price = limit_price 
                    else:
                        sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, STATE_SHORT)
                        print(sb, lenh2rate, lenh3rate)
                        
                        limit_price  = entry_price*(1 + lenh2rate/ leverage)
                        stop_price = limit_price  



                    
                    
                    exchange = ccxt.binance({
                        'apiKey': cst.key_binance,
                        'secret': cst.secret_binance,
                        'options': {
                            'defaultType': 'future',
                        }
                    })
                    print(f"---Vào lệnh 2")

                    
                    try:
                        order = exchange.create_order(
                            symbol=position['symbol'],
                            type='STOP',
                            side='SELL' if is_long else 'BUY',
                            amount=abs(position_amt),
                            price=limit_price,
                            params={
                                'stopPrice': stop_price,
                                'reduceOnly': True,  
                            }
                        )
                        print("Lệnh Stop Limit đã được tạo:", order)
                        msg = f"Lệnh 2: Stop Limit đã được tạo: {symbol}"
                        telegram_factory.send_tele(msg,cst.chat_id, True , True)

                    except ccxt.BaseError as e:
                        print("Lỗi khi tạo lệnh 2:", e)


                    print(f"---Vào lệnh 3")
                    
                    print(f"entry_price= {entry_price}")
                    
                    if is_long:
                        side = 'sell'
                        sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, STATE_SHORT)
                        print(sb, lenh2rate, lenh3rate)
                        stop_price = entry_price * (1 + lenh3rate / leverage)
                        
                        
                    else:
                        side = 'buy'
                        sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, STATE_LONG)
                        print(sb, lenh2rate, lenh3rate)
                        stop_price = entry_price * (1 - lenh3rate / leverage)
                        

                    print(f"side= {side} stop_price = {stop_price}")
                    rate = 0.2
                    
                    price = round(stop_price, binance_utils.get_price_precision(symbol))
                    params = {
                        'type': 'TRAILING_STOP_MARKET',
                        'activationPrice': price,
                        'callbackRate': rate,
                        'reduceOnly': True,  
                    }

                    try:
                        
                        order = exchange.create_order(symbol, 'market', side, abs(position_amt), None, params)
                        print("Lệnh TRAILING_STOP_MARKET đã được tạo:", order)
                        msg = f"Lệnh 3: TRAILING_STOP_MARKET đã được tạo: {symbol}"
                        telegram_factory.send_tele(msg,cst.chat_id, True , True)


                    except ccxt.BaseError as e:
                        print("Lỗi khi tạo lệnh 3:", e)
                        print("Vào lệnh 3a tỷ lệ bằng lệnh 3 cộng thêm 3%")

                        rate_3a = 0.3
                        try:
                            if is_long:
                                side = 'sell'

                                sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, STATE_SHORT)
                                print(sb, lenh2rate, lenh3rate)

                                
                                stop_price = entry_price * (1 + (lenh3rate+rate_3a) / leverage)
                                
                            else:
                                side = 'buy'
                                sb, lenh2rate, lenh3rate = getLenh23Rate(symbol, STATE_LONG)
                                print(sb, lenh2rate, lenh3rate)
                                
                                stop_price = entry_price * (1 - (lenh3rate+rate_3a) / leverage)

                            print(f"side= {side} stop_price = {stop_price}")
                            rate = 0.2
                            
                            price = round(stop_price, binance_utils.get_price_precision(symbol))
                            params = {
                                'type': 'TRAILING_STOP_MARKET',
                                'activationPrice': price,
                                'callbackRate': rate,
                                'reduceOnly': True,  
                            }
                            order = exchange.create_order(symbol, 'market', side, abs(position_amt), None, params)
                            print("Lệnh TRAILING_STOP_MARKET đã được tạo:", order)
                            msg = f"Lệnh 3a: TRAILING_STOP_MARKET đã được tạo: {symbol}"
                            telegram_factory.send_tele(msg,cst.chat_id, True , True)

                        except ccxt.BaseError as e:
                            print("Lỗi khi tạo lệnh 3a:", e)


        except Exception as e:
            print(f"Một lỗi đã xảy ra: {e}")






while True:
    try:
        do_it()
        
        
    except Exception as e:
        print("Tổng Lỗi:", e)
        logging.error("Tổng lỗi: %s", str(e))

    time.sleep(cst.delay_vao_lenh_123)







