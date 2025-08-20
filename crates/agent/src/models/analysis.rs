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
    /// Structured analysis response
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub structured_response: Option<StructuredAnalysisResponse>,
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

/// Structured response from the AI model
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StructuredAnalysisResponse {
    /// Overall verdict (good or bad)
    pub verdict: String,
    /// Conclusion summary (1-3 sentences)
    pub conclusion: String,
    /// Proposal quality evaluation
    pub proposal_quality: ProposalQuality,
    /// Submitter intentions analysis
    pub submitter_intentions: SubmitterIntentions,
}

/// Proposal quality evaluation
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct ProposalQuality {
    /// Clarity of goals assessment
    pub clarity_of_goals: String,
    /// Completeness of sections assessment
    pub completeness_of_sections: String,
    /// Level of detail assessment
    pub level_of_detail: String,
    /// Assumptions made in the proposal
    pub assumptions_made: Vec<String>,
    /// Missing elements in the proposal
    pub missing_elements: Vec<String>,
    /// Community adaptability assessment
    pub community_adaptability: String,
}

/// Submitter intentions analysis
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct SubmitterIntentions {
    /// Submitter identity information
    pub submitter_identity: String,
    /// Inferred interests of the submitter
    pub inferred_interests: Vec<String>,
    /// Social activity of the submitter
    pub social_activity: Vec<String>,
    /// Strategic positioning of the submitter
    pub strategic_positioning: Vec<String>,
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
