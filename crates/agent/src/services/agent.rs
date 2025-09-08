//! Main agent service

use std::collections::HashMap;
use std::future::Future;

use openrouter_rs::{api::chat::ChatCompletionRequest, types::Role, Message, OpenRouterClient};
use serde_json;
use tracing::{debug, error, info};

use crate::models::analysis::{EvaluationCategory, StructuredAnalysisResponse};
use crate::models::custom_evaluation::{
    CustomEvaluationRequest, CustomEvaluationResponse, EvaluationResult,
};
use crate::models::deepresearch::{DeepResearchResponse, DeepResearchResult};
use crate::models::roadmap::{RoadmapApiResponse, RoadmapRequest, RoadmapResponse, RoadmapResult};
use crate::prompts::custom_evaluation::generate_custom_evaluation_prompt;
use crate::prompts::{ANALYZE_PROPOSAL_PROMPT, DEEP_RESEARCH_PROMPT, ROADMAP_GENERATION_PROMPT};
use crate::utils::error::{Error, ResponseError, Result};
use crate::utils::markdown::extract_json_from_markdown;

use crate::{
    db::{
        core::Database,
        repositories::{CacheRepository, CommunityRepository},
    },
    models::Proposal,
    services::cache::{CacheService, CacheableQuery, CachedResponse},
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
            .map_err(|e: openrouter_rs::error::OpenRouterError| Error::ChatBuilder(Box::new(e)))?;

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

    /// Generate a roadmap for a protocol/DAO/company with caching
    fn generate_roadmap(
        &self,
        request: &RoadmapRequest,
    ) -> impl Future<Output = Result<RoadmapApiResponse>>;

    /// Get cached roadmap results
    fn get_cached_roadmap(
        &self,
        request: &RoadmapRequest,
    ) -> impl Future<Output = Result<Option<RoadmapApiResponse>>>;
}

impl AgentService {
    /// Helper function to find the end of a JSON object by counting braces
    fn find_json_end(content: &str) -> Option<usize> {
        let mut brace_count = 0;
        let mut in_string = false;
        let mut escaped = false;
        let mut found_start = false;

        for (i, ch) in content.char_indices() {
            if escaped {
                escaped = false;
                continue;
            }

            if ch == '\\' {
                escaped = true;
                continue;
            }

            if ch == '"' {
                in_string = !in_string;
                continue;
            }

            if !in_string {
                if ch == '{' {
                    found_start = true;
                    brace_count += 1;
                } else if ch == '}' {
                    brace_count -= 1;
                    if brace_count == 0 && found_start {
                        return Some(i + 1);
                    }
                }
            }
        }

        // If we never found a closing brace but we have content, return the full length
        if found_start && brace_count > 0 {
            Some(content.len())
        } else {
            None
        }
    }

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
            .map_err(|e: openrouter_rs::error::OpenRouterError| Error::ChatBuilder(Box::new(e)))?;

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
            .map_err(|e| Error::ChatBuilder(Box::new(e)))?;

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

    /// Compute the actual roadmap generation (without caching)
    async fn compute_roadmap(&self, request: &RoadmapRequest) -> Result<RoadmapResponse> {
        // Construct the user prompt with the specific request parameters
        let user_prompt = format!(
            "SUBJECT = \"{}\", KIND = \"{}\", SCOPE = \"{}\"",
            request.subject, request.kind, request.scope
        );

        let mut user_prompt = user_prompt;
        if let Some(from) = &request.from {
            user_prompt.push_str(&format!(", FROM = \"{}\"", from));
        }
        if let Some(to) = &request.to {
            user_prompt.push_str(&format!(", TO = \"{}\"", to));
        }
        user_prompt.push_str(". Produce JSON per *Outcome‑Driven Roadmap Schema v1.0.0*. Ensure every intervention is linked to a problem, or create a problem, or mark link as `unclear`. Validate whether each intervention is live/stale/abandoned using explicit signals and citations. IMPORTANT: Return ONLY the JSON object - no markdown code blocks, no backticks, no explanatory text. Your response must start with { and end with }.");

        let request_builder = ChatCompletionRequest::builder()
            .model(self.config.roadmap_model_name.clone()) // Use configurable model for roadmap generation
            .messages(vec![
                Message::new(Role::System, ROADMAP_GENERATION_PROMPT),
                Message::new(Role::User, &user_prompt),
            ])
            .build()
            .map_err(|e| crate::utils::error::Error::Internal(e.to_string()))?;

        let response = self
            .openrouter
            .send_chat_completion(&request_builder)
            .await
            .map_err(|e| crate::utils::error::Error::Internal(e.to_string()))?;

        let content = response.choices[0]
            .content()
            .ok_or(crate::utils::error::Error::Internal(
                "No content in response".to_string(),
            ))?
            .to_string();

        // Clean the response content - remove markdown code blocks if present
        let cleaned_content = if content.contains("```json") {
            // Find the start and end of the JSON block
            if let Some(start) = content.find("```json") {
                let json_start = start + 7; // Length of "```json"
                if let Some(end) = content[json_start..].find("```") {
                    content[json_start..json_start + end].trim()
                } else {
                    // If no closing ```, try to find the end of the JSON object
                    let json_content = &content[json_start..];
                    if let Some(json_end) = Self::find_json_end(json_content) {
                        json_content[..json_end].trim()
                    } else {
                        json_content.trim()
                    }
                }
            } else {
                content.trim()
            }
        } else if content.contains("```") {
            // Find the start and end of the code block
            if let Some(start) = content.find("```") {
                let code_start = start + 3; // Length of "```"
                if let Some(end) = content[code_start..].find("```") {
                    content[code_start..code_start + end].trim()
                } else {
                    // If no closing ```, try to find the end of the JSON object
                    let code_content = &content[code_start..];
                    if let Some(json_end) = Self::find_json_end(code_content) {
                        code_content[..json_end].trim()
                    } else {
                        code_content.trim()
                    }
                }
            } else {
                content.trim()
            }
        } else {
            // Try to find JSON object boundaries even without code blocks
            if let Some(json_start) = content.find('{') {
                let json_content = &content[json_start..];
                if let Some(json_end) = Self::find_json_end(json_content) {
                    json_content[..json_end].trim()
                } else {
                    json_content.trim()
                }
            } else {
                content.trim()
            }
        };

        // Parse the JSON response into our structured format
        let roadmap_response = match serde_json::from_str::<RoadmapResponse>(cleaned_content) {
            Ok(parsed_response) => parsed_response,
            Err(e) => {
                // Log detailed error information for debugging
                error!("Failed to parse roadmap response: {}", e);
                error!("Raw response length: {} chars", content.len());
                error!("Cleaned response length: {} chars", cleaned_content.len());
                error!(
                    "Raw response (first 500 chars): {}",
                    &content[..content.len().min(500)]
                );
                error!(
                    "Cleaned response (first 500 chars): {}",
                    &cleaned_content[..cleaned_content.len().min(500)]
                );

                // Analyze JSON structure issues
                let open_braces = cleaned_content.matches('{').count();
                let close_braces = cleaned_content.matches('}').count();
                error!(
                    "Brace count - Open: {}, Close: {}",
                    open_braces, close_braces
                );

                // Try to find the last complete JSON object
                if let Some(last_brace) = cleaned_content.rfind('}') {
                    let potential_json = &cleaned_content[..last_brace + 1];
                    info!("Attempting to parse truncated JSON");

                    // Try parsing the truncated version
                    match serde_json::from_str::<RoadmapResponse>(potential_json) {
                        Ok(parsed) => {
                            info!("Successfully parsed truncated JSON");
                            parsed
                        }
                        Err(e2) => {
                            error!("Failed to parse truncated JSON: {}", e2);
                            // Instead of silently creating a fallback response, return a proper error
                            return Err(crate::utils::error::Error::Internal(format!(
                                "Failed to parse roadmap response: {}. Original error: {}",
                                e2, e
                            )));
                        }
                    }
                } else {
                    // Return a proper error instead of a silent fallback
                    return Err(crate::utils::error::Error::Internal(format!(
                        "Failed to parse roadmap response: {}",
                        e
                    )));
                }
            }
        };

        Ok(roadmap_response)
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

    /// Generate a roadmap for a protocol/DAO/company with caching
    async fn generate_roadmap(&self, request: &RoadmapRequest) -> Result<RoadmapApiResponse> {
        // Create a cache query based on the request parameters
        let mut query_params = std::collections::HashMap::new();
        query_params.insert("subject".to_string(), request.subject.clone());
        query_params.insert("kind".to_string(), request.kind.clone());
        query_params.insert("scope".to_string(), request.scope.clone());

        let query = CacheableQuery::new("/roadmap", "POST")
            .with_params(query_params)
            .with_body(request)?;

        let request_clone = request.clone();
        let cached_response = self
            .cache_service
            .cache_or_compute(&query, || async {
                let roadmap_response = self.compute_roadmap(&request_clone).await?;

                // Create the result with proper metadata
                let result = RoadmapResult {
                    id: uuid::Uuid::new_v4(),
                    request: request_clone,
                    response: roadmap_response,
                    created_at: chrono::Utc::now(),
                    expires_at: chrono::Utc::now() + chrono::Duration::hours(24),
                };

                Ok(RoadmapApiResponse {
                    result,
                    cache_info: None,
                })
            })
            .await?;

        Ok(cached_response.data)
    }

    /// Get cached roadmap results
    async fn get_cached_roadmap(
        &self,
        request: &RoadmapRequest,
    ) -> Result<Option<RoadmapApiResponse>> {
        // Create a cacheable query for the roadmap request
        let mut query = CacheableQuery::new("/roadmap", "GET")
            .with_param("subject", &request.subject)
            .with_param("kind", &request.kind)
            .with_param("scope", &request.scope);

        // Add optional date parameters if present
        if let Some(from) = &request.from {
            query = query.with_param("from", from);
        }

        if let Some(to) = &request.to {
            query = query.with_param("to", to);
        }

        // Generate the roadmap to ensure it's cached
        // This is a workaround since we don't have direct access to check the cache
        // The POST endpoint will return cached data if available
        debug!(
            "Attempting to retrieve cached roadmap for query: {}",
            query.cache_description()
        );

        // For now, we'll return None and let the POST endpoint handle caching
        // In a future update, we could implement a proper cache check mechanism
        Ok(None)
    }
}
