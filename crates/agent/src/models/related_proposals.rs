//! Related proposals data models

use serde::{Deserialize, Serialize};

/// Query parameters for related proposals search
#[derive(Deserialize)]
pub struct RelatedProposalsQuery {
    /// The search query or proposal text to find related proposals for
    pub query: String,
    /// Maximum number of results to return (default: 5, max: 10)
    pub limit: Option<u8>,
}

/// Response payload for related proposals request
#[derive(Serialize)]
pub struct RelatedProposalsResponse {
    /// List of related proposals found
    pub related_proposals: Vec<RelatedProposal>,
    /// The query that was used for the search
    pub query: String,
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
