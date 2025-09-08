//! Data models for the indexer service
//!
//! This module contains the core data structures used by the indexer service
//! for representing proposals, actors, and protocols.

/// Actor/entity data model  
pub mod actor;
/// Proposal data model
pub mod proposal;
/// Protocol/network data model
pub mod protocol;

pub use actor::Actor;
pub use proposal::Proposal;
pub use protocol::ProtocolId;
