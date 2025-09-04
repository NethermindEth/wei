//! Data models for the agent service
//!
//! This module contains the core data structures used by the agent service
//! for representing analyses, proposals, and webhook events.

// Module imports and exports

/// Analysis data model
pub mod analysis;
/// Custom evaluation criteria data model
pub mod custom_evaluation;
/// Deep research data model
pub mod deepresearch;
/// Health check response model
pub mod health;
/// Proposal data model
pub mod proposal;
/// Webhook event data model
pub mod webhook;

/// Status of an evaluation
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize, Default)]
#[serde(rename_all = "lowercase")]
pub enum EvaluationStatus {
    /// The evaluation passed the criteria
    Pass,
    /// The evaluation failed the criteria
    Fail,
    /// The evaluation criteria is not applicable
    #[default]
    #[serde(rename = "n/a")]
    NotApplicable,
}

/// Re-export common types
pub use custom_evaluation::CustomEvaluationRequest;
pub use custom_evaluation::CustomEvaluationResponse;

pub use analysis::{Analysis, AnalysisResult, AnalyzeResponse, StructuredAnalysisResponse};
pub use deepresearch::{
    DeepResearchApiResponse, DeepResearchRequest, DeepResearchResponse, DeepResearchResult,
    DiscussionResource,
};
pub use health::HealthResponse;
pub use proposal::Proposal;
pub use webhook::WebhookEvent;
