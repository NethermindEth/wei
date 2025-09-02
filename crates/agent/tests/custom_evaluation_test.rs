use reqwest::{Client, StatusCode};
use serde_json::{json, Value};
use std::env;

/// Get API configuration for tests
/// Returns (api_url, api_key) if configuration is valid, None otherwise
fn get_test_api_config() -> Option<(String, String)> {
    let api_url = env::var("API_URL").unwrap_or_else(|_| "http://localhost:8000".to_string());
    
    // Check if the API keys environment variable is set
    let api_keys = match env::var("WEI_AGENT_API_KEYS") {
        Ok(keys) => keys,
        Err(_) => {
            println!("Skipping test: WEI_AGENT_API_KEYS environment variable not set");
            return None;
        }
    };
    
    // Get the first API key from the comma-separated list
    let api_key = match api_keys.split(',').next() {
        Some(key) => key.trim().to_string(),
        None => {
            println!("Skipping test: WEI_AGENT_API_KEYS is empty");
            return None;
        }
    };
    
    Some((api_url, api_key))
}

#[tokio::test]
#[ignore = "Requires environment variables to be set"]
async fn test_custom_evaluation_endpoint() {
    // Get API configuration for the test
    let (api_url, api_key) = match get_test_api_config() {
        Some(config) => config,
        None => return, // Test will be skipped if config can't be loaded
    };
    
    let client = Client::new();

    // Sample proposal content
    let proposal_content = "This is a sample proposal for testing custom evaluation. It includes goals, budget, and team information.";

    // Create a custom evaluation request matching the current API structure
    let request_body = json!({
        "content": proposal_content,
        "custom_criteria": "I want to evaluate the team background and the deliverable dates"
    });

    // Send the request to the custom evaluation endpoint using PUT method
    let response = client
        .put(format!("{}/pre-filter", api_url))
        .header("x-api-key", &api_key)
        .header("Content-Type", "application/json")
        .json(&request_body)
        .send()
        .await
        .expect("Failed to send request");

    // Check the response status
    assert_eq!(response.status(), StatusCode::OK);

    // Parse and validate the response
    let response_body: Value = response.json().await.expect("Failed to parse response");

    // Verify the response structure matches the CustomEvaluationResponse
    assert!(
        response_body.get("summary").is_some(),
        "Response should contain a summary"
    );

    // Check if response_map is included
    let response_map = response_body
        .get("response_map")
        .expect("Response should contain response_map");

    // The actual criteria keys will depend on how the AI interprets the custom_criteria string
    // but we can check for common expected formats
    let expected_keys = ["team_background", "deliverable_dates"];

    // Check if at least one of the expected keys is present
    let has_expected_key = expected_keys
        .iter()
        .any(|&key| response_map.get(key).is_some());
    assert!(
        has_expected_key,
        "Response should include at least one of the expected criteria keys"
    );

    // Check the structure of a criterion result if any exist
    if let Some(criterion) = expected_keys.iter().find_map(|&key| response_map.get(key)) {
        assert!(
            criterion.get("status").is_some(),
            "Criterion should have a status"
        );
        assert!(
            criterion.get("justification").is_some(),
            "Criterion should have a justification"
        );
        assert!(
            criterion.get("suggestions").is_some(),
            "Criterion should have suggestions"
        );
    }

    println!("Custom evaluation test passed successfully!");
}
