use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use uuid::Uuid;

/// Request to generate a roadmap for a protocol/DAO/company
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct RoadmapRequest {
    /// The subject/domain name (e.g., "Ethereum L1", "Acme DAO")
    pub subject: String,
    /// The kind of entity (protocol, DAO, company, country, product, other)
    pub kind: String,
    /// One-line scope of what to include
    pub scope: String,
    /// Research window start date (YYYY-MM-DD)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub from: Option<String>,
    /// Research window end date (YYYY-MM-DD)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub to: Option<String>,
}

/// Response containing the generated roadmap
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct RoadmapResponse {
    /// Schema version
    pub schema_version: String,
    /// Domain information
    pub domain: Domain,
    /// Work streams/pillars
    pub streams: Vec<String>,
    /// Fitness functions (KPIs/SLOs)
    pub fitness_functions: Vec<FitnessFunction>,
    /// Problems identified
    pub problems: Vec<Problem>,
    /// Interventions/initiatives
    pub interventions: Vec<Intervention>,
    /// Governance proposals (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub proposals: Option<Vec<Proposal>>,
    /// Links between problems and interventions
    pub links: Vec<Link>,
    /// Sources used for research
    pub sources: Vec<Source>,
    /// Metadata about generation
    #[serde(skip_serializing_if = "Option::is_none")]
    pub metadata: Option<Metadata>,
}

/// Domain information
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Domain {
    /// Domain name
    pub name: String,
    /// Kind of entity
    pub kind: String,
    /// Scope description
    pub scope: String,
    /// Date as of which this roadmap was generated
    pub as_of: String,
    /// Research window (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub research_window: Option<ResearchWindow>,
}

/// Research window
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ResearchWindow {
    /// Start date
    pub from: String,
    /// End date
    pub to: String,
}

/// Fitness function (KPI/SLO)
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FitnessFunction {
    /// Unique identifier
    pub id: String,
    /// Name of the fitness function
    pub name: String,
    /// Associated stream
    pub stream: String,
    /// Description (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    /// Unit of measurement (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub unit: Option<String>,
    /// Direction of improvement
    pub direction: String,
    /// Target value (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target: Option<Target>,
    /// Current value (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub current: Option<CurrentValue>,
}

/// Target value for a fitness function
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Target {
    /// Comparison operator
    pub operator: String,
    /// Target value
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value: Option<serde_json::Value>,
    /// Minimum value (for range targets)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub min: Option<serde_json::Value>,
    /// Maximum value (for range targets)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub max: Option<serde_json::Value>,
}

/// Current value for a fitness function
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct CurrentValue {
    /// Current value
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value: Option<serde_json::Value>,
    /// When this value was measured
    #[serde(skip_serializing_if = "Option::is_none")]
    pub measured_at: Option<String>,
    /// Source IDs for this measurement
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_ids: Option<Vec<String>>,
}

/// Problem identified in the roadmap
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Problem {
    /// Unique identifier
    pub id: String,
    /// Problem title
    pub title: String,
    /// Associated stream
    pub stream: String,
    /// Severity level
    pub severity: String,
    /// Time horizon
    pub horizon: String,
    /// Associated fitness function ID (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fitness_function_id: Option<String>,
    /// Target description (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target: Option<String>,
    /// Current state description (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub current: Option<String>,
    /// Risk description (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub risk: Option<String>,
    /// Exit criteria
    pub exit_criteria: String,
    /// Status (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status: Option<String>,
    /// Evidence (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub evidence: Option<Evidence>,
}

/// Evidence for a problem or intervention
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Evidence {
    /// Source IDs
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_ids: Option<Vec<String>>,
    /// Notes
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
}

/// Intervention/initiative
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Intervention {
    /// Unique identifier
    pub id: String,
    /// Intervention title
    pub title: String,
    /// Label (e.g., EIP number, proposal code)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub label: Option<String>,
    /// Associated stream
    pub stream: String,
    /// Status
    pub status: String,
    /// Stage (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub stage: Option<String>,
    /// Release (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub release: Option<String>,
    /// Timeframe (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeframe: Option<String>,
    /// Goal (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub goal: Option<String>,
    /// Dependencies (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub deps: Option<Vec<String>>,
    /// Risk notes (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub risk_notes: Option<String>,
    /// Live validation (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub live_validation: Option<LiveValidation>,
    /// Evidence (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub evidence: Option<Evidence>,
}

/// Live validation for an intervention
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct LiveValidation {
    /// Verdict
    pub verdict: String,
    /// Confidence level (0-1)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub confidence: Option<f64>,
    /// Summary
    #[serde(skip_serializing_if = "Option::is_none")]
    pub summary: Option<String>,
    /// Signals
    #[serde(skip_serializing_if = "Option::is_none")]
    pub signals: Option<Vec<Signal>>,
}

/// Signal for live validation
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Signal {
    /// Signal type
    pub r#type: String,
    /// Signal value
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value: Option<serde_json::Value>,
    /// When this signal was observed
    pub observed_at: String,
    /// Source ID
    pub source_id: String,
}

/// Governance proposal
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Proposal {
    /// Unique identifier
    pub id: String,
    /// Proposal title
    pub title: String,
    /// Stage
    pub stage: String,
    /// Owner (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub owner: Option<String>,
    /// Associated problem ID (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub problem_id: Option<String>,
    /// Linked item IDs (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub linked_item_ids: Option<Vec<String>>,
    /// Notes (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
}

/// Link between problem and intervention
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Link {
    /// Problem ID
    pub problem_id: String,
    /// Intervention ID
    pub intervention_id: String,
    /// Link quality
    pub link_quality: String,
    /// Rationale (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rationale: Option<String>,
    /// Source IDs (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub source_ids: Option<Vec<String>>,
}

/// Source used in research
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Source {
    /// Unique identifier
    pub id: String,
    /// Source type
    pub r#type: String,
    /// Source title
    pub title: String,
    /// Source URL
    pub url: String,
    /// Published date (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub published_at: Option<String>,
    /// Retrieved date
    pub retrieved_at: String,
    /// Credibility (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub credibility: Option<String>,
    /// Notes (optional)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
}

/// Metadata about roadmap generation
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Metadata {
    /// Generator information
    #[serde(skip_serializing_if = "Option::is_none")]
    pub generator: Option<String>,
    /// Generation timestamp
    #[serde(skip_serializing_if = "Option::is_none")]
    pub generated_at: Option<String>,
    /// Notes
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
}

/// Cached roadmap result
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct RoadmapResult {
    /// Unique identifier for the result
    pub id: Uuid,
    /// The request that generated this result
    pub request: RoadmapRequest,
    /// The roadmap response
    pub response: RoadmapResponse,
    /// Creation timestamp
    pub created_at: DateTime<Utc>,
    /// Expiry timestamp (24 hours from creation for caching)
    pub expires_at: DateTime<Utc>,
}

/// API response for roadmap endpoints
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct RoadmapApiResponse {
    /// The roadmap result
    pub result: RoadmapResult,
    /// Cache information
    pub cache_info: Option<serde_json::Value>,
}
