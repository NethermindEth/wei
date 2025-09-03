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

// Authentication handler descriptions
/// Description of the user registration handler
pub const HANDLER_USER_REGISTRATION_DESCRIPTION: &str = "Create a new user account with email and password. The password will be securely hashed and stored.";

/// Description of the user login handler
pub const HANDLER_USER_LOGIN_DESCRIPTION: &str = "Authenticate a user with email and password. Returns JWT access and refresh tokens upon successful authentication.";

/// Description of the token refresh handler
pub const HANDLER_TOKEN_REFRESH_DESCRIPTION: &str = "Exchange a valid refresh token for a new access token. This allows users to maintain authentication without re-entering credentials.";

/// Description of the get current user profile handler
pub const HANDLER_GET_CURRENT_USER_PROFILE_DESCRIPTION: &str = "Get the profile information of the currently authenticated user.";