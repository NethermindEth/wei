use serde::{Deserialize, Serialize};

/// Represents a blockchain protocol/network
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub struct ProtocolId {
    /// Chain ID
    pub chain_id: u64,
    /// Protocol name
    pub name: String,
    /// Protocol identifier
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
