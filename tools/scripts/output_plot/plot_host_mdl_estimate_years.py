#!/usr/bin/python3
"""This scripts plot the Fig. 12 of the paper."""
import sys
from pathlib import Path
import argparse
import timeit

from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import create_output_dir, build_iat_median_and_min_v


def process(run_dir: str, infilename_overlap: str, infilename_duplicate: str,
            outfilename: str, xmax: int):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    # read input CSV files
    dir_csv = f"{run_dir}/csv/years"
    df_overlap = pd.read_csv(f"{dir_csv}/{infilename_overlap}", header=0)
    df_overlap.reset_index(drop=True, inplace=True)
    df_duplicate = pd.read_csv(f"{dir_csv}/{infilename_duplicate}", header=0)
    df_duplicate.reset_index(drop=True, inplace=True)

    # merge df
    # ignore_index does not work as we could expect (https://stackoverflow.com/questions/32801806/pandas-concat-columns-ignore-index-doesnt-work)
    df = pd.concat([df_overlap, df_duplicate], axis=0)
    df.reset_index(drop=True, inplace=True)
    print("process: len(df)", len(df))

    # compute iat min and median for each srcIP across the years
    year_iat_info_hm_hm = {
        year: build_iat_median_and_min_v(year, year, df, xmax)
        for year in list(range(2007, 2025 + 1, 1))
    }

    # compute proportion of srcIP with min or median under 5 or 30 seconds
    mdl_under_5_median_y = [
        sum(
            list(1 for iat_median in year_iat_info_hm_hm[year][0]
                 if iat_median <= 5.0)) / len(year_iat_info_hm_hm[year][0]) *
        100 if year in year_iat_info_hm_hm
        and len(year_iat_info_hm_hm[year][0]) != 0 else 0
        for year in year_iat_info_hm_hm
    ]
    mdl_under_5_min_y = [
        sum(
            list(1 for iat_min in year_iat_info_hm_hm[year][1]
                 if iat_min <= 5.0)) / len(year_iat_info_hm_hm[year][1]) *
        100 if year in year_iat_info_hm_hm
        and len(year_iat_info_hm_hm[year][0]) != 0 else 0
        for year in year_iat_info_hm_hm
    ]
    mdl_under_30_median_y = [
        sum(
            list(1 for iat_median in year_iat_info_hm_hm[year][0]
                 if iat_median <= 30.0)) / len(year_iat_info_hm_hm[year][0]) *
        100 if year in year_iat_info_hm_hm
        and len(year_iat_info_hm_hm[year][0]) != 0 else 0
        for year in year_iat_info_hm_hm
    ]
    mdl_under_30_min_y = [
        sum(
            list(1 for iat_min in year_iat_info_hm_hm[year][1]
                 if iat_min <= 30.0)) / len(year_iat_info_hm_hm[year][1]) *
        100 if year in year_iat_info_hm_hm
        and len(year_iat_info_hm_hm[year][0]) != 0 else 0
        for year in year_iat_info_hm_hm
    ]

    # plot results
    _fig, ax = plt.subplots()
    year_v = list(year_iat_info_hm_hm.keys())
    ax.plot(year_v, mdl_under_5_min_y, color='blue', marker='o')
    ax.plot(year_v, mdl_under_30_min_y, color='orange', marker='D')
    ax.plot(year_v,
            mdl_under_5_median_y,
            color='blue',
            marker='o',
            linestyle='dotted')
    ax.plot(year_v,
            mdl_under_30_median_y,
            color='orange',
            marker='D',
            linestyle='dotted')
    ax.legend([
        "MDL under 5 sec (min)", "MDL under 30 sec (min)",
        "MDL under 5 sec (median)", "MDL under 30 sec (median)"
    ],
              loc="upper left",
              bbox_to_anchor=(0, 1.15),
              ncols=2)

    # Text in the x-axis will be displayed in 'YYYY-mm' format.
    year_str_v = [str(year) for year in year_v]
    ax.set_xticks(year_v,
                  labels=year_str_v,
                  rotation=45,
                  ha="right",
                  rotation_mode="anchor")
    ax.set_yticks(range(0, 101, 25),
                  labels=[f"{perc}%" for perc in range(0, 101, 25)])
    ax.set_ylabel("srcIP host proportion")
    ax.grid(axis="both")

    # create plot output dir if does not exist
    outfile_dir_plot = f"{run_dir}/plot/years"
    create_output_dir(outfile_dir_plot)
    plt.savefig(f"{outfile_dir_plot}/{outfilename}.pdf",
                bbox_inches='tight',
                dpi=250)

    toc = timeit.default_timer()
    elapsed_seconds = toc - tic
    elapsed_seconds_readable = str(timedelta(seconds=elapsed_seconds))

    print("process: elapsed_seconds_readable: ", elapsed_seconds_readable)

    print("process: end")


def main():
    """The script's entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=str, required=True)
    parser.add_argument("-io", "--infilename-overlap", type=str, required=True)
    parser.add_argument("-id",
                        "--infilename-duplicate",
                        type=str,
                        required=True)
    parser.add_argument("-o", "--outfilename", type=str, required=True)
    parser.add_argument("--xmax", type=int, required=True)
    args = parser.parse_args()

    run_dir = args.run_dir
    infilename_overlap = args.infilename_overlap
    infilename_duplicate = args.infilename_duplicate
    outfilename = args.outfilename
    xmax = args.xmax
    print("main: run_dir: ", run_dir)
    print("main: infilename_overlap: ", infilename_overlap)
    print("main: infilename_duplicate: ", infilename_duplicate)
    print("main: outfilename: ", outfilename)
    print("main: xmax: ", xmax)

    process(run_dir, infilename_overlap, infilename_duplicate, outfilename,
            xmax)


if __name__ == "__main__":
    main()
