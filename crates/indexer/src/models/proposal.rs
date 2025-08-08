use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
#[allow(unused_imports)]
use uuid::Uuid;

use super::ProtocolId;

/// Represents a DAO/Governance proposal
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Proposal {
    /// Unique identifier combining protocol and proposal ID
    pub id: String,
    /// Title of the proposal
    pub title: String,
    /// Description of the proposal
    pub description: String,
    /// Current status of the proposal
    pub status: ProposalStatus,
    /// Protocol/network identifier
    pub protocol_id: ProtocolId,
    /// Available choices for voting
    pub choices: Vec<String>,
    /// Author of the proposal
    pub author: String,
    /// Comments and discussions
    pub comments: Vec<String>,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    /// Last update timestamp
    pub updated_at: DateTime<Utc>,
}

/// Status of a proposal
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ProposalStatus {
    /// Proposal is currently active and open for voting
    Active,
    /// Proposal was accepted by voters
    Accepted,
    /// Proposal was rejected by voters
    Rejected,
    /// Proposal is pending and not yet active
    Pending,
    /// Proposal was cancelled
    Cancelled,
    /// Proposal was executed on-chain
    Executed,
}

impl Default for ProposalStatus {
    fn default() -> Self {
        Self::Pending
    }
}
