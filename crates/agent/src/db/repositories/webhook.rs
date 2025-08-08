//! Webhook repository for database operations

use crate::models::WebhookEvent;
use sqlx::PgPool;

/// Repository for webhook operations
#[allow(dead_code)] // TODO: Remove after development phase
pub struct WebhookRepository {
    pool: PgPool,
}

#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
impl WebhookRepository {
    /// Create a new webhook repository
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    /// Save webhook event
    pub async fn save_event(&self, event: &WebhookEvent) -> Result<(), sqlx::Error> {
        // TODO: Implement save event
        todo!("Implement save_event")
    }

    /// Mark event as processed
    pub async fn mark_processed(&self, id: &str) -> Result<(), sqlx::Error> {
        // TODO: Implement mark processed
        todo!("Implement mark_processed")
    }

    /// Get unprocessed events
    pub async fn get_unprocessed_events(&self) -> Result<Vec<WebhookEvent>, sqlx::Error> {
        // TODO: Implement get unprocessed events
        todo!("Implement get_unprocessed_events")
    }
}
