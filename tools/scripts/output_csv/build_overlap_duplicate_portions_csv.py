#!/usr/bin/python3
"""This script analyzes overlap and/or duplicate series and provides many 
information regarding their structure (e.g., number of chunks, IATs between 
overlapping chunks, have the leftmost fragments the same size)."""
import argparse
import json
import os
import sys
from pathlib import Path
import glob
import timeit
from datetime import datetime, timedelta
import statistics

import portion
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import build_date_from_path_basename_left, create_output_dir


def compute_portion_and_iat_of_overlapping_frag(
        begin_end_v: list, chunk_id_v: list, frag_chunk_d_v: list, log: str,
        three_tuple: dict, ip_id: str) -> tuple[list, list]:
    """This function identifies overlaps between fragments. When there is an 
    overlap, the overlapping byte offsets and the IAT between the fragments 
    are tracked."""
    iat_v = []
    overlapping_portion_v = []
    while len(chunk_id_v) > 1:
        # look for different overlap portions
        curr_chunk_id = chunk_id_v[0]
        chunk_id_to_compare = chunk_id_v[1]
        while True:
            # look for same overlap portions
            (begin_1, end_1), (
                begin_2, end_2
            ) = begin_end_v[curr_chunk_id], begin_end_v[chunk_id_to_compare]
            p_portion = compute_overlap_portion(begin_1, end_1, begin_2, end_2)
            if not p_portion.empty:
                overlapping_portion_v.append(p_portion)
                ts1 = datetime.fromtimestamp(
                    float(
                        f"{frag_chunk_d_v[curr_chunk_id]['ts']['secs']}.{frag_chunk_d_v[curr_chunk_id]['ts']['micros']:06d}"
                    ))
                ts2 = datetime.fromtimestamp(
                    float(
                        f"{frag_chunk_d_v[chunk_id_to_compare]['ts']['secs']}.{frag_chunk_d_v[chunk_id_to_compare]['ts']['micros']:06d}"
                    ))
                if ts2 < ts1:
                    print(
                        f"chunk disordered in {log} for three tuple {three_tuple} and id {ip_id}"
                    )
                    sys.exit(-1)
                delta_t_sec = (ts2 - ts1).total_seconds() if ts2 > ts1 else (
                    ts1 - ts2).total_seconds()
                iat_v.append(delta_t_sec)
                chunk_id_v.remove(curr_chunk_id)
                curr_chunk_id = chunk_id_to_compare

            if chunk_id_v.index(chunk_id_to_compare) + 1 < len(chunk_id_v):
                chunk_id_to_compare = chunk_id_v[
                    chunk_id_v.index(chunk_id_to_compare) + 1]
            else:
                chunk_id_v.remove(curr_chunk_id)
                break

    #if not overlapping_portion_v:
    if overlapping_portion_v == []:
        print("build_csv_data: overlapping_portion_v == [ ] for log: ", log)
        print("build_csv_data: begin_end_v: ", begin_end_v)
        print("build_csv_data: three_tuple: ")

    return overlapping_portion_v, iat_v


def compute_overlap_portion(
    begin_1: int,
    end_1: int,
    begin_2: int,
    end_2: int,
) -> portion.Interval:
    """Computes a possible overlapping portion

    Parameters
    ----------
    begin_1
        beginning offset of chunk 1
    end_1
        ending offset of chunk 1
    begin_2
        beginning offset of chunk 2
    end_2
        ending offset of chunk 2

    Returns
    -------
    portion
        portion if there is an intersection between chunk 1 and 2, or an empty
         portion if there is not 
    """
    return portion.open(begin_1, end_1) & portion.open(begin_2, end_2)


def compute_multiple_left_frag_sizes_t3(
        frag_chunk_c_v: list) -> int:
    """Compute the number of fragment sizes for the fragments with the MF bit 
    set, for all the three tuple's flows."""
    # keep only the sizes of leftmost fragments
    mf_frag_size_v = [
        frag_chunk_d['num_bytes'] for frag_chunk_c in frag_chunk_c_v
        for frag_chunk_d in frag_chunk_c['hm'].values()
        if frag_chunk_d['more_fragments']
    ]
    mf_frag_size_v_no_duplicates = list(set(mf_frag_size_v))

    return len(mf_frag_size_v_no_duplicates)


def label_t3_ipid(ipid_counter: dict) -> str:
    """Characterize the IPID algo behavior of the three tuple."""
    #print("label_t3_ipid: start")
    ipid_v_no_duplicates_sorted = sorted(list(set(ipid_counter)))
    if len(ipid_v_no_duplicates_sorted) == 1:
        return 'unique'  # unique series or constant IPID

    #THRESHOLD_IPID_CLOSENESS = 0.90
    #THRESHOLD_IPID_VISITED_RANGE = 0.5
    #ipid_closeness_v = [
    #    str(int(ipid) + 1) in ipid_v_no_duplicates_sorted
    #    for index, ipid in enumerate(ipid_v_no_duplicates_sorted)
    #    if index != len(ipid_v_no_duplicates_sorted) - 1
    #]
    #ipid_closeness = sum(ipid_closeness_v)
    #if ipid_closeness / len(
    #        ipid_v_no_duplicates_sorted) >= THRESHOLD_IPID_CLOSENESS and len(
    #            ipid_v_no_duplicates_sorted
    #        ) / 65535 < THRESHOLD_IPID_VISITED_RANGE:
    #    return 'counter'

    return 'unlabeled'


def compute_multiple_left_frag_sizes_series(
        frag_chunk_d_v: list) -> int:
    """Compute the number of fragment sizes for the fragments with the MF bit
    set, for a given series or IP flow."""
    # keep only the sizes of leftmost fragments
    mf_frag_size_v = [
        frag_chunk_d['num_bytes'] for frag_chunk_d in frag_chunk_d_v
        if frag_chunk_d['more_fragments']
    ]
    mf_frag_size_v_no_duplicates = list(set(mf_frag_size_v))

    return len(mf_frag_size_v_no_duplicates)


def build_csv_data(log_v: list, outfile_path: str, serie_kind: str,
                   start_ts_dir: str):
    """Retrieve and build the CSV data."""
    print("build_csv_data: start")

    for log in log_v:
        date = build_date_from_path_basename_left(log)

        # retrieve trace starting timestamp
        start_ts_filepath = f"{start_ts_dir}/{date}.txt"
        with open(start_ts_filepath, encoding='utf8') as file:
            trace_begin_ts_line = file.readline()
        trace_begin_ts = datetime.fromtimestamp(
            float(
                f"{trace_begin_ts_line.split('.')[0]}.{trace_begin_ts_line.split('.')[1]}"
            ))
        trace_end_ts = trace_begin_ts + timedelta(seconds=900)

        with open(log, encoding='utf8') as file:
            json_content = json.load(file)

        # iterate across IP flows
        t3_stat_c = json_content['hm']
        for t3_stat_d in t3_stat_c.values():
            src_ip = t3_stat_d['three_tuple']['src']
            dst_ip = t3_stat_d['three_tuple']['dst']
            l4_proto = t3_stat_d['three_tuple']['l4_proto']

            # build IPID label
            ipid_counter = {
                ipid: len(flow_stat_v)
                for ipid, flow_stat_v in t3_stat_d['t3_conversations'].items()
            }
            t3_ipid_label = label_t3_ipid(ipid_counter)

            # compute the number of different sizes of the fragments with MF 
            # bit set for a given three tuple
            frag_chunk_c_v = [
                flow_stat['frag_chunk_c']
                for flow_stat_v in t3_stat_d['t3_conversations'].values()
                for flow_stat in flow_stat_v
            ]
            t3_nb_inconsistent_first_fragment_sizes = compute_multiple_left_frag_sizes_t3(
                frag_chunk_c_v)

            # iterate across t3 flows
            for ip_id, flow_stat_v in t3_stat_d['t3_conversations'].items():
                # tell if four tuple has its first frag located in the first X seconds
                fourtuple_ts_v = [
                    datetime.fromtimestamp(
                        float(
                            f"{frag_chunk_d['ts']['secs']}.{frag_chunk_d['ts']['micros']}"
                        )) for flow_stat in flow_stat_v for frag_chunk_d in
                    flow_stat['frag_chunk_c']['hm'].values()
                ]
                fourtuple_ts_v.sort()
                fourtuple_begin_ts = min(fourtuple_ts_v)
                max_chunk_iat = 0
                max_chunk_iat = max(
                    list(fourtuple_ts_v[i + 1] - x
                         for i, x in enumerate(fourtuple_ts_v)
                         if i < len(fourtuple_ts_v) -
                         1)) if len(fourtuple_ts_v) > 1 else timedelta(
                             seconds=0)
                fourtuple_end_ts = max(fourtuple_ts_v)

                # X = 1 sec
                is_four_tuple_at_beginning_1sec = fourtuple_begin_ts - trace_begin_ts < timedelta(
                    seconds=1)
                is_four_tuple_at_end_1sec = trace_end_ts - fourtuple_end_ts < timedelta(
                    seconds=1)
                is_continuous_1sec = max_chunk_iat < timedelta(
                    seconds=1
                ) and is_four_tuple_at_beginning_1sec and is_four_tuple_at_end_1sec

                # X = 5 sec
                is_four_tuple_at_beginning_5sec = fourtuple_begin_ts - trace_begin_ts < timedelta(
                    seconds=5)
                is_four_tuple_at_end_5sec = trace_end_ts - fourtuple_end_ts < timedelta(
                    seconds=5)
                is_continuous_5sec = max_chunk_iat < timedelta(
                    seconds=5
                ) and is_four_tuple_at_beginning_5sec and is_four_tuple_at_end_5sec

                # X = 30 sec
                is_four_tuple_at_beginning_30sec = fourtuple_begin_ts - trace_begin_ts < timedelta(
                    seconds=30)
                is_four_tuple_at_end_30sec = trace_end_ts - fourtuple_end_ts < timedelta(
                    seconds=30)
                is_continuous_30sec = max_chunk_iat < timedelta(
                    seconds=30
                ) and is_four_tuple_at_beginning_30sec and is_four_tuple_at_end_30sec

                # X = 120 sec
                is_four_tuple_at_beginning_120sec = fourtuple_begin_ts - trace_begin_ts < timedelta(
                    seconds=120)
                is_four_tuple_at_end_120sec = trace_end_ts - fourtuple_end_ts < timedelta(
                    seconds=120)
                is_continuous_120sec = max_chunk_iat < timedelta(
                    seconds=120
                ) and is_four_tuple_at_beginning_120sec and is_four_tuple_at_end_120sec

                # iterate across four tuple flows
                for flow_stat in flow_stat_v:
                    assert flow_stat['flow_stat_extension'] is not None
                    flow_stat_extension = flow_stat['flow_stat_extension']
                    print(flow_stat_extension)

                    # check if the series verifies conditions
                    if serie_kind == "OverlapOrDuplicate":
                        if (
                                "Overlap"
                                not in flow_stat_extension["series_kind_v"]
                        ) and ("Duplicate"
                               not in flow_stat_extension["series_kind_v"] or
                               flow_stat_extension["l4_checksum_consistency"]
                               is not False):
                            continue
                    elif serie_kind not in flow_stat_extension[
                            "series_kind_v"] or (
                                serie_kind == "Duplicate" and
                                flow_stat_extension["l4_checksum_consistency"]
                                is not False):
                        continue

                    # retrieve info from flow
                    src_port = str(
                        flow_stat['l4_src_port']
                    ) if flow_stat['l4_src_port'] is not None else flow_stat[
                        'l4_src_port']
                    dst_port = str(
                        flow_stat['l4_dst_port']
                    ) if flow_stat['l4_dst_port'] is not None else flow_stat[
                        'l4_dst_port']
                    num_bytes = flow_stat['num_bytes']
                    num_chunks = flow_stat['num_chunks']

                    is_incomplete = 'Incomplete' in flow_stat_extension[
                        'series_kind_v']
                    allen_relation_sequence = flow_stat_extension[
                        'allen_relation_sequence']
                    datagram_size = flow_stat_extension['datagram_size_d']

                    is_invalid_ip_flags_combination = flow_stat_extension[
                        "is_weird_ip_flags"]
                    is_low_ttl = flow_stat_extension["is_weird_small_ttl"]

                    ip_flags_combination_v = [
                        frag_chunk_d['flags'] for frag_chunk_d in
                        flow_stat['frag_chunk_c']['hm'].values()
                    ]
                    ip_flags_combination_v_no_duplicates = list(
                        set(ip_flags_combination_v))

                    ttl_v = [
                        frag_chunk_d['ttl'] for frag_chunk_d in
                        flow_stat['frag_chunk_c']['hm'].values()
                    ]
                    ttl_v_no_duplicates = list(set(ttl_v))

                    # compute the number of different sizes of the fragments 
                    # with MF bit set for a given series
                    series_nb_inconsistent_first_fragment_sizes = compute_multiple_left_frag_sizes_series(
                        flow_stat['frag_chunk_c']['hm'].values())

                    # verify if a left frag has a small size
                    is_left_frag_under_556_bytes = bool([
                        True for frag_chunk_d in flow_stat['frag_chunk_c']
                        ['hm'].values() if frag_chunk_d['more_fragments'] < 556
                    ])
                    is_left_frag_under_1000_bytes = bool([
                        True for frag_chunk_d in flow_stat['frag_chunk_c']
                        ['hm'].values()
                        if frag_chunk_d['more_fragments'] < 1000
                    ])
                    is_left_frag_under_1200_bytes = bool([
                        True for frag_chunk_d in flow_stat['frag_chunk_c']
                        ['hm'].values()
                        if frag_chunk_d['more_fragments'] < 1200
                    ])

                    # compute the portions and IATs of overlapping fragments
                    begin_end_v = [
                        (frag_chunk_d['begin'],
                         frag_chunk_d['begin'] + frag_chunk_d['num_bytes'])
                        for frag_chunk_d in flow_stat['frag_chunk_c']
                        ['hm'].values()
                    ]
                    chunk_id_v = [
                        int(chunk_id)
                        for chunk_id in flow_stat['frag_chunk_c']['hm'].keys()
                    ]
                    frag_chunk_d_v = list(
                        flow_stat['frag_chunk_c']['hm'].values())

                    overlapping_portion_v, iat_v = compute_portion_and_iat_of_overlapping_frag(
                        begin_end_v, chunk_id_v, frag_chunk_d_v, log,
                        t3_stat_d['three_tuple'], ip_id)

                    overlapping_portion_no_duplicate_v = sorted(
                        list(set(overlapping_portion_v)))
                    iat_median = statistics.median(iat_v)

                    # prepare info for storing
                    duplicate_t = [[
                        date, src_ip, dst_ip, l4_proto, ip_id, src_port,
                        dst_port, num_bytes, num_chunks, is_incomplete,
                        datagram_size, is_invalid_ip_flags_combination,
                        ip_flags_combination_v_no_duplicates, is_low_ttl,
                        ttl_v_no_duplicates, t3_ipid_label, iat_median, iat_v,
                        t3_nb_inconsistent_first_fragment_sizes,
                        series_nb_inconsistent_first_fragment_sizes,
                        is_left_frag_under_556_bytes,
                        is_left_frag_under_1000_bytes,
                        is_left_frag_under_1200_bytes,
                        is_four_tuple_at_beginning_1sec,
                        is_four_tuple_at_end_1sec, is_continuous_1sec,
                        is_four_tuple_at_beginning_5sec,
                        is_four_tuple_at_end_5sec, is_continuous_5sec,
                        is_four_tuple_at_beginning_30sec,
                        is_four_tuple_at_end_30sec, is_continuous_30sec,
                        is_four_tuple_at_beginning_120sec,
                        is_four_tuple_at_end_120sec, is_continuous_120sec,
                        allen_relation_sequence,
                        overlapping_portion_no_duplicate_v,
                        overlapping_portion_v
                    ]]

                    duplicate_df = pd.DataFrame(
                        data=duplicate_t,
                        columns=[
                            'date', 'src_ip', 'dst_ip', 'l4_proto', 'ip_id',
                            'src_port', 'dst_port', 'num_bytes', 'num_chunks',
                            'is_incomplete', 'datagram_size',
                            'invalid_ip_flags_combination', 'present_ip_flags',
                            'low_ttl', 'present_ttl', 't3_ipid_label',
                            'iat_median', 'iat_v',
                            't3_nb_inconsistent_first_fragment_sizes',
                            'series_nb_inconsistent_first_fragment_sizes',
                            'is_left_frag_under_556_bytes',
                            'is_left_frag_under_1000_bytes',
                            'is_left_frag_under_1200_bytes',
                            'is_four_tuple_at_beginning_1sec',
                            'is_four_tuple_at_end_1sec', 'is_continuous_1sec',
                            'is_four_tuple_at_beginning_5sec',
                            'is_four_tuple_at_end_5sec', 'is_continuous_5sec',
                            'is_four_tuple_at_beginning_30sec',
                            'is_four_tuple_at_end_30sec',
                            'is_continuous_30sec',
                            'is_four_tuple_at_beginning_120sec',
                            'is_four_tuple_at_end_120sec',
                            'is_continuous_120sec', 'allen_relation_sequence',
                            'overlapping_portion_no_duplicate_v',
                            'overlapping_portion_v'
                        ])

                    # save to csv file
                    duplicate_df.to_csv(
                        outfile_path,
                        mode='a',
                        index=False,
                        header=not os.path.exists(outfile_path))


def process(run_dir: str, sym_dir: str, outfilename_no_extension: str,
            year_v: list, serie_kind: str, start_ts_dir: str):
    """The script's core logic."""
    print("process: start")

    tic = timeit.default_timer()

    if year_v is None or year_v == []:
        log_v = glob.glob(f"{sym_dir}/*.log")
    else:
        log_v_v = [glob.glob(f"{sym_dir}/{year}*.log") for year in year_v]
        log_v = [log for log_v in log_v_v for log in log_v]
    log_v.sort()

    outfile_csv_dir = f"{run_dir}/csv/years"
    create_output_dir(outfile_csv_dir)
    outfile_path = f"{outfile_csv_dir}/{outfilename_no_extension}.csv"
    build_csv_data(log_v, outfile_path, serie_kind, start_ts_dir)

    toc = timeit.default_timer()
    elapsed_seconds = toc - tic
    elapsed_seconds_readable = str(timedelta(seconds=elapsed_seconds))

    print("process: elapsed_seconds_readable: ", elapsed_seconds_readable)

    print("process: end")


def main():
    """The script's entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--run-dir", type=str, required=True)
    parser.add_argument("-i", "--sym-dir", type=str, required=True)
    parser.add_argument("-o", "--outfilename", type=str, required=True)
    parser.add_argument("-y",
                        "--years",
                        type=int,
                        choices=range(2007, 2026),
                        nargs="*",
                        help="Years to analyze. If no value \
                        is provided, all years of the run will be analyzed.",
                        required=False)
    parser.add_argument("--serie-kind",
                        type=str,
                        choices=["Overlap", "Duplicate", "OverlapOrDuplicate"],
                        required=True)
    parser.add_argument("--start-timestamp-dir", type=str, required=True)
    args = parser.parse_args()

    run_dir = args.run_dir
    sym_dir = args.sym_dir
    outfilename_no_extension = args.outfilename
    year_v = args.years
    serie_kind = args.serie_kind
    start_ts_dir = args.start_timestamp_dir
    print("main: run_dir: ", run_dir)
    print("main: sym_dir: ", sym_dir)
    print("main: outfilename_no_extension: ", outfilename_no_extension)
    print("main: year_v: ", year_v)
    print("main: serie_kind: ", serie_kind)
    print("main: start_ts_dir: ", start_ts_dir)

    process(run_dir, sym_dir, outfilename_no_extension, year_v, serie_kind,
            start_ts_dir)


if __name__ == "__main__":
    main()
