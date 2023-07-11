from tkinter import *
from tkinter import ttk

from .utils import get_button_image

class ToolBar(ttk.Frame):
    """GUI Left Side Toolbar

    Args:
        ttk.Frame
    """
    def __init__(self, container) -> None:
        super().__init__(container)
        
        # style
        toolbar_style = ttk.Style()
        toolbar_style.configure("toolbar.Toolbutton", font=("Helvetica", 10),
                                  background='#777',
                                  padding=[10,10],
                                  relief=FLAT,
                                  )
        
        toolbarframe_style = ttk.Style()
        toolbarframe_style.configure("toolbar.TFrame",
                                     background="#777",
                                     padding=[5,5]
                                     )

        # Widgets
        fimg = get_button_image("file.ico", (30, 30))
        self.file_open = ttk.Button(self, image=fimg, style='toolbar.Toolbutton')
        self.file_open.image = fimg
        self.file_open.pack(side=TOP, expand=False)

        fimg = get_button_image("folder.ico", (30, 30))
        self.folder_open = ttk.Button(self, image=fimg, style='toolbar.Toolbutton')
        self.folder_open.image = fimg
        self.folder_open.pack(side=TOP, expand=False)

        # current Frame config
        self.config(relief=FLAT, style="toolbar.TFrame")
