#!/usr/bin/python
# -*- coding: utf-8 -*-

import PySimpleGUI as sg
import sys
from os import path

sys.path.append(path.dirname(__file__))

main_window_theme = None


def theme_window_layout(theme=None):
    if theme:
        sg.theme(theme)
    theme_browser_layout = [[sg.Text('Look and Feel Browser')],
                            [sg.Text(
                                'Click a look and feel color to see demo window')],
                            [sg.Listbox(values=sg.theme_list(),
                                        size=(20, 20), key='-LIST-', enable_events=True)],
                            [sg.Button('OK')]]
    return sg.Window(
        'Choose Theme', theme_browser_layout, keep_on_top=True)


def render_gui():
    """ Sample
    """
    from gui.layout import main_window
    from gui.eventHandler import EventHandler
    from gui.eventHandler import keys
    from core.core import log
    theme = sg.user_settings_get_entry(keys.WINTHEME, 'DarkBlue4')
    window = main_window(theme)

    # sg.show_debugger_window()
    while True:
        event, values = window.read()
        if event != keys.NOTEPAD:
            log.debug('Event {}, Values {}'.format(event, values))
        if event in (None, sg.WIN_CLOSED, '-EXIT-'):
            break
        if event == keys.WINTHEME:
            theme_window = theme_window_layout(theme)
            while True:
                event, values = theme_window.read()
                print(event, values)
                if event in (None, '-Exit-'):
                    break
                if event == '-LIST-':
                    theme_window.close()
                    theme_window = theme_window_layout(values['-LIST-'][0])
                    main_window_theme = values['-LIST-'][0]
                if event == 'OK':
                    theme_window.close()
                    window.close()
                    window = main_window(main_window_theme)
                    sg.user_settings_set_entry(
                        keys.WINTHEME, main_window_theme)
                    break

        # Handles Other Events
        EventHandler(window, event, values)


def main():
    render_gui()


if __name__ == '__main__':
    main()
