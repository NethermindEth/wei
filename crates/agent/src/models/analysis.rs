use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Represents an analysis of a proposal
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Analysis {
    /// Unique identifier for the analysis
    pub id: Uuid,
    /// ID of the proposal being analyzed
    pub proposal_id: String,
    /// Analysis result
    pub result: AnalysisResult,
    /// Confidence score (0.0 to 1.0)
    pub confidence: f64,
    /// Detailed analysis text
    pub details: String,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
}

/// Result of proposal analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AnalysisResult {
    /// Proposal is considered good quality
    Good,
    /// Proposal is considered poor quality
    Bad,
    /// Proposal quality is neutral
    Neutral,
    /// Proposal needs manual review
    NeedsReview,
}

/// Complete proposal analysis with metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProposalAnalysis {
    /// The analysis
    pub analysis: Analysis,
    /// Proposal metadata
    pub proposal_metadata: ProposalMetadata,
}

/// Metadata about the proposal being analyzed
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProposalMetadata {
    /// Proposal title
    pub title: String,
    /// Proposal description
    pub description: String,
    /// Protocol ID
    pub protocol_id: String,
    /// Author address
    pub author: String,
}
