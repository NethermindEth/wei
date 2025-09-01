//! Data models for the agent service
//!
//! This module contains the core data structures used by the agent service
//! for representing analyses, proposals, and webhook events.

// Module imports and exports

/// Analysis data model
pub mod analysis;
/// Custom evaluation criteria data model
pub mod custom_evaluation;
/// Proposal data model
pub mod proposal;
/// Webhook event data model
pub mod webhook;

pub use analysis::{Analysis, AnalysisResult};
pub use custom_evaluation::{CustomCriterion, CustomEvaluationRequest, CustomEvaluationResponse};
pub use proposal::Proposal;
pub use webhook::WebhookEvent;
