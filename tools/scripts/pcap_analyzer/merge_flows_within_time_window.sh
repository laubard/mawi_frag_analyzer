#!/bin/bash

set -eu
set -o pipefail

echo "run_script_on_individual_log: start"

run_path=$1
rust_script_path=$2
log_file=$3
output_filename=$4
nb_processes=$5
time_window=$6

echo "run_script_on_individual_log: run_path: ${run_path}"
echo "run_script_on_individual_log: rust_script_path: ${rust_script_path}"
echo "run_script_on_individual_log: log_file: ${log_file}"
echo "run_script_on_individual_log: output_filename: ${output_filename}"
echo "run_script_on_individual_log: nb_processes: ${nb_processes}"
echo "run_script_on_individual_log: time_window: ${time_window}"

export run_path
export rust_script_path
export log_file
export output_filename
export time_window

printf -v date '%(%Y%m%d_%H%M%S)T' -1

function run() {
	set -e
	set -o pipefail
	echo ""
	echo ""
	echo "run: start"
	curr_log_file_path=$1
	echo "run: curr_log_file_path: ${curr_log_file_path}"

	curr_log_file_dir=$(dirname -- "$curr_log_file_path")
	echo "run_pcap_analyzer: curr_log_file_dir: ${curr_log_file_dir}"

	curr_outfile_path="${curr_log_file_dir}/${output_filename}"
	echo "run: curr_outfile_path: ${curr_outfile_path}"

	output_filename_without_extension="${output_filename%.*}"
	curr_log_file="${curr_log_file_dir}/log_${output_filename_without_extension}"
	echo "run: curr_log_file: ${curr_log_file}"
	echo "run: rust_script_extra_args: ${rust_script_extra_args}"

	set -x
	RUST_LOG=debug "${rust_script_path}" \
		-p "$curr_log_file_path" \
		-o "$curr_outfile_path" \
		--time-window "$time_window" &> "$curr_log_file"
	set +x

	echo "run: end"
}

export -f run

# Execution time measurement
# https://unix.stackexchange.com/questions/52313/how-to-get-execution-time-of-a-script-effectively
SECONDS=0

find "${run_path}" -name "${log_file}" -type f | parallel --bar --halt now,fail=1 -j "${nb_processes}" "run {};"

# https://unix.stackexchange.com/questions/52313/how-to-get-execution-time-of-a-script-effectively
elapsed_seconds=$SECONDS

printf -v date '%(%Y/%m/%d %H-%M-%S)T' -1

echo "run_script_on_individual_log: elapsed: $((elapsed_seconds / 3600))hrs $(((elapsed_seconds / 60) % 60))min $((elapsed_seconds % 60))sec at ${date}"

echo "run_script_on_individual_log: end"
