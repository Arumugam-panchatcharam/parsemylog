#!/usr/bin/python
# -*- coding: utf-8 -*-

import base64
from PIL import Image, ImageTk
from os import path
from importlib import resources

def get_image(b64_encoded_binary_string, img_resize):
    # Decode the base64 encoded image
    b64_decode_img = ImageTk.BytesIO(base64.b64decode(b64_encoded_binary_string))
    image = Image.open(b64_decode_img).resize(img_resize)
    tk_image = ImageTk.PhotoImage(image)
    return tk_image

def get_button_image(icon_file, img_resize):
    abspath = path.abspath(__file__)
    icon_full_path = path.join(path.dirname(abspath), "resource",icon_file)
    img = Image.open(icon_full_path).resize(img_resize)
    tkimg = ImageTk.PhotoImage(img)
    return tkimg

def position_window_center(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width/2 - width/2)
    y_coordinate = (screen_height/2 - height/2)
    root.geometry("%dx%d+%d+%d" % (width, height, x_coordinate, y_coordinate))
    root.minsize(width, height)
