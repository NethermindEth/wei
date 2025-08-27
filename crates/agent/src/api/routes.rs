//! API routes for the agent service

use axum::{
    extract::FromRef,
    http::{header, Method, StatusCode},
    middleware,
    routing::{get, post},
    Json, Router,
};
use tower_http::{
    cors::{AllowMethods, AllowOrigin, CorsLayer},
    trace::{DefaultMakeSpan, DefaultOnResponse, TraceLayer},
};
use tracing::Level;

use crate::{
    api::{
        error::ErrorResponse,
        handlers,
        middleware::{api_key_auth, handle_error_middleware},
    },
    config::Config,
    AgentService,
};

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

    // Configure CORS
    let cors_allowed_urls = config.cors_allowed_urls();

    // Check if any URL contains a wildcard pattern
    let has_wildcard = cors_allowed_urls.iter().any(|url| url.contains("*"));

    let cors = if has_wildcard {
        // If we have any wildcard patterns, use permissive CORS settings
        // Note: We can't use allow_credentials(true) with AllowOrigin::any()
        CorsLayer::new()
            .allow_origin(AllowOrigin::any())
            .allow_methods(AllowMethods::list([
                Method::GET,
                Method::POST,
                Method::OPTIONS,
            ]))
            .allow_headers([
                header::CONTENT_TYPE,
                header::AUTHORIZATION,
                header::ACCEPT,
                header::HeaderName::from_static("x-api-key"),
            ])
            .expose_headers([header::HeaderName::from_static("x-api-key")])
    } else {
        // Otherwise, use the exact list of allowed origins
        let mut cors_layer = CorsLayer::new();

        // Add each origin to the allowed origins list
        for url in cors_allowed_urls {
            if let Ok(origin) = url.parse() {
                cors_layer = cors_layer.allow_origin(AllowOrigin::exact(origin));
            } else {
                tracing::warn!("Invalid CORS origin: {}", url);
            }
        }

        cors_layer
            .allow_methods(AllowMethods::list([
                Method::GET,
                Method::POST,
                Method::OPTIONS,
            ]))
            .allow_headers([
                header::CONTENT_TYPE,
                header::AUTHORIZATION,
                header::ACCEPT,
                header::HeaderName::from_static("x-api-key"),
            ])
            .expose_headers([header::HeaderName::from_static("x-api-key")])
            .allow_credentials(true)
    };

    // Public routes that don't require authentication
    let public_routes = Router::new().route("/health", get(handlers::health));

    // Protected routes that require API key authentication
    let protected_routes = Router::new()
        .route(
            "/pre-filter",
            post(handlers::analyze_proposal)
                .options(|_: axum::extract::Request| async { "" })
                .get(method_not_allowed_handler)
                .put(method_not_allowed_handler)
                .delete(method_not_allowed_handler)
                .patch(method_not_allowed_handler),
        )
        .route(
            "/pre-filter/:id",
            get(handlers::get_analysis)
                .options(|_: axum::extract::Request| async { "" })
                .post(method_not_allowed_handler)
                .put(method_not_allowed_handler)
                .delete(method_not_allowed_handler)
                .patch(method_not_allowed_handler),
        )
        .route(
            "/pre-filter/proposal/:proposal_id",
            get(handlers::get_proposal_analyses)
                .options(|_: axum::extract::Request| async { "" })
                .post(method_not_allowed_handler)
                .put(method_not_allowed_handler)
                .delete(method_not_allowed_handler)
                .patch(method_not_allowed_handler),
        )
        .route_layer(middleware::from_fn_with_state(
            state.clone(),
            api_key_auth::<AppState>,
        ));

    // Method not allowed handler
    async fn method_not_allowed_handler() -> (StatusCode, Json<ErrorResponse>) {
        let error_response = ErrorResponse {
            message: "Method not allowed".to_string(),
            status: StatusCode::METHOD_NOT_ALLOWED.as_u16(),
        };
        (StatusCode::METHOD_NOT_ALLOWED, Json(error_response))
    }

    // Fallback handler for 404 errors
    let fallback = |_: axum::extract::Request| async {
        let error_response = ErrorResponse {
            message: "Not Found".to_string(),
            status: StatusCode::NOT_FOUND.as_u16(),
        };
        (StatusCode::NOT_FOUND, Json(error_response))
    };

    // Combine routes
    public_routes
        .merge(protected_routes)
        .fallback(fallback)
        // Use a simpler error handling approach
        .layer(axum::error_handling::HandleErrorLayer::new(|_| async {
            let error_response = ErrorResponse {
                message: "Internal Server Error".to_string(),
                status: StatusCode::INTERNAL_SERVER_ERROR.as_u16(),
            };
            (StatusCode::INTERNAL_SERVER_ERROR, Json(error_response))
        }))
        .layer(middleware::from_fn(handle_error_middleware))
        .layer(cors)
        .layer(tracing_layer)
        .with_state(state)
}
