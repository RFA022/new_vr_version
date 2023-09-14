import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import json
import tkinter
import threading
import Resources.mapping.vrf_map_gis as vrf_map_gis

class Gui(threading.Thread):
    [...]#costructor and other stuff
    def __init__(self,red_pos,blue_poses):
        threading.Thread.__init__(self)
        self.squad_pos_lla = red_pos
        self.blue_poses_lla = blue_poses
        if self.squad_pos_lla:
            self.squad_pos_grid = self.grid.latlon2idx(red_pos[0].red_pos[1])
        else:
            self.squad_pos_grid = [0,0]

        if self.blue_poses_lla:
            self.blue_poses_grid = self.blue_poses_lla
            for pos in self.blue_poses_grid:
                pos['loc'] = self.grid.latlon2idx(pos[0].pos[1])
        else:
            self.blue_poses_grid = [{"id":None,"loc":[0,0]}]

        self.heightmap= np.load("Resources/mapping/Height_map.npy")
        self.navmap= np.load("Resources/mapping/Nav_map.npy")


        with open(os.path.join(os.path.dirname(__file__), 'Resources/mapping/as_config.json')) as js_file:
            as_config = json.load(js_file)
        with open(os.path.join(os.path.dirname(__file__), 'Resources/mapping/map_config.json')) as js_file:
            map_config = json.load(js_file)
        self.grid = vrf_map_gis.GisEngine(map_config,as_config)

        "theme white bg"
        self.main_bg_clr = '#FFFFFF'
        self.bg_clr = "#ECDBDB"
        self.headr_clr = '#FF0000'
        self.lbl_tc = '#2F1C1C'
        self.entry_tc = '#322F2F'
        self.start()


    def run(self):

        s_w = 600
        s_h = 800



        t_size=12
        self.root =tkinter.Tk()
        self.root.iconbitmap('Resources/icons/iai7.ico')
        self.root.title("Mini Map")
        self.root.configure(background=self.main_bg_clr)
        self.frame = tkinter.Frame(self.root)
        self.frame.pack()

        fig, ax = plt.subplots(figsize=(50, 50))
        ax.imshow(self.heightmap,cmap='gist_earth',alpha=0.7, interpolation='nearest')
        ax.imshow(self.navmap,alpha=0.7,cmap='gist_gray', interpolation='nearest')

        self.scatter_red = ax.scatter(self.squad_pos_grid[0], self.squad_pos_grid[1], s=20, c='r', marker='o')
        self.scatter_blue = ax.scatter(0, 0, s=20, c='b', marker='o')
        self.scatter_blue_last_location = ax.scatter(0, 0, s=20, c='aqua', marker='o')
        self.canvas = FigureCanvasTkAgg(fig, master=self.frame)
        self.canvas.get_tk_widget().pack()


        self.root.geometry(str(s_h) + "x" + str(s_w))
        self.root.resizable(0, 0)  # cant be resizable
        self.root.mainloop()


    def updatemed(self,position=None,blues=None):
        self.root.update()
        if position!=None:
            self.squad_pos_lla = position
            self.squad_pos_grid = self.grid.latlon2idx(position[0],position[1])
            self.scatter_red.set_offsets(np.array([self.squad_pos_grid]))
        if blues!= None:
            blues_pos_array = [self.grid.latlon2idx(blue['location'][0],blue['location'][1]) for blue in blues]
            blues_last_pos_array = [self.grid.latlon2idx(blue['last_known_location'][0],blue['last_known_location'][1]) for blue in blues
                                    if blue['last_known_location'][0] is not None]
            self.scatter_blue.set_offsets(np.array(blues_pos_array))
            if blues_last_pos_array:
                self.scatter_blue_last_location.set_offsets(np.array(blues_last_pos_array))
        self.canvas.draw()


    def quitmed(self):
        self.root.quit()
        self.root.update()

# my_gui=Gui([50,50])


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
