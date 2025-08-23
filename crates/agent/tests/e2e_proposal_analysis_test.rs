use std::cmp::min;
use std::env;

use agent::models::analysis::StructuredAnalysisResponse;
use agent::models::Proposal;
use agent::services::agent::{AgentService, AgentServiceTrait};
use agent::utils::error::Result;
use agent::Config;
use clap::Parser;
use dotenv::dotenv;

// Import the fixtures directly
mod fixtures {
    include!("fixtures/proposals.rs");
}

/// create agent
async fn create_agent_service() -> Result<AgentService> {
    // Load environment variables from .env file
    dotenv().ok();
    let api_key: String = match env::var("WEI_AGENT_OPEN_ROUTER_API_KEY") {
        Ok(key) if !key.trim().is_empty() => key,
        _ => panic!(
            "WEI_AGENT_OPEN_ROUTER_API_KEY environment variable must be set and non-empty for e2e tests.\n\n\
            Make sure your .env file contains WEI_AGENT_OPEN_ROUTER_API_KEY and WEI_AGENT_AI_MODEL_NAME\n\n\
            Get an API key from https://openrouter.ai/"
        ),
    };

    println!(
        "Using OpenRouter API key: {}...",
        &api_key[0..min(8, api_key.len())]
    );

    let args = vec![
        "".to_string(),
        "--ai-model-api-key".to_string(),
        api_key.clone(),
    ];
    let mut config = Config::parse_from(args);

    config.ai_model_name = match env::var("WEI_AGENT_AI_MODEL_NAME") {
        Ok(key) if !key.trim().is_empty() => key,
        _ => panic!(
            "WEI_AGENT_AI_MODEL_NAME environment variable must be set and non-empty for e2e tests.\n\n\
            Make sure your .env file contains WEI_AGENT_OPEN_ROUTER_API_KEY and WEI_AGENT_AI_MODEL_NAME"
        ),
    };
    config.database_url = "sqlite::memory:".to_string();
    config.api_key_auth_enabled = false;

    Ok(AgentService::new((), config))
}

/// validate the structure of analysis response
fn validate_analysis(analysis: &StructuredAnalysisResponse) {
    // Basic validation of required fields
    assert!(!analysis.verdict.is_empty(), "Verdict should not be empty");
    assert!(
        !analysis.conclusion.is_empty(),
        "Conclusion should not be empty"
    );

    // Validate proposal quality fields with more flexibility
    let q = &analysis.proposal_quality;
    assert!(
        !q.clarity_of_goals.is_empty(),
        "Clarity of goals should not be empty"
    );
    assert!(
        !q.completeness_of_sections.is_empty(),
        "Completeness should not be empty"
    );
    assert!(
        !q.level_of_detail.is_empty(),
        "Level of detail should not be empty"
    );
    assert!(
        !q.community_adaptability.is_empty(),
        "Community adaptability should not be empty"
    );

    // For array fields, check that they exist but don't require them to be non-empty
    // Different AI models might handle these fields differently
    println!("Assumptions made: {:?}", q.assumptions_made);
    println!("Missing elements: {:?}", q.missing_elements);

    // Validate submitter intentions fields with more flexibility
    let s = &analysis.submitter_intentions;
    assert!(
        !s.submitter_identity.is_empty(),
        "Submitter identity should not be empty"
    );

    // For array fields, print them but don't strictly require content
    println!("Inferred interests: {:?}", s.inferred_interests);
    println!("Social activity: {:?}", s.social_activity);
    println!("Strategic positioning: {:?}", s.strategic_positioning);
}

#[tokio::test]
async fn test_e2e_proposal_analysis() {
    let proposals_data = fixtures::get_proposals();
    let proposal = Proposal {
        description: proposals_data[0].to_string(),
    };

    let agent_service = create_agent_service().await.unwrap();

    println!("Running analysis on first proposal...");
    let analysis = agent_service.analyze_proposal(&proposal).await.unwrap();
    validate_analysis(&analysis);

    println!("E2E test passed for proposal 1: {}", analysis.verdict);
    println!("Conclusion: {}", analysis.conclusion);
}

#[tokio::test]
async fn test_e2e_multiple_proposals() {
    let proposals_data = fixtures::get_proposals();
    let agent_service = create_agent_service().await.unwrap();

    let max_proposals = std::cmp::min(3, proposals_data.len());
    for (i, proposal_text) in proposals_data.iter().enumerate().take(max_proposals) {
        let proposal = Proposal {
            description: proposal_text.to_string(),
        };
        let analysis = agent_service.analyze_proposal(&proposal).await.unwrap();
        validate_analysis(&analysis);

        println!(
            "E2E test passed for proposal {}: {}",
            i + 1,
            analysis.verdict
        );
    }
}

#[tokio::test]
async fn test_e2e_all_proposals() {
    let proposals_data = fixtures::get_proposals();
    let agent_service = create_agent_service().await.unwrap();

    println!(
        "Testing all {} proposals from fixtures",
        proposals_data.len()
    );

    for (i, proposal_text) in proposals_data.iter().enumerate() {
        let proposal = Proposal {
            description: proposal_text.to_string(),
        };

        println!("Running analysis on proposal {}...", i + 1);
        let analysis = agent_service.analyze_proposal(&proposal).await.unwrap();
        validate_analysis(&analysis);

        println!("Proposal {} verdict: {}", i + 1, analysis.verdict);
        println!("Conclusion: {}", analysis.conclusion);
        println!("---");
    }

    println!("All proposal tests completed successfully");
}
