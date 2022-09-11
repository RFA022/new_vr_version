from tkinter import *
import customtkinter
import time
from threading import *


class Gui:
    [...]#costructor and other stuff
    def __init__(self):
        self.root = customtkinter.CTk()
        #self.root = Tk()

        self.root.geometry("640x320")
        self.root.iconbitmap('Resources/iai5.ico')
        self.root.title("RFA Manager")
        self.root.resizable(False, False) # cant be resizable
        window = Canvas(self.root, bg='white')
        window.pack(expand=1, fill=BOTH)
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")

        "packing labels and text:"

        squad_name = Label(self.root, text="Anti Tank Squad")
        squad_name.pack(pady=1)


    def play(self):
        self.root.mainloop()



    def update(self, COA):
        self.root.squad_name.config(text="1")


my_gui=Gui()


gui_thread = Thread(target=my_gui.play())
gui_thread.start()

time.sleep(2)
print("s")