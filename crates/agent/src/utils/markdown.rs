use serde::de::DeserializeOwned;
use thiserror::Error;

/// Error types for JSON extraction from markdown
#[derive(Debug, Error)]
pub enum ExtractJsonError {
    /// No JSON code block found in markdown
    #[error("No JSON code block found in markdown")]
    NoJsonBlock,

    /// JSON code block is not properly closed
    #[error("JSON code block is not properly closed")]
    UnclosedJsonBlock,

    /// Failed to parse JSON
    #[error("Failed to parse JSON: {0}")]
    ParseError(#[from] serde_json::Error),
}

/// Extracts and parses JSON from a markdown code block
///
/// # Examples
/// ```
/// use serde::Deserialize;
/// use agent::utils::markdown::extract_json_from_markdown;
///
/// #[derive(Deserialize, Debug, PartialEq)]
/// struct TestJson {
///     key: String,
/// }
///
/// let markdown = "Some text before\n```json\n{\n  \"key\": \"value\"\n}\n```\nSome text after";
///
/// let json: TestJson = extract_json_from_markdown(markdown).unwrap();
/// assert_eq!(json.key, "value");
/// ```
pub fn extract_json_from_markdown<T: DeserializeOwned>(
    content: &str,
) -> Result<T, ExtractJsonError> {
    const JSON_MARKER_START: &str = "```json";
    const JSON_MARKER_END: &str = "```";

    // Find the JSON block
    let start_idx = content
        .find(JSON_MARKER_START)
        .ok_or(ExtractJsonError::NoJsonBlock)?;

    let json_start = start_idx + JSON_MARKER_START.len();

    let end_idx = content[json_start..]
        .find(JSON_MARKER_END)
        .ok_or(ExtractJsonError::UnclosedJsonBlock)?;

    let json_str = content[json_start..json_start + end_idx].trim();

    // Parse the JSON
    serde_json::from_str(json_str).map_err(ExtractJsonError::ParseError)
}

/// Extracts JSON content from markdown code blocks without parsing
///
/// If the content contains a JSON code block (```json ... ```), this function
/// will extract and return the JSON content without the markdown markers.
/// If no JSON code block is found, it returns the original content.
///
/// # Arguments
///
/// * `content` - The string that may contain markdown with JSON code blocks
///
/// # Returns
///
/// The extracted JSON content or the original content if no JSON block is found
pub fn extract_json_string_from_markdown(content: &str) -> &str {
    const JSON_MARKER_START: &str = "```json";
    const JSON_MARKER_END: &str = "```";

    if let Some(start_idx) = content.find(JSON_MARKER_START) {
        let json_start = start_idx + JSON_MARKER_START.len();
        if let Some(end_idx) = content[json_start..].find(JSON_MARKER_END) {
            return content[json_start..json_start + end_idx].trim();
        }
    }
    content
}

/// Alternative implementation that returns Option<T> for simpler error handling
///
/// # Arguments
///
/// * `content` - The string that may contain markdown with JSON code blocks
///
/// # Returns
///
/// An Option containing the parsed JSON object or None if extraction/parsing fails
pub fn try_extract_json_from_markdown<T: DeserializeOwned>(content: &str) -> Option<T> {
    const JSON_MARKER_START: &str = "```json";
    const JSON_MARKER_END: &str = "```";

    let start_idx = content.find(JSON_MARKER_START)?;
    let json_start = start_idx + JSON_MARKER_START.len();
    let end_idx = content[json_start..].find(JSON_MARKER_END)?;
    let json_str = content[json_start..json_start + end_idx].trim();

    serde_json::from_str(json_str).ok()
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde::Deserialize;

    #[derive(Deserialize, Debug, PartialEq)]
    struct TestJson {
        key: String,
    }

    #[test]
    fn test_extract_json_with_markers() {
        let markdown = r#"Some text before
```json
{
  "key": "value"
}
```
Some text after"#;

        let expected = TestJson {
            key: "value".to_string(),
        };
        let result = extract_json_from_markdown::<TestJson>(markdown).unwrap();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_extract_json_string_with_markers() {
        let markdown = r#"Some text before
```json
{
  "key": "value"
}
```
Some text after"#;

        let expected = r#"{
  "key": "value"
}"#;

        assert_eq!(extract_json_string_from_markdown(markdown), expected);
    }

    #[test]
    fn test_extract_json_string_without_markers() {
        let content = r#"{"key": "value"}"#;
        assert_eq!(extract_json_string_from_markdown(content), content);
    }

    #[test]
    fn test_extract_json_string_with_start_marker_only() {
        let markdown = r#"```json
{
  "key": "value"
}"#;

        assert_eq!(extract_json_string_from_markdown(markdown), markdown);
    }

    #[test]
    fn test_try_extract_json_from_markdown() {
        let markdown = r#"Some text before
```json
{
  "key": "value"
}
```
Some text after"#;

        let expected = TestJson {
            key: "value".to_string(),
        };
        let result = try_extract_json_from_markdown::<TestJson>(markdown).unwrap();
        assert_eq!(result, expected);
    }
}
