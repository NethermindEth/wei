//! User repository for database operations

use chrono::Utc;
use uuid::Uuid;

use crate::{
    db::core::Database,
    models::user::{RefreshToken, User},
    utils::error::{Error, Result},
};

/// User repository for database operations
#[derive(Clone)]
pub struct UserRepository {
    db: Database,
}

impl UserRepository {
    /// Create a new user repository
    pub fn new(db: Database) -> Self {
        Self { db }
    }

    /// Create a new user
    pub async fn create_user(
        &self,
        email: &str,
        password_hash: &str,
        username: Option<&str>,
        first_name: Option<&str>,
        last_name: Option<&str>,
    ) -> Result<User> {
        let row = sqlx::query!(
            r#"
            INSERT INTO users (email, password_hash, username, first_name, last_name)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, email, password_hash, username, first_name, last_name, is_active, created_at, updated_at
            "#,
            email,
            password_hash,
            username,
            first_name,
            last_name
        )
        .fetch_one(&self.db)
        .await
        .map_err(|e| {
            if e.to_string().contains("duplicate key") {
                if e.to_string().contains("email") {
                    Error::Validation("User with this email already exists".to_string())
                } else if e.to_string().contains("username") {
                    Error::Validation("User with this username already exists".to_string())
                } else {
                    Error::Validation("User with this information already exists".to_string())
                }
            } else {
                Error::Internal(format!("Failed to create user: {}", e))
            }
        })?;

        let user = User {
            id: row.id,
            email: row.email,
            password_hash: row.password_hash,
            username: row.username,
            first_name: row.first_name,
            last_name: row.last_name,
            is_active: row.is_active,
            created_at: row.created_at,
            updated_at: row.updated_at,
        };

        Ok(user)
    }

    /// Find user by email
    pub async fn find_by_email(&self, email: &str) -> Result<Option<User>> {
        let row = sqlx::query!(
            r#"
            SELECT id, email, password_hash, username, first_name, last_name, is_active, created_at, updated_at
            FROM users
            WHERE email = $1
            "#,
            email
        )
        .fetch_optional(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to find user by email: {}", e)))?;

        let user = row.map(|row| User {
            id: row.id,
            email: row.email,
            password_hash: row.password_hash,
            username: row.username,
            first_name: row.first_name,
            last_name: row.last_name,
            is_active: row.is_active,
            created_at: row.created_at,
            updated_at: row.updated_at,
        });

        Ok(user)
    }

    /// Find user by ID
    pub async fn find_by_id(&self, id: Uuid) -> Result<Option<User>> {
        let row = sqlx::query!(
            r#"
            SELECT id, email, password_hash, username, first_name, last_name, is_active, created_at, updated_at
            FROM users
            WHERE id = $1
            "#,
            id
        )
        .fetch_optional(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to find user by ID: {}", e)))?;

        let user = row.map(|row| User {
            id: row.id,
            email: row.email,
            password_hash: row.password_hash,
            username: row.username,
            first_name: row.first_name,
            last_name: row.last_name,
            is_active: row.is_active,
            created_at: row.created_at,
            updated_at: row.updated_at,
        });

        Ok(user)
    }

    /// Find user by username
    pub async fn find_by_username(&self, username: &str) -> Result<Option<User>> {
        let row = sqlx::query!(
            r#"
            SELECT id, email, password_hash, username, first_name, last_name, is_active, created_at, updated_at
            FROM users
            WHERE username = $1
            "#,
            username
        )
        .fetch_optional(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to find user by username: {}", e)))?;

        let user = row.map(|row| User {
            id: row.id,
            email: row.email,
            password_hash: row.password_hash,
            username: row.username,
            first_name: row.first_name,
            last_name: row.last_name,
            is_active: row.is_active,
            created_at: row.created_at,
            updated_at: row.updated_at,
        });

        Ok(user)
    }

    /// Update user's last login time
    pub async fn update_last_login(&self, user_id: Uuid) -> Result<()> {
        let _ = sqlx::query!(
            r#"
            UPDATE users
            SET updated_at = $1
            WHERE id = $2
            "#,
            Utc::now(),
            user_id
        )
        .execute(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to update last login: {}", e)))?;

        Ok(())
    }

    /// Create a refresh token
    pub async fn create_refresh_token(
        &self,
        user_id: Uuid,
        token_hash: &str,
        expires_at: chrono::DateTime<Utc>,
    ) -> Result<RefreshToken> {
        let row = sqlx::query!(
            r#"
            INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
            VALUES ($1, $2, $3)
            RETURNING id, user_id, token_hash, expires_at, created_at, is_revoked
            "#,
            user_id,
            token_hash,
            expires_at
        )
        .fetch_one(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to create refresh token: {}", e)))?;

        let refresh_token = RefreshToken {
            id: row.id,
            user_id: row.user_id,
            token_hash: row.token_hash,
            expires_at: row.expires_at,
            created_at: row.created_at,
            is_revoked: row.is_revoked,
        };

        Ok(refresh_token)
    }

    /// Find refresh token by hash
    pub async fn find_refresh_token(&self, token_hash: &str) -> Result<Option<RefreshToken>> {
        let row = sqlx::query!(
            r#"
            SELECT id, user_id, token_hash, expires_at, created_at, is_revoked
            FROM refresh_tokens
            WHERE token_hash = $1 AND is_revoked = FALSE AND expires_at > NOW()
            "#,
            token_hash
        )
        .fetch_optional(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to find refresh token: {}", e)))?;

        let token = row.map(|row| RefreshToken {
            id: row.id,
            user_id: row.user_id,
            token_hash: row.token_hash,
            expires_at: row.expires_at,
            created_at: row.created_at,
            is_revoked: row.is_revoked,
        });

        Ok(token)
    }

    /// Revoke refresh token
    pub async fn revoke_refresh_token(&self, token_hash: &str) -> Result<()> {
        let _ = sqlx::query!(
            r#"
            UPDATE refresh_tokens
            SET is_revoked = TRUE
            WHERE token_hash = $1
            "#,
            token_hash
        )
        .execute(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to revoke refresh token: {}", e)))?;

        Ok(())
    }

    /// Revoke all refresh tokens for a user
    pub async fn revoke_all_user_tokens(&self, user_id: Uuid) -> Result<()> {
        let _ = sqlx::query!(
            r#"
            UPDATE refresh_tokens
            SET is_revoked = TRUE
            WHERE user_id = $1
            "#,
            user_id
        )
        .execute(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to revoke user tokens: {}", e)))?;

        Ok(())
    }

    /// Clean up expired refresh tokens
    pub async fn cleanup_expired_tokens(&self) -> Result<u64> {
        let result = sqlx::query!(
            r#"
            DELETE FROM refresh_tokens
            WHERE expires_at < NOW()
            "#
        )
        .execute(&self.db)
        .await
        .map_err(|e| Error::Internal(format!("Failed to cleanup expired tokens: {}", e)))?;

        Ok(result.rows_affected())
    }
}
