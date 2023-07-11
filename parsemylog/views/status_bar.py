from tkinter import *
from tkinter import ttk

import core.global_var as globalvar

class StatusBar(ttk.Frame):
    """GUI status Bar

    Args:
        ttk.Frame
    """
    def __init__(self, container, log) -> None:
        super().__init__(container)
        # Variables
        self.log = log
        self.path = StringVar()
        # style
        statusbar_style = ttk.Style()
        statusbar_style.configure("statusbar.TLabel", font=("Helvetica", 10),
                                  foreground="white",
                                  background="#06e",
                                  padding=[10,2],
                                  )

        # Widgets
        self.pathlabel = ttk.Label(self, textvariable=self.path,
                                   relief=FLAT,
                                   justify=CENTER,
                                   anchor=W,
                                   style="statusbar.TLabel")

        self.pathlabel.pack(side=LEFT, ipadx=20, fill=BOTH, expand=True)

        version = globalvar.get_val("APP_VERSION")
        app_name = globalvar.get_val("APP_NAME")
        self.verlabel = ttk.Label(self, text=app_name + ' ' + version,
                                   relief=FLAT,
                                   justify=CENTER,
                                   anchor=SE,
                                   style="statusbar.TLabel")
        self.verlabel.pack(side=RIGHT, ipadx=20, fill=BOTH, expand=True)
        #self.pathlabel = Label(self, textvariable=self.path, relief=FLAT,justify=LEFT, anchor=W, background="blue")
        #self.pathlabel.pack(side="left", fill="both", expand=True)

        # curent Frame config
        self.config(relief="flat")

    def set_path(self, path):
        self.path.set(path)
