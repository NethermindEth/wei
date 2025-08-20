//! Main agent service

use std::future::Future;

use openrouter_rs::{api::chat::ChatCompletionRequest, types::Role, Message, OpenRouterClient};
use serde_json;

use crate::models::analysis::StructuredAnalysisResponse;
use crate::prompts::ANALYZE_PROPOSAL_PROMPT;
use crate::utils::error::Result;

use crate::{db::core::Database, models::Proposal, Config};

/// Main agent service
#[derive(Clone)]
pub struct AgentService {
    db: Database,
    openrouter: OpenRouterClient,
    config: Config,
}

impl AgentService {
    /// Create a new agent service
    pub fn new(db: Database, config: Config) -> Self {
        Self {
            db,
            // Unwrap is safe because we are doing it on init only
            openrouter: Self::init_open_router(&config).unwrap(),
            config,
        }
    }

    /// Initialize the OpenRouter client
    fn init_open_router(config: &Config) -> Result<OpenRouterClient> {
        let openrouter = OpenRouterClient::builder()
            .api_key(config.ai_model_api_key.clone())
            .build()?;

        Ok(openrouter)
    }
}

/// Trait for the agent service
pub trait AgentServiceTrait {
    /// Analyze a proposal
    fn analyze_proposal(&self, proposal: &Proposal) -> impl Future<Output = Result<StructuredAnalysisResponse>>;
}

impl AgentServiceTrait for AgentService {
    /// Analyze a proposal
    async fn analyze_proposal(&self, proposal: &Proposal) -> Result<StructuredAnalysisResponse> {
        let request = ChatCompletionRequest::builder()
            .model(self.config.ai_model_name.clone())
            .messages(vec![
                Message::new(Role::System, ANALYZE_PROPOSAL_PROMPT),
                Message::new(Role::User, serde_json::to_string(&proposal)?.as_str()),
            ])
            .build()
            .map_err(|e| crate::utils::error::Error::Internal(e.to_string()))?;

        let response = self
            .openrouter
            .send_chat_completion(&request)
            .await
            .map_err(|e| crate::utils::error::Error::Internal(e.to_string()))?;

        let content = response.choices[0]
            .content()
            .ok_or(crate::utils::error::Error::Internal(
                "No content in response".to_string(),
            ))?
            .to_string();
            
        // Parse the JSON response into our structured format
        match serde_json::from_str::<StructuredAnalysisResponse>(&content) {
            Ok(structured_response) => Ok(structured_response),
            Err(e) => {
                tracing::error!("Failed to parse structured response: {}", e);
                tracing::error!("Raw response: {}", content);
                
                // Create a fallback response with just the raw text
                let fallback = StructuredAnalysisResponse {
                    verdict: if content.to_lowercase().contains("good") { "good".to_string() } else { "bad".to_string() },
                    conclusion: content.chars().take(300).collect::<String>() + "...",
                    proposal_quality: Default::default(),
                    submitter_intentions: Default::default(),
                };
                
                Ok(fallback)
            }
        }
    }
}
