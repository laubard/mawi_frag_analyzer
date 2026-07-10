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

  let matches = Command::new("merge-flow-within-time-window")
      .version("0.1")
      .author("Lucas Aubard <lucas.aubard@irisa.fr>")
      .about("Merge FlowStat objects of three-tuple-frag-stat logs that are within the same window time")
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
        Arg::new("time-window")
            .short('t')
            .long("time-window")
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

  let time_window_s = match matches.get_one::<String>("time-window") {
    Some(s) => s,
    None => {
        eprintln!("No time window provided");
        exit(-1);
    }
  };
  println!("time_window_s: {}", time_window_s);
  let time_window_u = match time_window_s.parse::<u32>() {
    Ok(tw) => tw,
    Err(_) => {
      eprintln!("Invalid time window provided (should be u32)");
      exit(-1);
    }
  };
  let time_window_d = Duration::new(time_window_u,0);
  println!("time_window_d: {:?}", time_window_d);

  println!("Reading log json file");
  let file = File::open(log_path)?;
  let reader = BufReader::new(file);
  let mut t3_stat_c: T3StatC = serde_json::from_reader(reader)?;
  
  T3StatC::merge_flow_stat_within_time_window(
    &mut t3_stat_c,
    time_window_d
  );

  println!("Exporting frag_size_stat");
  let json_string: String = serde_json::to_string_pretty(&t3_stat_c)?;
  fs::write(outfile_path, json_string).expect("Unable to write file");

  Ok(())

}