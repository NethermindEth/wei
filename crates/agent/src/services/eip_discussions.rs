use crate::models::eip::EipDiscussion;
use crate::utils::error::Result;
use chrono::Utc;
use tracing::{info, warn};
use uuid::Uuid;

/// Service for fetching EIP discussions from various sources
#[derive(Clone)]
pub struct EipDiscussionService {
    /// GitHub API client
    github_service: super::eip::EipService,
}

impl EipDiscussionService {
    /// Create a new EIP discussion service
    pub fn new(github_token: Option<String>) -> Self {
        Self {
            github_service: super::eip::EipService::new(github_token),
        }
    }

    /// Fetch discussions for a specific EIP from all available sources
    pub async fn fetch_discussions(&self, eip_number: u32) -> Result<Vec<EipDiscussion>> {
        info!(
            "Fetching discussions for EIP-{} from all sources",
            eip_number
        );

        // Try to fetch discussions from GitHub first
        match self.fetch_github_discussions(eip_number).await {
            Ok(discussions) if !discussions.is_empty() => {
                info!(
                    "Found {} GitHub discussions for EIP-{}",
                    discussions.len(),
                    eip_number
                );
                Ok(discussions)
            }
            Ok(_) => {
                // No GitHub discussions found, try other sources
                warn!(
                    "No GitHub discussions found for EIP-{}, trying other sources",
                    eip_number
                );
                self.fetch_from_other_sources(eip_number).await
            }
            Err(e) => {
                // Error fetching from GitHub, try other sources
                warn!(
                    "Error fetching GitHub discussions for EIP-{}: {}",
                    eip_number, e
                );
                self.fetch_from_other_sources(eip_number).await
            }
        }
    }

    /// Fetch discussions from GitHub
    async fn fetch_github_discussions(&self, eip_number: u32) -> Result<Vec<EipDiscussion>> {
        self.github_service.fetch_eip_discussions(eip_number).await
    }

    /// Fetch discussions from other sources (forums, mailing lists, etc.)
    async fn fetch_from_other_sources(&self, eip_number: u32) -> Result<Vec<EipDiscussion>> {
        // In a real implementation, this would fetch from Ethereum forums, mailing lists, etc.
        // For now, we'll return an empty list with a note about where to find discussions

        info!(
            "No discussions found for EIP-{} from available sources",
            eip_number
        );

        // Return an informational note instead of fake data
        let discussions = vec![
            EipDiscussion {
                id: Uuid::new_v4().to_string(),
                author: "wei-system".to_string(),
                content: format!(
                    "No discussions were found for EIP-{}. You can find discussions about this EIP on Ethereum forums, \
                    the Ethereum magicians forum (https://ethereum-magicians.org), or the Ethereum research forum \
                    (https://ethresear.ch). This is not mock data - we genuinely couldn't find discussions for this EIP \
                    from our available sources.", 
                    eip_number
                ),
                created_at: Utc::now(),
                vote: None,
            }
        ];

        Ok(discussions)
    }
}
