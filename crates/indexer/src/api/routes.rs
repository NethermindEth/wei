//! API routes for the indexer service

use axum::{
    routing::{get, post},
    Router,
};

use crate::{api::handlers, db::Database};

/// Create the API router
#[allow(dead_code)] // TODO: Remove after development phase
pub fn create_router(db: Database) -> Router {
    Router::new()
        .route("/health", get(handlers::health))
        .route("/proposals/:id", get(handlers::get_proposal_by_id))
        .route(
            "/proposals/network/:network",
            get(handlers::get_proposals_by_network),
        )
        .route("/proposals/search", get(handlers::search_proposals))
        .route("/accounts", get(handlers::get_account_by_address))
        .route("/hooks", post(handlers::register_webhook))
        .with_state(db)
}
