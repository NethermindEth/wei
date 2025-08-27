//! Core database module
//!
//! This module contains the core database types and functions.

use sqlx::postgres::{PgPool, PgPoolOptions};
use std::time::Duration;
use sqlx::migrate::MigrateError;

/// Database type - PostgreSQL connection pool
pub type Database = PgPool;

/// Database error type
pub type DbError = sqlx::Error;

/// Custom error type for database operations
#[derive(Debug, thiserror::Error)]
pub enum DatabaseError {
    /// Error from the underlying SQLx library
    #[error("Database error: {0}")]
    Sqlx(#[from] sqlx::Error),
    
    /// Error during database migration
    #[error("Migration error: {0}")]
    Migration(#[from] MigrateError),
    
    /// Other general errors
    #[error("Other error: {0}")]
    Other(String),
}

/// Extract database name from connection string
fn extract_db_name(connection_params: &str) -> String {
    connection_params
        .split('/')
        .last()
        .and_then(|s| s.split('?').next())
        .unwrap_or("wei_agent")
        .to_string()
}

/// Check if the database exists and create it if it doesn't
/// Returns a boolean indicating if the database was newly created
pub async fn ensure_database_exists(connection_params: &str) -> Result<bool, DatabaseError> {
    let db_name = extract_db_name(connection_params);
    
    // Connect to default postgres database
    let postgres_url = if connection_params.contains('/') {
        // Handle URL format like postgres://user:pass@host:port/dbname
        let base_url = connection_params.rsplitn(2, '/').nth(1).unwrap_or(connection_params);
        format!("{}/postgres", base_url)
    } else {
        // Handle simple connection string
        format!("{}/postgres", connection_params)
    };
    
    tracing::info!("Connecting to postgres database to check if {} exists", db_name);
    
    let pool = PgPoolOptions::new()
        .max_connections(1)
        .acquire_timeout(Duration::from_secs(3))
        .connect(&postgres_url)
        .await
        .map_err(|e| {
            tracing::error!("Failed to connect to postgres database: {}", e);
            DatabaseError::Sqlx(e)
        })?;

    // Check if database exists, create if not
    let query = format!("SELECT 1 FROM pg_database WHERE datname = '{}'", db_name);
    let exists: Option<(i32,)> = sqlx::query_as(&query)
        .fetch_optional(&pool)
        .await
        .map_err(DatabaseError::Sqlx)?;

    let is_new_database = exists.is_none();
    if is_new_database {
        tracing::info!("Database {} does not exist, creating it", db_name);
        let create_query = format!("CREATE DATABASE {}", db_name);
        sqlx::query(&create_query)
            .execute(&pool)
            .await
            .map_err(|e| {
                tracing::error!("Failed to create database {}: {}", db_name, e);
                DatabaseError::Sqlx(e)
            })?;
        tracing::info!("Created database: {}", db_name);
    } else {
        tracing::info!("Database {} already exists", db_name);
    }

    Ok(is_new_database)
}

/// Initialize the database with automatic creation and run migrations only for new databases
pub async fn init_db_with_migrations(database_url: &str) -> Result<Database, DatabaseError> {
    // Create database if needed and check if it's new
    let is_new_database = ensure_database_exists(database_url).await?;
    
    // Connect to the database
    let pool = init_db_pool(database_url).await?;
    
    // Run migrations only if the database was newly created
    if is_new_database {
        tracing::info!("New database detected, running migrations");
        sqlx::migrate!("./migrations")
            .run(&pool)
            .await
            .map_err(|e| {
                tracing::error!("Error running migrations: {}", e);
                DatabaseError::Migration(e)
            })?;
        
        tracing::info!("Database migrations completed successfully");
    } else {
        tracing::info!("Using existing database, skipping migrations");
    }
    
    Ok(pool)
}

/// Initialize the database connection pool
pub async fn init_db_pool(database_url: &str) -> Result<Database, DbError> {
    PgPoolOptions::new()
        .max_connections(10)
        .acquire_timeout(Duration::from_secs(3))
        .connect(database_url)
        .await
}
