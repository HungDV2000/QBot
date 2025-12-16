import gg_sheet_factory
import ccxt 
import time
import datetime
from enum import Enum
import numpy as np
from datetime import datetime, timedelta
import cst
import time
import logging
import pandas as pd
import ctypes
import utils
import numpy as np
import json

import os
file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

logging.basicConfig(filename='hd_update_price.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def set_cmd_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

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
   

def do_it():
    print(f"-------------------------------start scan giá: {datetime.now()}-------------------------------------")
    start_time = time.time()

    
    tickers = exchange.fetch_tickers()

    
    
    
    
    list_all = []

    sheet_dat_lenh = gg_sheet_factory.get_100_ma(f"A3:A500")
    
    for d in sheet_dat_lenh:
        try:
            sym = d[0]
            
            if sym:
                list_all.append(sym+":USDT")
                print(sym)
            else:
                break
            

        except Exception as e:
            print(f"Lỗi:getLenh23Rate : {e}")

    tab_100_ma_2d_arr = []

    not_symbol_contain = "trong 24h"
    
    for symbol in list_all:
        if not not_symbol_contain in symbol:
            print(symbol)
            
            print(symbol, tickers[symbol]['last'])
            pair= symbol.replace(":USDT", "")
            
            row = [ tickers[symbol]['last']]
            tab_100_ma_2d_arr.append(row)
        else:
            print("---------------")
            tab_100_ma_2d_arr.append([])

    
    
    
    
    print(tab_100_ma_2d_arr)
    gg_sheet_factory.update_multi(gg_sheet_factory.tab_list_all_ma, 1, tab_100_ma_2d_arr, "Y")

    end_time = time.time()
    execution_time = end_time - start_time
    print("Thời gian thực thi:", execution_time, "giây")
 

while True:
    try:
        do_it()
        
        
    except Exception as e:
        print("Tổng Lỗi:", e)
        logging.error("Tổng lỗi: %s", str(e))

    
    time.sleep(cst.delay_update_price)