//! REST API endpoints for the indexer service
//!
//! This module provides the HTTP API for the indexer service, including
//! handlers, routes, and middleware for processing requests.

/// Request handlers for API endpoints
pub mod handlers;
/// Middleware for request processing
pub mod middleware;
/// Route definitions and router creation
pub mod routes;
// TODO: Remove unused import after development phase
#[allow(unused_imports)]
pub use routes::create_router;
