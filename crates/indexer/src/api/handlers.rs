//! API handlers for the indexer service

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

use crate::{db::Database, models::Proposal};

/// Get proposal by ID
#[utoipa::path(
    get,
    path = "/proposals/{id}",
    params(
        ("id" = String, Path, description = "Unique identifier of the proposal")
    ),
    responses(
        (status = 200, description = "Proposal retrieved successfully", body = Proposal),
        (status = 404, description = "Proposal not found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Proposals",
    summary = "Retrieve proposal by ID",
    description = "Get a specific governance proposal using its unique identifier."
)]
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn get_proposal_by_id(
    Path(id): Path<String>,
    State(_db): State<Database>,
) -> Result<Json<Proposal>, StatusCode> {
    // TODO: Implement proposal retrieval by ID
    todo!("Implement get_proposal_by_id")
}

/// Get proposals by network
#[utoipa::path(
    get,
    path = "/proposals/network/{network}",
    params(
        ("network" = String, Path, description = "Network identifier (e.g., ethereum, polygon)")
    ),
    responses(
        (status = 200, description = "Proposals retrieved successfully", body = Vec<Proposal>),
        (status = 404, description = "Network not found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Proposals",
    summary = "Get proposals by network",
    description = "Retrieve all governance proposals for a specific blockchain network."
)]
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn get_proposals_by_network(
    Path(network): Path<String>,
    State(_db): State<Database>,
) -> Result<Json<Vec<Proposal>>, StatusCode> {
    // TODO: Implement proposal retrieval by network
    todo!("Implement get_proposals_by_network")
}

/// Search proposals by description/title
#[utoipa::path(
    get,
    path = "/proposals/search",
    params(
        ("description" = Option<String>, Query, description = "Description text to search for"),
        ("title" = Option<String>, Query, description = "Title text to search for")
    ),
    responses(
        (status = 200, description = "Search completed successfully", body = Vec<Proposal>),
        (status = 400, description = "Invalid search parameters"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Proposals",
    summary = "Search proposals",
    description = "Search governance proposals by description or title text."
)]
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn search_proposals(
    Query(_params): Query<SearchParams>,
    State(_db): State<Database>,
) -> Result<Json<Vec<Proposal>>, StatusCode> {
    // TODO: Implement proposal search
    todo!("Implement search_proposals")
}

/// Get account by address
#[utoipa::path(
    get,
    path = "/accounts",
    params(
        ("address" = Option<String>, Query, description = "Ethereum address to look up"),
        ("ens" = Option<String>, Query, description = "ENS name to look up")
    ),
    responses(
        (status = 200, description = "Account retrieved successfully", body = serde_json::Value),
        (status = 404, description = "Account not found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Accounts",
    summary = "Get account information",
    description = "Retrieve account information by Ethereum address or ENS name."
)]
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn get_account_by_address(
    Query(_params): Query<AccountParams>,
    State(_db): State<Database>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    // TODO: Implement account retrieval by address
    todo!("Implement get_account_by_address")
}

/// Register webhook
#[utoipa::path(
    post,
    path = "/hooks",
    request_body = WebhookRegistration,
    responses(
        (status = 200, description = "Webhook registered successfully", body = WebhookResponse),
        (status = 400, description = "Invalid webhook data"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Webhooks",
    summary = "Register webhook",
    description = "Register a new webhook to receive notifications about governance events."
)]
#[allow(unused_variables)] // TODO: Remove after development phase
pub async fn register_webhook(
    State(_db): State<Database>,
    Json(_payload): Json<WebhookRegistration>,
) -> Result<Json<WebhookResponse>, StatusCode> {
    // TODO: Implement webhook registration
    todo!("Implement register_webhook")
}

/// Search parameters for proposal queries
#[derive(Deserialize, ToSchema)]
#[schema(description = "Parameters for searching governance proposals")]
#[allow(dead_code)] // TODO: Remove after development phase
pub struct SearchParams {
    /// Description text to search for
    #[schema(example = "staking rewards")]
    pub description: Option<String>,
    /// Title text to search for
    #[schema(example = "Increase Rewards")]
    pub title: Option<String>,
}

/// Account lookup parameters
#[derive(Deserialize, ToSchema)]
#[schema(description = "Parameters for looking up account information")]
#[allow(dead_code)] // TODO: Remove after development phase
pub struct AccountParams {
    /// Ethereum address to look up
    #[schema(example = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6")]
    pub address: Option<String>,
    /// ENS name to look up
    #[schema(example = "vitalik.eth")]
    pub ens: Option<String>,
}

/// Webhook registration request
#[derive(Deserialize, ToSchema)]
#[schema(description = "Request to register a new webhook")]
#[allow(dead_code)] // TODO: Remove after development phase
pub struct WebhookRegistration {
    /// URL to send webhook notifications to
    #[schema(example = "https://api.example.com/webhooks/governance")]
    pub url: String,
    /// List of event types to subscribe to
    #[schema(example = "[\"proposal_created\", \"proposal_voted\", \"proposal_executed\"]")]
    pub events: Vec<String>,
}

/// Webhook registration response
#[derive(Serialize, ToSchema)]
#[schema(description = "Response confirming webhook registration")]
pub struct WebhookResponse {
    /// ID of the registered webhook
    #[schema(example = "webhook_123")]
    pub id: String,
    /// Status of the registration
    #[schema(example = "active")]
    pub status: String,
}
