#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import shutil
import mimetypes
from pathlib import Path
from os import path

import logging
import logging.config
import yaml

LOGGING_CONFIG_FILE = \
    path.join(path.dirname(__file__), r'logging_conf.yaml')

# logging
with open(LOGGING_CONFIG_FILE, 'r') as f:
    log_cfg = yaml.safe_load(f.read())

logging.config.dictConfig(log_cfg)
log = logging.getLogger('Prod')


# Command line Argument Parser
file_args = argparse.ArgumentParser(
    "FileArgs", description="File stat and extract file")
file_args.add_argument('-f', '--filename', dest='filename', required=True)

SUPPORTED_FILE_EXTENSION = ['.log', '.txt.0', '.txt.1', '.txt']

# for test only remove in prod


def check_file_type(args):
    ''' Input is args
        check if input file is in supported ASCII/text file
        if the input is supported archive format, then unpack the archive in current folder
        return none for ASCII/text
               path of successfully unpacked folder
    '''
    if not os.path.exists(args.filename):
        sys.exit("Error: Path not found")

    if os.stat(args.filename).st_size == 0:
        sys.exit("Error: Zero Length file provided")

    # check for suported ASCII/text format
    file_extn = ''.join(Path(args.filename).suffixes)
    log.debug('File extension {0}'.format(file_extn))
    if file_extn in SUPPORTED_FILE_EXTENSION:
        log.debug("input is ASCII/text file")
        return None

    dir_name = os.path.dirname(os.path.realpath(args.filename))
    filename = os.path.basename(os.path.realpath(args.filename))
    # check for archive formats
    _, mime = mimetypes.guess_type(args.filename)
    log.debug('mime guess {0}'.format(mimetypes.guess_type(args.filename)))
    if mime is not None:
        try:
            shutil.unpack_archive(args.filename)
        except:
            sys.exit("Error: Unpack unsuccessfull")
    else:
        log.debug('{0} File format not Supported'.format(file_extn))

    log.debug('filename without extension {0}'.format(
        Path(args.filename).stem))

    unpack_folder = os.path.join(dir_name, os.path.join(
        dir_name, filename.split(file_extn)[0]))
    log.debug('Unpacked folder {0}'.format(unpack_folder))
    if os.path.isdir(unpack_folder):
        return unpack_folder


class GlobalVarsSingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class GlobalVars(metaclass=GlobalVarsSingletonMeta):
    parsed_logs_folder = ""
    thread_id = None
    archive_status = False

    def __init__(self) -> None:
        pass


def main():
    args = file_args.parse_args()
    log.debug('File Name {0}'.format(args.filename))

    # check file type and unpack if input file is archive
    log.debug('FN return {0}'.format(check_file_type(args)))


if __name__ == "__main__":
    main()
    import pandas as pd
    pd.read_csv('a.log', delimiter="\n")
