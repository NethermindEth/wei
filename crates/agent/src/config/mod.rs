//! Configuration management for the agent service

use serde::{Deserialize, Serialize};

/// Application configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Server configuration
    pub server: ServerConfig,
    /// Database configuration
    pub database: DatabaseConfig,
    /// AI service configuration
    pub ai: AIConfig,
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

/// AI service configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIConfig {
    /// AI model endpoint
    pub endpoint: String,
    /// API key for AI service
    pub api_key: String,
    /// Model name
    pub model: String,
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
