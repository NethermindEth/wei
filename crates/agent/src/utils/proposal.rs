use crate::models::deepresearch::DeepResearchResponse;
use crate::models::Proposal;

/// Extract a relevant topic from a proposal for deep research
pub fn extract_topic_from_proposal(proposal: &Proposal) -> String {
    // Extract from the first few lines of the description
    let description = &proposal.description;
    let first_lines: Vec<&str> = description.lines().take(3).collect();

    if !first_lines.is_empty() {
        // Join the first few lines
        let topic = first_lines.join(" ");

        // Limit length to a reasonable size
        if topic.len() > 100 {
            return topic[..100].to_string();
        }
        return topic;
    }

    // Fallback to a substring of the description
    let max_len = description.len().min(100);
    description[..max_len].to_string()
}

/// Format deep research results into a concise summary for the AI prompt
pub fn format_deep_research_for_prompt(research: &DeepResearchResponse) -> String {
    let mut formatted = String::new();

    // Add topic
    formatted.push_str(&format!("Topic: {}\n\n", research.topic));

    // Add key resources and their descriptions
    formatted.push_str("Key discussion platforms and community insights:\n");

    // Limit to most relevant resources (max 5)
    let top_resources = research.resources.iter().take(5);

    for (i, resource) in top_resources.enumerate() {
        formatted.push_str(&format!(
            "{}. {} ({}): {}\n   Quality of discourse: {}\n\n",
            i + 1,
            resource.name,
            resource.resource_type,
            resource.description,
            resource.quality_of_discourse
        ));
    }

    formatted
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_topic_from_proposal_with_title() {
        let proposal = Proposal {
            title: Some("Implement Staking Rewards".to_string()),
            description:
                "This is a long description that should not be used when title is available"
                    .to_string(),
            url: None,
        };

        assert_eq!(
            extract_topic_from_proposal(&proposal),
            "Implement Staking Rewards"
        );
    }

    #[test]
    fn test_extract_topic_from_proposal_without_title() {
        let proposal = Proposal {
            title: None,
            description: "Proposal to implement staking rewards\n\nThis would allow users to earn passive income.".to_string(),
            url: None,
        };

        assert_eq!(
            extract_topic_from_proposal(&proposal), 
            "Proposal to implement staking rewards\n\nThis would allow users to earn passive income."
        );
    }
}
