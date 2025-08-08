//! Utility functions for the indexer service
//!
//! This module contains utility functions and types for the indexer service,
//! including error handling, ID generation, and validation.

/// Error types and handling
pub mod error;
/// ID generation utilities
pub mod id;
/// Data validation utilities
pub mod validation;

// TODO: Remove unused imports after development phase
#[allow(unused_imports)]
pub use error::IndexerError;
#[allow(unused_imports)]
pub use id::generate_proposal_id;
