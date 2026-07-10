#!/bin/bash

set -eu
set -o pipefail

echo "extract_corrupted_pcap: start"

symlink_dir_path=$1
nb_processes=$2

echo "extract_corrupted_pcap: symlink_dir_path: ${symlink_dir_path}"
echo "extract_corrupted_pcap: nb_processes: ${nb_processes}"

printf -v date '%(%Y%m%d_%H%M%S)T' -1

function analyze_packet_file() {
	set -e

	symlink_file_path=$1
	compressed_file_path=$(readlink -f "$symlink_file_path")

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

	# test what is the output when a file is corrupted
	if [[ $("${unzip_tool}" "$compressed_file_path" | tcpdump -n -r - "ip[7]>0 or ip[6] & 63>0" -w /dev/null 2>&1) =~ "truncated dump file" ]]; then
		echo "Corrupted compressed file $compressed_file_path"
	fi
}

export -f analyze_packet_file

# Execution time measurement
# https://unix.stackexchange.com/questions/52313/how-to-get-execution-time-of-a-script-effectively
SECONDS=0

find "$symlink_dir_path" -name "*.pcap" -print0 | xargs -0 -I {} -P "$nb_processes" bash -c 'analyze_packet_file "$@"' _ {}

# https://unix.stackexchange.com/questions/52313/how-to-get-execution-time-of-a-script-effectively
elapsed_seconds=$SECONDS

printf -v date '%(%Y/%m/%d %H-%M-%S)T' -1

echo "extract_corrupted_pcap: elapsed: $((elapsed_seconds / 3600))hrs $(((elapsed_seconds / 60) % 60))min $((elapsed_seconds % 60))sec at ${date}"

echo "extract_corrupted_pcap: end"
