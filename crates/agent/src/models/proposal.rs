use serde::{Deserialize, Serialize};

/// Simplified proposal model for agent analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Proposal {
    /// Unique identifier
    pub id: String,
    /// Title of the proposal
    pub title: String,
    /// Description of the proposal
    pub description: String,
    /// Protocol ID
    pub protocol_id: String,
    /// Author address
    pub author: String,
}
