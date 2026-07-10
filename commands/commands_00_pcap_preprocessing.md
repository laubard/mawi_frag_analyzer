# Generate random dates

## Daily traces dataset

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/generate_random_dates_csv.py" \
--outfilepath "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/list_10_traces_a_year.json" \
--mawi-data-path "${MAWI_DATA_PATH}" \
--year-start 2007 \
--year-end 2025 \
--day-number-per-year 100 &> log/log_generate_random_dates_csv &
```

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/generate_random_dates_csv.py" \
--outfilepath "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/list_10_traces_a_year.json" \
--mawi-data-path "${MAWI_DATA_PATH}" \
--year-start 2007 \
--year-end 2025 \
--day-number-per-year 10 &> log/log_generate_random_dates_csv &
```

## Longer traces dataset

```bash
sudo python3 "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/get_random_subtrace_from_long_traces.py" \
--outfilepath "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/list_random_longer_traces.csv" \
--hours 4 &> log/log_get_random_subtrace_from_long_traces &
```

# Build sym link dir

## Daily traces dataset

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/build_symbolic_link_directory.sh" \
"${MAWI_DATA_PATH}" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/list_10_traces_a_year.json" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/10_traces_a_year" &> log/log_build_symbolic_link_directory &
```

## Longer traces dataset

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/build_symbolic_link_directory_for_long_traces.sh" \
"${MAWI_DATA_PATH}" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/list_random_longer_traces.csv" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/longer_traces" &> log/log_build_symbolic_link_directory_for_long_traces &
```

sudo "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/build_symbolic_link_directory_for_long_traces.sh" "${MAWI_DATA_PATH}" "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/list_random_longer_traces.csv" "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/longer_traces" &> log/log_build_symbolic_link_directory_for_long_traces

# Verify that compressed files are not corrupted

## Daily traces dataset

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/extract_corrupted_pcap_files.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/10_traces_a_year" \
60 &> log/log_commands_extract_corrupted_pcap_files &
```

Then verify result in log/log_commands_extract_corrupted_pcap_files

## Longer traces dataset

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/extract_corrupted_pcap_files.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/longer_traces" \
20 &> log/log_commands_extract_corrupted_pcap_files &'
```

Then verify result in log/log_commands_extract_corrupted_pcap_files


# Get starting timestamp of pcaps    

## Daily traces dataset

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/build_trace_ts_start_end.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/10_traces_a_year" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/trace_ts/10_traces_a_year" &> log/log_build_trace_ts_start_end &
```

## Longer traces dataset

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_preprocessing/build_trace_ts_start_end.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/longer_traces" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/trace_ts/longer_traces" &> log/log_build_trace_ts_start_end &
```

