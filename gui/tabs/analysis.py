import customtkinter as ctk
import os, sys
from tkinter import messagebox, filedialog
from ..widgets.editable_treeview import editable_treeview
import pandas as pd
from gui import const, Padding, Styler
from functions.GlobalVars import GlobalVar, GlobalVars
gv = GlobalVars()


# Add the root directory to the Python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from functions.utility import log_message

class analysis_frame(ctk.CTkFrame):
    def __init__(self, master, master_frame):
        super().__init__(master)
        self.master_frame = master_frame
        self.grid(row=0, column=0, **Padding, sticky="nswe")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.analysis_list = editable_treeview(master=self, height=15)
        GlobalVar("treevars", [], list)
        Styler.register_func(lambda newfont: self.update_font(newfont))
        analysis_scrollbar_y = ctk.CTkScrollbar(master=self, orientation="vertical", command=self.analysis_list.yview)
        analysis_scroolbar_x = ctk.CTkScrollbar(master=self, orientation="horizontal", command=self.analysis_list.xview)

        self.analysis_list.configure(yscrollcommand = analysis_scrollbar_y.set, xscrollcommand = analysis_scroolbar_x.set)
        self.analysis_list.column("#0", width=200, stretch=False, anchor="w")
        self.analysis_list.heading("#0", text="Filename")

        an_save_button= ctk.CTkButton(master=self, text="Save", command=self.save_analysis, width=100)
        an_load_button= ctk.CTkButton(master=self, text="Load \nexperiments", command=self.an_load_files, width=100)
        an_delete_button = ctk.CTkButton(master=self, text = "Delete \nselected", command=self.analysis_list.delete_selected, width=100,fg_color="#D10000", hover_color="#A30000")
        an_delete_all_button = ctk.CTkButton(master=self, text = "Delete \nall", command=self.reset_tree_button, width=100,fg_color="#D10000", hover_color="#A30000")

        self.analysis_list.grid(row=0, column=0, **Padding, rowspan=4, sticky="ewns")
        analysis_scrollbar_y.grid(row=0, column=1, **Padding, rowspan=4, sticky="ns")
        analysis_scroolbar_x.grid(row=4, column=0, **Padding, sticky = "ew")

        an_save_button.grid(row=0, column=2, **Padding, sticky="w")
        an_load_button.grid(row=1, column=2, **Padding, sticky="w")
        an_delete_button.grid(row=2, column=2, **Padding, sticky="w")
        an_delete_all_button.grid(row=3, column=2, **Padding, sticky="w")
        
    def reset_tree_button(self):
        result = messagebox.askyesno(title="Are you sure?", default="no", icon="warning", message="Are you sure to delete all entries?")
        if result:
            self.reset_tree()
    def update_font(self, newfont):
        self.analysis_list.tag_configure("header",font=newfont)
        
    def save_analysis(self):
        dfs =[]
        colcount = len(gv.usedvars)
        for parent in self.analysis_list.get_children(""):
            allitems = list()
            allitems.append(("filename",self.analysis_list.item(parent).get("text"),""))
            parentdata = self.analysis_list.item(parent).get("values")[:colcount]
            for data, name in zip(parentdata, gv.usedvars):
                allitems.append((name,data,""))
            allitems.append(const.dataheaders_long)
            for child in self.analysis_list.get_children(parent):
                childdata = self.analysis_list.item(child).get("values")[-3:]
                allitems.append(childdata)
            parent_df = pd.DataFrame(allitems)
            dfs.append(parent_df)
        if dfs.__len__()==0:
            log_message("nothing to save")
            return
        result_df = pd.concat(dfs, axis=1)
        file = filedialog.asksaveasfilename(initialdir=gv.output_directory,
                                            filetypes=(("Excel file",".xlsx"),),
                                            defaultextension=".xslx")
        if not file:
            log_message("saving cancelled by user")
            return
        try:
            result_df.to_excel(file, header=False, index=False, engine='openpyxl')
        except Exception as e:
            log_message(f"Couldnt't save the file: {str(e)}", exception_info=sys.exc_info())
            return
        log_message(f"File saved as: {file}")
    
    def an_load_files(self):
        files = filedialog.askopenfilenames(initialdir=gv.input_directory,
                                            filetypes=(("Text files",".txt"),))
        if files:
            self.master_frame.filemanager.process_files(files,analyzeonly=True)
        else:
            log_message("no files selected")
    
    def reset_tree(self):
        self.analysis_list.delete_all()
        #self.master_frame.settings.update_global_vars()
        
        gv.treevars = []
        gv.treevars.extend(gv.usedvars)
        gv.treevars.extend(const.dataheaders_long)
        self.analysis_list.configure(displaycolumns=[])
        self.analysis_list.configure(columns=gv.treevars)
        for variable in gv.treevars:
            self.analysis_list.heading(variable, text=variable)
            self.analysis_list.column(variable, width=120, stretch=True, anchor="center") 
        self.analysis_list.configure(displaycolumns=gv.treevars)

    



