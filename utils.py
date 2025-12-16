import datetime
from pathlib import Path

def convert_unix_timestamp(timestamp):
    
    dt_object = datetime.datetime.fromtimestamp(timestamp)

    
    formatted_time = dt_object.strftime("%m/%d/%Y %H:%M:%S")

    return formatted_time









def get_all_open_orders_symbol_local():
    fn  = 'order'
    res = []
    for folder in Path(fn).iterdir():
        if folder.is_dir():
            subfolders = [subfolder for subfolder in folder.iterdir() if subfolder.is_dir()]
            for subfolder in subfolders:
                
                symbol = str(subfolder).replace(f"{fn}\\","").replace(f"\\","/")
                res.append(symbol)
    return res
