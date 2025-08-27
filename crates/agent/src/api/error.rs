//! Error handling for the API

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
}
