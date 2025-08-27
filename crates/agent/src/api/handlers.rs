//! API handlers for the agent service

use axum::{
    extract::{Path, State},
    Json,
};
use serde::Serialize;

use crate::{
    api::{error::ApiError, routes::AppState},
    models::{analysis::StructuredAnalysisResponse, Proposal},
    services::agent::AgentServiceTrait,
};

use chrono::Utc;

/// Health check endpoint
pub async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok".to_string(),
        timestamp: Utc::now().to_rfc3339(),
    })
}

/// Health check response
#[derive(Serialize)]
pub struct HealthResponse {
    /// Service status
    pub status: String,
    /// Current timestamp in RFC3339 format
    pub timestamp: String,
}

/// Analyze a proposal
pub async fn analyze_proposal(
    State(state): State<AppState>,
    Json(proposal): Json<Proposal>,
) -> Result<Json<AnalyzeResponse>, ApiError> {
    let structured_response = state
        .agent_service
        .analyze_proposal(&proposal)
        .await
        .map_err(|e| {
            tracing::error!("Error analyzing proposal: {:?}", e);
            ApiError::internal_error(format!("Failed to analyze proposal: {}", e))
        })?;

    Ok(Json(AnalyzeResponse {
        structured_response,
    }))
}

/// Get analysis by ID
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn get_analysis(
    Path(id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, ApiError> {
    // TODO: Implement analysis retrieval using state.agent_service
    Err(ApiError::internal_error(
        "Analysis retrieval not yet implemented",
    ))
}

/// Get analyses for a proposal
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn get_proposal_analyses(
    Path(proposal_id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<Vec<serde_json::Value>>, ApiError> {
    // TODO: Implement proposal analyses retrieval using state.agent_service
    Err(ApiError::internal_error(
        "Proposal analyses retrieval not yet implemented",
    ))
}

/// Response payload for analysis request
#[derive(Serialize)]
pub struct AnalyzeResponse {
    /// Structured analysis response
    #[serde(flatten)]
    pub structured_response: StructuredAnalysisResponse,
}
