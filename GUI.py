from tkinter import *
import customtkinter
import time
import threading

class Gui(threading.Thread):
    [...]#costructor and other stuff
    def __init__(self):
        threading.Thread.__init__(self)
        self.start()


    def run(self):
        self.root = customtkinter.CTk()
        self.root.geometry("640x320")
        self.root.iconbitmap('Resources/iai5.ico')
        self.root.title("RFA Manager")
        self.root.resizable(False, False) # cant be resizable

        self.squad_name = Label(self.root, text="Anti Tank Squad")
        self.squad_name.pack()
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.root.mainloop()


    def update(self):
        time.sleep(3)
        self.squad_name.config(text="1")
my_gui=Gui()


t2 = threading.Thread(target=my_gui.update)
t2.start()
while 1:
    for thread in threading.enumerate():
            print(thread.name)
