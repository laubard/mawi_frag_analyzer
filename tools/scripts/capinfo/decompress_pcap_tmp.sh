#!/bin/bash

set -eu
set -o pipefail

echo "extract_packets: start"

echo "extract_packets: current PID: $$"

symlink_parent_dir_path=$1
output_capinfo_dir_path=$2
symlink_dir_name=$3
tmp_output_pcap_path=$4
nb_processes=$5

echo "decompress_pcap_tmp: symlink_parent_dir_path: ${symlink_parent_dir_path}"
echo "decompress_pcap_tmp: output_capinfo_dir_path: ${output_capinfo_dir_path}"
echo "decompress_pcap_tmp: symlink_dir_name: ${symlink_dir_name}"
echo "decompress_pcap_tmp: nb_processes: ${nb_processes}"

tmp_dir_path="${tmp_output_pcap_path}/${symlink_dir_name}"
echo "decompress_pcap_tmp: tmp_dir_path: ${tmp_dir_path}"
rm -rf "$tmp_dir_path"
mkdir -p "$tmp_dir_path"

printf -v date '%(%Y%m%d_%H%M%S)T' -1

output_capinfo_dir_path_run_date="${output_capinfo_dir_path}/run_${date}"
echo "decompress_pcap_tmp: output_capinfo_dir_path_run_date: $output_capinfo_dir_path_run_date"

mkdir -p "$output_capinfo_dir_path_run_date"

symlink_dir_path="${symlink_parent_dir_path}/${symlink_dir_name}"
echo "decompress_pcap_tmp: symlink_dir_path: $symlink_dir_path"

export output_capinfo_dir_path_run_date
export tmp_dir_path
export MAWI_FRAG_ANALYZER_PATH

function decompress_and_filter_and_get_capinfos() {
	set -e

	echo ""
	echo ""
	echo ""
	echo "decompress_and_filter_and_get_capinfos: start"
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

	tmp_output_pcap_file_all_packets="${tmp_dir_path}/${year_month_day}.pcap"
	echo "extract_packets_from: tmp_output_pcap_file_all_packets: ${tmp_output_pcap_file_all_packets}"

	# decompress everything
	#set +e # we unset these options because some pcaps are corrupted
	#set +o pipefail
	if [[ $compressed_file_path == *.gz ]]; then
		zcat "${compressed_file_path}" >"${tmp_output_pcap_file_all_packets}"
	elif [[ $compressed_file_path == *.xz ]]; then
		xzcat "${compressed_file_path}" >"${tmp_output_pcap_file_all_packets}"
	elif [[ $compressed_file_path == *.lz4 ]]; then
		lz4cat "${compressed_file_path}" >"${tmp_output_pcap_file_all_packets}"
	elif [[ $compressed_file_path == *.zstd ]]; then
		zstdcat "${compressed_file_path}" >"${tmp_output_pcap_file_all_packets}"
	else
		echo "decompress_and_filter_and_get_capinfos: unsupported file extension"
		exit 1
	fi

	#set -e
	#set -o pipefail
	echo "decompress_and_filter_and_get_capinfos: ${tmp_output_pcap_file_all_packets} decompression done"

	# filter ipv4 packets only
	tmp_output_pcap_file_only_ipv4_packets="${tmp_dir_path}/${year_month_day}_ipv4.pcap"
	echo "extract_packets_from: tmp_output_pcap_file_only_ipv4_packets: ${tmp_output_pcap_file_only_ipv4_packets}"

	tcpdump -n -r "$tmp_output_pcap_file_all_packets" "ip" -w "$tmp_output_pcap_file_only_ipv4_packets"
	echo "decompress_and_filter_and_get_capinfos: ${tmp_output_pcap_file_only_ipv4_packets} filtering done"

	# filter ipv4 fragments only
	tmp_output_pcap_file_only_ipv4_frags="${tmp_dir_path}/${year_month_day}_ipv4-frags.pcap"
	echo "extract_packets_from: tmp_output_pcap_file_only_ipv4_frags: ${tmp_output_pcap_file_only_ipv4_frags}"

	tcpdump -n -r "$tmp_output_pcap_file_only_ipv4_packets" "ip[7]>0 or ip[6] & 63>0" -w "$tmp_output_pcap_file_only_ipv4_frags"
	echo "decompress_and_filter_and_get_capinfos: ${tmp_output_pcap_file_only_ipv4_frags} filtering done"

	output_capinfo_dir_path_run_date_date="${output_capinfo_dir_path_run_date}/${year_month_day}"
	echo "get_capinfos_from_filter: output_capinfo_dir_path_run_date_date: ${output_capinfo_dir_path_run_date_date}"

	mkdir -p "$output_capinfo_dir_path_run_date_date"
	export output_capinfo_dir_path_run_date_date

	log_output="${output_capinfo_dir_path_run_date_date}/log"
	echo "get_capinfos_from_filter: log_output: ${log_output}"

	# get capinfo from filters
	"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/capinfo/get_capinfos_from_filters.sh" \
		"$output_capinfo_dir_path_run_date" \
		"$tmp_output_pcap_file_all_packets" \
		"$tmp_output_pcap_file_only_ipv4_packets" \
		"$tmp_output_pcap_file_only_ipv4_frags" \
		"$output_capinfo_dir_path_run_date_date" &>"$log_output"

	# remove tmp pcaps
	rm -f "${tmp_output_pcap_file_all_packets}"
	echo "decompress_and_filter_and_get_capinfos: ${tmp_output_pcap_file_all_packets} removing done"
	rm -f "${tmp_output_pcap_file_only_ipv4_packets}"
	echo "decompress_and_filter_and_get_capinfos: ${tmp_output_pcap_file_only_ipv4_packets} removing done"
	rm -f "${tmp_output_pcap_file_only_ipv4_frags}"
	echo "decompress_and_filter_and_get_capinfos: ${tmp_output_pcap_file_only_ipv4_frags} removing done"

	echo "decompress_and_filter_and_get_capinfos: end"
}

export -f decompress_and_filter_and_get_capinfos

find "$symlink_dir_path" -name "*.pcap" -print0 | xargs -0 -I {} -P "$nb_processes" -n 1 bash -c 'decompress_and_filter_and_get_capinfos "$@"' _ {}
#find "$symlink_dir_path" -name "*.pcap" -print0 | parallel -0 --bar --halt now,fail=1 -j "${nb_processes}" "decompress_and_filter_and_get_capinfos {};"


# rm -rf "$tmp_dir_path" ???

# https://unix.stackexchange.com/questions/52313/how-to-get-execution-time-of-a-script-effectively
elapsed_seconds=$SECONDS

printf -v date '%(%Y/%m/%d %H-%M-%S)T' -1

echo "decompress_pcap_tmp: elapsed: $((elapsed_seconds / 3600))hrs $(((elapsed_seconds / 60) % 60))min $((elapsed_seconds % 60))sec at ${date}"

echo "decompress_pcap_tmp: end"
