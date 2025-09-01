//! Database repositories for the indexer service
//!
//! This module contains repository implementations for database operations
//! on proposals, actors, protocols, and webhooks.

/// Actor data repository
pub mod actor;
/// Proposal data repository
pub mod proposal;
/// Protocol data repository
pub mod protocol;
/// Webhook data repository
pub mod webhook;
