//! Database repositories for the agent service
//!
//! This module contains repository implementations for database operations
//! on analyses and webhook events.

/// Analysis data repository
pub mod analysis;
/// Webhook event repository
pub mod webhook;

// TODO: Remove unused imports after development phase
#[allow(unused_imports)]
pub use analysis::AnalysisRepository;
#[allow(unused_imports)]
pub use webhook::WebhookRepository;
