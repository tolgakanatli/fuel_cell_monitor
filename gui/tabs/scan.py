import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import os, sys
from dataclasses import dataclass
from datetime import timedelta
import functions.file_processing as fp
from functions.utility import log_message
from gui import gv
from gui import Padding, Styler


@dataclass
class file_data:
    path:str
    size:float = 0
    iterator:int = 0
    same_for:int = 0
    pendingname:bool=False
    
    
    
    

class scan_frame(ctk.CTkFrame):
    def __init__(self, master, master_frame):
        super().__init__(master)
        self.master_frame = master_frame
        self.create_widgets()
        self.create_layout()
        self.set_table()
        self.monitored_files = {}
        self.filecount = 0
        self.checking = False
        self.fm:'fp.FileManager' = master_frame.filemanager

    def create_widgets(self):
        self.files_label = ctk.CTkLabel(master=self, text="New files awaiting processing:")
        self.files_list = ttk.Treeview(master=self)
        Styler.register_func(lambda newfont: self.update_font(newfont))
        self.process_button = ctk.CTkButton(master=self,text="Process\nselected", command= lambda:self.process_items(self.files_list.selection()), width=100)
        self.process_all_button = ctk.CTkButton(master=self,text="Process\nall", command= lambda:self.process_items(self.files_list.get_children()), width=100)
        self.cancel_button = ctk.CTkButton(master=self,text="Cancel\nselected", fg_color="#D10000", hover_color="#A30000", command= lambda:self.cancel_items(self.files_list.selection()), width=100)
        self.cancel_all_button = ctk.CTkButton(master=self,text="Cancel\nall", fg_color="#D10000", hover_color="#A30000", command= self.cancel_all, width=100)
        self.montioring_label = ctk.CTkLabel(master=self, text="Not monitoring any files.")
        
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
        self.montioring_label.grid(row=5, column=0, **Padding, sticky="w")
    
    def update_font(self, newfont):
        self.files_list.tag_configure("header",font=newfont)

    
    def set_table(self):
        self.files_list.column("#0", width=10, stretch=True, anchor="w")
        self.files_list.heading("#0", text="Path")
        columns = ["Old name", "New name", "Size (KB)", "Status"]
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
        newnames = []
        for uuid in ids:
            path = self.files_list.item(uuid, "text")
            size = os.path.getsize(path) // 1024 #get size in kb
            if size > 0:
                newname = self.files_list.item(uuid, "values")[1]
                if newname == "...Pending...":
                    newname = self.fm.get_filename(path)    
                paths.append(path)
                newnames.append(newname)
            else:
                log_message("File size is 0. Skipping")
            
            if uuid in self.monitored_files:
                del self.monitored_files[uuid]
        
        self.fm.process_files(paths, newnames=newnames)
        self.files_list.delete(*ids)

    def cancel_items(self, ids):
        if not ids:
            return
        for uuid in ids:
            if uuid in self.monitored_files:
                del self.monitored_files[uuid]   
        self.files_list.delete(*ids)
        
    def new_file(self, file:str): #a new file will be processed
        file = fp.resolve_path(file)
        if not fp.file_exists(file): return #basic check
        log_message(f"New file is added for scanning {file}")
        if fp.has_vars(file): #has variables
            newname = self.fm.get_filename(file)
            self.queue_file(file, newname, pendingname=False)
        else: #wait for naming
            log_message(f"New file has no name. waiting for name")
            self.queue_file(file,"...Pending...", pendingname=True)         
 
            
    def queue_file(self, file:str, newname:str="", pendingname=False):
        self.filecount += 1
        log_message(f"File {self.filecount} queued {file} with new name {newname}")    
        file_size = os.path.getsize(file) // 1024
        filename = os.path.splitext(os.path.basename(file))[0]
        if pendingname:
            uuid = self.files_list.insert("", tk.END, iid=self.filecount, text=file, values=[filename, "...Pending...", file_size, "Waiting for naming"]) 
            
        else:
            uuid = self.files_list.insert("", tk.END, iid=self.filecount, text=file, values=[filename, newname, file_size, "Queued"])


        self.monitored_files[uuid] = file_data(path=file, size=file_size, pendingname=pendingname)
        
        if not self.checking:
            self.montioring_label.configure(text="Monitoring files...")
            self.checking = True
            self.checkfiles()
        
        log_message(f"Queued file: {file}")
            

    def checkfiles(self):
        def update_status(uuid, status):
            vals = list(self.files_list.item(uuid, "values"))
            vals[2] = self.monitored_files[uuid].size # Update file size in KB
            vals[3] = status
            self.files_list.item(uuid, values=vals)

        auto_process: bool =  self.master_frame.settings.auto_process_bool.get()
        check_interval = self.master_frame.settings.wait_entry.get() # Check every n seconds

        if not self.checking:
            return
        marked_for_delete = []
        try:
            data:'file_data'
            for uuid, data in self.monitored_files.items():
                data.size = os.path.getsize(self.monitored_files[uuid].path) // 1024 #get size in kb
                data.iterator += 1
                if fp.is_file_closed(data.path):
                    if data.size > 0:
                        marked_for_delete.append(uuid) 
                        
                        if auto_process:
                            update_status(uuid, "Closed. Autoprocess in 5s")
                            self.after(5000, lambda f = uuid: self.process_items([f]))

                        else:
                            update_status(uuid, "Closed. Ready for manual processsing")
                    else:
                        data.same_for += 1
                        samefor = timedelta(seconds=(data.same_for * check_interval))
                        update_status(uuid, f"File is closed, but size is 0 for {samefor}")
                    
                else:
                    openfor = timedelta(seconds=(data.iterator * check_interval))
                    update_status(uuid, "Open for " + str(openfor))

        except RuntimeError as e:
            if "dictionary changed size during iteration" in e:
                pass
            else:
                log_message("Error while checking files", exception_info=sys.exc_info())
        
        if len(marked_for_delete) > 0:
            for uuid in marked_for_delete:
                del self.monitored_files[uuid]

        if len(self.monitored_files) == 0:
            self.montioring_label.configure(text="Not monitoring any files.")
            self.checking = False
        else:
            self.after(check_interval * 1000, self.checkfiles)

    


        
        
        

            
            
            
            

                
                    
                
                

                
                
                
                
                
                



                
                

                

                


                
                
                
                
                
                
    
        
        
        

        
        
        

            

            
            
        
    

        
        
        