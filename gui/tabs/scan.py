import customtkinter as ctk
import tkinter as tk
from functions.utility import log_message
import os, sys
from gui import gv
from gui import Padding, Styler
from tkinter import ttk, messagebox


class scan_frame(ctk.CTkFrame):
    def __init__(self, master, master_frame):
        super().__init__(master)
        self.master_frame = master_frame
        self.create_widgets()
        self.create_layout()
        self.set_table()
        self.file_data = {}
        self.filecount = 0
        self.checking = False
    
    def create_widgets(self):
        self.files_label = ctk.CTkLabel(master=self, text="New files awaiting processing:")
        self.files_list = ttk.Treeview(master=self)
        Styler.register_func(lambda newfont: self.update_font(newfont))
        self.process_button = ctk.CTkButton(master=self,text="Process\nselected", command= lambda:self.process_items(self.files_list.selection()), width=100)
        self.process_all_button = ctk.CTkButton(master=self,text="Process\nall", command= lambda:self.process_items(self.files_list.get_children()), width=100)
        self.cancel_button = ctk.CTkButton(master=self,text="Cancel\nselected", fg_color="#D10000", hover_color="#A30000", command= lambda:self.cancel_items(self.files_list.selection()), width=100)
        self.cancel_all_button = ctk.CTkButton(master=self,text="Cancel\nall", fg_color="#D10000", hover_color="#A30000", command= self.cancel_all, width=100)
        self.awaiting_name_label = ctk.CTkLabel(master=self, text="No files in the rename buffer.")
        
    def create_layout(self):      
        self.grid_columnconfigure(0,weight=1)
        for i in range(1,4):
            self.grid_rowconfigure(i,weight=1)
        
        self.grid(row=0, column=0, **Padding, sticky="nswe")
        self.files_label.grid(row=0, column=0, **Padding, sticky="w")
        self.files_list.grid(row=1, column=0, **Padding, rowspan=4, sticky="nsew")
        self.process_button.grid(row=1, column=1, **Padding, sticky="nw")
        self.process_all_button.grid(row=2, column=1, **Padding, sticky="nw")
        self.cancel_button.grid(row=3, column=1, **Padding, sticky="nw")
        self.cancel_all_button.grid(row=4, column=1, **Padding, sticky="nw")
        self.awaiting_name_label.grid(row=5, column=0, **Padding, sticky="w")
    
    def update_font(self, newfont):
        self.files_list.tag_configure("header",font=newfont)

    
    def set_table(self):
        self.files_list.column("#0", width=10, stretch=True, anchor="w")
        self.files_list.heading("#0", text="Path")
        columns = ["Old name", "New name", "Length", "Status"]
        colwidths = [50,50,10,200]
        self.files_list.configure(columns=columns)
        for col,wdt in zip(columns,colwidths):
            self.files_list.heading(col, text=col)
            self.files_list.column(col, width=wdt,stretch=True, anchor="center")
        self.files_list.configure(displaycolumns=columns)

    def cancel_all(self):
        result = messagebox.askyesno(title="Are you sure?", default="no", icon="warning", message="Are you sure to delete all entries?")
        if result:
            self.cancel_items(self.files_list.get_children())
            
            
    def process_items(self, ids):
        if not ids:
            return
        paths = []
        for uuid in ids:
            paths.append(self.files_list.item(uuid, "text"))
            if uuid in self.file_data:
                del self.file_data[uuid]
        self.files_list.delete(*ids)
        self.master_frame.filemanager.process_files(paths) 

    def cancel_items(self, ids):
        if not ids:
            return
        for uuid in ids:
            if uuid in self.file_data:
                del self.file_data[uuid]   
        self.files_list.delete(*ids)
        
            
    def queue_file(self, file:str, newname:str="", pendingname=False):
        if not file:
            return
        file_path = os.path.join(gv.input_directory, file)
        if not os.path.exists(file_path):
            log_message(f"File not found: {file_path}")
            return
        
        self.filecount += 1        
        with open(file_path, 'r') as f:
            file_length = len(f.readlines())
        
        if pendingname:
            uuid = self.files_list.insert("", tk.END, iid=self.filecount, text=file_path, values=[file, "...Pending...", file_length, "Waiting for naming"]) 
            
        else:
            uuid = self.files_list.insert("", tk.END, iid=self.filecount, text=file_path, values=[file, newname, file_length, "Queued"])

        if self.master_frame.settings.auto_process_bool.get():
            self.file_data[uuid] = [file_path, 0, 0, file_length, pendingname] #path, iterator, issame, length
            if not self.checking:
                self.checking = True
                self.checkfiles()
        
        log_message(f"Queued file: {file}")
            
                
    def checkfiles(self):
        def update_status(uuid,status):
            vals = list(self.files_list.item(uuid, "values"))
            vals[2] = self.file_data[uuid][3]
            vals[3] = status
            self.files_list.item(uuid, values=vals)
        
        marked_for_delete = []
        marked_for_process = []
        maxsame = self.master_frame.settings.passes_entry.get()
        checktime = self.master_frame.settings.wait_entry.get()
        if not self.checking:
            return
        
        try:
            for uuid, data in self.file_data.items():
                path = data[0]
                data[1] += 1
                iterator = data[1]
                issame = data[2]
                oldlength = data[3]
                pendingname = data[4]
                
                if iterator >= 30: #iterated too many times
                    update_status(uuid, "Too many passes. Awaiting user action")
                    marked_for_delete.append(uuid)
                    continue
                
                with open(path, 'r') as f:
                    currlength = len(f.readlines())
                
                if currlength<5:
                    update_status(uuid,f"Awaiting variables for {iterator} passes")
                    continue
                else:
                    if pendingname: #rename this file first then send back here
                        marked_for_process.append(uuid)
                
                if currlength < 9:  #file has no data yet
                    update_status(uuid, f"Awaiting data for {iterator} passes")
                    continue
                        
                if currlength == oldlength:
                    data[2] += 1
                    issame = data[2]
                    update_status(uuid, f"File stable for {issame}/{maxsame} passes")
                else:
                    issame = 0
                    update_status(uuid, f"File changed since pass {iterator-1}")
                data[3] = currlength
                
                if issame >= maxsame: #filesize is same for enough passes
                    marked_for_process.append(uuid)
                
                vals = list(self.files_list.item(uuid, "values"))
                vals[2] = currlength
                self.files_list.item(uuid, values=vals)            
        except RuntimeError as e:
            if "dictionary changed size during iteration" in e:
                pass
            else:
                log_message("Error while checking files", exception_info=sys.exc_info())
            

            
        for uuid in marked_for_delete:
            if uuid in self.file_data:
                del self.file_data[uuid]
        
        if len(marked_for_process) > 0:
            self.process_items(marked_for_process)
        
        self.after(1000*checktime*60, self.checkfiles)
        
        
        

            
            
            
            

                
                    
                
                

                
                
                
                
                
                



                
                

                

                


                
                
                
                
                
                
    
        
        
        

        
        
        

            

            
            
        
    

        
        
        