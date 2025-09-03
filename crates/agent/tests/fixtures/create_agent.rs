use std::env;

use agent::models::analysis::StructuredAnalysisResponse;
use agent::services::agent::{AgentService, AgentServiceTrait};
use agent::utils::error::Error::Internal;
use agent::utils::error::Result;
use agent::Config;
use clap::Parser;
use dotenv::dotenv;
use openrouter_rs::{api::chat::ChatCompletionRequest, types::Role, Message, OpenRouterClient};
use sqlx::postgres::PgPoolOptions;
/// Creates an agent service for e2e testing
///
/// This function creates a real agent service that can be used in e2e tests.
/// It requires the following environment variables to be set:
/// - WEI_AGENT_OPEN_ROUTER_API_KEY: API key for OpenRouter
/// - WEI_AGENT_AI_MODEL_NAME: Name of the AI model to use
///
/// Example usage:
/// ```
/// let agent = create_agent_service().await?;
/// let analysis = agent.analyze_proposal(&proposal).await?;
/// ```
pub async fn create_agent_service() -> Result<AgentService> {
    // Load environment variables from .env file
    dotenv().ok();

    // Check if OpenRouter API key is set in environment
    if env::var("WEI_AGENT_OPEN_ROUTER_API_KEY")
        .unwrap_or_default()
        .trim()
        .is_empty()
    {
        panic!(
            "WEI_AGENT_OPEN_ROUTER_API_KEY environment variable must be set and non-empty for e2e tests.\n\n\
            Make sure your .env file contains WEI_AGENT_OPEN_ROUTER_API_KEY and WEI_AGENT_AI_MODEL_NAME\n\n\
            Get an API key from https://openrouter.ai/"
        );
    }

    // Create config - it will automatically read API key from environment
    let mut config = Config::parse_from(vec!["".to_string()]);

    // Get AI model name from environment
    config.ai_model_name = env::var("WEI_AGENT_AI_MODEL_NAME")
    .map(|key| {
        let trimmed = key.trim().to_string();
        if trimmed.is_empty() {
            panic!(
                "WEI_AGENT_AI_MODEL_NAME environment variable must be set and non-empty for e2e tests.\n\n\
                 Make sure your .env file contains WEI_AGENT_OPEN_ROUTER_API_KEY and WEI_AGENT_AI_MODEL_NAME"
            )
        }
        trimmed
    })
    .expect(
        "WEI_AGENT_AI_MODEL_NAME environment variable must be set and non-empty for e2e tests.\n\n\
         Make sure your .env file contains WEI_AGENT_OPEN_ROUTER_API_KEY and WEI_AGENT_AI_MODEL_NAME"
    );

    // For testing, we'll use a mock database connection
    // In a real test environment, you would set up a test database
    config.database_url = "postgres://postgres:postgres@localhost:5432/postgres".to_string();
    config.api_key_auth_enabled = false;

    // Create a database pool for testing
    // Note: In a real test environment, this would connect to an actual test database
    // For now, we'll create a pool that may not actually connect but will satisfy the type requirements
    let db = PgPoolOptions::new()
        .max_connections(5)
        .connect_lazy(&config.database_url)
        .expect("Failed to create database connection pool");

    Ok(AgentService::new(db, config))
}

/// Helper function to validate an evaluation category
#[allow(dead_code)]
pub fn validate_evaluation_category(
    category: &agent::models::analysis::EvaluationCategory,
    name: &str,
) {
    assert!(
        !category.status.is_empty(),
        "{} status should not be empty",
        name
    );

    // If status is "fail", there should be suggestions
    if category.status == "fail" {
        assert!(
            !category.suggestions.is_empty(),
            "{} should have suggestions when failing",
            name
        );
    }

    // If status is "n/a", there should be a justification
    if category.status == "n/a" {
        assert!(
            !category.justification.is_empty(),
            "{} should have justification when n/a",
            name
        );
    }

    println!("{} status: {}", name, category.status);
    if !category.justification.is_empty() {
        println!("{} justification: {}", name, category.justification);
    }
    if !category.suggestions.is_empty() {
        println!("{} suggestions: {:?}", name, category.suggestions);
    }
}

/// Helper function to validate the entire analysis response
#[allow(dead_code)]
pub fn validate_analysis(analysis: &StructuredAnalysisResponse) {
    // Validate each evaluation category
    validate_evaluation_category(&analysis.goals_and_motivation, "Goals and motivation");
    validate_evaluation_category(&analysis.measurable_outcomes, "Measurable outcomes");
    validate_evaluation_category(&analysis.budget, "Budget");
    validate_evaluation_category(
        &analysis.technical_specifications,
        "Technical specifications",
    );
    validate_evaluation_category(&analysis.language_quality, "Language quality");
}

/// Query the agent with a prompt and get a plain text response
///
/// This function sends a direct query to the agent and returns a plain text response
/// without the structured format used by analyze_proposal.
///
/// This is useful for asking direct questions like yes/no questions.
#[allow(dead_code)]
pub async fn query_agent(agent_service: &AgentService, prompt: &str) -> Result<String> {
    // Create a simple proposal with the prompt as the description
    let proposal = agent::models::Proposal {
        description: prompt.to_string(),
    };

    // Use the analyze_proposal method from the AgentServiceTrait
    let analysis = AgentServiceTrait::analyze_proposal(agent_service, &proposal).await?;

    // Extract the most relevant text from the analysis
    // Start with the justification from goals_and_motivation
    let mut response = analysis.data.goals_and_motivation.justification.clone();

    // If that's empty, try other fields
    if response.trim().is_empty() {
        response = analysis.data.goals_and_motivation.suggestions.join(". ");
    }

    if response.trim().is_empty() {
        response = analysis.data.measurable_outcomes.justification.clone();
    }
    if response.trim().is_empty() {
        response = analysis.data.budget.justification.clone();
    }

    if response.trim().is_empty() {
        response = analysis.data.technical_specifications.justification.clone();
    }

    if response.trim().is_empty() {
        response = analysis.data.language_quality.justification.clone();
    }

    // If we still have an empty response, return a default message
    if response.trim().is_empty() {
        response = "No relevant information found".to_string();
    }

    Ok(response)
}

/// Direct query function that bypasses the structured analysis response
///
/// This function sends a direct query to the OpenRouter API and returns the raw response
/// This is more suitable for direct question answering without the constraints of the
/// structured analysis format.
#[allow(dead_code)]
pub async fn direct_query_agent(_agent_service: &AgentService, prompt: &str) -> Result<String> {
    // Get the API key and model name from environment variables
    let api_key = std::env::var("WEI_AGENT_OPEN_ROUTER_API_KEY")
        .map_err(|_| Internal("Missing OpenRouter API key".to_string()))?;

    let model_name =
        std::env::var("WEI_AGENT_AI_MODEL_NAME").unwrap_or_else(|_| "openai/gpt-4o".to_string());

    // Create an OpenRouter client
    let client = OpenRouterClient::builder()
        .api_key(api_key)
        .build()
        .map_err(|e| Internal(e.to_string()))?;

    // Create a system message that instructs the model to answer directly
    let system_message = Message::new(
        Role::System,
        "You are a helpful assistant that answers questions directly and concisely. \
        For yes/no questions, always start your answer with 'yes' or 'no' followed by a brief explanation. \
        For other questions, provide a direct answer based solely on the information provided."
    );

    // Create a user message with the prompt
    let user_message = Message::new(Role::User, prompt);

    // Create a chat completion request
    let request = ChatCompletionRequest::builder()
        .model(model_name)
        .messages(vec![system_message, user_message])
        .build()
        .map_err(|e| Internal(e.to_string()))?;

    // Send the request to the OpenRouter API
    let response = client
        .send_chat_completion(&request)
        .await
        .map_err(|e| Internal(e.to_string()))?;

    // Extract the content from the response
    let content = response.choices[0]
        .content()
        .ok_or(Internal("No content in response".to_string()))?
        .to_string();

    Ok(content)
}
