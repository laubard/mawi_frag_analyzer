extern crate log;

extern crate clap;

use std::fs;
use std::fs::File;
use std::io;
use std::io::BufReader;
use std::path::Path;
use std::process::exit;

use clap::{Arg, Command};

use libpcap_analyzer::plugins::frag::detailed_t3_stat::T3StatC;
use libpcap_analyzer::plugins::frag::generic_stat::GenericFragStat;


fn main() -> io::Result<()> {
  env_logger::init();

  let matches = Command::new("generate-generic-frag-stats")
      .version("0.1")
      .author("Lucas Aubard <lucas.aubard@irisa.fr>")
      .about("Generate generic-frag-stats.json from extended-three-tuple-frag-stat logs")
      .arg(
        Arg::new("log-path")
        .short('p')
        .long("log-path")
        .required(true)
      )
      .arg(
        Arg::new("outfile-path")
            .short('o')
            .long("outfile-path")
            .required(true)
    )
    .get_matches();

  let log_path_s = match matches.get_one::<String>("log-path") {
    Some(s) => s,
    None => {
        eprintln!("No log path provided.");
        exit(-1);
    }
  };
  println!("log_path_s: {}", log_path_s);
  let log_path = Path::new(log_path_s);

  let outfile_path_s = match matches.get_one::<String>("outfile-path") {
    Some(s) => s,
    None => {
        eprintln!("No oufile path provided");
        exit(-1);
    }
  };
  println!("outfile_path_s: {}", outfile_path_s);
  let outfile_path = Path::new(outfile_path_s);

  println!("Reading log json file");
  let file = File::open(log_path)?;
  let reader = BufReader::new(file);
  let t3_stat_c: T3StatC = serde_json::from_reader(reader)?;

  let generic_frag_stat = GenericFragStat::of_t3_stat_c(t3_stat_c);

  println!("Exporting frag_size_stat");
  let json_string: String = serde_json::to_string_pretty(&generic_frag_stat)?;
  fs::write(outfile_path, json_string).expect("Unable to write file");

  Ok(())

}