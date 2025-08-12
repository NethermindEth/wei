//! Database operations for the agent service
//!
//! This module provides database connectivity and repository patterns
//! for the agent service.

use sqlx::PgPool;

/// Database migration management
pub mod migrations;
/// Repository implementations for data access
pub mod repositories;

/// Database connection pool type alias
pub type Database = PgPool;

/// Initialize database connection
#[allow(dead_code)] // TODO: Remove after development phase
pub async fn init_database(database_url: &str) -> Result<Database, sqlx::Error> {
    let pool = PgPool::connect(database_url).await?;

    // Run migrations
    sqlx::migrate!("./migrations").run(&pool).await?;

    Ok(pool)
}
