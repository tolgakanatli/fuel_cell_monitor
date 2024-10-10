from tkinter import ttk
import tkinter as tk

__all__ = ['editable_treeview']

class editable_treeview(ttk.Treeview):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.bind("<Double-1>", lambda event: self.onDoubleClick(event))
        self.bind("<Control-a>", self.select_all)
        
    def onDoubleClick(self,event):
        ''' Executed, when a row is double-clicked. Opens 
        EntryPopup above the item's column, so it is possible
        to select text '''

        # close previous popups
        try:  # in case there was no previous popup
            self.entryPopup.destroy()
        except AttributeError:
            pass

        # what row and column was clicked on
        rowid = self.identify_row(event.y)
        column = self.identify_column(event.x)
        region = self.identify_region(event.x, event.y)
        if region != "cell":
            return
        # handle exception when header is double click
        if not rowid:
            return

        # get column position info
        x,y,width,height = self.bbox(rowid, column)

        # y-axis offset
        pady = height // 2

        # place Entry popup properly
        text = self.item(rowid, 'values')[int(column[1:])-1]
        self.entryPopup = EntryPopup(self, rowid, int(column[1:])-1, text)
        self.entryPopup.place(x=x, y=y+pady, width=width, height=height, anchor='w')
    
    def sort_column(self, col, reverse):
        """Sort treeview by a given column."""
        l = [(self.set(k, col), k) for k in self.get_children('') if self.parent(k) == '']
        try:
            l.sort(reverse=reverse, key=lambda t: float(t[0]))
        except ValueError:
            l.sort(reverse=reverse, key=lambda t: t[0])
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.move(k, '', index)
            
        # reverse sort next time
        self.heading(col, command=lambda: self.sort_column(col, not reverse))
    
    def heading(self, *args, **kwargs):
        col = args[0] if args else kwargs.get('text')
        if col and col != "#0":
            if "command" not in kwargs:
                kwargs["command"] = lambda _col=col: self.sort_column(_col, False)     
        super().heading(*args, **kwargs)


    def select_all(self, event):
        for item in self.get_children():
            self.selection_add(item)
        return 'break'  # Prevent default behavior
    
    def delete_selected(self):
        selected_items = self.selection()
        if not selected_items:
            return
        # First, delete only parents
        deletelater = []
        for item in selected_items:
            if self.item(item).get("parent")=="":
                try:
                    self.delete(item)   
                except tk.TclError:
                    continue  
            else:
                deletelater.append(item)
        
        for item in deletelater:
            try:
                self.delete(item)   
            except tk.TclError:
                continue
    
    def delete_all(self):
        self.delete(*self.get_children())


class EntryPopup(ttk.Entry):
    def __init__(self, parent, iid, column, text, **kw):
        ttk.Style().configure('pad.TEntry', padding='1 1 1 1')
        super().__init__(parent, style='pad.TEntry', **kw)
        self.tv = parent
        self.iid = iid
        self.column = column

        self.insert(0, text) 
        # self['state'] = 'readonly'
        # self['readonlybackground'] = 'white'
        # self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False

        self.focus_force()
        self.select_all()
        self.bind("<Return>", self.on_return)
        self.bind("<Control-a>", self.select_all)
        self.bind("<Escape>", lambda *ignore: self.destroy())
        self.bind("<FocusOut>", lambda *ignore: self.destroy())


    def on_return(self, event):
        rowid = self.tv.focus()
        vals = self.tv.item(rowid, 'values')
        vals = list(vals)
        vals[self.column] = self.get()
        self.tv.item(rowid, values=vals)
        self.destroy()


    def select_all(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')

        # returns 'break' to interrupt default key-bindings
        return 'break'
    
    
    
    
    
    
    
    
    
    

