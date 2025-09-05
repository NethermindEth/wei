//! Data models for the agent service
//!
//! This module contains the core data structures used by the agent service
//! for representing analyses, proposals, and webhook events.

/// Analysis data model
pub mod analysis;
/// Deep research data model
pub mod deepresearch;
/// Health check response model
pub mod health;
/// Proposal data model
pub mod proposal;
/// Roadmap data model
pub mod roadmap;
/// Webhook event data model
pub mod webhook;

pub use analysis::{Analysis, AnalysisResult, AnalyzeResponse, StructuredAnalysisResponse};
pub use deepresearch::{
    DeepResearchApiResponse, DeepResearchRequest, DeepResearchResponse, DeepResearchResult,
    DiscussionResource,
};
pub use health::HealthResponse;
pub use proposal::Proposal;
pub use roadmap::{RoadmapApiResponse, RoadmapRequest, RoadmapResponse, RoadmapResult};
pub use webhook::WebhookEvent;
