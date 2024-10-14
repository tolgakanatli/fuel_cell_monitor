# This file can be empty or contain package initialization code
from tkinter import ttk, font
from typing import Literal, Callable, Any
import tkinter as tk
from dataclasses import dataclass
from functions.GlobalVars import GlobalVars, GlobalVar
gv = GlobalVars()

Padding = {"padx":(10,10), "pady":(5,5)}


class Styler:
    _instance = None
    _initialized = False
    fontfamily= "Helvetica"
    fontsize= 12
    custom_font, style = None, None
    style_change_funcs = []

    
    def __new__(cls, family="Helvetica", fontsize=12):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.fontfamily = family
            cls.fontsize = fontsize
        return cls._instance
    
    def __init__(self, *args, **kwargs):
        if self._initialized == False:
            self._initialized = True
            Styler.custom_font = font.Font(family= Styler.fontfamily, size= Styler.fontsize)
            Styler.style = ttk.Style()
    
    @classmethod
    def edit_style(cls, size:int | None = None, family:str | None = None):
        if size:
            cls.fontsize=size
        if family:
            cls.fontfamily = family
        cls.custom_font.configure(family=cls.fontfamily, size=cls.fontsize)
        cls.config_tree()
        for func in cls.style_change_funcs:
            func(cls.custom_font)
    
    @classmethod
    def register_func(cls, func):
        cls.style_change_funcs.append(func)
    
    @classmethod
    def config_tree(cls):
        # Configure the Treeview widget to use the custom font
        cls.style.configure("Treeview", font=cls.custom_font)
        cls.style.configure("Treeview.Heading", font=cls.custom_font, padding=(0, 20))
        

@dataclass(frozen=True)
class constants:
    dataheaders = ["Voltage", "Current", "Power"]
    dataheaders_long = ["Voltage \n(V)", "Current Density \n(mA/cm2)", "Power Density \n(mW/cm2)"]

const = constants()