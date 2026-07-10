#!/bin/bash

set -eu
set -o pipefail

echo "get_capinfos_from_filter: start"

output_capinfo_dir_path_run_date=$1
tmp_output_pcap_file_all_packets=$2
tmp_output_pcap_file_only_ipv4_packets=$3
tmp_output_pcap_file_only_ipv4_frags=$4
extra_tcpdump_filter=$5
outfilename_extension=$6

echo "get_capinfos_from_filter: output_capinfo_dir_path_run_date: ${output_capinfo_dir_path_run_date}"
echo "get_capinfos_from_filter: tmp_output_pcap_file_all_packets: ${tmp_output_pcap_file_all_packets}"
echo "get_capinfos_from_filter: tmp_output_pcap_file_only_ipv4_packets: ${tmp_output_pcap_file_only_ipv4_packets}"
echo "get_capinfos_from_filter: tmp_output_pcap_file_only_ipv4_frags: ${tmp_output_pcap_file_only_ipv4_frags}"
echo "get_capinfos_from_filter: extra_tcpdump_filter: ${extra_tcpdump_filter}"
echo "get_capinfos_from_filter: outfilename_extension: ${outfilename_extension}"

# All packets

filename_pcap_all_packets=$(basename -- "${tmp_output_pcap_file_all_packets%.*}")
echo "get_capinfos_from_filter: filename_pcap_all_packets: ${filename_pcap_all_packets}"
dirname_pcap_all_packets=$(dirname -- "${tmp_output_pcap_file_all_packets}")
echo "get_capinfos_from_filter: dirname_pcap_all_packets: ${dirname_pcap_all_packets}"

tmp_output_pcap_file_filter_all_packets="${dirname_pcap_all_packets}/${filename_pcap_all_packets}_${outfilename_extension}.pcap"
echo "get_capinfos_from_filter: tmp_output_pcap_file_filter_all_packets: ${tmp_output_pcap_file_filter_all_packets}"

tcpdump -n -r "$tmp_output_pcap_file_all_packets" "$extra_tcpdump_filter" -w "$tmp_output_pcap_file_filter_all_packets"

filename_output_all_packets="${filename_pcap_all_packets}_${outfilename_extension}.csv"
echo "get_capinfos_from_filter: filename_output_all_packets: ${filename_output_all_packets}"
filepath_output_all_packets="${output_capinfo_dir_path_run_date}/${filename_output_all_packets}"
echo "get_capinfos_from_filter: filepath_output_all_packets: ${filepath_output_all_packets}"

capinfos -Tm "$tmp_output_pcap_file_filter_all_packets" >"$filepath_output_all_packets"

rm -f "$tmp_output_pcap_file_filter_all_packets"

# IPv4 packets

filename_pcap_ipv4_packets=$(basename -- "${tmp_output_pcap_file_only_ipv4_packets%.*}")
echo "get_capinfos_from_filter: filename_pcap_ipv4_packets: ${filename_pcap_ipv4_packets}"
dirname_pcap_ipv4_packets=$(dirname -- "${tmp_output_pcap_file_only_ipv4_packets}")
echo "get_capinfos_from_filter: dirname_pcap_ipv4_packets: ${dirname_pcap_ipv4_packets}"

tmp_output_pcap_file_filter_ipv4_packets="${dirname_pcap_ipv4_packets}/${filename_pcap_ipv4_packets}_${outfilename_extension}.pcap"
echo "get_capinfos_from_filter: tmp_output_pcap_file_filter_ipv4_packets: ${tmp_output_pcap_file_filter_ipv4_packets}"

tcpdump -n -r "$tmp_output_pcap_file_only_ipv4_packets" "$extra_tcpdump_filter" -w "$tmp_output_pcap_file_filter_ipv4_packets"

filename_output_ipv4_packets="${filename_pcap_ipv4_packets}_${outfilename_extension}.csv"
echo "get_capinfos_from_filter: filename_output_ipv4_packets: ${filename_output_ipv4_packets}"
filepath_output_ipv4_packets="${output_capinfo_dir_path_run_date}/${filename_output_ipv4_packets}"
echo "get_capinfos_from_filter: filepath_output_ipv4_packets: ${filepath_output_ipv4_packets}"

capinfos -Tm "$tmp_output_pcap_file_filter_ipv4_packets" >"$filepath_output_ipv4_packets"

rm -f "$tmp_output_pcap_file_filter_ipv4_packets"

# IPv4 frags

filename_pcap_ipv4_frags=$(basename -- "${tmp_output_pcap_file_only_ipv4_frags%.*}")
echo "get_capinfos_from_filter: filename_pcap_ipv4_frags: ${filename_pcap_ipv4_frags}"
dirname_pcap_ipv4_frags=$(dirname -- "${tmp_output_pcap_file_only_ipv4_frags}")
echo "get_capinfos_from_filter: dirname_pcap_ipv4_frags: ${dirname_pcap_ipv4_frags}"

tmp_output_pcap_file_filter_ipv4_frags="${dirname_pcap_ipv4_frags}/${filename_pcap_ipv4_frags}_${outfilename_extension}.pcap"
echo "get_capinfos_from_filter: tmp_output_pcap_file_filter_ipv4_frags: ${tmp_output_pcap_file_filter_ipv4_frags}"

tcpdump -n -r "$tmp_output_pcap_file_only_ipv4_frags" "$extra_tcpdump_filter" -w "$tmp_output_pcap_file_filter_ipv4_frags"

filename_output_ipv4_frags="${filename_pcap_ipv4_frags}_${outfilename_extension}.csv"
echo "get_capinfos_from_filter: filename_output_ipv4_frags: ${filename_output_ipv4_frags}"
filepath_output_ipv4_frags="${output_capinfo_dir_path_run_date}/${filename_output_ipv4_frags}"
echo "get_capinfos_from_filter: filepath_output_ipv4_frags: ${filepath_output_ipv4_frags}"

capinfos -Tm "$tmp_output_pcap_file_filter_ipv4_frags" >"$filepath_output_ipv4_frags"

rm -f "$tmp_output_pcap_file_filter_ipv4_frags"

echo "get_capinfos_from_filter: end"
