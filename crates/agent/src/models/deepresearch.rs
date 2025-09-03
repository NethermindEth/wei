use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

/// Represents a deep research request for a protocol/community/topic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeepResearchRequest {
    /// The protocol, community, subculture, or idea to research
    pub topic: String,
}

/// Represents a deep research result
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeepResearchResult {
    /// Unique identifier for the research
    pub id: Uuid,
    /// The topic that was researched
    pub topic: String,
    /// The research response
    pub response: DeepResearchResponse,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    /// Expiry timestamp (24 hours from creation for caching)
    pub expires_at: DateTime<Utc>,
}

/// The structured response from the deep research AI model
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeepResearchResponse {
    /// The research topic
    pub topic: String,
    /// List of discovered resources/platforms
    pub resources: Vec<DiscussionResource>,
}

/// A single discussion resource/platform found during research
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DiscussionResource {
    /// Official name of the community/resource
    pub name: String,
    /// Direct link to the hub
    pub link: String,
    /// Category of resource (docs, forum, Discord, GitHub, meetup, newsletter, etc.)
    #[serde(rename = "type")]
    pub resource_type: String,
    /// Explanation of the role and value of this space
    pub description: String,
    /// Assessment of discourse quality
    pub quality_of_discourse: String,
}

/// Request to get cached research results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GetDeepResearchQuery {
    /// The topic to search for in cache
    pub topic: String,
}

/// Response for deep research API endpoints
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeepResearchApiResponse {
    /// The research result
    #[serde(flatten)]
    pub result: DeepResearchResponse,
    /// Whether this result was served from cache
    pub from_cache: bool,
    /// When this result was created
    pub created_at: DateTime<Utc>,
    /// When this result expires
    pub expires_at: DateTime<Utc>,
}
