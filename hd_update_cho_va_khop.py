import ccxt
import cst
import gg_sheet_factory
import cst
import logging
import time
from datetime import datetime
import utils
import os

file_name = os.path.basename(os.path.abspath(__file__))  
os.system(f"title {file_name} - {cst.key_name}")

logging.basicConfig(filename='hd_update_cho_va_khop.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

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



def get_all_open_orders_with_single_order():
    res = []
    
    for sym in  utils.get_all_open_orders_symbol_local():
        print(sym)
        
        
        orders = exchange.fetch_open_orders(symbol=sym)
        if len(orders) == 1:
            res.append(orders[0])
        
        for order in orders:
            print(f"Symbol: {order['symbol']}, ID: {order['id']}, Status: {order['status']}, Amount: {order['amount']}, Price: {order['price']}")
    return res

def get_opened_possition():
    
    balance = exchange.fetch_balance()
    positions = balance['info']['positions']
    opened_possition = []
    
    for position in positions:
        
        symbol = position['symbol']
        position_amt = float(position['positionAmt'])
        entry_price = float(position['entryPrice'])
        unrealized_pnl = float(position['unrealizedProfit'])
        leverage = int(position['leverage'])
        if position_amt != 0:
            print(position)
            opened_possition.append(position)
            print(f"Symbol: {symbol}, Position: {position_amt}, Entry Price: {entry_price}, Unrealized PnL: {unrealized_pnl}, Leverage: {leverage}")
    return opened_possition

def do_it():
    print(f"{datetime.now()}. Update chờ và khớp----------------------------------------------------")

    tab_100_ma_2d_arr = []
    res = get_opened_possition()
    print(f"Tổng Lệnh: {len(res)}")
    print(res)
    
    for position in res:
        position_amt = float(position['positionAmt'])
        cac_ma = position['symbol']
        vi_the_short_long = 'LONG' if  position_amt > 0 else 'SHORT' if position_amt < 0 else 'Flat'
        cho_khop = "N"
        da_khop_mo_vi_the = "Y"
        gia_vao = position['entryPrice']
        don_bay = position['leverage']
        
        orders = exchange.fetch_open_orders(symbol=cac_ma)
        
        lenh_nguoc_da_co_chua_co_2= len(orders)
        if lenh_nguoc_da_co_chua_co_2 == 1:
            
            lenh_tp= "Y"
            lenh_ls= "Y"
        else:
            
            lenh_tp= "N"
            lenh_ls= "N"
        print(cac_ma.replace("USDT", "/USDT"),vi_the_short_long ,cho_khop,da_khop_mo_vi_the , gia_vao,don_bay , lenh_tp, lenh_ls, lenh_nguoc_da_co_chua_co_2)
        row  = cac_ma.replace("USDT", "/USDT"),vi_the_short_long ,cho_khop,da_khop_mo_vi_the , gia_vao,don_bay , lenh_tp, lenh_ls, lenh_nguoc_da_co_chua_co_2
        tab_100_ma_2d_arr.append(row)

    res1 = get_all_open_orders_with_single_order()
    print(res1)
    print(f"Tổng Lệnh: {len(res1)}")

    for order in res1:
        print(f"Symbol: {order['symbol']}, ID: {order['id']}, Status: {order['status']}, Amount: {order['amount']}, Price: {order['price']}")
        
        
        order_symbol = order['info']['symbol']
        if next((position for position in res if order_symbol == position['symbol']), None):
                continue

        print(f"Found: {order}")
        
        cac_ma = order_symbol
        side = order['info']['side']
        vi_the_short_long = 'LONG' if  side == "BUY" else 'SHORT'
        cho_khop = "Y"
        da_khop_mo_vi_the = "N"
        gia_vao = order['info']['price']
        don_bay = "N"
        lenh_tp= "N"
        lenh_ls= "N"
        lenh_nguoc_da_co_chua_co_2 = 0
        print(cac_ma.replace("USDT", "/USDT"),vi_the_short_long ,cho_khop,da_khop_mo_vi_the , gia_vao,don_bay , lenh_tp, lenh_ls, lenh_nguoc_da_co_chua_co_2)
        row  = cac_ma.replace("USDT", "/USDT"),vi_the_short_long ,cho_khop,da_khop_mo_vi_the , gia_vao,don_bay , lenh_tp, lenh_ls, lenh_nguoc_da_co_chua_co_2
        tab_100_ma_2d_arr.append(row)

    gg_sheet_factory.clear_multi(gg_sheet_factory.tab_cho_va_khop,2, "a")
    gg_sheet_factory.update_multi(gg_sheet_factory.tab_cho_va_khop, 2, tab_100_ma_2d_arr, "a")

while True:
    try:
        do_it()
        
        
    except Exception as e:
        print("Tổng Lỗi:", e)
        logging.error("Tổng lỗi: %s", str(e))
    
    time.sleep(cst.delay_cho_va_khop)