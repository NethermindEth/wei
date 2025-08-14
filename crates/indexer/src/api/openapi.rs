//! OpenAPI specification for the indexer service

use utoipa::OpenApi;

use crate::api::handlers::{AccountParams, SearchParams, WebhookRegistration, WebhookResponse};
use crate::models::proposal::ProposalStatus;
use crate::models::{Proposal, ProtocolId};

/// OpenAPI specification for the indexer service
#[derive(OpenApi)]
#[openapi(
    paths(
        crate::api::handlers::get_proposal_by_id,
        crate::api::handlers::get_proposals_by_network,
        crate::api::handlers::search_proposals,
        crate::api::handlers::get_account_by_address,
        crate::api::handlers::register_webhook
    ),
    components(
        schemas(Proposal, ProposalStatus, ProtocolId, SearchParams, AccountParams, WebhookRegistration, WebhookResponse)
    ),
    tags(
        (name = "Proposals", description = "Governance proposal management and retrieval endpoints"),
        (name = "Accounts", description = "Account lookup and information endpoints"),
        (name = "Webhooks", description = "Webhook registration and management endpoints")
    ),
    info(
        title = "Wei Indexer API",
        description = "DAO/Governance proposal indexing service. This API provides comprehensive access to governance proposals across multiple blockchain networks, enabling efficient searching, filtering, and monitoring of DAO activities.",
        version = "0.1.0",
        contact(
            name = "Wei Team",
            url = "https://github.com/NethermindEth/wei"
        ),
        license(
            name = "MIT",
            url = "https://opensource.org/licenses/MIT"
        )
    ),
    servers(
        (url = "http://localhost:3001", description = "Local development server"),
    ),
    external_docs(
        description = "Wei Project Documentation",
        url = "https://github.com/NethermindEth/wei"
    )
)]
pub struct ApiDoc;
