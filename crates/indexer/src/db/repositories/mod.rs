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
// TODO: Remove unused imports after development phase
#[allow(unused_imports)]
pub use actor::ActorRepository;
#[allow(unused_imports)]
pub use proposal::ProposalRepository;
#[allow(unused_imports)]
pub use protocol::ProtocolRepository;
#[allow(unused_imports)]
pub use webhook::WebhookRepository;
