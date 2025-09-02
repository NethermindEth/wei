//! API handlers for the agent service

use axum::{
    extract::{Path, Query, State},
    Json,
};
use serde::{Deserialize, Serialize};
use tracing::error;

use crate::{
    api::{error::ApiError, routes::AppState},
    models::{analysis::StructuredAnalysisResponse, Proposal},
    services::{
        agent::AgentServiceTrait,
        exa::{ExaService, RelatedProposal},
    },
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
            error!("Error analyzing proposal: {:?}", e);
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

/// Query parameters for related proposals search
#[derive(Deserialize)]
pub struct RelatedProposalsQuery {
    /// The search query or proposal text to find related proposals for
    pub query: String,
    /// Maximum number of results to return (default: 5, max: 10)
    pub limit: Option<u8>,
}

/// Response payload for related proposals request
#[derive(Serialize)]
pub struct RelatedProposalsResponse {
    /// List of related proposals found
    pub related_proposals: Vec<RelatedProposal>,
    /// The query that was used for the search
    pub query: String,
}

/// Search for related proposals using Exa
pub async fn search_related_proposals(
    Query(query_params): Query<RelatedProposalsQuery>,
    State(state): State<AppState>,
) -> Result<Json<RelatedProposalsResponse>, ApiError> {
    // Check if Exa API key is configured
    let exa_api_key = state
        .config
        .exa_api_key
        .as_ref()
        .ok_or_else(|| ApiError::internal_error("Exa API key not configured"))?;

    // Validate limit parameter
    let limit = query_params.limit.unwrap_or(5).min(10);

    // Create Exa service instance
    let exa_service = ExaService::new(exa_api_key.clone());

    // Search for related proposals
    let related_proposals = exa_service
        .search_related_proposals(query_params.query.clone(), Some(limit))
        .await
        .map_err(|e| {
            error!("Error searching for related proposals: {:?}", e);
            ApiError::internal_error(format!("Failed to search for related proposals: {}", e))
        })?;

    Ok(Json(RelatedProposalsResponse {
        related_proposals,
        query: query_params.query,
    }))
}
