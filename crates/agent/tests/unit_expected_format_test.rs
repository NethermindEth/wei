use agent::models::analysis::{ProposalQuality, StructuredAnalysisResponse, SubmitterIntentions};
use agent::models::Proposal;
use agent::utils::error::Result;
use serde_json::{json, Value};

// Include proposal fixtures directly
mod fixtures {
    pub fn get_proposals() -> Vec<&'static str> {
        // Proposal 1 - Arbitrum Hackathon Continuation Program
        let proposal_1 = r#"Abstract
Arbitrum lacks an efficient mechanism to swap funds for projects, which has led to multiple challenges for service providers around token price changes. Specifically, the Hackathon Continuation Program is currently underfunded by $89,980 USD due to token price drop before RnDAO received any funds.

Beyond usual market risks, the program faced prolonged market risks due to delays as we worked with the Arbitrum Foundation on an improved fund management system for DAO-led investments, creating a valuable process template for the Arbitrum ecosystem, but exposing us to this situation.

This proposal suggests using a portion of the Domain Allocator (i.e. Questbook grant program) funds left over from the season 1 (a bit over $200k, due to be returned to the DAO) to "top up" the Hackathon Continuation Program and allow it to continue as approved by the DAO."#;

        vec![proposal_1]
    }
}

// Helper function to recursively check if a JSON structure matches the expected format
fn check_json_structure(actual: &Value, expected: &Value) -> bool {
    match (actual, expected) {
        (Value::Object(actual_obj), Value::Object(expected_obj)) => {
            // Check if all expected keys exist in the actual object
            for (key, expected_value) in expected_obj {
                match actual_obj.get(key) {
                    Some(actual_value) => {
                        if !check_json_structure(actual_value, expected_value) {
                            return false;
                        }
                    }
                    None => return false,
                }
            }
            true
        }
        (Value::Array(actual_arr), Value::Array(expected_arr)) => {
            if expected_arr.is_empty() {
                // If the expected array is empty, we just check that the actual array exists
                true
            } else {
                // If the expected array has items, we check that the actual array has at least one item
                // and that each item in the actual array matches the structure of the first item in the expected array
                !actual_arr.is_empty()
                    && actual_arr
                        .iter()
                        .all(|item| check_json_structure(item, &expected_arr[0]))
            }
        }
        (Value::String(_), Value::String(_)) => true,
        (Value::Number(_), Value::Number(_)) => true,
        (Value::Bool(_), Value::Bool(_)) => true,
        (Value::Null, Value::Null) => true,
        _ => false,
    }
}

// Simple mock agent service for testing
struct MockAgentService {
    response: Option<StructuredAnalysisResponse>,
}

impl MockAgentService {
    fn new() -> Self {
        Self { response: None }
    }

    fn expect_analyze_proposal(&mut self, response: StructuredAnalysisResponse) {
        self.response = Some(response);
    }

    async fn analyze_proposal(&self, _proposal: &Proposal) -> Result<StructuredAnalysisResponse> {
        if let Some(response) = &self.response {
            Ok(response.clone())
        } else {
            Err(agent::utils::error::Error::Internal(
                "No response configured".to_string(),
            ))
        }
    }
}

#[tokio::test]
async fn test_expected_format() {
    // Create a mock agent service
    let mut mock_agent_service = MockAgentService::new();

    // Get the test proposal
    let proposal_text = fixtures::get_proposals()[0];

    // Create a proposal from the test proposal
    let proposal = Proposal {
        description: proposal_text.to_string(),
    };

    // Create a response with the expected format
    let response = StructuredAnalysisResponse {
        verdict: "Approve".to_string(),
        conclusion:
            "This proposal addresses a funding shortfall for the Hackathon Continuation Program."
                .to_string(),
        proposal_quality: ProposalQuality {
            clarity_of_goals: "The proposal clearly states its goal.".to_string(),
            completeness_of_sections: "The proposal includes an abstract and rationale."
                .to_string(),
            level_of_detail: "The proposal provides specific details about the funding shortfall."
                .to_string(),
            assumptions_made: vec![
                "The Domain Allocator funds are available for reallocation.".to_string()
            ],
            missing_elements: vec!["Detailed timeline for fund transfer.".to_string()],
            community_adaptability: "The proposal addresses a community need.".to_string(),
        },
        submitter_intentions: SubmitterIntentions {
            submitter_identity: "The submitter appears to be associated with RnDAO.".to_string(),
            inferred_interests: vec![
                "Ensuring the continuation of the Hackathon Continuation Program.".to_string(),
            ],
            social_activity: vec![
                "Working with the Arbitrum Foundation on fund management systems.".to_string(),
            ],
            strategic_positioning: vec!["Positioning this as a one-time solution.".to_string()],
        },
    };

    // Set up the mock to expect a call to analyze_proposal
    mock_agent_service.expect_analyze_proposal(response);

    // Call the analyze_proposal method
    let result = mock_agent_service.analyze_proposal(&proposal).await;

    // Check that the result is successful
    assert!(result.is_ok());

    // Get the analysis response
    let analysis = result.unwrap();

    // Convert the analysis to JSON
    let analysis_json = serde_json::to_value(&analysis).unwrap();

    // Define the expected JSON structure
    let expected_structure = json!({
        "verdict": "",
        "conclusion": "",
        "proposal_quality": {
            "clarity_of_goals": "",
            "completeness_of_sections": "",
            "level_of_detail": "",
            "assumptions_made": [],
            "missing_elements": [],
            "community_adaptability": ""
        },
        "submitter_intentions": {
            "submitter_identity": "",
            "inferred_interests": [],
            "social_activity": [],
            "strategic_positioning": []
        }
    });

    // Check that the analysis matches the expected structure
    assert!(check_json_structure(&analysis_json, &expected_structure));

    // Check that specific fields are non-empty
    assert!(!analysis.verdict.is_empty());
    assert!(!analysis.conclusion.is_empty());
    assert!(!analysis.proposal_quality.clarity_of_goals.is_empty());
    assert!(!analysis
        .proposal_quality
        .completeness_of_sections
        .is_empty());
    assert!(!analysis.proposal_quality.level_of_detail.is_empty());
    assert!(!analysis.proposal_quality.community_adaptability.is_empty());
    assert!(!analysis.submitter_intentions.submitter_identity.is_empty());

    // Check that array fields have at least one item
    assert!(!analysis.proposal_quality.assumptions_made.is_empty());
    assert!(!analysis.proposal_quality.missing_elements.is_empty());
    assert!(!analysis.submitter_intentions.inferred_interests.is_empty());
    assert!(!analysis.submitter_intentions.social_activity.is_empty());
    assert!(!analysis
        .submitter_intentions
        .strategic_positioning
        .is_empty());
}
