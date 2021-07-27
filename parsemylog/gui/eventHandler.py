#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import path, listdir, stat

from pathlib import Path
import pandas as pd
import threading
import itertools
import time

import PySimpleGUI as sg

from gui.icons import Log_analyser_icon
from gui.helpers import add_file, add_files_and_folders
from core.logFormatParser import logformatparser
from core.logInsightParser import loginsightparser
from core.core import log, SUPPORTED_FILE_EXTENSION
from core.logFormatParser import GlobalVars

# plotting
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

import shutil

import re


# GUI Layout Keys
class keys():
    LOG_FILTER_SECTION = '-LOG FILTER SECTION-'
    FOLDER_BROWSE_SECTION = '-FOLDER BROWSE SECTION-'
    FILE_LIST = '-FILE LIST-'
    HIDE_DUPLICATE = '-HIDE DUPLICATE-'
    NOTEPAD = '-NOTEPAD-'
    SUMMARY = '-SUMMARY-'
    LOG_INSIGHT_BODY = '-LOG INSIGHT BODY-'
    LOG_FORMAT = '-LOG FORMAT-'
    JIRA_OPEN = '-JIRA OPEN-'
    DATA_VIEW = '-DATA VIEW-'
    LOG_SUMMARY = '-LOG SUMMARY-'
    WINTHEME = '-WINTHEME-'
    FILTER_LOG = '-FILTER LOG-'
    SEARCH_KEYWORD = '-SEARCH KEYWORD-'
    TABLE_RANDA = '-TABLE RANDA-'
    TABLE_LOGINSIGHT = '-TABLE LOGINSIGHT-'

    # TAB
    TAB_GROUP = '-TABGROUP-'
    TAB_DATA_VIEW = '-TABDVIEW-'
    TAB_R_AND_A = '-TABRANDA-'
    TAB_STATS = '-TABSTAT-'
    TAB_LOG_INSIGHT = '-LOG INSIGHT-'
    TAB_SUMMARY = '-TAB SUMMARY-'

    PLOT_STYLE = '-STYLE-'
    STAT_IMAGE = '-STAT IMAGE-'
    PLOT_CONTROL = '-CONTROL CV-'
    LOG_LEVEL_FILTER = '-FILTER LOG LEVEL-'
    STATUS_BAR = '-STATUS BAR-'
    OPEN_FOLDER = '-OPEN FOLDER-'
    OPEN_FILE = '-OPEN FILE-'
    OPEN_FILE = '-OPEN FILE-'
    OPEN_ARCHIVE = '-OPEN ARCHIVE-'

    # Thread Events
    THREAD_START = '-THREAD START-'
    PROGRESS_BAR = '-PROGRESS BAR-'
    THREAD_STATUS = '-THREAD STATUS-'


# Helper functions
class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)


def popup_error(error_str, image):
    sg.popup(error_str,
             image=image, font="Any 12",
             auto_close=True,
             auto_close_duration=2,
             # no_titlebar=True,
             title=None,)


def ParseLogs(in_path, archive=False):
    parser = logformatparser(in_path, archive)

    if parser.error:
        # Thread Execution Error
        pass
    else:
        # start Log format parsing
        parser.ParseLogs()

    # Log Insight Parser
    parser = loginsightparser()

    if parser.error:
        # Thread Execution Error
        pass
    else:
        # start log insight parsing
        parser.ParseLogs()


def ThreadedParseLogs(in_path, window, archive=False):
    # Number of tasks this thread working on
    MAX_TASKS = 2

    # Progress bar max value
    PROGRESS_METER_MAX = 10

    # Thread Start
    window.write_event_value(keys.THREAD_START, PROGRESS_METER_MAX)

    num_tasks = 1
    # Parse logs within the selected folder
    parser = logformatparser(in_path, archive)

    if parser.error:
        # Thread Execution Error
        pass
        window.write_event_value(keys.THREAD_STATUS, parser.error)
    else:
        # update progress bar before start parsing the logs (for first task only)
        # This gives message to user, that we are working on parsing logs.
        window.write_event_value(
            keys.PROGRESS_BAR, [num_tasks * (PROGRESS_METER_MAX/MAX_TASKS), PROGRESS_METER_MAX])

        # start Log format parsing
        parser.ParseLogs()
        num_tasks = num_tasks + 1

    # Log Insight Parser
    parser = loginsightparser()

    if parser.error:
        # Thread Execution Error
        pass
        window.write_event_value(keys.THREAD_STATUS, parser.error)
    else:
        # start log insight parsing
        parser.ParseLogs()
        # update Progerss
        window.write_event_value(
            keys.PROGRESS_BAR, [num_tasks * (PROGRESS_METER_MAX/MAX_TASKS), PROGRESS_METER_MAX])
        num_tasks = num_tasks + 1

    # Thread Stop
    window.write_event_value(keys.THREAD_STATUS, 'OK')


def update_heading(table_widget, COL_HEADING, headings):
    headings = headings + COL_HEADING[len(headings):]
    for cid, text in itertools.zip_longest(COL_HEADING, headings):
        table_widget.heading(cid, text=text)


def plot_me(window, df, title):
    if not 'log_level' in df.columns:
        return
    plt.close('all')
    plt.figure(1)
    fig = plt.gcf()
    DPI = fig.get_dpi()
    # TODO update canvas size
    fig.set_size_inches(500 * 2 / float(DPI), 500 / float(DPI))

    plt.suptitle(title.upper())
    # Creating autocpt arguments

    def plot_pct_val(pct, values):
        absolute = int(pct / 100.*np.sum(values))
        return "{v:d}".format(p=pct, v=absolute)

    def plot_pct_per(pct, values):
        absolute = int(pct / 100.*np.sum(values))
        return "{p:.0f}%".format(p=pct, v=absolute)
    # -------------------------------
    # 1
    plt.subplot(221)
    series = dict(df['log_level'].value_counts())
    explode = (0.1, 0.0, 0.2, 0.3, 0.0, 0.0)
    plt.pie(series.values(), labels=series.keys(), startangle=-90,
            autopct=lambda pct: plot_pct_val(pct, list(series.values())),
            explode=explode[:len(df.log_level.unique())])

    # 2
    plt.subplot(222)
    plt.xlabel('Log Level')
    plt.ylabel('Frequencey')
    series = dict(df['log_level'].value_counts())
    plt.bar(series.keys(), series.values())

    # 3
    plt.subplot(223)
    plt.xlabel('Log Level')
    plt.ylabel('Frequencey')
    series = dict(df['log_level'].value_counts())
    plt.bar(series.keys(), series.values())

    # 4
    plt.subplot(224)
    series = dict(df['log_level'].value_counts())
    plt.pie(series.values(), labels=series.keys(),
            autopct=lambda pct: plot_pct_per(pct, list(series.values())),
            startangle=-180, explode=explode[:len(df.log_level.unique())])

    # ------------------------------- Instead of plt.show()
    draw_figure_w_toolbar(window[keys.STAT_IMAGE].TKCanvas,
                          fig, window[keys.PLOT_CONTROL].TKCanvas)


# This is disabled for now as PysimpleGui is not happy with multi-threading
def threaded_parse_logs_disabled(in_path, window: sg.Window, archive=False):
    t1 = threading.Thread(target=ThreadedParseLogs, args=(
        in_path, window, archive,), daemon=True)
    g_val = GlobalVars()
    g_val.thread_id = t1
    print("Thread start ", t1)
    t1.start()


def threaded_parse_logs(in_path, archive=False):
    threading.Thread(target=ParseLogs, args=(
        in_path, archive,), daemon=True).start()


# Event Handler functions


def update_log_insight_table(window, event, values):
    if not values[keys.FILE_LIST]:
        return

    # check if respected log insight CSV file exists with the selected file
    slctd_file = values[keys.FILE_LIST][0]
    filepath, filename = path.split(slctd_file)
    g_val = GlobalVars()

    log_insight_file = path.join(g_val.parsed_logs_folder, filename+'-i.csv')

    if not path.exists(log_insight_file):
        window[keys.TABLE_LOGINSIGHT].update(values=pd.DataFrame())
        return

    # CSV file exists - Load
    df = pd.read_csv(log_insight_file)

    header_list = list(df.columns)
    # Drops the first row in the table (otherwise the header names and the first row will be the same)
    data = df.values.tolist()

    # Update Table Header
    table_widget = window[keys.TABLE_LOGINSIGHT].Widget
    COL_HEADINGS = [f"Column {i}" for i in range(3)]
    update_heading(table_widget, COL_HEADINGS, header_list)

    # Update Table
    window[keys.TABLE_LOGINSIGHT].update(values=data)


def update_RandA_table(window, event, values, drop_duplicates=False, filter=False, keyword=None):
    if not values[keys.FILE_LIST]:
        return
    # check if respected CSV file exists with the selected file
    slctd_file = values[keys.FILE_LIST][0]
    filepath, filename = path.split(slctd_file)
    g_val = GlobalVars()

    csv_filename = path.join(g_val.parsed_logs_folder, filename+'.csv')
    # print(csv_filename)

    if not path.exists(csv_filename):
        # Parsed data not avaiable, clear existing table
        window[keys.TABLE_RANDA].update(values=pd.DataFrame())
        return

    # CSV file exists - Load
    try:
        df = pd.read_csv(csv_filename)
    except:
        return

    # Bail out early if the data base is empty
    if df.empty:
        # DataBase is empty, clear existing table
        window[keys.TABLE_RANDA].update(values=pd.DataFrame())
        return

    if drop_duplicates:
        if 'log' in df.columns:
            df = df.drop_duplicates(subset=['log'], keep='last')
        else:
            df = df.drop_duplicates()

    if filter and values[keys.LOG_LEVEL_FILTER]:
        if 'log_level' in df.columns:
            df = df[df.log_level.str.upper().eq(values[keys.LOG_LEVEL_FILTER])]

    if keyword:
        # user may give invalid regex
        try:
            if 'log' in df.columns:
                df = df[df.log.str.contains(
                    pat=keyword, regex=True, flags=re.IGNORECASE, na=False)]
        except:
            popup_error("Regex seems to be invalid",
                        sg.EMOJI_BASE64_HAPPY_IDEA)
            return
        else:
            # update search keyword entry, so that user don't have to type
            # keywords to search everytime
            combo_val = values[keys.SEARCH_KEYWORD]
            update_combo = list(set(sg.user_settings_get_entry(
                keys.SEARCH_KEYWORD, []) + [combo_val, ]))
            update_combo = update_combo[:10]
            index = 0
            if combo_val in update_combo:
                index = update_combo.index(combo_val)

            # Store upto 10 values
            sg.user_settings_set_entry(
                keys.SEARCH_KEYWORD, update_combo)
            window[keys.SEARCH_KEYWORD].update(
                values=update_combo, set_to_index=index)

    header_list = list(df.columns)
    # Drops the first row in the table (otherwise the header names and the first row will be the same)
    data = df.values.tolist()

    # Update Table Header
    table_widget = window[keys.TABLE_RANDA].Widget
    COL_HEADINGS = [f"Column {i}" for i in range(6)]
    update_heading(table_widget, COL_HEADINGS, header_list)

    # Update Table
    window[keys.TABLE_RANDA].update(values=data)


def update_notepad(window, event, values):
    if not values[keys.FILE_LIST]:
        return

    slctd_file = values[keys.FILE_LIST][0]
    # print('selected file: ', slctd_file)
    # Check for file
    if not path.isfile(slctd_file):
        return
    file_extn = ''.join(Path(slctd_file).suffixes)

    # Check for suported FILE extension
    if file_extn not in SUPPORTED_FILE_EXTENSION:
        log.error("Not in supported extension")
        ERROR = "PARSEMYLOG: NOT IN SUPPORTED EXTENSION"
        window[keys.NOTEPAD].update(ERROR)
        return
    # Check for Zero '0' length file
    if not stat(slctd_file).st_size:
        log.error("File length is zero '0'")
        ERROR = "PARSEMYLOG: FILE LENGTH IS ZERO"
        window[keys.NOTEPAD].update(ERROR)
        return

    try:
        # TODO Text file with NULL encoing is not loading
        with open(slctd_file, 'r', encoding='utf-8', errors='ignore') as f:
            window[keys.NOTEPAD].update(value=f.read().lstrip('\x00'))
    except:
        log.error("File opening Error")
        ERROR = "PARSEMYLOG: ERROR WHILE OPENING THE SELECTED FILE"
        window[keys.NOTEPAD].update(ERROR)


def file_list_file_selected(window, event, values):
    tab_group(window, event, values)


def hide_duplicate(window, event, values):
    # TODO: need to find better way
    window[keys.TAB_GROUP].Widget.select(2)
    update_RandA_table(window, event, values,
                       drop_duplicates=values[keys.HIDE_DUPLICATE],
                       filter=values[keys.LOG_LEVEL_FILTER])


def open_archive(window, event, values):
    all_files = [i for _, l, _ in shutil.get_unpack_formats()
                 for i in l]
    supprt_file_type = [(a, l) for a, l, _ in shutil.get_unpack_formats()]
    supprt_file_type.insert(0, ("TAR Files", all_files))
    file_path = sg.popup_get_file("",
                                  no_window=True,
                                  keep_on_top=True,
                                  grab_anywhere=True,
                                  file_types=(supprt_file_type),
                                  icon=Log_analyser_icon)
    # user can close the open folder without selecting anything
    if not file_path:
        return

    update_statusbar(window, file_path)
    #threaded_parse_logs_disabled(file_path, window, archive=True)
    threaded_parse_logs(file_path, archive=True)

    # Give some time for background thread extract tarballs
    g_val = GlobalVars()
    while not g_val.archive_status:
        _, _ = window.read(timeout=500)
    g_val.archive_status = False

    dir_name = path.dirname(path.realpath(file_path))
    filename = path.basename(path.realpath(file_path))
    filename_woextn = Path(filename).stem
    folder_path = path.join(dir_name, filename_woextn)

    if not path.exists(folder_path):
        popup_error("Error opening Archive format",
                    sg.EMOJI_BASE64_NOTUNDERSTANDING)
        return

    treedata = add_files_and_folders(
        parent='', dirname=folder_path, treedata=sg.TreeData())
    # update Folder browser
    window[keys.FILE_LIST].update(values=treedata)

    # BUG if Theme is changed after selecting folder list
    #     we are losing all the info
    window[keys.WINTHEME].update(disabled=True)


def open_file(window, event, values):
    file_path = sg.popup_get_file("",
                                  no_window=True,
                                  keep_on_top=True,
                                  grab_anywhere=True,
                                  file_types=[
                                      ("Log Files", tuple(SUPPORTED_FILE_EXTENSION),)
                                  ],
                                  icon=Log_analyser_icon)
    # user can close the open folder without selecting anything
    if not file_path:
        return
    update_statusbar(window, file_path)

    treedata = add_file(
        parent='', dirname=file_path, treedata=sg.TreeData())
    # update Folder browser
    window[keys.FILE_LIST].update(values=treedata)

    # BUG if Theme is changed after selecting folder list
    #     we are losing all the info
    window[keys.WINTHEME].update(disabled=True)

    #threaded_parse_logs_disabled(file_path, window, archive=False)
    threaded_parse_logs(file_path, archive=False)


def threaded_add_files_and_folder(window, event, value, folder_path):
    treedata = add_files_and_folders(parent='', dirname=folder_path,
                                     treedata=sg.TreeData())
    # update Folder browser
    window[keys.FILE_LIST].update(values=treedata)

    # BUG if Theme is changed after selecting folder list
    #     we are losing all the info
    window[keys.WINTHEME].update(disabled=True)


def open_folder(window, event, values):
    folder_path = sg.popup_get_folder(
        "", no_window=True, keep_on_top=True, grab_anywhere=True, icon=Log_analyser_icon)
    # user can close the open folder without selecting anything
    if not folder_path:
        return

    update_statusbar(window, folder_path)

    #threaded_parse_logs_disabled(folder_path, window, archive=False)
    threaded_parse_logs(folder_path, archive=False)

    # threading.Thread(target=threaded_add_files_and_folder, args=(
    #    window, event, values, folder_path), daemon=True).start()
    threaded_add_files_and_folder(window, event, values, folder_path)


def log_filter_section(window, event, values):
    KEY = keys.LOG_FILTER_SECTION
    window[KEY].update(visible=not window[KEY].visible)
    window[KEY+'-SYMBOL-'].update(window[KEY].metadata[0]
                                  if window[KEY].visible else window[KEY].metadata[1])


def folder_browse_section(window, event, valus):
    KEY = keys.FOLDER_BROWSE_SECTION
    window[KEY].update(visible=not window[KEY].visible)
    window[KEY+'-SYMBOL-'].update(window[KEY].metadata[0]
                                  if window[KEY].visible else window[KEY].metadata[1])


def tab_report_and_analysis(window, event, values):
    update_RandA_table(window, event, values,
                       drop_duplicates=values[keys.HIDE_DUPLICATE],
                       filter=values[keys.LOG_LEVEL_FILTER])


def tab_statistics(window, event, values):
    if not values[keys.FILE_LIST]:
        return
    # check if respected CSV file exists with the selected file
    slctd_file = values[keys.FILE_LIST][0]
    filepath, filename = path.split(slctd_file)
    g_val = GlobalVars()
    csv_filename = path.join(g_val.parsed_logs_folder, filename+'.csv')

    if not path.exists(csv_filename):
        plt.close('all')
        return

    # CSV file exists - Load
    df = pd.read_csv(csv_filename)
    plot_me(window, df, title=filename)


def tab_data_view(window, event, values):
    update_notepad(window, event, values)


def tab_log_insight(window, event, values):
    update_log_insight_table(window, event, values)


def format_head(h, format, sp=''):
    return "{0}{1}\n{0}{2}\n".format(sp, h, format*len(h))


def tab_summary(window, event, values):
    if not values[keys.FILE_LIST]:
        return

    # check if respected summary file exists with the selected file
    slctd_file = values[keys.FILE_LIST][0]
    filepath, filename = path.split(slctd_file)
    g_val = GlobalVars()

    summary_filename = path.join(g_val.parsed_logs_folder, filename+'-s.txt')
    insight_filename = path.join(g_val.parsed_logs_folder, filename+'-i.csv')
    # print(csv_filename)

    if path.exists(summary_filename):
        try:
            # TODO Text file with NULL encoing is not loading
            with open(summary_filename, 'r', encoding='utf-8', errors='ignore') as f:
                window[keys.SUMMARY].update(value=f.read())
        except:
            log.error("File opening Error")
            ERROR = "PARSEMYLOG: ERROR WHILE OPENING THE SELECTED FILE"
            window[keys.SUMMARY].update(ERROR)

    elif path.exists(insight_filename):
        try:
            df = pd.read_csv(insight_filename)
            if df.empty:
                window[keys.SUMMARY].update(value='')
                return

            if 'Reason' in df.columns:
                summary = format_head(filename, '-')
                summary = summary+'\n'.join(df.Reason.values.tolist())
                window[keys.SUMMARY].update(
                    value=summary)
        except:
            log.error("File opening Error")
            ERROR = "PARSEMYLOG: ERROR WHILE OPENING THE SELECTED FILE"
            window[keys.SUMMARY].update(ERROR)
    else:
        # Parsed data not avaiable, clear existing summary
        window[keys.SUMMARY].update(value='')
        return


def tab_group(window, event, values):
    if not values[keys.FILE_LIST]:
        return

    # TAB Group Mini Handler
    tab_group_handler = {
        keys.TAB_LOG_INSIGHT: tab_log_insight,
        keys.TAB_DATA_VIEW:  tab_data_view,
        keys.TAB_R_AND_A: tab_report_and_analysis,
        keys.TAB_STATS: tab_statistics,
        keys.TAB_SUMMARY: tab_summary,
    }
    tab_group_handler.get(values[keys.TAB_GROUP])(window, event, values)


def stat_plot_style(window, event, values):
    if values[keys.PLOT_STYLE]:
        plt.style.use(values[keys.PLOT_STYLE])
    tab_statistics(window, event, values)


def filter_data_log_level(window, event, values):
    update_RandA_table(window, event, values,
                       drop_duplicates=values[keys.HIDE_DUPLICATE],
                       filter=values[keys.LOG_LEVEL_FILTER])


def filter_log_keyword(window, event, values):
    update_RandA_table(window, event, values,
                       drop_duplicates=values[keys.HIDE_DUPLICATE],
                       filter=values[keys.LOG_LEVEL_FILTER],
                       keyword=values[keys.SEARCH_KEYWORD])


def log_summary_report(window, event, values):
    g_val = GlobalVars()
    if not g_val.parsed_logs_folder:
        return

    summary_filename = path.join(g_val.parsed_logs_folder, 'summary.txt')
    if path.exists(summary_filename):
        with open(summary_filename, 'r') as fd:
            window[keys.SUMMARY].update(
                value=fd.read())
        return

    # order of data in summary report
    files_list = listdir(g_val.parsed_logs_folder)
    # get list of summary data
    summary_list = [file for file in files_list if file.endswith('-s.txt')]
    # get list of insight data
    insight_list = [file for file in files_list if file.endswith('-i.csv')]

    # save as summary.txt
    with open(summary_filename, 'w') as s_fd:
        # append summary files to summary report
        for file in summary_list:
            with open(path.join(g_val.parsed_logs_folder, file), 'r') as fd:
                s_fd.write(fd.read())

        s_fd.write('\n' + format_head('RDKB Log Summary', '=', sp='\t'*4))
        for file in insight_list:
            df = pd.read_csv(path.join(g_val.parsed_logs_folder, file))
            if df.empty:
                continue
            if 'Reason' in df.columns:
                summary = format_head(file.strip('-i.csv'), '-')
                summary = summary + '\t' + \
                    '\n\t'.join(df.Reason.values.tolist())
                s_fd.write(summary + '\n'*2)

    with open(summary_filename, 'r') as fd:
        window[keys.SUMMARY].update(
            value=fd.read())


def update_statusbar(window, text):
    window[keys.STATUS_BAR].update(text)


def thread_start(window, event, values):
    sg.one_line_progress_meter(f'Please Wait Parsing...', 0, values[event],
                               bar_color=('green', 'white'),
                               button_color=sg.theme_button_color(),
                               size=(20, 10),
                               orientation='h',
                               # no_titlebar=True,
                               key=keys.PROGRESS_BAR,
                               grab_anywhere=True,
                               border_width=4)
    # sg.one_line_progress_meter_cancel(keys.PROGRESS_BAR)


def thread_status(window, event, values):
    # sg.one_line_progress_meter_cancel(key=keys.PROGRESS_BAR)
    #ret, image = values[keys.THREAD_STATUS]
    g_val = GlobalVars()
    t1 = g_val.thread_id
    if t1:
        t1.join()
        print("Thread join ", t1)
    ret = values[keys.THREAD_STATUS]
    #popup_error(ret, sg.EMOJI_BASE64_HAPPY_JOY)


def progress_bar_update(window, event, values):
    current_val, max_val = values[event]
    sg.one_line_progress_meter(f'Please Wait Parsing...', current_val+1, max_val,
                               bar_color=('green', 'white'),
                               button_color=sg.theme_button_color(),
                               size=(20, 20),
                               orientation='h',
                               # no_titlebar=True,
                               key=keys.PROGRESS_BAR,
                               grab_anywhere=True,
                               border_width=4)
    # sg.one_line_progress_meter_cancel(keys.PROGRESS_BAR)


registered_handlers = {
    keys.OPEN_FILE: open_file,
    keys.OPEN_FOLDER: open_folder,
    keys.OPEN_ARCHIVE: open_archive,

    keys.FILE_LIST: file_list_file_selected,
    keys.HIDE_DUPLICATE: hide_duplicate,
    keys.LOG_LEVEL_FILTER: filter_data_log_level,
    keys.FILTER_LOG: filter_log_keyword,
    keys.SEARCH_KEYWORD: filter_log_keyword,
    keys.LOG_SUMMARY: log_summary_report,

    # Collapsible section
    keys.LOG_FILTER_SECTION+'-SYMBOL-': log_filter_section,
    keys.LOG_FILTER_SECTION+'-TITLE-': log_filter_section,
    keys.FOLDER_BROWSE_SECTION+'-SYMBOL-': folder_browse_section,
    keys.FOLDER_BROWSE_SECTION+'-TITLE-': folder_browse_section,

    # TAB Group
    keys.TAB_GROUP: tab_group,
    keys.TAB_DATA_VIEW: tab_data_view,
    keys.TAB_R_AND_A: tab_report_and_analysis,
    keys.TAB_STATS: tab_statistics,

    keys.PLOT_STYLE: stat_plot_style,

    # Thread functions
    keys.THREAD_START: thread_start,
    keys.THREAD_STATUS: thread_status,
    keys.PROGRESS_BAR: progress_bar_update,
}


def EventHandler(window, event, values):
    if event not in registered_handlers:
        return
    registered_handlers.get(event)(window, event, values)


if __name__ == '__main__':
    EventHandler()
