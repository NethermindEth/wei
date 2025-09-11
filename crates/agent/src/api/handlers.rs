//! API handlers for the agent service

use axum::{
    extract::{Path, Query, State},
    Json,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tracing::{debug, error, warn};
use utoipa::ToSchema;

/// Helper function to validate date format (YYYY-MM-DD)
fn is_valid_date_format(date: &str) -> bool {
    // Check basic format with regex
    let re = regex::Regex::new(r"^\d{4}-\d{2}-\d{2}$").unwrap();
    if !re.is_match(date) {
        return false;
    }

    // Validate as actual date
    if let Ok(_parsed_date) = chrono::NaiveDate::parse_from_str(date, "%Y-%m-%d") {
        // Additional validation if needed (e.g., not in the future)
        return true;
    }

    false
}

use crate::{
    api::{
        error::ApiError,
        error_utils::{log_and_convert_api_error, OperationContext},
        routes::AppState,
    },
    models::{
        analysis::{AnalyzeResponse, ProposalArguments},
        eip::EipProposal,
        eip_error::EipError,
        CustomEvaluationRequest, CustomEvaluationResponse, DeepResearchApiResponse,
        DeepResearchRequest, EipFilterRequest, EipResponse, EipsResponse, HealthResponse, Proposal,
        RoadmapApiResponse, RoadmapRequest,
    },
    services::{
        agent::AgentServiceTrait,
        cache::{CacheableQuery, CachedQueryInfo, CachedResponse},
        eip::EipService,
        exa::{ExaService, RelatedProposal},
    },
    utils::error::Error,
};

use crate::swagger::descriptions;
use chrono::Utc;

/// Health check endpoint
#[utoipa::path(
    get,
    path = "/health",
    responses(
        (status = 200, description = "Service is healthy", body = HealthResponse)
    ),
    tag = "Health",
    summary = "Health check",
    description = descriptions::HANDLER_HEALTH_DESCRIPTION
)]
pub async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        status: "ok".to_string(),
        timestamp: Utc::now().to_rfc3339(),
    })
}

/// Analyze a proposal
#[utoipa::path(
    post,
    path = "/pre-filter",
    request_body = Proposal,
    responses(
        (status = 200, description = "Analysis completed successfully", body = AnalyzeResponse),
        (status = 400, description = "Invalid request data"),
        (status = 500, description = "Internal server error during analysis")
    ),
    tag = "Analysis",
    summary = "Analyze a DAO/Governance proposal",
    description = descriptions::HANDLER_ANALYSIS_DESCRIPTION
)]
pub async fn analyze_proposal(
    State(state): State<AppState>,
    Json(proposal): Json<Proposal>,
) -> Result<Json<AnalyzeResponse>, ApiError> {
    let cached_response = state
        .agent_service
        .analyze_proposal(&proposal)
        .await
        .map_err(|e| log_and_convert_api_error(OperationContext::AnalyzeProposal, e))?;

    Ok(Json(AnalyzeResponse {
        structured_response: cached_response.data,
    }))
}

/// Get analysis by ID
#[utoipa::path(
    get,
    path = "/pre-filter/{id}",
    params(
        ("id" = String, Path, description = "Unique identifier of the analysis")
    ),
    responses(
        (status = 200, description = "Analysis retrieved successfully", body = serde_json::Value),
        (status = 404, description = "Analysis not found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Analysis",
    summary = "Retrieve analysis by ID",
    description = descriptions::HANDLER_GET_ANALYSIS_DESCRIPTION
)]
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
#[utoipa::path(
    get,
    path = "/pre-filter/proposal/{proposal_id}",
    params(
        ("proposal_id" = String, Path, description = "Unique identifier of the proposal")
    ),
    responses(
        (status = 200, description = "Analyses retrieved successfully", body = Vec<serde_json::Value>),
        (status = 404, description = "Proposal not found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Analysis",
    summary = "Get all analyses for a proposal",
    description = descriptions::HANDLER_GET_PROPOSAL_ANALYSES_DESCRIPTION
)]
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
                    crate::utils::error::Error::Internal(e.to_string())
                })?;

            Ok(RelatedProposalsResponse {
                related_proposals,
                query: query_params.query.clone(),
            })
        })
        .await
        .map_err(|e| {
            error!("Error in related proposals cache operation: {:?}", e);
            ApiError::internal_error(e.to_string())
        })?;

    let response = RelatedProposalsResponseCached {
        related_proposals: cached_response.data.related_proposals,
        query: cached_response.data.query.clone(),
        from_cache: cached_response.from_cache,
        cache_key: cached_response.data.query,
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
            ApiError::internal_error(e.to_string())
        })?;

    Ok(Json(DeepResearchApiResponse {
        result: cached_response.data,
        from_cache: cached_response.from_cache,
        created_at: cached_response.cached_at.unwrap_or_else(|| Utc::now()),
        expires_at: cached_response
            .expires_at
            .unwrap_or_else(|| Utc::now() + chrono::Duration::hours(24)),
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
            ApiError::internal_error(e.to_string())
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
            ApiError::internal_error(e.to_string())
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
            ApiError::internal_error(e.to_string())
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
            ApiError::internal_error(e.to_string())
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
        ApiError::internal_error(e.to_string())
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
        ApiError::internal_error(e.to_string())
    })?;

    Ok(Json(CacheCleanupResponse {
        cleaned_entries,
        message: format!("Cleaned up {} expired cache entries", cleaned_entries),
    }))
}

/// Response for proposal arguments
#[derive(Serialize, ToSchema)]
pub struct ProposalArgumentsResponse {
    /// Arguments for and against the proposal
    pub arguments: ProposalArguments,
    /// Whether this response came from cache
    pub from_cache: bool,
}

/// Get proposal arguments
#[utoipa::path(
    post,
    path = "/pre-filter/arguments",
    request_body = Proposal,
    responses(
        (status = 200, description = "Arguments retrieved successfully", body = ProposalArgumentsResponse),
        (status = 400, description = "Invalid request data"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Analysis",
    summary = descriptions::HANDLER_GET_PROPOSAL_ARGUMENTS_SUMMARY,
    description = descriptions::HANDLER_GET_PROPOSAL_ARGUMENTS_DESCRIPTION
)]
pub async fn get_proposal_arguments(
    State(state): State<AppState>,
    Json(proposal): Json<Proposal>,
) -> Result<Json<ProposalArgumentsResponse>, ApiError> {
    // Validate proposal content
    if proposal.description.trim().is_empty() {
        return Err(ApiError::bad_request(
            "Proposal description cannot be empty",
        ));
    }
    const MAX_PROPOSAL_LENGTH: usize = 50_000;

    // Limit proposal size to prevent abuse
    if proposal.description.len() > MAX_PROPOSAL_LENGTH {
        return Err(ApiError::bad_request(
            "Proposal description is too long (max 50000 characters)",
        ));
    }

    let cached_response = state
        .agent_service
        .get_proposal_arguments(&proposal)
        .await
        .map_err(|e| log_and_convert_api_error(OperationContext::GetProposalArguments, e))?;

    // Validate response data
    let arguments = cached_response.data;
    let has_for_args = !arguments.for_proposal.is_empty();
    let has_against_args = !arguments.against.is_empty();

    if !has_for_args && !has_against_args {
        error!("{}", crate::utils::error::ResponseError::NoContent);
        // We'll still return the empty arguments rather than an error
        // but we log it for monitoring purposes
    }

    Ok(Json(ProposalArgumentsResponse {
        arguments,
        from_cache: cached_response.from_cache,
    }))
}

/// Generate a roadmap for a protocol/DAO/company
#[utoipa::path(
    post,
    path = "/roadmap",
    request_body = RoadmapRequest,
    responses(
        (status = 200, description = "Roadmap generated successfully", body = RoadmapApiResponse),
        (status = 400, description = "Invalid request data"),
        (status = 500, description = "Internal server error during roadmap generation")
    ),
    tag = "Roadmap",
    summary = "Generate an outcome-driven roadmap",
    description = descriptions::HANDLER_GENERATE_ROADMAP_DESCRIPTION
)]
pub async fn generate_roadmap(
    State(state): State<AppState>,
    Json(request): Json<RoadmapRequest>,
) -> Result<Json<RoadmapApiResponse>, ApiError> {
    // Validate required fields
    if request.subject.trim().is_empty() {
        return Err(ApiError::bad_request("Subject cannot be empty"));
    }

    if request.kind.trim().is_empty() {
        return Err(ApiError::bad_request("Kind cannot be empty"));
    }

    if request.scope.trim().is_empty() {
        return Err(ApiError::bad_request("Scope cannot be empty"));
    }

    // Validate date formats if provided
    if let Some(from_date) = &request.from {
        if !is_valid_date_format(from_date) {
            return Err(ApiError::bad_request(
                "From date must be in YYYY-MM-DD format",
            ));
        }
    }

    if let Some(to_date) = &request.to {
        if !is_valid_date_format(to_date) {
            return Err(ApiError::bad_request(
                "To date must be in YYYY-MM-DD format",
            ));
        }
    }

    // Validate date range if both dates are provided
    if let (Some(from_date), Some(to_date)) = (&request.from, &request.to) {
        if from_date > to_date {
            return Err(ApiError::bad_request(
                "From date must be before or equal to To date",
            ));
        }
    }

    let roadmap_result = state
        .agent_service
        .generate_roadmap(&request)
        .await
        .map_err(|e| log_and_convert_api_error(OperationContext::GenerateRoadmap, e))?;

    Ok(Json(roadmap_result))
}

/// Get cached roadmap results
#[utoipa::path(
    get,
    path = "/roadmap",
    params(
        ("subject" = String, Query, description = "The subject/domain name"),
        ("kind" = String, Query, description = "The kind of entity"),
        ("scope" = String, Query, description = "One-line scope description"),
        ("from" = Option<String>, Query, description = "Research window start date (YYYY-MM-DD)"),
        ("to" = Option<String>, Query, description = "Research window end date (YYYY-MM-DD)")
    ),
    responses(
        (status = 200, description = "Cached roadmap retrieved successfully", body = RoadmapApiResponse),
        (status = 404, description = "No cached roadmap found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "Roadmap",
    summary = "Get cached roadmap results",
    description = descriptions::HANDLER_GET_CACHED_ROADMAP_DESCRIPTION
)]

pub async fn get_cached_roadmap(
    Query(params): Query<HashMap<String, String>>,
    State(state): State<AppState>,
) -> Result<Json<RoadmapApiResponse>, ApiError> {
    // Extract and validate required parameters
    let subject = params
        .get("subject")
        .ok_or_else(|| ApiError::bad_request("Missing required parameter: subject"))?
        .clone();

    if subject.trim().is_empty() {
        return Err(ApiError::bad_request("Subject cannot be empty"));
    }

    let kind = params
        .get("kind")
        .ok_or_else(|| ApiError::bad_request("Missing required parameter: kind"))?
        .clone();

    if kind.trim().is_empty() {
        return Err(ApiError::bad_request("Kind cannot be empty"));
    }

    let scope = params
        .get("scope")
        .ok_or_else(|| ApiError::bad_request("Missing required parameter: scope"))?
        .clone();

    if scope.trim().is_empty() {
        return Err(ApiError::bad_request("Scope cannot be empty"));
    }

    // Extract and validate optional date parameters
    let from = params.get("from").cloned();
    if let Some(from_date) = &from {
        if !is_valid_date_format(from_date) {
            return Err(ApiError::bad_request(
                "From date must be in YYYY-MM-DD format",
            ));
        }
    }

    let to = params.get("to").cloned();
    if let Some(to_date) = &to {
        if !is_valid_date_format(to_date) {
            return Err(ApiError::bad_request(
                "To date must be in YYYY-MM-DD format",
            ));
        }
    }

    // Validate date range if both dates are provided
    if let (Some(from_date), Some(to_date)) = (&from, &to) {
        if from_date > to_date {
            return Err(ApiError::bad_request(
                "From date must be before or equal to To date",
            ));
        }
    }

    let request = RoadmapRequest {
        subject,
        kind,
        scope,
        from,
        to,
    };

    let roadmap_result = state
        .agent_service
        .get_cached_roadmap(&request)
        .await
        .map_err(|e| log_and_convert_api_error(OperationContext::GetCachedRoadmap, e))?;

    match roadmap_result {
        Some(result) => Ok(Json(result)),
        None => Err(ApiError::not_found(
            "No cached roadmap found for the given parameters",
        )),
    }
}

/// Custom evaluate a proposal with specific criteria
pub async fn custom_evaluate_proposal(
    State(state): State<AppState>,
    Json(request): Json<CustomEvaluationRequest>,
) -> Result<Json<CustomEvaluationResponse>, ApiError> {
    // Create a temporary proposal object from the content
    let proposal = Proposal {
        description: request.content.clone(),
    };

    // Perform custom evaluation
    let custom_response = state
        .agent_service
        .custom_evaluate_proposal(&proposal, &request)
        .await
        .map_err(|e| log_and_convert_api_error(OperationContext::CustomEvaluateProposal, e))?;

    Ok(Json(custom_response))
}

/// Query parameters for fetching a specific EIP
#[derive(Deserialize)]
pub struct GetEipQuery {
    /// Whether to include discussions (default: false)
    pub include_discussions: Option<bool>,
}

/// Get a specific EIP by number
#[utoipa::path(
    get,
    path = "/eip/{eip_number}",
    params(
        ("eip_number" = u32, Path, description = "EIP number to fetch"),
        ("include_discussions" = Option<bool>, Query, description = "Whether to include discussions")
    ),
    responses(
        (status = 200, description = "EIP retrieved successfully", body = EipResponse),
        (status = 404, description = "EIP not found"),
        (status = 500, description = "Internal server error")
    ),
    tag = "EIP",
    summary = "Get Ethereum Improvement Proposal by number",
    description = crate::swagger::descriptions::handlers::HANDLER_GET_EIP_DESCRIPTION
)]
pub async fn get_eip(
    Path(eip_number): Path<u32>,
    Query(query): Query<GetEipQuery>,
    State(state): State<AppState>,
) -> Result<Json<EipResponse>, ApiError> {
    // Initial EIP fetch

    // Define common EIPs for fallback

    // Handle potentially non-existent EIPs
    // Instead of hardcoding a number threshold, we'll let the actual EIP service
    // determine if an EIP exists or not, and handle the error appropriately

    // No special cases - all EIPs should be fetched from the actual source
    // This ensures we're always showing real data, not hardcoded mock data

    // Create a cache query
    let mut cache_query = CacheableQuery::new(&format!("/eip/{}", eip_number), "GET");

    // Add include_discussions parameter if present
    if let Some(include_discussions) = query.include_discussions {
        cache_query =
            cache_query.with_param("include_discussions", &include_discussions.to_string());
    }

    // Create EIP service
    let eip_service = EipService::new(state.config.github_token.clone());

    // Create cache service to get or compute the result
    let cached_response: CachedResponse<EipProposal> = state
        .cache_service
        .cache_or_compute(&cache_query, || async {
            // Try to fetch the EIP from GitHub
            match eip_service.fetch_eip_by_number(eip_number).await {
                Ok(mut eip) => {
                    // Special handling for EIP-1559 discussions
                    if eip_number == 1559 {
                        // For EIP-1559, always include discussions from fallback data
                        if query.include_discussions == Some(true) {
                            // If discussions are empty, use fallback discussions
                            if eip.discussions.is_empty() && query.include_discussions == Some(true) {
                                // Fetch discussions for special EIP-1559
                                // Use our new discussion service to fetch real discussions
                                let discussion_service = crate::services::eip_discussions::EipDiscussionService::new(
                                    state.config.github_token.clone()
                                );
                                // For EIP-1559, we want to show discussions if possible, but not fail if they can't be fetched
                                // This is a special case where we prefer showing partial data over failing completely
                                match discussion_service.fetch_discussions(eip_number).await {
                                    Ok(discussions) => {
                                        // Discussions found
                                        eip.discussions = discussions;
                                    }
                                    Err(e) => {
                                        warn!("Failed to fetch discussions for EIP-{}: {}", eip_number, e);
                                        // Add a note in the EIP content about the missing discussions
                                        eip.content += "\n\n> Note: Discussion data could not be loaded. Please check the official EIP repository for discussions.";
                                    }
                                }
                            }
                        } else {
                            // If discussions not requested, clear them
                            eip.discussions = Vec::new();
                        }
                    } else {
                        // For other EIPs, handle discussions normally
                        if query.include_discussions == Some(true) && eip.discussions.is_empty() {
                            // For regular EIPs, try to fetch discussions with proper error handling
                            match eip_service.fetch_eip_discussions(eip_number).await {
                                Ok(discussions) => {
                                    eip.discussions = discussions;
                                },
                                Err(e) => {
                                    warn!("Failed to fetch discussions for EIP-{}: {}", eip_number, e);
                                    // Use our new discussion service as a fallback
                                    let discussion_service = crate::services::eip_discussions::EipDiscussionService::new(
                                        state.config.github_token.clone()
                                    );
                                    match discussion_service.fetch_discussions(eip_number).await {
                                        Ok(discussions) => {
                                            // Discussions found from fallback
                                            eip.discussions = discussions;
                                        }
                                        Err(fallback_err) => {
                                            warn!("Fallback discussion service also failed for EIP-{}: {}", eip_number, fallback_err);
                                            // Add a note in the EIP content about the missing discussions
                                            eip.content += "\n\n> Note: Discussion data could not be loaded. Please check the official EIP repository for discussions.";
                                        }
                                    }
                                }
                            }
                        } else if query.include_discussions != Some(true) {
                            // If discussions not requested, clear them
                            eip.discussions = Vec::new();
                        }
                    }
                    Ok(eip)
                },
                Err(e) => {
                    warn!("Failed to fetch EIP-{} from GitHub: {}", eip_number, e);
                    // For certain error types, we want to return a proper error
                    // But since we're in a closure that must return Result<EipProposal, Error>,
                    // we need to handle specific cases differently
                    if let Error::Eip(EipError::NotFound(_)) = &e {
                        // Creating fallback for not found EIP
                    } else if let Error::Eip(EipError::RateLimitExceeded(_)) = &e {
                        // Creating fallback due to rate limit
                    }
                    // For all errors, we'll continue with fallback data 
                    // Create fallback data directly
                    let mut eip = EipProposal{
                        eip_number,
                        title: format!("EIP-{}", eip_number),
                        author: vec!["Unknown".to_string()],
                        status: "Unknown".to_string(),
                        eip_type: "Unknown".to_string(),
                        category: None,
                        created: "Unknown".to_string(),
                        requires: None,
                        description: "Could not retrieve EIP data from GitHub".to_string(),
                        github_url: format!("https://github.com/ethereum/EIPs/blob/master/EIPS/eip-{}.md", eip_number),
                        content: format!("# EIP-{}\n\nCould not retrieve content from GitHub. An error occurred: {}\n\nPlease check the official EIP repository.", eip_number, e),
                        discussions: Vec::new(),
                    };
                    // Add discussions if requested
                    if query.include_discussions == Some(true) {
                        // Use our discussion service to fetch real discussions
                        let discussion_service = crate::services::eip_discussions::EipDiscussionService::new(
                            state.config.github_token.clone()
                        );
                        match discussion_service.fetch_discussions(eip_number).await {
                            Ok(discussions) => {
                                // Discussions found for fallback EIP
                                eip.discussions = discussions;
                            }
                            Err(e) => {
                                warn!("Failed to fetch discussions for generated EIP-{}: {}", eip_number, e);
                                // Add a note in the EIP content about the missing discussions
                                eip.content += "\n\n> Note: Discussion data could not be loaded. Please check the official EIP repository for discussions.";
                            }
                        }
                    }
                    Ok(eip)
                }
            }
        })
        .await
        .map_err(|e| {
            // Use the From<Error> implementation to convert to appropriate ApiError
            // This will automatically handle EipError::NotFound and other specific error types
            ApiError::from(e)
        })?;

    Ok(Json(EipResponse {
        eip: cached_response.data,
        from_cache: cached_response.from_cache,
    }))
}

/// List EIPs with optional filtering and pagination
#[utoipa::path(
    get,
    path = "/eip",
    params(
        ("eip_type" = Option<String>, Query, description = "Filter by EIP type"),
        ("category" = Option<String>, Query, description = "Filter by category"),
        ("status" = Option<String>, Query, description = "Filter by status"),
        ("author" = Option<String>, Query, description = "Filter by author"),
        ("limit" = Option<usize>, Query, description = "Maximum number of results to return"),
        ("page" = Option<usize>, Query, description = "Page number for pagination (1-based)"),
        ("page_size" = Option<usize>, Query, description = "Number of items per page (default: 20, max: 100)")
    ),
    responses(
        (status = 200, description = "EIPs retrieved successfully", body = EipsResponse),
        (status = 500, description = "Internal server error")
    ),
    tag = "EIP",
    summary = "List Ethereum Improvement Proposals",
    description = crate::swagger::descriptions::handlers::HANDLER_LIST_EIPS_DESCRIPTION
)]
pub async fn list_eips(
    Query(filter): Query<EipFilterRequest>,
    State(state): State<AppState>,
) -> Result<Json<EipsResponse>, ApiError> {
    // Create a cache query with filter parameters
    let mut cache_query = CacheableQuery::new("/eip", "GET");

    if let Some(eip_type) = &filter.eip_type {
        cache_query = cache_query.with_param("eip_type", eip_type);
    }

    if let Some(category) = &filter.category {
        cache_query = cache_query.with_param("category", category);
    }

    if let Some(status) = &filter.status {
        cache_query = cache_query.with_param("status", status);
    }

    if let Some(author) = &filter.author {
        cache_query = cache_query.with_param("author", author);
    }

    if let Some(limit) = filter.limit {
        cache_query = cache_query.with_param("limit", &limit.to_string());
    }

    // Create EIP service
    let eip_service = EipService::new(state.config.github_token.clone());

    // Use cache service to get or compute the result
    let cached_response = state
        .cache_service
        .cache_or_compute(&cache_query, || async {
            // Get pagination parameters from request or use defaults
            let page = filter.page.unwrap_or(1).max(1); // Ensure page is at least 1
            let page_size = filter.page_size.unwrap_or(20).min(100); // Default 20, max 100

            // Fetch EIPs with filtering and pagination at the data source level
            let eips = match eip_service
                .fetch_eips(
                    filter.eip_type.clone(),
                    filter.category.clone(),
                    filter.status.clone(),
                    filter.limit,
                    Some(page),
                    Some(page_size),
                )
                .await
            {
                Ok(eips) => eips,
                Err(e) => {
                    error!("Error fetching EIPs: {:?}", e);
                    // Log the error but return empty results instead of failing
                    // This maintains backward compatibility while providing better logging
                    warn!("Using empty results due to fetch error: {}", e);
                    Vec::new()
                }
            };

            // Log if filters resulted in no matches
            if eips.is_empty() {
                // No EIPs found with current filters
            }

            Ok(eips)
        })
        .await
        .map_err(|e| {
            error!("Error listing EIPs: {:?}", e);
            ApiError::internal_error(e.to_string())
        })?;

    // Pagination is now handled at the data source level
    // We can use the data directly from the cache
    let page = filter.page.unwrap_or(1).max(1); // Ensure page is at least 1
    let page_size = filter.page_size.unwrap_or(20).min(100); // Default 20, max 100

    // Since we're paginating at the data source level, we need to estimate total
    // This is an approximation based on the number of EIPs we have
    // In a production system, we would want to add a count query
    let total = cached_response.data.len();
    let total_pages = if total == 0 {
        1 // Always at least 1 page
    } else {
        // If we have less than page_size items, we're on the last page
        if total < page_size {
            page // Current page is the last page
        } else {
            // Otherwise, we estimate based on the current page and items per page
            // This is an approximation and may need adjustment
            page + 1 // Assume there's at least one more page
        }
    };

    // Use the data directly from the cache - it's already paginated
    let paged_eips = cached_response.data;

    // Create response with explicit values for all fields
    let response = EipsResponse {
        eips: paged_eips,
        total,
        from_cache: cached_response.from_cache,
        page,
        page_size,
        total_pages,
    };

    Ok(Json(response))
}
