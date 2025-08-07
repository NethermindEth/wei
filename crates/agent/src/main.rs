use tracing::info;

mod api;
mod config;
mod db;
mod models;
mod services;
mod utils;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt::init();

    info!("Starting Wei Agent service...");

    // TODO: Initialize configuration
    // TODO: Initialize database connection
    // TODO: Initialize AI services
    // TODO: Start API server
    // TODO: Start webhook listeners

    info!("Wei Agent service started successfully");

    // Keep the main thread alive
    tokio::signal::ctrl_c()
        .await
        .expect("Failed to listen for ctrl+c");

    info!("Shutting down Wei Agent service...");
    Ok(())
}
