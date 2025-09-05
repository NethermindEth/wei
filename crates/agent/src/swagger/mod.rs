//! API documentation for the agent service

use utoipa::OpenApi;

use crate::models::analysis::AnalyzeResponse;
use crate::models::analysis::{
    Analysis, AnalysisResult, EvaluationCategory, ProposalAnalysis, ProposalMetadata,
    StructuredAnalysisResponse,
};
use crate::models::roadmap::{
    CurrentValue, Domain, Evidence, FitnessFunction, Intervention, Link, LiveValidation, Metadata,
    Problem, Proposal as RoadmapProposal, ResearchWindow, RoadmapApiResponse, RoadmapRequest,
    RoadmapResponse, RoadmapResult, Signal, Source, Target,
};
use crate::models::HealthResponse;
use crate::models::Proposal;

pub mod descriptions;
pub mod examples;
pub mod handlers;

/// OpenAPI specification for the agent service
#[derive(OpenApi)]
#[openapi(
    paths(
        crate::api::handlers::health,
        crate::api::handlers::analyze_proposal,
        crate::api::handlers::get_analysis,
        crate::api::handlers::get_proposal_analyses,
        crate::api::handlers::generate_roadmap,
        crate::api::handlers::get_cached_roadmap
    ),
    components(
        schemas(
            Proposal, AnalyzeResponse, HealthResponse, Analysis, AnalysisResult,
            StructuredAnalysisResponse, EvaluationCategory, ProposalAnalysis, ProposalMetadata,
            RoadmapApiResponse, RoadmapRequest, RoadmapResponse, RoadmapResult,
            Domain, ResearchWindow, FitnessFunction, Target, CurrentValue, Problem, Evidence,
            Intervention, LiveValidation, Signal, RoadmapProposal, Link, Source, Metadata
        )
    ),
    tags(
        (name = "Health", description = "Service health and status endpoints"),
        (name = "Analysis", description = "Proposal analysis endpoints for AI-powered governance assessment"),
        (name = "Roadmap", description = "Outcome-driven roadmap generation endpoints for protocols, DAOs, and companies")
    ),
    info(
        title = "Wei Agent API",
        description = "AI agent service for analyzing DAO/Governance proposals. This API provides intelligent analysis of governance proposals, helping DAOs make informed decisions by evaluating proposal quality, risks, and governance best practices.",
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
        (url = "http://localhost:8000", description = "Local development server"),
        (url = "http://localhost:3000", description = "Alternative development server"),
    ),
    external_docs(
        description = "Wei Project Documentation",
        url = "https://github.com/NethermindEth/wei"
    )
)]
pub struct ApiDoc;
