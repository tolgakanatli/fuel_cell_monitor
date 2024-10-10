from gui.tabs.main import main_window           
try:
    import pyi_splash # type: ignore
except:
    pass
       
if __name__ == "__main__":
    try:    
        pyi_splash.update_text("Generating GUI...")
    except:
        pass    
    
    app = main_window()   

    try:    
        pyi_splash.close()
    except:
        pass

    app.main_frame.configmanager.load_config()
    
    app.mainloop()
