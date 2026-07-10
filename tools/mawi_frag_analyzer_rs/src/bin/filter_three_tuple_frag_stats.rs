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


fn main() -> io::Result<()> {
  env_logger::init();

  let matches = Command::new("filter-three-tuple-frag-stats")
      .version("0.1")
      .author("Lucas Aubard <lucas.aubard@irisa.fr>")
      .about("Filter three-tuple-frag-stat logs to keep only serie kind flows")
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
      .arg(
        Arg::new("serie-kind")
            .short('k')
            .long("serie-kind")
            .help("Complete | Incomplete | Correct | Duplicate | Overlap | InOrder | ReverseOrder | OutOfOrder")
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

  let serie_kind_s = match matches.get_one::<String>("serie-kind") {
    Some(s) => s,
    None => {
        eprintln!("No serie kind provided.");
        exit(-1);
    }
  };
  println!("serie_kind_s: {}", serie_kind_s);
  let serie_kind = serie_kind_s.parse().expect("Invalid input for SeriesKind");

  println!("Reading log json file");
  let file = File::open(log_path)?;
  let reader = BufReader::new(file);
  let mut t3_stat_c: T3StatC = serde_json::from_reader(reader)?;
  
  let filter_t3_stat_c = T3StatC::filter_series_kind(&mut t3_stat_c,serie_kind);

  println!("Exporting frag_size_stat");
  let json_string: String = serde_json::to_string_pretty(&filter_t3_stat_c)?;
  fs::write(outfile_path, json_string).expect("Unable to write file");

  Ok(())

}