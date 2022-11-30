#Import required libraries
from tkinter import *

#Create an instance of tkinter window
win =Tk()

#Define the geometry of the window
win.geometry("600x250")

#Create a text widget
text= Text(win)
text.insert(INSERT, "Hello World!")
text.insert(END, "This is a New Line")

text.pack(fill=BOTH)

#Configure the text widget with certain color
text.tag_config("start", foreground="red")
text.tag_add("start", "1.0", "1.10")

win.mainloop()