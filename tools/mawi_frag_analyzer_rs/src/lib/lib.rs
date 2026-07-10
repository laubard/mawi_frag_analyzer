#![deny(/*missing_docs,*/
  unstable_features,
  unused_import_braces, unused_qualifications)]
#![warn(
missing_debug_implementations,
/* missing_docs,
rust_2018_idioms,*/
unreachable_pub
)]
#![forbid(unsafe_code)]
#![deny(broken_intra_doc_links)]

#![deny(clippy::mem_forget)]
#![warn(clippy::all)]

extern crate log;
extern crate env_logger;

extern crate serde;
extern crate serde_json;