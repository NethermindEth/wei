//! API routes for the agent service

use axum::{
    routing::{get, post},
    Router,
    middleware,
    extract::FromRef,
};
use tower_http::{
    cors::{Any, CorsLayer},
    trace::{DefaultMakeSpan, DefaultOnResponse, TraceLayer},
};
use tracing::Level;

use crate::{api::{handlers, middleware::api_key_auth}, config::Config, AgentService};

/// Application state
#[derive(Clone)]
pub struct AppState {
    /// Configuration for the application
    pub config: Config,
    /// Agent service for processing requests
    pub agent_service: AgentService,
}

impl FromRef<AppState> for Config {
    fn from_ref(state: &AppState) -> Self {
        state.config.clone()
    }
}

/// Create the API router
pub fn create_router(config: &Config, agent_service: AgentService) -> Router {
    let tracing_layer = TraceLayer::new_for_http()
        .make_span_with(DefaultMakeSpan::new().include_headers(true))
        .on_response(
            DefaultOnResponse::new()
                .include_headers(true)
                .level(Level::INFO),
        );

    let state = AppState {
        config: config.clone(),
        agent_service,
    };

    // Configure CORS for local development
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    // Public routes that don't require authentication
    let public_routes = Router::new()
        .route("/health", get(handlers::health));
    
    // Protected routes that require API key authentication
    let protected_routes = Router::new()
        .route("/analyze", post(handlers::analyze_proposal))
        .route("/analyses/:id", get(handlers::get_analysis))
        .route(
            "/analyses/proposal/:proposal_id",
            get(handlers::get_proposal_analyses),
        )
        .route_layer(middleware::from_fn_with_state(state.clone(), api_key_auth::<AppState>));

    // Combine routes
    public_routes
        .merge(protected_routes)
        .layer(cors)
        .layer(tracing_layer)
        .with_state(state)
}
