//! Business logic services for the agent
//!
//! This module contains the core business logic services for the agent,
//! including the main agent service, AI analysis, caching, and webhook processing.

/// Main agent service implementation
pub mod agent;
/// Cache service for all API endpoints
pub mod cache;
/// Exa search service for finding related proposals
pub mod exa;
/// Webhook service for receiving events
pub mod webhook;

// TODO: Remove unused imports after development phase
#[allow(unused_imports)]
pub use agent::AgentService;
