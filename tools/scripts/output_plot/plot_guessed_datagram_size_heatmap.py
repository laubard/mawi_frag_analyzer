#!/usr/bin/env python3
""""This scripts plots Fig. 9 of the paper."""
import sys
from pathlib import Path
import argparse
import json
import timeit
import datetime

import matplotlib.pyplot as plt

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_path, get_year_from_date, create_output_dir, find_log_v


def build_datagram_size_v(path: str) -> list:
    """Retrieve all original datagram sizes from log. Only keep size over 
    10 000 bytes for plot readibility."""
    with open(path, encoding='utf8') as file:
        json_content = json.load(file)

    guessed_datagram_v = []
    t3_stat_c = json_content['hm']
    # visite all IP flows
    for t3_stat_d in t3_stat_c.values():
        for flow_stat_v in t3_stat_d['t3_conversations'].values():
            for flow_stat in flow_stat_v:

                if flow_stat[
                        'flow_stat_extension'] is None:
                    print("Abnormal null flow_stat_extension")
                    sys.exit(-1)

                # retrieve the original (guessed) datagram size, if it under 10 000
                if "FromAllChunks" in flow_stat['flow_stat_extension'][
                        'datagram_size_d'] or "FromSomeChunks" in flow_stat[
                            'flow_stat_extension']['datagram_size_d']:
                    datagram_size = int(
                        list(flow_stat['flow_stat_extension']
                             ['datagram_size_d'].values())[0])
                    if datagram_size <= 10000:
                        guessed_datagram_v.append(datagram_size)

    return guessed_datagram_v


def build_heatmap_data(hm: dict, y_max: int, range_y: int) -> list:
    """"Build the heatmap matrix."""
    y_range_hm = {y: i for i, y in enumerate(list(range(0, y_max, range_y)))}

    v_v = []
    for guessed_datagram_size_v in hm.values():
        # for each trace, initialize a 0 vector of length y-axis
        v = [0] * len(y_range_hm)
        for guessed_datagram_size in guessed_datagram_size_v:
            # increment the nb of datagram size at the appropriate coordinates
            v[guessed_datagram_size // range_y] += 1
        v_v.append(v)

    return v_v


def process(
    run_dir: str,
    infilename: str,
    year_v: list,
    outfilename: str,
    range_y: int,
):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    # find log paths
    log_v = find_log_v(run_dir,year_v,infilename)

    # associate date with a list of original guessed datagram size
    hm = {
        build_date_from_path(log): build_datagram_size_v(log)
        for log in log_v
    }
    hm_sorted = dict(sorted(hm.items()))

    # Shape hm to fit heatmap
    y_max = 10500
    v_v = build_heatmap_data(hm_sorted, y_max, range_y)
    v_v_interverting_axes = [[v[i] for v in v_v] for i in range(len(v_v[0]))]

    # Plot
    fig, ax = plt.subplots()
    fig.set_dpi(1500)

    im = ax.imshow(v_v_interverting_axes,
                   cmap="gist_heat_r",
                   norm="log",
                   origin='lower',
                   aspect="auto",
                   interpolation='none')

    date_year_v = [get_year_from_date(date) for date in hm_sorted.keys()]
    print('date_year_v: ', date_year_v)

    date_year_loc = []
    year_v = []
    curr_year = 0
    for i, date_year in enumerate(date_year_v):
        if curr_year == 0 or curr_year != date_year:
            date_year_loc.append(i)
            curr_year = date_year
            year_v.append(date_year)
    print('date_year_loc: ', date_year_loc)
    print('year_v: ', year_v)

    ylabel_i_v = [0, 1480, 2048, 2960, 4096, 4440, 7935, 5920, 7400,
               10000]
    ylabel_str_v = [ str(i) for i in ylabel_i_v ]
    yticks = [ylabel + 1 for ylabel in ylabel_i_v]

    ax.set_yticks(yticks, ylabel_str_v)
    ax.set_xticks(date_year_loc,
                  labels=[f"{year}-01" for year in year_v],
                  rotation=45,
                  ha="right",
                  rotation_mode="anchor")
    ax.set_ylabel('Original (guessed) datagram size')
    ax.set_ylim(0, 10001)
    fig.colorbar(im, ax=ax, label='No. series')

    # create output dir if does not exist
    outfile_plot_dir = f"{run_dir}/plot/years"
    create_output_dir(outfile_plot_dir)
    outfile_path_png = f"{outfile_plot_dir}/{outfilename}.png"
    print("process: outfile_path_png: ", outfile_path_png)
    plt.savefig(outfile_path_png, bbox_inches='tight')
    outfile_path_pdf = f"{outfile_plot_dir}/{outfilename}.pdf"
    print("process: outfile_path_pdf: ", outfile_path_pdf)
    plt.savefig(outfile_path_pdf, bbox_inches='tight', dpi=250)

    toc = timeit.default_timer()
    elapsed_seconds = toc - tic
    elapsed_seconds_readable = str(datetime.timedelta(seconds=elapsed_seconds))

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
    parser.add_argument("-r",
                        "--range-y",
                        type=int,
                        required=True,
                        choices=range(0, 10000),
                        help="Range to merge y values")
    args = parser.parse_args()

    run_dir = args.run_dir
    infilename = args.infilename
    year_v = args.years
    outfilename = args.outfilename
    range_y = args.range_y
    print("run_dir: ", run_dir)
    print("infilename: ", infilename)
    print("year_v: ", year_v)
    print("outfilename: ", outfilename)
    print("range_y: ", range_y)

    process(run_dir, infilename, year_v, outfilename, range_y)

    print("main: end")


if __name__ == "__main__":
    main(sys.argv[1:])
