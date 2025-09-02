//! Configuration management for the agent service

use clap::Parser;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

/// Application configuration
#[derive(Debug, Clone, Serialize, Deserialize, Parser)]
pub struct Config {
    /// Application port
    #[arg(env = "WEI_AGENT_PORT", long, default_value = "3001")]
    pub port: u16,

    /// Database URL
    #[arg(
        env = "WEI_AGENT_DATABASE_URL",
        long,
        default_value = "postgresql://postgres:postgres@localhost:5432/wei_agent"
    )]
    pub database_url: String,

    /// AI model provider
    #[arg(env = "WEI_AGENT_AI_MODEL_PROVIDER", long, default_value = "openai")]
    pub ai_model_provider: String,

    /// AI model name
    #[arg(env = "WEI_AGENT_AI_MODEL_NAME", long, default_value = "gpt-4o-mini")]
    pub ai_model_name: String,

    /// AI model API key
    #[arg(env = "WEI_AGENT_OPEN_ROUTER_API_KEY", long)]
    pub ai_model_api_key: String,

    /// API keys for authentication (comma-separated list)
    #[arg(env = "WEI_AGENT_API_KEYS", long, default_value = "")]
    api_keys_raw: String,

    /// Whether API key authentication is enabled
    #[arg(env = "WEI_AGENT_API_KEY_AUTH_ENABLED", long, default_value = "true")]
    pub api_key_auth_enabled: bool,

    /// CORS allowed origins (comma-separated list)
    #[arg(
        env = "CORS_ALLOWED_URLS",
        long,
        default_value = "http://localhost:3000"
    )]
    cors_allowed_urls_raw: String,
}

impl Config {
    /// Get the set of valid API keys
    pub fn api_keys(&self) -> HashSet<String> {
        if self.api_keys_raw.is_empty() {
            HashSet::new()
        } else {
            self.api_keys_raw
                .split(',')
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .collect()
        }
    }

    /// Check if an API key is valid
    pub fn is_valid_api_key(&self, key: &str) -> bool {
        // If authentication is disabled, all keys are valid
        if !self.api_key_auth_enabled {
            return true;
        }

        // If no keys are configured, authentication is effectively disabled
        let keys = self.api_keys();
        if keys.is_empty() {
            return true;
        }

        // Check if the provided key is in the set of valid keys
        keys.contains(key)
    }

    /// Get the list of allowed CORS origins
    pub fn cors_allowed_urls(&self) -> Vec<String> {
        if self.cors_allowed_urls_raw.is_empty() {
            vec!["http://localhost:3000".to_string()]
        } else {
            self.cors_allowed_urls_raw
                .split(',')
                .map(|s| s.trim().to_string())
                .filter(|s| !s.is_empty())
                .collect()
        }
    }
}
