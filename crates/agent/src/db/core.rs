//! Core database module
//!
//! This module contains the core database types and functions.

use sqlx::migrate::MigrateError;
use sqlx::postgres::{PgPool, PgPoolOptions};
use std::time::Duration;
use tracing::{error, info};

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
        .next_back()
        .and_then(|s| s.split('?').next())
        .unwrap_or("wei_agent")
        .to_string()
}

/// Check if the database exists and create it if it doesn't
/// Returns a boolean indicating if the database was newly created
/// Build a connection string to the postgres system database
fn build_postgres_system_url(connection_params: &str) -> String {
    if connection_params.contains('/') {
        // Handle URL format like postgres://user:pass@host:port/dbname
        let base_url = connection_params
            .rsplit_once('/')
            .map(|(base, _)| base)
            .unwrap_or(connection_params);
        format!("{}/postgres", base_url)
    } else {
        // Handle simple connection string
        format!("{}/postgres", connection_params)
    }
}

/// Connect to the postgres system database
async fn connect_to_postgres_system(postgres_url: &str) -> Result<PgPool, DatabaseError> {
    info!("Connecting to postgres system database");

    PgPoolOptions::new()
        .max_connections(1)
        .acquire_timeout(Duration::from_secs(3))
        .connect(postgres_url)
        .await
        .map_err(|e| {
            error!("Failed to connect to postgres database: {}", e);
            DatabaseError::Sqlx(e)
        })
}

/// Check if a database exists
async fn database_exists(pool: &PgPool, db_name: &str) -> Result<bool, DatabaseError> {
    let query = format!("SELECT 1 FROM pg_database WHERE datname = '{}'", db_name);
    let exists: Option<(i32,)> = sqlx::query_as(&query)
        .fetch_optional(pool)
        .await
        .map_err(DatabaseError::Sqlx)?;

    Ok(exists.is_some())
}

/// Create a new database
async fn create_database(pool: &PgPool, db_name: &str) -> Result<(), DatabaseError> {
    info!("Creating database: {}", db_name);
    let create_query = format!("CREATE DATABASE {}", db_name);

    sqlx::query(&create_query)
        .execute(pool)
        .await
        .map_err(|e| {
            error!("Failed to create database {}: {}", db_name, e);
            DatabaseError::Sqlx(e)
        })?;

    info!("Created database: {}", db_name);
    Ok(())
}

/// Ensure a database exists, creating it if necessary
pub async fn ensure_database_exists(connection_params: &str) -> Result<bool, DatabaseError> {
    let db_name = extract_db_name(connection_params);
    let postgres_url = build_postgres_system_url(connection_params);

    // Connect to postgres system database
    let pool = connect_to_postgres_system(&postgres_url).await?;

    // Check if database exists
    let exists = database_exists(&pool, &db_name).await?;

    // Create database if it doesn't exist
    if !exists {
        create_database(&pool, &db_name).await?;
        return Ok(true); // New database was created
    }

    info!("Database {} already exists", db_name);
    Ok(false) // Database already existed
}

/// Initialize the database with automatic creation and run migrations only for new databases
pub async fn init_db_with_migrations(database_url: &str) -> Result<Database, DatabaseError> {
    // Connect to the database
    let pool = init_db_pool(database_url).await?;

    // Run migrations only if the database was newly created
    run_migrations(&pool).await?;

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

/// Run migrations
pub async fn run_migrations(pool: &sqlx::Pool<sqlx::Postgres>) -> Result<(), DatabaseError> {
    info!("Run  migrations...");

    sqlx::migrate!("./migrations")
        .run(pool)
        .await
        .map_err(|e| {
            error!("Error running migrations: {}", e);
            DatabaseError::Migration(e)
        })?;

    info!("Migrations completed successfully");
    Ok(())
}
