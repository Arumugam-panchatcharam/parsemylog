#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
from PIL import Image
import base64
import os
import PySimpleGUI as sg
from gui.icons import file_icon, folder_icon


def sizeof_fmt(num):
    for unit in [' B', ' KB', ' MB', ' GB', ' TB', ' PB', ' EB', ' ZB']:
        if abs(num) < 1024.0:
            return "%3.1f%s" % (num, unit)
        num /= 1024.0
    return "%.1f%s" % (num, 'YB')


def resize_base64_image(imageBase64, size):
    '''
    May not be the original purpose, but this code is being used to resize an image for use with PySimpleGUI (tkinter) button graphics
    :param image64: (str) The Base64 image
    :param size: Tuple[int, int] Size to make the image in pixels (width, height)
    :return: (str) A new Base64 image
    '''
    image_file = io.BytesIO(base64.b64decode(imageBase64))
    img = Image.open(image_file)
    img.thumbnail(size, Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    imgbytes = bio.getvalue()
    return imgbytes


# if single file is selected
def add_file(parent, dirname, treedata=sg.TreeData()):
    if os.path.isfile(dirname):
        dir, file = os.path.split(dirname)
        treedata.Insert(parent, dir, ".", values=[],
                        icon=folder_icon)
        treedata.Insert(parent, dirname, file, values=[
            sizeof_fmt(os.stat(dirname).st_size)], icon=file_icon)
        return treedata


# Recurse Directory
def add_files_and_folders(parent, dirname, treedata=sg.TreeData()):

    files = os.listdir(dirname)
    for f in files:
        fullname = os.path.join(dirname, f)
        # if it's a folder, add folder and recurse
        # Skip .parsemylog cache folder
        if os.path.isdir(fullname) and not fullname.endswith('.parsemylog'):
            treedata.Insert(parent, fullname, f, values=[],
                            icon=folder_icon)
            add_files_and_folders(fullname, fullname, treedata)
        elif os.path.isfile(fullname):
            treedata.Insert(parent, fullname, f, values=[
                            sizeof_fmt(os.stat(fullname).st_size)], icon=file_icon)
        else:
            pass

    return treedata


if __name__ == '__main__':
    pass
