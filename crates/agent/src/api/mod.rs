//! API module for the agent service

pub mod handlers;
pub mod middleware;
pub mod openapi;
pub mod routes;

// TODO: Remove unused import after development phase
#[allow(unused_imports)]
pub use routes::create_router;
