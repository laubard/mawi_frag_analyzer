#!/usr/bin/python3
"""This scripts plots the Fig. 2 of the paper."""
import argparse
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_path, get_year_from_date, create_output_dir, find_log_v

EMPTY_SERIES_KIND_OCCURRENCE_HM = {
    "Complete": 0,
    "Incomplete": 0,
    "Correct": 0,
    "Duplicate": 0,
    "Overlap": 0,
    "InOrder": 0,
    "OutOfOrder": 0,
    "ReverseOrder": 0
}

def get_empty_series_kind_occurence_hm() -> dict:
    """Provide a copy of EMPTY_SERIES_KIND_OCCURRENCE_HM"""
    return EMPTY_SERIES_KIND_OCCURRENCE_HM.copy()


def build_date_serie_info_hm_hm(log_v: list) -> tuple[dict, dict]:
    """Retrieve the number of series for every series kind and date."""
    print("build_date_serie_info_hm_hm: start")
    date_seriekind_occurence_hm_hm = {} # series nb for each date and series kind
    date_serie_occurence_hm = {} # series nb for each date

    # iterate over the log files
    for log in log_v:
        serie_occ = 0
        seriekind_occurence_hm = get_empty_series_kind_occurence_hm()
        with open(log, encoding='utf8') as file:
            json_content = json.load(file)
        date = build_date_from_path(log)

        t3_stat_c = json_content['hm']
        # iterate over the IP flows
        for t3_stat_d in t3_stat_c.values():
            for flow_stat_v in t3_stat_d['t3_conversations'].values():
                for flow_stat in flow_stat_v:
                    flow_stat_extension = flow_stat['flow_stat_extension']
                    if flow_stat_extension is None:
                        continue

                    serie_occ += 1
                    for serie_kind in flow_stat_extension['series_kind_v']:
                        if serie_kind in seriekind_occurence_hm:
                            seriekind_occurence_hm[serie_kind] += 1
                        else:
                            raise ValueError("Unexpected serie kind ",
                                             serie_kind)

        date_seriekind_occurence_hm_hm[date] = seriekind_occurence_hm
        date_serie_occurence_hm[date] = serie_occ

    # sort results by date
    sorted_date_seriekind_occurence_hm_hm = dict(
        sorted(date_seriekind_occurence_hm_hm.items()))
    sorted_date_serie_occurence_hm = dict(
        sorted(date_serie_occurence_hm.items()))

    print("build_date_serie_info_hm_hm: end")
    return sorted_date_seriekind_occurence_hm_hm, sorted_date_serie_occurence_hm


def build_year_seriekind_info_hm_hm(
    date_seriekind_info_hm_hm: dict,
    date_serie_occurence_hm: dict,
) -> tuple[dict, dict]:
    """Group series nb of series kind from date basis to year basis."""
    print("build_year_seriekind_info_hm_hm: start")

    year_seriekind_info_hm_hm = {}
    year_serie_occurence_hm = {}

    merged_serie_info_hm = get_empty_series_kind_occurence_hm()
    merged_serie_occurence = 0

    curr_year = -1
    for (date, seriekind_info_hm), (_, serie_occurence) in zip(
            date_seriekind_info_hm_hm.items(),
            date_serie_occurence_hm.items()):

        date_year = get_year_from_date(date)
        if curr_year == -1:
            curr_year = date_year

        if date_year != curr_year:
            # year has changed: store results and re-initialize variables
            year_seriekind_info_hm_hm[curr_year] = merged_serie_info_hm
            year_serie_occurence_hm[curr_year] = merged_serie_occurence
            curr_year = date_year
            merged_serie_info_hm = get_empty_series_kind_occurence_hm()
            merged_serie_occurence = 0

        # merge stats
        merged_serie_info_hm = {
            x: seriekind_info_hm.get(x, 0) + merged_serie_info_hm.get(x, 0)
            for x in set(seriekind_info_hm).union(merged_serie_info_hm)
        }
        merged_serie_occurence += serie_occurence

    # last year
    year_seriekind_info_hm_hm[curr_year] = merged_serie_info_hm
    year_serie_occurence_hm[curr_year] = merged_serie_occurence

    print("build_year_seriekind_info_hm_hm: end")
    return year_seriekind_info_hm_hm, year_serie_occurence_hm


def prepare_plot_values_from_mode_and_sk(serie_info_hm: list, serie_occurence_v: list,
                               serie_kind: str, mode: str) -> list:

    """Provide the nb/percent of series from the given series kind for each year."""
    if mode == "percentage":
        v = []
        for serie_info, serie_occurence in zip(serie_info_hm,
                                               serie_occurence_v):
            if serie_occurence == 0:
                assert serie_info[serie_kind] == 0
                v.append(0)
            else:
                v.append(serie_info[serie_kind] / serie_occurence * 100)

    else: # mode is "log"
        v = [serie_info[serie_kind] for serie_info in serie_info_hm]

    return v


def process(run_dir: str, infilename: str, outfilename: str, year_v: list):
    """The script's core logic."""
    print("process: start")

    # create output dir if does not exist
    output_dir = f"{run_dir}/plot/years"
    create_output_dir(output_dir)

    # find list of log
    log_v = find_log_v(run_dir,year_v,infilename)

    # compute the number of series for every series kind and date (need global
    # occurence to compute percentages)
    date_seriekind_info_hm_hm, date_serie_occurence_hm = build_date_serie_info_hm_hm(
        log_v)

    # plot raw series nb of series kind and percentage (yearly)
    for mode in ['percentage', 'log']:
        # group dates by year
        year_seriekind_info_hm_hm, year_serie_occurence_hm = build_year_seriekind_info_hm_hm(
            date_seriekind_info_hm_hm,
            date_serie_occurence_hm,
        )
        year_v = list(year_seriekind_info_hm_hm.keys())
        print("process: year_v: ", year_v)

        # prepare the plot data for each series kind
        complete_occurences_v = prepare_plot_values_from_mode_and_sk(
            list(year_seriekind_info_hm_hm.values()),
            list(year_serie_occurence_hm.values()), "Complete", mode)
        incomplete_occurences_v = prepare_plot_values_from_mode_and_sk(
            list(year_seriekind_info_hm_hm.values()),
            list(year_serie_occurence_hm.values()), "Incomplete", mode)
        correct_occurences_v = prepare_plot_values_from_mode_and_sk(
            list(year_seriekind_info_hm_hm.values()),
            list(year_serie_occurence_hm.values()), "Correct", mode)
        duplicate_occurences_v = prepare_plot_values_from_mode_and_sk(
            list(year_seriekind_info_hm_hm.values()),
            list(year_serie_occurence_hm.values()), "Duplicate", mode)
        overlap_occurences_v = prepare_plot_values_from_mode_and_sk(
            list(year_seriekind_info_hm_hm.values()),
            list(year_serie_occurence_hm.values()), "Overlap", mode)

        plt.plot(year_v,
                 correct_occurences_v,
                 label="Correct",
                 color='orange',
                 marker='x')
        plt.plot(year_v,
                 complete_occurences_v,
                 label="Complete",
                 color='red',
                 marker='+')
        plt.plot(year_v,
                 incomplete_occurences_v,
                 label="Incomplete",
                 color='blue',
                 marker='o')
        plt.plot(year_v,
                 duplicate_occurences_v,
                 label="Duplicate",
                 color='green',
                 marker='D')
        plt.plot(year_v,
                 overlap_occurences_v,
                 label="Overlap",
                 color='purple',
                 marker="^")

        ax = plt.gca()
        ax.legend(loc='upper left')

        # y-axis name and scale depending on mode
        if mode == 'log':
            ax.set_yscale('log')
            ax.set_ylabel(f"No. series ({mode})")
        elif mode == 'percentage':
            ax.set_ylabel('% of series')

        # Rotates and right-aligns the x labels so they don't crowd each other.
        for label in ax.get_xticklabels(which='major'):
            label.set(rotation=45, ha="right", rotation_mode="anchor")

        ax.grid(axis="y")

        outfile_path_png = f"{output_dir}/{outfilename}_yearly_{mode}.png"
        print("process: outfile_path_png: ", outfile_path_png)
        plt.savefig(outfile_path_png, bbox_inches='tight', dpi=200)
        plt.cla()

    print("process: end")


def main():
    """The script's entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--run-dir", type=str, required=True)
    parser.add_argument("-i", "--infilename", type=str, required=True)
    parser.add_argument("-o", "--outfilename", type=str, required=True)
    parser.add_argument("-y",
                        "--years",
                        type=int,
                        choices=range(2007, 2024),
                        nargs="*",
                        help="Years to analyze. If no value \
                        is provided, all years of the run will be analyzed.",
                        required=False)
    args = parser.parse_args()

    run_dir = args.run_dir
    infilename = args.infilename
    outfilename = args.outfilename
    year_v = args.years
    print("main: run_dir: ", run_dir)
    print("main: infilename: ", infilename)
    print("main: outfilename: ", outfilename)
    print("main: year_v: ", year_v)

    process(run_dir, infilename, outfilename, year_v)


if __name__ == "__main__":
    main()
