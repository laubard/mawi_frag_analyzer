#!/usr/bin/env python3
"""This scripts plots Fig. 3 of the paper, and stores precise numbers in CSV files. 
It performs the analysis for all series kind."""
import sys
from pathlib import Path
import os
import argparse
import glob
import itertools

import matplotlib.pyplot as plt
from matplotlib.container import BarContainer
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import create_output_dir


def process(
    run_dir: str,
    infilename_no_extension: str,
):
    """The script's core logic."""
    print("process: start")

    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)

    # create output dir if does not exist
    outfile_plot_dir = f"{run_dir}/plot/years"
    create_output_dir(outfile_plot_dir)
    outfile_csv_dir = f"{run_dir}/csv/years"
    create_output_dir(outfile_csv_dir)

    infile_dir = f"{run_dir}/csv/year"
    print("process: infile_dir: ", infile_dir)

    year_dir_v = [
        year_path
        for year_path in glob.glob(f"{infile_dir}/20*")
    ]
    year_dir_v.sort()
    print("process: year_dir_v: ", year_dir_v)

    # get each year's csv data
    year_csv_hm = {
        os.path.basename(year_dir):
        pd.read_csv(f"{year_dir}/{infilename_no_extension}.csv",
                    index_col='serie_kind')
        for year_dir in year_dir_v
    }
    # normalize each row so that the values in each row sum is 1.
    normalized_year_csv_hm = {
        year: df.div(df.sum(axis=1), axis=0)
        for year, df in year_csv_hm.items()
    }

    with open(year_dir_v[0], 'r', encoding = 'utf-8') as f:
        series_kind_v = list(pd.read_csv(f).index.values)
    print("process: series_kind_v: ", series_kind_v)

    # plot
    plt.figure(dpi=300)

    csv_header_pretty_v = [
        "[0,555]",
        "[556,1259]",
        "[1260,1479]",
        "1480",
        "[1481,1700]",
        "[1701,65515]",
        "[65516,...]",
        "unknown",
        "inconsistent",
    ]
    for series_kind in series_kind_v:
        # with normalized data
        normalized_data = [[year] + list(dict(csv.loc[series_kind]).values())
                           for year, csv in normalized_year_csv_hm.items()]
        normalized_year_any_sk_df = pd.DataFrame(normalized_data,
                                                 columns=['years'] +
                                                 csv_header_pretty_v)

        ax = normalized_year_any_sk_df.plot(x="years",
                                            kind="bar",
                                            stacked=True,
                                            rot=45)

        # add hatches to improve readibility
        bars = [
            thing for thing in ax.containers
            if isinstance(thing, BarContainer)
        ]
        patterns = itertools.cycle(
            ('|', '++', 'x', '\\\\', '*', 'O', '--', '//', '..'))
        d = {}
        for b_bar in bars:
            for patch in b_bar:
                pat = d.setdefault(patch.get_facecolor(), next(patterns))
                patch.set_hatch(pat)

        ax.legend(bbox_to_anchor=(1.0, 1.0))
        ax.set_xlabel("")
        ax.set_ylabel("Original (guessed) datagram size percentage")

        # save plot
        outfile_path = f"{outfile_plot_dir}/{infilename_no_extension}_{series_kind}_stacked"
        outfile_path_pdf = f"{outfile_path}.pdf"
        print("process: outfile_path_pdf: ", outfile_path_pdf)
        plt.savefig(outfile_path_pdf, bbox_inches='tight', dpi=250)
        outfile_path_png = f"{outfile_path}.png"
        print("process: outfile_path_png: ", outfile_path_png)
        plt.savefig(outfile_path_png, bbox_inches='tight', dpi=250)

        # save csv
        outfile_normalized_path_csv = f"{outfile_csv_dir}/{infilename_no_extension}-normalized_{series_kind}.csv"
        print("process: outfile_noramlized_path_csv: ",
              outfile_normalized_path_csv)
        normalized_year_any_sk_df.to_csv(outfile_normalized_path_csv)

        # with non normalized data
        data = [[year_range] +
                list(dict(merged_csv.loc[series_kind]).values())
                for year_range, merged_csv in year_csv_hm.items()]
        non_normalized_year_any_sk_df = pd.DataFrame(data,
                                                     columns=['years'] +
                                                     csv_header_pretty_v)
        print("process: year_any_sk_df (non normalized): ",
              non_normalized_year_any_sk_df)
        year_any_sk_df = pd.DataFrame(data,
                                      columns=['years'] + csv_header_pretty_v)

        # save csv
        outfile_path_csv = f"{outfile_csv_dir}/{infilename_no_extension}_{series_kind}.csv"
        print("process: outfile_path_csv: ", outfile_path_csv)
        year_any_sk_df.to_csv(outfile_path_csv)

    print("process: end")


def main(_argv):
    """The script's entry point."""
    print("main: start")
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--run-dir", type=str, required=True)
    parser.add_argument("-i", "--infilename", type=str, required=True)
    parser.add_argument("-ygg",
                        "--year-granularity-grouping",
                        type=int,
                        required=False)
    args = parser.parse_args()

    run_dir = args.run_dir
    infilename_no_extension = args.infilename
    print("run_dir: ", run_dir)
    print("infilename_no_extension: ", infilename_no_extension)

    process(run_dir, infilename_no_extension)

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
