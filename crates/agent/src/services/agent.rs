//! Main agent service

use std::future::Future;

use openrouter_rs::{api::chat::ChatCompletionRequest, types::Role, Message, OpenRouterClient};
use serde_json;
use tracing::error;

use crate::models::analysis::{EvaluationCategory, StructuredAnalysisResponse};
use crate::models::deepresearch::{DeepResearchResponse, DeepResearchResult};
use crate::prompts::{ANALYZE_PROPOSAL_PROMPT, DEEP_RESEARCH_PROMPT};
use crate::utils::error::Result;

use crate::services::cache::{CacheService, CacheableQuery, CachedResponse};
use crate::{
    db::{
        core::Database,
        repositories::{CacheRepository, CommunityRepository},
    },
    models::Proposal,
    Config,
};

/// Main agent service
#[derive(Clone)]
pub struct AgentService {
    db: Database,
    community_repo: CommunityRepository,
    cache_service: CacheService,
    openrouter: OpenRouterClient,
    config: Config,
}

impl AgentService {
    /// Create a new agent service
    pub fn new(db: Database, config: Config) -> Self {
        let community_repo = CommunityRepository::new(db.clone());
        let cache_repo = CacheRepository::new(db.clone());
        let cache_service = CacheService::new(cache_repo);
        Self {
            db,
            community_repo,
            cache_service,
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
    /// Analyze a proposal with caching
    fn analyze_proposal(
        &self,
        proposal: &Proposal,
    ) -> impl Future<Output = Result<CachedResponse<StructuredAnalysisResponse>>>;

    /// Perform deep research on a protocol/community/topic with caching
    fn deep_research(
        &self,
        topic: &str,
    ) -> impl Future<Output = Result<CachedResponse<DeepResearchResponse>>>;

    /// Get cached deep research results (deprecated - use deep_research instead)
    fn get_cached_deep_research(
        &self,
        topic: &str,
    ) -> impl Future<Output = Result<Option<DeepResearchResult>>>;
}

impl AgentService {
    /// Compute the actual proposal analysis (without caching)
    async fn compute_proposal_analysis(
        &self,
        proposal: &Proposal,
    ) -> Result<StructuredAnalysisResponse> {
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
                error!("Failed to parse structured response: {}", e);
                error!("Raw response: {}", content);

                // Create a fallback response with the new structure
                // Try to extract any valid JSON from the content
                let default_category = EvaluationCategory {
                    status: "n/a".to_string(),
                    justification: "Could not parse response".to_string(),
                    suggestions: vec!["Please try again".to_string()],
                };

                let fallback = StructuredAnalysisResponse {
                    goals_and_motivation: default_category.clone(),
                    measurable_outcomes: default_category.clone(),
                    budget: default_category.clone(),
                    technical_specifications: default_category.clone(),
                    language_quality: default_category.clone(),
                };

                Ok(fallback)
            }
        }
    }

    /// Compute the actual deep research (without caching)
    async fn compute_deep_research(&self, topic: &str) -> Result<DeepResearchResponse> {
        // Construct the prompt with the specific topic
        let user_prompt = format!(
            "Apply the above method to the following anchor topic:\n**{}**",
            topic
        );

        let request = ChatCompletionRequest::builder()
            .model("perplexity/sonar-pro".to_string()) // Use Sonar DeepResearch Pro model
            .messages(vec![
                Message::new(Role::System, DEEP_RESEARCH_PROMPT),
                Message::new(Role::User, &user_prompt),
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

        // Clean the response content - remove markdown code blocks if present
        let cleaned_content = if content.starts_with("```json") {
            content
                .strip_prefix("```json")
                .unwrap_or(&content)
                .strip_suffix("```")
                .unwrap_or(&content)
                .trim()
        } else if content.starts_with("```") {
            content
                .strip_prefix("```")
                .unwrap_or(&content)
                .strip_suffix("```")
                .unwrap_or(&content)
                .trim()
        } else {
            content.trim()
        };

        // Parse the JSON response into our structured format
        let research_response = match serde_json::from_str::<DeepResearchResponse>(cleaned_content)
        {
            Ok(parsed_response) => parsed_response,
            Err(e) => {
                error!("Failed to parse deep research response: {}", e);
                error!("Raw response: {}", content);
                error!("Cleaned response: {}", cleaned_content);

                // Create a fallback response
                DeepResearchResponse {
                    topic: topic.to_string(),
                    resources: vec![],
                }
            }
        };

        Ok(research_response)
    }
}

impl AgentServiceTrait for AgentService {
    /// Analyze a proposal with caching
    async fn analyze_proposal(
        &self,
        proposal: &Proposal,
    ) -> Result<CachedResponse<StructuredAnalysisResponse>> {
        // Create a cache query based on the proposal content hash
        let query = CacheableQuery::new("/pre-filter", "POST").with_body(proposal)?;

        let proposal_clone = proposal.clone();
        self.cache_service
            .cache_or_compute(&query, || async {
                self.compute_proposal_analysis(&proposal_clone).await
            })
            .await
    }

    /// Perform deep research on a protocol/community/topic with caching
    async fn deep_research(&self, topic: &str) -> Result<CachedResponse<DeepResearchResponse>> {
        let query = CacheableQuery::community_analysis(topic);

        let topic_clone = topic.to_string();
        self.cache_service
            .cache_or_compute(&query, || async {
                self.compute_deep_research(&topic_clone).await
            })
            .await
    }

    /// Get cached deep research results (deprecated - use deep_research instead)
    async fn get_cached_deep_research(&self, topic: &str) -> Result<Option<DeepResearchResult>> {
        self.community_repo.get_by_topic(topic).await
    }
}
