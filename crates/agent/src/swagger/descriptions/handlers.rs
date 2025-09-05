//! Descriptions for the agent service swagger documentation

/// Description of the health check handler
pub const HANDLER_HEALTH_DESCRIPTION: &str = "Health check for the agent service";

/// Description of the analysis handler
pub const HANDLER_ANALYSIS_DESCRIPTION: &str = "Submit a proposal for AI analysis. The service will evaluate the proposal content and provide insights on governance quality, risks, and recommendations.";

/// Description of the get analysis handler
pub const HANDLER_GET_ANALYSIS_DESCRIPTION: &str =
    "Get a specific analysis result using its unique identifier.";

/// Description of the get proposal analyses handler
pub const HANDLER_GET_PROPOSAL_ANALYSES_DESCRIPTION: &str = "Get analyses by proposal ID";

/// Summary for the get proposal arguments handler
pub const HANDLER_GET_PROPOSAL_ARGUMENTS_SUMMARY: &str = "Get arguments for and against a proposal";

/// Description of the get proposal arguments handler
pub const HANDLER_GET_PROPOSAL_ARGUMENTS_DESCRIPTION: &str =
    "Returns a list of arguments for and against the given proposal";
