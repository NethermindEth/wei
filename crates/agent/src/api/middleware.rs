//! Middleware for the agent API

use axum::{extract::Request, http::StatusCode, middleware::Next, response::Response};

/// Logging middleware
#[allow(dead_code)] // TODO: Remove after development phase
pub async fn logging_middleware(request: Request, next: Next) -> Result<Response, StatusCode> {
    // TODO: Implement request logging
    let response = next.run(request).await;
    Ok(response)
}

/// Authentication middleware
#[allow(dead_code)] // TODO: Remove after development phase
pub async fn auth_middleware(request: Request, next: Next) -> Result<Response, StatusCode> {
    // TODO: Implement authentication
    let response = next.run(request).await;
    Ok(response)
}
