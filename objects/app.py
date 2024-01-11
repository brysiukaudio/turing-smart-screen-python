import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
from threading import Lock
class app:

    def __init__(self,background_handler,queue,mutex):
        self.window_x = 250
        self.window_y = 190
        self.background_handler = background_handler
        self.mutex = mutex
        self.queue = queue
        self.window = Tk()
        self.window.title('KSC')
        window_string = str(self.window_x) + "x" + str(self.window_y)
        self.window.geometry(window_string)
        x = self.window.winfo_width()
        self.ff14_button = ttk.Button(self.window, text="Final Fantasy 14", command=lambda: self.on_ff14_click())
        self.ff14_button.place(x=20, y=20, height=100, width=100)

        self.climb_button = ttk.Button(self.window, text="Climbing", command=lambda: self.on_climb_click())
        self.climb_button.place(x=130, y=20, height=100, width=100)

        self.sleep_button = ttk.Button(self.window, text="Sleep", command=lambda: self.on_sleep_click())
        self.sleep_button.place(x=20, y=130, height=50, width=210)

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
            item = (False,True)
            self.queue.put(item)

    def on_climb_click(self):
        with self.mutex:
            self.background_handler.load_backgrounds("res/backgrounds/Climbing/")
            item = (False,True)
            self.queue.put(item)

    def on_sleep_click(self):
        item = (False,False)
        self.queue.put(item)

    def run(self):
        self.window.mainloop()

    def stop_event(self):
        self.window.after(10,self.stop)

    def stop(self):
        self.ff14_button.destroy()
        self.climb_button.destroy()
        self.window.destroy()
    

if __name__ == "__main__":

    mutex = Lock()
    app_gui = app("res/backgrounds/")
    app_gui.run()