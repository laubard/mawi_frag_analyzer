#!/usr/bin/env python3
"""The script generates a given number of random dates between two years."""
import sys
from pathlib import Path
import os
import argparse
import glob
import json
from datetime import date, timedelta
import random

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import create_output_dir

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


def process(
    mawi_data_path: str,
    outfilepath: str,
    year_start: int,
    year_end: int,
    day_number_per_year: int,
):
    """The script's core logic. Adapted from https://www.geeksforgeeks.org/python/python-generate-k-random-dates-between-two-other-dates/."""
    print("process: start")

    year_date_v_hm_v = []

    for year in range(year_start, year_end, 1):
        # initialize dates ranges
        year_day_first, year_day_last = date(year, 1, 1), date(year, 12, 31)
        print("The original range : " + str(year_day_first) + " " +
              str(year_day_last))

        # get days between dates
        dates_bet = year_day_last - year_day_first
        total_days = dates_bet.days

        date_v = []
        for _idx in range(day_number_per_year):
            random.seed(a=None)

            # get random days
            randay = random.randrange(total_days)

            # get random dates
            date_candidate = year_day_first + timedelta(days=randay)
            date_candidate_str = date_candidate.strftime("%Y-%m-%d")

            while date_candidate_str in date_v or not does_file_exist_and_is_not_empty(
                    date_candidate, mawi_data_path):
                randay = random.randrange(total_days)
                date_candidate = year_day_first + timedelta(days=randay)
                date_candidate_str = date_candidate.strftime("%Y-%m-%d")

            date_v.append(date_candidate_str)

        date_v_no_duplicates = list(set(date_v))
        assert len(date_v) == len(date_v_no_duplicates)

        # store random dates for the current year
        year_date_v_hm_v.append({"year": year, "date_v": sorted(date_v)})

    # create output dir if does not exist and save data
    outfile_csv_dir = os.path.dirname(outfilepath)
    create_output_dir(outfile_csv_dir)

    with open(outfilepath, "w", encoding="utf-8") as f:
        json.dump(year_date_v_hm_v, f)

    print("process: end")


def main(_argv):
    """The script's entry point."""
    print("main: start")
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outfilepath", type=str, required=True)
    parser.add_argument("-mdp", "--mawi-data-path", type=str, required=True)
    parser.add_argument("-ys", "--year-start", type=int, required=True)
    parser.add_argument("-ye", "--year-end", type=int, required=True)
    parser.add_argument("-dnpy",
                        "--day-number-per-year",
                        type=int,
                        required=True)
    args = parser.parse_args()

    outfilepath = args.outfilepath
    mawi_data_path = args.mawi_data_path
    year_start = args.year_start
    year_end = args.year_end + 1
    day_number_per_year = args.day_number_per_year
    print("mawi_data_path: ", mawi_data_path)
    print("year_start: ", year_start)
    print("year_end: ", year_end)
    print("outfilepath: ", outfilepath)
    print("day_number_per_year: ", day_number_per_year)

    process(
        mawi_data_path,
        outfilepath,
        year_start,
        year_end,
        day_number_per_year,
    )

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
