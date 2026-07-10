#!/usr/bin/env python3
"""The script randomly select a 15-min PCAP file every X hours from every year's 24h capture."""
import sys
import os
import argparse
import glob
import random
from datetime import date
import csv


# TODO: Populate this dictionary to fit your need
def get_LONG_TRACE_DIR_TRACE_DATE_HM() -> dict:
    #return {
    #    "/export_mawi/DITL/2011": "20110608",
    #    "/export_mawi/DITL/2012": "20120330",
    #    "/export_mawi/DITL/2013/notemachi": "20130625",
    #    "/export_mawi/DITL/20141002": "20141002",
    #    "/export_mawi/DITL/2015": "20151202",
    #    "/export_mawi/DITL/2017": "20170412",
    #    "/export_mawi/DITL/2018": "20180509",
    #    "/export_mawi/DITL/2019": "20190409",
    #    "/export_mawi/DITL/2020": "20200408",
    #    "/export_mawi/DITL/2021": "20210414",
    #    "/export_mawi/DITL/2022": "20220413",
    #    "/export_mawi/DITL/2023": "20230412",
    #    "/export_mawi/DITL/2025": "20250409",
    #}
    pass



def does_file_exist_and_is_not_empty(d_date: date,
                                     mawi_data_path: str) -> bool:
    """The function verifies the pcap file actually exist and is non empty."""
    year = d_date.strftime('%Y')
    month = d_date.strftime('%m')
    day = d_date.strftime('%d')
    date_candidate_mawi_path_no_extension = f"{mawi_data_path}/{year}/{month}/{year}-{month}-{day}"

    date_candidate_mawi_path_resolution = glob.glob(
        f"{date_candidate_mawi_path_no_extension}.*")

    if len(date_candidate_mawi_path_resolution) == 0:
        return False
    if len(date_candidate_mawi_path_resolution) != 1:
        print(
            f"{year}-{month}-{day} exists with different extensions ({date_candidate_mawi_path_resolution})"
        )

    if os.stat(date_candidate_mawi_path_resolution[0]).st_size <= 32:
        return False

    return True


def build_fake_date(trace_name: str, hours: int, pos: int) -> str:
    """This function generates a fake date from the given year's 24h trace, hours and position. 
    This is done in order to be able to re-use scripts from the daily analysis."""
    year = trace_name[0:4]
    if hours == 2:
        month = f"{pos + 1:02d}"
    else:  # ie hours = 4
        month = f"{pos * 2 + 1:02d}"
    day = "01"

    return f'{year}-{month}-{day}'


def process(outfilepath: str, hours: int):
    """The script's core logic."""
    print("process: start")

    csv_rows_v = []

    LONG_TRACE_DIR_TRACE_DATE_HM = get_LONG_TRACE_DIR_TRACE_DATE_HM()
    #for dir_path, trace_date in LONG_TRACE_DIR_TRACE_DATE_HM.items():
    for dir_path, trace_date in LONG_TRACE_DIR_TRACE_DATE_HM.items():
        # find list of traces for the given 24h dir and date
        trace_v = glob.glob(f'{dir_path}/{trace_date}*.*')
        trace_v.sort()

        # the 24h capture is divised into 24 * 4 (15-min) pcap files
        if len(trace_v) != 24 * 4:
            sys.exit(
                f"Not all traces ({len(trace_v)}) are present in {dir_path} (considering there are 24*4 traces for a given day)"
            )

        # group traces every x hours
        group_trace_nb = hours * 4
        trace_v_v = [
            trace_v[i * group_trace_nb:(i + 1) * group_trace_nb]
            for i in range(0,
                           len(trace_v) // group_trace_nb)
        ]

        # find a random trace in every trace group
        random.seed(a=None)
        current_trace_random_v = [
            random.choice(traces) for traces in trace_v_v
        ]

        csv_rows_v.append([[
            trace_date, random_trace_path,
            os.path.basename(random_trace_path),
            build_fake_date(os.path.basename(random_trace_path), hours, i)
        ] for i, random_trace_path in enumerate(current_trace_random_v)])

    # write results in csv
    header = ["date", "path_to_trace", "trace_name", "fake_date"]
    csv_rows = [e for v in csv_rows_v for e in v]

    with open(outfilepath, 'w', encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)  # Create writer object
        csvwriter.writerow(header)  # Write header
        csvwriter.writerows(csv_rows)  # Write multiple rows

    print("process: end")


def main(_argv):
    """The script's entry point."""
    print("main: start")
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfilepath", type=str, required=True)
    parser.add_argument(
        "--hours",
        type=int,
        choices=[2, 4],
        required=True,
        help="Keep a 15-min trace every X hours from the 24h trace")
    args = parser.parse_args()

    outfilepath = args.outfilepath
    hours = args.hours

    print("outfilepath: ", outfilepath)
    print("hours: ", hours)

    process(
        outfilepath,
        hours,
    )

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
