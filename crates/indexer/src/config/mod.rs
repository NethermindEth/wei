//! Configuration management for the indexer service

use clap::Parser;
use serde::{Deserialize, Serialize};

/// Application configuration
#[derive(Debug, Clone, Serialize, Deserialize, Parser)]
pub struct Config {
    /// Application port
    #[arg(env = "WEI_INDEXER_PORT", long, default_value = "8001")]
    pub port: u16,

    /// Host to bind to
    #[arg(env = "WEI_INDEXER_HOST", long, default_value = "0.0.0.0")]
    pub host: String,

    /// Database URL
    #[arg(
        env = "WEI_INDEXER_DATABASE_URL",
        long,
        default_value = "postgresql://postgres:postgres@localhost:5432/wei_indexer"
    )]
    pub database_url: String,

    /// Maximum number of database connections
    #[arg(env = "WEI_INDEXER_MAX_CONNECTIONS", long, default_value = "10")]
    pub max_connections: u32,

    /// Snapshot API base URL
    #[arg(
        env = "WEI_INDEXER_SNAPSHOT_BASE_URL",
        long,
        default_value = "https://hub.snapshot.org"
    )]
    pub snapshot_base_url: String,

    /// Snapshot API key (optional)
    #[arg(env = "WEI_INDEXER_SNAPSHOT_API_KEY", long)]
    pub snapshot_api_key: Option<String>,

    /// Tally API base URL
    #[arg(
        env = "WEI_INDEXER_TALLY_BASE_URL",
        long,
        default_value = "https://api.tally.xyz"
    )]
    pub tally_base_url: String,

    /// Tally API key (optional)
    #[arg(env = "WEI_INDEXER_TALLY_API_KEY", long)]
    pub tally_api_key: Option<String>,

    /// Webhook secret for authentication
    #[arg(env = "WEI_INDEXER_WEBHOOK_SECRET", long)]
    pub webhook_secret: String,

    /// Maximum webhook retry attempts
    #[arg(env = "WEI_INDEXER_MAX_RETRIES", long, default_value = "3")]
    pub max_retries: u32,
}

#[allow(dead_code)] // TODO: Remove after development phase
impl Config {
    /// Get server configuration
    pub fn server(&self) -> ServerConfig {
        ServerConfig {
            host: self.host.clone(),
            port: self.port,
        }
    }

    /// Get database configuration
    pub fn database(&self) -> DatabaseConfig {
        DatabaseConfig {
            url: self.database_url.clone(),
            max_connections: self.max_connections,
        }
    }

    /// Get data source configuration
    pub fn data_sources(&self) -> DataSourceConfig {
        DataSourceConfig {
            snapshot: SnapshotConfig {
                base_url: self.snapshot_base_url.clone(),
                api_key: self.snapshot_api_key.clone(),
            },
            tally: TallyConfig {
                base_url: self.tally_base_url.clone(),
                api_key: self.tally_api_key.clone(),
            },
        }
    }

    /// Get webhook configuration
    pub fn webhook(&self) -> WebhookConfig {
        WebhookConfig {
            secret: self.webhook_secret.clone(),
            max_retries: self.max_retries,
        }
    }
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
