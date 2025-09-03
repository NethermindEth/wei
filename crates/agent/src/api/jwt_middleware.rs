//! JWT authentication middleware

use axum::{
    extract::{Request, State},
    http::header::AUTHORIZATION,
    middleware::Next,
    response::Response,
};
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};
use uuid::Uuid;

use crate::{
    api::{error::ApiError, routes::AppState},
    utils::auth::Claims,
};

/// JWT authentication middleware
///
/// This middleware validates JWT tokens in the Authorization header.
/// If the token is valid, it extracts the user information and adds it to the request.
/// If the token is missing or invalid, the request is rejected.
pub async fn jwt_auth(
    State(state): State<AppState>,
    mut request: Request,
    next: Next,
) -> Result<Response, ApiError> {
    // Extract the Authorization header
    let auth_header = request
        .headers()
        .get(AUTHORIZATION)
        .and_then(|header| header.to_str().ok());

    let token = match auth_header {
        Some(header) if header.starts_with("Bearer ") => {
            header.strip_prefix("Bearer ").unwrap_or("")
        }
        Some(_) => {
            return Err(ApiError::unauthorized(
                "Invalid authorization header format",
            ));
        }
        None => {
            return Err(ApiError::unauthorized("Authorization header is required"));
        }
    };

    // Verify the JWT token
    let claims = verify_jwt_token(token, &state.config.jwt_secret)
        .map_err(|_| ApiError::unauthorized("Invalid or expired token"))?;

    // Add user information to request extensions
    request.extensions_mut().insert(claims);

    Ok(next.run(request).await)
}

/// Verify JWT token and extract claims
fn verify_jwt_token(token: &str, secret: &str) -> Result<Claims, jsonwebtoken::errors::Error> {
    let validation = Validation::new(Algorithm::HS256);
    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret.as_ref()),
        &validation,
    )?;

    Ok(token_data.claims)
}

/// Extract user ID from request extensions (set by JWT middleware)
pub fn get_current_user_id(request: &Request) -> Option<Uuid> {
    request
        .extensions()
        .get::<Claims>()
        .and_then(|claims| Uuid::parse_str(&claims.sub).ok())
}

/// Extract user email from request extensions (set by JWT middleware)
pub fn get_current_user_email(request: &Request) -> Option<String> {
    request
        .extensions()
        .get::<Claims>()
        .map(|claims| claims.email.clone())
}

/// Extract full claims from request extensions (set by JWT middleware)
pub fn get_current_claims(request: &Request) -> Option<&Claims> {
    request.extensions().get::<Claims>()
}

/// User ID extractor for JWT-authenticated routes
#[derive(Debug, Clone)]
pub struct UserId(pub Uuid);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::utils::auth::{generate_access_token, JwtConfig};
    use uuid::Uuid;

    #[tokio::test]
    async fn test_jwt_middleware_valid_token() {
        let config = JwtConfig::new("test_secret".to_string());
        let user_id = Uuid::new_v4();
        let email = "test@example.com";

        let token = generate_access_token(user_id, email, &config).unwrap();

        // Test token verification
        let claims = verify_jwt_token(&token, &config.secret).unwrap();
        assert_eq!(claims.sub, user_id.to_string());
        assert_eq!(claims.email, email);
    }

    #[tokio::test]
    async fn test_jwt_middleware_invalid_token() {
        let result = verify_jwt_token("invalid_token", "test_secret");
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_jwt_middleware_missing_bearer() {
        let result = verify_jwt_token("token_without_bearer", "test_secret");
        assert!(result.is_err());
    }
}
