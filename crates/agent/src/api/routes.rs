//! API routes for the agent service

use axum::{
    routing::{get, post},
    Router,
};
use tower_http::{
    cors::{Any, CorsLayer},
    trace::{DefaultMakeSpan, DefaultOnResponse, TraceLayer},
};
use tracing::Level;
use utoipa::OpenApi;

use crate::{api::handlers, config::Config, AgentService};

/// Handler for OpenAPI specification
async fn openapi_handler() -> axum::Json<utoipa::openapi::OpenApi> {
    axum::Json(crate::api::openapi::ApiDoc::openapi())
}

/// Handler for Swagger UI HTML page
async fn swagger_ui_handler() -> axum::response::Html<&'static str> {
    axum::response::Html(
        r#"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="Wei Agent API Documentation" />
    <title>Wei Agent API - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js" crossorigin></script>
    <script>
        window.onload = () => {
            window.ui = SwaggerUIBundle({
                url: '/api-docs/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "BaseLayout",
                validatorUrl: null,
                docExpansion: "list",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1
            });
        };
    </script>
</body>
</html>
    "#,
    )
}

/// Application state
#[derive(Clone)]
pub struct AppState {
    /// Configuration for the application
    pub config: Config,
    /// Agent service for processing requests
    pub agent_service: AgentService,
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

    Router::new()
        .route("/analyze", post(handlers::analyze_proposal))
        .route("/analyses/:id", get(handlers::get_analysis))
        .route(
            "/analyses/proposal/:proposal_id",
            get(handlers::get_proposal_analyses),
        )
        .route("/api-docs/openapi.json", get(openapi_handler))
        .route("/api-docs", get(swagger_ui_handler))
        .layer(cors)
        .layer(tracing_layer)
        .with_state(state)
}
