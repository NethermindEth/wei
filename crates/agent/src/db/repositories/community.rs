//! Community analysis repository

use chrono::Utc;
use serde_json;
use sqlx::{query, PgPool, Row};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use crate::models::deepresearch::{DeepResearchResponse, DeepResearchResult};
use crate::utils::error::Result;

/// Repository type for community operations
#[derive(Clone)]
pub enum CommunityRepositoryType {
    /// Database-backed community repository
    Database(PgPool),
    /// In-memory community repository for testing
    Memory(Arc<Mutex<HashMap<String, DeepResearchResult>>>),
}

/// Repository for community analysis operations
#[derive(Clone)]
pub struct CommunityRepository {
    repo_type: CommunityRepositoryType,
}

impl CommunityRepository {
    /// Create a new database-backed community repository
    pub fn new(pool: PgPool) -> Self {
        Self {
            repo_type: CommunityRepositoryType::Database(pool),
        }
    }

    /// Create a new in-memory community repository for testing
    pub fn new_memory() -> Self {
        Self {
            repo_type: CommunityRepositoryType::Memory(Arc::new(Mutex::new(HashMap::new()))),
        }
    }

    /// Store a community analysis result in the database or memory
    pub async fn store_analysis(&self, result: &DeepResearchResult) -> Result<()> {
        match &self.repo_type {
            CommunityRepositoryType::Database(pool) => {
                let response_json = serde_json::to_value(&result.response)?;

                // Use query() instead of query! to avoid SQLx macro issues
                let query_str = r#"
                    INSERT INTO community_analyses (id, topic, response_data, created_at, expires_at)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (topic) 
                    DO UPDATE SET 
                        response_data = EXCLUDED.response_data,
                        created_at = EXCLUDED.created_at,
                        expires_at = EXCLUDED.expires_at
                "#;

                query(query_str)
                    .bind(result.id)
                    .bind(&result.topic)
                    .bind(&response_json)
                    .bind(result.created_at)
                    .bind(result.expires_at)
                    .execute(pool)
                    .await?;
            }
            CommunityRepositoryType::Memory(cache) => {
                let mut cache_map = cache.lock().unwrap();
                cache_map.insert(result.topic.clone(), result.clone());
            }
        }

        Ok(())
    }

    /// Get a cached community analysis by topic
    pub async fn get_by_topic(&self, topic: &str) -> Result<Option<DeepResearchResult>> {
        match &self.repo_type {
            CommunityRepositoryType::Database(pool) => {
                // Use query_as() instead of query! to avoid SQLx macro issues
                let query_str = r#"
                    SELECT id, topic, response_data, created_at, expires_at
                    FROM community_analyses
                    WHERE topic = $1 AND expires_at > NOW()
                    ORDER BY created_at DESC
                    LIMIT 1
                "#;

                // We need to manually handle the row data since we're not using the query! macro
                let row = sqlx::query(query_str)
                    .bind(topic)
                    .fetch_optional(pool)
                    .await?;

                if let Some(row) = row {
                    let id: uuid::Uuid = row.try_get("id")?;
                    let topic: String = row.try_get("topic")?;
                    let response_data: serde_json::Value = row.try_get("response_data")?;
                    let created_at: Option<chrono::DateTime<Utc>> = row.try_get("created_at")?;
                    let expires_at: chrono::DateTime<Utc> = row.try_get("expires_at")?;

                    let response: DeepResearchResponse = serde_json::from_value(response_data)?;

                    Ok(Some(DeepResearchResult {
                        id,
                        topic,
                        response,
                        created_at: created_at.unwrap_or_else(Utc::now),
                        expires_at,
                    }))
                } else {
                    Ok(None)
                }
            }
            CommunityRepositoryType::Memory(cache) => {
                let now = Utc::now();
                let cache_map = cache.lock().unwrap();

                if let Some(result) = cache_map.get(topic) {
                    if result.expires_at > now {
                        Ok(Some(result.clone()))
                    } else {
                        Ok(None)
                    }
                } else {
                    Ok(None)
                }
            }
        }
    }

    /// Clean up expired entries
    pub async fn cleanup_expired(&self) -> Result<u64> {
        match &self.repo_type {
            CommunityRepositoryType::Database(pool) => {
                // Use query() instead of query! to avoid SQLx macro issues
                let query_str = "DELETE FROM community_analyses WHERE expires_at <= NOW()";

                let result = sqlx::query(query_str).execute(pool).await?;

                Ok(result.rows_affected())
            }
            CommunityRepositoryType::Memory(cache) => {
                let now = Utc::now();
                let mut cache_map = cache.lock().unwrap();

                // Find expired entries
                let keys_to_remove: Vec<String> = cache_map
                    .iter()
                    .filter(|(_, entry)| entry.expires_at <= now)
                    .map(|(key, _)| key.clone())
                    .collect();

                // Remove expired entries
                let count = keys_to_remove.len() as u64;
                for key in keys_to_remove {
                    cache_map.remove(&key);
                }

                Ok(count)
            }
        }
    }

    /// Get all cached topics (for debugging/admin purposes)
    pub async fn get_all_topics(&self) -> Result<Vec<String>> {
        match &self.repo_type {
            CommunityRepositoryType::Database(pool) => {
                // Use query() instead of query! to avoid SQLx macro issues
                let query_str = r#"
                    SELECT topic 
                    FROM community_analyses 
                    WHERE expires_at > NOW()
                    ORDER BY created_at DESC
                "#;

                let rows = sqlx::query(query_str).fetch_all(pool).await?;

                // Extract topics from rows
                let mut topics = Vec::new();
                for row in rows {
                    let topic: String = row.try_get("topic")?;
                    topics.push(topic);
                }

                Ok(topics)
            }
            CommunityRepositoryType::Memory(cache) => {
                let now = Utc::now();
                let cache_map = cache.lock().unwrap();

                let active_topics = cache_map
                    .iter()
                    .filter(|(_, entry)| entry.expires_at > now)
                    .map(|(key, _)| key.clone())
                    .collect();

                Ok(active_topics)
            }
        }
    }
}
