//! API handlers for the indexer service

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};

use crate::{db::Database, models::Proposal};

/// Health check endpoint
pub async fn health() -> StatusCode {
    StatusCode::OK
}

/// Get proposal by ID
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn get_proposal_by_id(
    Path(id): Path<String>,
    State(_db): State<Database>,
) -> Result<Json<Proposal>, StatusCode> {
    // TODO: Implement proposal retrieval by ID
    todo!("Implement get_proposal_by_id")
}

/// Get proposals by network
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn get_proposals_by_network(
    Path(network): Path<String>,
    State(_db): State<Database>,
) -> Result<Json<Vec<Proposal>>, StatusCode> {
    // TODO: Implement proposal retrieval by network
    todo!("Implement get_proposals_by_network")
}

/// Search proposals by description/title
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn search_proposals(
    Query(_params): Query<SearchParams>,
    State(_db): State<Database>,
) -> Result<Json<Vec<Proposal>>, StatusCode> {
    // TODO: Implement proposal search
    todo!("Implement search_proposals")
}

/// Get account by address
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn get_account_by_address(
    Query(_params): Query<AccountParams>,
    State(_db): State<Database>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    // TODO: Implement account retrieval by address
    todo!("Implement get_account_by_address")
}

/// Register webhook
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn register_webhook(
    State(_db): State<Database>,
    Json(_payload): Json<WebhookRegistration>,
) -> Result<Json<WebhookResponse>, StatusCode> {
    // TODO: Implement webhook registration
    todo!("Implement register_webhook")
}

/// Search parameters for proposal queries
#[derive(Deserialize)]
#[allow(dead_code)] // TODO: Remove after development phase
pub struct SearchParams {
    /// Description text to search for
    pub description: Option<String>,
    /// Title text to search for
    pub title: Option<String>,
}

/// Account lookup parameters
#[derive(Deserialize)]
#[allow(dead_code)] // TODO: Remove after development phase
pub struct AccountParams {
    /// Ethereum address to look up
    pub address: Option<String>,
    /// ENS name to look up
    pub ens: Option<String>,
}

/// Webhook registration request
#[derive(Deserialize)]
#[allow(dead_code)] // TODO: Remove after development phase
pub struct WebhookRegistration {
    /// URL to send webhook notifications to
    pub url: String,
    /// List of event types to subscribe to
    pub events: Vec<String>,
}

/// Webhook registration response
#[derive(Serialize)]
pub struct WebhookResponse {
    /// ID of the registered webhook
    pub id: String,
    /// Status of the registration
    pub status: String,
}
