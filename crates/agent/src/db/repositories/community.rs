//! Community analysis repository

use serde_json;
use sqlx::PgPool;

use crate::models::deepresearch::{DeepResearchResponse, DeepResearchResult};
use crate::utils::error::Result;

/// Repository for community analysis operations
#[derive(Clone)]
pub struct CommunityRepository {
    pool: PgPool,
}

impl CommunityRepository {
    /// Create a new community repository
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    /// Store a community analysis result in the database
    pub async fn store_analysis(&self, result: &DeepResearchResult) -> Result<()> {
        let response_json = serde_json::to_value(&result.response)?;

        sqlx::query!(
            r#"
            INSERT INTO community_analyses (id, topic, response_data, created_at, expires_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (topic) 
            DO UPDATE SET 
                response_data = EXCLUDED.response_data,
                created_at = EXCLUDED.created_at,
                expires_at = EXCLUDED.expires_at
            "#,
            result.id,
            result.topic,
            response_json,
            result.created_at,
            result.expires_at
        )
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Get a cached community analysis by topic
    pub async fn get_by_topic(&self, topic: &str) -> Result<Option<DeepResearchResult>> {
        let row = sqlx::query!(
            r#"
            SELECT id, topic, response_data, created_at, expires_at
            FROM community_analyses
            WHERE topic = $1 AND expires_at > NOW()
            ORDER BY created_at DESC
            LIMIT 1
            "#,
            topic
        )
        .fetch_optional(&self.pool)
        .await?;

        if let Some(row) = row {
            let response: DeepResearchResponse = serde_json::from_value(row.response_data)?;

            Ok(Some(DeepResearchResult {
                id: row.id,
                topic: row.topic,
                response,
                created_at: row.created_at.unwrap_or_else(chrono::Utc::now),
                expires_at: row.expires_at,
            }))
        } else {
            Ok(None)
        }
    }

    /// Clean up expired entries
    pub async fn cleanup_expired(&self) -> Result<u64> {
        let result = sqlx::query!("DELETE FROM community_analyses WHERE expires_at <= NOW()")
            .execute(&self.pool)
            .await?;

        Ok(result.rows_affected())
    }

    /// Get all cached topics (for debugging/admin purposes)
    pub async fn get_all_topics(&self) -> Result<Vec<String>> {
        let rows = sqlx::query!(
            r#"
            SELECT topic 
            FROM community_analyses 
            WHERE expires_at > NOW()
            ORDER BY created_at DESC
            "#
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(rows.into_iter().map(|row| row.topic).collect())
    }
}
