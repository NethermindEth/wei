//! Configuration management for the indexer service

use serde::{Deserialize, Serialize};

/// Application configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Server configuration
    pub server: ServerConfig,
    /// Database configuration
    pub database: DatabaseConfig,
    /// Data source configurations
    pub data_sources: DataSourceConfig,
    /// Webhook configuration
    pub webhook: WebhookConfig,
}

/// Server configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    /// Host to bind to
    pub host: String,
    /// Port to bind to
    pub port: u16,
}

/// Database configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    /// Database URL
    pub url: String,
    /// Maximum number of connections
    pub max_connections: u32,
}

/// Data source configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataSourceConfig {
    /// Snapshot API configuration
    pub snapshot: SnapshotConfig,
    /// Tally API configuration
    pub tally: TallyConfig,
}

/// Snapshot API configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnapshotConfig {
    /// Base URL for Snapshot API
    pub base_url: String,
    /// API key (optional)
    pub api_key: Option<String>,
}

/// Tally API configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TallyConfig {
    /// Base URL for Tally API
    pub base_url: String,
    /// API key (optional)
    pub api_key: Option<String>,
}

/// Webhook configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebhookConfig {
    /// Webhook secret for authentication
    pub secret: String,
    /// Maximum retry attempts
    pub max_retries: u32,
}

impl Config {
    /// Load configuration from environment variables
    #[allow(dead_code)] // TODO: Remove after development phase
    pub fn from_env() -> Result<Self, config::ConfigError> {
        let cfg = config::Config::builder()
            .add_source(config::Environment::default().separator("__"))
            .build()?;

        cfg.try_deserialize()
    }
}
