use clap::Parser;
use tracing::info;

use indexer::config::Config;

mod api;
mod config;
mod db;
mod models;
mod services;
mod utils;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    dotenv::dotenv().ok();

    let config = Config::parse();

    if std::env::var("RUST_LOG").is_err() {
        std::env::set_var("RUST_LOG", "info");
    }

    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .with_target(false)
        .with_thread_ids(true)
        .with_thread_names(true)
        .init();

    info!("Starting Wei Indexer service...");

    // TODO: Initialize database connection
    // TODO: Initialize services
    // TODO: Start API server
    // TODO: Start background indexing tasks

    info!(
        "Wei Indexer service started successfully on port {}",
        config.port
    );

    // Keep the main thread alive
    tokio::signal::ctrl_c()
        .await
        .expect("Failed to listen for ctrl+c");

    info!("Shutting down Wei Indexer service...");
    Ok(())
}
