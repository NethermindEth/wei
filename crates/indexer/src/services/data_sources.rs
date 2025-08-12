//! Data source abstractions using Strategy pattern

use async_trait::async_trait;

use crate::models::{Actor, Proposal, ProtocolId};

/// Trait for data sources (Strategy pattern)
#[async_trait]
pub trait DataSource {
    /// Get the name of the data source
    #[allow(dead_code)] // TODO: Remove after development phase
    fn name(&self) -> &str;

    /// Get the protocol ID this source handles
    #[allow(dead_code)] // TODO: Remove after development phase
    fn protocol_id(&self) -> ProtocolId;

    /// Fetch proposals from this data source
    #[allow(dead_code)] // TODO: Remove after development phase
    async fn fetch_proposals(&self) -> anyhow::Result<Vec<Proposal>>;

    /// Fetch actors from this data source
    #[allow(dead_code)] // TODO: Remove after development phase
    async fn fetch_actors(&self) -> anyhow::Result<Vec<Actor>>;

    /// Check if the data source is available
    #[allow(dead_code)] // TODO: Remove after development phase
    async fn is_available(&self) -> bool;
}

/// Snapshot data source implementation
#[allow(dead_code)] // TODO: Remove after development phase
pub struct SnapshotDataSource {
    base_url: String,
    api_key: Option<String>,
    protocol_id: ProtocolId,
}

impl SnapshotDataSource {
    /// Create a new Snapshot data source
    #[allow(dead_code)] // TODO: Remove after development phase
    pub fn new(base_url: String, api_key: Option<String>, protocol_id: ProtocolId) -> Self {
        Self {
            base_url,
            api_key,
            protocol_id,
        }
    }
}

#[async_trait]
impl DataSource for SnapshotDataSource {
    #[allow(dead_code)] // TODO: Remove after development phase
    fn name(&self) -> &str {
        "snapshot"
    }

    #[allow(dead_code)] // TODO: Remove after development phase
    fn protocol_id(&self) -> ProtocolId {
        self.protocol_id.clone()
    }

    #[allow(dead_code)] // TODO: Remove after development phase
    async fn fetch_proposals(&self) -> anyhow::Result<Vec<Proposal>> {
        // TODO: Implement Snapshot API integration
        todo!("Implement Snapshot fetch_proposals")
    }

    #[allow(dead_code)] // TODO: Remove after development phase
    async fn fetch_actors(&self) -> anyhow::Result<Vec<Actor>> {
        // TODO: Implement Snapshot actors fetching
        todo!("Implement Snapshot fetch_actors")
    }

    #[allow(dead_code)] // TODO: Remove after development phase
    async fn is_available(&self) -> bool {
        // TODO: Implement availability check
        true
    }
}

/// Tally data source implementation
#[allow(dead_code)] // TODO: Remove after development phase
pub struct TallyDataSource {
    base_url: String,
    api_key: Option<String>,
    protocol_id: ProtocolId,
}

impl TallyDataSource {
    /// Create a new Tally data source
    #[allow(dead_code)] // TODO: Remove after development phase
    pub fn new(base_url: String, api_key: Option<String>, protocol_id: ProtocolId) -> Self {
        Self {
            base_url,
            api_key,
            protocol_id,
        }
    }
}

#[async_trait]
impl DataSource for TallyDataSource {
    fn name(&self) -> &str {
        "tally"
    }

    fn protocol_id(&self) -> ProtocolId {
        self.protocol_id.clone()
    }

    async fn fetch_proposals(&self) -> anyhow::Result<Vec<Proposal>> {
        // TODO: Implement Tally API integration
        todo!("Implement Tally fetch_proposals")
    }

    async fn fetch_actors(&self) -> anyhow::Result<Vec<Actor>> {
        // TODO: Implement Tally actors fetching
        todo!("Implement Tally fetch_actors")
    }

    async fn is_available(&self) -> bool {
        // TODO: Implement availability check
        true
    }
}
