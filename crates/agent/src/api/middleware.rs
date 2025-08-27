//! API middleware for the agent service

use axum::{
    extract::{Request, State},
    http::{HeaderMap, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
    BoxError, Json,
};
use futures::future::FutureExt;
use std::panic::AssertUnwindSafe;
use tracing::{debug, error, info, warn};

use crate::api::{
    error::{ApiError, ErrorResponse},
    routes::AppState,
};

/// Trait for API key validation
///
/// This trait allows us to mock the API key validation logic in tests
pub trait ApiKeyValidator {
    /// Check if API key authentication is enabled
    fn api_key_auth_enabled(&self) -> bool;

    /// Validate if the provided API key is valid
    ///
    /// Returns true if the key is valid, false otherwise
    fn is_valid_api_key(&self, key: &str) -> bool;
}

/// Logging middleware
///
/// This middleware logs incoming requests and outgoing responses
pub async fn logging_middleware(request: Request, next: Next) -> Result<Response, StatusCode> {
    let path = request.uri().path().to_string();
    let method = request.method().clone();
    info!("Request: {} {}", method, path);

    let response = next.run(request).await;

    let status = response.status();
    info!("Response: {} {} {}", method, path, status);

    Ok(response)
}

/// Error handling middleware for catching panics and returning JSON responses
pub async fn handle_error_middleware(request: Request, next: Next) -> Response {
    // Use AssertUnwindSafe to catch panics and convert them to JSON responses
    let result = AssertUnwindSafe(next.run(request)).catch_unwind().await;

    match result {
        Ok(response) => response,
        Err(err) => {
            // Convert panic to a JSON error response
            let message = if let Some(s) = err.downcast_ref::<String>() {
                format!("Internal server error: {}", s)
            } else if let Some(s) = err.downcast_ref::<&str>() {
                format!("Internal server error: {}", s)
            } else {
                "Internal server error".to_string()
            };

            error!("Panic occurred: {}", message);

            let error_response = ErrorResponse {
                message: "Internal Server Error".to_string(),
                status: StatusCode::INTERNAL_SERVER_ERROR.as_u16(),
            };

            (StatusCode::INTERNAL_SERVER_ERROR, Json(error_response)).into_response()
        }
    }
}

/// Handle errors from tower services
pub async fn handle_service_error(err: BoxError) -> impl IntoResponse {
    error!("Service error: {:?}", err);

    let error_response = ErrorResponse {
        message: "Internal Server Error".to_string(),
        status: StatusCode::INTERNAL_SERVER_ERROR.as_u16(),
    };

    (StatusCode::INTERNAL_SERVER_ERROR, Json(error_response))
}

/// Implement ApiKeyValidator for AppState
impl ApiKeyValidator for AppState {
    fn api_key_auth_enabled(&self) -> bool {
        self.config.api_key_auth_enabled
    }

    fn is_valid_api_key(&self, key: &str) -> bool {
        self.config.is_valid_api_key(key)
    }
}

/// Validate an API key against the configuration
///
/// This is a helper function that can be used directly in tests
pub fn validate_api_key<T: ApiKeyValidator>(
    validator: &T,
    path: &str,
    api_key: Option<&str>,
) -> Result<(), StatusCode> {
    if !validator.api_key_auth_enabled() {
        debug!("API key authentication is disabled");
        return Ok(());
    }

    match api_key {
        Some(key) => {
            // Validate API key
            if validator.is_valid_api_key(key) {
                debug!("Valid API key provided");
                Ok(())
            } else {
                warn!("Invalid API key provided");
                Err(StatusCode::FORBIDDEN)
            }
        }
        None => {
            warn!("No API key provided for protected endpoint: {}", path);
            Err(StatusCode::UNAUTHORIZED)
        }
    }
}

// Error response structure moved to api/error.rs

/// API key authentication middleware
///
/// This middleware validates the API key in the request header against the configured API keys.
/// If the API key is valid, the request is allowed to proceed.
/// If the API key is missing or invalid, the request is rejected with an appropriate status code and error message.
/// Public endpoints (e.g., /health) are exempt from API key validation.
pub async fn api_key_auth<S>(
    State(state): State<AppState>,
    headers: HeaderMap,
    request: Request,
    next: Next,
) -> Result<Response, ApiError>
where
    S: Send + Sync,
{
    let path = request.uri().path();

    let api_key = headers
        .get("x-api-key")
        .and_then(|value| value.to_str().ok());

    match validate_api_key(&state, path, api_key) {
        Ok(_) => Ok(next.run(request).await),
        Err(StatusCode::UNAUTHORIZED) => Err(ApiError::unauthorized("API key is required")),
        Err(StatusCode::FORBIDDEN) => Err(ApiError::forbidden("Invalid API key provided")),
        Err(status_code) => Err(ApiError {
            status_code,
            message: "Authentication error".to_string(),
        }),
    }
}
