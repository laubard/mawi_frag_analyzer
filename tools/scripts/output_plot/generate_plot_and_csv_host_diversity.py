#!/usr/bin/env python3
"""This script builds the Fig 5. of the paper. It also stores the precise 
numbers into a CSV file."""
import sys
from pathlib import Path
import os
import argparse
import json
import timeit
import datetime

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_path, get_year_from_date, create_output_dir, find_log_v


def percent_decrease(ref: int, new: int) -> float:
    """Compute percentage decrease."""
    return ((ref - new) / ref) * 100


def from_32_to_24_prefix(ip: str) -> str:
    """Provide the /24 of a /32 IPv4 address."""
    return '.'.join(list(ip.split('.')[:2] + ['0']))


def from_32_to_16_prefix(ip: str) -> str:
    """Provide the /16 of a /32 IPv4 address."""
    return '.'.join(list(ip.split('.')[:1] + ['0', '0']))

def build_host_hm(path: str) -> dict:
    """Build the lists of srcIP and three tuples without duplicates from a trace."""
    with open(path, encoding='utf8') as file:
        json_content = json.load(file)

    src_ip_v = []
    t3_v = []
    t3_stat_c = json_content['hm']
    for t3_stat_d in t3_stat_c.values():
        t3_v.append(
            (t3_stat_d["three_tuple"]["src"], t3_stat_d["three_tuple"]["dst"],
             t3_stat_d["three_tuple"]["l4_proto"]))
        src_ip_v.append(t3_stat_d["three_tuple"]["src"])

    src_ip_v_no_duplicates = list(set(src_ip_v))
    t3_v_no_duplicates = list(set(t3_v))

    return {"src_ip_v": src_ip_v_no_duplicates, "t3_v": t3_v_no_duplicates}


def build_year_host_hm(date_host_hm: dict) -> dict:
    """Group the lists of srcIP and three tuples from traces of the same year."""
    year_host_hm = {}

    for date, host_hm in date_host_hm.items():
        year = get_year_from_date(date)

        if year not in year_host_hm:
            year_host_hm.update({year: host_hm})
        else:
            year_host_hm_to_extend = year_host_hm[year]
            year_host_hm_to_extend["src_ip_v"] += host_hm["src_ip_v"]
            year_host_hm_to_extend["t3_v"] += host_hm["t3_v"]

    year_host_hm_no_duplicates = {
        year: {
            "src_ip_v": list(set(host_hm["src_ip_v"])),
            "t3_v": list(set(host_hm["t3_v"]))
        }
        for year, host_hm in year_host_hm.items()
    }

    return year_host_hm_no_duplicates


def build_year_host_wth_prefixes_hm(year_host_hm: dict) -> dict:
    """Build the lists of srcIP and three tuples from traces of the same year, 
    for /32, /24 and /16 IPv4 addresses."""
    year_host_prefixes_hm = {}

    for year, host_hm in year_host_hm.items():
        prefix_32_src_ip_v = host_hm["src_ip_v"]
        prefix_32_t3_v = host_hm["t3_v"]

        prefix_24_src_ip_v = [
            from_32_to_24_prefix(src_ip) for src_ip in host_hm["src_ip_v"]
        ]
        prefix_24_src_ip_v_no_duplicates = list(set(prefix_24_src_ip_v))
        prefix_24_t3_v = [(from_32_to_24_prefix(src_ip),
                           from_32_to_24_prefix(dst_ip), l4_proto)
                          for (src_ip, dst_ip, l4_proto) in host_hm["t3_v"]]
        prefix_24_t3_v_no_duplicates = list(set(prefix_24_t3_v))

        prefix_16_src_ip_v = [
            from_32_to_16_prefix(src_ip) for src_ip in host_hm["src_ip_v"]
        ]
        prefix_16_src_ip_v_no_duplicates = list(set(prefix_16_src_ip_v))
        prefix_16_t3_v = [(from_32_to_16_prefix(src_ip),
                           from_32_to_16_prefix(dst_ip), l4_proto)
                          for (src_ip, dst_ip, l4_proto) in host_hm["t3_v"]]
        prefix_16_t3_v_no_duplicates = list(set(prefix_16_t3_v))

        year_host_prefixes_hm.update({
            year: {
                "prefix_32_src_ip_v": prefix_32_src_ip_v,
                "prefix_32_t3_v": prefix_32_t3_v,
                "prefix_24_src_ip_v": prefix_24_src_ip_v_no_duplicates,
                "prefix_24_t3_v": prefix_24_t3_v_no_duplicates,
                "prefix_16_src_ip_v": prefix_16_src_ip_v_no_duplicates,
                "prefix_16_t3_v": prefix_16_t3_v_no_duplicates,
            }
        })

    return year_host_prefixes_hm


def prepare_csv_data(year_host_wth_prefixes_hm: dict) -> dict:
    """Prepare dictionary for CSV storing."""
    csv_data = {
        year: {
            "prefix_32_src_ip_v":
            host_wth_prefixes_hm["prefix_32_src_ip_v"],
            "prefix_32_src_ip_v_len":
            len(host_wth_prefixes_hm["prefix_32_src_ip_v"]),
            "prefix_32_t3_v":
            host_wth_prefixes_hm["prefix_32_t3_v"],
            "prefix_32_t3_v_len":
            len(host_wth_prefixes_hm["prefix_32_t3_v"]),
            "prefix_24_src_ip_v":
            host_wth_prefixes_hm["prefix_24_src_ip_v"],
            "prefix_24_src_ip_v_len":
            len(host_wth_prefixes_hm["prefix_24_src_ip_v"]),
            "prefix_24_t3_v":
            host_wth_prefixes_hm["prefix_24_t3_v"],
            "prefix_24_t3_v_len":
            len(host_wth_prefixes_hm["prefix_24_t3_v"]),
            "prefix_16_src_ip_v":
            host_wth_prefixes_hm["prefix_16_src_ip_v"],
            "prefix_16_src_ip_v_len":
            len(host_wth_prefixes_hm["prefix_16_src_ip_v"]),
            "prefix_16_t3_v":
            host_wth_prefixes_hm["prefix_16_t3_v"],
            "prefix_16_t3_v_len":
            len(host_wth_prefixes_hm["prefix_16_t3_v"]),
            "prefix_32_24_decrease_nb":
            len(host_wth_prefixes_hm["prefix_32_src_ip_v"]) -
            len(host_wth_prefixes_hm["prefix_24_src_ip_v"]),
            "prefix_32_24_decrease_perc":
            percent_decrease(len(host_wth_prefixes_hm["prefix_32_src_ip_v"]),
                             len(host_wth_prefixes_hm["prefix_24_src_ip_v"])),
            "prefix_32_16_decrease_nb":
            len(host_wth_prefixes_hm["prefix_32_src_ip_v"]) -
            len(host_wth_prefixes_hm["prefix_16_src_ip_v"]),
            "prefix_32_16_decrease_perc":
            percent_decrease(len(host_wth_prefixes_hm["prefix_32_src_ip_v"]),
                             len(host_wth_prefixes_hm["prefix_16_src_ip_v"])),
            "prefix_24_16_decrease_nb":
            len(host_wth_prefixes_hm["prefix_24_src_ip_v"]) -
            len(host_wth_prefixes_hm["prefix_24_src_ip_v"]),
            "prefix_24_16_decrease_perc":
            percent_decrease(len(host_wth_prefixes_hm["prefix_24_src_ip_v"]),
                             len(host_wth_prefixes_hm["prefix_16_src_ip_v"])),
        }
        for year, host_wth_prefixes_hm in year_host_wth_prefixes_hm.items()
    }

    return csv_data

def process(
    run_dir: str,
    infilename: str,
    year_v: list,
    outfilename: str,
):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    # Find logs
    log_v = find_log_v(run_dir,year_v,infilename)

    # Build the lists of srcIP and three tuples for all the trace dates
    date_host_hm = {
        build_date_from_path(log): build_host_hm(log)
        for log in log_v
    }

    # Group by year
    year_host_hm = build_year_host_hm(date_host_hm)

    # Extend /32 lists to /24 and /16 lists
    year_host_wth_prefixes_hm = build_year_host_wth_prefixes_hm(year_host_hm)

    csv_data = prepare_csv_data(year_host_wth_prefixes_hm)

    # Plot srcIP nb
    _fig, ax1 = plt.subplots()
    year_v = list(year_host_wth_prefixes_hm.keys())

    prefix_32_src_ip_y = [
        host_hm["prefix_32_src_ip_v_len"] for host_hm in csv_data.values()
    ]
    prefix_24_src_ip_y = [
        host_hm["prefix_24_src_ip_v_len"] for host_hm in csv_data.values()
    ]

    ax1.plot(year_v, prefix_32_src_ip_y, 'black', linestyle='-')
    ax1.plot(year_v, prefix_24_src_ip_y, 'black', linestyle='--')

    ax1.set_ylabel('No. source IP addresses', color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    plt.grid()

    # Plot t3 nb
    ax2 = ax1.twinx()
    prefix_32_t3_y = [
        host_hm["prefix_32_t3_v_len"] for host_hm in csv_data.values()
    ]
    prefix_24_t3_y = [
        host_hm["prefix_24_t3_v_len"] for host_hm in csv_data.values()
    ]
    ax2.plot(year_v, prefix_32_t3_y, 'r', linestyle='-')
    ax2.plot(year_v, prefix_24_t3_y, 'r', linestyle='--')
    ax2.set_ylabel('No. three-tuples', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    ax1.set_xticks(range(len(year_v)),
                   labels=year_v,
                   rotation=45,
                   ha="right",
                   rotation_mode="anchor")

    ax2.set_yticks([0, 20000, 40000, 60000, 80000])

    custom_legend_lines = [
        Line2D([0], [0], color="black", lw=1, linestyle='-'),
        Line2D([0], [0], color="black", lw=1, linestyle='--')
    ]
    plt.legend(custom_legend_lines, ['/32 prefixes', '/24 prefixes'])

    # create output dir if does not exist
    outfile_plot_dir = f"{run_dir}/plot/years"
    print("process: outfile_plot_dir: ", outfile_plot_dir)
    os.makedirs(outfile_plot_dir, exist_ok=True)
    outfile_path_png = f"{outfile_plot_dir}/{outfilename}.png"
    print("process: outfile_path_png: ", outfile_path_png)
    plt.savefig(outfile_path_png, bbox_inches='tight', dpi=200)

    # Csv
    csv_df = pd.DataFrame(
        data=csv_data.values(),
        index=list(csv_data.keys()),
    )

    # create output dir if does not exist
    outfile_csv_dir = f"{run_dir}/csv/years"
    create_output_dir(outfile_csv_dir)
    csv_df.to_csv(f'{outfile_csv_dir}/{outfilename}.csv')

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
    args = parser.parse_args()

    run_dir = args.run_dir
    infilename = args.infilename
    year_v = args.years
    outfilename = args.outfilename
    print("run_dir: ", run_dir)
    print("infilename: ", infilename)
    print("year_v: ", year_v)
    print("outfilename: ", outfilename)

    process(
        run_dir,
        infilename,
        year_v,
        outfilename,
    )

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
