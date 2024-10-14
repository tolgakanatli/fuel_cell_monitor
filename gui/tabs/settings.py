import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import os, sys
from gui import Padding, Styler
from functions.utility import log_message
from ..widgets.directory_selector import directory_selector
from ..widgets.spinbox import spinbox
from functions.GlobalVars import GlobalVars, GlobalVar
gv = GlobalVars()


class settings_frame(ctk.CTkScrollableFrame):
    def __init__(self, master, master_frame):
        super().__init__(master)
        # settings tab
        self.master_frame = master_frame
        self.grid(row=0, column=0, **Padding, sticky="nwse")
        self.grid_columnconfigure(1, weight=1)
        self.create_widgets()
        self.create_layout()
        self.register_global_vars()
        self.register_configs(self.master_frame.configmanager)

    def create_widgets(self):
        #input - output selectors
        self.input_dir = directory_selector(self, "Input Directory", command=self.populate_variables, **Padding)
        self.output_dir = directory_selector(self, "Output Directory", **Padding)    

        self.separator = ttk.Separator(master=self, orient="horizontal")
        self.separator.grid(row=2, column=0, columnspan=3, **Padding, sticky="ew")

        #naming convention
        self.variables_label = ctk.CTkLabel(master=self, text="Available variables:")
        self.variable_list = ctk.CTkComboBox(master=self, values=[" "])
        self.variable_button = ctk.CTkButton(master=self,text="+", command=self.add_var, width=100)
        self.convention_label = ctk.CTkLabel(master=self, text="Naming convention:")
        self.convention_text = ctk.CTkTextbox(master=self, height=75)
        self.individual_naming_bool = ctk.BooleanVar(value=False)
        self.individual_naming = ctk.CTkSwitch(master=self, text="Name every file individually",command=self.toggle_naming,variable=self.individual_naming_bool)

        self.separator2 = ttk.Separator(master=self, orient="horizontal")  

        #others
        self.area_label = ctk.CTkLabel(master=self, text="Cell area (cm^2):")
        self.cell_area = ctk.CTkEntry(master=self)
        self.cell_area.insert(0, "5.0")
        
        self.seperator3 = ttk.Separator(master=self, orient="horizontal")
        
        #scan related
        self.spd_label = ctk.CTkLabel(master=self, text="Scan interval \n(seconds):")
        self.speed_slider = spinbox(master=self,min=1,max=5, increment=1, initial=1,integer=True)
        self.auto_process_bool = ctk.BooleanVar(value=True)
        self.auto_process_switch= ctk.CTkSwitch(master=self, text="Automatically process new files when they become available", variable=self.auto_process_bool)
        self.wait_label = ctk.CTkLabel(master=self, text="Monitor interval \n(seconds):")
        self.wait_entry = spinbox(master=self,min=1, max=15, increment=1, initial=5,integer=True)
        
        self. sepeartor4 = ttk.Separator(master=self, orient="horizontal")
        
        #ui related
        self.style_label = ctk.CTkLabel(master=self, text="UI Style:")
        self.style_box = ctk.CTkComboBox(master=self, values=["blue", "dark-blue", "green"])
        self.style_box.set("green")
        self.darkmode_bool = ctk.BooleanVar(value=False)
        self.darkmode_switch = ctk.CTkSwitch(master=self, text="Dark mode", variable=self.darkmode_bool,command=self.apply_mode_change)
        self.font_size_label = ctk.CTkLabel(master=self, text="List font size:")
        self.font_size_entry = spinbox(master=self, min = 8, max=32, increment=1, initial=12, integer=True,command=self.apply_font_changes)
                
        #save, load
        self.save_load_frame = ctk.CTkFrame(master=self)
        self.save_load_seperator = ttk.Separator(master=self.save_load_frame, orient="horizontal")
        self.save_button = ctk.CTkButton(master=self.save_load_frame, text="Save config", command= self.master_frame.configmanager.save_config)
        self.load_button = ctk.CTkButton(master=self.save_load_frame, text="Load config", command= self.master_frame.configmanager.load_config)
        
    def create_layout(self):
        
        #input-output selector
        self.input_dir.grid(row=0, column=0, columnspan=3, **Padding, sticky="ew")
        self.output_dir.grid(row=1, column=0, columnspan=3,**Padding, sticky="ew")

        #naming convention
        self.variables_label.grid(row=3, column=0, **Padding, sticky="e")
        self.variable_list.grid(row=3, column=1, **Padding, sticky="ew")
        self.convention_label.grid(row=4, column=0, **Padding, sticky="e")
        self.variable_button.grid(row=3, column=2, **Padding, sticky="e")
        self.convention_text.grid(row=4, column=1, columnspan=2, **Padding, sticky="ew")
        self.individual_naming.grid(row=6, column=1, columnspan=2, **Padding, sticky="ew")
        self.convention_text.bind(".", lambda event: "break")
        
        self.separator2.grid(row=8, column=0, columnspan=3, **Padding, sticky="ew")
        
        #others
        self.area_label.grid(row=9, column=0, **Padding, sticky="e")
        self.cell_area.grid(row=9, column=1, **Padding, sticky="w")
        
        self.seperator3.grid(row=10, column=0, columnspan=3, **Padding, sticky="ew")
        #scan related

        self.spd_label.grid(row=11, column=0, **Padding, sticky="e")
        self.speed_slider.grid(row=11, column=1, **Padding, sticky="w")
        self.auto_process_switch.grid(row=12, column=1, columnspan=2, **Padding, sticky="w")
        self.wait_label.grid(row=13,column=0, **Padding, sticky="e")
        self.wait_entry.grid(row=13,column=1, **Padding, sticky="w")

        self. sepeartor4.grid(row=16, column=0,columnspan=3, **Padding, sticky="ew")
        
        #ui related
        self.style_label.grid(row=17, column=0, **Padding, sticky="e")
        self.style_box.grid(row=17, column=1, **Padding, sticky="ew")
        self.darkmode_switch.grid(row=17, column=2, **Padding, sticky="w")
        self.font_size_label.grid(row=19, column=0, **Padding, sticky="e")
        self.font_size_entry.grid(row=19, column=1, **Padding, sticky="w")
        
        #save, load
        self.save_load_frame.grid(row=20,column=0, **Padding, columnspan=3, sticky="ew")   
        self.save_load_frame.grid_columnconfigure(0, weight=1)
        self.save_load_frame.grid_columnconfigure(1, weight=1)
        self.save_load_seperator.grid(row=0, column=0, columnspan=2, **Padding, sticky="ew")
        
        self.save_button.grid(row=1, column=0, **Padding)
        self.load_button.grid(row=1, column=1, **Padding)
    
    def register_global_vars(self):
        GlobalVar("input_directory", "", str, widget=self.input_dir, widget_type="entry")
        GlobalVar("output_directory", "", str, widget=self.output_dir, widget_type="entry")
        
        def conv_for_getter(interimval):
            return interimval.strip().replace("\n"," ")
        
        GlobalVar("convention_format", "", str, widget=self.convention_text, widget_type="text", getterfunc= conv_for_getter)
        GlobalVar("allvars", [], list)
        
        def get_used_vars(instance):
            result = []  # Ensure you update the global usedvars list
            for variable in gv.allvars:
                if "[" + variable + "]" in gv.convention_format:
                    result.append(str(variable))
            return result              
        
        GlobalVar("usedvars", [], list, getterfunc=get_used_vars)

     
    def register_configs(self,cm):
        cm.register("input_directory", self.input_dir,"entry","str",load_command=self.populate_variables)
        cm.register("output_directory", self.output_dir,"entry","str")
        cm.register("convention_format", self.convention_text,"text","str")
        cm.register("individual_naming_bool", self.individual_naming_bool, "checkbutton", "bool")
        cm.register("cell_area", self.cell_area,"entry", "float")
        cm.register("speed_slider", self.speed_slider, "scale", "int")
        cm.register("auto_process_bool", self.auto_process_bool, "checkbutton", "bool")
        cm.register("wait_entry", self.wait_entry, "scale", "int")
        cm.register("style_box", self.style_box, "combobox", "str", section="Init")
        cm.register("darkmode_bool", self.darkmode_bool, "checkbutton", "bool", section="Init")
        cm.register("font_size_entry", self.font_size_entry, "scale", "int", section="Init", load_command=self.apply_font_changes)
        
    def apply_mode_change(self, *ignore):
        if self.darkmode_bool.get():
            ctk.set_appearance_mode("dark") # Modes: system (default), light, dark
        else:
            ctk.set_appearance_mode("light")
        Styler.edit_style(size=self.font_size_entry.get())
    
    def apply_font_changes(self):
        Styler.edit_style(size=self.font_size_entry.get())
    
    def add_var(self):
        self.convention_text.insert("insert", "["+self.variable_list.get()+"] ")
        
    def toggle_naming(self):
        state = "disabled" if self.individual_naming.get() else "normal"
        for widget in (self.convention_text, self.variable_list, self.variable_button, self.variables_label, self.convention_label):
            widget.configure(state=state)
    
    def populate_variables(self):
        if not gv.input_directory or not os.path.isdir(gv.input_directory):
            return
        try:
            files = os.listdir(gv.input_directory)
            if not files:
                log_message("No experiment files found in the input directory.")
                return

            first_txt_file = next((f for f in files if f.lower().endswith(".txt")), None)

            if not first_txt_file:
                log_message("No .txt files found in the input directory.")
                return

            file_path = os.path.join(gv.input_directory, first_txt_file)
            with open(file_path, 'r') as f:
                lines = f.readlines()
                if len(lines) >= 4:
                    variables_line = lines[3].strip()
                    gv.allvars = variables_line.split(", ")
                    self.variable_list.configure(values=gv.allvars)
                    
        except Exception as e:
            log_message(f"Error reading file: {str(e)}", exception_info=sys.exc_info())
            
        
        
        
