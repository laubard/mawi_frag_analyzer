#!/bin/bash

set -eu
set -o pipefail

echo "run_script_on_individual_log: start"

run_path=$1
ts_logfile_path=$2
pcapanlyzer_log_file=$3
output_filename=$4
seconds_to_filter=$5
nb_processes=$6

echo "run_script_on_individual_log: run_path: ${run_path}"
echo "run_script_on_individual_log: ts_logfile_path: ${ts_logfile_path}"
echo "run_script_on_individual_log: pcapanlyzer_log_file: ${pcapanlyzer_log_file}"
echo "run_script_on_individual_log: output_filename: ${output_filename}"
echo "run_script_on_individual_log: seconds_to_filter: ${seconds_to_filter}"
echo "run_script_on_individual_log: nb_processes: ${nb_processes}"

output_filename_without_extension="${output_filename%.*}"
echo "run_script_on_individual_log: output_filename_without_extension: ${output_filename_without_extension}"

export run_path
export ts_logfile_path
export pcapanlyzer_log_file
export output_filename
export output_filename_without_extension
export seconds_to_filter

function run() {
	set -e
	echo ""
	echo ""
	echo "run: start"
	curr_log_file_path=$1
	echo "run: curr_log_file_path: ${curr_log_file_path}"

	curr_log_file_dir=$(dirname -- "$curr_log_file_path")
	echo "run: curr_log_file_dir: ${curr_log_file_dir}"

	curr_outfile_dir="${curr_log_file_dir}"
	echo "run: curr_outfile_dir: ${curr_outfile_dir}"
	mkdir -p "$curr_outfile_dir"

	curr_outfile_path="${curr_outfile_dir}/${output_filename}"
	#curr_outfile_path="${curr_log_file_dir}/${output_filename}"
	echo "run: curr_outfile_path: ${curr_outfile_path}"

	curr_log_file="${curr_outfile_dir}/log_${output_filename_without_extension}"
	echo "run: curr_log_file: ${curr_log_file}"

	curr_date=$(basename -- "$curr_log_file_dir" | cut -d'-' -f2,3,4)
	echo "run: curr_date: ${curr_date}"

	curr_ts_log_file="${ts_logfile_path}/${curr_date}.txt"
	echo "run: curr_ts_log_file: ${curr_ts_log_file}"

	if [ $(wc -c <"$curr_ts_log_file") -eq 1 ]; then
		echo " ${curr_date} because trace is empty"
		ts_start_secs=0
		ts_start_micros=0
	else
		ts_start=$(cat "$curr_ts_log_file")
		echo "run: ts_start: ${ts_start}"
		ts_start_secs=$(echo $ts_start | cut -d'.' -f1)
		echo "run: ts_start_secs: ${ts_start_secs}"
		ts_start_micros=$(echo $ts_start | cut -d'.' -f2)
		echo "run: ts_start_micros: ${ts_start_micros}"
	fi

	set -x
	RUST_LOG=debug "${MAWI_FRAG_ANALYZER_PATH}/rust_code/target/debug/filter_three_tuple_frag_stats_with_ts_in_start_end" \
		-p "$curr_log_file_path" \
		-o "$curr_outfile_path" \
		-s "$ts_start_secs" \
		-m "$ts_start_micros" \
		-f "$seconds_to_filter" &>"$curr_log_file"
	set +x

	echo "run: end"
}

export -f run

find "${run_path}" -name "${pcapanlyzer_log_file}" -type f | parallel --no-notice --bar --halt now,fail=1 -j "${nb_processes}" "run {};"

echo "run_script_on_individual_log: end"
