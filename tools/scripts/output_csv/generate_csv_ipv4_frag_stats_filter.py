#!/usr/bin/env python3
"""This script groups capinfo data by years inside a CSV file"""
import sys
from pathlib import Path
import argparse
import glob
import timeit
import datetime

import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_capinfo_path, get_year_from_date, create_output_dir


def build_stats_hm(path: str) -> dict:
    """Retrieve capinfo csv data."""
    csv_data = pd.read_csv(path)
    if csv_data.empty:
        print("Empty ", path)
        return {"Number of packets": 0, "Data size (bytes)": 0}
    return {
        "Number of packets": csv_data["Number of packets"][0],
        "Data size (bytes)": csv_data["Data size (bytes)"][0]
    }


def build_year_stats_hm(date_stats_hm: dict) -> dict:
    """Group capinfo csv data by year."""
    year_stats_hm = {}

    for date, stats_hm in date_stats_hm.items():
        year = get_year_from_date(date)
        if year not in year_stats_hm:
            year_stats_hm.update({year: stats_hm})
        else:
            year_host_hm_to_extend = year_stats_hm[year]
            year_host_hm_to_extend["Number of packets"] += stats_hm[
                "Number of packets"]
            year_host_hm_to_extend["Data size (bytes)"] += stats_hm[
                "Data size (bytes)"]

    return year_stats_hm


def prepare_csv_data(year_stats_hm: dict) -> dict:
    """Prepare dictionary for CSV storing."""
    csv_data = {
        year: {
            "Number of packets": stats_hm["Number of packets"],
            "Data size (bytes)": stats_hm["Data size (bytes)"],
        }
        for year, stats_hm in year_stats_hm.items()
    }

    return csv_data


def process(
    run_dir: str,
    tcpdump_filter_name: str,
    year_v: list,
    outfilename: str,
):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    # find input csv files
    if year_v is None or year_v == []:
        log_v = glob.glob(f"{run_dir}/**/*ipv4[-_]{tcpdump_filter_name}.csv",
                          recursive=True)
    else:
        log_v_v = [
            glob.glob(f"{run_dir}/**/{year}*ipv4[-_]{tcpdump_filter_name}.csv",
                      recursive=True) for year in year_v
        ]
        log_v = [log for log_v in log_v_v for log in log_v]
    log_v_sorted = sorted(log_v)

    # retrieve and group capinfo data
    date_stats_hm = {
        build_date_from_capinfo_path(log): build_stats_hm(log)
        for log in log_v_sorted
    }
    year_stats_hm = build_year_stats_hm(date_stats_hm)

    # prepare data before storing
    csv_data = prepare_csv_data(year_stats_hm)
    csv_df = pd.DataFrame(
        data=csv_data.values(),
        index=list(csv_data.keys()),
    )

    # create output dir if does not exist
    outfile_csv_dir = f"{run_dir}/csv/years"
    create_output_dir(outfile_csv_dir)
    csv_df.to_csv(f'{outfile_csv_dir}/{outfilename}')

    toc = timeit.default_timer()
    elapsed_seconds = toc - tic
    elapsed_seconds_readable = str(datetime.timedelta(seconds=elapsed_seconds))

    print('\n\n')
    print("process: elapsed_seconds_readable: ", elapsed_seconds_readable)

    print("process: end")


def main(_argv):
    """The script's entry point."""
    print("main: start")
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--run-dir", type=str, required=True)
    parser.add_argument("-i", "--filter", type=str, required=True)
    parser.add_argument("-y",
                        "--years",
                        type=int,
                        choices=range(2007, 2026),
                        nargs="*",
                        help="Years to analyze. If no value \
                        is provided, all years of the run will be analyzed.",
                        required=False)
    parser.add_argument("-o", "--outfilename", type=str, required=True)
    args = parser.parse_args()

    run_dir = args.run_dir
    tcpdump_filter_name = args.filter
    year_v = args.years
    outfilename = args.outfilename
    print("run_dir: ", run_dir)
    print(tcpdump_filter_name)
    print("year_v: ", year_v)
    print("outfilename: ", outfilename)

    process(
        run_dir,
        tcpdump_filter_name,
        year_v,
        outfilename,
    )

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
