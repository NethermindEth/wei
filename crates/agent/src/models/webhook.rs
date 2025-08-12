use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// Webhook event from the indexer
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebhookEvent {
    /// Event type
    pub event_type: WebhookEventType,
    /// Proposal data
    pub proposal: ProposalData,
    /// Timestamp of the event
    pub timestamp: DateTime<Utc>,
}

/// Type of webhook event
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum WebhookEventType {
    /// A new proposal was created
    Created,
    /// An existing proposal was updated
    Updated,
    /// Voting started on a proposal
    VotingStarted,
    /// Voting ended on a proposal
    VotingEnded,
}

/// Proposal data in webhook events
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProposalData {
    /// Proposal ID
    pub id: String,
    /// Proposal title
    pub title: String,
    /// Proposal description
    pub description: String,
    /// Protocol ID
    pub protocol_id: String,
    /// Author address
    pub author: String,
}
