from tkinter import *

import customtkinter
import tkinter
import time
from threading import *


class Gui:
    [...]#costructor and other stuff
    def __init__(self):
        self.root = customtkinter.CTk()
        self.root.geometry("640x320")
        self.root.iconbitmap('Resources/iai5.ico')
        self.root.title("RFA Manager")
        window = Canvas(self.root, bg='gray')
        window.pack(expand=1, fill=BOTH)
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.play()
    def play(self):
        self.root.mainloop()


gui_thread = Thread(target=Gui)
gui_thread.start()