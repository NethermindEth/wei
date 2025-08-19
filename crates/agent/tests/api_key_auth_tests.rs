use axum::http::StatusCode;
use std::collections::HashSet;

use agent::api::middleware::{validate_api_key, ApiKeyValidator};

struct MockValidator {
    api_keys: HashSet<String>,
    auth_enabled: bool,
}

impl MockValidator {
    fn new(api_keys: &[&str], auth_enabled: bool) -> Self {
        let keys: HashSet<String> = api_keys.iter().map(|k: &&str| k.to_string()).collect();
        Self {
            api_keys: keys,
            auth_enabled,
        }
    }
}

impl ApiKeyValidator for MockValidator {
    fn api_key_auth_enabled(&self) -> bool {
        self.auth_enabled
    }
    
    fn is_valid_api_key(&self, key: &str) -> bool {
        if !self.auth_enabled {
            return true;
        }
        
        if self.api_keys.is_empty() {
            return true;
        }
        
        self.api_keys.contains(key)
    }
}

// Test cases
#[test]
fn test_protected_endpoint_auth_required() {
    let validator: MockValidator = MockValidator::new(&["valid-key"], true);
    
    let result: Result<(), StatusCode> = validate_api_key(&validator, "/protected", None);
    
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), StatusCode::UNAUTHORIZED);
}

#[test]
fn test_protected_endpoint_no_key() {
    let validator: MockValidator = MockValidator::new(&["valid-key"], true);
    
    let result: Result<(), StatusCode> = validate_api_key(&validator, "/analyze", None);
    
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), StatusCode::UNAUTHORIZED);
}

#[test]
fn test_protected_endpoint_invalid_key() {
    let validator: MockValidator = MockValidator::new(&["valid-key"], true);
    
    let result: Result<(), StatusCode> = validate_api_key(&validator, "/analyze", Some("invalid-key"));
    
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), StatusCode::FORBIDDEN);
}

#[test]
fn test_protected_endpoint_valid_key() {
    let validator: MockValidator = MockValidator::new(&["valid-key"], true);
    
    let result: Result<(), StatusCode> = validate_api_key(&validator, "/analyze", Some("valid-key"));
    
    assert!(result.is_ok());
}

#[test]
fn test_auth_disabled() {
    let validator: MockValidator = MockValidator::new(&["valid-key"], false);
    
    let result: Result<(), StatusCode> = validate_api_key(&validator, "/analyze", None);
    
    assert!(result.is_ok());
}

#[test]
fn test_protected_endpoint_multiple_valid_keys_unmatched_key() {
    let validator: MockValidator = MockValidator::new(&["matched_key1", "matched_key2", "matched_key3"], true);
    
    let result: Result<(), StatusCode> = validate_api_key(&validator, "/analyze", Some("unmatched_key"));
    
    assert!(result.is_err());
    assert_eq!(result.unwrap_err(), StatusCode::FORBIDDEN);
}
