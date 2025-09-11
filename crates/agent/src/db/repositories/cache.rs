//! Generic cache repository for all API endpoints

use crate::utils::error::Result;
use crate::{db_query, db_query_as_one, db_query_as_optional, db_query_as_all};
use chrono::{DateTime, Duration, Utc};
use dashmap::DashMap;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sqlx::{postgres::PgPool, FromRow};
use std::sync::Arc;
use uuid::Uuid;

/// Database row representation of a cache entry
#[derive(FromRow)]
struct CacheEntryRow {
    id: Uuid,
    cache_key: String,
    data: Value,
    created_at: DateTime<Utc>,
    expires_at: DateTime<Utc>,
    metadata: Option<Value>,
}

/// Database row representation of a cache key
#[derive(FromRow)]
struct CacheKeyRow {
    cache_key: String,
}

/// Database row representation of a count result
#[derive(FromRow)]
struct CountRow {
    count: i64,
}

/// Cache store implementation type
/// 
/// This enum replaces the trait-based approach to avoid issues with async generic methods
/// in trait objects. It provides a concrete type for the cache store implementation.
#[derive(Clone)]
pub enum CacheStoreImpl {
    /// Database-backed cache store implementation
    Database(DbCacheStore),
    /// In-memory cache store implementation
    Memory(MemoryCacheStore),
}

/// Database implementation of cache store
#[derive(Clone)]
pub struct DbCacheStore {
    pool: PgPool,
}

impl DbCacheStore {
    /// Create a new database cache store
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }
}

/// In-memory implementation of cache store using DashMap for concurrent access
#[derive(Clone)]
pub struct MemoryCacheStore {
    // DashMap provides concurrent access without explicit locking
    cache: Arc<DashMap<String, CacheEntry>>,
}

impl MemoryCacheStore {
    /// Create a new in-memory cache store
    pub fn new() -> Self {
        Self {
            cache: Arc::new(DashMap::new()),
        }
    }
}

/// Repository for generic caching operations
#[derive(Clone)]
pub struct CacheRepository {
    store: CacheStoreImpl,
}

impl CacheRepository {
    /// Create a new database-backed cache repository
    pub fn new(pool: PgPool) -> Self {
        Self {
            store: CacheStoreImpl::Database(DbCacheStore::new(pool)),
        }
    }

    /// Create a new in-memory cache repository for testing
    pub fn new_memory() -> Self {
        Self {
            store: CacheStoreImpl::Memory(MemoryCacheStore::new()),
        }
    }

    /// Store a value in the cache
    pub async fn set<T: Serialize + Sync>(
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

        match &self.store {
            CacheStoreImpl::Database(store) => {
                // Insert or update the cache entry
                let query_str = r#"
                    INSERT INTO cache_entries (id, cache_key, data, created_at, expires_at, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (cache_key) 
                    DO UPDATE SET 
                        data = EXCLUDED.data,
                        created_at = EXCLUDED.created_at,
                        expires_at = EXCLUDED.expires_at,
                        metadata = EXCLUDED.metadata
                    "#;
                
                let metadata_json = serde_json::to_value(metadata)?;
                db_query!(
                    &store.pool,
                    query_str,
                    id,
                    cache_key,
                    data_json,
                    now,
                    expires_at,
                    metadata_json
                )?;
            }
            CacheStoreImpl::Memory(store) => {
                let entry = CacheEntry {
                    id,
                    cache_key: cache_key.to_string(),
                    data: data_json,
                    created_at: now,
                    expires_at,
                    metadata,
                };

                // DashMap provides thread-safe access without explicit locking
                store.cache.insert(cache_key.to_string(), entry);
            }
        }

        Ok(())
    }

    /// Get a value from the cache
    pub async fn get<T: for<'de> Deserialize<'de>>(&self, cache_key: &str) -> Result<Option<T>> {
        let entry = self.get_entry(cache_key).await?;

        match entry {
            Some(entry) => {
                let data = serde_json::from_value(entry.data)?;
                Ok(Some(data))
            }
            None => Ok(None),
        }
    }

    /// Get cache entry with metadata
    pub async fn get_entry(&self, cache_key: &str) -> Result<Option<CacheEntry>> {
        let now = Utc::now();

        match &self.store {
            CacheStoreImpl::Database(store) => {
                let query_str = r#"
                    SELECT id, cache_key, data, created_at, expires_at, metadata
                    FROM cache_entries
                    WHERE cache_key = $1 AND expires_at > $2
                    "#;
                
                let row = db_query_as_optional!(CacheEntryRow, &store.pool, query_str, cache_key, now)?;

                match row {
                    Some(row) => Ok(Some(CacheEntry {
                        id: row.id,
                        cache_key: row.cache_key,
                        data: row.data,
                        created_at: row.created_at,
                        expires_at: row.expires_at,
                        metadata: row.metadata,
                    })),
                    None => Ok(None),
                }
            }
            CacheStoreImpl::Memory(store) => {
                // DashMap provides thread-safe access without explicit locking
                if let Some(entry) = store.cache.get(cache_key) {
                    if entry.expires_at > now {
                        return Ok(Some(entry.clone()));
                    }
                }

                Ok(None)
            }
        }
    }

    /// Delete a specific cache entry
    pub async fn delete(&self, cache_key: &str) -> Result<bool> {
        match &self.store {
            CacheStoreImpl::Database(store) => {
                let result = db_query!(&store.pool, "DELETE FROM cache_entries WHERE cache_key = $1", cache_key)?;

                Ok(result.rows_affected() > 0)
            }
            CacheStoreImpl::Memory(store) => {
                // DashMap provides thread-safe access without explicit locking
                let removed = store.cache.remove(cache_key).is_some();
                Ok(removed)
            }
        }
    }

    /// Delete all cache entries matching a key pattern
    pub async fn delete_pattern(&self, key_pattern: &str) -> Result<u64> {
        match &self.store {
            CacheStoreImpl::Database(store) => {
                let pattern = format!("%{}%", key_pattern);
                let result = db_query!(&store.pool, "DELETE FROM cache_entries WHERE cache_key LIKE $1", pattern)?;

                Ok(result.rows_affected())
            }
            CacheStoreImpl::Memory(store) => {
                // DashMap doesn't have a direct retain method like HashMap
                // We need to collect keys first to avoid iterator invalidation
                let keys_to_remove: Vec<String> = store.cache
                    .iter()
                    .filter(|entry| entry.key().contains(key_pattern))
                    .map(|entry| entry.key().clone())
                    .collect();
                
                // Remove the collected keys
                let count = keys_to_remove.len() as u64;
                for key in keys_to_remove {
                    store.cache.remove(&key);
                }
                
                Ok(count)
            }
        }
    }

    /// Clean up expired entries
    pub async fn cleanup_expired(&self) -> Result<u64> {
        let now = Utc::now();

        match &self.store {
            CacheStoreImpl::Database(store) => {
                let result = db_query!(&store.pool, "DELETE FROM cache_entries WHERE expires_at <= $1", now)?;

                Ok(result.rows_affected())
            }
            CacheStoreImpl::Memory(store) => {
                // DashMap doesn't have a direct retain method like HashMap
                // We need to collect keys first to avoid iterator invalidation
                let keys_to_remove: Vec<String> = store.cache
                    .iter()
                    .filter(|entry| entry.value().expires_at <= now)
                    .map(|entry| entry.key().clone())
                    .collect();
                
                // Remove the collected keys
                let count = keys_to_remove.len() as u64;
                for key in &keys_to_remove {
                    store.cache.remove(key);
                }
                
                Ok(count)
            }
        }
    }

    /// Get cache statistics
    pub async fn get_stats(&self) -> Result<CacheStats> {
        let now = Utc::now();

        match &self.store {
            CacheStoreImpl::Database(store) => {
                // Get total count
                let total_count_row = db_query_as_one!(CountRow, &store.pool, "SELECT COUNT(*) as count FROM cache_entries")?;
                let total_count = total_count_row.count as u64;
                
                // Get expired count
                let expired_count_row = db_query_as_one!(CountRow, &store.pool, "SELECT COUNT(*) as count FROM cache_entries WHERE expires_at <= $1", now)?;
                let expired_count = expired_count_row.count as u64;

                let active_count = total_count - expired_count;

                Ok(CacheStats {
                    total_entries: total_count,
                    active_entries: active_count,
                    expired_entries: expired_count,
                })
            }
            CacheStoreImpl::Memory(store) => {
                // DashMap provides thread-safe access without explicit locking
                let total_entries = store.cache.len() as u64;
                
                // Count expired entries
                let expired_entries = store.cache
                    .iter()
                    .filter(|entry| entry.value().expires_at <= now)
                    .count() as u64;
                
                let active_entries = total_entries - expired_entries;

                Ok(CacheStats {
                    total_entries,
                    active_entries,
                    expired_entries,
                })
            }
        }
    }

    /// Get all active cache keys (for debugging/admin purposes)
    pub async fn get_active_keys(&self) -> Result<Vec<String>> {
        let now = Utc::now();

        match &self.store {
            CacheStoreImpl::Database(store) => {
                let query_str = r#"
                    SELECT cache_key
                    FROM cache_entries
                    WHERE expires_at > $1
                    ORDER BY cache_key
                    "#;
                
                let rows = db_query_as_all!(CacheKeyRow, &store.pool, query_str, now)?;

                let active_keys = rows.into_iter().map(|row| row.cache_key).collect();

                Ok(active_keys)
            }
            CacheStoreImpl::Memory(store) => {
                // DashMap provides thread-safe access without explicit locking
                let active_keys: Vec<String> = store.cache
                    .iter()
                    .filter(|entry| entry.value().expires_at > now)
                    .map(|entry| entry.key().clone())
                    .collect();

                Ok(active_keys)
            }
        }
    }
}

/// Cache entry representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheEntry {
    /// Unique identifier
    pub id: Uuid,
    /// Cache key
    pub cache_key: String,
    /// Cached data
    pub data: Value,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    /// Expiration timestamp
    pub expires_at: DateTime<Utc>,
    /// Optional metadata
    pub metadata: Option<Value>,
}

/// Cache configuration
#[derive(Debug, Clone)]
pub struct CacheConfig {
    /// Default time-to-live
    pub default_ttl: Duration,
    /// TTL overrides based on cache key patterns
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

/// Cache statistics
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheStats {
    /// Total number of entries in the cache
    pub total_entries: u64,
    /// Number of active (non-expired) entries
    pub active_entries: u64,
    /// Number of expired entries
    pub expired_entries: u64,
}
