use once_cell::sync::Lazy;
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
    // Common JSON code block markers with more variations
    const JSON_MARKERS: [&str; 6] = [
        "```json",
        "```JSON",
        "```js",
        "```javascript",
        "```typescript",
        "```ts",
    ];
    const CODE_MARKERS: [&str; 4] = ["```", "~~~", "'''", "```\n"];

    // First try to find a proper JSON code block
    for start_marker in &JSON_MARKERS {
        if let Some(start_idx) = content.find(start_marker) {
            let json_start = start_idx + start_marker.len();

            // Find the closing marker
            for end_marker in &CODE_MARKERS {
                if let Some(end_idx) = content[json_start..].find(end_marker) {
                    let json_str = content[json_start..json_start + end_idx].trim();

                    // Try to parse the JSON
                    match serde_json::from_str(json_str) {
                        Ok(parsed) => return Ok(parsed),
                        Err(_) => {
                            // Try to fix common JSON issues and parse again
                            if let Some(fixed_json) = fix_common_json_issues(json_str) {
                                if let Ok(parsed) = serde_json::from_str(&fixed_json) {
                                    return Ok(parsed);
                                } // Continue to next approach if this fails
                            } else {
                                continue; // Try next end marker if parsing fails
                            }
                        }
                    }
                }
            }
        }
    }

    // Try with any code block marker (not just JSON specific)
    for code_marker in &CODE_MARKERS {
        if let Some(start_idx) = content.find(code_marker) {
            let potential_start = start_idx + code_marker.len();

            // Find the closing marker
            if let Some(end_idx) = content[potential_start..].find(code_marker) {
                let potential_json = content[potential_start..potential_start + end_idx].trim();

                // Try to parse this as JSON
                match serde_json::from_str(potential_json) {
                    Ok(parsed) => return Ok(parsed),
                    Err(_) => {
                        // Try to fix common JSON issues and parse again
                        if let Some(fixed_json) = fix_common_json_issues(potential_json) {
                            if let Ok(parsed) = serde_json::from_str(&fixed_json) {
                                return Ok(parsed);
                            } // Continue to next approach if this fails
                        } else {
                            {} // Continue to next approach if this fails
                        }
                    }
                }
            }
        }
    }

    // If no proper code block found, try to find any JSON-like content
    // Look for content that starts with { and ends with }
    if let Some(start_idx) = content.find('{') {
        if let Some(end_idx) = content[start_idx..].rfind('}') {
            let potential_json = &content[start_idx..start_idx + end_idx + 1];

            // Try to parse this as JSON
            match serde_json::from_str(potential_json) {
                Ok(parsed) => return Ok(parsed),
                Err(_) => {
                    // Try to clean up the JSON string and parse again
                    let cleaned_json = potential_json
                        .lines()
                        .map(|line| line.trim())
                        .collect::<Vec<_>>()
                        .join(" ");

                    match serde_json::from_str(&cleaned_json) {
                        Ok(parsed) => return Ok(parsed),
                        Err(_) => {
                            // Try to fix common JSON issues and parse again
                            if let Some(fixed_json) = fix_common_json_issues(&cleaned_json) {
                                if let Ok(parsed) = serde_json::from_str(&fixed_json) {
                                    return Ok(parsed);
                                } // Continue to next approach if this fails
                            } else {
                                {} // Continue to next approach if this fails
                            }
                        }
                    }
                }
            }
        }
    }

    // Try to find the largest JSON-like substring
    if let Some(json_like) = extract_largest_json_substring(content) {
        match serde_json::from_str(&json_like) {
            Ok(parsed) => return Ok(parsed),
            Err(_) => {
                // Try to fix common JSON issues and parse again
                if let Some(fixed_json) = fix_common_json_issues(&json_like) {
                    if let Ok(parsed) = serde_json::from_str(&fixed_json) {
                        return Ok(parsed);
                    } // Continue to next approach if this fails
                }
            }
        }
    }

    // As a last resort, try to parse the entire content as JSON
    match serde_json::from_str(content.trim()) {
        Ok(parsed) => Ok(parsed),
        Err(e) => Err(ExtractJsonError::ParseError(e)),
    }
}

/// Static regex patterns for JSON fixing
static RE_OBJ_COMMA: Lazy<regex::Regex> = Lazy::new(|| {
    regex::Regex::new(r",\s*}\s*").expect("Invalid regex pattern for object trailing comma")
});

static RE_ARR_COMMA: Lazy<regex::Regex> = Lazy::new(|| {
    regex::Regex::new(r",\s*]\s*").expect("Invalid regex pattern for array trailing comma")
});

static RE_UNQUOTED_KEYS: Lazy<regex::Regex> = Lazy::new(|| {
    regex::Regex::new(r"(\{|,)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:")
        .expect("Invalid regex pattern for unquoted keys")
});

/// Attempts to fix common JSON formatting issues
///
/// # Arguments
///
/// * `json_str` - The potentially malformed JSON string
///
/// # Returns
///
/// An Option containing the fixed JSON string or None if unfixable
fn fix_common_json_issues(json_str: &str) -> Option<String> {
    // Fix trailing commas in objects
    let mut fixed = RE_OBJ_COMMA.replace_all(json_str, "}").to_string();

    // Fix trailing commas in arrays
    fixed = RE_ARR_COMMA.replace_all(&fixed, "]").to_string();

    // Fix missing quotes around keys
    fixed = RE_UNQUOTED_KEYS
        .replace_all(&fixed, "$1\"$2\":")
        .to_string();

    // Fix single quotes used instead of double quotes
    let mut in_string = false;
    let mut result = String::new();
    let mut chars = fixed.chars().peekable();

    while let Some(c) = chars.next() {
        match c {
            '\'' => {
                // Replace single quote with double quote
                result.push('"');
            }
            '"' => {
                // Toggle in_string state for proper double quotes
                in_string = !in_string;
                result.push('"');
            }
            '\\' if chars.peek() == Some(&'"') => {
                // Keep escaped double quotes
                result.push('\\');
                result.push(chars.next().unwrap());
            }
            _ => result.push(c),
        }
    }

    // Fix missing commas between objects in arrays
    let re_missing_comma = regex::Regex::new(r"\}\s*\{").ok()?;
    let mut fixed = re_missing_comma.replace_all(&result, "},{").to_string();

    // Fix invalid control characters or escape sequences
    let re_invalid_escapes = regex::Regex::new(r#"\\[^"\\bfnrtu]"#).ok()?;
    fixed = re_invalid_escapes.replace_all(&fixed, "").to_string();

    // Fix unescaped newlines in strings
    let re_newlines = regex::Regex::new(r#""[^"]*\n[^"]*""#).ok()?;
    fixed = re_newlines
        .replace_all(&fixed, |caps: &regex::Captures| {
            caps[0].replace('\n', "\\n")
        })
        .to_string();

    // Fix unescaped quotes in strings
    let mut cleaned = String::new();
    let mut in_string = false;
    let mut escaped = false;

    for c in fixed.chars() {
        match c {
            '"' if !escaped => {
                in_string = !in_string;
                cleaned.push('"');
            }
            '\\' if in_string => {
                escaped = !escaped;
                cleaned.push('\\');
            }
            '"' if escaped => {
                escaped = false;
                cleaned.push('"');
            }
            _ => {
                if escaped && in_string {
                    escaped = false;
                    // Only keep valid escape sequences
                    if matches!(c, 'b' | 'f' | 'n' | 'r' | 't' | 'u' | '\\' | '"') {
                        cleaned.push(c);
                    }
                } else {
                    escaped = false;
                    cleaned.push(c);
                }
            }
        }
    }

    // Remove any non-JSON characters that might be causing issues
    let re_non_json_chars = regex::Regex::new(r"[\x00-\x08\x0B\x0C\x0E-\x1F]").ok()?;
    let cleaned = re_non_json_chars.replace_all(&cleaned, "").to_string();

    Some(cleaned)
}

/// Extracts the largest substring that looks like valid JSON
///
/// # Arguments
///
/// * `content` - The string to search for JSON-like content
///
/// # Returns
///
/// An Option containing the largest JSON-like substring or None if not found
fn extract_largest_json_substring(content: &str) -> Option<String> {
    let mut best_candidate = None;
    let mut best_length = 0;

    // Find all potential JSON objects (starting with { and ending with })
    let mut start_indices = Vec::new();
    for (i, c) in content.char_indices() {
        if c == '{' {
            start_indices.push(i);
        }
    }

    for start_idx in start_indices {
        let mut brace_count = 0;
        let mut in_string = false;
        let mut end_idx = start_idx;

        for (i, c) in content[start_idx..].char_indices() {
            let pos = start_idx + i;
            match c {
                '{' if !in_string => brace_count += 1,
                '}' if !in_string => {
                    brace_count -= 1;
                    if brace_count == 0 {
                        end_idx = pos + 1; // +1 to include the closing brace
                        break;
                    }
                }
                '"' => {
                    // Check if the quote is escaped
                    let is_escaped = pos > 0 && content.chars().nth(pos - 1) == Some('\\');
                    if !is_escaped {
                        in_string = !in_string;
                    }
                }
                _ => {}
            }
        }

        // If we found a complete JSON object and it's longer than our best candidate
        if brace_count == 0 && end_idx > start_idx {
            let length = end_idx - start_idx;
            if length > best_length {
                best_length = length;
                best_candidate = Some(content[start_idx..end_idx].to_string());
            }
        }
    }

    best_candidate
}

/// Extracts JSON content from markdown code blocks without parsing
///
/// If the content contains a JSON code block (```json ... ```), this function
/// will extract and return the JSON content without the markdown markers.
/// If no JSON code block is found, it returns the original content.
///
/// # Arguments
pub fn extract_json_string_from_markdown(content: &str) -> Option<String> {
    // Common JSON code block markers with more variations
    const JSON_MARKERS: [&str; 4] = ["```json", "```JSON", "```js", "```javascript"];
    const CODE_MARKERS: [&str; 3] = ["```", "~~~", "'''"];

    // First try to find a proper JSON code block
    for start_marker in &JSON_MARKERS {
        if let Some(start_idx) = content.find(start_marker) {
            let json_start = start_idx + start_marker.len();

            // Find the closing marker
            for end_marker in &CODE_MARKERS {
                if let Some(end_idx) = content[json_start..].find(end_marker) {
                    let json_str = content[json_start..json_start + end_idx].trim();

                    // Try to parse the JSON
                    if let Ok(parsed) = serde_json::from_str(json_str) {
                        return Some(parsed);
                    }
                }
            }
        }
    }

    // Try with any code block marker (not just JSON specific)
    for code_marker in &CODE_MARKERS {
        if let Some(start_idx) = content.find(code_marker) {
            let potential_start = start_idx + code_marker.len();

            // Find the closing marker
            if let Some(end_idx) = content[potential_start..].find(code_marker) {
                let potential_json = content[potential_start..potential_start + end_idx].trim();

                // Try to parse this as JSON
                if let Ok(parsed) = serde_json::from_str(potential_json) {
                    return Some(parsed);
                }
            }
        }
    }

    // If no proper code block found, try to find any JSON-like content
    if let Some(start_idx) = content.find('{') {
        if let Some(end_idx) = content[start_idx..].rfind('}') {
            let potential_json = &content[start_idx..start_idx + end_idx + 1];

            // Try to parse this as JSON
            if let Ok(parsed) = serde_json::from_str(potential_json) {
                return Some(parsed);
            } else {
                // Try to clean up the JSON string and parse again
                let cleaned_json = potential_json
                    .lines()
                    .map(|line| line.trim())
                    .collect::<Vec<_>>()
                    .join(" ");

                if let Ok(parsed) = serde_json::from_str(&cleaned_json) {
                    return Some(parsed);
                }
            }
        }
    }

    // As a last resort, try to parse the entire content as JSON
    serde_json::from_str(content.trim()).ok()
}

/// Attempts to extract and parse JSON from markdown content with error handling
///
/// Similar to extract_json_from_markdown but returns a Result instead of panicking
/// on failure. This is useful when you want to handle the error case explicitly.
///
/// # Arguments
///
/// * `content` - The string that may contain markdown with JSON code blocks
///
/// # Returns
///
/// A Result containing the parsed JSON or an ExtractJsonError
pub fn try_extract_json_from_markdown<T: DeserializeOwned>(
    content: &str,
) -> Result<T, ExtractJsonError> {
    // Common JSON code block markers with more variations
    const JSON_MARKERS: [&str; 6] = [
        "```json",
        "```JSON",
        "```js",
        "```javascript",
        "```typescript",
        "```ts",
    ];
    const CODE_MARKERS: [&str; 4] = ["```", "~~~", "'''", "```\n"];

    // First try to find a proper JSON code block
    for start_marker in &JSON_MARKERS {
        if let Some(start_idx) = content.find(start_marker) {
            let json_start = start_idx + start_marker.len();

            // Find the closing marker
            for end_marker in &CODE_MARKERS {
                if let Some(end_idx) = content[json_start..].find(end_marker) {
                    let json_str = content[json_start..json_start + end_idx].trim();

                    // Try to parse the JSON
                    match serde_json::from_str(json_str) {
                        Ok(parsed) => return Ok(parsed),
                        Err(_) => {
                            // Try to fix common JSON issues and parse again
                            if let Some(fixed_json) = fix_common_json_issues(json_str) {
                                if let Ok(parsed) = serde_json::from_str(&fixed_json) {
                                    return Ok(parsed);
                                } // Continue to next approach if this fails
                            } else {
                                continue; // Try next end marker if parsing fails
                            }
                        }
                    }
                }
            }
        }
    }

    // Try with any code block marker (not just JSON specific)
    for code_marker in &CODE_MARKERS {
        if let Some(start_idx) = content.find(code_marker) {
            let potential_start = start_idx + code_marker.len();

            // Find the closing marker
            if let Some(end_idx) = content[potential_start..].find(code_marker) {
                let potential_json = content[potential_start..potential_start + end_idx].trim();

                // Try to parse this as JSON
                match serde_json::from_str(potential_json) {
                    Ok(parsed) => return Ok(parsed),
                    Err(_) => {
                        // Try to fix common JSON issues and parse again
                        if let Some(fixed_json) = fix_common_json_issues(potential_json) {
                            if let Ok(parsed) = serde_json::from_str(&fixed_json) {
                                return Ok(parsed);
                            } // Continue to next approach if this fails
                        }
                    }
                }
            }
        }
    }

    // If no proper code block found, try to find any JSON-like content
    // Look for content that starts with { and ends with }
    if let Some(start_idx) = content.find('{') {
        if let Some(end_idx) = content[start_idx..].rfind('}') {
            let potential_json = &content[start_idx..start_idx + end_idx + 1];

            // Try to parse this as JSON
            match serde_json::from_str(potential_json) {
                Ok(parsed) => return Ok(parsed),
                Err(_) => {
                    // Try to clean up the JSON string and parse again
                    let cleaned_json = potential_json
                        .lines()
                        .map(|line| line.trim())
                        .collect::<Vec<_>>()
                        .join(" ");

                    match serde_json::from_str(&cleaned_json) {
                        Ok(parsed) => return Ok(parsed),
                        Err(_) => {
                            // Try to fix common JSON issues and parse again
                            if let Some(fixed_json) = fix_common_json_issues(&cleaned_json) {
                                if let Ok(parsed) = serde_json::from_str(&fixed_json) {
                                    return Ok(parsed);
                                } // Continue to next approach if this fails
                            }
                        }
                    }
                }
            }
        }
    }

    // Try to find the largest JSON-like substring
    if let Some(json_like) = extract_largest_json_substring(content) {
        match serde_json::from_str(&json_like) {
            Ok(parsed) => return Ok(parsed),
            Err(_) => {
                // Try to fix common JSON issues and parse again
                if let Some(fixed_json) = fix_common_json_issues(&json_like) {
                    if let Ok(parsed) = serde_json::from_str(&fixed_json) {
                        return Ok(parsed);
                    } // Continue to next approach if this fails
                }
            }
        }
    }

    // As a last resort, try to parse the entire content as JSON
    match serde_json::from_str(content.trim()) {
        Ok(parsed) => Ok(parsed),
        Err(e) => Err(ExtractJsonError::ParseError(e)),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde::Deserialize;

    #[derive(Deserialize, Debug, PartialEq)]
    struct TestJson {
        key: String,
    }

    #[derive(Deserialize, Debug, PartialEq)]
    struct ComplexTestJson {
        summary: String,
        response_map: std::collections::HashMap<String, ResponseItem>,
    }

    #[derive(Deserialize, Debug, PartialEq)]
    struct ResponseItem {
        status: String,
        justification: String,
        suggestions: Vec<String>,
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
    fn test_extract_json_with_uppercase_markers() {
        let markdown = r#"Some text before
```JSON
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
    fn test_extract_json_with_alternative_markers() {
        let markdown = r#"Some text before
```json
{
  "key": "value"
}
~~~
Some text after"#;

        let expected = TestJson {
            key: "value".to_string(),
        };
        let result = extract_json_from_markdown::<TestJson>(markdown).unwrap();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_extract_json_without_markers() {
        let content = r#"{
  "key": "value"
}"#;

        let expected = TestJson {
            key: "value".to_string(),
        };
        let result = extract_json_from_markdown::<TestJson>(content).unwrap();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_extract_complex_json() {
        let content = r#"{
  "summary": "Test summary",
  "response_map": {
    "test_criterion": {
      "status": "pass",
      "justification": "Test passed",
      "suggestions": ["Suggestion 1", "Suggestion 2"]
    }
  }
}"#;

        let mut response_map = std::collections::HashMap::new();
        response_map.insert(
            "test_criterion".to_string(),
            ResponseItem {
                status: "pass".to_string(),
                justification: "Test passed".to_string(),
                suggestions: vec!["Suggestion 1".to_string(), "Suggestion 2".to_string()],
            },
        );

        let expected = ComplexTestJson {
            summary: "Test summary".to_string(),
            response_map,
        };

        let result = extract_json_from_markdown::<ComplexTestJson>(content).unwrap();
        assert_eq!(result, expected);
    }

    #[test]
    fn test_extract_json_with_surrounding_text() {
        let content = r#"I've analyzed the proposal and here's my evaluation:

{
  "key": "value"
}

I hope this helps!"#;

        let expected = TestJson {
            key: "value".to_string(),
        };
        let result = extract_json_from_markdown::<TestJson>(content).unwrap();
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

        assert_eq!(extract_json_string_from_markdown(markdown), Some(expected.to_string()));
    }

    #[test]
    fn test_extract_json_string_without_markers() {
        let content = r#"{"key": "value"}"#;
        assert_eq!(extract_json_string_from_markdown(content), Some(content.to_string()));
    }

    #[test]
    fn test_extract_json_string_with_start_marker_only() {
        let markdown = r#"```json
{
  "key": "value"
}"#;

        assert_eq!(extract_json_string_from_markdown(markdown), Some(markdown.to_string()));
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

    #[test]
    fn test_try_extract_json_from_markdown_no_markers() {
        let content = r#"{
  "key": "value"
}"#;

        let expected = TestJson {
            key: "value".to_string(),
        };
        let result = try_extract_json_from_markdown::<TestJson>(content).unwrap();
        assert_eq!(result, expected);
    }
}
