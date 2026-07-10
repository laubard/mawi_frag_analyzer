#!/usr/bin/python3
"""This script plotos the Fig. 10 of the paper."""
import argparse
import os
import sys
from pathlib import Path
from glob import glob

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_capinfo_path, get_year_from_date, create_output_dir


def build_logfile_path_v(log_dir_v: list, filter_s: str) -> list:
    """Build list of logfile path from filter"""
    return [
        f"{log_dir}/{os.path.basename(log_dir)}_ipv4-frags_{filter_s}.csv"
        for log_dir in log_dir_v
    ]


def build_stats_hm(path: str) -> dict:
    """Read CSV data"""
    csv_data = pd.read_csv(path)
    if csv_data.empty:
        print("Empty ", path)
        return {"Number of packets": 0, "Data size (bytes)": 0}
    return {
        "Number of packets": csv_data["Number of packets"][0],
        "Data size (bytes)": csv_data["Data size (bytes)"][0]
    }


def build_year_stats_hm(date_stats_hm: dict) -> dict:
    """Groups log stats by year."""
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


def build_filter_stats_hm(path_v: list) -> dict:
    """Retrieve log stats and groups log stats by year."""
    date_filter_stats_hm = {
        build_date_from_capinfo_path(log): build_stats_hm(log)
        for log in path_v
    }
    return build_year_stats_hm(date_filter_stats_hm)


def plot_data(csv_index: str, y_label: str, output_filepath: str, udp_hm: dict,
              icmp_hm: dict, tcp_hm: dict, gre_hm: dict, esp_hm: dict,
              other_hm: dict):
    """Plot L4 stacked chart """
    year_v = list(udp_hm.keys())
    y_udp = [stats[csv_index] for stats in udp_hm.values()]
    y_icmp = [stats[csv_index] for stats in icmp_hm.values()]
    y_tcp = [stats[csv_index] for stats in tcp_hm.values()]
    y_gre = [stats[csv_index] for stats in gre_hm.values()]
    y_esp = [stats[csv_index] for stats in esp_hm.values()]
    y_other = [stats[csv_index] for stats in other_hm.values()]

    data = pd.DataFrame(
        {
            'UDP': y_udp,
            'ICMP': y_icmp,
            'TCP': y_tcp,
            'GRE': y_gre,
            'ESP': y_esp,
            'Other': y_other
        },
        index=year_v)
    data_perc = data.divide(data.sum(axis=1), axis=0)

    ax1 = plt.gca()
    stacks_ax1 = ax1.stackplot(
        year_v,
        data_perc["UDP"],
        data_perc["ICMP"],
        data_perc["TCP"],
        data_perc["GRE"],
        data_perc["ESP"],
        data_perc["Other"],
        labels=['UDP', 'ICMP', 'TCP', 'GRE', 'ESP', 'Other'])

    hatches = ["|", "++", "//", "\\\\", "*", 'O']
    for stack, hatch in zip(stacks_ax1, hatches):
        stack.set_hatch(hatch)

    ax1.legend()
    ax1.set_xlabel("Year")
    ax1.set_ylabel(f"{y_label} proportion")

    # Rotates and right-aligns the x labels so they don't crowd each other.
    for label in ax1.get_xticklabels(which='major'):
        label.set(rotation=45, ha="right", rotation_mode="anchor")
    plt.savefig(f"{output_filepath}_{y_label.lower()}.pdf",
                bbox_inches='tight',
                dpi=200)
    plt.savefig(f"{output_filepath}_{y_label.lower()}.png",
                bbox_inches='tight',
                dpi=200)
    plt.cla()
    data_perc = pd.concat([data_perc, data_perc.mean().to_frame('Average').T])
    print("data_perc for bytes: ", data_perc)


def process(run_dir: str, output_filepath: str, year_v: list):
    """The script's core logic."""
    print("process: start")

    # find dir of logs
    if year_v is not None and year_v != []:
        log_dir_v_v = [
            glob(f"{run_dir}/{year}-*-*", recursive=False) for year in year_v
        ]
        log_dir_v = [
            log_dir for log_dir_v in log_dir_v_v for log_dir in log_dir_v
        ]
    else:
        log_dir_v = glob(f"{run_dir}/20*-*-*", recursive=False)
    log_dir_v.sort()

    # build L4 proto logfile paths
    all_ipv4_frags_path_v = build_logfile_path_v(log_dir_v, "no-filter")
    udp_path_v = build_logfile_path_v(log_dir_v, "proto-17")
    icmp_path_v = build_logfile_path_v(log_dir_v, "proto-1")
    tcp_path_v = build_logfile_path_v(log_dir_v, "proto-6")
    gre_path_v = build_logfile_path_v(log_dir_v, "proto-47")
    esp_path_v = build_logfile_path_v(log_dir_v, "proto-50")

    # Retrieve L4 proto stats from logs
    all_ipv4_frag_stats_hm = build_filter_stats_hm(all_ipv4_frags_path_v)
    udp_stats_hm = build_filter_stats_hm(udp_path_v)
    icmp_stats_hm = build_filter_stats_hm(icmp_path_v)
    tcp_stats_hm = build_filter_stats_hm(tcp_path_v)
    gre_stats_hm = build_filter_stats_hm(gre_path_v)
    esp_stats_hm = build_filter_stats_hm(esp_path_v)

    # Compute stats for non udp, icmp, tcp, gre, and esp traffic
    year_other_stats_hm = {
        year: {
            "Data size (bytes)":
            all_frags["Data size (bytes)"] - udp["Data size (bytes)"] -
            icmp["Data size (bytes)"] - tcp["Data size (bytes)"] -
            gre["Data size (bytes)"] - esp["Data size (bytes)"],
            "Number of packets":
            all_frags["Number of packets"] - udp["Number of packets"] -
            icmp["Number of packets"] - tcp["Number of packets"] -
            gre["Number of packets"] - esp["Number of packets"],
        }
        for ((year, all_frags), udp, icmp, tcp, gre,
             esp) in zip(all_ipv4_frag_stats_hm.items(), udp_stats_hm.values(),
                         icmp_stats_hm.values(), tcp_stats_hm.values(),
                         gre_stats_hm.values(), esp_stats_hm.values())
    }

    # create output dir if does not exist
    dirname = os.path.dirname(output_filepath)
    create_output_dir(dirname)

    # bytes
    plot_data("Data size (bytes)", "Bytes", output_filepath, udp_stats_hm,
              icmp_stats_hm, tcp_stats_hm, gre_stats_hm, esp_stats_hm,
              year_other_stats_hm)

    # packets
    plot_data("Number of packets", "Packet", output_filepath, udp_stats_hm,
              icmp_stats_hm, tcp_stats_hm, gre_stats_hm, esp_stats_hm,
              year_other_stats_hm)

    print("process: end")


def main(_argv):
    """The script's entry point."""
    print("main: start")
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run-dir", type=str, default="")
    parser.add_argument("-o", "--output-filepath", type=str, default="")
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
    output_filepath = args.output_filepath
    year_v = args.years
    print("main: run_dir: ", run_dir)
    print("main: output_filepath: ", output_filepath)
    print("main: year_v: ", year_v)

    process(run_dir, output_filepath, year_v)

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
