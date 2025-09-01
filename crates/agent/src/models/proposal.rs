use crate::swagger::descriptions;
use crate::swagger::examples;
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

/// Simplified proposal model for agent analysis
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = descriptions::PROPOSAL_DESCRIPTION)]
pub struct Proposal {
    /// Description of the proposal
    #[schema(
        example = examples::PROPOSAL_DESCRIPTION_EXAMPLE,
        min_length = 10,
        max_length = 10000
    )]
    pub description: String,
}
