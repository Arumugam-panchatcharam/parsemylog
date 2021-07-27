#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml
import re
import csv
import os
from pathlib import Path
import shutil

from py7zr import unpack_7zarchive

import concurrent.futures
#import pandas as pd
from importlib import resources

import pandas as pd
# Local imports
from .core import log, GlobalVars
from .rgLogParser import rglogparser
# Log Config File
# LOG_CONFIG_FILE = \
#    os.path.join(os.path.dirname(__file__), '../configs', r'config.yaml')

# Temp location to store the parsed CSV files
LOG_PARSER_TEMP_DIR = '.parsemylog'


def get_supported_archive_fomats():
    # Register for .7z format - pip install py7zr required
    shutil.register_unpack_format('7z', ['.7z', '.7Z'], unpack_7zarchive,
                                  description='7z File',)

    supported_formats = []
    for spptrd_type in shutil.get_unpack_formats():
        for type_extns in spptrd_type[1]:
            supported_formats.append(type_extns)

    return supported_formats


SUPPORTED_ARCHIVE_FOMATS = get_supported_archive_fomats()


def unpack_archive(inpath):

    if not os.path.exists(inpath):
        log.error("Path not found!")
        return 1, "Path not found!"

    if os.stat(inpath).st_size == 0:
        log.error("Input file is of Zero Length")
        return 1, "Input file is of Zero Length"

    dir_name = os.path.dirname(os.path.realpath(inpath))
    filename = os.path.basename(os.path.realpath(inpath))
    filename_woextn = Path(filename).stem
    file_extn = ''.join(Path(filename).suffixes)
    unpack_folder = os.path.join(dir_name, filename_woextn)

    log.debug(" dir name {0} \nfilename {1} file wo extn {2} file extension {3}".format(
        dir_name, filename, filename_woextn, file_extn))

    # check for archive formats
    if file_extn not in SUPPORTED_ARCHIVE_FOMATS:
        log.error("Input Archive Format not supported")
        return 1, "Input Archive Format not supported"

    try:
        shutil.unpack_archive(inpath, extract_dir=unpack_folder)
    except:
        log.error("Error unpacking ")

    if os.path.isdir(unpack_folder):
        log.debug('Unpacked folder {0}'.format(unpack_folder))
        return 0, unpack_folder
    else:
        return 1, "Unpack Un-sucessfull"


class logformatparser():
    def __init__(self, inpath, archive=False) -> None:
        self.inpath = inpath
        self.foldername = None
        self.filename = None
        self.error = None
        g_val = GlobalVars()

        if not os.path.exists(inpath):
            self._error("Input path not Exists")
            return
        if not archive and os.path.isdir(inpath):
            self.foldername = inpath
        if not archive and os.path.isfile(inpath):
            self.foldername, self.filename = os.path.split(
                os.path.realpath(inpath))
            #print("folder {0} file {1}".format(self.foldername, self.filename))

        if archive:
            ret, unpacked_folder_or_error = unpack_archive(inpath)
            log.debug("{0}: {1}".format(ret, unpacked_folder_or_error))
            g_val.archive_status = True
            if not ret:
                self.foldername = unpacked_folder_or_error
            else:
                self._error(unpacked_folder_or_error)
                return

        parsed_logs_folder = os.path.join(
            self.foldername, LOG_PARSER_TEMP_DIR)

        # Remove existing CACHE directory
        if os.path.exists(parsed_logs_folder):
            shutil.rmtree(parsed_logs_folder)

        if not os.path.exists(parsed_logs_folder):
            os.mkdir(parsed_logs_folder)

        g_val.parsed_logs_folder = parsed_logs_folder

        # Check if Log config file exists
        if not resources.is_resource("configs", "config.yaml"):
            self._error("Log config file not found")
            return

        # Load yaml file
        with resources.open_text("configs", "config.yaml") as lcf:
            try:
                self.log_format = yaml.safe_load(lcf.read())
            except:
                self._error("Log config YAML load error")

    def _error(self, error_str):
        self.error = error_str
        log.error(self.error)

    def _search(self, logName, logInfo):
        log.debug('Log Name {0}'.format(logName))
        log.debug('Log REGEX {0}'.format(logInfo.get('regex')))

        for log_name in logInfo.get('filename'):
            # Search for file recursively
            log_file_path = list(Path(self.foldername).rglob(log_name))
            if not log_file_path:
                return

            log_file = os.path.realpath(log_file_path[0])

            if not os.path.exists(log_file):
                return

            csv_filename = os.path.join(
                self.foldername, LOG_PARSER_TEMP_DIR, log_name + '.csv')

            # unformatted log file
            if logInfo.get('regex').lower() == 'unformatted':
                try:
                    df = pd.read_csv(log_file, delimiter="\n",
                                    skip_blank_lines=True, skipinitialspace=True,
                                    names=['log', ], encoding='utf-8',
                                    lineterminator='\n')
                    df.to_csv(csv_filename, index=False)
                except:
                    pass
                return
            # regex
            log_regex = re.compile(logInfo.get('regex'))

            # hdfstore = os.path.join(
            #    self.foldername, LOG_PARSER_TEMP_DIR, 'store.h5')
            #hdf = pd.HDFStore(hdfstore, mode='a')
            csv_fields = dict(log_regex.groupindex).keys()

            # Remove Null at the start of File
            with open(log_file, 'r+') as file:
                data = file.read().lstrip('\x00')
                file.seek(0)
                file.write(data)
                file.truncate()

            # write parsed data to CSV
            with open(csv_filename, 'w', newline="") as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
                csv_writer.writeheader()

                with open(log_file, 'r') as file:
                    for line in file:
                        match = log_regex.search(line)
                        if match is not None:
                            csv_writer.writerow(match.groupdict())

                # hdf.put(log_name, pd.read_csv(csv_filename), format='table', data_columns=True,
                #        complevel=0)
                # hdf.close()

        log.debug('{0} parsed successfully'.format(logName))

    def _rg_log_parsing(self, inpath):
        parse_rg_log = rglogparser(inpath)
        if not parse_rg_log.error:
            parse_rg_log.ParseLogs()

    def _cm_log_parsing(self, inpath):
        log.debug('CM Log Parsing {0}'.format(inpath))

    def ParseLogs(self):
        if not self.foldername:
            return
        log.debug(' Parse Logs')
        # TODO: Need to revisit
        #   - is it worth to avoid parsing if existing parsed folder is present?
        #   - what if user updates log file within the cached folder?
        #   - Add GUI option to remove cache folder
        #parsed_logs_folder = os.path.join(self.foldername, LOG_PARSER_TEMP_DIR)
        # if os.path.exists(parsed_logs_folder):
        #    if os.listdir(parsed_logs_folder):
        #        g_val = GlobalVars()
        #        g_val.parsed_logs_folder = parsed_logs_folder
        #        return

        if self.filename:
            if (self.filename).lower().startswith('rg'):
                self._rg_log_parsing(self.inpath)
            elif (self.filename).lower().startswith('cm'):
                self._cm_log_parsing(self.inpath)
            else:
                for logName in self.log_format.get('logfiles'):
                    log_filename = self.log_format.get('logfiles')[logName]
                    for filename in log_filename['filename']:
                        if self.filename.lower() == filename.lower():
                            self._search(logName, self.log_format.get(
                                'logfiles')[logName])
        else:
            with concurrent.futures.ThreadPoolExecutor() as TPE:
                futures = []
                for logName in self.log_format.get('logfiles'):
                    log.debug(' Log format {0}'.format(logName))
                    # TODO: if we have existing parsed file then we can avoid parsing again
                    futures.append(TPE.submit(self._search, logName,
                                              self.log_format.get('logfiles')[logName]))

                    for future in concurrent.futures.as_completed(futures):
                        log.debug("{0}".format(future.result()))

            #print("RG Log Parsing")
            with concurrent.futures.ThreadPoolExecutor() as TPE:
                futures = []
                # i can't magically know that the given log file is RG console log
                # unless user specify starting log file name as rg*|RG*
                for rgfile in list(Path(self.foldername).rglob('rg*')):
                    futures.append(TPE.submit(self._rg_log_parsing,
                                              os.path.realpath(rgfile)))
                # same applies for CM log
                for cmfile in list(Path(self.foldername).rglob('cm*')):
                    futures.append(TPE.submit(self._cm_log_parsing,
                                              os.path.realpath(cmfile)))

                for future in concurrent.futures.as_completed(futures):
                    log.debug("{0}".format(future.result()))
            #print("RG Log Parsing completed")


if __name__ == '__main__':
    # input_folder = os.path.join(os.path.dirname(
    #    __file__), 'WiFilog.txt.0')

    input_folder = os.path.join(os.path.dirname(
        __file__), 'WiFilog.txt.0')
    #parser = logformatparser(input_folder, archive=True)
    parser = logformatparser(input_folder)
    if parser.error:
        print(parser.error)
    else:
        parser.ParseLogs()
    '''
    input_file = os.path.join(os.path.dirname(__file__), 'triage.tar')
    err, ret = unpack_archive(input_file)
    if err:
        print(ret)
    else:
        print("RET ", ret)
    '''
