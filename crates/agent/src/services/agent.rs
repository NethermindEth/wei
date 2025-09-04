//! Main agent service

use crate::models::analysis::EvaluationCategory;
use std::collections::HashMap;
use std::future::Future;

use openrouter_rs::{api::chat::ChatCompletionRequest, types::Role, Message, OpenRouterClient};
use serde_json;
use tracing::{debug, error, info};

use crate::models::analysis::StructuredAnalysisResponse;
use crate::models::custom_evaluation::EvaluationResult;
use crate::models::custom_evaluation::{CustomEvaluationRequest, CustomEvaluationResponse};
use crate::models::deepresearch::{DeepResearchResponse, DeepResearchResult};
use crate::prompts::custom_evaluation::generate_custom_evaluation_prompt;
use crate::prompts::{ANALYZE_PROPOSAL_PROMPT, DEEP_RESEARCH_PROMPT};
use crate::utils::error::{Error, ResponseError, Result};
use crate::utils::markdown::extract_json_from_markdown;

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
    #[allow(clippy::result_large_err)]
    fn init_open_router(config: &Config) -> Result<OpenRouterClient> {
        let openrouter: OpenRouterClient = OpenRouterClient::builder()
            .api_key(config.ai_model_api_key.clone())
            .build()
            .map_err(|e: openrouter_rs::error::OpenRouterError| Error::ChatBuilder(e))?;

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

    /// Custom evaluate a proposal with specific criteria
    fn custom_evaluate_proposal(
        &self,
        proposal: &Proposal,
        request: &CustomEvaluationRequest,
    ) -> impl Future<Output = Result<CustomEvaluationResponse>>;

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
            .map_err(|e: openrouter_rs::error::OpenRouterError| Error::ChatBuilder(e))?;

        let response = self
            .openrouter
            .send_chat_completion(&request)
            .await
            .map_err(Error::from)?;

        let content = response.choices[0]
            .content()
            .ok_or(Error::Response(ResponseError::NoContent))?
            .to_string();

        // Extract and parse JSON from the response if it's wrapped in markdown code blocks
        match extract_json_from_markdown::<StructuredAnalysisResponse>(&content) {
            Ok(structured_response) => Ok(structured_response),
            Err(e) => {
                error!("Failed to parse structured response: {}", e);
                error!("Raw response: {}", content);

                // Create a fallback response with the new structure
                let default_category = EvaluationCategory {
                    status: "n/a".to_string(),
                    justification: "Could not parse response".to_string(),
                    suggestions: vec!["Please try again".to_string()],
                };

                let fallback = StructuredAnalysisResponse {
                    summary: "Unable to generate summary due to parsing error".to_string(),
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

    /// Custom evaluate a proposal with specific criteria
    async fn compute_custom_evaluation(
        &self,
        proposal: &Proposal,
        request: &CustomEvaluationRequest,
    ) -> Result<CustomEvaluationResponse> {
        // Generate custom prompt based on the request
        let custom_prompt: String = generate_custom_evaluation_prompt(request);

        // Log the generated prompt for debugging
        info!("Generated custom prompt: {}", custom_prompt);

        // We no longer need to serialize the proposal as JSON since the content is already in the request
        // Instead, we'll use the proposal's description directly in the user message
        let chat_request: ChatCompletionRequest = ChatCompletionRequest::builder()
            .model(self.config.ai_model_name.clone())
            .messages(vec![
                Message::new(Role::System, custom_prompt.as_str()),
                Message::new(Role::User, proposal.description.as_str()),
            ])
            .build()
            .map_err(Error::ChatBuilder)?;

        let response = self.openrouter.send_chat_completion(&chat_request).await?;

        let content = response.choices[0]
            .content()
            .ok_or(Error::Response(ResponseError::NoContent))?
            .to_string();

        // Log the raw response content for debugging
        debug!("Raw AI response: {}", content);

        // Extract and parse JSON from the response if it's wrapped in markdown code blocks
        match extract_json_from_markdown::<CustomEvaluationResponse>(&content) {
            Ok(custom_response) => Ok(custom_response),
            Err(e) => {
                error!("Failed to parse custom evaluation response: {}", e);
                error!("Raw response: {}", content);

                // Try to parse as a Value first to see what we're getting
                if let Ok(value) = serde_json::from_str::<serde_json::Value>(&content) {
                    error!("Response parsed as generic JSON: {}", value);
                }

                let default_evaluation = EvaluationResult::na("Could not parse response");

                // Create a fallback response with default fields
                // We always include the three default criteria
                let mut response_map: HashMap<String, EvaluationResult> = HashMap::new();

                // Add the default criteria
                response_map.extend([
                    (
                        "goals_and_motivation".to_string(),
                        default_evaluation.clone(),
                    ),
                    (
                        "measurable_outcomes".to_string(),
                        default_evaluation.clone(),
                    ),
                    ("budget".to_string(), default_evaluation.clone()),
                ]);

                // Try to parse custom criteria from the JSON string to add them to the fallback
                if let Ok(custom_criteria_value) =
                    serde_json::from_str::<serde_json::Value>(&request.custom_criteria)
                {
                    if let Some(criteria_array) = custom_criteria_value.as_array() {
                        response_map.extend(criteria_array.iter().filter_map(|criterion_value| {
                            criterion_value
                                .as_object()?
                                .get("name")?
                                .as_str()
                                .map(|name| {
                                    (
                                        name.to_lowercase().replace(' ', "_"),
                                        default_evaluation.clone(),
                                    )
                                })
                        }));
                    }
                }

                let fallback = CustomEvaluationResponse {
                    summary: "Unable to generate summary due to parsing error".to_string(),
                    response_map,
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
            .map_err(|e| Error::Internal(e.to_string()))?;

        let response = self
            .openrouter
            .send_chat_completion(&request)
            .await
            .map_err(|e| Error::Internal(e.to_string()))?;

        let content = response.choices[0]
            .content()
            .ok_or(Error::Internal("No content in response".to_string()))?
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
    
    /// Custom evaluate a proposal with specific criteria
    async fn custom_evaluate_proposal(
        &self,
        proposal: &Proposal,
        request: &CustomEvaluationRequest,
    ) -> Result<CustomEvaluationResponse> {
        self.compute_custom_evaluation(proposal, request).await
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
