//! Error types for the agent service

use thiserror::Error;

/// Agent service error
#[allow(dead_code)] // TODO: Remove after development phase
#[derive(Error, Debug)]
pub enum Error {
    /// Database operation failed
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    /// HTTP request failed
    #[error("HTTP request error: {0}")]
    HttpRequest(#[from] reqwest::Error),

    /// JSON serialization/deserialization failed
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    /// Configuration loading failed
    #[error("Configuration error: {0}")]
    Configuration(#[from] clap::Error),

    /// AI service operation failed
    #[error("AI service error: {0}")]
    #[allow(dead_code)] // TODO: Remove after development phase
    AIService(String),

    /// Analysis was not found in the database
    #[error("Analysis not found: {id}")]
    #[allow(dead_code)] // TODO: Remove after development phase
    AnalysisNotFound {
        /// ID of the missing analysis
        id: String,
    },

    /// Webhook operation failed
    #[error("Webhook error: {0}")]
    #[allow(dead_code)] // TODO: Remove after development phase
    Webhook(String),

    /// Authentication failed
    #[error("Authentication error: {0}")]
    #[allow(dead_code)] // TODO: Remove after development phase
    Authentication(String),

    /// OpenRouter API error
    #[error("OpenRouter API error: {0}")]
    #[allow(dead_code)] // TODO: Remove after development phase
    OpenRouter(Box<openrouter_rs::error::OpenRouterError>),

    /// ChatCompletionRequest builder error
    #[error("ChatCompletionRequest builder error: {0}")]
    ChatBuilder(openrouter_rs::error::OpenRouterError),

    /// Internal service error
    #[error("Internal error: {0}")]
    Internal(String),
}

impl From<openrouter_rs::error::OpenRouterError> for Error {
    fn from(error: openrouter_rs::error::OpenRouterError) -> Self {
        Error::OpenRouter(Box::new(error))
    }
}

/// Result type for the agent service
pub type Result<T> = core::result::Result<T, Error>;
