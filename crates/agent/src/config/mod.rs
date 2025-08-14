//! Configuration management for the agent service

use clap::Parser;
use serde::{Deserialize, Serialize};

/// Application configuration
#[derive(Debug, Clone, Serialize, Deserialize, Parser)]
pub struct Config {
    /// Application port
    #[arg(env = "WEI_AGENT_PORT", long, default_value = "8000")]
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
}
