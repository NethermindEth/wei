//! Utility functions for the agent service
//!
//! This module contains utility functions and types for the agent service,
//! including error handling and validation.

/// Error types and handling
pub mod error;
/// Data validation utilities
pub mod validation;

// TODO: Remove unused import after development phase
#[allow(unused_imports)]
pub use error::AgentError;
