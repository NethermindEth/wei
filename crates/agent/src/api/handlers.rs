//! API handlers for the agent service

use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use serde::Serialize;
use utoipa::ToSchema;

use crate::{api::routes::AppState, models::Proposal, services::agent::AgentServiceTrait};

/// Analyze a proposal
#[utoipa::path(
    post,
    path = "/analyze",
    request_body = Proposal,
    responses(
        (status = 200, description = "Analysis completed successfully", body = AnalyzeResponse),
        (status = 400, description = "Invalid request data"),
        (status = 500, description = "Internal server error during analysis")
    ),
    tag = "Analysis",
    summary = "Analyze a DAO/Governance proposal",
    description = "Submit a proposal for AI analysis. The service will evaluate the proposal content and provide insights on governance quality, risks, and recommendations."
)]
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn analyze_proposal(
    State(state): State<AppState>,
    Json(proposal): Json<Proposal>,
) -> Result<Json<AnalyzeResponse>, StatusCode> {
    let analysis = state
        .agent_service
        .analyze_proposal(&proposal)
        .await
        .map_err(|e| {
            tracing::error!("Error analyzing proposal: {:?}", e);
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    Ok(Json(AnalyzeResponse { analysis }))
}

/// Get analysis by ID
#[utoipa::path(
    get,
    path = "/analyses/{id}",
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
    description = "Get a specific analysis result using its unique identifier."
)]
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn get_analysis(
    Path(id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    // TODO: Implement analysis retrieval using state.agent_service
    todo!("Implement get_analysis")
}

/// Get analyses for a proposal
#[utoipa::path(
    get,
    path = "/analyses/proposal/{proposal_id}",
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
    description = "Retrieve all analysis results associated with a specific proposal."
)]
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn get_proposal_analyses(
    Path(proposal_id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<Vec<serde_json::Value>>, StatusCode> {
    // TODO: Implement proposal analyses retrieval using state.agent_service
    todo!("Implement get_proposal_analyses")
}

/// Response payload for analysis request
#[derive(Serialize, ToSchema)]
#[schema(description = "Response containing the AI analysis of a governance proposal")]
pub struct AnalyzeResponse {
    /// Analysis result
    #[schema(
        example = "This proposal appears to be well-structured with clear objectives. The proposed 2% increase in staking rewards could effectively incentivize participation while maintaining protocol sustainability. Key strengths include detailed implementation timeline and quarterly review mechanisms. Consider monitoring the impact on protocol tokenomics and ensuring adequate risk mitigation measures are in place."
    )]
    pub analysis: String,
}
