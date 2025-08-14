use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
#[allow(unused_imports)]
use uuid::Uuid;

use super::ProtocolId;

/// Represents a DAO/Governance proposal
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = "A DAO/Governance proposal with voting details and metadata")]
pub struct Proposal {
    /// Unique identifier combining protocol and proposal ID
    #[schema(example = "uniswap_v3_proposal_123")]
    pub id: String,
    /// Title of the proposal
    #[schema(example = "Increase Staking Rewards")]
    pub title: String,
    /// Description of the proposal
    #[schema(
        example = "This proposal aims to increase the reward rate for stakers from 5% to 7% to incentivize more participation in the protocol."
    )]
    pub description: String,
    /// Current status of the proposal
    pub status: ProposalStatus,
    /// Protocol/network identifier
    pub protocol_id: ProtocolId,
    /// Available choices for voting
    #[schema(example = "[\"Yes\", \"No\", \"Abstain\"]")]
    pub choices: Vec<String>,
    /// Author of the proposal
    #[schema(example = "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6")]
    pub author: String,
    /// Comments and discussions
    #[schema(example = "[\"Great proposal!\", \"Need more details on implementation\"]")]
    pub comments: Vec<String>,
    /// Creation timestamp
    #[schema(example = "2024-01-15T10:30:00Z")]
    pub created_at: DateTime<Utc>,
    /// Last update timestamp
    #[schema(example = "2024-01-15T10:30:00Z")]
    pub updated_at: DateTime<Utc>,
}

/// Status of a proposal
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = "Current status of a governance proposal")]
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
