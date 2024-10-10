import os
from tkinter import messagebox
import customtkinter as ctk
from gui import Padding, Styler
from gui.tabs import *
from functions.utility import log_message 
from functions.config_manager import ConfigManager, get_init_configs
from functions.file_manager import FileManager
from functions.GlobalVars import GlobalVar, GlobalVars
gv = GlobalVars()
    
class main_window(ctk.CTk):
    def __init__(self):
        initcfgs = get_init_configs("config_gui.ini")
        if "style_box" in initcfgs:
            ctk.set_default_color_theme(initcfgs["style_box"])
        else:
            ctk.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green
            
        if "darkmode_bool" in initcfgs:
            darkmode = True if initcfgs["darkmode_bool"]=="True" else False 
            ctk.set_appearance_mode("dark") if darkmode else ctk.set_appearance_mode("light")
        else:            
            ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
        
        super().__init__()
        self.title("File Analyzer")
        self.geometry("800x600")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        
        if "font_size_entry" in initcfgs:
            self.style = Styler(fontsize=initcfgs["font_size_entry"])
        else:
            self.style = Styler()
        
        self.main_frame = main_frame(self)
    
        

class main_frame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configmanager = ConfigManager("config_gui.ini")
        self.create_widgets()
        self.create_layout()
        self.filemanager = FileManager(self)
        
        #add all the tabs
        self.settings = settings_frame(self.add_tab("Settings"),master_frame=self)
        self.scan = scan_frame(self.add_tab("Scan"),master_frame=self)
        self.analysis = analysis_frame(self.add_tab("Analysis"),master_frame=self)
        self.log = log_frame(self.add_tab("Log"),master_frame=self)

        
            
        #initialize log list
        log_message("Program started", log_list=self.log.log_list, last_error=self.last_error)
    
    def create_widgets(self):
        #main frame
        self.main_tabview=ctk.CTkTabview(master=self)
    
        #controls frame
        self.fcontrols=ctk.CTkFrame(master=self)
        self.scan_button = ctk.CTkButton(master=self.fcontrols, text="Start monitoring", fg_color="#18a558", hover=False, width=50,command=self.togglescan)
        self.scan_progress = ctk.CTkProgressBar(master=self.fcontrols, mode="indeterminate")
        self.last_error = ctk.CTkLabel(master=self.fcontrols, text="")
        GlobalVar("scanning", False, bool)


    def create_layout(self):
        #main frame
        self.grid(row=0, column=0, **Padding, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.main_tabview.grid(row=0, column=0, **Padding, sticky="nsew")
        
        #controls frame
        self.fcontrols.grid_columnconfigure(1, weight=1)
        self.fcontrols.grid(row=1, column=0, **Padding, sticky="sew")
        self.scan_button.grid(row=0, column=0, **Padding, sticky="e")
        self.scan_progress.grid(row=0, column=1, **Padding, sticky="ew")
        self.last_error.grid(row=1, column=0, columnspan=2, padx=Padding["padx"], pady=(0,5), sticky="ew")
         
    def add_tab(self, text):
        added_tab = self.main_tabview.add(text)
        added_tab.grid_columnconfigure(0, weight=1)
        added_tab.grid_rowconfigure(0, weight=1)
        return added_tab
    
    def togglescan(self):
        
        if not gv.input_directory or not os.path.isdir(indir := gv.input_directory):
            messagebox.showerror(title="Error", message=f"The input directory {indir} does not exist.")
            return
        
        if not gv.output_directory or not os.path.isdir(outdir := gv.output_directory):
            result = messagebox.askyesno(title="Create directory?", default="yes", icon="warning", message=f"The output directory {outdir} does not exist. Do you want to create it?")
            if result:
                try:
                    os.makedirs(outdir)
                    log_message(f"Created output directory: {outdir}")
                except OSError as e:
                    log_message(f"Error creating output directory: {str(e)}")
                    return   
            else:  
                log_message("Please select a valid output directory.")
                return 
        
        gv.scanning = not gv.scanning
        
        if gv.scanning:
            self.scan_button.configure(text="Stop monitoring", fg_color="#D10000")
            self.scan_progress.start()
            self.filemanager.check_new_files()
        else:
            self.scan_button.configure(text="Start monitoring", fg_color="#18a558")
            self.scan_progress.stop()