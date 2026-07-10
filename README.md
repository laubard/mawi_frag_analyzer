MAWI_FRAG_ANALYZER
====

MAWI_FRAG_ANALYZER was used to analyze IPv4 fragment characteristics from the MAWI dataset. 
Some of the analyzed characteristics include fragment series structures, original datagram sizes, and upper-layer protocols. 
We also used it to evaluate the traffic compliance with the RFC 6864 requirement regarding host rate limitation. 
Check our paper for more details on the results [https://tma.ifip.org/2026/wp-content/uploads/sites/15/2026/06/tma2026-final40.pdf](https://tma.ifip.org/2026/wp-content/uploads/sites/15/2026/06/tma2026-final40.pdf). 


# Installation

Note: these commands are specific to the Ubuntu distribution, please change them if you use another OS.

    $ sudo apt-get install capinfos tcpdump zcat xzcat lz4cat zstdcat

## Rust toolchain

    $ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

See [https://rustup.rs/](https://rustup.rs/) for more details.

Add the path to the cargo executable in your PATH environment variable. Its usual location is ~/.cargo/bin/.

WARNING: it is strongly advised to not do this as root.

## Build pcap-analyzer (reassembly engine and frag log provider)

At the root of the project:
    $ cd tools 
    $ git clone https://github.com/laubard/pcap-analyzer
    $ cd pcap-analyzer 
    $ cargo build

## Build mawi-frag-analyzer-rs (frag log analyzer)

At the root of the project:
    $ cd tools/mawi_frag_analyzer_rs
    $ cargo build

## Python (analysis scripts)

Use a dedicated venv for the project.
At the root of the project:
    $ python -m venv mfa_venv
    $ source mfa_venv/bin/activate
    $ pip install matplotlib pandas numpy portion


# Command files in commands/

Full commands are located in the ./commands directory. 
They should be executed in the specified order.

## Set environment variables

To execute the provided commands, you need to set the following environment variables:
- MAWI_FRAG_ANALYZER_PATH: the root of this project
- PCAP_ANALYZER_PATH: the root of the pcap-analyzer tool (which should be located in ./tools/pcap-analyzer)
- MAWI_DATA_PATH: the directory where PCAP compressed files are stored
- OUTPUT_DATA_PATH: a directory with enough space to temporarily store decompressed PCAP files
- run_dir_pcap_analyzer: where the output files related to pcap-analyzer are stored. It should be set after command 01.A.   
- run_dir_capinfos: where the output files related to capinfos are stored. It should be set after command 02.A.   

# License

Licensed under either of

 * Apache License, Version 2.0
   ([LICENSE-APACHE](LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
 * MIT license
   ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

at your option.

# Related TMA'26 publication

* A longitudinal study of IPv4 fragmentation characteristics in Internet traffic
* Lucas Aubard, Kensuke Fukuda, Johan Mazel, Gilles Guette, Pierre Chifflier 
* DOI TODO 
* [https://tma.ifip.org/2026/wp-content/uploads/sites/15/2026/06/tma2026-final40.pdf](https://tma.ifip.org/2026/wp-content/uploads/sites/15/2026/06/tma2026-final40.pdf)

```
@inproceedings{aubard2026longitudinal,
  title={{A longitudinal study of IPv4 fragmentation characteristics in Internet traffic}},
  author={Aubard, Lucas and Fukuda, Kensuke and Mazel, Johan and Guette, Gilles and Chifflier, Pierre},
  booktitle={TMA},
  year={2026}
}
```
