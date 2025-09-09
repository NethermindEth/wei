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
            Self::AnalyzeProposal => "Error analyzing proposal",
            Self::GetProposalArguments => "Error retrieving proposal arguments",
            Self::CustomEvaluateProposal => "Error performing custom evaluation",
            Self::GetAnalysis => "Error retrieving analysis",
            Self::GetProposalAnalyses => "Error retrieving proposal analyses",
            Self::SearchRelatedProposals => "Error searching for related proposals",
            Self::AnalyzeCommunity => "Error analyzing community",
            Self::GetCommunityAnalysis => "Error retrieving community analysis",
            Self::GenerateRoadmap => "Error generating roadmap",
            Self::GetCachedRoadmap => "Error retrieving cached roadmap",
            Self::ListCachedQueries => "Error listing cached queries",
            Self::GetCacheStats => "Error retrieving cache statistics",
            Self::InvalidateCache => "Error invalidating cache",
            Self::RefreshCache => "Error refreshing cache",
            Self::CleanupCache => "Error cleaning up expired cache",
        }
    }
}

/// Helper function to log errors and convert them to ApiError
pub fn log_and_convert_api_error<E: std::fmt::Debug + std::fmt::Display>(context: OperationContext, err: E) -> ApiError {
    error!("{}: {:?}", context.error_message(), err);
    ApiError::internal_error(format!("{}", err))
}
