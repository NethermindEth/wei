//! Authentication integration tests

use agent::{
    db::core::init_db_with_migrations,
    db::repositories::UserRepository,
    models::user::{CreateUserRequest, LoginRequest},
    services::auth::AuthService,
};
use sqlx::postgres::PgPoolOptions;
use uuid::Uuid;

/// Test database manager that creates a unique database and automatically cleans it up
struct TestDatabase {
    db_name: String,
    pool: sqlx::PgPool,
}

impl TestDatabase {
    /// Create a new test database with migrations
    async fn new() -> Self {
        let test_db_name = format!(
            "wei_agent_test_{}",
            Uuid::new_v4().to_string().replace('-', "")
        );
        let postgres_url = "postgresql://postgres:postgres@localhost:5432/postgres";
        let test_db_url = format!(
            "postgresql://postgres:postgres@localhost:5432/{}",
            test_db_name
        );

        // Connect to postgres system database to create test database
        let postgres_pool = PgPoolOptions::new()
            .max_connections(1)
            .connect(postgres_url)
            .await
            .expect("Failed to connect to postgres system database");

        // Create the test database
        sqlx::query(&format!("CREATE DATABASE {}", test_db_name))
            .execute(&postgres_pool)
            .await
            .expect("Failed to create test database");

        // Close the postgres connection
        postgres_pool.close().await;

        // Initialize the test database with migrations
        let pool = init_db_with_migrations(&test_db_url)
            .await
            .expect("Failed to initialize test database with migrations");

        Self {
            db_name: test_db_name,
            pool,
        }
    }

    /// Get the database pool
    fn pool(&self) -> &sqlx::PgPool {
        &self.pool
    }
}

impl Drop for TestDatabase {
    fn drop(&mut self) {
        let db_name = self.db_name.clone();
        let postgres_url = "postgresql://postgres:postgres@localhost:5432/postgres";

        // Spawn a task to clean up the database
        tokio::spawn(async move {
            // Wait a bit to ensure all connections are closed
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;

            // Connect back to postgres to drop the test database
            if let Ok(postgres_pool) = PgPoolOptions::new()
                .max_connections(1)
                .connect(postgres_url)
                .await
            {
                // Terminate any remaining connections to the test database
                sqlx::query(&format!(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{}' AND pid <> pg_backend_pid()",
                    db_name
                ))
                .execute(&postgres_pool)
                .await
                .ok(); // Ignore errors

                // Drop the test database
                sqlx::query(&format!("DROP DATABASE IF EXISTS {}", db_name))
                    .execute(&postgres_pool)
                    .await
                    .ok(); // Ignore errors
            }
        });
    }
}

#[tokio::test]
async fn test_user_registration_and_login() {
    // Initialize test database
    let test_db = TestDatabase::new().await;
    let db = test_db.pool();

    // Create auth service
    let user_repo = UserRepository::new(db.clone());
    let auth_service = AuthService::new(user_repo, "test_secret".to_string());

    // Test user registration
    let register_request = CreateUserRequest {
        email: "test@example.com".to_string(),
        password: "TestPassword123".to_string(),
        username: Some("testuser".to_string()),
        first_name: Some("Test".to_string()),
        last_name: Some("User".to_string()),
    };

    let register_response = auth_service.register(register_request).await.unwrap();
    assert_eq!(register_response.email, "test@example.com");

    // Test user login
    let login_request = LoginRequest {
        email: "test@example.com".to_string(),
        password: "TestPassword123".to_string(),
    };

    let login_response = auth_service.login(login_request).await.unwrap();
    assert_eq!(login_response.token_type, "Bearer");
    assert!(!login_response.access_token.is_empty());
    assert!(!login_response.refresh_token.is_empty());
    assert_eq!(login_response.expires_in, 3600); // 1 hour
}

#[tokio::test]
async fn test_invalid_login() {
    // Initialize test database
    let test_db = TestDatabase::new().await;
    let db = test_db.pool();

    // Create auth service
    let user_repo = UserRepository::new(db.clone());
    let auth_service = AuthService::new(user_repo, "test_secret".to_string());

    // Test invalid login
    let login_request = LoginRequest {
        email: "nonexistent@example.com".to_string(),
        password: "WrongPassword".to_string(),
    };

    let result = auth_service.login(login_request).await;
    assert!(result.is_err());
}

#[tokio::test]
async fn test_password_validation() {
    // Initialize test database
    let test_db = TestDatabase::new().await;
    let db = test_db.pool();

    // Create auth service
    let user_repo = UserRepository::new(db.clone());
    let auth_service = AuthService::new(user_repo, "test_secret".to_string());

    // Test weak password
    let weak_password_request = CreateUserRequest {
        email: "test2@example.com".to_string(),
        password: "weak".to_string(),
        username: None,
        first_name: None,
        last_name: None,
    };

    let result = auth_service.register(weak_password_request).await;
    assert!(result.is_err());

    // Test duplicate email - first register a user, then try to register with same email
    let first_user_request = CreateUserRequest {
        email: "duplicate@example.com".to_string(),
        password: "ValidPassword123".to_string(),
        username: Some("firstuser".to_string()),
        first_name: None,
        last_name: None,
    };

    let result = auth_service.register(first_user_request).await;
    assert!(result.is_ok());

    // Now try to register with the same email
    let duplicate_email_request = CreateUserRequest {
        email: "duplicate@example.com".to_string(), // Same email as above
        password: "AnotherPassword123".to_string(),
        username: Some("anotheruser".to_string()),
        first_name: None,
        last_name: None,
    };

    let result = auth_service.register(duplicate_email_request).await;
    assert!(result.is_err());
}
