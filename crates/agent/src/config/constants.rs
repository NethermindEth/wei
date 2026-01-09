//! Application-wide constants
//!
//! This module provides centralized constants for the application
//! to avoid magic numbers and improve maintainability.

/// Default cache TTL in hours
pub const DEFAULT_CACHE_TTL_HOURS: i64 = 1;

/// Default page size for pagination
pub const DEFAULT_PAGE_SIZE: usize = 20;

/// Maximum page size for pagination
pub const MAX_PAGE_SIZE: usize = 100;

/// Maximum number of retries for external API calls
pub const MAX_API_RETRIES: usize = 3;

/// Default timeout for external API calls in seconds
pub const DEFAULT_API_TIMEOUT_SECONDS: u64 = 30;

/// Default batch size for bulk operations
pub const DEFAULT_BATCH_SIZE: usize = 50;

/// Maximum number of EIPs to process in a single request
pub const MAX_EIPS_TO_PROCESS: usize = 100;

/// GitHub API rate limit threshold for warnings
pub const GITHUB_RATE_LIMIT_WARNING_THRESHOLD: u32 = 100;

/// Default number of arguments to generate per side
pub const DEFAULT_ARGUMENTS_PER_SIDE: usize = 3;

/// Maximum number of arguments to generate per side
pub const MAX_ARGUMENTS_PER_SIDE: usize = 10;

/// Default temperature for AI model calls
pub const DEFAULT_AI_TEMPERATURE: f32 = 0.7;

/// Default maximum tokens for AI model responses
pub const DEFAULT_AI_MAX_TOKENS: u32 = 2048;

/// Database connection pool settings
pub mod db {
    /// Default maximum connections in the pool
    pub const MAX_CONNECTIONS: u32 = 10;
    
    /// Default minimum connections in the pool
    pub const MIN_CONNECTIONS: u32 = 2;
    
    /// Default connection timeout in seconds
    pub const CONNECTION_TIMEOUT_SECONDS: u64 = 5;
    
    /// Default idle timeout in seconds
    pub const IDLE_TIMEOUT_SECONDS: u64 = 300;
    
    /// Default maximum lifetime of a connection in seconds
    pub const MAX_LIFETIME_SECONDS: u64 = 1800;
}

/// HTTP server settings
pub mod http {
    /// Default server port
    pub const DEFAULT_PORT: u16 = 8000;
    
    /// Default server host
    pub const DEFAULT_HOST: &str = "0.0.0.0";
    
    /// Default request timeout in seconds
    pub const REQUEST_TIMEOUT_SECONDS: u64 = 60;
    
    /// Default graceful shutdown timeout in seconds
    pub const SHUTDOWN_TIMEOUT_SECONDS: u64 = 30;
    
    /// Default maximum request body size in bytes
    pub const MAX_REQUEST_SIZE_BYTES: usize = 10 * 1024 * 1024; // 10 MB
}

/// EIP-specific constants
pub mod eip {
    /// Base URL for EIP GitHub repository
    pub const GITHUB_BASE_URL: &str = "https://api.github.com/repos/ethereum/EIPs";
    
    /// Base URL for EIP raw content
    pub const GITHUB_RAW_URL: &str = "https://raw.githubusercontent.com/ethereum/EIPs/master";
    
    /// EIP file pattern
    pub const EIP_FILE_PATTERN: &str = "eip-*.md";
    
    /// EIP number regex pattern
    pub const EIP_NUMBER_REGEX: &str = r"eip-(\d+)\.md";
    
    /// EIP statuses
    pub const STATUS_DRAFT: &str = "Draft";
    pub const STATUS_REVIEW: &str = "Review";
    pub const STATUS_LAST_CALL: &str = "Last Call";
    pub const STATUS_FINAL: &str = "Final";
    pub const STATUS_STAGNANT: &str = "Stagnant";
    pub const STATUS_WITHDRAWN: &str = "Withdrawn";
    pub const STATUS_LIVING: &str = "Living";
    
    /// EIP types
    pub const TYPE_STANDARDS_TRACK: &str = "Standards Track";
    pub const TYPE_META: &str = "Meta";
    pub const TYPE_INFORMATIONAL: &str = "Informational";
}

/// Special EIP configurations
pub mod special_eips {
    use std::collections::HashMap;
    use once_cell::sync::Lazy;
    
    /// Special EIP configurations
    pub static SPECIAL_EIPS: Lazy<HashMap<u32, SpecialEipConfig>> = Lazy::new(|| {
        let mut map = HashMap::new();
        
        // EIP-1559: Fee market change
        map.insert(1559, SpecialEipConfig {
            title_override: Some("Fee market change for ETH 1.0 chain"),
            important: true,
            custom_cache_ttl_hours: Some(24),
        });
        
        // EIP-4844: Shard Blob Transactions
        map.insert(4844, SpecialEipConfig {
            title_override: Some("Shard Blob Transactions"),
            important: true,
            custom_cache_ttl_hours: Some(24),
        });
        
        map
    });
    
    /// Special configuration for an EIP
    pub struct SpecialEipConfig {
        /// Override for the EIP title
        pub title_override: Option<String>,
        /// Whether this is an important EIP
        pub important: bool,
        /// Custom cache TTL in hours
        pub custom_cache_ttl_hours: Option<i64>,
    }
}

/// AI model settings
pub mod ai {
    /// Default model for general tasks
    pub const DEFAULT_MODEL: &str = "gpt-4o";
    
    /// Model for summarization tasks
    pub const SUMMARIZATION_MODEL: &str = "gpt-4o";
    
    /// Model for argument generation
    pub const ARGUMENT_GENERATION_MODEL: &str = "gpt-4o";
    
    /// Model for evaluation tasks
    pub const EVALUATION_MODEL: &str = "gpt-4o";
    
    /// System prompt for argument generation
    pub const ARGUMENT_GENERATION_PROMPT: &str = "You are an expert in Ethereum governance proposals. \
        Generate balanced, nuanced arguments both for and against the proposal. \
        Focus on technical merits, economic implications, security considerations, and community impact.";
    
    /// System prompt for evaluation
    pub const EVALUATION_PROMPT: &str = "You are an expert in Ethereum governance proposals. \
        Evaluate the proposal based on the provided criteria. \
        Be objective and provide clear justifications for your assessment.";
}
