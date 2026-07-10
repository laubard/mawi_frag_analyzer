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
use libpcap_tools::Duration;


fn main() -> io::Result<()> {
  env_logger::init();

  let matches = Command::new("filter-three-tuple-frag-stats")
      .version("0.1")
      .author("Lucas Aubard <lucas.aubard@irisa.fr>")
      .about("Filter three-tuple-frag-stat logs to keep only series that are non active in the first and last seconds")
      .arg(
        Arg::new("log-path")
        .short('p')
        .long("log-path")
        .required(true)
      )
      .arg(
        Arg::new("ts-start-secs")
        .short('s')
        .long("ts-start-secs")
        .required(true)
      )
      .arg(
        Arg::new("ts-start-micros")
        .short('m')
        .long("ts-start-micros")
        .required(true)
      )
      .arg(
        Arg::new("seconds-to-filter")
        .short('f')
        .long("seconds-to-filter")
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

  let ts_start_secs_s = match matches.get_one::<String>("ts-start-secs") {
    Some(s) => s,
    None => {
        eprintln!("No ts-start-secs provided.");
        exit(-1);
    }
  };
  println!("ts_start_secs_s: {}", ts_start_secs_s);
  let ts_start_secs = ts_start_secs_s.parse::<u32>().unwrap();

  let ts_start_micros_s = match matches.get_one::<String>("ts-start-micros") {
    Some(s) => s,
    None => {
        eprintln!("No ts-start-micros provided.");
        exit(-1);
    }
  };
  println!("ts_start_micros_s: {}", ts_start_micros_s);
  let ts_start_micros = ts_start_micros_s.parse::<u32>().unwrap();

  let seconds_to_filter_s = match matches.get_one::<String>("seconds-to-filter") {
    Some(s) => s,
    None => {
        eprintln!("No seconds-to-filter provided.");
        exit(-1);
    }
  };
  println!("seconds_to_filter_s: {}", seconds_to_filter_s);
  let seconds_to_filter = seconds_to_filter_s.parse::<u32>().unwrap();

  println!("Reading log json file");
  let file = File::open(log_path)?;
  let reader = BufReader::new(file);
  let mut t3_stat_c: T3StatC = serde_json::from_reader(reader)?;

  let ts_start = Duration::new(ts_start_secs,ts_start_micros); 
  println!("ts_start: {:?}", ts_start);
  let filter_t3_stat_c = T3StatC::filter_ts_start_end(&mut t3_stat_c,ts_start,seconds_to_filter);

  println!("Exporting frag_size_stat");
  let json_string: String = serde_json::to_string_pretty(&filter_t3_stat_c)?;
  fs::write(outfile_path, json_string).expect("Unable to write file");

  Ok(())

}