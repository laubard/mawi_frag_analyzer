#!/bin/bash

set -eu
set -o pipefail

echo "build_trace_ts_start_end: start"

echo "build_trace_ts_start_end: current PID: $$"

symlink_dir_path=$1
output_dir_path=$2

echo "build_trace_ts_start_end: symlink_dir_path: ${symlink_dir_path}"
echo "build_trace_ts_start_end: output_dir_path: ${output_dir_path}"

printf -v date '%(%Y%m%d_%H%M%S)T' -1

mkdir -p "$output_dir_path"
echo "build_trace_ts_start_end: output_dir_path created"

export output_dir_path

function get_ts_start_end() {
    set -e

    echo ""
    echo ""
    echo ""
    echo "get_ts_start_end: start"
    symlink_file_path=$1
    echo "build_trace_ts_start_end_from: symlink_file_path: ${symlink_file_path}"
    compressed_file_path=$(readlink -f "$symlink_file_path")
    echo "build_trace_ts_start_end_from: compressed_file_path: ${compressed_file_path}"
    compressed_file_name=$(basename -- "$symlink_file_path")
    echo "build_trace_ts_start_end_from: compressed_file_name: ${compressed_file_name}"

    year_month_day_tmp="${compressed_file_name%.*}"
    year_month_day="${year_month_day_tmp%.*}" # do it twice because from 2016, file extension is .pcap.xz
    echo "build_trace_ts_start_end_from: year_month_day: ${year_month_day}"

    output_filepath="${output_dir_path}/${year_month_day}.txt"
    echo "build_trace_ts_start_end_from: output_filepath: ${output_filepath}"

    # choose decompression tool
    if [[ $compressed_file_path == *.gz ]]; then
        unzip_tool="zcat"
    elif [[ $compressed_file_path == *.xz ]]; then
        unzip_tool="xzcat"
    elif [[ $compressed_file_path == *.lz4 ]]; then
        unzip_tool="lz4cat"
    elif [[ $compressed_file_path == *.zstd ]]; then
        unzip_tool="zstdcat"
    else
        echo "decompress_and_filter_and_get_capinfos: unsupported file extension"
        exit 1
    fi

    ts_start=$("${unzip_tool}" "$compressed_file_path" | tcpdump -n -r - -c 1 -tt | cut -d' ' -f1)
    echo "get_ts_start_end: ts_start: ${ts_start}"

    echo "$ts_start" > "$output_filepath"

    echo "get_ts_start_end: end"
}

export -f get_ts_start_end

find "$symlink_dir_path" -name "*.pcap" -print0 | xargs -0 -I {} -P 1 -n 1 bash -c 'get_ts_start_end "$@"' _ {}

# https://unix.stackexchange.com/questions/52313/how-to-get-execution-time-of-a-script-effectively
elapsed_seconds=$SECONDS

printf -v date '%(%Y/%m/%d %H-%M-%S)T' -1

echo "build_trace_ts_start_end: elapsed: $((elapsed_seconds / 3600))hrs $(((elapsed_seconds / 60) % 60))min $((elapsed_seconds % 60))sec at ${date}"

echo "build_trace_ts_start_end: end"