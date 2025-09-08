//! Wei Indexer - DAO/Governance proposal indexing service
//!
//! This crate provides functionality to collect and index DAO/Governance proposals
//! from various ecosystems and store them in a database for training AI models.
#![deny(missing_docs)]
// TODO: Remove after development phase
#![allow(dead_code)]

pub mod api;
pub mod config;
pub mod db;
pub mod models;
pub mod services;
pub mod utils;

// Re-export commonly used types
pub use config::Config;
pub use models::{Actor, Proposal, ProtocolId};
