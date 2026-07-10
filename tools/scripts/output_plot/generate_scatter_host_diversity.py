#!/usr/bin/env python3
"""This script plots Fig. 11 of the paper."""
import sys
from pathlib import Path
import argparse
import glob
import json
import timeit
import datetime

import matplotlib.pyplot as plt

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_path, get_year_from_date, create_output_dir


def build_host_total_series_or_bytes_sent_hm(log_v: list,
                                             series_or_bytes: str) -> dict:
    """For each srcIP present in the traces, compute its total number of 
    series or sent bytes."""
    print("build_host_total_series_or_bytes_sent_hm: start")
    print("build_host_total_series_or_bytes_sent_hm: series_or_bytes: ",
          series_or_bytes)

    if series_or_bytes == "series":
        index = "total_num_datagrams"
    elif series_or_bytes == "bytes":
        index = "total_bytes"
    else:
        sys.exit(1)
    print("build_host_total_series_or_bytes_sent_hm: index: ", index)

    total_series_or_bytes = 0
    hosts_series_or_bytes_hm = {}
    # iterate over the logs
    for log in log_v:
        with open(log, encoding='utf8') as file:
            json_content = json.load(file)

        t3_stat_c = json_content['hm']
        for t3_stat_d in t3_stat_c.values():

            src_ip = t3_stat_d['three_tuple']['src']
            # update entry for the give srcIP
            if src_ip in hosts_series_or_bytes_hm:
                current = hosts_series_or_bytes_hm[src_ip] + t3_stat_d[index]
                hosts_series_or_bytes_hm.update({src_ip: current})
                total_series_or_bytes += t3_stat_d[index]
            else:
                hosts_series_or_bytes_hm.update({src_ip: t3_stat_d[index]})
                total_series_or_bytes += t3_stat_d[index]

    total = sum(list(v for v in hosts_series_or_bytes_hm.values()))
    print("build_host_total_series_or_bytes_sent_hm: total: ", total)
    print("build_host_total_series_or_bytes_sent_hm: total_series_or_bytes: ",
          total_series_or_bytes)

    # sort
    hosts_series_or_bytes_hm_sorted = {
        k: v / total_series_or_bytes * 100
        for k, v in sorted(hosts_series_or_bytes_hm.items(),
                           key=lambda item: item[1],
                           reverse=True)
    }
    print("build_host_total_series_or_bytes_sent_hm: end")

    return hosts_series_or_bytes_hm_sorted


def process(run_dir: str, infilename: str, year_v: list, outfilename: str,
            series_or_bytes: str):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    # find years if not provided
    if year_v is None or year_v == []:
        log_v = glob.glob(f"{run_dir}/**/{infilename}", recursive=True)
        year_v = list(
            set(
                get_year_from_date(build_date_from_path(log)) for log in log_v
            ))

    year_v.sort()
    year_host_info = {}
    for year in year_v:
        # find all traces from given year
        year_log_v = glob.glob(f"{run_dir}/{year}/**/{infilename}",
                               recursive=True)
        # sum number of series and data bytes for the year's traces
        host_total_series_or_bytes_sent_hm = build_host_total_series_or_bytes_sent_hm(
            year_log_v, series_or_bytes)
        year_host_info.update({year: host_total_series_or_bytes_sent_hm})

    # plot results
    _fig, ax = plt.subplots()

    # scatters
    top1_y = [
        sum(list(year_host_info[year].values())[j] for j in range(1))
        for year in year_v
    ]
    top10_y = [
        sum(list(year_host_info[year].values())[j] for j in range(10))
        for year in year_v
    ]
    top100_y = [
        sum(list(year_host_info[year].values())[j] for j in range(100))
        for year in year_v
    ]
    x = year_v

    ax.plot(x, top1_y, color='red', marker='^')
    ax.plot(x, top10_y, color='blue', marker='o')
    ax.plot(x, top100_y, color='orange', marker='D')
    ax.legend(["Top 1 host", "Top 10 hosts", "Top 100 hosts"],
              loc="upper left",
              bbox_to_anchor=(0, 1.1),
              ncols=3)


    # Text in the x-axis will be displayed in 'YYYY-mm' format.
    ax.set_xticks(year_v,
                  labels=year_v,
                  rotation=45,
                  ha="right",
                  rotation_mode="anchor")
    ax.set_yticks(range(0, 101, 25),
                  labels=[f"{perc}%" for perc in range(0, 101, 25)])
    ax.set_ylabel("Cumulative host traffic")
    ax.grid(axis="y")

    # create output dir if does not exist
    outfile_plot_dir = f"{run_dir}/plot/years"
    create_output_dir(outfile_plot_dir)
    outfile_path_png = f"{outfile_plot_dir}/{outfilename}.png"
    print("process: outfile_path_png: ", outfile_path_png)
    plt.savefig(outfile_path_png, bbox_inches='tight')

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
    parser.add_argument("-i", "--infilename", type=str, required=True)
    parser.add_argument("-y",
                        "--years",
                        type=int,
                        choices=range(2007, 2026),
                        nargs="*",
                        help="Years to analyze. If no value \
                        is provided, all years of the run will be analyzed.",
                        required=False)
    parser.add_argument("-o", "--outfilename", type=str, required=True)
    parser.add_argument("--series-or-bytes",
                        type=str,
                        choices=["series", "bytes"],
                        required=True)
    args = parser.parse_args()

    run_dir = args.run_dir
    infilename = args.infilename
    year_v = args.years
    outfilename = args.outfilename
    series_or_bytes = args.series_or_bytes
    print("run_dir: ", run_dir)
    print("infilename: ", infilename)
    print("year_v: ", year_v)
    print("outfilename: ", outfilename)
    print("series_or_bytes: ", series_or_bytes)

    process(run_dir, infilename, year_v, outfilename, series_or_bytes)

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
