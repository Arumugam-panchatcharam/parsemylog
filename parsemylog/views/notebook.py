from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox

from pandastable import Table, TableModel
import pandas as pd
import os
import matplotlib
from pathlib import Path
import re
from .utils import get_button_image

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)

import core.global_var as globalvar

# Ref: https://wiki.rdkcentral.com/display/RDK/RDK-B+Logger
LOG_LEVEL_MAPPING = {
    "NONE" : 0,
    "FATAL":  1,
    "ERROR":  2,
    "WARN":   3,
    "NOTICE": 4,
    "INFO":   5,
    "DEBUG":  6,
    "TRACE1": 7,
    "TRACE2": 8,
    "TRACE3": 9,
    "TRACE4": 10,
    "TRACE5": 11,
    "TRACE6": 12,
    "TRACE7": 13,
    "TRACE8": 14,
    "TRACE9": 15
}

class NoteBook(ttk.Frame):
    """GUI Details TAB

    Args:
        ttk (_type_): _description_
    """
    def __init__(self, container) -> None:
        super().__init__(container)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=LEFT,fill=BOTH, expand=True)

        # notepad
        self.data_view = ttk.Frame(self.notebook)
        self.text_area = ScrolledText(self.data_view)
        self.text_area.pack(fill=BOTH, expand=True)
        self.data_view.pack(fill=BOTH, expand=True)
        self.notebook.add(self.data_view, text='Data View')

        # pandas data frame
        self.filter_loglevel = StringVar()
        self.drop_duplicate_flag = IntVar()
        self.regex_search = StringVar()

        self.log_insight = ttk.Frame(self.notebook)
        self.log_insight.pack(fill=BOTH, expand=True)
        # Table Toolbar
        table_toolbarframe = ttk.Frame(self.log_insight)
        table_toolbarframe.pack(side=TOP, fill=X, expand=False, pady=5, anchor=CENTER)
        ttk.Label(table_toolbarframe, text="Filter Log Level").pack(side=LEFT, fill=BOTH,anchor=CENTER)

        log_level_options = list(LOG_LEVEL_MAPPING)
        self.filter_log_level_option = ttk.OptionMenu(table_toolbarframe,
                                                      self.filter_loglevel,
                                                      log_level_options[0],
                                                      *log_level_options,
                                                      direction="below",
                                                      command=self._filter_log_level_event)
        self.filter_log_level_option.pack(side=LEFT, fill=BOTH,anchor=CENTER)

        ttk.Label(table_toolbarframe,text="  ").pack(side=LEFT, fill=BOTH, padx=5, pady=5)

        ttk.Label(table_toolbarframe, text="Search Keywords [Regex-case insensitive]").pack(side=LEFT, fill=BOTH, anchor=CENTER)

        self.regex_entry = ttk.Entry(table_toolbarframe, 
                                     justify='left',
                                     width=25,
                                     textvariable=self.regex_search)
        self.regex_entry.pack(side=LEFT, fill=X,anchor=CENTER)

        self.fimg = get_button_image("search.ico", (20, 20))
        self.regex_enter_check_button = ttk.Button(table_toolbarframe, image=self.fimg, width=25, style="Toolbutton")
        self.regex_enter_check_button.pack(side=LEFT, fill=BOTH,anchor=CENTER)

        ttk.Label(table_toolbarframe,text="  ").pack(side=LEFT, fill=BOTH, padx=5, pady=5)

        self.drop_duplicate_check = ttk.Checkbutton(table_toolbarframe, text="Drop Duplicates", 
                                                   onvalue=1, offvalue=0, variable=self.drop_duplicate_flag)
        self.drop_duplicate_check.pack(side=LEFT, fill=BOTH, anchor=CENTER)

        # Table
        tableframe = ttk.Frame(self.log_insight, border=1, borderwidth=1,relief=RAISED)
        tableframe.pack(side=TOP, fill=BOTH, expand=True, padx=2)

        self.table = Table(tableframe, showtoolbar=False, showstatusbar=False, editable=False)
        self.table.show()

        self.notebook.add(self.log_insight, text='Log Insight')

        # Report
        self.log_report = ttk.Frame(self.notebook)
        self.log_report.pack(fill=BOTH, expand=True)
        self.notebook.add(self.log_report, text='Log Report')

        self.canvas = Canvas(self.log_report, bg="#357")
        self.canvas.pack(fill=BOTH, expand=True)
        self.figure_canvas = None

    def _clear_plot(self):
        if self.figure_canvas is None:
            return
        self.figure_canvas.get_tk_widget().delete("all")
        '''
        for item in self.figure_canvas.get_tk_widget().find_all():
            print("Number of items ", item)
            self.figure_canvas.get_tk_widget().delete("all")
        '''
    def _plot_data(self, df, filename):
        if 'log' in df.columns:
            df = df.drop_duplicates(subset=['log'], keep='last')
        else:
            df = df.drop_duplicates()

        series = dict(df['log_level'].value_counts())

        # create a figure
        figure = Figure(figsize=(6, 4), dpi=100)

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(figure, self.canvas)

        # create the toolbar
        #NavigationToolbar2Tk(figure_canvas, self.canvas)

        # create axes
        axes = figure.add_subplot()

        # create the barchart
        axes.bar(series.keys(), series.values())
        axes.set_title(os.path.basename(filename))
        axes.set_xlabel('log Level')

        #self.fig_canvas = figure_canvas.get_tk_widget()
        #self.fig_canvas.pack(side=TOP, fill=BOTH, expand=False)
        self.figure_canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=False)

    def plot_data(self, filename):
        # clear previous plot
        self._clear_plot()

        csv_file_path = self._get_csv_file_path(filename)
        if not os.path.exists(csv_file_path):
            return
        df = pd.read_csv(csv_file_path, sep=',', encoding= 'unicode_escape')
        df = self._drop_duplicates(df)
        self._plot_data(df, filename)

    def load_file(self,file_path):
        # clear previous contents
        self.text_area.delete("1.0",END)

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
                self.text_area.insert("1.0",content)
        except:
            pass
    
    def _clear_table(self):
        model = TableModel(pd.DataFrame())
        self.table.updateModel(model)
        self.table.redraw()

    def _update_table(self, csv_file_path):
        self.table.importCSV(csv_file_path, sep=',', encoding= 'unicode_escape')
        #resize the columns to fit the data better
        self.table.autoResizeColumns()

    def _drop_duplicates(self,df):
        if 'log' in df.columns:
            df = df.drop_duplicates(subset=['log'], keep='last')
        else:
            df = df.drop_duplicates()
        return df

    def drop_duplicates(self):
        flag =  self.drop_duplicate_flag.get()
        if flag:
            df = self.table.model.df
            self.table.model.df = self._drop_duplicates(df)

    def _filter_log_level_event(self, event):
        self.filter_log_level_option.event_generate("<<FilterOptionChanged>>")

    def _filter_log_level(self):
        loglevel = self.filter_loglevel.get()
        df = self.table.model.df
        if loglevel !='NONE' and 'log_level' in df.columns:
            df = df[df.log_level.str.upper().eq(loglevel)]
        self.table.model.df = df

    def _filter_regex(self):
        reg_pattern = self.regex_entry.get()
        print("regex is  ", reg_pattern)
        if len(reg_pattern) == 0:
            return
        df = self.table.model.df
        # user may give invalid regex
        try:
            if 'log' in df.columns:
                df = df[df.log.str.contains(
                    pat=reg_pattern, regex=True, flags=re.IGNORECASE, na=False)]
        except:
            messagebox.showwarning(title="RegEx Error!",message="Regex seems to be invalid")
            pass
        self.table.model.df = df

    def _get_csv_file_path(self, filename):
        parsed_logs_folder = globalvar.get_val("PARSED_LOGS_FOLDER")
        csv_filename = filename + '.csv'
        csv_file_path = os.path.join(Path(parsed_logs_folder),csv_filename)
        return csv_file_path

    def _apply_filter_updates(self, csv_file_path):
        self._update_table(csv_file_path)
        self._filter_log_level()
        self.drop_duplicates()
        self._filter_regex()
        self.table.redraw()

    def apply_filter_updates(self, filename):
        self._clear_table()
        csv_file_path = self._get_csv_file_path(filename)
        if not os.path.exists(csv_file_path):
            return
        self._apply_filter_updates(csv_file_path)
    
    def load_data_frame(self,filename):
        self._clear_table()
        csv_file_path = self._get_csv_file_path(filename)
        if not os.path.exists(csv_file_path):
            return
        self.table.importCSV(csv_file_path, sep=',', encoding= 'unicode_escape')
        #resize the columns to fit the data better
        self.table.autoResizeColumns()
        self._apply_filter_updates(csv_file_path)
