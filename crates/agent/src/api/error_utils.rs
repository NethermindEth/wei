use crate::api::error::ApiError;
use tracing::error;

/// Operation context for standardized error messages
#[derive(Debug, Clone, Copy)]
pub enum OperationContext {
    /// Context for analyzing a proposal
    AnalyzeProposal,
    /// Context for retrieving proposal arguments
    GetProposalArguments,
    /// Context for custom evaluation of a proposal
    CustomEvaluateProposal,
    /// Context for retrieving analysis by ID
    GetAnalysis,
    /// Context for retrieving analyses for a proposal
    GetProposalAnalyses,
    /// Context for searching related proposals
    SearchRelatedProposals,
    /// Context for analyzing community discourse
    AnalyzeCommunity,
    /// Context for retrieving cached community analysis
    GetCommunityAnalysis,
    /// Context for generating a roadmap
    GenerateRoadmap,
    /// Context for retrieving a cached roadmap
    GetCachedRoadmap,
    /// Context for listing cached queries
    ListCachedQueries,
    /// Context for retrieving cache statistics
    GetCacheStats,
    /// Context for invalidating cache entries
    InvalidateCache,
    /// Context for refreshing cache entries
    RefreshCache,
    /// Context for cleaning up expired cache entries
    CleanupCache,
}

impl OperationContext {
    /// Get a standardized error message for this operation context
    pub fn error_message(&self) -> &'static str {
        match self {
            Self::AnalyzeProposal => "analyze proposal",
            Self::GetProposalArguments => "retrieve proposal arguments",
            Self::CustomEvaluateProposal => "perform custom evaluation",
            Self::GetAnalysis => "retrieve analysis",
            Self::GetProposalAnalyses => "retrieve proposal analyses",
            Self::SearchRelatedProposals => "search for related proposals",
            Self::AnalyzeCommunity => "analyze community",
            Self::GetCommunityAnalysis => "retrieve community analysis",
            Self::GenerateRoadmap => "generate roadmap",
            Self::GetCachedRoadmap => "retrieve cached roadmap",
            Self::ListCachedQueries => "list cached queries",
            Self::GetCacheStats => "retrieve cache statistics",
            Self::InvalidateCache => "invalidate cache",
            Self::RefreshCache => "refresh cache",
            Self::CleanupCache => "clean up expired cache",
        }
    }
}

/// Helper function to log errors and convert them to ApiError
pub fn log_and_convert_api_error<E: std::fmt::Debug + std::fmt::Display>(context: OperationContext, err: E) -> ApiError {
    error!("Failed to {}: {:?}", context.error_message(), err);
    ApiError::internal_error(format!("Failed to {}: {}", context.error_message(), err))
}
