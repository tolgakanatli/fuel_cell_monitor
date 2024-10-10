import inspect, traceback
import tkinter as tk

log_list_g = None
log_error_g = None

def log_message(message, log_list=None, last_error=None, exception_info=None):
    global log_list_g, last_error_g
    if log_list != None: log_list_g = log_list
    if last_error != None: last_error_g = last_error
        
    caller= inspect.stack()[1]
    entry = f"[{caller.function}]: {message}"
    
    if exception_info:
        tb_str = ''.join(traceback.format_exception(*exception_info))
        print(tb_str)
        entry += f"\n{tb_str}"
        
    
    if log_list_g is None or last_error_g is None:
        print(entry)
        return
        
    log_list_g.insert(tk.END, entry)
    log_list_g.see(tk.END)
    last_error_g.configure(text=entry)

def format_number(value, asnumber=False):
    try:
        float_value = float(value)
        if float_value >= 10:
            formatted_value = round(float_value)
            if formatted_value % 10 == 1:
                formatted_value -= 1
            elif formatted_value % 10 == 9:
                formatted_value += 1  
        else:
            formatted_value = float(f"{float_value:.2f}")
         
        if not asnumber:
            if formatted_value>=10:
                strval = str(int(formatted_value))
            else:
                strval = f"{formatted_value:.2f}"
            formatted_value = strval.replace('.',',')      
        return formatted_value
    except ValueError:
        # If value is not a valid number, return it unchanged
        return value