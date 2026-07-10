#!/usr/bin/env python3
"""This is a generic script to plot the percentage of X fragmented traffic 
over the years. X being IPv4, an L4 protocol, or a service."""
import sys
from pathlib import Path
import argparse
import timeit
import datetime
#from distutils.util import strtobool

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import numpy as np

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import strtobool,create_output_dir


def process(
    run_dir: str,
    infilename_ipv4_all: str,
    infilename_ipv4_frags: str,
    outfilename_no_extension: str,
    _plot_title: str,
    log_scale: bool,
):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    infiledirpath = f"{run_dir}/csv/years"
    infilepath_ipv4_all = f"{infiledirpath}/{infilename_ipv4_all}"
    csv_ipv4_all = pd.read_csv(infilepath_ipv4_all, index_col=0)
    infilepath_ipv4_frags = f"{infiledirpath}/{infilename_ipv4_frags}"
    csv_ipv4_frags = pd.read_csv(infilepath_ipv4_frags, index_col=0)

    csv_prop = csv_ipv4_frags.div(csv_ipv4_all)
    print("process: csv_prop: ", csv_prop)

    # Plot
    _fig, ax1 = plt.subplots()
    year_i_v = [int(k) for k in csv_prop.index.values]
    year_str_v = [str(k) for k in csv_prop.index.values]
    frag_number_y = [
        row["Number of packets"] * 100 for _, row in csv_prop.iterrows()
    ]
    frag_bytes_y = [
        row["Data size (bytes)"] * 100 for _, row in csv_prop.iterrows()
    ]

    ax1.plot(year_i_v, frag_number_y, 'black', linestyle=':')
    ax1.plot(year_i_v, frag_bytes_y, 'black', linestyle='-')
    ax1.set_ylabel('% of fragmented IPv4 traffic', color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    if log_scale:
        ax1.set_yscale('log')

    ax2 = ax1.twinx()
    ipv4_bytes_y = [
        row["Data size (bytes)"] for _, row in csv_ipv4_all.iterrows()
    ]
    print('ipv4_bytes_y: ', ipv4_bytes_y)
    ax2.bar(year_i_v, ipv4_bytes_y, color='r', alpha=0.25)
    ax2.set_ylabel('total IPv4 bytes', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    if log_scale:
        ax2.set_yscale('log')

    ax1.set_xticks(year_i_v,
                   labels=year_str_v,
                   rotation=45,
                   ha="right",
                   rotation_mode="anchor")

    custom_legend_lines = [
        Line2D([0], [0], color="black", lw=1, linestyle='-'),
        Line2D([0], [0], color="black", lw=1, linestyle=':')
    ]
    plt.legend(custom_legend_lines, ['bytes', 'packets'], loc='upper left')

    # create output dir if does not exist
    outfile_plot_dir = f"{run_dir}/plot"
    create_output_dir(outfile_plot_dir)
    outfilepath = f"{outfile_plot_dir}/{outfilename_no_extension}.pdf"
    plt.savefig(outfilepath, bbox_inches='tight', dpi=250)

    # Csv
    data = {
        "Number of packets": {
            "min": min(frag_number_y),
            "max": max(frag_number_y),
            "mean": np.mean(frag_number_y),
            "median": np.median(frag_number_y),
        },
        "Data size (bytes)": {
            "min": min(frag_bytes_y),
            "max": max(frag_bytes_y),
            "mean": np.mean(frag_bytes_y),
            "median": np.median(frag_bytes_y),
        },
    }
    df = pd.DataFrame(data)

    # create output dir if does not exist
    outfile_csv_dir = f"{run_dir}/csv/years"
    create_output_dir(outfile_csv_dir)
    outfilepath = f"{outfile_csv_dir}/{outfilename_no_extension}.csv"
    df.to_csv(outfilepath)

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
    parser.add_argument("--run-dir", type=str, required=True)
    parser.add_argument("--infilename-ipv4-all", type=str, required=True)
    parser.add_argument("--infilename-ipv4-frags", type=str, required=True)
    parser.add_argument("--outfilename-no-extension", type=str, required=True)
    parser.add_argument("--plot-title", type=str, required=True)
    #parser.add_argument("-lc", "--log-scale", type=lambda x: bool(strtobool(x)), required=False, default=False)
    parser.add_argument("--log-scale",
                        type=strtobool,
                        required=False,
                        default=False)
    args = parser.parse_args()

    run_dir = args.run_dir
    infilename_ipv4_all = args.infilename_ipv4_all
    infilename_ipv4_frags = args.infilename_ipv4_frags
    outfilename_no_extension = args.outfilename_no_extension
    plot_title = args.plot_title
    log_scale = args.log_scale
    print("run_dir: ", run_dir)
    print("infilename_ipv4_all: ", infilename_ipv4_all)
    print("infilename_ipv4_frags: ", infilename_ipv4_frags)
    print("outfilename_no_extension: ", outfilename_no_extension)
    print("plot_title: ", plot_title)
    print("log_scale: ", log_scale)

    process(
        run_dir,
        infilename_ipv4_all,
        infilename_ipv4_frags,
        outfilename_no_extension,
        plot_title,
        log_scale,
    )

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
