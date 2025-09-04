//! Health check response model

use serde::Serialize;
use utoipa::ToSchema;

/// Health check response
#[derive(Serialize, ToSchema)]
#[schema(description = "Health check response indicating service status")]
pub struct HealthResponse {
    /// Service status
    #[schema(example = "ok")]
    pub status: String,
    /// Current timestamp in RFC3339 format
    #[schema(example = "2024-01-15T10:30:00Z")]
    pub timestamp: String,
}
