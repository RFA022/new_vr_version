import tkinter as tk
import random

class Example(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.ticker = tk.Text(height=1, wrap="none")
        self.ticker.pack(side="top", fill="x")

        self.ticker.tag_configure("up", foreground="green")
        self.ticker.tag_configure("down", foreground="red")
        self.ticker.tag_configure("event", foreground="black")

        self.data = ["AAPL", "GOOG", "MSFT"]
        self.after_idle(self.tick)

    def tick(self):
        symbol = self.data.pop(0)
        self.data.append(symbol)

        n = random.randint(-1,1)
        tag = {-1: "down", 0: "even", 1: "up"}[n]

        self.ticker.configure(state="normal")
        self.ticker.insert("end", " %s %s" % (symbol, n), tag)
        self.ticker.see("end")
        self.ticker.configure(state="disabled")
        self.after(1000, self.tick)

if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()