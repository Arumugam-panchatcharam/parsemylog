from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk

from models.main import Model
from views.main import View

from tkinter import filedialog, messagebox
from pathlib import Path
import core.global_var as globalvar

class ToolBarController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.log = globalvar.get_val("LOGGER")
        self.toolbar = self.view.toolbar

        # Variables
        self.file_open_filename = Path()
        self.folder_open_foldername = Path()
        self._bind()

    def _bind(self) -> None:
        self.toolbar.file_open.config(command=self.open_log_file)
        self.toolbar.folder_open.config(command=self.open_log_folder)

    def open_log_file(self):
        filetypes = (
        ('text files', '*.txt'),
        ('All files', '*.*')
        )
        self.file_open_filename = filedialog.askopenfilename(title="Open a Log file",
                                                             initialdir=Path.home(),
                                                             filetypes=filetypes)
        self.log.debug(self.file_open_filename)
        self.view.status_bar.set_path(self.file_open_filename)
        self.toolbar.file_open['state']=NORMAL

        # populate path
        self.view.explorer.populate_path(self.file_open_filename)

        # invoke logformatparser model
        self.model.log_format_parser.set_path(self.file_open_filename)
        self.model.log_format_parser.ParseLogs()
        
    
    def open_log_folder(self):
        self.folder_open_foldername = filedialog.askdirectory(title="Open a Log folder",
                                                             initialdir=
                                                             self.folder_open_foldername or Path.home())
        self.log.debug(self.folder_open_foldername)
        self.toolbar.folder_open['state']=NORMAL
        self.view.status_bar.set_path(self.folder_open_foldername)
        
        # populate explorer
        self.view.explorer.populate_path(self.folder_open_foldername)

        # invoke logformatparser model
        self.model.log_format_parser.set_path(self.folder_open_foldername)
        self.model.log_format_parser.ParseLogs()