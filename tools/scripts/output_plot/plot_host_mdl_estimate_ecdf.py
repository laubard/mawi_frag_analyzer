#!/usr/bin/python3
"""This scripts plot the Fig. 7 of the paper."""
import sys
from pathlib import Path
import argparse
import timeit
from datetime import timedelta

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import create_output_dir, build_iat_median_and_min_v


def prepare_csv_entry(iat_median_v: list, iat_min_v: list) -> dict:
    """Prepare CSV file entry: provide y value at x = (1.0, 5.0, 30.0)."""
    iat_min_array = np.sort(np.array(iat_min_v))
    iat_median_array = np.sort(np.array(iat_median_v))

    return {
        "at_1sec_min":
        np.searchsorted(iat_min_array, 1.0, side="right") / len(iat_min_array),
        "at_5sec_min":
        np.searchsorted(iat_min_array, 5.0, side="right") / len(iat_min_array),
        "at_30sec_min":
        np.searchsorted(iat_min_array, 30.0, side="right") /
        len(iat_min_array),
        "at_1sec_median":
        np.searchsorted(iat_median_array, 1.0, side="right") /
        len(iat_median_array),
        "at_5sec_median":
        np.searchsorted(iat_median_array, 5.0, side="right") /
        len(iat_median_array),
        "at_30sec_median":
        np.searchsorted(iat_median_array, 30.0, side="right") /
        len(iat_median_array),
    }


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

    # compute iat min and median for each srcIP and period
    (iat_median_v_20072014,
     iat_min_v_20072014) = build_iat_median_and_min_v(2007, 2014, df, xmax)
    (iat_median_v_20152020,
     iat_min_v_20152020) = build_iat_median_and_min_v(2015, 2020, df, xmax)
    (iat_median_v_20212025,
     iat_min_v_20212025) = build_iat_median_and_min_v(2021, 2025, df, xmax)

    # plot ECDFs
    _fig, ax = plt.subplots()
    ax.ecdf(iat_min_v_20072014, color='black', linestyle='solid')
    ax.ecdf(iat_median_v_20072014, color='black', linestyle='dotted')
    ax.ecdf(iat_min_v_20152020, color='blue', linestyle='solid')
    ax.ecdf(iat_median_v_20152020, color='blue', linestyle='dotted')
    ax.ecdf(iat_min_v_20212025, color='red', linestyle='solid')
    ax.ecdf(iat_median_v_20212025, color='red', linestyle='dotted')
    ax.set_xticks([0, 5, 30, 120])
    ax.grid()
    ax.set_ylabel("ECDF of source IP addresses")
    ax.set_xlabel("Inter-arrival time between overlapping fragments (seconds)")
    ax.legend([
        "2007-2014, min", "2007-2014, median", "2015-2020, min",
        "2015-2020, median", "2021-2025, min", "2021-2025, median"
    ])

    # create plot output dir if does not exist
    outfile_dir_plot = f"{run_dir}/plot/years"
    create_output_dir(outfile_dir_plot)
    # save plot
    plt.savefig(f"{outfile_dir_plot}/{outfilename}.pdf",
                bbox_inches='tight',
                dpi=250)

    # store precise results in CSV
    csv_data_hm = {
        "2007-2014": prepare_csv_entry(iat_median_v_20072014,
                                       iat_min_v_20072014),
        "2015-2020": prepare_csv_entry(iat_median_v_20152020,
                                       iat_min_v_20152020),
        "2021-2025": prepare_csv_entry(iat_median_v_20212025,
                                       iat_min_v_20212025),
    }
    df = pd.DataFrame(csv_data_hm)

    # save csv
    df.to_csv(f"{dir_csv}/{outfilename}.csv")

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
