import tkinter
from tkinter import ttk
import customtkinter
import time
import threading
import ttk
from PIL import ImageTk, Image

class Gui(threading.Thread):
    [...]#costructor and other stuff
    def __init__(self,squad_name,squad_COA,squad_current_task,destination,target):
        threading.Thread.__init__(self)
        self.squad_name= squad_name
        self.squad_COA = squad_COA
        self.squad_current_task = squad_current_task
        self.destination=destination
        self.target=target

        "theme white bg"
        self.main_bg_clr = '#FFFFFF'
        self.bg_clr = "#d9463e"
        self.headr_clr = '#000000'
        self.lbl_tc = '#FFFFFF'
        self.entry_tc = '#322F2F'

        self.start()


    def run(self):

        dist=30
        x_cl=30
        y_cl=60
        s_w = 2*y_cl+5*dist-30
        s_h = 1000



        t_size=10
        self.root =tkinter.Tk()
        self.root.iconbitmap('Resources/icons/iai7.ico')
        self.root.title("Red Force Agent")
        self.root.configure(background=self.main_bg_clr)
        self.frame = tkinter.Frame(self.root,)
        self.frame.pack()


        #red squad data:



        self.red_squad_frame = tkinter.LabelFrame(self.frame,background=self.bg_clr, width=s_h-20, height=s_w-10)
        self.red_squad_frame.pack(fill="both", expand="yes", anchor="center")

        header = tkinter.Label(self.red_squad_frame, text="Red Squad Manager", background=self.bg_clr,fg=self.headr_clr,font=('Montserrat', t_size+2, 'bold'))
        header.place(x=x_cl, y=15, anchor="w")

        header2 = tkinter.Label(self.red_squad_frame, text="Long Range Anti Tank Squad", background=self.bg_clr, fg=self.headr_clr, font=('Brush Script Std', t_size-2, 'bold'))
        header2.place(x=x_cl, y=15+20, anchor="w")

        self.squad_name_label=tkinter.Label(self.red_squad_frame, text="Squad name:" ,background=self.bg_clr,fg=self.lbl_tc,font=('Montserrat', t_size, 'bold'))
        self.squad_name_label.place(x=x_cl, y=y_cl, anchor="w")
        # self.squad_name_label.grid(row=0, column=0,sticky=tkinter.W)

        self.squad_COA_label=tkinter.Label(self.red_squad_frame, text="Plan:",background=self.bg_clr,fg=self.lbl_tc,font=('Montserrat', t_size, 'bold'))
        self.squad_COA_label.place(x=x_cl, y=y_cl+dist, anchor="w")

        #
        self.squad_current_task_label = tkinter.Label(self.red_squad_frame, text="Current task:",background=self.bg_clr,fg=self.lbl_tc,font=('Montserrat', t_size, 'bold'))
        self.squad_current_task_label.place(x=x_cl, y=y_cl+2*dist, anchor="w")

        self.destination_label = tkinter.Label(self.red_squad_frame, text="Geo destination:",background=self.bg_clr,fg=self.lbl_tc,font=('Montserrat', t_size, 'bold'))
        self.destination_label.place(x=x_cl, y=y_cl+3*dist, anchor="w")

        self.target_label = tkinter.Label(self.red_squad_frame, text="Target:",background=self.bg_clr,fg=self.lbl_tc,font=('Montserrat', t_size, 'bold'))
        self.target_label.place(x=x_cl, y=y_cl+4*dist, anchor="w")

        self.squad_name_entry=tkinter.Label(self.red_squad_frame, text=self.squad_name,background=self.bg_clr,font=('Montserrat', t_size, ), fg=self.entry_tc)
        self.squad_COA_entry=tkinter.Label(self.red_squad_frame, text=self.squad_COA,background=self.bg_clr,font=('Montserrat', t_size, ), fg=self.entry_tc)
        self.squad_current_task_entry=tkinter.Label(self.red_squad_frame, text=self.squad_current_task,background=self.bg_clr,font=('Montserrat', t_size, ), fg=self.entry_tc)
        self.destination_entry = tkinter.Label(self.red_squad_frame, text=self.destination,background=self.bg_clr,font=('Montserrat', t_size,), fg=self.entry_tc)
        self.target_entry = tkinter.Label(self.red_squad_frame, text=self.target,background=self.bg_clr,font=('Montserrat', t_size,), fg=self.entry_tc)

        self.squad_name_entry.place(x=160, y=y_cl, anchor="w")
        self.squad_COA_entry.place(x=160, y=y_cl+dist, anchor="w")
        self.squad_current_task_entry.place(x=160, y=y_cl+2*dist, anchor="w")
        self.destination_entry.place(x=160, y=y_cl+3*dist, anchor="w")
        self.target_entry.place(x=160, y=y_cl+4*dist, anchor="w")

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
        if len(COA)==0:
            self.squad_COA=None
        self.squad_COA_entry.configure(text=self.squad_COA)
        if current_task != None:
            self.squad_current_task = current_task
            if current_task!='Planning':
                self.squad_current_task_entry.configure(text=self.squad_current_task,fg=self.entry_tc)
            else:
                self.squad_current_task_entry.configure(text=self.squad_current_task,fg="#EED909")

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
