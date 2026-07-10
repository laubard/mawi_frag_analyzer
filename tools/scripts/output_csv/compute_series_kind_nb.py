#!/usr/bin/python3
"""This script computes the number of series, fragments and fragment data bytes across series kinds."""
import argparse
import json
import timeit
from datetime import timedelta
import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import find_log_v, create_output_dir


def process(run_dir: str, infilename: str, outfilename: str, year_v: list):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    # find file path
    log_v = find_log_v(run_dir,year_v,infilename)
    assert len(log_v) > 0

    sk_stats_hm_hm = {}
    sk_any_series_nb = 0
    sk_any_frag_nb = 0
    sk_any_total_bytes = 0

    for log in log_v:
        with open(log, encoding='utf8') as file:
            json_content = json.load(file)
        t3_stat_c = json_content['hm']

        for t3_stat_d in t3_stat_c.values():
            for flow_stat_v in t3_stat_d['t3_conversations'].values():
                for flow_stat in flow_stat_v:
                    sk_any_series_nb += 1
                    sk_any_frag_nb += flow_stat['num_chunks']
                    sk_any_total_bytes += flow_stat['num_bytes']

                    for series_kind in flow_stat['flow_stat_extension'][
                            "series_kind_v"]:
                        if series_kind not in sk_stats_hm_hm:
                            entry = {
                                "series_nb": 0,
                                "frag_nb": 0,
                                "total_bytes": 0,
                            }
                        else:
                            entry = sk_stats_hm_hm[series_kind]

                        entry["series_nb"] += 1
                        entry["frag_nb"] += flow_stat['num_chunks']
                        entry["total_bytes"] += flow_stat['num_bytes']

                        sk_stats_hm_hm.update({series_kind: entry})

    sk_stats_hm_hm.update({
        "Any": {
            "series_nb": sk_any_series_nb,
            "frag_nb": sk_any_frag_nb,
            "total_bytes": sk_any_total_bytes,
        }
    })
    df = pd.DataFrame(data=sk_stats_hm_hm)

    # create output dir if does not exist
    outfile_csv_dir = f"{run_dir}/csv/years"
    create_output_dir(outfile_csv_dir)
    df.to_csv(f'{outfile_csv_dir}/{outfilename}')

    toc = timeit.default_timer()
    elapsed_seconds = toc - tic
    elapsed_seconds_readable = str(timedelta(seconds=elapsed_seconds))

    print("process: elapsed_seconds_readable: ", elapsed_seconds_readable)

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
                        choices=range(2007, 2026),
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
