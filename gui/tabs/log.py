import customtkinter as ctk
import tkinter as tk
from gui import Padding, Styler

class log_frame(ctk.CTkFrame):
    def __init__(self, master, master_frame):
        super().__init__(master)
        self.master_frame = master_frame
        self.log_list = tk.Listbox(master=self, height=10, width=100, font = Styler.custom_font)
        Styler.register_func(lambda newfont: self.update_font(newfont))
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.grid(row=0, column=0, **Padding, sticky="nswe")
        self.log_list.grid(row=0, column=0, **Padding, columnspan=2, sticky="nsew")
    
    def update_font(self, newfont):
        self.log_list.configure(font=newfont)