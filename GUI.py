import tkinter
from tkinter import ttk
import customtkinter
import time
import threading

class Gui(threading.Thread):
    [...]#costructor and other stuff
    def __init__(self,squad_name,squad_COA,squad_current_task):
        threading.Thread.__init__(self)
        self.squad_name= squad_name
        self.squad_COA = squad_COA
        self.squad_current_task = squad_current_task

        self.start()


    def run(self):
        self.root =tkinter.Tk()
        self.root.iconbitmap('Resources/icons/iai5.ico')
        self.root.title("RFA Manager")
        self.frame=tkinter.Frame(self.root)
        self.frame.pack()

        #red squad data:
        self.red_squad_frame=tkinter.LabelFrame(self.frame,text="Red Squad Data")
        self.red_squad_frame.grid(row=0, column=0,padx=20,pady=20,)

        self.squad_name_label=tkinter.Label(self.red_squad_frame, text="Squad name:")
        self.squad_name_label.grid(row=0, column=0)

        self.squad_COA_label=tkinter.Label(self.red_squad_frame, text="Squad COA:")
        self.squad_COA_label.grid(row=1, column=0)

        self.squad_current_task_label = tkinter.Label(self.red_squad_frame, text="Squad current task:")
        self.squad_current_task_label.grid(row=2, column=0)

        self.squad_name_entry=tkinter.Label(self.red_squad_frame, text=self.squad_name)
        self.squad_COA_entry=tkinter.Label(self.red_squad_frame, text=self.squad_COA)
        self.squad_current_task_entry=tkinter.Label(self.red_squad_frame, text=self.squad_current_task)
        self.squad_name_entry.grid(row=0, column=1)
        self.squad_COA_entry.grid(row=1, column=1)
        self.squad_current_task_entry.grid(row=2, column=1)

        for widget in self.red_squad_frame.winfo_children():
            widget.grid_configure(padx=10, pady=5)



        self.root.geometry("1500x240")
        self.root.resizable(False, False) # cant be resizable


        # self.squad_COA = Label(self.root, text="squad_COA", background="white").grid(row=1, column=0, sticky=W)
        # self.squad_current_task = Label(self.root, text="squad_current_task", background="white").grid(row=2, column=0, sticky=W)
        # customtkinter.set_appearance_mode("dark")
        # customtkinter.set_default_color_theme("blue")
        self.root.mainloop()


    def updatemed(self,COA,current_task):
        self.root.update()
        self.squad_COA=COA
        self.squad_COA_entry.configure(text=self.squad_COA)

        self.squad_current_task = current_task
        self.squad_current_task_entry.configure(text=self.squad_current_task)
        #print('GUI RUNNING')

    def quitmed(self):
        self.root.quit()
        self.root.update()

my_gui=Gui("anti_tank",["defend","attack","shoot"],"move_position")


# st=time.time()
# breakbool_0=0
# while 1:
#     time.sleep(0.1)
#     for thread in threading.enumerate():
#         #print(thread.name)
#         continue
#     if time.time()-st >2 and breakbool_0==0:
#         gui_update_thread=threading.Thread(target=my_gui.updatemed,args=["as"])
#         gui_update_thread.start()
#         breakbool_0+=1
