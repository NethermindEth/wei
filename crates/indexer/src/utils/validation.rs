//! Validation utilities

use crate::models::{Actor, Proposal, ProtocolId};

/// Validate a proposal
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub fn validate_proposal(proposal: &Proposal) -> Result<(), String> {
    if proposal.title.is_empty() {
        return Err("Proposal title cannot be empty".to_string());
    }

    if proposal.description.is_empty() {
        return Err("Proposal description cannot be empty".to_string());
    }

    if proposal.author.is_empty() {
        return Err("Proposal author cannot be empty".to_string());
    }

    Ok(())
}

/// Validate an actor
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub fn validate_actor(actor: &Actor) -> Result<(), String> {
    if actor.address.is_empty() {
        return Err("Actor address cannot be empty".to_string());
    }

    // TODO: Add more validation rules
    Ok(())
}

/// Validate a protocol ID
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub fn validate_protocol_id(protocol_id: &ProtocolId) -> Result<(), String> {
    if protocol_id.name.is_empty() {
        return Err("Protocol name cannot be empty".to_string());
    }

    if protocol_id.protocol.is_empty() {
        return Err("Protocol identifier cannot be empty".to_string());
    }

    Ok(())
}
