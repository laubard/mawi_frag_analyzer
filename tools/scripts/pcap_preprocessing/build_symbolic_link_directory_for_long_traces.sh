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

tail -n +2 "${incsvfile}" | while IFS=',' read -r _date path_to_trace _trace_name fake_date; do
    echo "fake_date: ${fake_date}"
    year=$(echo "${fake_date}" | cut -d'-' -f1)
    month=$(echo "${fake_date}" | cut -d'-' -f2)
    
    symlink_path="${outdir}/${year}-${month}-01.pcap"
    echo "symlink_path: ${symlink_path}"

    set +e
    readarray -d '' array_all < <(find "${path_to_trace}" -print0)
    set -e

    if [ -z "${array_all+x}" ]; then 
      echo " skipping ${fake_date} because trace is not present"
    elif [ "$(wc -c <"${array_all}")" -eq 32 ] || [ "$(wc -c <"$array_all")" -eq 0 ]; then 
      echo " skipping ${fake_date} because trace is empty"
    else 
      ln -s "$array_all" "$symlink_path"
    fi
done

echo "build_symbolic_link_directory: end"
