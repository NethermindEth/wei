//! Wei Agent - AI agent for analyzing DAO/Governance proposals
//!
//! This crate provides AI-powered analysis of DAO/Governance proposals
//! to determine their quality and provide insights.
#![deny(missing_docs)]
// TODO: Remove after development phase
#![allow(dead_code)]

pub mod api;
pub mod config;
pub mod db;
pub mod models;
pub mod prompts;
pub mod services;
pub mod swagger;
pub mod utils;

// Re-export commonly used types
pub use crate::services::agent::AgentService;
pub use config::Config;
pub use models::{Analysis, AnalysisResult};
pub use utils::error::{Error, Result};
