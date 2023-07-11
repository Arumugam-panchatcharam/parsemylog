from tkinter import *
from tkinter import ttk

from models.main import Model
from views.main import View

import os
import core.global_var as globalvar

class ExplorerController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.log = globalvar.get_val("LOGGER")
        self.explorer = self.view.explorer
        self.notebook = self.view.notebook

        # Variables
        self._bind()

    def _bind(self) -> None:
        self.explorer.tree.bind("<<TreeviewSelect>>", self._tree_view_item_selected)
    
    def _tree_view_item_selected(self, event):
        for selected_item in self.explorer.tree.selection():
            selected_item = self.explorer.tree.item(selected_item)
            record = selected_item['values']
            dict_val = eval(record[0])
        # skip directory
        if dict_val['path'] and os.path.isfile(dict_val['path']):
            nb  = self.notebook.notebook
            current_tab = nb.tab(nb.select(), "text")
            if current_tab == "Data View":
                self.log.debug("Currently selected TAB is Data View")
                self.notebook.load_file(dict_val['path'])
            if current_tab == "Log Insight":
                self.log.debug("Currently selected TAB is Log Insight")
                self.notebook.load_data_frame(selected_item['text'])
            if current_tab == "Log Report":
                self.log.debug("Currently selected TAB is Log Report")
                self.notebook.plot_data(selected_item['text'])
