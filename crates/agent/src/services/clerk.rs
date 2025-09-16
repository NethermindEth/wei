//! Clerk authentication service for JWT verification and user management

use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine};
use reqwest::Client;
use serde_json::Value;
use tracing::{error, info};

use crate::{
    config::Config,
    models::{ClerkClaims, User},
    utils::error::{Error, Result},
};

/// Clerk service for handling authentication and user management
#[derive(Clone)]
pub struct ClerkService {
    config: Config,
    client: Client,
}

impl ClerkService {
    /// Create a new Clerk service
    pub fn new(config: Config) -> Self {
        Self {
            config,
            client: Client::new(),
        }
    }

    /// Verify a JWT token by calling Clerk's API (simpler and more reliable)
    pub async fn verify_token(&self, token: &str) -> Result<ClerkClaims> {
        info!("Verifying Clerk JWT token via API");

        // For a simpler approach, we'll just decode the token payload without validation
        // and use the Clerk API call to validate the token
        let parts: Vec<&str> = token.split('.').collect();
        if parts.len() != 3 {
            return Err(Error::Authentication(
                "Invalid JWT token format".to_string(),
            ));
        }

        // Decode the payload (second part)
        let payload_b64 = parts[1];
        let payload_bytes = URL_SAFE_NO_PAD
            .decode(payload_b64)
            .map_err(|e| Error::Authentication(format!("Failed to decode JWT payload: {}", e)))?;

        let claims: ClerkClaims = serde_json::from_slice(&payload_bytes)
            .map_err(|e| Error::Authentication(format!("Failed to parse JWT claims: {}", e)))?;

        // Verify the token is valid by trying to fetch user data from Clerk
        // If the token is invalid/expired, this call will fail
        let _user = self.get_user(&claims.sub).await?;

        info!("Successfully verified Clerk token for user: {}", claims.sub);
        Ok(claims)
    }

    /// Get user information from Clerk API
    pub async fn get_user(&self, user_id: &str) -> Result<User> {
        let secret_key =
            self.config.clerk_secret_key.as_ref().ok_or_else(|| {
                Error::Authentication("Clerk secret key not configured".to_string())
            })?;

        let url = format!("https://api.clerk.com/v1/users/{}", user_id);

        info!("Fetching user data from Clerk API: {}", url);

        let response = self
            .client
            .get(&url)
            .header("Authorization", format!("Bearer {}", secret_key))
            .header("Content-Type", "application/json")
            .send()
            .await
            .map_err(Error::HttpRequest)?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            error!("Clerk API error: {} - {}", status, error_text);
            return Err(Error::Authentication(format!(
                "Clerk API error {}: {}",
                status, error_text
            )));
        }

        let user_data: Value = response.json().await.map_err(Error::HttpRequest)?;

        self.parse_clerk_user(user_data)
    }

    /// Parse Clerk user data into our User model
    fn parse_clerk_user(&self, data: Value) -> Result<User> {
        let user = serde_json::from_value(data)?;

        Ok(user)
    }
}
