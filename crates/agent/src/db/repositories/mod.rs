//! Database repositories for the agent service
//!
//! This module contains repository implementations for database operations
//! on analyses, caching, and webhook events.

/// Analysis data repository
pub mod analysis;
/// Generic cache repository
pub mod cache;
/// Community analysis repository
pub mod community;
/// Webhook event repository
pub mod webhook;

// TODO: Remove unused imports after development phase
#[allow(unused_imports)]
pub use analysis::AnalysisRepository;
#[allow(unused_imports)]
pub use cache::CacheRepository;
#[allow(unused_imports)]
pub use community::CommunityRepository;
#[allow(unused_imports)]
pub use webhook::WebhookRepository;
