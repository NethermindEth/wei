use agent::models::Proposal;
use agent::services::agent::AgentServiceTrait;

// Import the fixtures as proper modules
mod fixtures;
use fixtures::create_agent::{create_agent_service, validate_analysis};
use fixtures::proposals::get_proposals;

#[tokio::test]
async fn test_e2e_proposal_analysis() {
    let proposals_data = get_proposals();
    let proposal = Proposal {
        description: proposals_data[0].to_string(),
    };

    let agent_service = create_agent_service().await.unwrap();

    println!("Running analysis on first proposal...");
    let analysis = agent_service.analyze_proposal(&proposal).await.unwrap();
    validate_analysis(&analysis.data);

    println!("E2E test passed for proposal 1");
}

#[tokio::test]
async fn test_e2e_multiple_proposals() {
    let proposals_data = get_proposals();
    let agent_service = create_agent_service().await.unwrap();

    let max_proposals = std::cmp::min(3, proposals_data.len());
    for (i, proposal_text) in proposals_data.iter().enumerate().take(max_proposals) {
        let proposal = Proposal {
            description: proposal_text.to_string(),
        };
        let analysis = agent_service.analyze_proposal(&proposal).await.unwrap();
        validate_analysis(&analysis.data);

        println!("E2E test passed for proposal {}", i + 1);
    }
}

#[tokio::test]
async fn test_e2e_all_proposals() {
    let proposals_data = get_proposals();
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
        validate_analysis(&analysis.data);

        println!("Proposal {} analysis completed", i + 1);
        println!("---");
    }

    println!("All proposal tests completed successfully");
}
