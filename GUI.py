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
        self.root.after(100000)
        self.squad_name.config(text="1")


    def quitmed(self):
        self.root.quit()
        self.root.update()

def sleeper():
    time.sleep(100)
    print('done sleeping')

my_gui=Gui()


st=time.time()
breakbool_0=0
while 1:
    time.sleep(1)
    for thread in threading.enumerate():
            print(thread.name)
    if time.time()-st >2 and breakbool_0==0:
        gui_update_thread=threading.Thread(target=my_gui.update())
        gui_update_thread.start()
        breakbool_0+=1
