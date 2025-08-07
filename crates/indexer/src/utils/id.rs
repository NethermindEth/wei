//! ID generation utilities

use crate::models::ProtocolId;

/// Generate a proposal ID from protocol and proposal details
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub fn generate_proposal_id(protocol_id: &ProtocolId, proposal_id: &str) -> String {
    format!("{protocol_id}:{proposal_id}")
}

/// Parse a proposal ID to extract protocol and proposal parts
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub fn parse_proposal_id(id: &str) -> Option<(String, String)> {
    let parts: Vec<&str> = id.split(':').collect();
    if parts.len() >= 2 {
        let protocol_part = parts[..parts.len() - 1].join(":");
        let proposal_part = parts[parts.len() - 1];
        Some((protocol_part, proposal_part.to_string()))
    } else {
        None
    }
}
