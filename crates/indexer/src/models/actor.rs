use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

use super::ProtocolId;

/// Represents an actor/entity in the governance system
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Actor {
    /// Ethereum address of the actor
    pub address: String,
    /// ENS name if available
    pub ens: Option<String>,
    /// Organization name
    pub name: Option<String>,
    /// Description of the entity
    pub description: Option<String>,
    /// Voting power of the entity
    pub voting_power: Option<String>,
    /// Protocol/network identifier
    pub protocol_id: Option<ProtocolId>,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    /// Last update timestamp
    pub updated_at: DateTime<Utc>,
}
