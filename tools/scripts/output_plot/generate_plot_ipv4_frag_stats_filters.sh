#!/bin/bash

set -eu
set -o pipefail

echo "generate_plot_ipv4_frag_stats_filters: start"

run_dir=$1
infilename_prefix=$2
log_scale=$3

echo "generate_plot_ipv4_frag_stats_filters: run_dir: ${run_dir}"
echo "generate_plot_ipv4_frag_stats_filters: infilename_prefix: ${infilename_prefix}"
echo "generate_plot_ipv4_frag_stats_filters: log_scale: ${log_scale}"

export run_dir
export infilename_prefix
export log_scale

function generate_plot_ipv4_frag_stats_filter() {
	set -e

	echo ""
	echo ""
	echo ""
	echo "generate_plot_ipv4_frag_stats_filter: start"
	filter_name=$1
	plot_title=$2
	echo "generate_plot_ipv4_frag_stats_filter: filter_name: ${filter_name}"
	echo "generate_plot_ipv4_frag_stats_filter: plot_title: ${plot_title}"
	infilename_ipv4_all="${infilename_prefix}_${filter_name}.csv"
	echo "generate_plot_ipv4_frag_stats_filter: infilename_ipv4_all: ${infilename_ipv4_all}"
	infilename_ipv4_frags="${infilename_prefix}_frags_${filter_name}.csv"
	echo "generate_plot_ipv4_frag_stats_filter: infilename_ipv4_frags: ${infilename_ipv4_frags}"
	outfilename_no_extension="${infilename_prefix}_log-${log_scale}_${filter_name}"
	echo "generate_plot_ipv4_frag_stats_filter: outfilename_no_extension: ${outfilename_no_extension}"

	python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/generate_plot_ipv4_frag_stats_filter.py" \
		--run-dir "$run_dir" \
		--infilename-ipv4-all "$infilename_ipv4_all" \
		--infilename-ipv4-frags "$infilename_ipv4_frags" \
		--outfilename-no-extension "$outfilename_no_extension" \
		--plot-title "$plot_title" \
		--log-scale "$log_scale"

	echo "generate_plot_ipv4_frag_stats_filter: end"
}

export -f generate_plot_ipv4_frag_stats_filter

generate_plot_ipv4_frag_stats_filter "no-filter" ""
generate_plot_ipv4_frag_stats_filter "proto-17" "UDP"
generate_plot_ipv4_frag_stats_filter "proto-6" "TCP"
generate_plot_ipv4_frag_stats_filter "proto-50" "ESP"
generate_plot_ipv4_frag_stats_filter "proto-47" "GRE"
generate_plot_ipv4_frag_stats_filter "proto-1" "ICMP"
generate_plot_ipv4_frag_stats_filter "proto-17-port-53" "UDP/DNS"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-161" "UDP/SNMP"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-389" "UDP/LDAP"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-443" "UDP/QUIC"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-1194" "UDP/OPENVPN"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-4500" "UDP/IPSEC-NAT-T"
#
#generate_plot_ipv4_frag_stats_filter "proto-17-port-5060" "UDP/SIP"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-3074" "UDP/XBOX"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-21" "UDP/FTP"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-500" "UDP/ISAKMP"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-2049" "UDP/SHILP"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-1812" "UDP/RADIUS"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-1080" "UDP/SOCKS"
#generate_plot_ipv4_frag_stats_filter "proto-17-port-1863" "UDP/MSNP"

echo "generate_plot_ipv4_frag_stats_filters: end"
