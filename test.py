# Import the required libraries
from tkinter import *

# Create an instance of tkinter frame
win= Tk()

# Define the size of the window
win.geometry("700x300")

# Function to change the color of the canvas
def change_color():
   canvas.configure(bg='blue')

# Create a canvas widget
canvas= Canvas(win, bg='skyblue')
canvas.pack()

# Create a button
button=Button(win, text= "Change Color", font=('Helvetica 10 bold'), command=change_color)
button.pack()

win.mainloop()