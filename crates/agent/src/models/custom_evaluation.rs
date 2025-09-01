use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Custom evaluation criteria request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustomEvaluationRequest {
    /// The proposal content as a string
    pub content: String,
    /// Custom criteria as plain text (e.g., "I want to see if the proposal has clear milestones")
    pub custom_criteria: String,
}

/// A custom evaluation criterion
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustomCriterion {
    /// Name of the criterion (e.g., "team_background", "popularity_level")
    pub name: String,
    /// Description of what to evaluate
    pub description: String,
    /// Bullet points with specific aspects to check
    pub check_points: Vec<String>,
}

/// Response for custom evaluation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustomEvaluationResponse {
    /// Brief summary of the proposal's main objective and approach
    pub summary: String,
    /// Map of all evaluation categories (both default and custom)
    pub response_map: HashMap<String, EvaluationResult>,
}

/// Result of an evaluation category
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EvaluationResult {
    /// Status of the evaluation: pass, fail, or n/a
    pub status: String,
    /// Justification for the status (empty for pass/fail, explanation for n/a)
    pub justification: String,
    /// Suggestions for improvement (only provided for fail status)
    pub suggestions: Vec<String>,
}
