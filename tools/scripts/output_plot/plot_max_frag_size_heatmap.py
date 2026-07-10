#!/usr/bin/env python3
""""This scripts plots Fig. 8 of the paper and provides the Table I numbers."""
import sys
from pathlib import Path
import os
import argparse
import json
import timeit
import datetime
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_path, find_log_v, get_year_from_date, create_output_dir


def build_max_frag_size_v(path: str) -> list:
    """Build a list of max size of left fragments for the given log."""
    with open(path, encoding='utf8') as file:
        json_content = json.load(file)

    t3_stat_c = json_content['hm']
    max_frag_size_v = [
        max(list(
            frag_chunk_d["num_bytes"]
            if frag_chunk_d["more_fragments"] is True else -1
            for frag_chunk_d in flow_stat["frag_chunk_c"]["hm"].values()
        )) for t3_stat_d in t3_stat_c.values()
        for flow_stat_v in t3_stat_d['t3_conversations'].values()
        for flow_stat in flow_stat_v
    ]
    # keep only data for series with a fragment with the MF bit set
    max_frag_size_v_no_0 = [
        max_frag_size for max_frag_size in max_frag_size_v
        if max_frag_size != -1
    ]

    return max_frag_size_v_no_0


def build_heatmap_data(hm: dict, y_max: int, range_y: int) -> list:
    """"Build the heatmap matrix."""
    y_range_hm = {y: i for i, y in enumerate(list(range(0, y_max, range_y)))}

    v_v = []
    for max_frag_size_v in hm.values():
        # for each trace, initialize a 0 vector of length y-axis
        v = [0] * len(y_range_hm)
        for max_frag_size in max_frag_size_v:
            # increment the nb of left frag size at the appropriate coordinates
            v[max_frag_size // range_y] += 1
        v_v.append(v)

    return v_v

def build_top_ten_max_frag_size_v(date_max_frag_size_v_hm: dict) -> list:
    """Compute overall top 10 max frag sizes."""
    max_frag_size_v = [
        max_frag_size
        for _, max_frag_size_v in date_max_frag_size_v_hm.items()
        for max_frag_size in max_frag_size_v
    ]
    print("build_top_ten_max_frag_size_v: len(max_frag_size_v): ",
          len(max_frag_size_v))

    return Counter(max_frag_size_v).most_common(10)

def build_year_max_frag_size_v_hm(date_max_frag_size_v_hm: dict) -> dict:
    """For each year, group the list of max frag size."""
    year_max_frag_size_v_hm = {}

    for date, max_frag_size_v in date_max_frag_size_v_hm.items():
        year = get_year_from_date(date)
        if year not in year_max_frag_size_v_hm:
            year_v = max_frag_size_v.copy()
        else:
            year_v = year_max_frag_size_v_hm[year]
            year_v.extend(max_frag_size_v.copy())
        year_max_frag_size_v_hm.update({year: year_v})

    return year_max_frag_size_v_hm


def build_top_ten_sizes_and_year_weights_normalized(
        year_max_frag_size_v_hm: dict, year_frag_nb_hm: dict,
        total_frag_nb: int) -> tuple:
    """Compute the normalized overall top 10 max frag sizes and the 
    corresponding weight of each year."""
    year_weight_hm = {
        year: frag_nb / total_frag_nb
        for year, frag_nb in year_frag_nb_hm.items()
    }
    year_counter_hm = {
        year: Counter(max_frag_size_v)
        for year, max_frag_size_v in year_max_frag_size_v_hm.items()
    }
    year_counter_weighted_hm = {
        year: [(size, round(count / weight))
               for (size, count) in counter_hm.items()]
        for ((year, counter_hm),
             (_,
              weight)) in zip(year_counter_hm.items(), year_weight_hm.items())
    }
    max_frag_size_v_weighted = [
        size for counter_v in year_counter_weighted_hm.values()
        for (size, count) in counter_v for _ in range(count)
    ]

    total_frag_nb_with_weighted = sum(list(
        round(count / weight) for (_, counter_hm), (
            _, weight) in zip(year_counter_hm.items(), year_weight_hm.items())
        for (_, count) in counter_hm.items()
    ))

    return (Counter(max_frag_size_v_weighted).most_common(10),
            total_frag_nb_with_weighted)


def build_year_fragnb_hm(date_max_frag_size_v_hm: dict) -> dict:
    """Build a dictionary with years as keys and the total series nb to consider."""
    year_fragnb_hm = {}

    for date, max_frag_size_v in date_max_frag_size_v_hm.items():
        year = get_year_from_date(date)
        year_nb = len(
            max_frag_size_v
        ) if year not in year_fragnb_hm else year_fragnb_hm[year] + len(
            max_frag_size_v)
        year_fragnb_hm.update({year: year_nb})

    return year_fragnb_hm


def prepare_csv_data(year_top_10_hm: dict, year_frag_nb_hm: dict,
                     total_frag_nb: int, top_ten_max_frag_size_v: list,
                     weighted_top_ten_max_frag_size_v: list,
                     total_frag_nb_with_weighted: int) -> dict:
    """Prepare CSV data to store in dictionary"""
    csv_hm = {}
    for (year, top10_hm), (_, frag_nb) in zip(year_top_10_hm.items(),
                                              year_frag_nb_hm.items()):
        value = {}
        for i, (fragzise, occurence) in enumerate(top10_hm):
            top_id = i + 1
            value.update({f"top_{top_id}_fragsize_value": fragzise})
            value.update({f"top_{top_id}_fragsize_occurence": occurence})
            value.update(
                {f"top_{top_id}_fragsize_perc": (occurence / frag_nb) * 100})
        csv_hm.update({year: value})

    # mean
    value = {}
    for i, (fragzise, occurence) in enumerate(top_ten_max_frag_size_v):
        top_id = i + 1
        value.update({f"top_{top_id}_fragsize_value": fragzise})
        value.update({f"top_{top_id}_fragsize_occurence": occurence})
        value.update(
            {f"top_{top_id}_fragsize_perc": (occurence / total_frag_nb) * 100})
    csv_hm.update({"all_abs": value})

    # weighted mean
    value = {}
    for i, (fragzise,
            occurence) in enumerate(weighted_top_ten_max_frag_size_v):
        top_id = i + 1
        value.update({f"top_{top_id}_fragsize_value": fragzise})
        value.update({f"top_{top_id}_fragsize_occurence": occurence})
        value.update({
            f"top_{top_id}_fragsize_perc":
            (occurence / total_frag_nb_with_weighted) * 100
        })
    csv_hm.update({"all_weighted": value})

    return csv_hm


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

    # associate date with a list of left frag sizes
    hm = {
        build_date_from_path(log): build_max_frag_size_v(log)
        for log in log_v
    }
    hm_sorted = dict(sorted(hm.items()))

    # Shape hm to fit heatmap
    y_max = 1550
    v_v = build_heatmap_data(hm_sorted, y_max, range_y)
    v_v_interverting_axes = [[v[i] for v in v_v] for i in range(len(v_v[0]))]

    # Plot
    fig, ax = plt.subplots()

    im = ax.imshow(v_v_interverting_axes,
                   cmap="gist_heat_r",
                   norm="log",
                   origin='lower',
                   aspect="auto",
                   interpolation='none')

    date_year_v = [date.split('-')[0] for date in hm_sorted.keys()]
    print('date_year_v: ', date_year_v)

    date_year_loc = []
    year_v = []
    curr_year = 0
    for i, date_year in enumerate(date_year_v):
        if curr_year == 0 or curr_year != date_year:
            date_year_loc.append(i)
            curr_year = date_year
            year_v.append(date_year)
    print('year_v: ', year_v)

    ylabel_i_v = [104, 552, 744, 1012, 1112, 1256, 1376, 1480]
    ylabel_str_v = [ str(i) for i in ylabel_i_v ]
    yticks = [ylabel + 1 for ylabel in ylabel_i_v]
    ax.set_yticks(yticks,
                  ylabel_str_v)
    ax.set_xticks(date_year_loc,
                  labels=[f"{year}-01" for year in year_v],
                  rotation=45,
                  ha="right",
                  rotation_mode="anchor")
    ax.set_ylabel('Fragment size')
    fig.colorbar(im, ax=ax, label='No. series')

    # create output dir if does not exist
    outfile_plot_dir = f"{run_dir}/plot/years"
    print("process: outfile_plot_dir: ", outfile_plot_dir)
    os.makedirs(outfile_plot_dir, exist_ok=True)
    outfile_path_png = f"{outfile_plot_dir}/{outfilename}.png"
    print("process: outfile_path_png: ", outfile_path_png)
    plt.savefig(outfile_path_png, bbox_inches='tight')
    outfile_path_pdf = f"{outfile_plot_dir}/{outfilename}.pdf"
    print("process: outfile_path_pdf: ", outfile_path_pdf)
    plt.savefig(outfile_path_pdf, bbox_inches='tight', dpi=250)

    # Build CSV data
    year_fragnb_hm = build_year_fragnb_hm(hm_sorted)
    print("process: year_fragnb_hm: ", year_fragnb_hm)
    total_frag_nb = sum(list(frag_nb for frag_nb in year_fragnb_hm.values()))
    print("process: total_frag_nb: ", total_frag_nb)

    year_max_frag_size_v_hm = build_year_max_frag_size_v_hm(hm_sorted)
    year_top_ten_max_frag_size_v_hm = {
        year: Counter(max_frag_size_v).most_common(10)
        for year, max_frag_size_v in year_max_frag_size_v_hm.items()
    }
    print("process: year_top_ten_max_frag_size_v_hm: ",
          year_top_ten_max_frag_size_v_hm)

    top_ten_max_frag_size_v = build_top_ten_max_frag_size_v(hm_sorted)
    print("process: top_ten_max_frag_size_v: ", top_ten_max_frag_size_v)

    (
        weighted_top_ten_max_frag_size_v, total_frag_nb_with_weighted
    ) = build_top_ten_sizes_and_year_weights_normalized(
        year_max_frag_size_v_hm, year_fragnb_hm, total_frag_nb)

    # format data to store
    csv_hm = prepare_csv_data(year_top_ten_max_frag_size_v_hm, year_fragnb_hm,
                              total_frag_nb, top_ten_max_frag_size_v,
                              weighted_top_ten_max_frag_size_v,
                              total_frag_nb_with_weighted)
    csv_df = pd.DataFrame(
        data=list(csv_hm.values()),
        index=list(csv_hm.keys()),
    )

    # create output dir if does not exist
    outfile_csv_dir = f"{run_dir}/csv/years"
    create_output_dir(outfile_csv_dir)
    csv_df.to_csv(f'{outfile_csv_dir}/{outfilename}.csv')

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
