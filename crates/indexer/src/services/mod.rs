//! Business logic services for the indexer
//!
//! This module contains the core business logic services for the indexer,
//! including the main indexer service, data source abstractions, and webhook handling.

/// Data source abstractions and implementations
pub mod data_sources;
/// Main indexer service implementation
pub mod indexer;
/// Webhook service for external notifications
pub mod webhook;
