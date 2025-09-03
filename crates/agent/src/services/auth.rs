//! Authentication service for user management and JWT tokens

use chrono::{Duration, Utc};
use uuid::Uuid;

use crate::{
    db::repositories::user::UserRepository,
    models::user::{
        CreateUserRequest, LoginRequest, LoginResponse, RefreshTokenRequest, RegisterResponse,
        UserProfile,
    },
    utils::{
        auth::{
            generate_access_token, generate_refresh_token, hash_password, hash_refresh_token,
            verify_password, JwtConfig,
        },
        error::{Error, Result},
    },
};

/// Authentication service
#[derive(Clone)]
pub struct AuthService {
    user_repo: UserRepository,
    jwt_config: JwtConfig,
}

impl AuthService {
    /// Create a new authentication service
    pub fn new(user_repo: UserRepository, jwt_secret: String) -> Self {
        Self {
            user_repo,
            jwt_config: JwtConfig::new(jwt_secret),
        }
    }

    /// Register a new user
    pub async fn register(&self, request: CreateUserRequest) -> Result<RegisterResponse> {
        // Validate email format
        if !self.is_valid_email(&request.email) {
            return Err(Error::Validation("Invalid email format".to_string()));
        }

        // Validate password strength
        if !self.is_strong_password(&request.password) {
            return Err(Error::Validation(
                "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one number".to_string()
            ));
        }

        // Validate username if provided
        if let Some(ref username) = request.username {
            if !self.is_valid_username(username) {
                return Err(Error::Validation(
                    "Username must be 3-50 characters long and contain only letters, numbers, and underscores".to_string()
                ));
            }
        }

        // Check if user already exists by email
        if self
            .user_repo
            .find_by_email(&request.email)
            .await?
            .is_some()
        {
            return Err(Error::Validation(
                "User with this email already exists".to_string(),
            ));
        }

        // Check if username is already taken (if provided)
        if let Some(ref username) = request.username {
            if self.user_repo.find_by_username(username).await?.is_some() {
                return Err(Error::Validation("Username is already taken".to_string()));
            }
        }

        // Hash the password
        let password_hash = hash_password(&request.password)?;

        // Create the user
        let user = self
            .user_repo
            .create_user(
                &request.email,
                &password_hash,
                request.username.as_deref(),
                request.first_name.as_deref(),
                request.last_name.as_deref(),
            )
            .await?;

        Ok(RegisterResponse {
            user_id: user.id,
            email: user.email,
            message: "User registered successfully".to_string(),
        })
    }

    /// Login a user
    pub async fn login(&self, request: LoginRequest) -> Result<LoginResponse> {
        // Find user by email
        let user = self
            .user_repo
            .find_by_email(&request.email)
            .await?
            .ok_or_else(|| Error::Validation("Invalid email or password".to_string()))?;

        // Check if user is active
        if !user.is_active {
            return Err(Error::Validation("Account is deactivated".to_string()));
        }

        // Verify password
        if !verify_password(&request.password, &user.password_hash)? {
            return Err(Error::Validation("Invalid email or password".to_string()));
        }

        // Generate tokens
        let access_token = generate_access_token(user.id, &user.email, &self.jwt_config)?;
        let refresh_token = generate_refresh_token();
        let refresh_token_hash = hash_refresh_token(&refresh_token)?;

        // Store refresh token in database
        let expires_at =
            Utc::now() + Duration::seconds(self.jwt_config.refresh_token_expiry as i64);
        self.user_repo
            .create_refresh_token(user.id, &refresh_token_hash, expires_at)
            .await?;

        // Update last login time
        self.user_repo.update_last_login(user.id).await?;

        Ok(LoginResponse {
            access_token,
            refresh_token,
            token_type: "Bearer".to_string(),
            expires_in: self.jwt_config.access_token_expiry,
        })
    }

    /// Refresh access token using refresh token
    pub async fn refresh_token(&self, request: RefreshTokenRequest) -> Result<LoginResponse> {
        // Hash the refresh token to find it in database
        let refresh_token_hash = hash_refresh_token(&request.refresh_token)?;

        // Find the refresh token in database
        let stored_token = self
            .user_repo
            .find_refresh_token(&refresh_token_hash)
            .await?
            .ok_or_else(|| Error::Validation("Invalid refresh token".to_string()))?;

        // Get the user
        let user = self
            .user_repo
            .find_by_id(stored_token.user_id)
            .await?
            .ok_or_else(|| Error::Validation("User not found".to_string()))?;

        // Check if user is still active
        if !user.is_active {
            return Err(Error::Validation("Account is deactivated".to_string()));
        }

        // Generate new access token
        let access_token = generate_access_token(user.id, &user.email, &self.jwt_config)?;

        // Generate new refresh token and revoke the old one
        let new_refresh_token = generate_refresh_token();
        let new_refresh_token_hash = hash_refresh_token(&new_refresh_token)?;

        // Revoke old refresh token
        self.user_repo
            .revoke_refresh_token(&refresh_token_hash)
            .await?;

        // Store new refresh token
        let expires_at =
            Utc::now() + Duration::seconds(self.jwt_config.refresh_token_expiry as i64);
        self.user_repo
            .create_refresh_token(user.id, &new_refresh_token_hash, expires_at)
            .await?;

        Ok(LoginResponse {
            access_token,
            refresh_token: new_refresh_token,
            token_type: "Bearer".to_string(),
            expires_in: self.jwt_config.access_token_expiry,
        })
    }

    /// Get user profile by ID
    pub async fn get_user_profile(&self, user_id: Uuid) -> Result<UserProfile> {
        let user = self
            .user_repo
            .find_by_id(user_id)
            .await?
            .ok_or_else(|| Error::Validation("User not found".to_string()))?;

        Ok(UserProfile::from(user))
    }

    /// Logout user (revoke all refresh tokens)
    pub async fn logout(&self, user_id: Uuid) -> Result<()> {
        self.user_repo.revoke_all_user_tokens(user_id).await?;
        Ok(())
    }

    /// Validate email format
    fn is_valid_email(&self, email: &str) -> bool {
        // Basic email validation - in production, use a proper email validation library
        if email.len() < 5 || email.len() > 255 {
            return false;
        }

        // Must contain exactly one @ symbol
        let at_count = email.matches('@').count();
        if at_count != 1 {
            return false;
        }

        // Split by @ and check both parts
        let parts: Vec<&str> = email.split('@').collect();
        let local_part = parts[0];
        let domain_part = parts[1];

        // Local part cannot be empty
        if local_part.is_empty() {
            return false;
        }

        // Domain part cannot be empty
        if domain_part.is_empty() {
            return false;
        }

        // Domain must contain at least one dot
        if !domain_part.contains('.') {
            return false;
        }

        true
    }

    /// Validate password strength
    fn is_strong_password(&self, password: &str) -> bool {
        if password.len() < 8 {
            return false;
        }

        let has_uppercase = password.chars().any(|c| c.is_uppercase());
        let has_lowercase = password.chars().any(|c| c.is_lowercase());
        let has_digit = password.chars().any(|c| c.is_ascii_digit());

        has_uppercase && has_lowercase && has_digit
    }

    /// Validate username format
    fn is_valid_username(&self, username: &str) -> bool {
        if username.len() < 3 || username.len() > 50 {
            return false;
        }

        // Username can only contain letters, numbers, and underscores
        username.chars().all(|c| c.is_alphanumeric() || c == '_')
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_email_validation() {
        let service = create_test_auth_service().await;

        assert!(service.is_valid_email("test@example.com"));
        assert!(service.is_valid_email("user.name@domain.co.uk"));
        assert!(!service.is_valid_email("invalid-email"));
        assert!(!service.is_valid_email("@domain.com"));
        assert!(!service.is_valid_email("user@"));
    }

    #[tokio::test]
    async fn test_password_validation() {
        let service = create_test_auth_service().await;

        assert!(service.is_strong_password("Password123"));
        assert!(service.is_strong_password("MySecure1"));
        assert!(!service.is_strong_password("weak"));
        assert!(!service.is_strong_password("password"));
        assert!(!service.is_strong_password("PASSWORD"));
        assert!(!service.is_strong_password("12345678"));
    }

    async fn create_test_auth_service() -> AuthService {
        // For unit tests that only test validation methods, we can create a service
        // with a dummy user repository since we're not actually using the database
        use crate::db::repositories::UserRepository;
        use sqlx::postgres::PgPoolOptions;

        // Create a dummy database connection (won't be used for validation tests)
        let dummy_url = "postgresql://postgres:postgres@localhost:5432/postgres";
        let dummy_pool = PgPoolOptions::new()
            .max_connections(1)
            .connect(dummy_url)
            .await
            .expect("Failed to create dummy database connection");

        let user_repo = UserRepository::new(dummy_pool);
        AuthService::new(user_repo, "test_secret".to_string())
    }
}
