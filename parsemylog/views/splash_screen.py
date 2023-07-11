#!/usr/bin/python
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter import ttk

from .utils import position_window_center, get_image
from .icons import parsemylog_logo_full

class SplashScreen(Tk):
    """Splash Screen

    Args:
        Tk
    """
    def __init__(self):
        Tk.__init__(self)
        self.w = 550
        self.h = 200
        # center the splash screen
        position_window_center(self, self.w, self.h)
        # set resizable to false
        self.resizable(False, False)
        # Hide Titlebar
        self.overrideredirect(True)
        # render spash image
        self._splash()

    def _splash(self):
        """Render Splash Screen
        """
        image = get_image(parsemylog_logo_full, (self.w, self.h))
        # create widget
        frame = Frame(self, width=self.w, height=self.h)
        label = Label(frame, image=image, bg="white")
        # position widgets
        frame.grid(column=0, row=0)
        label.grid(column=0, row=0)
        # destroy after 2 seconds
        self.after(2000, self.destroy)
        self.mainloop()

if __name__ == "__main__":
    SplashScreen()
