//! User authentication models

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use uuid::Uuid;

use crate::swagger::descriptions;
use crate::swagger::examples;

/// User model
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = descriptions::USER_PROFILE_DESCRIPTION)]
pub struct User {
    /// Unique user identifier
    #[schema(example = examples::USER_ID_EXAMPLE)]
    pub id: Uuid,
    /// User's email address
    #[schema(example = examples::USER_EMAIL_EXAMPLE)]
    pub email: String,
    /// Hashed password
    pub password_hash: String,
    /// User's unique username
    #[schema(example = examples::USER_USERNAME_EXAMPLE)]
    pub username: Option<String>,
    /// User's first name
    #[schema(example = examples::USER_FIRST_NAME_EXAMPLE)]
    pub first_name: Option<String>,
    /// User's last name
    #[schema(example = examples::USER_LAST_NAME_EXAMPLE)]
    pub last_name: Option<String>,
    /// Whether the user account is active
    #[schema(example = true)]
    pub is_active: bool,
    /// When the user was created
    #[schema(example = examples::ANALYSIS_CREATED_AT_EXAMPLE)]
    pub created_at: DateTime<Utc>,
    /// When the user was last updated
    #[schema(example = examples::ANALYSIS_CREATED_AT_EXAMPLE)]
    pub updated_at: DateTime<Utc>,
}

/// User creation request
#[derive(Debug, Deserialize, ToSchema)]
#[schema(description = descriptions::USER_REGISTRATION_DESCRIPTION)]
pub struct CreateUserRequest {
    /// User's email address
    #[schema(example = examples::USER_EMAIL_EXAMPLE)]
    pub email: String,
    /// User's password
    #[schema(example = examples::USER_PASSWORD_EXAMPLE)]
    pub password: String,
    /// User's unique username
    #[schema(example = examples::USER_USERNAME_EXAMPLE)]
    pub username: Option<String>,
    /// User's first name
    #[schema(example = examples::USER_FIRST_NAME_EXAMPLE)]
    pub first_name: Option<String>,
    /// User's last name
    #[schema(example = examples::USER_LAST_NAME_EXAMPLE)]
    pub last_name: Option<String>,
}

/// User registration response
#[derive(Debug, Serialize, ToSchema)]
#[schema(description = descriptions::USER_REGISTRATION_DESCRIPTION)]
pub struct RegisterResponse {
    /// ID of the created user
    #[schema(example = examples::USER_ID_EXAMPLE)]
    pub user_id: Uuid,
    /// Email of the created user
    #[schema(example = examples::USER_EMAIL_EXAMPLE)]
    pub email: String,
    /// Success message
    #[schema(example = examples::REGISTRATION_SUCCESS_MESSAGE_EXAMPLE)]
    pub message: String,
}

/// User login request
#[derive(Debug, Deserialize, ToSchema)]
#[schema(description = descriptions::USER_LOGIN_DESCRIPTION)]
pub struct LoginRequest {
    /// User's email address
    #[schema(example = examples::USER_EMAIL_EXAMPLE)]
    pub email: String,
    /// User's password
    #[schema(example = examples::USER_PASSWORD_EXAMPLE)]
    pub password: String,
}

/// User login response
#[derive(Debug, Serialize, ToSchema)]
#[schema(description = descriptions::USER_LOGIN_RESPONSE_DESCRIPTION)]
pub struct LoginResponse {
    /// JWT access token
    #[schema(example = examples::JWT_ACCESS_TOKEN_EXAMPLE)]
    pub access_token: String,
    /// Refresh token for getting new access tokens
    #[schema(example = examples::REFRESH_TOKEN_EXAMPLE)]
    pub refresh_token: String,
    /// Token type (Bearer)
    #[schema(example = "Bearer")]
    pub token_type: String,
    /// Token expiration time in seconds
    #[schema(example = examples::TOKEN_EXPIRY_EXAMPLE)]
    pub expires_in: u64,
}

/// Refresh token request
#[derive(Debug, Deserialize, ToSchema)]
#[schema(description = descriptions::TOKEN_REFRESH_DESCRIPTION)]
pub struct RefreshTokenRequest {
    /// Refresh token to exchange for new access token
    #[schema(example = examples::REFRESH_TOKEN_EXAMPLE)]
    pub refresh_token: String,
}

/// Refresh token model
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
#[schema(description = "Refresh token information")]
pub struct RefreshToken {
    /// Unique token identifier
    #[schema(example = examples::USER_ID_EXAMPLE)]
    pub id: Uuid,
    /// ID of the user this token belongs to
    #[schema(example = examples::USER_ID_EXAMPLE)]
    pub user_id: Uuid,
    /// Hashed refresh token
    pub token_hash: String,
    /// When the token expires
    #[schema(example = examples::ANALYSIS_CREATED_AT_EXAMPLE)]
    pub expires_at: DateTime<Utc>,
    /// When the token was created
    #[schema(example = examples::ANALYSIS_CREATED_AT_EXAMPLE)]
    pub created_at: DateTime<Utc>,
    /// Whether the token has been revoked
    #[schema(example = false)]
    pub is_revoked: bool,
}

/// User without sensitive information
#[derive(Debug, Serialize, ToSchema)]
#[schema(description = descriptions::USER_PROFILE_DESCRIPTION)]
pub struct UserProfile {
    /// Unique user identifier
    #[schema(example = examples::USER_ID_EXAMPLE)]
    pub id: Uuid,
    /// User's email address
    #[schema(example = examples::USER_EMAIL_EXAMPLE)]
    pub email: String,
    /// User's unique username
    #[schema(example = examples::USER_USERNAME_EXAMPLE)]
    pub username: Option<String>,
    /// User's first name
    #[schema(example = examples::USER_FIRST_NAME_EXAMPLE)]
    pub first_name: Option<String>,
    /// User's last name
    #[schema(example = examples::USER_LAST_NAME_EXAMPLE)]
    pub last_name: Option<String>,
    /// Whether the user account is active
    #[schema(example = true)]
    pub is_active: bool,
    /// When the user was created
    #[schema(example = examples::ANALYSIS_CREATED_AT_EXAMPLE)]
    pub created_at: DateTime<Utc>,
}

impl From<User> for UserProfile {
    fn from(user: User) -> Self {
        Self {
            id: user.id,
            email: user.email,
            username: user.username,
            first_name: user.first_name,
            last_name: user.last_name,
            is_active: user.is_active,
            created_at: user.created_at,
        }
    }
}
