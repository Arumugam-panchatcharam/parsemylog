from tkinter import *
from tkinter import ttk

from .status_bar import StatusBar
from .notebook import NoteBook
from .toolbar import ToolBar
from .explorer import Explorer

from .icons import parsemylog_logo
from .utils import get_image, position_window_center

import core.global_var as globalvar

#from parsemylog.parsemylog import logger

class View(Tk):
    """GUI Views collection class

    Args:
        Tk
    """
    def __init__(self) -> None:
        super().__init__()
        self.title(globalvar.get_val("APP_NAME"))
        icon = get_image(parsemylog_logo, (100, 100))
        self.wm_iconphoto(False, icon)
        self.rowconfigure(2,weight=1)
        self.columnconfigure(3,weight=1)
        self.w = 800
        self.h = 500
        # center the splash screen
        position_window_center(self, self.w, self.h)
        #sg = ttk.Sizegrip(self)
        #sg.grid(row=1, sticky=SE)
        self.geometry("800x500")
        self.log = globalvar.get_val("LOGGER")
        #self.wm_attributes('-transparentcolor', '#333')
        self._create_widgets()
        self._position_widgets()
        
    def _create_widgets(self):
        self.status_bar = StatusBar(self, self.log)
        self.toolbar = ToolBar(self)
        self.explorer = Explorer(self)
        self.notebook = NoteBook(self)

    def _position_widgets(self):
        self.toolbar.grid(row=0, column=0, rowspan=3, sticky='nsew')
        self.explorer.grid(row=0, column=1,columnspan=1, rowspan=3, sticky='nsew')
        self.notebook.grid(row=0, column=2, rowspan=3, columnspan=4, sticky='nsew')
        self.status_bar.grid(row=3, column=0, columnspan=4, sticky='ew')

    def start_mainloop(self) -> None:
        self.mainloop()