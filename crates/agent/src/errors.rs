use openrouter_rs::error::Error as OpenRouterError;
use std::fmt;

#[derive(Debug)]
pub enum Error {
    Internal(String),
    InvalidInput(String),
    OpenRouter(String),
    // Add other error types as needed
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Error::Internal(msg) => write!(f, "Internal error: {}", msg),
            Error::InvalidInput(msg) => write!(f, "Invalid input: {}", msg),
            Error::OpenRouter(msg) => write!(f, "OpenRouter error: {}", msg),
        }
    }
}

impl std::error::Error for Error {}

// Implement From trait for OpenRouterError
impl From<OpenRouterError> for Error {
    fn from(err: OpenRouterError) -> Self {
        Error::OpenRouter(err.to_string())
    }
}

// Implement From trait for std::io::Error
impl From<std::io::Error> for Error {
    fn from(err: std::io::Error) -> Self {
        Error::Internal(format!("IO error: {}", err))
    }
}

// Implement From trait for serde_json::Error
impl From<serde_json::Error> for Error {
    fn from(err: serde_json::Error) -> Self {
        Error::Internal(format!("JSON error: {}", err))
    }
}
