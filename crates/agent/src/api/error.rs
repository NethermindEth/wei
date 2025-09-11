//! Error handling for the API

use crate::models::eip_error::EipError;
use crate::utils::error::Error;
use axum::{
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde::Serialize;

/// API error response structure
#[derive(Serialize)]
pub struct ErrorResponse {
    /// Error message
    pub message: String,
    /// HTTP status code
    pub status: u16,
}

/// Global error handler for API errors
pub struct ApiError {
    /// HTTP status code
    pub status_code: StatusCode,
    /// Error message
    pub message: String,
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        let error_response = ErrorResponse {
            message: self.message,
            status: self.status_code.as_u16(),
        };

        (self.status_code, Json(error_response)).into_response()
    }
}

impl ApiError {
    /// Create a new API error with the given status code and message
    pub fn new(status_code: StatusCode, message: impl Into<String>) -> Self {
        Self {
            status_code,
            message: message.into(),
        }
    }

    /// Create a 400 Bad Request error
    pub fn bad_request(message: impl Into<String>) -> Self {
        Self::new(StatusCode::BAD_REQUEST, message)
    }

    /// Create a 401 Unauthorized error
    pub fn unauthorized(message: impl Into<String>) -> Self {
        Self::new(StatusCode::UNAUTHORIZED, message)
    }

    /// Create a 403 Forbidden error
    pub fn forbidden(message: impl Into<String>) -> Self {
        Self::new(StatusCode::FORBIDDEN, message)
    }

    /// Create a 404 Not Found error
    pub fn not_found(message: impl Into<String>) -> Self {
        Self::new(StatusCode::NOT_FOUND, message)
    }

    /// Create a 500 Internal Server Error
    pub fn internal_error(message: impl Into<String>) -> Self {
        Self::new(StatusCode::INTERNAL_SERVER_ERROR, message)
    }

    /// Create a 405 Method Not Allowed error
    pub fn method_not_allowed(message: impl Into<String>) -> Self {
        Self::new(StatusCode::METHOD_NOT_ALLOWED, message)
    }

    /// Create a 429 Too Many Requests error
    pub fn rate_limited(message: impl Into<String>) -> Self {
        Self::new(StatusCode::TOO_MANY_REQUESTS, message)
    }
}

/// Convert from internal Error to ApiError
impl From<Error> for ApiError {
    fn from(error: Error) -> Self {
        match error {
            // Handle database errors
            Error::Database(e) => ApiError::internal_error(format!("Database error: {}", e)),

            // Handle HTTP request errors
            Error::HttpRequest(e) => ApiError::internal_error(format!("HTTP error: {}", e)),

            // Handle serialization errors
            Error::Serialization(e) => ApiError::internal_error(format!("JSON error: {}", e)),

            // Handle configuration errors
            Error::Configuration(e) => {
                ApiError::internal_error(format!("Configuration error: {}", e))
            }

            // Handle AI service errors
            Error::AIService(msg) => ApiError::internal_error(format!("AI service error: {}", msg)),

            // Handle analysis not found errors
            Error::AnalysisNotFound { id } => {
                ApiError::not_found(format!("Analysis not found: {}", id))
            }

            // Handle webhook errors
            Error::Webhook(msg) => ApiError::internal_error(format!("Webhook error: {}", msg)),

            // Handle authentication errors
            Error::Authentication(msg) => ApiError::unauthorized(msg),

            // Handle OpenRouter errors
            Error::OpenRouter(e) => ApiError::internal_error(format!("OpenRouter error: {}", e)),

            // Handle chat builder errors
            Error::ChatBuilder(e) => ApiError::internal_error(format!("Chat builder error: {}", e)),

            // Handle response errors
            Error::Response(e) => ApiError::internal_error(format!("Response error: {}", e)),

            // Handle internal errors
            Error::Internal(msg) => ApiError::internal_error(msg),

            // Handle EIP-specific errors
            Error::Eip(eip_error) => match eip_error {
                EipError::NotFound(eip_number) => {
                    ApiError::not_found(format!("EIP-{} not found", eip_number))
                }
                EipError::RateLimitExceeded(msg) => ApiError::rate_limited(msg),
                EipError::GitHubError(msg) => ApiError::internal_error(msg),
                EipError::CacheError(msg) => ApiError::internal_error(msg),
                EipError::ParseError(msg) => ApiError::internal_error(msg),
                EipError::NetworkError(msg) => ApiError::internal_error(msg),
                EipError::InvalidEipNumber(msg) => ApiError::bad_request(msg),
                EipError::Timeout(msg) => ApiError::internal_error(msg),
            },
        }
    }
}
