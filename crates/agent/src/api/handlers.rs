//! API handlers for the agent service

use axum::{
    extract::{Path, Query, State},
    Json,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tracing::error;

use crate::{
    api::{error::ApiError, routes::AppState},
    models::{
        analysis::StructuredAnalysisResponse, DeepResearchApiResponse, DeepResearchRequest,
        Proposal,
    },
    services::{
        agent::AgentServiceTrait,
        cache::{CacheableQuery, CachedQueryInfo},
        exa::{ExaService, RelatedProposal},
    },
};

use chrono::Utc;

/// Health check endpoint
pub async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok".to_string(),
        timestamp: Utc::now().to_rfc3339(),
    })
}

/// Health check response
#[derive(Serialize)]
pub struct HealthResponse {
    /// Service status
    pub status: String,
    /// Current timestamp in RFC3339 format
    pub timestamp: String,
}

/// Analyze a proposal
pub async fn analyze_proposal(
    State(state): State<AppState>,
    Json(proposal): Json<Proposal>,
) -> Result<Json<AnalyzeResponse>, ApiError> {
    let cached_response = state
        .agent_service
        .analyze_proposal(&proposal)
        .await
        .map_err(|e| {
            error!("Error analyzing proposal: {:?}", e);
            ApiError::internal_error(format!("Failed to analyze proposal: {}", e))
        })?;

    Ok(Json(AnalyzeResponse {
        structured_response: cached_response.data,
        from_cache: cached_response.from_cache,
        cache_key: cached_response.cache_key,
    }))
}

/// Get analysis by ID
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn get_analysis(
    Path(id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<serde_json::Value>, ApiError> {
    // TODO: Implement analysis retrieval using state.agent_service
    Err(ApiError::internal_error(
        "Analysis retrieval not yet implemented",
    ))
}

/// Get analyses for a proposal
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub async fn get_proposal_analyses(
    Path(proposal_id): Path<String>,
    State(state): State<AppState>,
) -> Result<Json<Vec<serde_json::Value>>, ApiError> {
    // TODO: Implement proposal analyses retrieval using state.agent_service
    Err(ApiError::internal_error(
        "Proposal analyses retrieval not yet implemented",
    ))
}

/// Response payload for analysis request
#[derive(Serialize)]
pub struct AnalyzeResponse {
    /// Structured analysis response
    #[serde(flatten)]
    pub structured_response: StructuredAnalysisResponse,
    /// Whether this response was served from cache
    pub from_cache: bool,
    /// The cache key for this response
    pub cache_key: String,
}

/// Query parameters for related proposals search
#[derive(Deserialize)]
pub struct RelatedProposalsQuery {
    /// The search query or proposal text to find related proposals for
    pub query: String,
    /// Maximum number of results to return (default: 5, max: 10)
    pub limit: Option<u8>,
}

/// Response payload for related proposals request
#[derive(Serialize, Deserialize, Clone)]
pub struct RelatedProposalsResponse {
    /// List of related proposals found
    pub related_proposals: Vec<RelatedProposal>,
    /// The query that was used for the search
    pub query: String,
}

/// Cached response payload for related proposals request
#[derive(Serialize)]
pub struct RelatedProposalsResponseCached {
    /// List of related proposals found
    pub related_proposals: Vec<RelatedProposal>,
    /// The query that was used for the search
    pub query: String,
    /// Whether this response came from cache
    pub from_cache: bool,
    /// Cache key used for this request
    pub cache_key: String,
}

/// Search for related proposals using Exa with caching
pub async fn search_related_proposals(
    Query(query_params): Query<RelatedProposalsQuery>,
    State(state): State<AppState>,
) -> Result<Json<RelatedProposalsResponseCached>, ApiError> {
    // Check if Exa API key is configured
    let exa_api_key = state
        .config
        .exa_api_key
        .as_ref()
        .ok_or_else(|| ApiError::internal_error("Exa API key not configured"))?;

    // Validate limit parameter
    let limit = query_params.limit.unwrap_or(5).min(10);

    // Create cache query
    let mut query_map = HashMap::new();
    query_map.insert("query".to_string(), query_params.query.clone());
    query_map.insert("limit".to_string(), limit.to_string());

    let cache_query = CacheableQuery {
        endpoint: "related-proposals".to_string(),
        method: "GET".to_string(),
        query_params: query_map,
        body: None,
        user_context: None,
    };

    // Use cache service to get or compute the result
    let cached_response = state
        .cache_service
        .cache_or_compute(&cache_query, || async {
            // Create Exa service instance
            let exa_service = ExaService::new(exa_api_key.clone());

            // Search for related proposals
            let related_proposals = exa_service
                .search_related_proposals(query_params.query.clone(), Some(limit))
                .await
                .map_err(|e| {
                    error!("Error searching for related proposals: {:?}", e);
                    crate::utils::error::Error::Internal(format!(
                        "Failed to search for related proposals: {}",
                        e
                    ))
                })?;

            Ok(RelatedProposalsResponse {
                related_proposals,
                query: query_params.query.clone(),
            })
        })
        .await
        .map_err(|e| {
            error!("Error in related proposals cache operation: {:?}", e);
            ApiError::internal_error(format!("Failed to search for related proposals: {}", e))
        })?;

    let response = RelatedProposalsResponseCached {
        related_proposals: cached_response.data.related_proposals,
        query: cached_response.data.query,
        from_cache: cached_response.from_cache,
        cache_key: cached_response.cache_key,
    };

    Ok(Json(response))
}

/// Analyze community discourse for a protocol/topic
pub async fn analyze_community(
    State(state): State<AppState>,
    Json(request): Json<DeepResearchRequest>,
) -> Result<Json<DeepResearchApiResponse>, ApiError> {
    let cached_response = state
        .agent_service
        .deep_research(&request.topic)
        .await
        .map_err(|e| {
            error!("Error analyzing community: {:?}", e);
            ApiError::internal_error(format!("Failed to analyze community: {}", e))
        })?;

    Ok(Json(DeepResearchApiResponse {
        result: cached_response.data,
        from_cache: cached_response.from_cache,
        created_at: cached_response.created_at,
        expires_at: cached_response.expires_at,
    }))
}

/// Query parameters for getting cached deep research
#[derive(Deserialize)]
pub struct GetDeepResearchQuery {
    /// The topic to search for in cache
    pub topic: String,
}

/// Get cached community analysis results
pub async fn get_community_analysis(
    Query(query_params): Query<GetDeepResearchQuery>,
    State(state): State<AppState>,
) -> Result<Json<Option<DeepResearchApiResponse>>, ApiError> {
    let cached_result = state
        .agent_service
        .get_cached_deep_research(&query_params.topic)
        .await
        .map_err(|e| {
            error!("Error retrieving cached community analysis: {:?}", e);
            ApiError::internal_error(format!(
                "Failed to retrieve cached community analysis: {}",
                e
            ))
        })?;

    let response = cached_result.map(|result| DeepResearchApiResponse {
        result: result.response,
        from_cache: true,
        created_at: result.created_at,
        expires_at: result.expires_at,
    });

    Ok(Json(response))
}

// ===== CACHE MANAGEMENT ENDPOINTS =====

/// Get all cached queries
pub async fn list_cached_queries(
    State(state): State<AppState>,
) -> Result<Json<Vec<CachedQueryInfo>>, ApiError> {
    let cached_queries = state
        .cache_service
        .list_cached_queries()
        .await
        .map_err(|e| {
            error!("Error listing cached queries: {:?}", e);
            ApiError::internal_error(format!("Failed to list cached queries: {}", e))
        })?;

    Ok(Json(cached_queries))
}

/// Request body for cache operations
#[derive(Deserialize)]
pub struct CacheOperationRequest {
    /// The cacheable query to operate on
    pub query: CacheableQuery,
}

/// Response for cache operations
#[derive(Serialize)]
pub struct CacheOperationResponse {
    /// Whether the operation was successful
    pub success: bool,
    /// Optional message
    pub message: String,
    /// The cache key that was operated on
    pub cache_key: String,
}

/// Invalidate a specific cached query
pub async fn invalidate_cache(
    State(state): State<AppState>,
    Json(request): Json<CacheOperationRequest>,
) -> Result<Json<CacheOperationResponse>, ApiError> {
    let cache_key = request.query.cache_key();
    let success = state
        .cache_service
        .invalidate_query(&request.query)
        .await
        .map_err(|e| {
            error!("Error invalidating cache: {:?}", e);
            ApiError::internal_error(format!("Failed to invalidate cache: {}", e))
        })?;

    let message = if success {
        format!(
            "Cache invalidated for query: {}",
            request.query.cache_description()
        )
    } else {
        format!(
            "No cache entry found for query: {}",
            request.query.cache_description()
        )
    };

    Ok(Json(CacheOperationResponse {
        success,
        message,
        cache_key,
    }))
}

/// Refresh (invalidate and recompute) a cached query
/// This endpoint allows the frontend to force refresh any cached query
pub async fn refresh_cache(
    State(state): State<AppState>,
    Json(request): Json<CacheOperationRequest>,
) -> Result<Json<CacheOperationResponse>, ApiError> {
    let cache_key = request.query.cache_key();

    // For now, we'll just invalidate - the next request will recompute
    // TODO: In the future, we could trigger recomputation here
    let success = state
        .cache_service
        .invalidate_query(&request.query)
        .await
        .map_err(|e| {
            error!("Error refreshing cache: {:?}", e);
            ApiError::internal_error(format!("Failed to refresh cache: {}", e))
        })?;

    let message = if success {
        format!(
            "Cache refreshed for query: {} (will be recomputed on next request)",
            request.query.cache_description()
        )
    } else {
        format!(
            "No cache entry found for query: {} (will be computed on next request)",
            request.query.cache_description()
        )
    };

    Ok(Json(CacheOperationResponse {
        success: true, // Always return true since the cache will be fresh on next request
        message,
        cache_key,
    }))
}

/// Get cache statistics
#[derive(Serialize)]
pub struct CacheStatsResponse {
    /// Total number of cache entries
    pub total_entries: u64,
    /// Number of active (non-expired) entries
    pub active_entries: u64,
    /// Number of expired entries
    pub expired_entries: u64,
}

/// Get cache statistics
pub async fn get_cache_stats(
    State(state): State<AppState>,
) -> Result<Json<CacheStatsResponse>, ApiError> {
    let stats = state.cache_service.get_stats().await.map_err(|e| {
        error!("Error getting cache stats: {:?}", e);
        ApiError::internal_error(format!("Failed to get cache stats: {}", e))
    })?;

    Ok(Json(CacheStatsResponse {
        total_entries: stats.total_entries,
        active_entries: stats.active_entries,
        expired_entries: stats.expired_entries,
    }))
}

/// Clean up expired cache entries
#[derive(Serialize)]
pub struct CacheCleanupResponse {
    /// Number of entries that were cleaned up
    pub cleaned_entries: u64,
    /// Success message
    pub message: String,
}

/// Clean up expired cache entries
pub async fn cleanup_cache(
    State(state): State<AppState>,
) -> Result<Json<CacheCleanupResponse>, ApiError> {
    let cleaned_entries = state.cache_service.cleanup_expired().await.map_err(|e| {
        error!("Error cleaning up cache: {:?}", e);
        ApiError::internal_error(format!("Failed to cleanup cache: {}", e))
    })?;

    Ok(Json(CacheCleanupResponse {
        cleaned_entries,
        message: format!("Cleaned up {} expired cache entries", cleaned_entries),
    }))
}
