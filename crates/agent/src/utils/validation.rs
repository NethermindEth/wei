//! Validation utilities for the agent service

use crate::models::{Analysis, Proposal};

/// Validate an analysis
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub fn validate_analysis(analysis: &Analysis) -> Result<(), String> {
    if analysis.proposal_id.is_empty() {
        return Err("Analysis proposal ID cannot be empty".to_string());
    }

    if analysis.details.is_empty() {
        return Err("Analysis details cannot be empty".to_string());
    }

    if analysis.confidence < 0.0 || analysis.confidence > 1.0 {
        return Err("Analysis confidence must be between 0.0 and 1.0".to_string());
    }

    Ok(())
}

/// Validate a proposal for analysis
#[allow(dead_code, unused_variables)] // TODO: Remove after development phase
pub fn validate_proposal_for_analysis(proposal: &Proposal) -> Result<(), String> {
    if proposal.title.is_empty() {
        return Err("Proposal title cannot be empty".to_string());
    }

    if proposal.description.is_empty() {
        return Err("Proposal description cannot be empty".to_string());
    }

    Ok(())
}
