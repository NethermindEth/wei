//! API middleware for the agent service

use axum::{
    extract::{Request, State},
    http::{HeaderMap, StatusCode},
    middleware::Next,
    response::{IntoResponse, Response},
    Json,
};
use serde::Serialize;
use tracing::{debug, info, warn};

use crate::api::routes::AppState;

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

/// Error response structure
#[derive(Serialize)]
pub struct ErrorResponse {
    /// Error message
    pub message: String,
    /// Error code
    pub status: u16,
}

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
) -> Result<Response, impl IntoResponse>
where
    S: Send + Sync,
{
    let path = request.uri().path();

    let api_key = headers
        .get("x-api-key")
        .and_then(|value| value.to_str().ok());

    match validate_api_key(&state, path, api_key) {
        Ok(_) => Ok(next.run(request).await),
        Err(status) => {
            let message = match status {
                StatusCode::UNAUTHORIZED => "API key is required".to_string(),
                StatusCode::FORBIDDEN => "Invalid API key provided".to_string(),
                _ => "Authentication error".to_string(),
            };

            let error_response = ErrorResponse {
                message,
                status: status.as_u16(),
            };

            Err((status, Json(error_response)))
        }
    }
}
