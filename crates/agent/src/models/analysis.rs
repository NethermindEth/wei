use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::models::EvaluationStatus;

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

/// Structured response from the AI model based on standardized evaluation criteria
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StructuredAnalysisResponse {
    /// Brief summary of the proposal's main objective and approach
    pub summary: String,
    /// Goals and motivation evaluation
    pub goals_and_motivation: EvaluationCategory,
    /// Measurable outcomes evaluation
    pub measurable_outcomes: EvaluationCategory,
    /// Budget evaluation
    pub budget: EvaluationCategory,
    /// Technical specifications evaluation
    pub technical_specifications: EvaluationCategory,
    /// Language quality evaluation
    pub language_quality: EvaluationCategory,
}

/// Evaluation category with status, justification and suggestions
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct EvaluationCategory {
    /// Status of the evaluation: pass, fail, or n/a
    pub status: EvaluationStatus,
    /// Justification for the status (empty for pass/fail, explanation for n/a)
    pub justification: String,
    /// Suggestions for improvement (only provided for fail status)
    pub suggestions: Vec<String>,
}

impl EvaluationCategory {
    /// Creates a new EvaluationCategory with status NotApplicable and a default suggestion
    pub fn na(justification: &str) -> Self {
        Self {
            status: EvaluationStatus::NotApplicable,
            justification: justification.to_string(),
            suggestions: vec!["Please try again".to_string()],
        }
    }
}

// Deprecated structs have been removed
// ProposalQuality and SubmitterIntentions were previously here
// They have been replaced by the new evaluation categories above

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
