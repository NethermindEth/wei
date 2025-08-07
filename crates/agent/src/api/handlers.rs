//! API handlers for the agent service

use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};

use crate::db::Database;

/// Analyze a proposal
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn analyze_proposal(
    State(_db): State<Database>,
    Json(_payload): Json<AnalyzeRequest>,
) -> Result<Json<AnalyzeResponse>, StatusCode> {
    // TODO: Implement proposal analysis
    todo!("Implement analyze_proposal")
}

/// Get analysis by ID
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn get_analysis(
    Path(id): Path<String>,
    State(_db): State<Database>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    // TODO: Implement analysis retrieval
    todo!("Implement get_analysis")
}

/// Get analyses for a proposal
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn get_proposal_analyses(
    Path(proposal_id): Path<String>,
    State(_db): State<Database>,
) -> Result<Json<Vec<serde_json::Value>>, StatusCode> {
    // TODO: Implement proposal analyses retrieval
    todo!("Implement get_proposal_analyses")
}

/// Request payload for proposal analysis
#[derive(Deserialize)]
#[allow(dead_code)] // TODO: Remove after development phase
pub struct AnalyzeRequest {
    /// ID of the proposal to analyze
    pub proposal_id: String,
    /// Title of the proposal
    pub title: String,
    /// Description of the proposal
    pub description: String,
}

/// Response payload for analysis request
#[derive(Serialize)]
pub struct AnalyzeResponse {
    /// ID of the created analysis
    pub analysis_id: String,
    /// Status of the analysis
    pub status: String,
}
