//! Main agent service

use std::future::Future;
use std::collections::HashMap;

use openrouter_rs::{api::chat::ChatCompletionRequest, types::Role, Message, OpenRouterClient};
use serde_json;
use tracing::{error, info};

use crate::models::analysis::{ StructuredAnalysisResponse};
 use crate::models::custom_evaluation::EvaluationResult;
use crate::models::custom_evaluation::{CustomEvaluationRequest, CustomEvaluationResponse};
use crate::prompts::custom_evaluation::generate_custom_evaluation_prompt;
use crate::prompts::ANALYZE_PROPOSAL_PROMPT;
use crate::utils::error::{Error, Result};

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
        let openrouter: OpenRouterClient = OpenRouterClient::builder()
            .api_key(config.ai_model_api_key.clone())
            .build()
            .map_err(|e| Error::Internal(e.to_string()))?;

        Ok(openrouter)
    }
}

/// Trait for the agent service
pub trait AgentServiceTrait {
    /// Analyze a proposal
    fn analyze_proposal(
        &self,
        proposal: &Proposal,
    ) -> impl Future<Output = Result<StructuredAnalysisResponse>>;

    /// Custom evaluate a proposal with specific criteria
    fn custom_evaluate_proposal(
        &self,
        proposal: &Proposal,
        request: &CustomEvaluationRequest,
    ) -> impl Future<Output = Result<CustomEvaluationResponse>>;
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

        // Parse the JSON response into our structured format
        match serde_json::from_str::<StructuredAnalysisResponse>(&content) {
            Ok(structured_response) => Ok(structured_response),
            Err(e) => {
                error!("Failed to parse structured response: {}", e);
                error!("Raw response: {}", content);

                // Create a fallback response with the new structure
                use crate::models::analysis::EvaluationCategory;
                let default_category = EvaluationCategory::na("Could not parse response");

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
    async fn custom_evaluate_proposal(
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
            .map_err(|e| Error::Internal(e.to_string()))?;

        let response = self
            .openrouter
            .send_chat_completion(&chat_request)
            .await
            .map_err(|e| Error::Internal(e.to_string()))?;

        let content = response.choices[0]
            .content()
            .ok_or(Error::Internal("No content in response".to_string()))?
            .to_string();

        // Log the raw response content for debugging
        info!("Raw AI response: {}", content);

        // Try to extract JSON from the response if it's wrapped in markdown code blocks
        let json_content = if content.contains("```json") && content.contains("```") {
            let start = content.find("```json").map(|i| i + 7).unwrap_or(0);
            let end = content[start..]
                .find("```")
                .map(|i| start + i)
                .unwrap_or(content.len());
            content[start..end].trim().to_string()
        } else {
            content.clone()
        };

        // Parse the JSON response into our custom evaluation format
        match serde_json::from_str::<CustomEvaluationResponse>(&json_content) {
            Ok(custom_response) => Ok(custom_response),
            Err(e) => {
                error!("Failed to parse custom evaluation response: {}", e);
                error!("Raw response: {}", content);
                error!("Extracted JSON: {}", json_content);

                // Try to parse as a Value first to see what we're getting
                if let Ok(value) = serde_json::from_str::<serde_json::Value>(&json_content) {
                    error!("Response parsed as generic JSON: {}", value);
                }

               
                let default_evaluation = EvaluationResult::na("Could not parse response");

                // Create a fallback response with default fields
                // We always include the three default criteria
                let mut response_map: HashMap<String, EvaluationResult> = HashMap::new();

                // Add the default criteria
                response_map.insert(
                    "goals_and_motivation".to_string(),
                    default_evaluation.clone(),
                );
                response_map.insert(
                    "measurable_outcomes".to_string(),
                    default_evaluation.clone(),
                );
                response_map.insert("budget".to_string(), default_evaluation.clone());

                // Try to parse custom criteria from the JSON string to add them to the fallback
                if let Ok(custom_criteria_value) =
                    serde_json::from_str::<serde_json::Value>(&request.custom_criteria)
                {
                    if let Some(criteria_array) = custom_criteria_value.as_array() {
                        for criterion_value in criteria_array {
                            if let Some(criterion_obj) = criterion_value.as_object() {
                                if let Some(name) =
                                    criterion_obj.get("name").and_then(|v| v.as_str())
                                {
                                    let field_name = name.to_lowercase().replace(" ", "_");
                                    response_map.insert(field_name, default_evaluation.clone());
                                }
                            }
                        }
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
}
