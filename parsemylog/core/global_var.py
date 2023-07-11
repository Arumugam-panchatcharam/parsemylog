#!/usr/bin/python
# -*- coding: utf-8 -*-

def init_global_var():
    """initialize Global variable Dict
    """
    global GLOBAL_DICT
    GLOBAL_DICT = {}
   
def get_val(key):
    try:
        return GLOBAL_DICT.get(key)
    except:
        pass

def set_val(key, val):
    try:
        GLOBAL_DICT[key] = val
    except:
        pass