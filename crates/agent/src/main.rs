use std::net::SocketAddr;

use agent::api::create_router;
use clap::Parser;
use tokio::net::TcpListener;
use tracing::{error, info};

use tokio::signal;

#[cfg(unix)]
use tokio::signal::unix::{signal, SignalKind};

use agent::config::Config;
use agent::services::agent::AgentService;

#[tokio::main]
#[allow(clippy::result_large_err)]
async fn main() -> agent::Result<()> {
    dotenv::dotenv().ok();

    let config = Config::parse();

    if std::env::var("RUST_LOG").is_err() {
        std::env::set_var("RUST_LOG", "info");
    }

    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .with_target(false)
        .with_thread_ids(true)
        .with_thread_names(true)
        .init();

    info!("Starting Wei Agent service...");

    // Initialize database connection using config with automatic database creation and migrations
    let db = match agent::db::core::init_db_with_migrations(&config.database_url).await {
        Ok(pool) => {
            info!("Database initialized successfully with migrations");
            pool
        }
        Err(e) => {
            error!("Failed to initialize database: {}", e);
            return Err(agent::utils::error::Error::Internal(format!(
                "Database initialization failed: {}",
                e
            )));
        }
    };

    info!("Wei Agent service started successfully");

    let agent_service = AgentService::new(db, config.clone());

    let app = create_router(&config, agent_service);

    let addr = SocketAddr::from(([0, 0, 0, 0], config.port));
    let listener = TcpListener::bind(addr).await.unwrap();

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .unwrap();

    info!("Shutting down Wei Agent service...");
    Ok(())
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install CTRL+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal(SignalKind::terminate())
            .expect("failed to install SIGTERM handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {
            info!("Received CTRL+C signal");
        },
        _ = terminate => {
            info!("Received SIGTERM signal");
        },
    }

    info!("Graceful shutdown signal received, server will stop accepting new requests");
}
