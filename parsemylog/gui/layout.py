#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import font
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import Frame, SELECT_MODE_EXTENDED, VerticalSeparator, theme_background_color

import matplotlib.pyplot as plt

# Local Imports
from gui.icons import *
from gui.helpers import resize_base64_image

from gui.eventHandler import keys
from core.logstat import LOG_LEVEL_MAPPING
''' Define window Layout
'''

# Layout Constants
DEF_TOOLBAR_ICON_COLOR = (sg.theme_background_color(),
                          sg.theme_background_color())
SLCTD_ROW_COLOR = (sg.theme_background_color(), sg.theme_element_text_color())


# Layout Helper Functions

def toolbar_icon(image, key, tooltip, size=(40, 40)):
    return sg.Button('', image_data=resize_base64_image(image, size),
                     button_color=(sg.theme_background_color(),
                                   sg.theme_background_color()),
                     border_width=0, key=key,
                     pad=(3, 3), tooltip=tooltip,
                     enable_events=True,
                     )


def Collapsible(layout, key, title='', arrows=(sg.SYMBOL_DOWN_ARROWHEAD, sg.SYMBOL_RIGHT_ARROWHEAD), collapsed=False):
    """
    User Defined Element
    A "collapsable section" element. Like a container element that can be collapsed and brought back
    :param layout:Tuple[List[sg.Element]]: The layout for the section
    :param key:Any: Key used to make this section visible / invisible
    :param title:str: Title to show next to arrow
    :param arrows:Tuple[str, str]: The strings to use to show the section is (Open, Closed).
    :param collapsed:bool: If True, then the section begins in a collapsed state
    :return:sg.Column: Column including the arrows, title and the layout that is pinned
    """
    return sg.Column([[sg.T((arrows[1] if collapsed else arrows[0]), enable_events=True, k=key+'-SYMBOL-'),
                       sg.T(title, enable_events=True, key=key+'-TITLE-')],
                      [sg.pin(sg.Column(layout, key=key, visible=not collapsed, metadata=arrows))]], pad=(0, 0))


BLUE_BUTTON_COLOR = '#FFFFFF on #2196f2'


# Main Layout
def main_window(theme=None):
    if theme:
        sg.theme(theme)

    # Toolbar
    toolbar_load = [[
        toolbar_icon(file_new_icon, keys.OPEN_FILE, "Open File"),
        toolbar_icon(folder_toolbar_icon, keys.OPEN_FOLDER, "Open Folder"),
        toolbar_icon(zip_icon, keys.OPEN_ARCHIVE, "Open Archive"),
    ]]
    toolbar_logformat = [[
        #toolbar_icon(format_icon, keys.LOG_FORMAT, "Log Formatter"),
        toolbar_icon(statistic_icon, keys.LOG_SUMMARY, "Log Summary"),
    ]]

    toolbar_misc = [[
        toolbar_icon(theme_icon, keys.WINTHEME, "Change themes"),
    ]]


    # Left section 1 - Log Directory list
    left_folder_list = [
        [
            sg.Tree(data=sg.TreeData(),
                    headings=['Size', ],
                    justification='l',
                    col_widths=[30, 15],
                    # num_rows=30,
                    col0_width=30,
                    key=keys.FILE_LIST,
                    enable_events=True,
                    show_expanded=True,
                    selected_row_colors=SLCTD_ROW_COLOR,
                    select_mode=SELECT_MODE_EXTENDED,
                    visible=True,
                    )
        ],
    ]

    # Right Column - Log insight
    log_insight_tab = [[
        sg.Table(values=[[f"NA" for i in range(3)]],
                 headings=[f"Column {i}" for i in range(3)],
                 display_row_numbers=True, selected_row_colors=SLCTD_ROW_COLOR,
                 auto_size_columns=False,
                 def_col_width=38, max_col_width=38,
                 justification='left',
                 num_rows=30, key=keys.TABLE_LOGINSIGHT,)
    ]]
    # Right Column - Notepad
    raw_log_tab = [[
        sg.Multiline(font=('Consolas', 12),
                     background_color=sg.theme_background_color(),
                     text_color=sg.theme_element_text_color(),
                     key=keys.NOTEPAD, write_only=True,
                     expand_x=True, expand_y=True,
                     tooltip='Notepad')
    ]]

    log_filters_toolbar = [[
        sg.Checkbox("Hide Duplicate", enable_events=True,
                    background_color=sg.theme_background_color(),
                    text_color=sg.theme_element_text_color(),
                    key=keys.HIDE_DUPLICATE, tooltip='Hide Duplicates',
                    pad=(40, 8)),
        sg.T("Filter Logs Levels"),
        sg.Combo(list(LOG_LEVEL_MAPPING), enable_events=True,
                 background_color=sg.theme_background_color(),
                 text_color=sg.theme_element_text_color(),
                 size=(15, 1), key=keys.LOG_LEVEL_FILTER,
                 auto_size_text=False, tooltip='Filter Logs Levels',
                 pad=((0, 40), (8, 8))),

        sg.T("Search keywords"),
        sg.Combo(values=sorted(sg.user_settings_get_entry(keys.SEARCH_KEYWORD, [])),
                 default_value=None,
                 size=(40, 1),
                 k=keys.SEARCH_KEYWORD,
                 enable_events=True,
                 bind_return_key=True, tooltip='[Regex - case insensitive]',
                 pad=((0, 2), (8, 8)),
                 background_color=sg.theme_background_color(),
                 text_color=sg.theme_element_text_color()),
        sg.B("", button_color=(sg.theme_background_color(),
                               sg.theme_background_color(),),
             key=keys.FILTER_LOG, border_width=0,
             pad=(2, 8),
             image_data=resize_base64_image(search_icon, size=(30, 30)),
             tooltip='[Regex - case insensitive]')
    ]]
    # Right Column - Log Report and Analyze
    filtered_log_tab = [
        [sg.Frame('Log filters', log_filters_toolbar,
                  element_justification='c',
                  border_width=0,)],
        [
            sg.Table(values=[[f"NA" for i in range(6)]],
                     headings=[f"Column {i}" for i in range(6)],
                     display_row_numbers=True, selected_row_colors=SLCTD_ROW_COLOR,
                     auto_size_columns=False,
                     def_col_width=19, max_col_width=19,
                     justification='left',
                     num_rows=30, key=keys.TABLE_RANDA,)
        ]
    ]

    # Right Column - Statistics
    stats_tab = [
        [sg.T(" " * 100), sg.T('Log Statistics', font='Any 20')],
        [
            sg.T('Plot Styles'),
            sg.Combo(plt.style.available, enable_events=True,
                     key=keys.PLOT_STYLE)
        ],
        [sg.T('Controls:')],
        [sg.T(' ' * 5), sg.Canvas(key=keys.PLOT_CONTROL)],
        [sg.T('Figure:')],
        [sg.T(' ' * 5), sg.Column(
            layout=[
                [sg.Canvas(key=keys.STAT_IMAGE,
                           # it's important that you set this size
                           size=(500 * 2, 500)
                           )]
            ],
            background_color='#DAE0E6',
            pad=(8, 8)
        )]
    ]

    # Right Column - Notepad
    summary_log_tab = [
        [
            sg.Multiline(font=('Consolas', 12),
                         background_color=sg.theme_background_color(),
                         text_color=sg.theme_element_text_color(),
                         key=keys.SUMMARY, write_only=True,
                         expand_x=True, expand_y=True,
                         tooltip='Notepad')
        ]
    ]

    tab_group = [[
        sg.Tab('Log Insight', log_insight_tab,
               key=keys.TAB_LOG_INSIGHT, ),
        sg.Tab('Data View', raw_log_tab,
               key=keys.TAB_DATA_VIEW, ),
        sg.Tab('Report And Analysis', filtered_log_tab,
               key=keys.TAB_R_AND_A, ),
        sg.Tab('Statistics', stats_tab,
               key=keys.TAB_STATS, ),
        sg.Tab('Summary', summary_log_tab,
               key=keys.TAB_SUMMARY, ),
    ]]

    # Right TAB group
    tab_layout = [[
        sg.TabGroup(tab_group, key=keys.TAB_GROUP,
                    tab_location='topleft',
                    enable_events=True,
                    pad=(0, 0),
                    # border_width=0,
                    )
    ]]

    # Main Window Layout
    layout = [
        [
            sg.Frame('', toolbar_load, border_width=0, pad=(8, 8),),
            sg.Frame('', toolbar_logformat, border_width=0, pad=(8, 8), ),
            sg.Frame('', toolbar_misc, border_width=0, pad=(8, 8), ),
        ],
        [
            sg.Column(left_folder_list, justification='left',
                      expand_x=True, expand_y=True,),
            sg.Column(tab_layout, justification='right',
                      expand_x=True, expand_y=True,),
        ],
        [
            sg.StatusBar("ParseMyLog v0.1", enable_events=True,
                         justification='l', font='Arial 12',
                         size=(150, 1),
                         key=keys.STATUS_BAR)
        ]
    ]

    window = sg.Window("ParseMyLog",
                       layout,
                       icon=search_icon1,
                       keep_on_top=False,
                       grab_anywhere=False,
                       resizable=True,
                       debugger_enabled=True,
                       finalize=True,
                       element_justification='l',
                       )

    # Expand
    window[keys.TAB_GROUP].expand(expand_x=True, expand_y=True)
    window[keys.TABLE_LOGINSIGHT].expand(expand_x=True, expand_y=True)
    window[keys.TABLE_RANDA].expand(expand_x=True, expand_y=True)
    window[keys.STAT_IMAGE].expand(expand_x=True, expand_y=True)
    window[keys.FILE_LIST].expand(expand_x=True, expand_y=True)

    return window
