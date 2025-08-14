use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use uuid::Uuid;

/// Represents an analysis of a proposal
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Analysis {
    /// Unique identifier for the analysis
    #[schema(example = "123e4567-e89b-12d3-a456-426614174000")]
    pub id: Uuid,
    /// ID of the proposal being analyzed
    #[schema(example = "proposal_123")]
    pub proposal_id: String,
    /// Analysis result
    pub result: AnalysisResult,
    /// Confidence score (0.0 to 1.0)
    #[schema(example = 0.85)]
    pub confidence: f64,
    /// Detailed analysis text
    #[schema(
        example = "This proposal demonstrates strong governance practices with clear objectives and reasonable risk assessment."
    )]
    pub details: String,
    /// Creation timestamp
    #[schema(example = "2024-01-15T10:30:00Z")]
    pub created_at: DateTime<Utc>,
}

/// Result of proposal analysis
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
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
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ProposalAnalysis {
    /// The analysis
    pub analysis: Analysis,
    /// Proposal metadata
    pub proposal_metadata: ProposalMetadata,
}

/// Metadata about the proposal being analyzed
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ProposalMetadata {
    /// Proposal title
    #[schema(example = "Increase Staking Rewards")]
    pub title: String,
    /// Proposal description
    #[schema(
        example = "This proposal aims to increase the reward rate for stakers from 5% to 7% to incentivize more participation in the protocol."
    )]
    pub description: String,
    /// Protocol ID
    #[schema(example = "uniswap_v3")]
    pub protocol_id: String,
    /// Author address
    #[schema(example = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6")]
    pub author: String,
}
