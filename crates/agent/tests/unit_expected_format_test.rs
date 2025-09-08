use agent::models::analysis::{EvaluationCategory, StructuredAnalysisResponse};
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
        summary: "Proposal to reallocate $89,980 USD from Domain Allocator funds to the Hackathon Continuation Program to address a funding shortfall caused by token price changes.".to_string(),
        goals_and_motivation: EvaluationCategory {
            status: "pass".to_string(),
            justification: "The proposal clearly states its goal to address funding shortfall."
                .to_string(),
            suggestions: vec![],
        },
        measurable_outcomes: EvaluationCategory {
            status: "pass".to_string(),
            justification: "The proposal specifies the exact amount needed ($89,980 USD)."
                .to_string(),
            suggestions: vec![],
        },
        budget: EvaluationCategory {
            status: "pass".to_string(),
            justification: "The budget is clearly specified with exact amounts.".to_string(),
            suggestions: vec![],
        },
        technical_specifications: EvaluationCategory {
            status: "n/a".to_string(),
            justification:
                "This proposal is about fund reallocation, not technical implementation."
                    .to_string(),
            suggestions: vec![],
        },
        language_quality: EvaluationCategory {
            status: "pass".to_string(),
            justification: "The proposal is well-written and clearly communicates the need."
                .to_string(),
            suggestions: vec![],
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
        "summary": "",
        "goals_and_motivation": {
            "status": "",
            "justification": "",
            "suggestions": []
        },
        "measurable_outcomes": {
            "status": "",
            "justification": "",
            "suggestions": []
        },
        "budget": {
            "status": "",
            "justification": "",
            "suggestions": []
        },
        "technical_specifications": {
            "status": "",
            "justification": "",
            "suggestions": []
        },
        "language_quality": {
            "status": "",
            "justification": "",
            "suggestions": []
        }
    });

    // Check that the analysis matches the expected structure
    assert!(check_json_structure(&analysis_json, &expected_structure));

    // Validate each evaluation category
    validate_category(&analysis.goals_and_motivation, "Goals and motivation");
    validate_category(&analysis.measurable_outcomes, "Measurable outcomes");
    validate_category(&analysis.budget, "Budget");
    validate_category(
        &analysis.technical_specifications,
        "Technical specifications",
    );
    validate_category(&analysis.language_quality, "Language quality");
}

// Helper function to validate an evaluation category
fn validate_category(category: &EvaluationCategory, name: &str) {
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
