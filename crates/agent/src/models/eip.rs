use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

/// Ethereum Improvement Proposal (EIP) model
#[derive(Debug, Serialize, Deserialize, Clone, ToSchema)]
pub struct EipProposal {
    /// EIP number identifier
    pub eip_number: u32,
    /// Title of the EIP
    pub title: String,
    /// List of authors
    pub author: Vec<String>,
    /// Current status (e.g., Draft, Final, Accepted)
    pub status: String,
    /// Type of EIP (e.g., Standards Track, Meta, Informational)
    #[serde(rename = "type")]
    pub eip_type: String,
    /// Category for Standards Track EIPs (e.g., Core, Networking)
    pub category: Option<String>,
    /// Creation date
    pub created: String,
    /// EIP numbers that this EIP depends on
    pub requires: Option<Vec<u32>>,
    /// Brief description of the EIP
    pub description: String,
    /// URL to the EIP on GitHub
    pub github_url: String,
    /// Full content of the EIP
    pub content: String,
    /// Discussion comments and votes
    #[serde(default)]
    pub discussions: Vec<EipDiscussion>,
}

/// Discussion or comment on an EIP
#[derive(Debug, Serialize, Deserialize, Clone, ToSchema)]
pub struct EipDiscussion {
    /// Unique identifier for the comment
    pub id: String,
    /// Author of the comment
    pub author: String,
    /// Content of the comment
    pub content: String,
    /// When the comment was created
    pub created_at: DateTime<Utc>,
    /// Vote type (positive, negative, neutral)
    pub vote: Option<EipVote>,
}

/// Vote on an EIP
#[derive(Debug, Serialize, Deserialize, Clone, ToSchema)]
pub enum EipVote {
    /// Supporting the EIP
    #[serde(rename = "for")]
    For,
    /// Against the EIP
    #[serde(rename = "against")]
    Against,
    /// Neutral or abstaining
    #[serde(rename = "neutral")]
    Neutral,
}

/// Response for EIP requests
#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct EipResponse {
    /// The requested EIP
    pub eip: EipProposal,
    /// Whether this response came from cache
    pub from_cache: bool,
}

/// Response for multiple EIPs
#[derive(Debug, Serialize, Deserialize, ToSchema)]
pub struct EipsResponse {
    /// List of EIPs
    pub eips: Vec<EipProposal>,
    /// Total count of EIPs
    pub total: usize,
    /// Whether this response came from cache
    pub from_cache: bool,
    /// Current page number (1-based)
    #[serde(default = "default_page")]
    pub page: usize,
    /// Number of items per page
    #[serde(default = "default_page_size")]
    pub page_size: usize,
    /// Total number of pages
    #[serde(default = "default_total_pages")]
    pub total_pages: usize,
}

/// Default page number (1-based)
fn default_page() -> usize {
    1
}

/// Default page size
fn default_page_size() -> usize {
    20
}

/// Default total pages
fn default_total_pages() -> usize {
    1
}

/// Filter parameters for EIP listing
#[derive(Deserialize, ToSchema)]
pub struct EipFilterRequest {
    /// Filter by EIP type (e.g., "Standards Track", "Meta", "Informational")
    pub eip_type: Option<String>,
    /// Filter by category (e.g., "Core", "ERC", "Interface")
    pub category: Option<String>,
    /// Filter by status (e.g., "Draft", "Final", "Withdrawn")
    pub status: Option<String>,
    /// Filter by author
    pub author: Option<String>,
    /// Maximum number of results to return
    pub limit: Option<usize>,
    /// Page number for pagination (1-based)
    pub page: Option<usize>,
    /// Number of items per page
    pub page_size: Option<usize>,
}
