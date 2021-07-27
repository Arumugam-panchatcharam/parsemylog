#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pandas as pd
from importlib import resources
import yaml
from .core import log, GlobalVars
import sys
import re


def parse(input_folder):
    df = pd.read_csv(input_folder, delimiter="\n",
                     skip_blank_lines=True, skipinitialspace=True)
    print(df)
    df.columns = ["log"]
    df.to_csv('rg.csv')


# Summary Order
SUMMARY_ORDER = {1: 'rg', 2: 'cm', 3: 'cr', 4: 'wifi'}


class rglogparser():
    def __init__(self, inp) -> None:
        self.inpath = inp
        self.filename = None
        self.foldername = None
        self.log_format = None
        self.error = None

        if not os.path.exists(inp) and not os.path.isfile(inp):
            self._error("Path not Exists or input is not a file")
            return

        self.foldername, self.filename = os.path.split(
            os.path.realpath(inp))

        g_val = GlobalVars()

        self.RG_LOG_SUMMARY = os.path.join(
            g_val.parsed_logs_folder, self.filename + '-s.txt')
        #print("g_VAL", g_val.parsed_logs_folder)
        #print("RG LOG SUMMARY", self.RG_LOG_SUMMARY)
        self.RG_LOG = os.path.join(self.foldername, self.filename)

        # load RG log formatter
        with resources.open_text("configs", "RG.yaml") as rgyml:
            try:
                self.log_format = yaml.safe_load(rgyml.read())
            except:
                self._error("RG Log formatter Load error")
                return

    def _write_to_summary_file(self, key, val, fd):
        line = ''
        for v in zip(key, val):
            line = line + "{0} ".format(' : '.join(v))

        if key[0].lower().endswith('version'):
            line = line + self._blversion(*val)
        elif key[0].upper().startswith('OTP'):
            line = line + '\n\t' + self._otp(val[0], val[2])

        fd.write('\t{0}\n'.format(line))

    def _parse_summary(self, log_insight, fd_rg_sum):

        try:
            df = pd.read_csv(self.RG_LOG, delimiter="\n",
                             skip_blank_lines=True, skipinitialspace=True,
                             names=['log', ])
        except:
            return

        df = df.drop_duplicates()

        if df.empty:
            return

        for insight_list in log_insight:
            fd_rg_sum.write(self._format_head(insight_list, '-'))

            info_list = log_insight.get(insight_list)
            for key, value in dict(info_list).items():
                regex = re.compile(value)
                group = list(regex.groupindex)

                df_str = df.loc[df.log.str.match(
                    value)]

                if df_str.empty:
                    continue

                # set - to remove duplicates
                val = regex.findall(*df_str.values.tolist()[0])

                if not val:
                    continue

                if len(group) == 1:
                    self._write_to_summary_file(
                        group, val, fd_rg_sum)
                else:
                    self._write_to_summary_file(
                        group, list(*val), fd_rg_sum)

    def _parse_marker(self, log_marker, fd_rg_sum):

        fd_rg_sum.write(self._format_head("Markers", '-'))
        for key, value in dict(log_marker).items():
            regex = re.compile(value)
            group = list(regex.groupindex)
            # set - to remove duplicates
            #val = regex.findall(file_buffer)

            # if not val:
            #    continue
            try:
                df = pd.read_csv(self.RG_LOG, delimiter="\n",
                                 skip_blank_lines=True, skipinitialspace=True,
                                 names=['log', ])
            except:
                return

            if key.lower().startswith("reboot"):
                reboot_count = df.loc[df.log.str.contains(
                    pat=value, regex=True, na=False)].count()

                if reboot_count.item() > 1:
                    line = [str(reboot_count.item()) + ' Reboots Detected']
                    key = [key, ]
                    self._write_to_summary_file(key, line, fd_rg_sum)

    def ParseLogs(self):
        if not self.log_format or not (self.filename and self.foldername):
            return

        with open(self.RG_LOG_SUMMARY, 'w') as fd_rg_sum:
            log_insight = self.log_format.get('loginsight')
            fd_rg_sum.write(self._format_head(
                "RG Log Summary - " + self.filename, '=', sp='\t'*4))

            self._parse_summary(log_insight, fd_rg_sum)
            log_marker = self.log_format.get('markers')

            self._parse_marker(log_marker, fd_rg_sum)

    def _otp(self, otp1, otp3):
        if not (otp1 and otp3):
            return ""
        market_code = "NOT SET"
        xver = "NOT SET"
        customer_code = "NOT SET"
        tch_prod = "NOT SET"
        # OTP 1
        # ---------+-------+------+-----
        # 31..24   |23..16 |15..8 |7..0
        # ---------+-------+------+-----
        # chk_sum  |MC     |MC    |X-ver
        # ---------+-------+------+-----
        MC_MASK = 0x00FFFF00
        MC_SHIFT = 8
        XVER_MASK = 0x000000FF
        otp_1 = int(otp1, 16)

        xver = [(otp_1 & XVER_MASK) if otp_1 & XVER_MASK else xver]

        market_code = [(otp_1 & MC_MASK) >> MC_SHIFT if otp_1 &
                       MC_MASK else market_code]
        # OTP 3
        # ---------+---------------+------+-----
        # 31..24   |23..16         |15..8 |7..0
        # ---------+---------------+------+-----
        # TCH_PROD |cmsSign_Revo   |CC    |X-ver
        # ---------+---------------+------+-----
        TCH_PROD_MASK = 0xF0000000
        CC_MASK = 0x0000FF00
        CC_SHIFT = 8
        otp_3 = int(otp3, 16)
        tch_prod = ["SET" if otp_3 & TCH_PROD_MASK else tch_prod]

        customer_code = [(otp_3 & CC_MASK) >> CC_SHIFT if otp_3 &
                         CC_MASK else customer_code]

        return 'Market Code: {0} Customer Code: {1} X-VER: {2} TCH_PROD: {3}'.format(market_code, customer_code, xver, tch_prod)

    def _blversion(self, version):
        if not version:
            return ""
        TEST = ['0', '3', '6']
        PROD = ['1', '4', '7']
        DEV = ['2', '5', '8']

        if version[-1] in TEST:
            return "(TEST Bootloader)"
        elif version[-1] in PROD:
            return "(PROD Bootloader)"
        elif version[-1] in DEV:
            return "(DEV Bootloader)"
        else:
            return "(Incorrect BL version)"

    def _error(self, error_str):
        self.error = error_str
        log.error(self.error)

    def _format_head(self, h, format, sp=''):
        return "{0}{1}\n{0}{2}\n".format(sp, h, format*len(h))


if __name__ == '__main__':
    sys.path.append(os.path.dirname('../configs'))
    input_folder = os.path.join(os.path.dirname(
        __file__), 'rg_xi6.log')
    # parse(input_folder)
    rg = rglogparser(input_folder)
    if rg.error:
        print(rg.error)
    else:
        rg.ParseLogs()
