//! Generic cache repository for all API endpoints

use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sqlx::PgPool;
use uuid::Uuid;

use crate::utils::error::Result;

/// Repository for generic caching operations
#[derive(Clone)]
pub struct CacheRepository {
    pool: PgPool,
}

/// Generic cache entry for storing API responses
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheEntry {
    /// Unique identifier for the cache entry
    pub id: Uuid,
    /// Cache key (unique identifier for the cached data)
    pub cache_key: String,
    /// The cached response data
    pub data: Value,
    /// When this entry was created
    pub created_at: DateTime<Utc>,
    /// When this entry expires
    pub expires_at: DateTime<Utc>,
    /// Optional metadata about the cache entry
    pub metadata: Option<Value>,
}

/// Configuration for cache behavior
#[derive(Debug, Clone)]
pub struct CacheConfig {
    /// Default TTL for cache entries
    pub default_ttl: Duration,
    /// Specific TTL overrides for different cache key patterns
    pub ttl_overrides: Vec<(String, Duration)>,
}

impl Default for CacheConfig {
    fn default() -> Self {
        Self {
            default_ttl: Duration::hours(1), // Default 1 hour TTL
            ttl_overrides: vec![
                ("community:".to_string(), Duration::days(1)), // Community analysis cache for 24 hours
                ("proposal:".to_string(), Duration::hours(6)), // Proposal analysis cache for 6 hours
                ("related:".to_string(), Duration::minutes(30)), // Related proposals cache for 30 minutes
            ],
        }
    }
}

impl CacheRepository {
    /// Create a new cache repository
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    /// Store a value in the cache
    pub async fn set<T: Serialize>(
        &self,
        cache_key: &str,
        data: &T,
        config: &CacheConfig,
        metadata: Option<Value>,
    ) -> Result<()> {
        let data_json = serde_json::to_value(data)?;
        let now = Utc::now();

        // Determine TTL based on cache key pattern
        let ttl = config
            .ttl_overrides
            .iter()
            .find(|(pattern, _)| cache_key.starts_with(pattern))
            .map(|(_, ttl)| *ttl)
            .unwrap_or(config.default_ttl);

        let expires_at = now + ttl;
        let id = Uuid::new_v4();

        sqlx::query!(
            r#"
            INSERT INTO cache_entries (id, cache_key, data, created_at, expires_at, metadata)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (cache_key) 
            DO UPDATE SET 
                data = EXCLUDED.data,
                created_at = EXCLUDED.created_at,
                expires_at = EXCLUDED.expires_at,
                metadata = EXCLUDED.metadata
            "#,
            id,
            cache_key,
            data_json,
            now,
            expires_at,
            metadata
        )
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    /// Get a value from the cache
    pub async fn get<T: for<'de> Deserialize<'de>>(&self, cache_key: &str) -> Result<Option<T>> {
        let row = sqlx::query!(
            r#"
            SELECT data
            FROM cache_entries
            WHERE cache_key = $1 AND expires_at > NOW()
            ORDER BY created_at DESC
            LIMIT 1
            "#,
            cache_key
        )
        .fetch_optional(&self.pool)
        .await?;

        if let Some(row) = row {
            let data: T = serde_json::from_value(row.data)?;
            Ok(Some(data))
        } else {
            Ok(None)
        }
    }

    /// Get cache entry with metadata
    pub async fn get_entry(&self, cache_key: &str) -> Result<Option<CacheEntry>> {
        let row = sqlx::query!(
            r#"
            SELECT id, cache_key, data, created_at, expires_at, metadata
            FROM cache_entries
            WHERE cache_key = $1 AND expires_at > NOW()
            ORDER BY created_at DESC
            LIMIT 1
            "#,
            cache_key
        )
        .fetch_optional(&self.pool)
        .await?;

        if let Some(row) = row {
            Ok(Some(CacheEntry {
                id: row.id,
                cache_key: row.cache_key,
                data: row.data,
                created_at: row.created_at.unwrap_or_else(Utc::now),
                expires_at: row.expires_at,
                metadata: row.metadata,
            }))
        } else {
            Ok(None)
        }
    }

    /// Delete a specific cache entry
    pub async fn delete(&self, cache_key: &str) -> Result<bool> {
        let result = sqlx::query!("DELETE FROM cache_entries WHERE cache_key = $1", cache_key)
            .execute(&self.pool)
            .await?;

        Ok(result.rows_affected() > 0)
    }

    /// Delete all cache entries matching a key pattern
    pub async fn delete_pattern(&self, key_pattern: &str) -> Result<u64> {
        let result = sqlx::query!(
            "DELETE FROM cache_entries WHERE cache_key LIKE $1",
            format!("{}%", key_pattern)
        )
        .execute(&self.pool)
        .await?;

        Ok(result.rows_affected())
    }

    /// Clean up expired entries
    pub async fn cleanup_expired(&self) -> Result<u64> {
        let result = sqlx::query!("DELETE FROM cache_entries WHERE expires_at <= NOW()")
            .execute(&self.pool)
            .await?;

        Ok(result.rows_affected())
    }

    /// Get cache statistics
    pub async fn get_stats(&self) -> Result<CacheStats> {
        let row = sqlx::query!(
            r#"
            SELECT 
                COUNT(*) as total_entries,
                COUNT(CASE WHEN expires_at > NOW() THEN 1 END) as active_entries,
                COUNT(CASE WHEN expires_at <= NOW() THEN 1 END) as expired_entries
            FROM cache_entries
            "#
        )
        .fetch_one(&self.pool)
        .await?;

        Ok(CacheStats {
            total_entries: row.total_entries.unwrap_or(0) as u64,
            active_entries: row.active_entries.unwrap_or(0) as u64,
            expired_entries: row.expired_entries.unwrap_or(0) as u64,
        })
    }

    /// Get all active cache keys (for debugging/admin purposes)
    pub async fn get_active_keys(&self) -> Result<Vec<String>> {
        let rows = sqlx::query!(
            r#"
            SELECT cache_key 
            FROM cache_entries 
            WHERE expires_at > NOW()
            ORDER BY created_at DESC
            "#
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(rows.into_iter().map(|row| row.cache_key).collect())
    }
}

/// Cache statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheStats {
    /// Total number of cache entries
    pub total_entries: u64,
    /// Number of active (non-expired) entries
    pub active_entries: u64,
    /// Number of expired entries
    pub expired_entries: u64,
}
