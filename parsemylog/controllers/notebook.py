from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk

from models.main import Model
from views.main import View

import os
import core.global_var as globalvar

class NoteBookController:
    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.log = globalvar.get_val("LOGGER")
        self.explorer = self.view.explorer
        self.notebook = self.view.notebook

        # Variables
        self._bind()

    def _bind(self) -> None:
        nb = self.notebook
        nb.notebook.bind("<<NotebookTabChanged>>", self._note_book_tab_selected)
        nb.filter_log_level_option.bind("<<FilterOptionChanged>>", self._notebook_data_frame_filter_log_level)
        nb.regex_entry.bind("<Return>", self._notebook_data_frame_regex_search)
        nb.regex_enter_check_button.config(command=self._notebook_data_frame_regex_search)
        nb.drop_duplicate_check.config(command=self._notebook_data_frame_drop_duplicates)
    
    def _get_explorer_selected_item(self):
        dict_val = dict()
        # skip null selection
        if self.explorer.tree.selection() == tuple():
            return None, None

        for selected_item in self.explorer.tree.selection():
            selected_item = self.explorer.tree.item(selected_item)
            record = selected_item['values']
            dict_val = eval(record[0])
            file =  selected_item['text']
            fpath = dict_val['path']

        return file,fpath
    
    def _note_book_tab_selected(self,event):
        file, fpath = self._get_explorer_selected_item()
        print(file, fpath)
        if file is None or fpath is None:
            return
        # skip directory
        if os.path.isfile(fpath):
            nb  = self.notebook.notebook
            current_tab = nb.tab(nb.select(), "text")
            if current_tab == "Data View":
                self.log.debug("Currently selected TAB is Data View")
                self.notebook.load_file(fpath)
            if current_tab == "Log Insight":
                self.log.debug("Currently selected TAB is Log Insight")
                self.notebook.load_data_frame(file)
            if current_tab == "Log Report":
                self.log.debug("Currently selected TAB is Log Report")
                self.notebook.plot_data(file)

    def _notebook_data_frame_filter_log_level(self, event):
        file, fpath = self._get_explorer_selected_item()
        if file is None or fpath is None:
            return
        # skip directory
        if os.path.isfile(fpath):
            self.notebook.apply_filter_updates(file)

    def _notebook_data_frame_regex_search(self, event=None):
        file, fpath = self._get_explorer_selected_item()
        if file is None or fpath is None:
            return
        # skip directory
        if os.path.isfile(fpath):
            self.notebook.apply_filter_updates(file)

    def _notebook_data_frame_drop_duplicates(self):
        file, fpath = self._get_explorer_selected_item()
        if file is None or fpath is None:
            return
        # skip directory
        if os.path.isfile(fpath):
            self.notebook.apply_filter_updates(file)