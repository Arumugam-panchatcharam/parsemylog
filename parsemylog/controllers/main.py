from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk

from views.main import View
from models.main import Model

from pathlib import Path
import core.global_var as globalvar

from .toolbar import ToolBarController
from .explorer import ExplorerController
from .notebook import NoteBookController

class Controller():
    def __init__(self, model:Model , view: View) -> None:
        self.view = view
        self.model = model
        self.log = globalvar.get_val("LOGGER")
        self.toolbar_controller = ToolBarController(model, view)
        self.explorer_controller = ExplorerController(model, view)
        self.notebook_controller = NoteBookController(model, view)
        #self.model.auth.add_event_listener("PARSING_DONE", self._parsing_done)

    def _parsing_done(self) -> None:
        # stop progressbar
        pass

    def start(self) -> None:
        self.view.start_mainloop()