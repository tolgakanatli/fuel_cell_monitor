import customtkinter as ctk

class spinbox(ctk.CTkFrame):
    def __init__(self, master, min=None, max=None, increment=1, initial=0, integer=True, command=None):
        super().__init__(master, 
                         bg_color="transparent", 
                         fg_color="transparent", 
                         border_width=0, 
                         border_color=None, 
                         corner_radius=0)
        self.min = min
        self.max = max
        self.increment = increment
        self.integer = integer      
        self.command = command 
        self.string_var = ctk.StringVar(value=str(initial))
        self.last_value = initial
        
        self.vcmd = master.register(self.validate_input)
        
        self.entry = ctk.CTkEntry(master=self, 
                                  textvariable=self.string_var,
                                  validate="key",
                                  validatecommand=(self.vcmd, "%d", "%S", "%P")
                                  )
        
        self.entry.bind("<FocusOut>", self.on_entry_change)
        self.entry.bind("<Return>", self.on_entry_change)
        #self.entry.bind("<KeyRelease>", self.on_entry_change)
        self.entry.bind("<FocusIn>", self.select_all_text)
        self.increase_button = ctk.CTkButton(master=self,text="+", command = lambda: self.button_press(1), width=30)
        self.decrease_button = ctk.CTkButton(master=self,text="-", command = lambda: self.button_press(-1), width=30)
        
        
        self.grid_columnconfigure(0,weight=1)
        self.grid_rowconfigure(0,weight=1)
        self.entry.grid(row=0, column=0,sticky ="ew")
        self.decrease_button.grid(row=0,column=1,sticky ="w")
        self.increase_button.grid(row=0,column=2,sticky ="w")
       
        self.clamp(initial)

    def validate_input(self,d,S,P):

        #allow deleting
        if d !='1' or S == '':
            return True

        # Allowing only numbers, one dot, or one comma
        if not (S.isdigit() or S in ['.', ',']):  # If not a number or decimal point dont allow it
            self.bell()
            return False
        
        # Allow only one dot or comma
        decimalcount = 0
        for char in P:
            if char in ['.', ',']:
                decimalcount += 1
                if decimalcount > 1:
                    self.bell()
                    return False
        return True    

       
    def clamp(self, value=None):
        if value is None:
            try:
                value = int(self.string_var.get()) if self.integer else float(self.string_var.get())
            except ValueError:
                value = self.last_value
        
        # Clamp the value using max and min functions
        
        value = min(self.max, value) if self.max else value
        value = max(self.min, value) if self.min else value
        
        #value = max(self.min, min(self.max, value))
        value = int(value) if self.integer else float(value)
        
        self.string_var.set(str(value))
          
        #check if changed and callable
        changedandcallable = (value != self.last_value and callable(self.command))
        self.last_value = value
        return changedandcallable

    def button_press(self, sign = 1):
        var = self.string_var.get()
        try:
            value = int(var) if self.integer else float(var)
        except ValueError:
            value = self.last_value
        
        value += self.increment * sign
        shouldcall = self.clamp(value)
        
        if shouldcall:
            self.command()

  
    def on_entry_change(self, event):
        shouldcall = self.clamp()
        
        if shouldcall:
            self.command()    
    
    def select_all_text(self, event=None):
        self.entry.select_range(0, "end")
    
    def get(self):
        self.clamp()
        if self.integer:
            return int(self.string_var.get())
        else:
            return float(self.string_var.get())
        
    def getstr(self):
        self.clamp()
        return self.string_var.get()
    
    def set(self, val):
        self.string_var.set(str(val))
        self.clamp()
        
    def __getattr__(self, name):
        self.clamp()
        # Delegate attribute access to the entry widget
        return getattr(self.entry, name)
        
        

    