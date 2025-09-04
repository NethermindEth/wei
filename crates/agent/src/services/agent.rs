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

    /// Get proposal arguments with caching
    fn get_proposal_arguments(
        &self,
        proposal: &Proposal,
    ) -> impl Future<Output = Result<CachedResponse<crate::models::analysis::ProposalArguments>>>;

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

        self.cache_service
            .cache_or_compute(&query, || async {
                self.compute_proposal_analysis(proposal).await
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

    /// Get proposal arguments with caching
    async fn get_proposal_arguments(
        &self,
        proposal: &Proposal,
    ) -> Result<CachedResponse<crate::models::analysis::ProposalArguments>> {
        // Create a cache query based on the proposal content hash
        let query = CacheableQuery::new("/pre-filter/arguments", "POST").with_body(proposal)?;

        let proposal_clone = proposal.clone();
        self.cache_service
            .cache_or_compute(&query, || async {
                // Generate arguments separately since they're no longer part of the main analysis
                let prompt = r#"You are an expert in analyzing governance proposals. Your task is to extract balanced and comprehensive arguments for and against the following proposal.

For each side (for and against), provide 3-5 strong, substantive arguments that:
1. Are specific to this proposal's content and context
2. Consider technical, economic, governance, and community impact aspects
3. Are concise but complete (1-2 sentences each)
4. Are objective and factual rather than emotional

Your response MUST be in this exact JSON format:
{
  "for_proposal": ["argument 1", "argument 2", "argument 3", "argument 4", "argument 5"],
  "against": ["argument 1", "argument 2", "argument 3", "argument 4", "argument 5"]
}

Do not include any explanatory text, only the JSON object.
"#;

                let request = ChatCompletionRequest::builder()
                    .model(self.config.ai_model_name.clone())
                    .messages(vec![
                        Message::new(Role::System, prompt),
                        Message::new(Role::User, serde_json::to_string(&proposal_clone)?.as_str()),
                    ])
                    .temperature(0.2) // Lower temperature for more consistent, focused responses
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

                // Try to parse the response as ProposalArguments
                match serde_json::from_str::<crate::models::analysis::ProposalArguments>(cleaned_content) {
                    Ok(arguments) => {
                        // Ensure we have at least one argument on each side
                        if arguments.for_proposal.is_empty() || arguments.against.is_empty() {
                            let mut args = arguments;
                            if args.for_proposal.is_empty() {
                                args.for_proposal.push("No supporting arguments could be identified for this proposal".to_string());
                            }
                            if args.against.is_empty() {
                                args.against.push("No opposing arguments could be identified for this proposal".to_string());
                            }
                            Ok(args)
                        } else {
                            // Limit the number of arguments to a reasonable amount if we got too many
                            let mut args = arguments;
                            if args.for_proposal.len() > 7 {
                                args.for_proposal.truncate(7);
                            }
                            if args.against.len() > 7 {
                                args.against.truncate(7);
                            }
                            Ok(args)
                        }
                    },
                    Err(e) => {
                        error!("Failed to parse arguments response: {}", e);
                        error!("Raw response: {}", content);
                        error!("Cleaned response: {}", cleaned_content);
                        // Try to extract arguments using a more sophisticated approach
                        let mut for_args = Vec::new();
                        let mut against_args = Vec::new();

                        // Look for patterns that might indicate arguments
                        let lines: Vec<&str> = content.lines().collect();
                        let mut current_section: Option<&str> = None;

                        for line in lines {
                            let line_lower = line.trim().to_lowercase();

                            // Detect section headers
                            if line_lower.contains("for") || line_lower.contains("supporting") || line_lower.contains("pros") || line_lower.contains("pro:") {
                                current_section = Some("for");
                                continue;
                            } else if line_lower.contains("against") || line_lower.contains("opposing") || line_lower.contains("cons") || line_lower.contains("con:") {
                                current_section = Some("against");
                                continue;
                            }

                            // Extract argument points (often bullet points or numbered)
                            if line.trim().starts_with("-") || line.trim().starts_with("*") || 
                               (line.trim().len() > 2 && line.trim()[0..2].chars().all(|c| c.is_ascii_digit() || c == '.')) {
                                let arg = line.trim().trim_start_matches(|c: char| c == '-' || c == '*' || c == '.' || c.is_ascii_digit() || c.is_whitespace()).trim().to_string();
                                if !arg.is_empty() {
                                    match current_section {
                                        Some("for") => for_args.push(arg),
                                        Some("against") => against_args.push(arg),
                                        _ => {} // Ignore if we don't know which section we're in
                                    }
                                }
                            }
                        }

                        // If we couldn't extract anything meaningful, provide fallback
                        if for_args.is_empty() {
                            for_args.push("Could not extract supporting arguments from the response".to_string());
                        }
                        if against_args.is_empty() {
                            against_args.push("Could not extract opposing arguments from the response".to_string());
                        }

                        Ok(crate::models::analysis::ProposalArguments {
                            for_proposal: for_args,
                            against: against_args,
                        })
                    }
                }
            })
            .await
    }
}
