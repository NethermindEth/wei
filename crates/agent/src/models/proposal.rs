use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

/// Simplified proposal model for agent analysis
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = "A governance proposal to be analyzed by the AI agent")]
pub struct Proposal {
    // /// Unique identifier
    // pub id: String,
    // /// Title of the proposal
    // pub title: String,
    /// Description of the proposal
    #[schema(
        example = "This proposal aims to increase the reward rate for stakers from 5% to 7% to incentivize more participation in the protocol. The change will be implemented over a 30-day period with quarterly reviews to assess impact on protocol sustainability.",
        min_length = 10,
        max_length = 10000
    )]
    pub description: String,
    // /// Protocol ID
    // pub protocol_id: String,
    // /// Author address
    // pub author: String,
}
