//! Generic query-based caching service for all API endpoints

use std::collections::HashMap;
use std::future::Future;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use tracing::{debug, warn};

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

    /// Set the request body
    pub fn with_body<T: Serialize>(mut self, body: &T) -> Result<Self> {
        self.body = Some(serde_json::to_value(body)?);
        Ok(self)
    }

    /// Set user context for user-specific caching
    pub fn with_user_context(mut self, user_id: &str) -> Self {
        self.user_context = Some(user_id.to_string());
        self
    }

    /// Generate a unique cache key for this query
    pub fn cache_key(&self) -> String {
        let mut hasher = Sha256::new();

        // Hash the endpoint and method
        hasher.update(self.endpoint.as_bytes());
        hasher.update(self.method.as_bytes());

        // Hash query parameters (sorted for consistency)
        let mut sorted_params: Vec<_> = self.query_params.iter().collect();
        sorted_params.sort_by_key(|(k, _)| *k);
        for (key, value) in sorted_params {
            hasher.update(key.as_bytes());
            hasher.update(value.as_bytes());
        }

        // Hash body if present
        if let Some(ref body) = self.body {
            if let Ok(body_str) = serde_json::to_string(body) {
                hasher.update(body_str.as_bytes());
            }
        }

        // Hash user context if present
        if let Some(ref user_context) = self.user_context {
            hasher.update(user_context.as_bytes());
        }

        format!("query:{:x}", hasher.finalize())
    }

    /// Generate a human-readable cache description
    pub fn cache_description(&self) -> String {
        let params_str = if self.query_params.is_empty() {
            String::new()
        } else {
            format!(
                "?{}",
                self.query_params
                    .iter()
                    .map(|(k, v)| format!("{}={}", k, v))
                    .collect::<Vec<_>>()
                    .join("&")
            )
        };

        format!("{} {}{}", self.method, self.endpoint, params_str)
    }
}

/// Response wrapper that includes cache metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CachedResponse<T> {
    /// The actual response data
    #[serde(flatten)]
    pub data: T,
    /// Whether this response was served from cache
    pub from_cache: bool,
    /// When this response was created
    pub created_at: DateTime<Utc>,
    /// When this response expires
    pub expires_at: DateTime<Utc>,
    /// The cache key for this response
    pub cache_key: String,
    /// Human-readable description of the cached query
    pub cache_description: String,
}

impl CacheService {
    /// Create a new cache service
    pub fn new(repository: CacheRepository, config: Option<CacheConfig>) -> Self {
        Self {
            repository,
            config: config.unwrap_or_default(),
        }
    }

    /// Cache or retrieve a value using a query
    /// If the value exists in cache and is not expired, it's returned
    /// Otherwise, the provided closure is executed and its result is cached
    pub async fn cache_or_compute<T, F, Fut>(
        &self,
        query: &CacheableQuery,
        compute_fn: F,
    ) -> Result<CachedResponse<T>>
    where
        T: Serialize + for<'de> Deserialize<'de> + Clone,
        F: FnOnce() -> Fut,
        Fut: Future<Output = Result<T>>,
    {
        let cache_key = query.cache_key();
        debug!("Checking cache for query: {}", query.cache_description());

        // Try to get from cache first
        if let Some(entry) = self.repository.get_entry(&cache_key).await? {
            debug!("Cache hit for query: {}", query.cache_description());

            let cached_data: T = serde_json::from_value(entry.data)?;
            return Ok(CachedResponse {
                data: cached_data,
                from_cache: true,
                created_at: entry.created_at,
                expires_at: entry.expires_at,
                cache_key: cache_key.clone(),
                cache_description: query.cache_description(),
            });
        }

        debug!(
            "Cache miss for query: {}, computing value",
            query.cache_description()
        );

        // Cache miss - compute the value
        let computed_value = compute_fn().await?;
        let created_at = Utc::now();

        // Determine expiry based on endpoint pattern
        let ttl = self
            .config
            .ttl_overrides
            .iter()
            .find(|(pattern, _)| query.endpoint.starts_with(pattern))
            .map(|(_, ttl)| *ttl)
            .unwrap_or(self.config.default_ttl);

        let expires_at = created_at + ttl;

        // Store in cache with query metadata
        let metadata = serde_json::to_value(query)?;
        if let Err(e) = self
            .repository
            .set(&cache_key, &computed_value, &self.config, Some(metadata))
            .await
        {
            warn!(
                "Failed to cache value for query {}: {}",
                query.cache_description(),
                e
            );
            // Don't fail the entire request if caching fails
        }

        Ok(CachedResponse {
            data: computed_value,
            from_cache: false,
            created_at,
            expires_at,
            cache_key,
            cache_description: query.cache_description(),
        })
    }

    /// Refresh (invalidate and recompute) a cached query
    pub async fn refresh_query<T, F, Fut>(
        &self,
        query: &CacheableQuery,
        compute_fn: F,
    ) -> Result<CachedResponse<T>>
    where
        T: Serialize + for<'de> Deserialize<'de> + Clone,
        F: FnOnce() -> Fut,
        Fut: Future<Output = Result<T>>,
    {
        let cache_key = query.cache_key();
        debug!("Refreshing cache for query: {}", query.cache_description());

        // Invalidate existing cache entry
        let _ = self.repository.delete(&cache_key).await;

        // Compute fresh value
        self.cache_or_compute(query, compute_fn).await
    }

    /// Invalidate cache for a specific key
    pub async fn invalidate(&self, cache_key: &str) -> Result<bool> {
        debug!("Invalidating cache for key: {}", cache_key);
        self.repository.delete(cache_key).await
    }

    /// Invalidate all cache entries matching a pattern
    pub async fn invalidate_pattern(&self, key_pattern: &str) -> Result<u64> {
        debug!("Invalidating cache for pattern: {}", key_pattern);
        self.repository.delete_pattern(key_pattern).await
    }

    /// Get all cached queries with their metadata
    pub async fn list_cached_queries(&self) -> Result<Vec<CachedQueryInfo>> {
        let keys = self.repository.get_active_keys().await?;
        let mut cached_queries = Vec::new();

        for key in keys {
            if let Some(entry) = self.repository.get_entry(&key).await? {
                let query_info = if let Some(metadata) = entry.metadata {
                    if let Ok(query) = serde_json::from_value::<CacheableQuery>(metadata) {
                        CachedQueryInfo {
                            cache_key: entry.cache_key,
                            description: query.cache_description(),
                            endpoint: query.endpoint,
                            method: query.method,
                            created_at: entry.created_at,
                            expires_at: entry.expires_at,
                            query_params: query.query_params,
                            user_context: query.user_context,
                        }
                    } else {
                        // Fallback for entries without proper metadata
                        CachedQueryInfo {
                            cache_key: entry.cache_key.clone(),
                            description: format!("Legacy cache entry: {}", entry.cache_key),
                            endpoint: "unknown".to_string(),
                            method: "unknown".to_string(),
                            created_at: entry.created_at,
                            expires_at: entry.expires_at,
                            query_params: HashMap::new(),
                            user_context: None,
                        }
                    }
                } else {
                    // Fallback for entries without metadata
                    CachedQueryInfo {
                        cache_key: entry.cache_key.clone(),
                        description: format!("Legacy cache entry: {}", entry.cache_key),
                        endpoint: "unknown".to_string(),
                        method: "unknown".to_string(),
                        created_at: entry.created_at,
                        expires_at: entry.expires_at,
                        query_params: HashMap::new(),
                        user_context: None,
                    }
                };
                cached_queries.push(query_info);
            }
        }

        // Sort by creation time (newest first)
        cached_queries.sort_by(|a, b| b.created_at.cmp(&a.created_at));

        Ok(cached_queries)
    }

    /// Invalidate cache by query (frontend can call this to refresh specific queries)
    pub async fn invalidate_query(&self, query: &CacheableQuery) -> Result<bool> {
        let cache_key = query.cache_key();
        debug!(
            "Invalidating cache for query: {}",
            query.cache_description()
        );
        self.repository.delete(&cache_key).await
    }

    /// Get cache statistics
    pub async fn get_stats(&self) -> Result<crate::db::repositories::cache::CacheStats> {
        self.repository.get_stats().await
    }

    /// Clean up expired entries
    pub async fn cleanup_expired(&self) -> Result<u64> {
        debug!("Cleaning up expired cache entries");
        self.repository.cleanup_expired().await
    }
}

/// Information about a cached query
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CachedQueryInfo {
    /// The cache key
    pub cache_key: String,
    /// Human-readable description
    pub description: String,
    /// API endpoint
    pub endpoint: String,
    /// HTTP method
    pub method: String,
    /// When this was cached
    pub created_at: DateTime<Utc>,
    /// When this expires
    pub expires_at: DateTime<Utc>,
    /// Query parameters
    pub query_params: HashMap<String, String>,
    /// User context if any
    pub user_context: Option<String>,
}

/// Helper functions for creating common queries
impl CacheableQuery {
    /// Create a query for proposal analysis
    pub fn proposal_analysis(proposal_id: &str) -> Self {
        Self::new("/pre-filter", "POST").with_param("proposal_id", proposal_id)
    }

    /// Create a query for community analysis
    pub fn community_analysis(topic: &str) -> Self {
        Self::new("/community", "POST").with_param("topic", topic)
    }

    /// Create a query for getting community analysis
    pub fn get_community_analysis(topic: &str) -> Self {
        Self::new("/community", "GET").with_param("topic", topic)
    }

    /// Create a query for related proposals search
    pub fn related_proposals(query: &str, limit: Option<u8>) -> Self {
        let mut cacheable_query = Self::new("/related-proposals", "GET").with_param("query", query);

        if let Some(limit) = limit {
            cacheable_query = cacheable_query.with_param("limit", &limit.to_string());
        }

        cacheable_query
    }

    /// Create a query for getting analysis by ID
    pub fn analysis_by_id(analysis_id: &str) -> Self {
        Self::new(&format!("/pre-filter/{}", analysis_id), "GET")
    }

    /// Create a query for getting proposal analyses
    pub fn proposal_analyses(proposal_id: &str) -> Self {
        Self::new(&format!("/pre-filter/proposal/{}", proposal_id), "GET")
    }
}
