//! User data models for Clerk integration

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use utoipa::ToSchema;

/// Complete User information from Clerk API
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct User {
    /// Unique identifier for the user
    pub id: String,
    /// Object type - always "user"
    pub object: String,
    /// External ID
    pub external_id: Option<String>,
    /// Primary email address ID
    pub primary_email_address_id: Option<String>,
    /// Primary phone number ID
    pub primary_phone_number_id: Option<String>,
    /// Primary web3 wallet ID
    pub primary_web3_wallet_id: Option<String>,
    /// Username
    pub username: Option<String>,
    /// First name
    pub first_name: Option<String>,
    /// Last name
    pub last_name: Option<String>,
    /// Profile image URL (deprecated, use image_url)
    pub profile_image_url: Option<String>,
    /// Image URL
    pub image_url: String,
    /// Whether user has an image
    pub has_image: bool,
    /// Public metadata
    pub public_metadata: HashMap<String, Value>,
    /// Private metadata
    pub private_metadata: Option<HashMap<String, Value>>,
    /// Unsafe metadata
    pub unsafe_metadata: HashMap<String, Value>,
    /// Email addresses
    pub email_addresses: Vec<EmailAddress>,
    /// Phone numbers
    pub phone_numbers: Vec<PhoneNumber>,
    /// Web3 wallets
    pub web3_wallets: Vec<Web3Wallet>,
    /// Passkeys
    pub passkeys: Vec<Passkey>,
    /// Password enabled
    pub password_enabled: bool,
    /// Two factor authentication enabled
    pub two_factor_enabled: bool,
    /// TOTP enabled
    pub totp_enabled: bool,
    /// Backup code enabled
    pub backup_code_enabled: bool,
    /// MFA enabled timestamp
    pub mfa_enabled_at: Option<i64>,
    /// MFA disabled timestamp
    pub mfa_disabled_at: Option<i64>,
    /// External accounts
    pub external_accounts: Vec<ExternalAccount>,
    /// SAML accounts
    pub saml_accounts: Vec<SamlAccount>,
    /// Last sign-in timestamp
    pub last_sign_in_at: Option<i64>,
    /// Whether user is banned
    pub banned: bool,
    /// Whether user is locked
    pub locked: bool,
    /// Lockout expiration in seconds
    pub lockout_expires_in_seconds: Option<i64>,
    /// Verification attempts remaining
    pub verification_attempts_remaining: Option<i64>,
    /// Last update timestamp
    pub updated_at: i64,
    /// Creation timestamp
    pub created_at: i64,
    /// Delete self enabled
    pub delete_self_enabled: bool,
    /// Create organization enabled
    pub create_organization_enabled: bool,
    /// Create organizations limit
    pub create_organizations_limit: Option<i64>,
    /// Last active timestamp
    pub last_active_at: Option<i64>,
    /// Legal accepted timestamp
    pub legal_accepted_at: Option<i64>,
}

/// Email address from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct EmailAddress {
    /// Email address ID
    pub id: String,
    /// Object type
    pub object: String,
    /// Email address
    pub email_address: String,
    /// Whether reserved
    pub reserved: bool,
    /// Verification status
    pub verification: Option<Verification>,
    /// Linked accounts
    pub linked_to: Vec<IdentificationLink>,
    /// Whether matches SSO connection
    pub matches_sso_connection: bool,
    /// Creation timestamp
    pub created_at: i64,
    /// Update timestamp
    pub updated_at: i64,
}

/// Phone number from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct PhoneNumber {
    /// Phone number ID
    pub id: String,
    /// Object type
    pub object: String,
    /// Phone number
    pub phone_number: String,
    /// Reserved for second factor
    pub reserved_for_second_factor: bool,
    /// Default second factor
    pub default_second_factor: bool,
    /// Whether reserved
    pub reserved: bool,
    /// Verification status
    pub verification: Option<Verification>,
    /// Linked accounts
    pub linked_to: Vec<IdentificationLink>,
    /// Backup codes
    pub backup_codes: Option<Vec<String>>,
    /// Creation timestamp
    pub created_at: i64,
    /// Update timestamp
    pub updated_at: i64,
}

/// Web3 wallet from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Web3Wallet {
    /// Wallet ID
    pub id: String,
    /// Object type
    pub object: String,
    /// Wallet address
    pub web3_wallet: String,
    /// Verification status
    pub verification: Option<Verification>,
    /// Creation timestamp
    pub created_at: i64,
    /// Update timestamp
    pub updated_at: i64,
}

/// Passkey from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Passkey {
    /// Passkey ID
    pub id: String,
    /// Object type
    pub object: String,
    /// Passkey name
    pub name: String,
    /// Last used timestamp
    pub last_used_at: i64,
    /// Verification status
    pub verification: Option<Verification>,
}

/// External account from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ExternalAccount {
    /// Account ID
    pub id: String,
    /// Object type
    pub object: String,
    /// Provider name
    pub provider: String,
    /// Identification ID
    pub identification_id: String,
    /// Provider user ID
    pub provider_user_id: String,
    /// Approved scopes
    pub approved_scopes: String,
    /// Email address
    pub email_address: String,
    /// First name
    pub first_name: String,
    /// Last name
    pub last_name: String,
    /// Avatar URL (deprecated)
    pub avatar_url: Option<String>,
    /// Image URL
    pub image_url: Option<String>,
    /// Username
    pub username: Option<String>,
    /// Phone number
    pub phone_number: Option<String>,
    /// Public metadata
    pub public_metadata: HashMap<String, Value>,
    /// Label
    pub label: Option<String>,
    /// Creation timestamp
    pub created_at: i64,
    /// Update timestamp
    pub updated_at: i64,
    /// Verification status
    pub verification: Option<Verification>,
}

/// SAML account from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct SamlAccount {
    /// Account ID
    pub id: String,
    /// Object type
    pub object: String,
    /// Provider name
    pub provider: String,
    /// Whether active
    pub active: bool,
    /// Email address
    pub email_address: String,
    /// First name
    pub first_name: Option<String>,
    /// Last name
    pub last_name: Option<String>,
    /// Provider user ID
    pub provider_user_id: Option<String>,
    /// Public metadata
    pub public_metadata: HashMap<String, Value>,
    /// Verification status
    pub verification: Option<Verification>,
    /// SAML connection
    pub saml_connection: Option<SamlConnection>,
}

/// SAML connection from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct SamlConnection {
    /// Connection ID
    pub id: String,
    /// Connection name
    pub name: String,
    /// Domain (deprecated)
    pub domain: Option<String>,
    /// Domains
    pub domains: Option<Vec<String>>,
    /// Whether active
    pub active: bool,
    /// Provider
    pub provider: String,
    /// Sync user attributes
    pub sync_user_attributes: bool,
    /// Allow subdomains
    pub allow_subdomains: Option<bool>,
    /// Allow IDP initiated
    pub allow_idp_initiated: Option<bool>,
    /// Disable additional identifications
    pub disable_additional_identifications: Option<bool>,
    /// Creation timestamp
    pub created_at: i64,
    /// Update timestamp
    pub updated_at: i64,
}

/// Verification status from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct Verification {
    /// Object type
    pub object: Option<String>,
    /// Verification status
    pub status: String,
    /// Verification strategy
    pub strategy: Option<String>,
    /// Attempts
    pub attempts: Option<i64>,
    /// Expiration timestamp
    pub expire_at: Option<i64>,
    /// Verified at client
    pub verified_at_client: Option<String>,
}

/// Identification link from Clerk
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct IdentificationLink {
    /// Link type
    #[serde(rename = "type")]
    pub link_type: String,
    /// Link ID
    pub id: String,
}

/// Response for user endpoint
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct UserResponse {
    /// User information
    pub user: User,
}

/// JWT claims from Clerk token
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClerkClaims {
    /// Subject (user ID)
    pub sub: String,
    /// Issuer
    pub iss: String,
    /// Audience
    pub aud: Option<String>,
    /// Expiration time
    pub exp: i64,
    /// Issued at time
    pub iat: i64,
    /// Not before time
    pub nbf: Option<i64>,
    /// Session ID
    pub sid: Option<String>,
    /// Organization ID
    pub org_id: Option<String>,
    /// Organization role
    pub org_role: Option<String>,
    /// Organization slug
    pub org_slug: Option<String>,
}

impl User {
    /// Get the primary email address
    pub fn primary_email(&self) -> Option<String> {
        // First try to find email by primary_email_address_id
        if let Some(primary_id) = &self.primary_email_address_id {
            if let Some(email) = self.email_addresses.iter().find(|e| &e.id == primary_id) {
                return Some(email.email_address.clone());
            }
        }

        // Fallback to first email address
        self.email_addresses
            .first()
            .map(|e| e.email_address.clone())
    }

    /// Check if the primary email is verified
    pub fn is_email_verified(&self) -> bool {
        if let Some(primary_id) = &self.primary_email_address_id {
            if let Some(email) = self.email_addresses.iter().find(|e| &e.id == primary_id) {
                return email
                    .verification
                    .as_ref()
                    .map(|v| v.status == "verified")
                    .unwrap_or(false);
            }
        }

        // Fallback to first email
        self.email_addresses
            .first()
            .and_then(|e| e.verification.as_ref())
            .map(|v| v.status == "verified")
            .unwrap_or(false)
    }

    /// Get full name (first + last name)
    pub fn full_name(&self) -> Option<String> {
        match (&self.first_name, &self.last_name) {
            (Some(first), Some(last)) => Some(format!("{} {}", first, last)),
            (Some(first), None) => Some(first.clone()),
            (None, Some(last)) => Some(last.clone()),
            (None, None) => None,
        }
    }

    /// Convert timestamps to DateTime<Utc>
    pub fn created_at_datetime(&self) -> DateTime<Utc> {
        DateTime::from_timestamp(
            self.created_at / 1000,
            ((self.created_at % 1000) * 1_000_000) as u32,
        )
        .unwrap_or_else(|| DateTime::from_timestamp(0, 0).unwrap())
    }

    /// Convert timestamps to DateTime<Utc>
    pub fn updated_at_datetime(&self) -> DateTime<Utc> {
        DateTime::from_timestamp(
            self.updated_at / 1000,
            ((self.updated_at % 1000) * 1_000_000) as u32,
        )
        .unwrap_or_else(|| DateTime::from_timestamp(0, 0).unwrap())
    }
}
