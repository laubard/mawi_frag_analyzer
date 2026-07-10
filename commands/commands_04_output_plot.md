# Plot per frag, L4 and service (ie fig 1)

## Without log scale  

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/generate_plot_ipv4_frag_stats_filters.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/capinfos/${run_dir_capinfos}" \
"frag_stats" \
false &> log/log_generate_plot_ipv4_frag_stats_filters &
```

## With log scale  

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/generate_plot_ipv4_frag_stats_filters.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/capinfos/${run_dir_capinfos}" \
"frag_stats" \
true &> log/log_generate_plot_ipv4_frag_stats_filters &
```

# Plot stacked L4 proto (ie fig 10)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/plot_l4_proto_stack_chart.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/capinfos/${run_dir_capinfos}" \
--output-filepath "${MAWI_FRAG_ANALYZER_PATH}/output/capinfos/${run_dir_capinfos}/plot/l4_proto_stack_chart" &> log/plot_l4_proto_stack_chart &
```

# Plot series types (ie fig 2)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/plot_serie_evolution.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "stateful-fragment-series-stats.json" \
--outfilename "serie_evolution" &> log/log_plot_serie_evolution &
```

# Plot datagram sizes in datagram sizes ranges (ie fig 3)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/generate_plot_and_csv_range_datagram_size.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "datagram-size-per-range" &> log/log_generate_plot_and_csv_range_datagram_size &
```

# Plot and get PMTU info (ie fig 8 and table I)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/plot_max_frag_size_heatmap.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "stateful-fragment-series-stats.json" \
--outfilename "max_frag_size" \
--range-y 1 &> log/log_plot_max_frag_size_heatmap &
```

# Plot original (guessed) datagram sizes (ie fig 9)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/plot_guessed_datagram_size_heatmap.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "stateful-fragment-series-stats.json" \
--outfilename "guessed_datagram_size_heatmap" \
--range-y 1 &> log/log_plot_guessed_datagram_size_heatmap &
```

# Plot L4 services with iana labels (ie fig 4)

## UDP

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/plot_services_from_serie_kind.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--service-name-port-number-filepath "${PCAP_ANALYZER_PATH}/assets/service-names-port-numbers.csv" \
--infilename "generic-frag-stats.json" \
--outfilename "iana-services" \
--service-number 10 \
--verbose "false" \
--l4-protocol "udp" \
--mode "abs" \
--service-sorting "trace-presence" \
--datagramNb-or-bytes "datagramNb" &> log/log_plot_iana_services_from_serie_kinds &
```

## TCP

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/plot_services_from_serie_kind.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--service-name-port-number-filepath "${PCAP_ANALYZER_PATH}/assets/service-names-port-numbers.csv" \
--infilename "generic-frag-stats.json" \
--outfilename "iana-services" \
--service-number 10 \
--verbose "false" \
--l4-protocol "tcp" \
--mode "abs" \
--service-sorting "trace-presence" \
--datagramNb-or-bytes "datagramNb" &> log/log_plot_iana_services_from_serie_kinds &
```

# Plot hosts and three tuples number across years (ie fig 5)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/generate_plot_and_csv_host_diversity.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "stateful-fragment-series-stats.json" \
--outfilename "host_diversity" &> log/log_generate_plot_and_csv_host_diversity &
```

# Plot the cumulative traffic for top x hosts (ie fig 11)

## by series number

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/generate_scatter_host_diversity.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "stateful-fragment-series-stats.json" \
--outfilename "host_scatter_series" \
--series-or-bytes "series" &> log/log_generate_scatter_host_diversity_series &
```

## by bytes

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/generate_scatter_host_diversity.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
--infilename "stateful-fragment-series-stats.json" \
--outfilename "host_scatter_bytes" \
--series-or-bytes "bytes" &> log/log_generate_scatter_host_diversity_bytes &
```

# Plot ECDF of MDL estimate (ie fig 7)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/plot_host_mdl_estimate_ecdf.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
-id "duplicate-inconsistent-checksum-info-tw-900.csv" \
-io "overlap-info-tw-900.csv" \
--outfilename "host_mdl_estimate_ecdf" \
--xmax 120 &> log/log_plot_host_mdl_estimate_ecdf & 
```

### Plot host proportion with MDL estimate under value across years (ie fig 12)

```bash
python "${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/output_plot/plot_host_mdl_estimate_years.py" \
--run-dir "${MAWI_FRAG_ANALYZER_PATH}/output/pcap_analyzer/${run_dir_pcap_analyzer}" \
-id "duplicate-inconsistent-checksum-info-tw-900.csv" \
-io "overlap-info-tw-900.csv" \
--outfilename "host_mdl_estimate_years" \
--xmax 120 &> log/log_plot_host_mdl_estimate_years & 
```