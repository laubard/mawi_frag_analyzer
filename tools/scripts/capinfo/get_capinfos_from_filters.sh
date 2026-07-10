#!/bin/bash

set -eu
set -o pipefail

echo "get_capinfos_from_filters: start"

output_capinfo_dir_path_run=$1
tmp_output_pcap_file_all_packets=$2
tmp_output_pcap_file_only_ipv4_packets=$3
tmp_output_pcap_file_only_ipv4_frags=$4
output_capinfo_dir_path_run_date=$5

echo "get_capinfos_from_filters: output_capinfo_dir_path_run: ${output_capinfo_dir_path_run}"
echo "get_capinfos_from_filters: tmp_output_pcap_file_all_packets: ${tmp_output_pcap_file_all_packets}"
echo "get_capinfos_from_filters: tmp_output_pcap_file_only_ipv4_packets: ${tmp_output_pcap_file_only_ipv4_packets}"
echo "get_capinfos_from_filters: output_capinfo_dir_path_run_date: ${output_capinfo_dir_path_run_date}"

export tmp_output_pcap_file_all_packets
export tmp_output_pcap_file_only_ipv4_packets
export tmp_output_pcap_file_only_ipv4_frags
export output_capinfo_dir_path_run_date
export MAWI_FRAG_ANALYZER_PATH

function get_capinfo_filter() {
	set -e

	echo ""
	echo ""
	echo ""
	echo "get_capinfo_filter: start"
	extra_tcpdump_filter=$1
	outfilename_extension=$2
	echo "get_capinfo_filter: extra_tcpdump_filter: ${extra_tcpdump_filter}"
	echo "get_capinfo_filter: outfilename_extension: ${outfilename_extension}"

	log_filter="${output_capinfo_dir_path_run_date}/log_${outfilename_extension}"
	echo "get_capinfo_filter: log_filter: ${log_filter}"

	"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/capinfo/get_capinfos_from_filter.sh" \
		"$output_capinfo_dir_path_run_date" \
		"$tmp_output_pcap_file_all_packets" \
		"$tmp_output_pcap_file_only_ipv4_packets" \
		"$tmp_output_pcap_file_only_ipv4_frags" \
		"$extra_tcpdump_filter" \
		"$outfilename_extension" &>"$log_filter"

	echo "get_capinfo_filter: end"
}

export -f get_capinfo_filter

get_capinfo_filter "" "no-filter"
get_capinfo_filter "proto 17" "proto-17"
get_capinfo_filter "proto 6" "proto-6"
get_capinfo_filter "proto 50" "proto-50"
get_capinfo_filter "proto 47" "proto-47"
get_capinfo_filter "proto 1" "proto-1"
get_capinfo_filter "proto 17 and port 53" "proto-17-port-53"
#get_capinfo_filter "proto 17 and port 161" "proto-17-port-161"
#get_capinfo_filter "proto 17 and port 389" "proto-17-port-389"
#get_capinfo_filter "proto 17 and port 443" "proto-17-port-443"
#get_capinfo_filter "proto 17 and port 1194" "proto-17-port-1194"
#get_capinfo_filter "proto 17 and port 4500" "proto-17-port-4500"
#
#get_capinfo_filter "proto 17 and port 5060" "proto-17-port-5060"
#get_capinfo_filter "proto 17 and port 3074" "proto-17-port-3074"
#get_capinfo_filter "proto 17 and port 21" "proto-17-port-21"
#get_capinfo_filter "proto 17 and port 500" "proto-17-port-500"
#get_capinfo_filter "proto 17 and port 2049" "proto-17-port-2049"
#get_capinfo_filter "proto 17 and port 1812" "proto-17-port-1812"
#get_capinfo_filter "proto 17 and port 1080" "proto-17-port-1080"
#get_capinfo_filter "proto 17 and port 1863" "proto-17-port-1863"
#
#get_capinfo_filter "proto 17 and port 1024" "proto-17-port-1024"
#get_capinfo_filter "proto 17 and port 1024" "proto-17-port-1026"
#get_capinfo_filter "proto 17 and port 1024" "proto-17-port-1027"
#get_capinfo_filter "proto 17 and port 1024" "proto-17-port-1028"
#get_capinfo_filter "proto 17 and port 1024" "proto-17-port-1029"
#get_capinfo_filter "proto 17 and port 1024" "proto-17-port-19"
#get_capinfo_filter "proto 17 and port 1024" "proto-17-port-1"


echo "get_capinfos_from_filters: end"
