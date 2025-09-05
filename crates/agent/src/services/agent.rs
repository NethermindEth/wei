//! Main agent service

use std::future::Future;

use openrouter_rs::{api::chat::ChatCompletionRequest, types::Role, Message, OpenRouterClient};
use serde_json;
use tracing::error;

use crate::models::analysis::{EvaluationCategory, StructuredAnalysisResponse};
use crate::models::deepresearch::{DeepResearchResponse, DeepResearchResult};
use crate::models::roadmap::{RoadmapApiResponse, RoadmapRequest, RoadmapResponse, RoadmapResult};
use crate::prompts::{ANALYZE_PROPOSAL_PROMPT, DEEP_RESEARCH_PROMPT, ROADMAP_GENERATION_PROMPT};
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
            .model("perplexity/sonar-pro".to_string()) // Use Sonar DeepResearch Pro model for comprehensive research
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
                error!("Failed to parse roadmap response: {}", e);
                error!("Raw response length: {} chars", content.len());
                error!("Cleaned response length: {} chars", cleaned_content.len());
                error!(
                    "Raw response (first 2000 chars): {}",
                    &content[..content.len().min(2000)]
                );
                error!(
                    "Cleaned response (first 2000 chars): {}",
                    &cleaned_content[..cleaned_content.len().min(2000)]
                );

                // Try to find where the JSON parsing failed
                error!("JSON parsing error details: {}", e);

                // Check if the JSON is properly closed
                let open_braces = cleaned_content.matches('{').count();
                let close_braces = cleaned_content.matches('}').count();
                error!(
                    "Brace count - Open: {}, Close: {}",
                    open_braces, close_braces
                );

                // Check if the response ends properly
                let trimmed = cleaned_content.trim();
                if !trimmed.ends_with('}') {
                    error!(
                        "Response doesn't end with '}}' - last 100 chars: {}",
                        &trimmed[trimmed.len().saturating_sub(100)..]
                    );
                }

                // Try to find the last complete JSON object
                if let Some(last_brace) = cleaned_content.rfind('}') {
                    let potential_json = &cleaned_content[..last_brace + 1];
                    error!(
                        "Attempting to parse truncated JSON (first {} chars): {}",
                        potential_json.len(),
                        &potential_json[..potential_json.len().min(500)]
                    );

                    // Try parsing the truncated version
                    match serde_json::from_str::<RoadmapResponse>(potential_json) {
                        Ok(truncated_response) => {
                            error!("Successfully parsed truncated JSON! Using truncated response.");
                            return Ok(truncated_response);
                        }
                        Err(truncated_e) => {
                            error!("Truncated JSON also failed to parse: {}", truncated_e);
                        }
                    }
                }

                // Create a fallback response with minimal structure
                RoadmapResponse {
                    schema_version: "1.0.0".to_string(),
                    domain: crate::models::roadmap::Domain {
                        name: request.subject.clone(),
                        kind: request.kind.clone(),
                        scope: request.scope.clone(),
                        as_of: chrono::Utc::now().format("%Y-%m-%d").to_string(),
                        research_window: if request.from.is_some() || request.to.is_some() {
                            Some(crate::models::roadmap::ResearchWindow {
                                from: request
                                    .from
                                    .clone()
                                    .unwrap_or_else(|| "2024-01-01".to_string()),
                                to: request.to.clone().unwrap_or_else(|| {
                                    chrono::Utc::now().format("%Y-%m-%d").to_string()
                                }),
                            })
                        } else {
                            None
                        },
                    },
                    streams: vec!["General".to_string()],
                    fitness_functions: vec![],
                    problems: vec![],
                    interventions: vec![],
                    proposals: None,
                    links: vec![],
                    sources: vec![],
                    metadata: Some(crate::models::roadmap::Metadata {
                        generator: Some("Wei Agent".to_string()),
                        generated_at: Some(chrono::Utc::now().to_rfc3339()),
                        notes: Some("Fallback response due to parsing error".to_string()),
                    }),
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
        _request: &RoadmapRequest,
    ) -> Result<Option<RoadmapApiResponse>> {
        // The POST endpoint handles caching automatically through cache_or_compute
        // This GET endpoint is not needed since POST already returns cached data
        Ok(None)
    }
}
