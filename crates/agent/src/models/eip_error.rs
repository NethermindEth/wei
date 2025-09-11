//! Error types for EIP-related operations

use thiserror::Error;

/// Specific error types for EIP operations
#[derive(Debug, Error)]
pub enum EipError {
    /// EIP not found
    #[error("EIP-{0} not found")]
    NotFound(u32),
    
    /// GitHub API error
    #[error("GitHub API error: {0}")]
    GitHubError(String),
    
    /// Rate limit exceeded
    #[error("GitHub rate limit exceeded: {0}")]
    RateLimitExceeded(String),
    
    /// Cache error
    #[error("Cache error: {0}")]
    CacheError(String),
    
    /// Parsing error
    #[error("EIP parsing error: {0}")]
    ParseError(String),
    
    /// Network error
    #[error("Network error: {0}")]
    NetworkError(String),
    
    /// Invalid EIP number
    #[error("Invalid EIP number: {0}")]
    InvalidEipNumber(String),
    
    /// Timeout error
    #[error("Request timeout: {0}")]
    Timeout(String),
}
