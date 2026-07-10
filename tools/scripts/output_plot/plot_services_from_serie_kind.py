#!/usr/bin/python3
"""This script builds the Fig. 4 plots from the paper."""
import argparse
import json
import sys
from pathlib import Path
#from distutils.util import strtobool

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

sys.path.append(str(Path(__file__).parent.parent))
from misc.common import strtobool, create_output_dir, find_log_v, build_datetime64_from_path

###############################################################################
######################### Constant value declaration ##########################

PORT_SERVICENAME_UDP_HM = { # built manually from IANA info
    "53": "DNS",
    "161": "SNMP",
    "443": "QUIC",
    "4500": "IPSec",
    "5060": "SIP",
    "1194": "OpenVPN",
    "1026": "CAP",
    "3074": "Xbox",
    "389": "LDAP",
    "1027": "6a44",
    "1029": "DCOM, SOLID-MUX",
    "500": "ISAKMP, IKE",
    "1863": "MSNP",
    "1812": "RADIUS",
    "1": "TCPMUX",
    "22": "SSH",
    "2049": "NFS",
    "1080": "SOCKS",
    "80": "HTTP? QUIC?",
    "19": "CHARGEN",
    "111": "Sun RPC",
    "21": "FTP",
    "27015": "Steam, GoldSrc, Source (2) engine",
    "453": "CreativeServer",
    "427": "SLP, SRVLOC",
    "179": "BGP",
    "104": "DICOM",
    "20": "FTP",
    "1813": "RADIUS",
    "152": "BFTP",
}

PORT_SERVICENAME_TCP_HM = { # built manually from IANA info
    "443": "HTTPS",
    "80": "HTTP",
    "22": "SSH, SFTP",
    "111": "Sun RPC",
    "993": "IMAPS",
    "25": "SMTP",
    "20": "FTP",
    "21": "FTP",
    "143": "IMAP",
    "53": "DNS",
    "23": "Telnet",
    "554": "RTSP",
    "88": "Kerberos",
    "631": "IPP, CUPS",
    "445": "Microsoft-DS",
    "135": "EPMAP",
    "587": "MSA",
    "702": "IRIS-BEEP",
    "318": "PKIS-TSP",
}

# IANA says they are assigned, but no other source support it
PORT_UDP_BLACKLIST_V = [
    "0",
    "1024",
    "1028",
]
PORT_TCP_BLACKLIST_V = [
    "0",
    "1024",
]

###############################################################################
########################## Script specific functions ##########################


def build_port_dict(path: str, l4_protocol: str):
    """Pick L4 protocol entries from the IANA service-names-port-numbers.csv
    file."""
    df = pd.read_csv(path)
    return df.loc[df['Transport Protocol'] == l4_protocol]


def build_l4_protocol_i(l4_protocol: str) -> int:
    """Transform protocol string into IPv4 protocol number."""
    if l4_protocol == 'udp':
        return 17
    if l4_protocol == 'tcp':
        return 6

    raise ValueError('Unexpected l4_protocol')


def get_service_name(service_both_sides: str, l4_protocol_i: int,
                     l4_protocol_s: str, port_file: str, verbose: bool) -> str:
    """Build the service name from the corresponding log entry."""
    service_both_sides_lower = service_both_sides.lower()
    custom_service_port_hm = PORT_SERVICENAME_UDP_HM if l4_protocol_i == 17 else PORT_SERVICENAME_TCP_HM
    port_blacklist_v = PORT_UDP_BLACKLIST_V if l4_protocol_i == 17 else PORT_TCP_BLACKLIST_V
    iana_service_port_df = build_port_dict(port_file, l4_protocol_s)

    if l4_protocol_s in service_both_sides_lower:
        if "Assigned" in service_both_sides:
            if len(service_both_sides.split(":")[1].split("->")) == 1:
                port = service_both_sides.split(":")[1]
            else:
                # both src and dst ports are assigned, keep the min
                port_src = service_both_sides.split(":")[1].split("->")[0]
                port_dst = service_both_sides.split(":")[1].split("->")[1]
                port = min(port_src, port_dst)

            service_o = iana_service_port_df.loc[
                iana_service_port_df['Port Number'] == port, 'Service Name']

            if port in port_blacklist_v:
                # IANA says they are assigned, but no other source support it
                return "-1"
            if port in custom_service_port_hm:
                # provide a pretty string format for the service
                return f'{port} ({custom_service_port_hm[port]})'
            if service_o.empty:
                # assigned without a name?
                return port
            # otherwise, get IANA's name
            return f'{port} ({service_o.iat[0]})'

        if verbose:
            return "Non Assigned"
    if f"None:{l4_protocol_i}" in service_both_sides and verbose:
        return "Missing Info"

    return "-1"


def retrieve_stat(hm: dict, datagramnb_or_bytes: str) -> int:
    """Get total datagram nb or bytes."""
    return hm[
        "total_nb_datagrams"] if datagramnb_or_bytes == "datagramNb" else hm[
            "total_data_bytes"]


def build_service_date_info_hm_hm(log_v: list, l4_protocol_s: str,
                                  l4_protocol_i: int, port_file: str,
                                  verbose: bool,
                                  datagramnb_or_bytes: str) -> dict:
    """Build a dictionary of services' stat for each date log."""
    service_date_info_hm_hm = {}
    # iterate over the logs
    for log in log_v:
        service_info_v_hm = {}

        with open(log, encoding='utf8') as file:
            json_content = json.load(file)

        print("process: log: ", log)
        date = build_datetime64_from_path(log)

        if str(l4_protocol_i
               ) not in json_content["per_l4_proto_generic_stat_c"]:
            continue

        # retrieve the stat for the considered L4 proto to compute service perc
        l4_protocol_datagramnb_or_bytes = retrieve_stat(
            json_content["per_l4_proto_generic_stat_c"][str(l4_protocol_i)],
            datagramnb_or_bytes)

        # iterate over identified iana services
        for service_both_sides in json_content[
                "per_iana_service_both_sides_generic_stat_c"]:

            # retrieve service name
            service = get_service_name(service_both_sides, l4_protocol_i,
                                       l4_protocol_s, port_file, verbose)
            if service == "-1":
                continue

            # retrieve the stat for the considered service
            service_datagramnb_or_bytes = retrieve_stat(
                json_content["per_iana_service_both_sides_generic_stat_c"]
                [service_both_sides], datagramnb_or_bytes)

            src_host_v = json_content[
                "per_iana_service_both_sides_generic_stat_c"][
                    service_both_sides]["src_hosts"]

            dict_entry = {
                "abs": service_datagramnb_or_bytes,
                "src_host_v": src_host_v
            }

            # update dictionary with service stat
            if service in service_info_v_hm:
                info_v = service_info_v_hm[service]
                info_v.append(dict_entry)
            else:
                service_info_v_hm.update({service: [dict_entry]})

        # flatten info_v of service_info_v_hm and add service perc
        for service, info_v in service_info_v_hm.items():
            total_date_service_datagramnb_or_bytes = sum(
                list(info["abs"] for info in info_v))
            total_date_src_host_nb = len(
                set(src_host for info in info_v
                    for src_host in info["src_host_v"]))

            date_entry = {
                "abs":
                total_date_service_datagramnb_or_bytes,
                "prop":
                total_date_service_datagramnb_or_bytes /
                l4_protocol_datagramnb_or_bytes * 100,
                "src_host_nb":
                total_date_src_host_nb
            }

            if service in service_date_info_hm_hm:
                date_info_hm = service_date_info_hm_hm.get(service)
                assert date_info_hm is not None
                date_info_hm.update({date: date_entry})
            else:
                service_date_info_hm_hm.update({service: {date: date_entry}})

    return service_date_info_hm_hm


def build_datetime64_v_from_log_v(log_v: list) -> list:
    """Transform the list of log to a list of datetime64."""
    return [build_datetime64_from_path(log) for log in sorted(log_v)]


def sort_hm(service_date_info_hm_hm: dict, service_sorting: str) -> dict:
    """Sort services according to the provided sorting method."""
    if service_sorting == "trace-presence":
        # sort by presence in trace
        return dict(sorted(service_date_info_hm_hm.items(), key=lambda k: len(k[1])))

    # else service_sorting == "datagram-number"
    sums = {
        service: sum(int(day["abs"]) for day in dates.values())
        for service, dates in service_date_info_hm_hm.items()
    }
    sorted_protocols = sorted(sums.items(), key=lambda x: x[1])
    return {
        protocol: service_date_info_hm_hm[protocol]
        for protocol, _ in sorted_protocols
    }


def plot_service(reduced_service_date_info_hm_hm: dict, sorted_date_v: list,
                 mode: str, l4_protocol_s: str, outfile_path_pdf: str):
    """The function to plot the services."""
    plt.figure(figsize=(8, 3.5))
    cmap = mpl.colormaps.get_cmap('viridis')
    for service_y, (service, date_info_hm) in enumerate(
            reduced_service_date_info_hm_hm.items()):
        y = [service_y] * len(sorted_date_v)
        x = sorted_date_v

        if mode == 'abs':
            # compute some variables to improve scatter readibility
            abs_max = max(
                list(
                    max(list(info['abs'] for info in date_info_hm.values()))
                    for date_info_hm in
                    reduced_service_date_info_hm_hm.values()))
            coefficient = 5000 if l4_protocol_s == "udp" else 500

            s = [(date_info_hm.get(date)['abs'] / abs_max) *
                 coefficient if date in date_info_hm else 0
                 for date in sorted_date_v]
        else:
            s = [
                date_info_hm.get(date)['prop'] if date in date_info_hm else 0
                for date in sorted_date_v
            ]
        assert (len(x) == len(s))
        edgecolor_v = []
        for date in sorted_date_v:
            if date in date_info_hm:
                if date_info_hm.get(date)['src_host_nb'] == 1:
                    edgecolor_v.append(cmap(0.))
                elif date_info_hm.get(date)['src_host_nb'] >= 10:
                    edgecolor_v.append(cmap(1.))
                else:
                    assert date_info_hm.get(date)['src_host_nb'] > 1
                    edgecolor_v.append(cmap(0.5))
            else:
                edgecolor_v.append(cmap(0.))

        plt.scatter(x,
                    y,
                    s,
                    label=service,
                    edgecolors=edgecolor_v,
                    facecolors='none',
                    linewidths=0.8)

    ax = plt.gca()

    ## Text in the x-axis will be displayed in 'YYYY-mm' format.
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    # Rotates and right-aligns the x labels so they don't crowd each other.
    for label in ax.get_xticklabels(which='major'):
        label.set(rotation=45, ha="right", rotation_mode="anchor")

    cmap_plt = mpl.colors.ListedColormap([cmap(0.), cmap(0.5), cmap(1.)])
    bounds = [1, 2, 10]
    norm = mpl.colors.BoundaryNorm(bounds, cmap_plt.N, extend='max')
    plt.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap_plt),
                 ax=ax,
                 orientation='vertical',
                 label='No. source hosts',
                 extendfrac='auto')
    plt.yticks(range(-1, len(reduced_service_date_info_hm_hm)),
               list([""] + list(reduced_service_date_info_hm_hm.keys())))

    plt.savefig(outfile_path_pdf, bbox_inches='tight', dpi=300)
    plt.cla()


def process(run_dir: str, port_file: str, infilename: str, outfilename: str,
            year_v: list, service_number: int, verbose: bool,
            l4_protocol_s: str, mode: str, service_sorting: str,
            datagramnb_or_bytes: str):
    """The script's core logic."""
    print("process: start")

    # create output dir if does not exist
    outfile_dir = f"{run_dir}/plot/years"
    create_output_dir(outfile_dir)

    # find file path
    log_v = find_log_v(run_dir, year_v, infilename)

    # get the protocol number of the considered L4 protocol
    l4_protocol_i = build_l4_protocol_i(l4_protocol_s)

    # retrieve service info from log file
    service_date_info_hm_hm = build_service_date_info_hm_hm(
        log_v, l4_protocol_s, l4_protocol_i, port_file, verbose,
        datagramnb_or_bytes)

    if len(service_date_info_hm_hm) == 0:
        # early exit
        print(f"process: no IANA service for {l4_protocol_s} protocol")
        print("process: exit")
        return

    # sort services according to the provided sorting method
    sorted_service_date_info_hm_hm = sort_hm(service_date_info_hm_hm,
                                             service_sorting)

    # keep only the top $service_number services
    reduced_service_date_info_hm_hm = dict(
        list(sorted_service_date_info_hm_hm.items())
        [len(sorted_service_date_info_hm_hm) -
         service_number:len(sorted_service_date_info_hm_hm)])

    # plot
    sorted_date_v = build_datetime64_v_from_log_v(log_v)
    outfile_path_pdf = f"{outfile_dir}/{outfilename}_{l4_protocol_s}_top-{service_number}-services_{mode}_sorted-{service_sorting}_{datagramnb_or_bytes}.pdf"
    print("process: outfile_path_pdf: ", outfile_path_pdf)
    plot_service(reduced_service_date_info_hm_hm, sorted_date_v, mode,
                 l4_protocol_s, outfile_path_pdf)

    print("process: end")


def main():
    """The script's entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=str, required=True)
    parser.add_argument("--service-name-port-number-filepath",
                        type=str,
                        required=True)
    parser.add_argument("-i", "--infilename", type=str, required=True)
    parser.add_argument("-o", "--outfilename", type=str, required=True)
    parser.add_argument("--years",
                        type=int,
                        choices=range(2007, 2026),
                        nargs="*",
                        help="Years to analyze. If no value \
                        is provided, all years of the run will be analyzed.",
                        required=False)
    parser.add_argument("--service-number",
                        type=int,
                        required=True,
                        help="Top number of services to plot")
    #parser.add_argument("-v", "--verbose", help="Add info on the plot regarding \
    #                    1) l4_protocol flows without leftmost frag (i.e., no info on ports) \
    #                    and 2) unassigned ports", type=lambda x: bool(strtobool(x)))
    parser.add_argument("-v",
                        "--verbose",
                        help="Add info on the plot regarding \
                        1) l4_protocol flows without leftmost frag (i.e., no info on ports) \
                        and 2) unassigned ports",
                        type=strtobool)
    parser.add_argument("--l4-protocol",
                        type=str,
                        choices=['udp', 'tcp'],
                        required=True)
    parser.add_argument("--mode",
                        type=str,
                        choices=['perc', 'abs'],
                        default='perc')
    parser.add_argument("--service-sorting",
                        type=str,
                        choices=['trace-presence', 'datagram-number'],
                        default='trace-presence')
    parser.add_argument("--datagramNb-or-bytes",
                        type=str,
                        choices=['datagramNb', 'bytes'],
                        required=True)
    args = parser.parse_args()

    run_dir = args.run_dir
    port_file = args.service_name_port_number_filepath
    infilename = args.infilename
    outfilename = args.outfilename
    year_v = args.years
    service_number = args.service_number
    verbose = args.verbose
    l4_protocol = args.l4_protocol
    mode = args.mode
    service_sorting = args.service_sorting
    datagramnb_or_bytes = args.datagramNb_or_bytes
    print("main: run_dir: ", run_dir)
    print("main: port_file: ", port_file)
    print("main: infilename: ", infilename)
    print("main: outfilename: ", outfilename)
    print("main: year_v: ", year_v)
    print("main: service_number: ", service_number)
    print("main: verbose: ", verbose)
    print("main: l4_protocol: ", l4_protocol)
    print("main: mode: ", mode)
    print("main: service_sorting: ", service_sorting)
    print("main: datagramnb_or_bytes: ", datagramnb_or_bytes)

    process(run_dir, port_file, infilename, outfilename, year_v,
            service_number, verbose, l4_protocol, mode, service_sorting,
            datagramnb_or_bytes)


if __name__ == "__main__":
    main()
