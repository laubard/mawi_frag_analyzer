#!/usr/bin/python3
""""This script computes the number of fragment series with original datagram
size inside hardcoded size ranges. Results are stored in a separate CSV based
on the series' trace year."""
import argparse
import json
import os
import sys
from pathlib import Path
import glob
from threading import Thread
import timeit
import datetime

import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_path, create_output_dir


def get_range_label(range_str_v: list, range_i_v: list,
                    datagram_size: int) -> int:
    """Bind a datagram size with its range."""
    for i, (range_min, range_max) in enumerate(range_i_v):
        if range_min <= datagram_size <= range_max:
            return range_str_v[i]
    sys.exit(f'Datagram size {datagram_size} not in ranges {range_i_v}')


def build_sk_range_datagram_size_df(log_v: list) -> pd.DataFrame:
    """Build a dataframe with series kind (sk) as keys and ranges of original
    datagram sizes as values."""
    print("build_sk_range_datagram_size_df: start")

    range_str_v = [
        '0-555', '556-1259', '1260-1479', '1480', '1481-1700', '1701-65515',
        '65516-131063', 'Unknown', 'Inconsistency'
    ]
    print("build_sk_range_datagram_size_df: range_str_v: ", range_str_v)
    range_i_v = [(0, 555), (556, 1259), (1260, 1479), (1480, 1480),
                 (1481, 1700), (1701, 65515), (65516, 131063)]
    print("build_sk_range_datagram_size_df: range_i_v: ", range_i_v)

    sk_v = [
        'Any', 'Correct', 'Complete', 'Incomplete', 'Duplicate', 'Overlap',
        'InOrder', 'ReverseOrder', 'OutOfOrder'
    ]
    sk_range_datagram_size_hm = {
        sk: {
            size_range: 0
            for size_range in range_str_v
        }
        for sk in sk_v
    }

    for log in log_v:
        with open(log, encoding='utf8') as file:
            json_content = json.load(file)

        # iterate across ip flows
        t3_stat_c = json_content['hm']
        for t3_stat_d in t3_stat_c.values():
            for flow_stat_v in t3_stat_d['t3_conversations'].values():
                for flow_stat in flow_stat_v:

                    if flow_stat['flow_stat_extension'] is None:
                        continue

                    if "FromAllChunks" in flow_stat['flow_stat_extension'][
                            'datagram_size_d'] or "FromSomeChunks" in flow_stat[
                                'flow_stat_extension']['datagram_size_d']:
                        datagram_size = list(flow_stat['flow_stat_extension']
                                             ['datagram_size_d'].values())[0]
                        range_label = get_range_label(range_str_v, range_i_v,
                                                      datagram_size)
                    else:  # either inconsistent or unknown datagram size
                        range_label = flow_stat['flow_stat_extension'][
                            'datagram_size_d']
                    #print("build_sk_range_datagram_size_df: range_label: ",range_label)
                    assert range_label in range_str_v

                    # log unusual datagram size
                    if range_label == '65516-131063':
                        date = build_date_from_path(log)
                        print(
                            f"Range '65516-131063' with {datagram_size} in {date} trace for {t3_stat_d['three_tuple']}"
                        )

                    sk_range_datagram_size_hm['Any'][range_label] += 1
                    for serie_kind in flow_stat['flow_stat_extension'][
                            'series_kind_v']:
                        sk_range_datagram_size_hm[serie_kind][range_label] += 1

    # from dict to dataframe
    df = pd.DataFrame(data=sk_range_datagram_size_hm.values(),
                      index=list(sk_range_datagram_size_hm.keys()),
                      columns=range_str_v)
    df.index.name = "serie_kind"
    print("build_sk_range_datagram_size_df: end")

    return df


class YearThread(Thread):
    """Every thread takes care of only one year's traces."""

    def __init__(self, year: str, run_dir: str, infilename: str,
                 outfile_dir: str, outfilename: str):
        super().__init__()
        self.year = year
        self.run_dir = run_dir
        self.infilename = infilename
        self.outfile_dir = outfile_dir
        self.outfilename = outfilename

    def run(self):
        print("run: start: self.year: ", self.year)

        # create output dir if does not exist
        outfile_dir_year = f"{self.outfile_dir}/{self.year}"
        print("run: outfile_dir_year: ", outfile_dir_year)
        os.makedirs(outfile_dir_year, exist_ok=True)

        # find file path
        log_v = glob.glob(f"{self.run_dir}/{self.year}/**/{self.infilename}",
                          recursive=True)

        df = build_sk_range_datagram_size_df(log_v)

        # save csv
        outfile_dir = f"{outfile_dir_year}/{self.outfilename}"
        print("run: saving csv in ", outfile_dir)
        df.to_csv(outfile_dir)


def process(
    run_dir: str,
    infilename: str,
    outfilename: str,
    year_v: list,
):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    # create output dir if does not exist
    outfile_dir = f"{run_dir}/csv/year"
    create_output_dir(outfile_dir)

    # find file path
    if year_v is None or year_v == []:
        year_v = [
            os.path.basename(year_path)
            for year_path in glob.glob(f"{run_dir}/20*")
        ]
        print("process: year_v: ", year_v)

    thread_v = []
    for year in year_v:
        year_thread = YearThread(year, run_dir, infilename, outfile_dir,
                                 outfilename)
        year_thread.start()
        thread_v.append(year_thread)

    # wait for the thread to stop
    for thread in thread_v:
        thread.join()

    toc = timeit.default_timer()
    elapsed_seconds = toc - tic
    elapsed_seconds_readable = str(datetime.timedelta(seconds=elapsed_seconds))

    print("process: elapsed_seconds_readable: ", elapsed_seconds_readable)

    print("process: end")


def main():
    """The script's entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--run-dir", type=str, required=True)
    parser.add_argument("-i", "--infilename", type=str, required=True)
    parser.add_argument("-o", "--outfilename", type=str, required=True)
    parser.add_argument("-y",
                        "--years",
                        type=int,
                        choices=range(2007, 2026),
                        nargs="*",
                        help="Years to analyze. If no value \
                        is provided, all years of the run will be analyzed.",
                        required=False)
    args = parser.parse_args()

    run_dir = args.run_dir
    infilename = args.infilename
    outfilename = args.outfilename
    year_v = args.years
    print("main: run_dir: ", run_dir)
    print("main: infilename: ", infilename)
    print("main: outfilename: ", outfilename)
    print("main: year_v: ", year_v)

    process(run_dir, infilename, outfilename, year_v)


if __name__ == "__main__":
    main()
