#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

import pandas as pd
import matplotlib.pyplot as plt

import numpy as np

# Ref: https://wiki.rdkcentral.com/display/RDK/RDK-B+Logger
LOG_LEVEL_MAPPING = {
    "FATAL":  0,
    "ERROR":  1,
    "WARN":   2,
    "NOTICE": 3,
    "INFO":   4,
    "DEBUG":  5,
    "TRACE1": 6,
    "TRACE2": 7,
    "TRACE3": 8,
    "TRACE4": 9,
    "TRACE5": 10,
    "TRACE6": 11,
    "TRACE7": 12,
    "TRACE8": 13,
    "TRACE9": 14
}


def plot_me(df, csv_filename):
    plt.title(csv_filename.upper())
    plt.xlabel('Log Level')
    plt.ylabel('Frequencey')

    series = dict(df['log_level'].value_counts())
    plt.bar(series.keys(), series.values())

    plt.show()


def logstat(csv_filename):
    df = pd.read_csv(csv_filename)
    df.drop_duplicates(inplace=True)
    #df['log_index'] = df['log_level'].map(MAPPING)
    #df = df.applymap(lambda s: MAPPING.get(s) if s in MAPPING else s)
    print(df)
    # df.plot()
    filter = df['log_level'] == "ERROR"
    df = df[filter]
    print(df)
    #plot_me(df, csv_filename)


if __name__ == '__main__':
    logstat('WiFilog.txt.1.csv')
