#!/bin/bash

set -eu
set -o pipefail

echo "analyze_packets: start"

pcap_analyzer_script_path=$1
pcap_analyzer_conf_path=$2
outdir=$3
symlink_dir_path=$4
nb_processes=$5

echo "analyze_packets: pcap_analyzer_script_path: ${pcap_analyzer_script_path}"
echo "analyze_packets: outdir: ${outdir}"
echo "analyze_packets: symlink_dir_path: ${symlink_dir_path}"
echo "analyze_packets: nb_processes: ${nb_processes}"
echo "analyze_packets: pcap_analyzer_conf_path: ${pcap_analyzer_conf_path}"

printf -v date '%(%Y%m%d_%H%M%S)T' -1

outdir_run_date="${outdir}/run_${date}"
echo "analyze_packets: outdir_run_date: $outdir_run_date"

mkdir -p "$outdir_run_date"

export outdir_run_date
export pcap_analyzer_script_path
export pcap_analyzer_conf_path

function analyze_packet_file() {
	set -e

	echo ""
	echo ""
	echo ""
	echo "analyze_packet_file: start"
	symlink_file_path=$1
	echo "extract_packets_from: symlink_file_path: ${symlink_file_path}"
	compressed_file_path=$(readlink -f "$symlink_file_path")
	echo "extract_packets_from: compressed_file_path: ${compressed_file_path}"
	#compressed_file_name=$(basename -- "$compressed_file_path")
	compressed_file_name=$(basename -- "$symlink_file_path")
	echo "extract_packets_from: compressed_file_name: ${compressed_file_name}"

	year_month_day_tmp="${compressed_file_name%.*}"
	year_month_day="${year_month_day_tmp%.*}" # do it twice because from 2016, file extension is .pcap.xz
	echo "extract_packets_from: year_month_day: ${year_month_day}"

	year=$(echo "${year_month_day}" | cut -d'-' -f1)
	echo "analyze_packet_file: year: ${year}"
	month=$(echo "${year_month_day}" | cut -d'-' -f2)
	echo "analyze_packet_file: month: ${month}"
	day=$(echo "${year_month_day}" | cut -d'-' -f3)
	echo "analyze_packet_file: day: ${day}"

	current_outdir="${outdir_run_date}/${year}/${month}/output-${year_month_day}"
	echo "analyze_packet_file: current_outdir: ${current_outdir}"
	mkdir -p "$current_outdir"
	current_log="${current_outdir}/analyze_packets_log"
	echo "analyze_packet_file: current_log: ${current_log}"

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

	"${unzip_tool}" "$compressed_file_path" | tcpdump -n -r - "ip[7]>0 or ip[6] & 63>0" -w - |
		"$pcap_analyzer_script_path" \
			- \
			-c "${pcap_analyzer_conf_path}/pcap-analyzer.conf" \
			-p "FragStat" \
			--outdir "$current_outdir" &>"$current_log"

	echo "analyze_packet_file: end"
}

export -f analyze_packet_file

# Execution time measurement
# https://unix.stackexchange.com/questions/52313/how-to-get-execution-time-of-a-script-effectively
SECONDS=0

find "$symlink_dir_path" -name "*.pcap" -print0 | xargs -0 -I {} -P "$nb_processes" bash -c 'analyze_packet_file "$@"' _ {}

# https://unix.stackexchange.com/questions/52313/how-to-get-execution-time-of-a-script-effectively
elapsed_seconds=$SECONDS

printf -v date '%(%Y/%m/%d %H-%M-%S)T' -1

echo "analyze_packets: elapsed: $((elapsed_seconds / 3600))hrs $(((elapsed_seconds / 60) % 60))min $((elapsed_seconds % 60))sec at ${date}"

echo "analyze_packets: end"
