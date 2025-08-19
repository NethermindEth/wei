//! REST API endpoints for the agent service
//!
//! This module provides the HTTP API for the agent service, including
//! handlers, routes, and middleware for processing requests.

/// Error handling for API endpoints
pub mod error;
/// Request handlers for API endpoints
pub mod handlers;
/// Middleware for request processing
pub mod middleware;
/// Route definitions and router creation
pub mod routes;

// TODO: Remove unused import after development phase
#[allow(unused_imports)]
pub use routes::create_router;
