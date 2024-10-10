import configparser
from gui import *
from functions.utility import log_message
import os
import tkinter as tk
from typing import Literal        
        
class ConfigManager:
    def __init__(self, config_path: str = 'config.ini'):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.widgets = {}

    def register(self, name: str, 
                 widget: tk.Widget, 
                 widget_type: Literal['entry', 'text', 'checkbutton', 'scale', 'combobox'], 
                 data_type: Literal['str', 'bool', 'float', 'int'] = 'str',
                 load_command: callable = None,
                 section: Literal['Settings','Init'] = 'Settings'
                 ):
        self.widgets[name] = (widget, widget_type, data_type, load_command, section)

    def load_config(self):
        if os.path.isfile(self.config_path):
            self.config.read(self.config_path)
            for name, (widget, widget_type, data_type, loadcommand, section) in self.widgets.items():
                if name in self.config['Settings'] or name in self.config['Init']:
                    if self.config.has_option(section, name):
                        value = self.get_config_value(name, data_type, section)
                        self.set_widget_value(widget, widget_type, value)
                    if loadcommand:
                        loadcommand()
        else:
            log_message(f"Config file not found at: {self.config_path}")

    def save_config(self):
        self.config['Settings'] = {}
        self.config['Init'] = {}
        
        for name, (widget, widget_type, _, _, section) in self.widgets.items():
            value = self.get_widget_value(widget, widget_type)
            self.config[section][name] = str(value)
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
            log_message("Config file saved.")

    def get_widget_value(self, widget: tk.Widget, widget_type: str):
        if widget_type == 'text':
            return widget.get("1.0", tk.END).strip()
        elif widget_type in ['entry','checkbutton', 'scale', 'combobox']:
            return widget.get()



    def set_widget_value(self, widget: tk.Widget, widget_type: str, value):
        if widget_type == 'entry':
            widget.delete(0, tk.END)
            widget.insert(0, value)
        elif widget_type == 'text':
            widget.delete("1.0", tk.END)
            widget.insert(tk.END, value)
        elif widget_type in ['checkbutton', 'scale', 'combobox']:
            widget.set(value)

    def get_config_value(self, name: str, data_type: str, section: Literal['Settings','Init'] = 'Settings'):
        if data_type == 'str':
            return self.config[section][name]
        elif data_type == 'bool':
            return self.config.getboolean(section, name)
        elif data_type == 'float':
            return self.config.getfloat(section, name)
        elif data_type == 'int':
            return self.config.getint(section, name)
        
def get_init_configs(config_path:str = "config.ini"):
    if not os.path.isfile(config_path):
        print("Error: Config file not found.")
        return {}  
    config = configparser.ConfigParser()   
    config.read(config_path)
    if not config.has_section("Init"):
        return {}
    
    init_items = {}
    
    for item in config.items("Init"):
        init_items[item[0]] = item[1]
      
    return init_items


