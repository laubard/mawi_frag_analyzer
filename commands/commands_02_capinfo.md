# A. Execute capinfos and store the stats 

```bash
"${MAWI_FRAG_ANALYZER_PATH}/tools/scripts/capinfo/decompress_pcap_tmp.sh" \
"${MAWI_FRAG_ANALYZER_PATH}/output/pcap_preprocessing/symbolic_dir" \
"${MAWI_FRAG_ANALYZER_PATH}/output/capinfos" \
"10_traces_a_year" \
"${TMP_OUTPUT_PCAP_PATH}" \
10 &> log/log_decompress_pcap_tmp &
```

# B. Store run_dir_capinfos environment variable

The previous command output log in a dir inside ${MAWI_FRAG_ANALYZER_PATH}/output/capinfos 
and prefixed with run_20. 
Either store permanently this run_dir_capinfos name in you ~.profile or export it temporarily. 