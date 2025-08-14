//! API routes for the indexer service

use axum::{
    routing::{get, post},
    Router,
};
use utoipa::OpenApi;

use crate::{api::handlers, db::Database};

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
    <meta name="description" content="Wei Indexer API Documentation" />
    <title>Wei Indexer API - Swagger UI</title>
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

/// Create the API router
#[allow(dead_code)] // TODO: Remove after development phase
pub fn create_router(db: Database) -> Router {
    Router::new()
        .route("/proposals/:id", get(handlers::get_proposal_by_id))
        .route(
            "/proposals/network/:network",
            get(handlers::get_proposals_by_network),
        )
        .route("/proposals/search", get(handlers::search_proposals))
        .route("/accounts", get(handlers::get_account_by_address))
        .route("/hooks", post(handlers::register_webhook))
        .route("/api-docs/openapi.json", get(openapi_handler))
        .route("/api-docs", get(swagger_ui_handler))
        .with_state(db)
}
