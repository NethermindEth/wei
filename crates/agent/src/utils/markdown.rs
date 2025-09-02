/// Extracts JSON content from markdown code blocks
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
pub fn extract_json_from_markdown(content: &str) -> &str {
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_json_with_markers() {
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

        assert_eq!(extract_json_from_markdown(markdown), expected);
    }

    #[test]
    fn test_extract_json_without_markers() {
        let content = r#"{"key": "value"}"#;
        assert_eq!(extract_json_from_markdown(content), content);
    }

    #[test]
    fn test_extract_json_with_start_marker_only() {
        let markdown = r#"```json
{
  "key": "value"
}"#;

        assert_eq!(extract_json_from_markdown(markdown), markdown);
    }
}
