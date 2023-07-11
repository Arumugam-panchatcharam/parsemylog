#!/usr/bin/python
# -*- coding: utf-8 -*-

import yaml
import re
import csv
import os
from pathlib import Path
import shutil

from threading import Thread
import concurrent.futures
from importlib import resources

import pandas as pd

import core.global_var as globalvar

class LogFormatParser(Thread):
    def __init__(self, inpath=None, archive=False) -> None:
        self.inpath = inpath
        self.is_archive = archive
        self.foldername = None
        self.filename = None
        self.error = None
        self.log_format = None
        self.parsed_logs_folder = None
        self.log_parser_temp_dir = globalvar.get_val("LOG_PARSER_TEMP_DIR")
        self.log = globalvar.get_val("LOGGER")

    def set_path(self,inpath, archive=False):
        self.inpath = inpath
        self.is_archive = archive

        if not os.path.exists(inpath):
            self._error("Input path not Exists")
            return
        if os.path.isdir(inpath):
            self.foldername = inpath
        if os.path.isfile(inpath):
            self.foldername, self.filename = os.path.split(
                os.path.realpath(inpath))
            self.log.debug("folder {0} file {1}".format(self.foldername, self.filename))

        self.parsed_logs_folder = os.path.join(
            self.foldername, self.log_parser_temp_dir)
        
        globalvar.set_val("PARSED_LOGS_FOLDER", self.parsed_logs_folder)

        # Remove existing CACHE directory
        if os.path.exists(self.parsed_logs_folder):
            shutil.rmtree(self.parsed_logs_folder)

        if not os.path.exists(self.parsed_logs_folder):
            os.mkdir(self.parsed_logs_folder)

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
        self.log.error(self.error)

    def _search(self, logname, logInfo):
        self.log.debug('Log Name {0}'.format(logname))
        self.log.debug('Log REGEX {0}'.format(logInfo.get('regex')))

        for log_name in logInfo.get('filename'):
            # Search for file recursively
            log_file_path = list(Path(self.foldername).rglob(log_name))
            if not log_file_path:
                continue

            log_file = os.path.realpath(log_file_path[0])

            if not os.path.exists(log_file):
                return

            csv_filename = os.path.join(
                self.foldername, self.log_parser_temp_dir, log_name + '.csv')

            # unformatted log file
            if logInfo.get('regex').lower() == 'unformatted':
                try:
                    df = pd.read_csv(log_file, delimiter="\n",
                                     skip_blank_lines=True, skipinitialspace=True,
                                     names=['log', ], encoding='utf-8',
                                     lineterminator='\n')
                    df.to_csv(csv_filename, encoding='utf-8', index=False)
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

        self.log.debug('{0} parsed successfully'.format(logname))

    def ParseLogs(self):
        if not self.foldername:
            return
        self.log.debug(' Parse Logs')
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
                pass
                #self._rg_log_parsing(self.inpath)
            elif (self.filename).lower().startswith('cm'):
                pass
                #self._cm_log_parsing(self.inpath)
            else:
                for logname in self.log_format.get('logfiles'):
                    log_filename = self.log_format.get('logfiles')[logname]
                    for filename in log_filename['filename']:
                        if self.filename.lower() == filename.lower():
                            self._search(logname, self.log_format.get(
                                'logfiles')[logname])
        else:
            with concurrent.futures.ThreadPoolExecutor() as TPE:
                futures = []
                for logname in self.log_format.get('logfiles'):
                    self.log.debug('Log format {0}'.format(logname))
                    futures.append(TPE.submit(self._search, logname,
                                              self.log_format.get('logfiles')[logname]))

                    for future in concurrent.futures.as_completed(futures):
                        pass
                        #self.log.debug("Thread exit return {0}".format(future.result()))


if __name__ == '__main__':
    pass