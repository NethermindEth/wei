//! API routes for the agent service

use axum::{
    routing::{get, post},
    Router,
};

use crate::{api::handlers, db::Database};

/// Create the API router
#[allow(dead_code)] // TODO: Remove after development phase
pub fn create_router(db: Database) -> Router {
    Router::new()
        .route("/analyze", post(handlers::analyze_proposal))
        .route("/analyses/:id", get(handlers::get_analysis))
        .route(
            "/analyses/proposal/:proposal_id",
            get(handlers::get_proposal_analyses),
        )
        .with_state(db)
}
