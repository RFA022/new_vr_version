import tkinter
from tkinter import ttk
import customtkinter
import time
import threading

class Gui(threading.Thread):
    [...]#costructor and other stuff
    def __init__(self,squad_name,squad_COA,squad_current_task,destination,target):
        threading.Thread.__init__(self)
        self.squad_name= squad_name
        self.squad_COA = squad_COA
        self.squad_current_task = squad_current_task
        self.destination=destination
        self.target=target

        self.start()


    def run(self):
        s_w=200
        s_h=1000
        self.root =tkinter.Tk()
        self.root.iconbitmap('Resources/icons/iai5.ico')
        self.root.title("RFA Manager")
        self.frame = tkinter.Frame(self.root)
        self.frame.pack()
        #red squad data:
        self.red_squad_frame = tkinter.LabelFrame(self.frame, text="Red Squad Data", font=('Montserrat', 10, 'bold'),fg='#f00', width=s_h-20, height=s_w-20)
        self.red_squad_frame.pack(fill="both", expand="yes")
        # self.red_squad_frame.grid(row=2, column=0, columnspan=2, sticky="E",padx=5, pady=0, ipadx=0, ipady=0)
        #
        self.squad_name_label=tkinter.Label(self.red_squad_frame, text="Squad name:" , font=('Montserrat', 10, 'bold'))
        self.squad_name_label.place(x=10, y=10, anchor="w")
        # self.squad_name_label.grid(row=0, column=0,sticky=tkinter.W)

        self.squad_COA_label=tkinter.Label(self.red_squad_frame, text="Tasks list:",font=('Montserrat', 10, 'bold'))
        self.squad_COA_label.place(x=10, y=40, anchor="w")

        #
        self.squad_current_task_label = tkinter.Label(self.red_squad_frame, text="Current task:",font=('Montserrat', 10, 'bold'))
        self.squad_current_task_label.place(x=10, y=70, anchor="w")

        self.destination_label = tkinter.Label(self.red_squad_frame, text="Geo destination:",font=('Montserrat', 10, 'bold'))
        self.destination_label.place(x=10, y=100, anchor="w")

        self.target_label = tkinter.Label(self.red_squad_frame, text="Target:",font=('Montserrat', 10, 'bold'))
        self.target_label.place(x=10, y=130, anchor="w")

        self.squad_name_entry=tkinter.Label(self.red_squad_frame, text=self.squad_name,font=('Montserrat', 10, ))
        self.squad_COA_entry=tkinter.Label(self.red_squad_frame, text=self.squad_COA,font=('Montserrat', 10, ))
        self.squad_current_task_entry=tkinter.Label(self.red_squad_frame, text=self.squad_current_task,font=('Montserrat', 10, ))
        self.destination_entry = tkinter.Label(self.red_squad_frame, text=self.destination,font=('Montserrat', 10,))
        self.target_entry = tkinter.Label(self.red_squad_frame, text=self.target,font=('Montserrat', 10,))

        self.squad_name_entry.place(x=160, y=10, anchor="w")
        self.squad_COA_entry.place(x=160, y=40, anchor="w")
        self.squad_current_task_entry.place(x=160, y=70, anchor="w")
        self.destination_entry.place(x=160, y=100, anchor="w")
        self.target_entry.place(x=160, y=130, anchor="w")

        for widget in self.root.winfo_children():
            widget.grid_configure(padx=10, pady=5)



        self.root.geometry(str(s_h)+"x"+str(s_w))
        self.root.resizable(0, 0) # cant be resizable


        # self.squad_COA = Label(self.root, text="squad_COA", background="white").grid(row=1, column=0, sticky=W)
        # self.squad_current_task = Label(self.root, text="squad_current_task", background="white").grid(row=2, column=0, sticky=W)
        # customtkinter.set_appearance_mode("dark")
        # customtkinter.set_default_color_theme("blue")
        self.root.mainloop()


    def updatemed(self,COA=None,current_task=None,destination=None,target=None):
        self.root.update()
        if COA!=None:
            self.squad_COA=COA
            self.squad_COA_entry.configure(text=self.squad_COA)

        if current_task != None:
            self.squad_current_task = current_task
            self.squad_current_task_entry.configure(text=self.squad_current_task)

        if destination!=None:
            self.destination = destination
            self.destination_entry.configure(text=self.destination)
        if target!= None:
            self.target = target
            self.target_entry.configure(text=self.target)

        #print('GUI RUNNING')

    def quitmed(self):
        self.root.quit()
        self.root.update()

# my_gui=Gui("anti_tank",["defend","attack","shoot"],"move_position","Attack position 13","LAV 2")


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
