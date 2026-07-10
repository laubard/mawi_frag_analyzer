#!/bin/bash

set -eu
set -o pipefail

echo "generate_csv_ipv4_frag_stats_filters: start"

run_dir_capinfos=$1
outfilename_prefix=$2

echo "generate_csv_ipv4_frag_stats_filters: run_dir_capinfos: ${run_dir_capinfos}"
echo "generate_csv_ipv4_frag_stats_filters: outfilename_prefix: ${outfilename_prefix}"

export run_dir_capinfos
export outfilename_prefix

function generate_csv_ipv4_frag_stats_filter() {
    set -e

    echo ""
    echo ""
    echo ""
    echo "generate_csv_ipv4_frag_stats_filter: start"
    filter_name=$1
    echo "generate_csv_ipv4_frag_stats_filter: filter_name: ${filter_name}"
    outfilename="${outfilename_prefix}_${filter_name}.csv"
    echo "generate_csv_ipv4_frag_stats_filter: outfilename: ${outfilename}"

    python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/generate_csv_ipv4_frag_stats_filter.py" \
    --run-dir "$run_dir_capinfos" \
    --filter "$filter_name" \
    --outfilename "$outfilename" 

    echo "generate_csv_ipv4_frag_stats_filter: end"
}

export -f generate_csv_ipv4_frag_stats_filter


generate_csv_ipv4_frag_stats_filter "no-filter"
generate_csv_ipv4_frag_stats_filter "frags_no-filter"
generate_csv_ipv4_frag_stats_filter "proto-17"
generate_csv_ipv4_frag_stats_filter "frags_proto-17"
generate_csv_ipv4_frag_stats_filter "proto-6"
generate_csv_ipv4_frag_stats_filter "frags_proto-6"
generate_csv_ipv4_frag_stats_filter "proto-50"
generate_csv_ipv4_frag_stats_filter "frags_proto-50"
generate_csv_ipv4_frag_stats_filter "proto-47"
generate_csv_ipv4_frag_stats_filter "frags_proto-47"
generate_csv_ipv4_frag_stats_filter "proto-1"
generate_csv_ipv4_frag_stats_filter "frags_proto-1"
generate_csv_ipv4_frag_stats_filter "proto-17-port-53"
generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-53"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-161"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-161"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-389"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-389"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-443"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-443"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-1194"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-1194"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-4500"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-4500"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-5060"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-5060"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-3074"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-3074"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-21"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-21"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-500"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-500"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-2049"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-2049"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-1812"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-1812"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-1080"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-1080"
#generate_csv_ipv4_frag_stats_filter "proto-17-port-1863"
#generate_csv_ipv4_frag_stats_filter "frags_proto-17-port-1863"

echo "generate_csv_ipv4_frag_stats_filters: end"
