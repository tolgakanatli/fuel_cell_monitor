import customtkinter as ctk
from tkinter import filedialog
import os

class directory_selector(ctk.CTkFrame):
    def __init__(self, master, label:str, initialdir:str|None=None, command:callable=None, padx=(10,10), pady=(5,5)):
        super().__init__(master, 
                         bg_color="transparent", 
                         fg_color="transparent", 
                         border_width=0, 
                         border_color=None, 
                         corner_radius=0)
        self.command = command
        self.initialdir = initialdir
        self.pad = {
            "padx":padx,
            "pady":pady
        }
        self.label = ctk.CTkLabel(master=self, text=label)
        self.entry = ctk.CTkEntry(master=self,width=300)
        self.button = ctk.CTkButton(master=self,text="Browse", command=self.on_button_click,width=100)
        
        self.label.grid(row=0, column=0, padx=(0,self.pad["padx"][1]), pady= self.pad["pady"], sticky="e")
        self.entry.grid(row=0, column=1, **self.pad, sticky="we")
        self.button.grid(row=0, column=2, padx=(self.pad["padx"][0],0), pady= self.pad["pady"], sticky="w")
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, minsize=200)       

    def on_button_click(self):
        if self.initialdir is None:
            curr_dir = self.entry.get()
            if os.path.isdir(curr_dir):
                self.initialdir = curr_dir
        
                
        directory = filedialog.askdirectory(initialdir=self.initialdir,mustexist=True)
        if directory:
            self.entry.delete(0, "end")
            self.entry.insert(0,directory)
            if callable(self.command):
                self.command()
    
    def __getattr__(self, name):
        # Delegate attribute access to the entry widget
        return getattr(self.entry, name)