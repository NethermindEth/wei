//! Error types for the indexer service

use thiserror::Error;

/// Indexer service error
#[allow(dead_code)] // TODO: Remove after development phase
#[derive(Error, Debug)]
pub enum IndexerError {
    /// Database operation failed
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),

    /// HTTP request failed
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("HTTP request error: {0}")]
    HttpRequest(#[from] reqwest::Error),

    /// JSON serialization/deserialization failed
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    /// Configuration loading failed
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Configuration error: {0}")]
    Configuration(String),

    /// Data source operation failed
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Data source error: {0}")]
    DataSource(String),

    /// Proposal was not found in the database
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Proposal not found: {id}")]
    ProposalNotFound {
        /// ID of the missing proposal
        id: String,
    },

    /// Actor was not found in the database
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Actor not found: {address}")]
    ActorNotFound {
        /// Address of the missing actor
        address: String,
    },

    /// Protocol ID is invalid
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Invalid protocol ID: {id}")]
    InvalidProtocolId {
        /// Invalid protocol ID
        id: String,
    },

    /// Webhook operation failed
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Webhook error: {0}")]
    Webhook(String),

    /// Internal service error
    #[allow(dead_code)] // TODO: Remove after development phase
    #[error("Internal error: {0}")]
    Internal(String),
}

impl From<anyhow::Error> for IndexerError {
    fn from(err: anyhow::Error) -> Self {
        IndexerError::Internal(err.to_string())
    }
}
