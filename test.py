import tkinter as Tkinter

form = Tkinter.Tk()

errorArea = Tkinter.LabelFrame(form, text=" Errors ", width=250, height=80)
errorArea.grid(row=2, column=0, columnspan=2, sticky="E", \
             padx=5, pady=0, ipadx=0, ipady=0)

errorMessage = Tkinter.Label(errorArea, text="")

# 1) 'x' and 'y' are the x and y coordinates inside 'errorArea'
# 2) 'place' uses 'anchor' instead of 'sticky'
# 3) There is no need for 'padx' and 'pady' with 'place'
# since you can specify the exact coordinates
errorMessage.place(x=10, y=10, anchor="w")

form.mainloop()