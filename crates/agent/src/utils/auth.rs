//! Authentication utilities for password hashing and JWT tokens

use argon2::password_hash::{rand_core::OsRng, SaltString};
use argon2::{Argon2, PasswordHash, PasswordHasher, PasswordVerifier};
use jsonwebtoken::{decode, encode, Algorithm, DecodingKey, EncodingKey, Header, Validation};
use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use uuid::Uuid;

use crate::utils::error::{Error, Result};

/// JWT claims structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Claims {
    /// Subject (user ID)
    pub sub: String,
    /// User's email address
    pub email: String,
    /// Expiration time
    pub exp: usize,
    /// Issued at
    pub iat: usize,
    /// JWT ID (for token revocation)
    pub jti: String,
}

/// JWT configuration
#[derive(Clone)]
pub struct JwtConfig {
    /// JWT signing secret
    pub secret: String,
    /// Access token expiry time in seconds
    pub access_token_expiry: u64,
    /// Refresh token expiry time in seconds
    pub refresh_token_expiry: u64,
}

impl JwtConfig {
    /// Create a new JWT configuration
    pub fn new(secret: String) -> Self {
        Self {
            secret,
            access_token_expiry: 3600,    // 1 hour
            refresh_token_expiry: 604800, // 7 days
        }
    }
}

/// Hash a password using Argon2
pub fn hash_password(password: &str) -> Result<String> {
    let salt = SaltString::generate(&mut OsRng);
    let argon2 = Argon2::default();

    let password_hash = argon2
        .hash_password(password.as_bytes(), &salt)
        .map_err(|e| Error::Internal(format!("Failed to hash password: {}", e)))?;

    Ok(password_hash.to_string())
}

/// Verify a password against a hash
pub fn verify_password(password: &str, hash: &str) -> Result<bool> {
    let parsed_hash = PasswordHash::new(hash)
        .map_err(|e| Error::Internal(format!("Failed to parse password hash: {}", e)))?;

    let argon2 = Argon2::default();
    let is_valid = argon2
        .verify_password(password.as_bytes(), &parsed_hash)
        .is_ok();

    Ok(is_valid)
}

/// Generate a JWT access token
pub fn generate_access_token(user_id: Uuid, email: &str, config: &JwtConfig) -> Result<String> {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| Error::Internal(format!("Failed to get current time: {}", e)))?
        .as_secs() as usize;

    let exp = now + config.access_token_expiry as usize;
    let jti = Uuid::new_v4().to_string();

    let claims = Claims {
        sub: user_id.to_string(),
        email: email.to_string(),
        exp,
        iat: now,
        jti,
    };

    let token = encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(config.secret.as_ref()),
    )
    .map_err(|e| Error::Internal(format!("Failed to encode JWT: {}", e)))?;

    Ok(token)
}

/// Generate a refresh token (just a random UUID)
pub fn generate_refresh_token() -> String {
    Uuid::new_v4().to_string()
}

/// Verify and decode a JWT access token
pub fn verify_access_token(token: &str, config: &JwtConfig) -> Result<Claims> {
    let validation = Validation::new(Algorithm::HS256);

    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(config.secret.as_ref()),
        &validation,
    )
    .map_err(|e| match e.kind() {
        jsonwebtoken::errors::ErrorKind::ExpiredSignature => {
            Error::Validation("Token has expired".to_string())
        }
        jsonwebtoken::errors::ErrorKind::InvalidToken => {
            Error::Validation("Invalid token".to_string())
        }
        _ => Error::Internal(format!("Failed to decode JWT: {}", e)),
    })?;

    Ok(token_data.claims)
}

/// Hash a refresh token for storage
pub fn hash_refresh_token(token: &str) -> Result<String> {
    use sha2::{Digest, Sha256};

    let mut hasher = Sha256::new();
    hasher.update(token.as_bytes());
    let result = hasher.finalize();

    Ok(hex::encode(result))
}

/// Get current timestamp in seconds since epoch
pub fn current_timestamp() -> Result<u64> {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|e| Error::Internal(format!("Failed to get current time: {}", e)))
        .map(|d| d.as_secs())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_password_hashing() {
        let password = "test_password_123";
        let hash = hash_password(password).unwrap();

        // Verify the password
        assert!(verify_password(password, &hash).unwrap());

        // Verify wrong password fails
        assert!(!verify_password("wrong_password", &hash).unwrap());
    }

    #[test]
    fn test_jwt_token_generation_and_verification() {
        let config = JwtConfig::new("test_secret".to_string());
        let user_id = Uuid::new_v4();
        let email = "test@example.com";

        // Generate token
        let token = generate_access_token(user_id, email, &config).unwrap();

        // Verify token
        let claims = verify_access_token(&token, &config).unwrap();

        assert_eq!(claims.sub, user_id.to_string());
        assert_eq!(claims.email, email);
    }

    #[test]
    fn test_refresh_token_hashing() {
        let token = "test_refresh_token";
        let hash1 = hash_refresh_token(token).unwrap();
        let hash2 = hash_refresh_token(token).unwrap();

        // Same token should produce same hash
        assert_eq!(hash1, hash2);

        // Different token should produce different hash
        let different_hash = hash_refresh_token("different_token").unwrap();
        assert_ne!(hash1, different_hash);
    }
}
