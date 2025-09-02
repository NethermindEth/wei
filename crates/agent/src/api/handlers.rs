//! API handlers for the agent service

use axum::{
    extract::{Path, State},
    Json,
};
use tracing::error;

use crate::{
    api::{error::ApiError, routes::AppState},
    models::{analysis::AnalyzeResponse, HealthResponse, Proposal},
    services::agent::AgentServiceTrait,
};

use crate::swagger::descriptions;
use chrono::Utc;

/// Health check endpoint
#[utoipa::path(
    get,
    path = "/health",
    responses(
        (status = 200, description = "Service is healthy", body = HealthResponse)
    ),
    tag = "Health",
    summary = "Health check",
    description = descriptions::HANDLER_HEALTH_DESCRIPTION
)]
pub async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok".to_string(),
        timestamp: Utc::now().to_rfc3339(),
    })
}

/// Analyze a proposal
#[utoipa::path(
    post,
    path = "/pre-filter",
    request_body = Proposal,
    responses(
        (status = 200, description = "Analysis completed successfully", body = AnalyzeResponse),
        (status = 400, description = "Invalid request data"),
        (status = 500, description = "Internal server error during analysis")
    ),
    tag = "Analysis",
    summary = "Analyze a DAO/Governance proposal",
    description = descriptions::HANDLER_ANALYSIS_DESCRIPTION
)]
pub async fn analyze_proposal(
    State(state): State<AppState>,
    Json(proposal): Json<Proposal>,
) -> Result<Json<AnalyzeResponse>, ApiError> {
    let structured_response = state
        .agent_service
        .analyze_proposal(&proposal)
        .await
        .map_err(|e| {
            error!("Error analyzing proposal: {:?}", e);
            ApiError::internal_error(format!("Failed to analyze proposal: {}", e))
        })?;

    Ok(Json(AnalyzeResponse {
        structured_response,
    }))
}

/// Get analysis by ID
#[utoipa::path(
    get,
    path = "/pre-filter/{id}",
    params(
        ("id" = String, Path, description = "Unique identifier of the analysis")
    ),
    responses(
        (status = 200, description = "Analysis retrieved successfully", body = serde_json::Value),
        (status = 404, description = "Analysis not found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Analysis",
    summary = "Retrieve analysis by ID",
    description = descriptions::HANDLER_GET_ANALYSIS_DESCRIPTION
)]
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
#[utoipa::path(
    get,
    path = "/pre-filter/proposal/{proposal_id}",
    params(
        ("proposal_id" = String, Path, description = "Unique identifier of the proposal")
    ),
    responses(
        (status = 200, description = "Analyses retrieved successfully", body = Vec<serde_json::Value>),
        (status = 404, description = "Proposal not found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Analysis",
    summary = "Get all analyses for a proposal",
    description = descriptions::HANDLER_GET_PROPOSAL_ANALYSES_DESCRIPTION
)]
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
