//! API handlers for the agent service

use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use serde::{Serialize};

use crate::{api::routes::AppState, models::Proposal, services::agent::AgentServiceTrait};

/// Analyze a proposal
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn analyze_proposal(
    State(state): State<AppState>,
    Json(proposal): Json<Proposal>,
) -> Result<Json<AnalyzeResponse>, StatusCode> {
    let analysis = state.agent_service.analyze_proposal(&proposal).await.map_err(|e| {
        tracing::error!("Error analyzing proposal: {:?}", e);
        StatusCode::INTERNAL_SERVER_ERROR
    })?;

    Ok(Json(AnalyzeResponse {
        analysis,
    }))
}

/// Get analysis by ID
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn get_analysis(
    Path(id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    // TODO: Implement analysis retrieval using state.agent_service
    todo!("Implement get_analysis")
}

/// Get analyses for a proposal
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn get_proposal_analyses(
    Path(proposal_id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<Vec<serde_json::Value>>, StatusCode> {
    // TODO: Implement proposal analyses retrieval using state.agent_service
    todo!("Implement get_proposal_analyses")
}

/// Response payload for analysis request
#[derive(Serialize)]
pub struct AnalyzeResponse {
    /// Analysis result
    pub analysis: String,
}
