//! OpenAPI handlers for the agent service

use utoipa::OpenApi;

/// Handler for OpenAPI specification
pub async fn openapi_handler() -> axum::Json<utoipa::openapi::OpenApi> {
    axum::Json(crate::swagger::ApiDoc::openapi())
}

const SWAGGER_UI_HTML: &str = include_str!("../../assets/swagger-ui.html");

/// Handler for Swagger UI HTML page
pub async fn swagger_ui_handler() -> axum::response::Html<&'static str> {
    axum::response::Html(SWAGGER_UI_HTML)
}
