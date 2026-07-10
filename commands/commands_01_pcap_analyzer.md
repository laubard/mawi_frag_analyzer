# A. Run pcap-analyzer executable

It constructs stateful fragment series.

## Daily traces dataset

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_analyzer/analyze_packets.sh" \
"${PCAP_ANALYZER_PATH}/target/debug/pcap-analyzer" \
"${PCAP_ANALYZER_PATH}/conf" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/10_traces_a_year" \
40 &> log/log_analyze_packets & 
```

## Longer traces dataset

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_analyzer/analyze_packets.sh" \
"${PCAP_ANALYZER_PATH}/target/debug/pcap-analyzer" \
"${PCAP_ANALYZER_PATH}/conf" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir/longer_traces" \
30 &> log/log_analyze_packets & 
```

# B. Store run_dir_pcap_analyzer environment variable

The previous command output log in a dir inside ${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer 
and prefixed with run_20. 
Either store permanently this run_dir_pcap_analyzer name in you ~.profile or export it temporarily. 

# C. Merge flows within a 900-second time window

It constructs time window fragment series.

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_analyzer/merge_flows_within_time_window.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/$run_dir_pcap_analyzer" \
"${MAWI_FRAG_ANALYZER_PATH}/tools/mawi_frag_analyzer_rs/target/debug/merge_flows_within_time_window" \
"three-tuple-frag-stats.json" \
"merged-three-tuple-frag-stats_tw-900.json" \
40 \
"--time-window" \
"900" &> log/log_merge_flows_within_time_window &
```

# D. Fill extension flow stat (post pcap-analyzer analysis)

## Stateful series

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_analyzer/run_script_on_individual_log.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/$run_dir_pcap_analyzer" \
"${MAWI_FRAG_ANALYZER_PATH}/tools/mawi_frag_analyzer_rs/target/debug/fill_extension_flow_stat" \
"three-tuple-frag-stats.json" \
"stateful-fragment-series-stats.json" \
40 &> log/log_fill_extension_flow_stat &
```

## Time window series

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_analyzer/run_script_on_individual_log.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/$run_dir_pcap_analyzer" \
"${MAWI_FRAG_ANALYZER_PATH}/tools/mawi_frag_analyzer_rs/target/debug/fill_extension_flow_stat" \
"merged-three-tuple-frag-stats_tw-900.json" \
"time-window-fragment-series-stats.json" \
40 &> log/log_fill_extension_flow_stat &
```

# E. Generate generic frag stats (L4 proto, L4 proto services and host info per log)

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/pcap_analyzer/run_script_on_individual_log.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/$run_dir_pcap_analyzer" \
"${MAWI_FRAG_ANALYZER_PATH}/tools/mawi_frag_analyzer_rs/target/debug/generate_generic_frag_stats" \
"stateful-fragment-series-stats.json" \
"generic-frag-stats.json" \
40 &> log/log_generate_generic_frag_stats &
```