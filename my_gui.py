import Tkinter


class Window:
    def __init__(self, message):
        input = ""
        self.window = Tkinter.Tk()
        self.l = Tkinter.Label(self.window, text=message)
        self.l.pack(side=Tkinter.LEFT)
        self.e = Tkinter.Entry(self.window)
        self.e.pack(side=Tkinter.RIGHT)
        #self.b = Tkinter.Button(self.window, borderwidth=4, text="Scan", width=10, pady=8, command=self.get_search(None))
        #self.b.pack(side=Tkinter.BOTTOM)
        self.window.bind('<Return>', self.get_search)
        self.l.focus_set()
        self.window.mainloop()

    def get_search(self, event):
        txt = self.e.get()
        self.input = txt
        self.window.destroy()
