//! Integration tests for the indexer service

use indexer::config::{DataSourceConfig, DatabaseConfig, ServerConfig, WebhookConfig};

#[tokio::test]
async fn test_indexer_service_creation() {
    // TODO: Implement integration tests
}

#[tokio::test]
async fn test_data_source_strategy() {
    // TODO: Test data source strategy pattern
}

#[tokio::test]
async fn test_proposal_indexing() {
    // TODO: Test proposal indexing functionality
}

#[test]
fn test_config_structure() {
    // Test that config structs can be created and have correct fields
    let server_config = ServerConfig {
        host: "127.0.0.1".to_string(),
        port: 8080,
    };

    assert_eq!(server_config.host, "127.0.0.1");
    assert_eq!(server_config.port, 8080);

    let db_config = DatabaseConfig {
        url: "postgresql://test:test@localhost:5432/test".to_string(),
        max_connections: 5,
    };

    assert_eq!(db_config.url, "postgresql://test:test@localhost:5432/test");
    assert_eq!(db_config.max_connections, 5);
}

#[test]
fn test_data_source_config() {
    let ds_config = DataSourceConfig {
        snapshot: indexer::config::SnapshotConfig {
            base_url: "https://test.snapshot.org".to_string(),
            api_key: Some("test-key".to_string()),
        },
        tally: indexer::config::TallyConfig {
            base_url: "https://test.tally.xyz".to_string(),
            api_key: None,
        },
    };

    assert_eq!(ds_config.snapshot.base_url, "https://test.snapshot.org");
    assert_eq!(ds_config.snapshot.api_key, Some("test-key".to_string()));
    assert_eq!(ds_config.tally.base_url, "https://test.tally.xyz");
    assert_eq!(ds_config.tally.api_key, None);
}

#[test]
fn test_webhook_config() {
    let webhook_config = WebhookConfig {
        secret: "test-secret".to_string(),
        max_retries: 5,
    };

    assert_eq!(webhook_config.secret, "test-secret");
    assert_eq!(webhook_config.max_retries, 5);
}
