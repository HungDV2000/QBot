
import ccxt
import cst
from pathlib import Path
import time
import telegram_factory
import schedule
import time


def cancel_all_open_orders(symbol):
    open_orders = exchange.fetch_open_orders(symbol)

    if open_orders:
        for order in open_orders:
            order_id = order['id']
            cancel_result = exchange.cancel_order(order_id, symbol)
            print(f"Hủy lệnh {order_id} kết quả: {cancel_result}")
            msg = f"Đã Hủy lệnh chờ theo lịch: {order['symbol']}"
            telegram_factory.send_tele(msg,cst.chat_id, True , True)
    else:
        print(f"Không có lệnh mở nào cho {symbol}")

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




import gg_sheet_factory
from datetime import datetime

def my_function():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] Hàm đang chạy...")

    
    
    

    
    
    
    
    
    
    

    
    


    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

    
    

    
    for symbol in gg_sheet_factory.get_cho_va_khop("A3:A100"):
        if "USDT" in str(symbol) :
            print(f"cancel: {symbol[0]}")
            cancel_all_open_orders(symbol[0])




schedule.every(cst.cancel_orders_minutes).minutes.do(my_function)
print(f"Bắt đầu chạy...{cst.cancel_orders_minutes} phút một lần")

while True:
    schedule.run_pending()
    time.sleep(1)







