//! Exa API search service for finding related proposals

use anyhow::{anyhow, Result};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use tracing::{error, info};

/// Exa API client for searching related content
#[derive(Clone)]
pub struct ExaService {
    client: Client,
    api_key: String,
    base_url: String,
}

/// Request payload for Exa search
#[derive(Debug, Serialize)]
pub struct ExaSearchRequest {
    /// The search query
    pub query: String,
    /// Number of search results to return (max 10)
    pub num_results: Option<u8>,
    /// Whether to include content in results
    pub include_domains: Option<Vec<String>>,
    /// Whether to exclude certain domains
    pub exclude_domains: Option<Vec<String>>,
    /// Start published date filter (YYYY-MM-DD format)
    pub start_published_date: Option<String>,
    /// End published date filter (YYYY-MM-DD format)  
    pub end_published_date: Option<String>,
    /// Type of search to perform
    pub r#type: Option<String>,
}

/// Individual search result from Exa
#[derive(Debug, Deserialize, Serialize)]
pub struct ExaSearchResult {
    /// URL of the result
    pub url: String,
    /// Title of the content
    pub title: String,
    /// Snippet/summary of the content
    pub text: Option<String>,
    /// Highlighted snippet
    pub highlights: Option<Vec<String>>,
    /// Published date
    pub published_date: Option<String>,
    /// Author information
    pub author: Option<String>,
    /// Score/relevance
    pub score: Option<f64>,
}

/// Response from Exa search API
#[derive(Debug, Deserialize, Serialize)]
pub struct ExaSearchResponse {
    /// List of search results
    pub results: Vec<ExaSearchResult>,
    /// Autoprompt info
    pub autoprompt_string: Option<String>,
}

/// Related proposal information for the frontend
#[derive(Debug, Serialize)]
pub struct RelatedProposal {
    /// URL of the related proposal
    pub url: String,
    /// Title of the proposal
    pub title: String,
    /// Summary/excerpt of the proposal content
    pub summary: Option<String>,
    /// Published date if available
    pub published_date: Option<String>,
    /// Relevance score
    pub relevance_score: Option<f64>,
    /// Source domain
    pub source: String,
}

impl ExaService {
    /// Create a new Exa service instance
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
            base_url: "https://api.exa.ai".to_string(),
        }
    }

    /// Search for related proposals using Exa
    pub async fn search_related_proposals(
        &self,
        query: String,
        num_results: Option<u8>,
    ) -> Result<Vec<RelatedProposal>> {
        info!("Searching for related proposals with query: {}", query);

        let search_request = ExaSearchRequest {
            query: format!("governance proposal dao {}", query),
            num_results: num_results.or(Some(5)),
            include_domains: Some(vec![
                "snapshot.org".to_string(),
                "forum.arbitrum.foundation".to_string(),
                "governance.aave.com".to_string(),
                "compound.finance".to_string(),
                "gov.uniswap.org".to_string(),
                "forum.makerdao.com".to_string(),
                "research.tally.xyz".to_string(),
                "commonwealth.im".to_string(),
            ]),
            exclude_domains: None,
            start_published_date: None,
            end_published_date: None,
            r#type: Some("auto".to_string()),
        };

        let response = self
            .client
            .post(&format!("{}/search", self.base_url))
            .header("Authorization", &format!("Bearer {}", self.api_key))
            .header("Content-Type", "application/json")
            .json(&search_request)
            .send()
            .await
            .map_err(|e| anyhow!("Failed to send request to Exa API: {}", e))?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response
                .text()
                .await
                .unwrap_or_else(|_| "Unknown error".to_string());
            error!("Exa API error {}: {}", status, error_text);
            return Err(anyhow!(
                "Exa API request failed with status {}: {}",
                status,
                error_text
            ));
        }

        let exa_response: ExaSearchResponse = response
            .json()
            .await
            .map_err(|e| anyhow!("Failed to parse Exa API response: {}", e))?;

        info!("Found {} related proposals", exa_response.results.len());

        // Convert Exa results to our RelatedProposal format
        let related_proposals = exa_response
            .results
            .into_iter()
            .map(|result| {
                let source = extract_domain(&result.url);
                RelatedProposal {
                    url: result.url,
                    title: result.title,
                    summary: result
                        .text
                        .or_else(|| result.highlights.and_then(|h| h.first().cloned())),
                    published_date: result.published_date,
                    relevance_score: result.score,
                    source,
                }
            })
            .collect();

        Ok(related_proposals)
    }
}

/// Extract domain name from URL for display purposes
fn extract_domain(url: &str) -> String {
    if let Ok(parsed_url) = url::Url::parse(url) {
        if let Some(domain) = parsed_url.domain() {
            return domain.to_string();
        }
    }
    "Unknown".to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_domain() {
        assert_eq!(
            extract_domain("https://snapshot.org/proposal/123"),
            "snapshot.org"
        );
        assert_eq!(
            extract_domain("https://forum.arbitrum.foundation/t/proposal/123"),
            "forum.arbitrum.foundation"
        );
        assert_eq!(extract_domain("invalid-url"), "Unknown");
    }
}
