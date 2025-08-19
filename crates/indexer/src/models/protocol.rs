use serde::{Deserialize, Serialize};
use utoipa::ToSchema;

/// Represents a blockchain protocol/network
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash, ToSchema)]
#[schema(description = "A blockchain protocol or network identifier")]
pub struct ProtocolId {
    /// Chain ID
    #[schema(example = 1)]
    pub chain_id: u64,
    /// Protocol name
    #[schema(example = "Ethereum Mainnet")]
    pub name: String,
    /// Protocol identifier
    #[schema(example = "uniswap_v3")]
    pub protocol: String,
}

impl ProtocolId {
    /// Creates a new protocol ID
    #[allow(dead_code)] // TODO: Remove after development phase
    pub fn new(chain_id: u64, name: String, protocol: String) -> Self {
        Self {
            chain_id,
            name,
            protocol,
        }
    }
}

impl std::fmt::Display for ProtocolId {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}:{}:{}", self.chain_id, self.name, self.protocol)
    }
}
