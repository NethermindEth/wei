//! Generic query-based caching service for all API endpoints

use std::collections::HashMap;
use std::future::Future;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use tracing::debug;

use crate::db::repositories::cache::{CacheConfig, CacheRepository};
use crate::utils::error::Result;

/// Cache service providing high-level caching operations
#[derive(Clone)]
pub struct CacheService {
    repository: CacheRepository,
    config: CacheConfig,
}

/// Generic query structure for caching any API call
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheableQuery {
    /// The API endpoint path
    pub endpoint: String,
    /// HTTP method
    pub method: String,
    /// Query parameters
    pub query_params: HashMap<String, String>,
    /// Request body (for POST requests)
    pub body: Option<Value>,
    /// Optional user context (for user-specific caching)
    pub user_context: Option<String>,
}

impl CacheableQuery {
    /// Create a new cacheable query
    pub fn new(endpoint: &str, method: &str) -> Self {
        Self {
            endpoint: endpoint.to_string(),
            method: method.to_string(),
            query_params: HashMap::new(),
            body: None,
            user_context: None,
        }
    }

    /// Add a query parameter
    pub fn with_param(mut self, key: &str, value: &str) -> Self {
        self.query_params.insert(key.to_string(), value.to_string());
        self
    }

    /// Add multiple query parameters
    pub fn with_params(mut self, params: HashMap<String, String>) -> Self {
        self.query_params.extend(params);
        self
    }

    /// Add a request body
    pub fn with_body<T: Serialize>(mut self, body: T) -> Self {
        match serde_json::to_value(body) {
            Ok(value) => self.body = Some(value),
            Err(e) => {
                // Log the error but continue without body
                tracing::warn!("Failed to serialize body: {}", e);
            }
        }
        self
    }

    /// Add user context
    pub fn with_user_context(mut self, user_context: &str) -> Self {
        self.user_context = Some(user_context.to_string());
        self
    }

    /// Get a human-readable description of the cache query
    pub fn cache_description(&self) -> String {
        let mut desc = format!("{}:{}", self.method, self.endpoint);

        if !self.query_params.is_empty() {
            let params: Vec<String> = self
                .query_params
                .iter()
                .map(|(k, v)| format!("{k}={v}"))
                .collect();
            desc.push_str(&format!(" with params {}", params.join(", ")));
        }

        if self.body.is_some() {
            desc.push_str(" with request body");
        }

        desc
    }

    /// Get the cache key for this query
    pub fn cache_key(&self) -> String {
        self.to_cache_key()
    }

    /// Create a community analysis query
    pub fn community_analysis(topic: &str) -> Self {
        Self::new("/community", "POST").with_param("topic", topic)
    }

    /// Generate a unique cache key for this query
    pub fn to_cache_key(&self) -> String {
        // Create a string representation of the query
        let mut query_string = format!("{}:{}", self.method, self.endpoint);

        // Add sorted query parameters
        let mut params: Vec<(&String, &String)> = self.query_params.iter().collect();
        params.sort_by(|a, b| a.0.cmp(b.0));
        for (key, value) in params {
            query_string.push_str(&format!("&{}={}", key, value));
        }

        // Add body if present
        if let Some(body) = &self.body {
            query_string.push_str(&format!(":{}", body.to_string()));
        }

        // Add user context if present
        if let Some(context) = &self.user_context {
            query_string.push_str(&format!(":user:{}", context));
        }

        // Hash the query string to create a fixed-length key
        let mut hasher = Sha256::new();
        hasher.update(query_string.as_bytes());
        let result = hasher.finalize();
        format!("query:{:x}", result)
    }
}

/// Response with cache metadata
#[derive(Debug, Clone)]
pub struct CachedResponse<T> {
    /// The actual data
    pub data: T,
    /// Whether the data was retrieved from cache
    pub from_cache: bool,
    /// When the data was cached
    pub cached_at: Option<DateTime<Utc>>,
    /// When the cache will expire
    pub expires_at: Option<DateTime<Utc>>,
    /// Additional metadata
    pub metadata: Option<Value>,
}

impl CacheService {
    /// Create a new cache service
    pub fn new(repository: CacheRepository) -> Self {
        Self {
            repository,
            config: CacheConfig::default(),
        }
    }

    /// Set the default TTL for cache entries
    pub fn with_ttl(mut self, ttl_seconds: u32) -> Self {
        // Convert ttl_seconds to Duration
        let duration = chrono::Duration::seconds(ttl_seconds as i64);
        self.config.default_ttl = duration;
        self
    }

    /// Get a cached value or compute it if not found
    pub async fn cache_or_compute<T, F, Fut>(
        &self,
        query: &CacheableQuery,
        compute_fn: F,
    ) -> Result<CachedResponse<T>>
    where
        T: Serialize + for<'de> Deserialize<'de> + Send + Sync,
        F: FnOnce() -> Fut,
        Fut: Future<Output = Result<T>>,
    {
        let cache_key = query.to_cache_key();

        // Try to get from cache first
        if let Some(entry) = self.repository.get_entry(&cache_key).await? {
            debug!("Cache hit for key: {}", cache_key);
            let data: T = serde_json::from_value(entry.data)?;
            return Ok(CachedResponse {
                data,
                from_cache: true,
                cached_at: Some(entry.created_at),
                expires_at: Some(entry.expires_at),
                metadata: entry.metadata,
            });
        }

        debug!("Cache miss for key: {}", cache_key);
        // Compute the value
        let computed_value = compute_fn().await?;
        let metadata = serde_json::json!({
            "query": {
                "endpoint": query.endpoint,
                "method": query.method,
                "params": query.query_params,
                "user_context": query.user_context,
            }
        });

        let metadata_clone = metadata.clone();

        // Store in cache
        self.repository
            .set(&cache_key, &computed_value, &self.config, Some(metadata))
            .await?;

        Ok(CachedResponse {
            data: computed_value,
            from_cache: false,
            cached_at: Some(Utc::now()),
            expires_at: None,
            metadata: Some(metadata_clone),
        })
    }

    /// Invalidate a specific cache entry
    pub async fn invalidate(&self, query: &CacheableQuery) -> Result<bool> {
        let cache_key = query.to_cache_key();
        debug!("Invalidating cache key: {}", cache_key);
        let _ = self.repository.delete(&cache_key).await;
        Ok(true)
    }

    /// Invalidate a specific cache entry (alias for invalidate)
    pub async fn invalidate_query(&self, query: &CacheableQuery) -> Result<bool> {
        self.invalidate(query).await
    }

    /// Delete a specific cache entry by key
    pub async fn delete(&self, cache_key: &str) -> Result<bool> {
        self.repository.delete(cache_key).await
    }

    /// Delete all cache entries matching a pattern
    pub async fn delete_pattern(&self, key_pattern: &str) -> Result<u64> {
        self.repository.delete_pattern(key_pattern).await
    }

    /// List all cached queries
    pub async fn list_cached_queries(&self) -> Result<Vec<CachedQueryInfo>> {
        let keys = self.repository.get_active_keys().await?;
        let mut result = Vec::new();

        for key in keys {
            if let Some(entry) = self.repository.get_entry(&key).await? {
                if let Some(metadata) = entry.metadata {
                    if let Ok(query_info) = serde_json::from_value::<QueryMetadata>(metadata) {
                        result.push(CachedQueryInfo {
                            key,
                            endpoint: query_info.query.endpoint,
                            method: query_info.query.method,
                            params: query_info.query.params,
                            user_context: query_info.query.user_context,
                            created_at: entry.created_at,
                            expires_at: entry.expires_at,
                        });
                    }
                }
            }
        }

        Ok(result)
    }

    /// Refresh a cached value by recomputing it
    pub async fn refresh<T, F, Fut>(
        &self,
        query: &CacheableQuery,
        compute_fn: F,
    ) -> Result<CachedResponse<T>>
    where
        T: Serialize + for<'de> Deserialize<'de> + Send + Sync,
        F: FnOnce() -> Fut,
        Fut: Future<Output = Result<T>>,
    {
        let cache_key = query.to_cache_key();

        // Delete existing entry if any
        self.delete(&cache_key).await?;

        // Compute the value
        let computed_value = compute_fn().await?;
        let metadata = serde_json::json!({
            "query": {
                "endpoint": query.endpoint,
                "method": query.method,
                "params": query.query_params,
                "user_context": query.user_context,
            }
        });

        let metadata_clone = metadata.clone();

        // Store in cache
        self.repository
            .set(&cache_key, &computed_value, &self.config, Some(metadata))
            .await?;

        Ok(CachedResponse {
            data: computed_value,
            from_cache: false,
            cached_at: Some(Utc::now()),
            expires_at: None,
            metadata: Some(metadata_clone),
        })
    }

    /// Get cache statistics
    pub async fn get_stats(&self) -> Result<CacheStats> {
        let repo_stats = self.repository.get_stats().await?;

        Ok(CacheStats {
            total_entries: repo_stats.total_entries,
            active_entries: repo_stats.active_entries,
            expired_entries: repo_stats.expired_entries,
        })
    }

    /// Clean up expired cache entries
    pub async fn cleanup_expired(&self) -> Result<u64> {
        self.repository.cleanup_expired().await
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

/// Information about a cached query
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CachedQueryInfo {
    /// Cache key
    pub key: String,
    /// API endpoint
    pub endpoint: String,
    /// HTTP method
    pub method: String,
    /// Query parameters
    pub params: HashMap<String, String>,
    /// User context
    pub user_context: Option<String>,
    /// When the query was cached
    pub created_at: DateTime<Utc>,
    /// When the cache will expire
    pub expires_at: DateTime<Utc>,
}

/// Query metadata structure
#[derive(Debug, Clone, Serialize, Deserialize)]
struct QueryMetadata {
    query: QueryInfo,
}

/// Query information
#[derive(Debug, Clone, Serialize, Deserialize)]
struct QueryInfo {
    endpoint: String,
    method: String,
    params: HashMap<String, String>,
    user_context: Option<String>,
}
