from tkinter import *
from tkinter import ttk

import os
from pathlib import Path
from .utils import get_button_image
import core.global_var as globalvar

class ToggledFrame(ttk.Frame):
    def __init__(self, parent, text="", up_arrow=None, down_arrow=None):
        super().__init__(parent)

        self.up_arrow = up_arrow
        self.down_arrow = down_arrow
        self.show = IntVar()
        self.show.set(0)

        self.title_frame = ttk.Frame(self, border=1, borderwidth=1, width=40)

        self.icon_img = get_button_image("down_arrow.ico", (10, 10))
        #ttk.Label(self.title_frame, text=text, image=icon_img, compound=LEFT).pack(side="left", fill="x", expand=True)
        
        self.toggle_button = ttk.Button(self.title_frame, text=text, image=self.down_arrow, compound=LEFT, command=self.toggle,
                                            variable=self.show, style='Toolbutton')
        self.toggle_button.pack(side=LEFT, fill=X, expand=True, padx=2, pady=2, ipadx=2, ipady=2)

        self.sub_frame = ttk.Frame(self)
        self.title_frame.pack(fill=X, expand=True)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill=X, expand=True)
            self.toggle_button.configure(image=self.up_arrow)
        else:
            self.sub_frame.forget()
            icon_img = get_button_image("up_arrow.ico", (30, 30))
            self.toggle_button.configure(image=self.down_arrow)

class Explorer(ttk.Frame):
    """GUI Explorer Window

    Args:
        ttk (_type_): _description_
    """
    def __init__(self, container, path=None) -> None:
        super().__init__(container)
        self.nodes = dict()
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text='EXPLORER', anchor=NW)
        #self.tree.heading('#0', text='', anchor='w')
        self.tree.pack(side=LEFT, fill=Y, anchor=W)
        '''
        self.up_arrow = get_button_image("up_arrow.ico", (10, 10))
        self.down_arrow = get_button_image("down_arrow.ico", (10, 10))

        self.explorer = ToggledFrame(self.tree, text='  Explorer', up_arrow=self.up_arrow, down_arrow=self.down_arrow)
        #self.explorer.pack(fill=X, expand=True, anchor=N)
        self.explorer.grid(row=0, column=0,columnspan=2, rowspan=3, sticky='nsew')
        '''

        # current Frame config
        self.config(relief="flat")

    def populate_path(self,path):
        print("path is  ", Path(path))
        if path is not None:
            dirname = os.path.abspath(Path(path))
            print()
            self._insert_node('', os.path.basename(dirname), dirname)
            self.tree.bind('<<TreeviewOpen>>', self._open_node)

    def _insert_node(self, parent, text, dirname):
        val_dict = dict()
        val_dict['path'] = dirname #Path(dirname)
        node = self.tree.insert(parent, 'end', text=text, values =[val_dict],open=False)
        if os.path.isdir(dirname) and not dirname.endswith('.parsemylog'):
            self.nodes[node] = dirname
            self.tree.insert(node, 'end')

    def _open_node(self, event):
        node = self.tree.focus()
        dirname = self.nodes.pop(node, None)
        if dirname:
            self.tree.delete(self.tree.get_children(node))
            for dir in os.listdir(dirname):
                # Skip .parsemylog cache folder
                if os.path.isdir(dir) and not dir.endswith('.parsemylog'):
                    continue
                self._insert_node(node, dir, os.path.join(dirname, dir))

