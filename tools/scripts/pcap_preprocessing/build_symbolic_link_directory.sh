#!/bin/bash

set -eu
set -o pipefail

echo "build_symbolic_link_directory: start"

pcap_dir=$1
incsvfile=$2
outdir=$3

echo "build_symbolic_link_directory: pcap_dir: ${pcap_dir}"
echo "build_symbolic_link_directory: incsvfile: ${incsvfile}"
echo "build_symbolic_link_directory: outdir: ${outdir}"

echo "build_symbolic_link_directory: creating symlink dir"
rm -rf "$outdir"
mkdir -p "$outdir" 

jq -c '.[]' "$incsvfile" | while read -r item; do
    year=$(echo "$item" | jq '.year')
    #echo "Year: $year"
    # Loop over each date
    echo "$item" | jq -r '.date_v[]' | while read -r date; do
        month=$(echo "$date" | cut -d'-' -f2)

        all_ip_packets_pcap_filename="${date}.*"
        symlink_path="${outdir}/${date}.pcap"

        set +e
        readarray -d '' array_all < <(find "${pcap_dir}/${year}/${month}" -maxdepth 1 -name "$all_ip_packets_pcap_filename" -print0)
        set -e

        if [ -z "${array_all+x}" ]; then 
          echo " skipping ${date} because trace is not present"
        elif [ "$(wc -c <"$array_all")" -eq 32 ] || [ "$(wc -c <"$array_all")" -eq 0 ]; then 
          echo " skipping ${date} because trace is empty"
        else 
          ln -s "$array_all" "$symlink_path"
        fi
    done
done

echo "build_symbolic_link_directory: end"
