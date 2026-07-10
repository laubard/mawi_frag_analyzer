#!/usr/bin/python3
"""This file contains general-purpose functions."""
import os
import glob
import ast

import numpy as np
import pandas as pd
import statistics

def build_date_from_path(path: str) -> str:
    """Build date (year-month-day) from a PCAP or log path."""
    log_dir = os.path.basename(os.path.dirname(path))
    year = log_dir.split('-')[1]
    month = log_dir.split('-')[2]
    day = log_dir.split('-')[3]
    return f'{year}-{month}-{day}'


def build_date_from_capinfo_path(path: str) -> str:
    """Build date (year-month-day) from a PCAP or log path."""
    log_dir = os.path.basename(os.path.dirname(path))
    year = log_dir.split('-')[0]
    month = log_dir.split('-')[1]
    day = log_dir.split('-')[2]
    return f'{year}-{month}-{day}'

def build_date_from_path_basename_left(path: str) -> str:
    """Build date (year-month-day) from a PCAP or log path."""
    log_dir = os.path.basename(path).split('.')[0]
    year = log_dir.split('-')[0]
    month = log_dir.split('-')[1]
    day = log_dir.split('-')[2]
    return f'{year}-{month}-{day}'

def build_datetime64_from_path(path:str) -> np.datetime64:
    """Build a datetime64 object from a PCAP or log path."""
    log_dir = os.path.basename(os.path.dirname(path))
    print("build_datetime64_from_path: log_dir: ",log_dir)
    year = log_dir.split('-')[1]
    month = log_dir.split('-')[2]
    day = log_dir.split('-')[3]
    return np.datetime64(f'{year}-{month}-{day}')

def get_year_from_date(date: str) -> str:
    """Retrieve year from a date (year-month-day)."""
    return date.split('-')[0]

def get_year_from_path(path: str) -> str:
    """Provide the trace year from a PCAP path."""
    log_dir = os.path.basename(path)
    return log_dir.split('-')[0]

def create_output_dir(path:str):
    """Build a dir if does not exist."""
    print("create_output_dir: path: ", path)
    os.makedirs(path, exist_ok=True)


def find_log_v(run_dir:str,year_v:list,infilename:str) -> list:
    """Find the list of log with name $infilename."""
    if year_v is None or year_v == []:
        log_v = glob.glob(f"{run_dir}/**/{infilename}", recursive=True)
    else:
        log_v_v = [
            glob.glob(f"{run_dir}/{year}/**/{infilename}", recursive=True)
            for year in year_v
        ]
        log_v = [log for log_v in log_v_v for log in log_v]
    assert len(log_v) > 0
    log_v.sort()

    return log_v

def strtobool(val: str) -> bool:
    """Since strtobool from distutils.util is deprecated, re-implement it.
    Convert the val string into a bool."""
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    if val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    raise ValueError(f"invalid truth value {val}")


def build_iat_median_and_min_v(year_start: int, year_end: int,
                               df: pd.DataFrame, xmax: int) -> tuple:
    """Build the representative iat median and min for each srcIP between two 
    years."""
    # filter series not in year range from df
    year_v = list(range(year_start, year_end + 1, 1))
    print("build_iat_median_and_min_v: year_v: ", year_v)
    df_from_year_v = df[df['date'].apply(
        lambda x: int(x.split('-')[0]) in year_v)]

    # get non-duplicate list of srcIP
    src_ip_v = list(set(df_from_year_v['src_ip']))

    iat_median_v = []
    iat_min_v = []
    # iterate over the hosts
    for src_ip in src_ip_v:
        quadruplet_df = df_from_year_v[df_from_year_v['src_ip'] == src_ip]
        # for each srcIP host, find the series with the max nb of frags
        max_num_chunks_pos = quadruplet_df['num_chunks'].idxmax()
        quadruplet_iat_v_str = quadruplet_df.loc[max_num_chunks_pos, 'iat_v']
        quadruplet_iat_float_v = ast.literal_eval(quadruplet_iat_v_str)

        # keep only if iat_median is under xmax
        iat_median = statistics.median(quadruplet_iat_float_v)
        if iat_median <= xmax:
            iat_median_v.append(iat_median)
            iat_min_v.append(min(quadruplet_iat_float_v))

    return tuple((iat_median_v, iat_min_v))
