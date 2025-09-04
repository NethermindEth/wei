use crate::swagger::descriptions;
use crate::swagger::examples;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use uuid::Uuid;

/// Represents an analysis of a proposal
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = descriptions::ANALYSIS_DESCRIPTION)]
pub struct Analysis {
    /// Unique identifier for the analysis
    #[schema(example = examples::ANALYSIS_ID_EXAMPLE)]
    pub id: Uuid,
    /// ID of the proposal being analyzed
    #[schema(example = examples::PROPOSAL_ID_EXAMPLE)]
    pub proposal_id: String,
    /// Analysis result
    pub result: AnalysisResult,
    /// Confidence score (0.0 to 1.0)
    #[schema(example = examples::ANALYSIS_CONFIDENCE_EXAMPLE)]
    pub confidence: f64,
    /// Detailed analysis text
    #[schema(
        example = examples::ANALYSIS_DETAILS_EXAMPLE
    )]
    pub details: String,
    /// Creation timestamp
    #[schema(example = examples::ANALYSIS_CREATED_AT_EXAMPLE)]
    pub created_at: DateTime<Utc>,
    /// Structured analysis response
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub structured_response: Option<StructuredAnalysisResponse>,
}

/// Result of proposal analysis
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = descriptions::ANALYSIS_RESULT_DESCRIPTION)]
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
#[derive(Debug, Clone, Serialize, Deserialize, Default, ToSchema)]
#[schema(description = descriptions::STRUCTURED_ANALYSIS_RESPONSE_DESCRIPTION)]
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
#[derive(Debug, Clone, Serialize, Deserialize, Default, ToSchema)]
#[schema(description = descriptions::EVALUATION_CATEGORY_DESCRIPTION)]
pub struct EvaluationCategory {
    /// Status of the evaluation: pass, fail, or n/a
    #[schema(example = examples::EVALUATION_CATEGORY_STATUS_EXAMPLE)]
    pub status: String,
    /// Justification for the status (empty for pass/fail, explanation for n/a)
    #[schema(example = examples::EVALUATION_CATEGORY_JUSTIFICATION_EXAMPLE)]
    pub justification: String,
    /// Suggestions for improvement (only provided for fail status)
    #[schema(example = examples::EVALUATION_CATEGORY_SUGGESTIONS_EXAMPLE)]
    pub suggestions: Vec<String>,
}

impl EvaluationCategory {
    /// Creates a new EvaluationCategory with status NotApplicable and a default suggestion
    pub fn na(justification: &str) -> Self {
        Self {
            status: "n/a".to_string(),
            justification: justification.to_string(),
            suggestions: vec!["Please try again".to_string()],
        }
    }
}

// Deprecated structs have been removed
// ProposalQuality and SubmitterIntentions were previously here
// They have been replaced by the new evaluation categories above

/// Complete proposal analysis with metadata
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = descriptions::PROPOSAL_ANALYSIS_DESCRIPTION)]
pub struct ProposalAnalysis {
    /// The analysis
    pub analysis: Analysis,
    /// Proposal metadata
    pub proposal_metadata: ProposalMetadata,
}

/// Metadata about the proposal being analyzed
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = descriptions::PROPOSAL_METADATA_DESCRIPTION)]
pub struct ProposalMetadata {
    /// Proposal title
    #[schema(example = examples::PROPOSAL_METADATA_TITLE_EXAMPLE)]
    pub title: String,
    /// Proposal description
    #[schema(
        example = examples::PROPOSAL_METADATA_DESCRIPTION_EXAMPLE
    )]
    pub description: String,
    /// Protocol ID
    #[schema(example = examples::PROPOSAL_METADATA_PROTOCOL_ID_EXAMPLE)]
    pub protocol_id: String,
    /// Author address
    #[schema(example = examples::PROPOSAL_METADATA_AUTHOR_EXAMPLE)]
    pub author: String,
}

/// Response payload for analysis request
#[derive(Serialize, ToSchema)]
#[schema(description = descriptions::ANALYZE_RESPONSE_DESCRIPTION)]
pub struct AnalyzeResponse {
    /// Structured analysis response
    #[serde(flatten)]
    pub structured_response: StructuredAnalysisResponse,
}
