//! Data models for the agent service
//!
//! This module contains the core data structures used by the agent service
//! for representing analyses, proposals, and webhook events.

// TODO: Remove unused imports after development phase
#[allow(unused_imports)]
use chrono::{DateTime, Utc};
#[allow(unused_imports)]
use serde::{Deserialize, Serialize};
#[allow(unused_imports)]
use uuid::Uuid;

/// Analysis data model
pub mod analysis;
/// Proposal data model
pub mod proposal;
/// Related proposals data model
pub mod related_proposals;
/// Webhook event data model
pub mod webhook;

pub use analysis::{Analysis, AnalysisResult};
pub use proposal::Proposal;
pub use related_proposals::{RelatedProposal, RelatedProposalsQuery, RelatedProposalsResponse};
pub use webhook::WebhookEvent;
