import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
from threading import Lock
class app:

    def __init__(self,background_handler,mutex):
        self.window_x = 250
        self.window_y = 140
        self.background_handler = background_handler
        self.mutex = mutex
        self.window = Tk()
        self.window.title('KSC')
        window_string = str(self.window_x) + "x" + str(self.window_y)
        self.window.geometry(window_string)
        x = self.window.winfo_width()
        self.ff14_button = ttk.Button(self.window, text="Final Fantasy 14", command=lambda: self.on_ff14_click())
        self.ff14_button.place(x=20, y=20, height=100, width=100)

        self.ff14_button = ttk.Button(self.window, text="Climbing", command=lambda: self.on_climb_click())
        self.ff14_button.place(x=130, y=20, height=100, width=100)

        self.window.protocol("WM_DELETE_WINDOW",self.on_closing)

    def on_closing(self):
        self.window.withdraw()

    def resume_window_event(self):
        self.window.after(10,self.resume_window())

    def resume_window(self):
        self.window.deiconify()

    def on_ff14_click(self):
        with self.mutex:
            self.background_handler.load_backgrounds("res/backgrounds/FF14/")

    def on_climb_click(self):
        with self.mutex:
            self.background_handler.load_backgrounds("res/backgrounds/Climbing/")


    def run(self):
        self.window.mainloop()

    def stop_event(self):
        self.window.after(10,self.stop)

    def stop(self):
        self.ff14_button.destroy()
        self.window.destroy()
    

if __name__ == "__main__":

    mutex = Lock()
    app_gui = app("res/backgrounds/")
    app_gui.run()