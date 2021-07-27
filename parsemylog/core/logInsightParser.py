#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import yaml
from pathlib import Path

import concurrent.futures
import pandas as pd

# Local imports
from .core import log, GlobalVars


# Log Config File
LOG_CONFIGS_PATH = \
    os.path.join(os.path.dirname(__file__), '../configs')


class loginsightparser():
    def __init__(self) -> None:
        self.error = None

    def _error(self, error_str):
        self.error = error_str
        log.error(self.error)

    def __search(self, file_csv, insight_yml, insight_op):
        log.debug("CSV: {0} insight_yml {1} insight_op {2}".format(
            file_csv, insight_yml, insight_op))
        # Load yaml file
        with open(insight_yml, 'r') as f_yml:
            try:
                insight_log_format = yaml.safe_load(f_yml.read())
            except:
                self._error("Log config YAML load error")
                return

        # From CSV load data Frame
        try:
            with open(file_csv, 'r') as f_csv:
                df = pd.read_csv(file_csv)
        except:
            return

        df_op = pd.DataFrame(columns=['Reason', 'log'])
        pattern_sequence = insight_log_format['loginsight'].items()
        for seq, pattern in sorted(pattern_sequence):
            token, reason = pattern.values()
            if not df.empty and 'log' in df.columns:
                match = df[df.log.str.contains(
                    pat=token, regex=True, na=False) == True]
                if match.empty:
                    continue

            df_op = df_op.append({'Reason': reason, 'log': match.log.iloc[0]},
                                 ignore_index=True)

        df_op.to_csv(insight_op, index=False)

    def ParseLogs(self):
        g_val = GlobalVars()
        if not os.path.exists(g_val.parsed_logs_folder):
            return

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for file in os.listdir(g_val.parsed_logs_folder):
                insight_yml = Path(file).stem
                #print(file, insight_yml)
                insight_op_file = os.path.join(
                    g_val.parsed_logs_folder,  insight_yml + '-i.csv')
                insight_yml = os.path.join(
                    LOG_CONFIGS_PATH, insight_yml + '.yaml')

                if not os.path.exists(insight_yml):
                    continue

                csv_file = os.path.join(g_val.parsed_logs_folder, file)
                # TODO: if we have existing parsed file then we can avoid parsing again
                futures.append(executor.submit(self.__search, csv_file, insight_yml,
                                               insight_op_file))

            for future in concurrent.futures.as_completed(futures):
                log.debug("{0}".format(future.result()))


if __name__ == '__main__':
    g_val = GlobalVars()
    g_val.parsed_logs_folder = 'rdkbcore/.RDKLogParser'
    # log.debug("test")
    parser = loginsightparser()
    if parser.error:
        print(parser.error)
    else:
        parser.ParseLogs()
