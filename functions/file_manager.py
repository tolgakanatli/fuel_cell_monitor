import pandas as pd
import os, sys, shutil
from gui import const
from .utility import format_number, log_message
from tkinter import simpledialog, messagebox
from .FlexibleLoop import FlexibleWhile
from .GlobalVars import GlobalVars
gv = GlobalVars()

def files_are_identical(file1_path, file2_path):
    try:
        with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2:
            while True:
                chunk1 = file1.read(4096)
                chunk2 = file2.read(4096)
                
                if chunk1 != chunk2:
                    return False
                
                if not chunk1:  # End of file
                    return True
    except IOError as e:
        log_message(f"Error reading files: {str(e)}", exception_info=sys.exc_info())
        return False

def prompt_for_filename(default_filename):
    if default_filename.endswith(".txt"):
        default_filename = default_filename[:-4]
    new_filename = simpledialog.askstring("Filename Input", f"Enter new filename for {default_filename}:", initialvalue=default_filename)
    return new_filename + ".txt" if new_filename else None

def is_file_closed(file_path):
    # Check if the file exists first
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    
    #tries to rename the file to its own name, windows will not allow if the file is open somewhere.
    try:
        os.rename(file_path, file_path)
        return True
    except OSError:
        return False


class FileManager():
    def __init__(self, master_frame):
        self.master_frame = master_frame
        self.waiting_list = {}
        self.waiting_bool = False
        self.file_count = 0  

    def wait_for_names(self, name:str = None, path:str = None):
        
        if name and path:
            self.waiting_list[path] = [name,0]
            if self.waiting_bool:
                return
     
        if not self.waiting_list: # waiting list is empty
            self.master_frame.scan.awaiting_name_label.configure(text="No files in the renaming buffer.")
            self.waiting_bool = False
            return
        else:
            self.master_frame.scan.awaiting_name_label.configure(text=f"Renaming buffer has {len(self.waiting_list)} items")
            self.waiting_bool = True

        mark_for_delete = []
        mark_for_process = []
        
        for path, vals in self.waiting_list.items():
            vals[1] += 1
            if vals[1]> 120: #too many iterations
                log_message(f"File {vals[0]} took too long to get a name. Cancelling.")
                mark_for_delete.append(path)
                continue
            
            with open(path, 'r') as f:
                length = len(f.readlines())
            if length>=5: #it got a name
                mark_for_process.append(vals[0])
                mark_for_delete.append(path)
        
        if len(mark_for_delete)>0:
            for item in mark_for_delete:
                del self.waiting_list[item]
        
        if len(mark_for_process)>0:
            self.process_files(mark_for_process)
        
        if self.waiting_bool:
            self.master_frame.after(5000,self.wait_for_names)             

    def process_files(self, files, analyzeonly=False):    
        individual_naming_bool = self.master_frame.settings.individual_naming_bool
        analysis_list = self.master_frame.analysis.analysis_list
        cell_area = self.master_frame.settings.cell_area
    
        def get_vals(lines, number=False):
            variable_names = lines[3].strip().split(", ")
            variable_values = lines[4].strip().split(",")
            var_vals = {}
            for variable in gv.usedvars:
                index = variable_names.index(variable)
                value = format_number(variable_values[index], asnumber=number)
                var_vals[variable] = value
            return var_vals
                    
        def get_convention_filename(vals):
            final_filename = gv.convention_format
            for key, value in vals.items():
                final_filename = final_filename.replace(f"[{key}]", value)
            return final_filename
        
        def get_filename(lines):
            final_filename = get_convention_filename(get_vals(lines))
            # Individual naming
            if individual_naming_bool.get():
                new_filename = None
                while not new_filename:
                    new_filename = prompt_for_filename(final_filename)
                final_filename = new_filename
            #append .txt
            if not final_filename.endswith(".txt"):
                final_filename += ".txt"
            return final_filename
        
        def copy_file(input_file, output_file):
            input_path = os.path.join(gv.input_directory, input_file)
            output_path = os.path.join(gv.output_directory, output_file)
            copyit = True
            #check for existing files, if exists add _2 to the name                
            if os.path.exists(output_path):
                if files_are_identical(input_path, output_path):
                    copyit = False                  
                log_message(f"File {output_file} already exists. Finding a new filename")

                for output_path, i in FlexibleWhile(before_func=lambda p, i: (os.path.join(gv.output_directory, f"{output_file[:-4]} ({i}).txt"),i+1),
                                            cond_func= lambda p,i: os.path.exists(p),
                                            start_vals= ("", 2)):
                    if files_are_identical(input_path,output_path):
                        copyit = False
                                 
            final_filename = os.path.basename(output_path)
            final_filename = os.path.splitext(final_filename)[0]
            
            if copyit:                           
                shutil.copy(input_path, output_path)
                log_message(f"Copied {filename} as {final_filename}")
            else:
                log_message(f"identical files detected. skipping {final_filename}")
        
        if not gv.output_directory or not os.path.isdir(outdir := gv.output_directory):
            result = messagebox.askyesno(title="Create directory?", default="yes", icon="warning", message=f"The output directory {outdir} does not exist. Do you want to create it?")
            if result:
                try:
                    os.makedirs(outdir)
                except OSError as e:
                    log_message(f"Error creating output directory: {str(e)}")
                    return   
            else:  
                log_message("Please select a valid output directory.")
                return 
    
        try:
            for filename in files:
                log_message(f"Processing file {filename}...")             
                file_path = os.path.join(gv.input_directory, filename)
                if not os.path.exists(file_path):
                    log_message(f"{file_path} does not exist.")
                    continue
                
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                
                if not analyzeonly:
                    if len(lines) < 5: #check if we can't get the name
                        log_message(f"File {filename} does not have variables. Waiting for vars.")
                        self.wait_for_names(filename,file_path)
                        continue
                    
                    else: #get the name
                        final_filename = get_filename(lines) 
                        log_message(f"{filename} will be copied as {final_filename}")            

                    if len(lines) < 9: #queue file
                        log_message(f"File {filename} does not have data yet. Queuing...")
                        self.master_frame.scan.queue_file(filename,final_filename)
                        continue
                    else:
                        copy_file(filename,final_filename)
                else:
                    if len(lines) < 9:
                        log_message(f"File {filename} is incomplete.")  
                        continue
                    
                    if os.path.dirname(filename) == gv.input_directory:
                        final_filename = get_filename(lines)
                        copy_file(filename,final_filename) 
                    else:
                        final_filename = os.path.basename(filename)   
                        log_message(f"{final_filename} added for analysis")            

                #set treeview columns if first file
                if self.file_count == 0: self.master_frame.analysis.reset_tree()
                
                self.file_count += 1
                var_vals = list(get_vals(lines, number=True).values())
                
                #calculate densities and max values
                df = pd.DataFrame([val.strip().split(',') for val in lines[7:]], columns=const.dataheaders)
                df = df.apply(pd.to_numeric, errors='coerce')
                area = float(cell_area.get()) if float(cell_area.get()) else 1                
                df[["Current", "Power"]] = df[["Current", "Power"]] * (1000 / area)
                df = df.round(2)
                maxid = df["Power"].idxmax()                             
                var_vals.extend(df.loc[maxid].to_list())
                
                #input data into the treeview
                just_filename = os.path.splitext(final_filename)[0]                        
                iid = analysis_list.insert(parent="", index="end",text=just_filename, values=var_vals)
                start_column = len(analysis_list['columns']) - 3
                for row in df.itertuples(index=False):
                    empty_row = [""] * start_column
                    empty_row.extend(row)
                    analysis_list.insert(parent=iid, index="end", values=empty_row)                
                    
        except Exception as e:
            log_message(f"Error processing files: {str(e)}", exception_info=sys.exc_info())


    def check_new_files(self, iterator = 0):
        if iterator == 0:
            #self.master_frame.settings.update_global_vars()
            self.last_checked_files = set(os.listdir(gv.input_directory))

        sleeptime = self.master_frame.settings.speed_slider.get()
        iterator += 1
                  
        if not gv.scanning: return
        
        try:
            files = os.listdir(gv.input_directory)
            new_files = [f for f in files if f.lower().endswith(".txt") and f not in self.last_checked_files]
            if len(new_files)>0:
                log_message(f"Found {len(new_files)} new files. Processing...")
                self.process_files(new_files)
                self.last_checked_files.update(new_files)
        except Exception as e:
            log_message(f"Error monitoring files: {str(e)}") 
        
        self.master_frame.after(sleeptime*1000,lambda:self.check_new_files(iterator))