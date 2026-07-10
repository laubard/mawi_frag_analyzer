# Group capinfos stats into csv files

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/generate_csv_ipv4_frag_stats_filters.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/capinfos/${run_dir_capinfos}" \
"frag_stats" &> log/generate_csv_ipv4_frag_stats_filter &
```

# Compute the number of series for a given series type (e.g., Duplicate, Overlap, Incomplete, Any)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/compute_series_kind_nb.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "stateful-fragment-series-stats.json" \
--outfilename "series_kind_nb.csv" &> log/log_ompute_series_kind_nb &
```

# Compute the number of fragment series with original datagram size inside some size ranges (for fig 3)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/populate_csv_range_datagram_size.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "stateful-fragment-series-stats.json" \
--outfilename "datagram-size-per-range.csv"  &> log/log_populate_csv_range_datagram_size &
```

# Analyze overlap and/or duplicate series to create MDL estimate

## Build sym dir 

### Duplicate

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/build_sym_dir_log_duplicate_inconsistent_checksum.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
"time-window-fragment-series-stats.json" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}/sym-dir-duplicate-inconsistent-checksum-tw-900" \
10 &> log/log_build_sym_dir_log_duplicate_inconsistent_checksum_tw_900_dup &
```


### Overlap

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/build_sym_dir_log_overlap.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
"time-window-fragment-series-stats.json" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}/sym-dir-overlap-tw-900" \
10 &> log/log_build_sym_dir_log_overlap_tw_900 &
```

### Overlap or Duplicate ???

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/build_sym_dir_log_overlap_and_duplicate_inconsistent_checksum.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
"time-window-fragment-series-stats.json" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}/sym-dir-overlap-and-duplicate-inconsistent-checksum-tw-900" \
10 &> log/log_build_sym_dir_log_overlap_and_duplicate_inconsistent_checksum_tw_900 &
```

## Build csv 

### Duplicate

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/build_overlap_duplicate_portions_csv.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--sym-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}/sym-dir-duplicate-inconsistent-checksum-tw-900" \
--outfilename "duplicate-inconsistent-checksum-info-tw-900" \
--serie-kind "Duplicate" \
--start-timestamp-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/trace_ts/10_traces_a_year" &> log/log_build_overlap_duplicate_portions_csv_duplicate_tw_900 &
```

### Overlap

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/build_overlap_duplicate_portions_csv.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--sym-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}/sym-dir-overlap-tw-900" \
--outfilename "overlap-info-tw-900" \
--serie-kind "Overlap" \
--start-timestamp-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/trace_ts/10_traces_a_year" &> log/log_build_overlap_duplicate_portions_csv_overlap_tw_900 &
```

### Duplicate and Overlap ???

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_csv/build_overlap_duplicate_portions_csv.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--sym-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}/sym-dir-overlap-and-duplicate-inconsistent-checksum-tw-900" \
--outfilename "overlap-and-duplicate-inconsistent-checksum-info-tw-900" \
--serie-kind "OverlapOrDuplicate" \
--start-timestamp-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/trace_ts/10_traces_a_year" &> log/log_build_overlap_duplicate_portions_csv_tw_900 &
```