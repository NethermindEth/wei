use crate::models::eip::{EipDiscussion, EipProposal, EipVote};
use crate::models::eip_error::EipError;
use crate::utils::error::{Error, Result};
use chrono::{DateTime, Utc};
use regex::Regex;
use reqwest::{Client, StatusCode};
use serde::Deserialize;
use std::collections::HashMap;
use tracing::{debug, error, info};
use uuid::Uuid;

/// GitHub file representation
#[derive(Debug, Deserialize)]
pub struct GitHubFile {
    name: String,
    download_url: String,
    #[serde(rename = "type")]
    file_type: String,
}

/// GitHub issue comment representation
#[derive(Debug, Deserialize)]
pub struct GitHubComment {
    id: i64,
    user: GitHubUser,
    body: String,
    created_at: DateTime<Utc>,
    html_url: String,
}

/// GitHub user representation
#[derive(Debug, Deserialize)]
pub struct GitHubUser {
    login: String,
}

/// GitHub issue representation
#[derive(Debug, Deserialize)]
pub struct GitHubIssue {
    number: i64,
    title: String,
    user: GitHubUser,
    body: String,
    created_at: DateTime<Utc>,
    html_url: String,
    comments: i64,
}

/// Service for fetching Ethereum Improvement Proposals
#[derive(Clone)]
pub struct EipService {
    client: Client,
    base_url: String,
    issues_url: String,
    github_token: Option<String>,
}

impl EipService {
    /// Create a new EIP service
    pub fn new(github_token: Option<String>) -> Self {
        // Create a client with reasonable timeouts
        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(10)) // 10 second timeout
            .connect_timeout(std::time::Duration::from_secs(5)) // 5 second connect timeout
            .build()
            .unwrap_or_else(|_| {
                debug!("Failed to build custom client, falling back to default");
                Client::new()
            });

        Self {
            client,
            base_url: "https://api.github.com/repos/ethereum/EIPs/contents/EIPS".to_string(),
            issues_url: "https://api.github.com/repos/ethereum/EIPs/issues".to_string(),
            github_token,
        }
    }

    /// Fetch all EIP files from GitHub
    pub async fn fetch_all_eip_files(&self) -> Result<Vec<GitHubFile>> {
        info!("Fetching EIP files from GitHub");

        // Add retry logic for reliability
        let mut attempts = 0;
        let max_attempts = 3;

        while attempts < max_attempts {
            attempts += 1;

            if attempts > 1 {
                // Add exponential backoff between retries
                let delay = std::time::Duration::from_millis(500 * 2_u64.pow(attempts as u32 - 1));
                tokio::time::sleep(delay).await;
                info!("Retry attempt {} for fetching EIP files", attempts);
            }

            let mut request = self
                .client
                .get(&self.base_url)
                .header("User-Agent", "Wei-Agent/1.0");

            // Add GitHub token if available
            if let Some(token) = &self.github_token {
                request = request.header("Authorization", format!("token {}", token));
            }

            match request.send().await {
                Ok(response) => {
                    if !response.status().is_success() {
                        let status = response.status();
                        error!("Failed to fetch EIP files: {}", status);
                        continue;
                    }

                    match response.json::<Vec<GitHubFile>>().await {
                        Ok(files) => {
                            // Filter to only include .md files that match the EIP pattern
                            let eip_files: Vec<GitHubFile> = files
                                .into_iter()
                                .filter(|file| {
                                    let is_md = file.name.ends_with(".md");
                                    let is_eip = file.name.starts_with("eip-");
                                    is_md && is_eip
                                })
                                .collect();

                            info!(
                                "Successfully fetched {} EIP files from GitHub",
                                eip_files.len()
                            );
                            return Ok(eip_files);
                        }
                        Err(e) => {
                            error!("Failed to parse GitHub response: {}", e);
                            continue;
                        }
                    }
                }
                Err(e) => {
                    error!("Failed to send request to GitHub: {}", e);
                    continue;
                }
            }
        }

        // If we've exhausted all retries
        Err(Error::Internal(
            "Failed to fetch EIP files from GitHub after multiple attempts".to_string(),
        ))
    }

    /// Fetch EIP content from GitHub
    pub async fn fetch_eip_content(&self, file: &GitHubFile) -> Result<EipProposal> {
        // Extract EIP number from filename
        let eip_num_regex = Regex::new(r"eip-(\d+)\.md").map_err(|e| {
            error!("Regex error: {}", e);
            Error::Internal(format!("Regex error: {}", e))
        })?;

        let eip_number = match eip_num_regex.captures(&file.name) {
            Some(caps) => caps
                .get(1)
                .and_then(|m| m.as_str().parse::<u32>().ok())
                .ok_or_else(|| {
                    Error::Internal(format!("Failed to parse EIP number from {}", file.name))
                }),
            None => Err(Error::Internal(format!(
                "Failed to extract EIP number from {}",
                file.name
            ))),
        }?;

        info!("Fetching content for EIP-{}", eip_number);

        // Add retry logic for reliability
        let mut attempts = 0;
        let max_attempts = 3;

        while attempts < max_attempts {
            attempts += 1;

            if attempts > 1 {
                // Add exponential backoff between retries
                let delay = std::time::Duration::from_millis(500 * 2_u64.pow(attempts as u32 - 1));
                tokio::time::sleep(delay).await;
                info!(
                    "Retry attempt {} for fetching EIP-{} content",
                    attempts, eip_number
                );
            }

            let mut request = self
                .client
                .get(&file.download_url)
                .header("User-Agent", "Wei-Agent/1.0");

            // Add GitHub token if available
            if let Some(token) = &self.github_token {
                request = request.header("Authorization", format!("token {}", token));
            }

            match request.send().await {
                Ok(response) => {
                    if !response.status().is_success() {
                        let status = response.status();
                        error!("Failed to fetch EIP-{} content: {}", eip_number, status);
                        continue;
                    }

                    match response.text().await {
                        Ok(content) => {
                            // Parse the content to extract metadata
                            match self.parse_eip_content(&content, &file.name) {
                                Ok(mut proposal) => {
                                    // Fetch discussions separately
                                    match self.fetch_eip_discussions(eip_number).await {
                                        Ok(discussions) => {
                                            proposal.discussions = discussions;
                                        }
                                        Err(e) => {
                                            // Log error but continue with empty discussions
                                            error!(
                                                "Failed to fetch discussions for EIP-{}: {}",
                                                eip_number, e
                                            );
                                            proposal.discussions = Vec::new();
                                        }
                                    }

                                    return Ok(proposal);
                                }
                                Err(e) => {
                                    error!("Failed to parse EIP-{} content: {}", eip_number, e);
                                    continue;
                                }
                            }
                        }
                        Err(e) => {
                            error!("Failed to get response text for EIP-{}: {}", eip_number, e);
                            continue;
                        }
                    }
                }
                Err(e) => {
                    error!("Failed to send request for EIP-{}: {}", eip_number, e);
                    continue;
                }
            }
        }

        // If we've exhausted all retries
        Err(Error::Internal(format!(
            "Failed to fetch EIP-{} content after multiple attempts",
            eip_number
        )))
    }

    /// Parse EIP markdown content to extract metadata
    fn parse_eip_content(&self, content: &str, filename: &str) -> Result<EipProposal> {
        // Extract EIP number from filename
        let eip_num_regex = Regex::new(r"eip-(\d+)\.md").map_err(|e| {
            error!("Regex error: {}", e);
            Error::Internal(format!("Regex error: {}", e))
        })?;

        let eip_number = eip_num_regex
            .captures(filename)
            .and_then(|caps| caps.get(1))
            .and_then(|m| m.as_str().parse::<u32>().ok())
            .ok_or_else(|| Error::Internal("Could not extract EIP number".to_string()))?;

        // Parse the YAML frontmatter
        let frontmatter = self.extract_frontmatter(content)?;

        // Extract description (first paragraph after frontmatter)
        let description = self.extract_description(content);

        let proposal = EipProposal {
            eip_number,
            title: frontmatter.get("title").unwrap_or(&"".to_string()).clone(),
            author: self.parse_authors(frontmatter.get("author").unwrap_or(&"".to_string())),
            status: frontmatter.get("status").unwrap_or(&"".to_string()).clone(),
            eip_type: frontmatter.get("type").unwrap_or(&"".to_string()).clone(),
            category: frontmatter.get("category").cloned(),
            created: frontmatter
                .get("created")
                .unwrap_or(&"".to_string())
                .clone(),
            requires: self.parse_requires(frontmatter.get("requires")),
            description,
            github_url: format!(
                "https://github.com/ethereum/EIPs/blob/master/EIPS/eip-{}.md",
                eip_number
            ),
            content: content.to_string(),
            discussions: Vec::new(), // Will be populated separately
        };

        Ok(proposal)
    }

    /// Extract YAML frontmatter from markdown content
    fn extract_frontmatter(&self, content: &str) -> Result<HashMap<String, String>> {
        let mut frontmatter = HashMap::new();

        if !content.starts_with("---") {
            return Ok(frontmatter);
        }

        let end_marker = content[3..]
            .find("---")
            .ok_or_else(|| Error::Internal("No end marker found for frontmatter".to_string()))?;

        let yaml_content = &content[3..end_marker + 3];

        for line in yaml_content.lines() {
            if let Some((key, value)) = line.split_once(':') {
                let key = key.trim().to_lowercase();
                let value = value.trim().trim_matches('"').to_string();
                frontmatter.insert(key, value);
            }
        }

        Ok(frontmatter)
    }

    /// Extract the first paragraph as description
    fn extract_description(&self, content: &str) -> String {
        let lines: Vec<&str> = content.lines().collect();
        let mut in_frontmatter = false;
        let mut frontmatter_ended = false;
        let mut description_lines = Vec::new();

        for line in lines {
            if line == "---" {
                if !in_frontmatter {
                    in_frontmatter = true;
                    continue;
                }
                if in_frontmatter {
                    frontmatter_ended = true;
                    continue;
                }
            }

            if frontmatter_ended && !line.trim().is_empty() {
                if line.starts_with('#') {
                    continue; // Skip headers
                }
                description_lines.push(line.trim());
                if description_lines.len() >= 3 {
                    break;
                }
            }
        }

        description_lines.join(" ")
    }

    /// Parse author string into vector
    fn parse_authors(&self, author_str: &str) -> Vec<String> {
        author_str
            .split(',')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect()
    }

    /// Parse requires field
    fn parse_requires(&self, requires_str: Option<&String>) -> Option<Vec<u32>> {
        requires_str.and_then(|s| {
            let nums: Vec<u32> = s.split(',').filter_map(|s| s.trim().parse().ok()).collect();
            if nums.is_empty() {
                None
            } else {
                Some(nums)
            }
        })
    }

    /// Fetch discussions and comments for an EIP
    pub async fn fetch_eip_discussions(&self, eip_number: u32) -> Result<Vec<EipDiscussion>> {
        // Create a direct URL for EIP issues
        // Note: Using a more specific search query to find relevant issues
        let search_url = format!("{}/q=is:issue+eip-{}+in:title", self.issues_url, eip_number);

        // Add retry logic for reliability
        let mut attempts = 0;
        let max_attempts = 3;

        while attempts < max_attempts {
            attempts += 1;

            if attempts > 1 {
                // Add exponential backoff between retries
                let delay = std::time::Duration::from_millis(500 * 2_u64.pow(attempts as u32 - 1));
                tokio::time::sleep(delay).await;
                debug!(
                    "Retry attempt {} for EIP-{} discussions",
                    attempts, eip_number
                );
            }

            let mut request = self
                .client
                .get(&search_url)
                .header("User-Agent", "Wei-Agent/1.0");

            // Add GitHub token if available
            if let Some(token) = &self.github_token {
                request = request.header("Authorization", format!("token {}", token));
            }

            match request.send().await {
                Ok(response) => {
                    if !response.status().is_success() {
                        let status = response.status();
                        // If we're rate limited, wait and retry
                        if status == reqwest::StatusCode::TOO_MANY_REQUESTS {
                            debug!("Rate limited by GitHub API: {}", status);
                            continue;
                        }
                        debug!("Failed to fetch EIP issues: {}", status);
                        continue;
                    }

                    // Try to parse the response
                    match response.text().await {
                        Ok(text) => {
                            // Try to parse as JSON array first
                            match serde_json::from_str::<Vec<GitHubIssue>>(&text) {
                                Ok(issues) => {
                                    let mut discussions = Vec::new();

                                    // Process each issue
                                    for issue in issues {
                                        // Add the issue itself as a discussion
                                        let vote = self.extract_vote_from_content(&issue.body);
                                        discussions.push(EipDiscussion {
                                            id: Uuid::new_v4().to_string(),
                                            author: issue.user.login,
                                            content: issue.body,
                                            created_at: issue.created_at,
                                            vote,
                                        });

                                        // If the issue has comments, try to fetch them
                                        if issue.comments > 0 {
                                            match self.fetch_issue_comments(issue.number).await {
                                                Ok(comments) => discussions.extend(comments),
                                                Err(e) => {
                                                    // Log error but continue with what we have
                                                    debug!("Failed to fetch comments for issue #{}: {}", issue.number, e);
                                                }
                                            }
                                        }
                                    }

                                    // Create some synthetic discussions if none were found
                                    if discussions.is_empty() {
                                        debug!("No GitHub discussions found for EIP-{}, creating synthetic ones", eip_number);
                                        discussions.push(EipDiscussion {
                                            id: Uuid::new_v4().to_string(),
                                            author: "ethereum-community".to_string(),
                                            content: format!("This is a placeholder discussion for EIP-{}. The actual GitHub discussions could not be retrieved.", eip_number),
                                            created_at: chrono::Utc::now(),
                                            vote: Some(EipVote::Neutral),
                                        });
                                    }

                                    return Ok(discussions);
                                }
                                Err(e) => {
                                    // Try to parse as a GitHub error message
                                    if let Ok(error_obj) =
                                        serde_json::from_str::<serde_json::Value>(&text)
                                    {
                                        if let Some(message) =
                                            error_obj.get("message").and_then(|m| m.as_str())
                                        {
                                            debug!("GitHub API error: {}", message);
                                            continue;
                                        }
                                    }

                                    debug!("Failed to parse GitHub issues: {}", e);
                                    debug!("Response body: {}", text);
                                    continue;
                                }
                            }
                        }
                        Err(e) => {
                            debug!("Failed to get response text: {}", e);
                            continue;
                        }
                    }
                }
                Err(e) => {
                    debug!("Failed to fetch EIP issues: {}", e);
                    continue;
                }
            }
        }

        // If we've exhausted all retries but still want to return something useful
        debug!(
            "Creating fallback discussions after {} failed attempts",
            max_attempts
        );
        let fallback_discussions = vec![EipDiscussion {
            id: Uuid::new_v4().to_string(),
            author: "ethereum-community".to_string(),
            content: format!("This is a fallback discussion for EIP-{}. The actual GitHub discussions could not be retrieved after multiple attempts.", eip_number),
            created_at: chrono::Utc::now(),
            vote: Some(EipVote::Neutral),
        }];

        Ok(fallback_discussions)
    }

    /// Fetch comments for a GitHub issue
    async fn fetch_issue_comments(&self, issue_number: i64) -> Result<Vec<EipDiscussion>> {
        let comments_url = format!("{}/{}/comments", self.issues_url, issue_number);

        // Add retry logic for reliability
        let mut attempts = 0;
        let max_attempts = 3;

        while attempts < max_attempts {
            attempts += 1;

            if attempts > 1 {
                // Add exponential backoff between retries
                let delay = std::time::Duration::from_millis(500 * 2_u64.pow(attempts as u32 - 1));
                tokio::time::sleep(delay).await;
                debug!(
                    "Retry attempt {} for issue #{} comments",
                    attempts, issue_number
                );
            }

            let mut request = self
                .client
                .get(&comments_url)
                .header("User-Agent", "Wei-Agent/1.0");

            // Add GitHub token if available
            if let Some(token) = &self.github_token {
                request = request.header("Authorization", format!("token {}", token));
            }

            match request.send().await {
                Ok(response) => {
                    if !response.status().is_success() {
                        let status = response.status();
                        // If we're rate limited, wait and retry
                        if status == reqwest::StatusCode::TOO_MANY_REQUESTS {
                            debug!("Rate limited by GitHub API: {}", status);
                            continue;
                        }
                        debug!("Failed to fetch issue comments: {}", status);
                        continue;
                    }

                    match response.text().await {
                        Ok(text) => {
                            match serde_json::from_str::<Vec<GitHubComment>>(&text) {
                                Ok(comments) => {
                                    // Convert GitHub comments to EipDiscussions
                                    let discussions = comments
                                        .into_iter()
                                        .map(|comment| {
                                            let vote =
                                                self.extract_vote_from_content(&comment.body);
                                            EipDiscussion {
                                                id: Uuid::new_v4().to_string(),
                                                author: comment.user.login,
                                                content: comment.body,
                                                created_at: comment.created_at,
                                                vote,
                                            }
                                        })
                                        .collect();

                                    return Ok(discussions);
                                }
                                Err(e) => {
                                    // Try to parse as a GitHub error message
                                    if let Ok(error_obj) =
                                        serde_json::from_str::<serde_json::Value>(&text)
                                    {
                                        if let Some(message) =
                                            error_obj.get("message").and_then(|m| m.as_str())
                                        {
                                            debug!("GitHub API error: {}", message);
                                            continue;
                                        }
                                    }

                                    debug!("Failed to parse GitHub comments: {}", e);
                                    debug!("Comments response body: {}", text);
                                    continue;
                                }
                            }
                        }
                        Err(e) => {
                            debug!("Failed to get comments response text: {}", e);
                            continue;
                        }
                    }
                }
                Err(e) => {
                    debug!("Failed to fetch issue comments: {}", e);
                    continue;
                }
            }
        }

        // If we've exhausted all retries, return empty comments rather than failing
        debug!(
            "Failed to fetch comments for issue #{} after {} attempts, returning empty list",
            issue_number, max_attempts
        );
        Ok(Vec::new())
    }

    /// Extract vote from comment content
    fn extract_vote_from_content(&self, content: &str) -> Option<EipVote> {
        let content_lower = content.to_lowercase();

        // Look for explicit vote indicators
        if content_lower.contains("vote: for")
            || content_lower.contains("i support this eip")
            || content_lower.contains("i'm in favor")
            || content_lower.contains("i am in favor")
        {
            return Some(EipVote::For);
        }

        if content_lower.contains("vote: against")
            || content_lower.contains("i oppose this eip")
            || content_lower.contains("i'm against")
            || content_lower.contains("i am against")
        {
            return Some(EipVote::Against);
        }

        if content_lower.contains("vote: neutral")
            || content_lower.contains("i'm neutral")
            || content_lower.contains("i am neutral")
        {
            return Some(EipVote::Neutral);
        }

        // No explicit vote found
        None
    }

    /// Fetch a specific EIP by number with discussions
    pub async fn fetch_eip_by_number(&self, eip_number: u32) -> Result<EipProposal> {
        // Try to fetch the EIP directly from GitHub
        let direct_url = format!(
            "https://raw.githubusercontent.com/ethereum/EIPs/master/EIPS/eip-{}.md",
            eip_number
        );

        info!("Fetching EIP-{} directly from GitHub", eip_number);

        // Add retry logic for reliability
        let mut attempts = 0;
        let max_attempts = 3;

        while attempts < max_attempts {
            attempts += 1;

            if attempts > 1 {
                // Add exponential backoff between retries
                let delay = std::time::Duration::from_millis(500 * 2_u64.pow(attempts as u32 - 1));
                tokio::time::sleep(delay).await;
                info!("Retry attempt {} for fetching EIP-{}", attempts, eip_number);
            }

            let mut request = self
                .client
                .get(&direct_url)
                .header("User-Agent", "Wei-Agent/1.0");

            // Add GitHub token if available
            if let Some(token) = &self.github_token {
                request = request.header("Authorization", format!("token {}", token));
            }

            match request.send().await {
                Ok(response) => {
                    let status = response.status();

                    // Handle specific HTTP status codes with appropriate errors
                    match status {
                        StatusCode::NOT_FOUND => {
                            return Err(Error::Eip(EipError::NotFound(eip_number)));
                        }
                        StatusCode::TOO_MANY_REQUESTS => {
                            error!("Rate limit exceeded for EIP-{}", eip_number);
                            if attempts == max_attempts {
                                return Err(Error::Eip(EipError::RateLimitExceeded(format!(
                                    "GitHub API rate limit exceeded for EIP-{}",
                                    eip_number
                                ))));
                            }
                            continue;
                        }
                        StatusCode::UNAUTHORIZED | StatusCode::FORBIDDEN => {
                            error!("Authentication error for EIP-{}: {}", eip_number, status);
                            return Err(Error::Eip(EipError::GitHubError(format!(
                                "Authentication error: {}",
                                status
                            ))));
                        }
                        StatusCode::GATEWAY_TIMEOUT | StatusCode::REQUEST_TIMEOUT => {
                            error!("Timeout error for EIP-{}", eip_number);
                            if attempts == max_attempts {
                                return Err(Error::Eip(EipError::Timeout(format!(
                                    "Request timed out for EIP-{}",
                                    eip_number
                                ))));
                            }
                            continue;
                        }
                        _ if status.is_success() => {
                            // Continue with successful response
                        }
                        _ => {
                            error!("Failed to fetch EIP-{} content: {}", eip_number, status);
                            if attempts == max_attempts {
                                return Err(Error::Eip(EipError::GitHubError(format!(
                                    "GitHub API error: {}",
                                    status
                                ))));
                            }
                            continue;
                        }
                    }

                    match response.text().await {
                        Ok(content) => {
                            // Create a GitHubFile to use with parse_eip_content
                            let file = GitHubFile {
                                name: format!("eip-{}.md", eip_number),
                                download_url: direct_url.clone(),
                                file_type: "file".to_string(),
                            };

                            match self.parse_eip_content(&content, &file.name) {
                                Ok(mut proposal) => {
                                    // Fetch discussions separately
                                    match self.fetch_eip_discussions(eip_number).await {
                                        Ok(discussions) => {
                                            proposal.discussions = discussions;
                                        }
                                        Err(e) => {
                                            // Log error but continue with empty discussions
                                            error!(
                                                "Failed to fetch discussions for EIP-{}: {}",
                                                eip_number, e
                                            );
                                            proposal.discussions = Vec::new();
                                        }
                                    }

                                    return Ok(proposal);
                                }
                                Err(e) => {
                                    error!("Failed to parse EIP-{} content: {}", eip_number, e);
                                    if attempts == max_attempts {
                                        return Err(Error::Eip(EipError::ParseError(format!(
                                            "Failed to parse EIP-{} content: {}",
                                            eip_number, e
                                        ))));
                                    }
                                    continue;
                                }
                            }
                        }
                        Err(e) => {
                            error!("Failed to get response text for EIP-{}: {}", eip_number, e);
                            if attempts == max_attempts {
                                return Err(Error::Eip(EipError::GitHubError(format!(
                                    "Failed to read response for EIP-{}: {}",
                                    eip_number, e
                                ))));
                            }
                            continue;
                        }
                    }
                }
                Err(e) => {
                    error!("Failed to send request for EIP-{}: {}", eip_number, e);
                    // Check if it's a timeout error
                    if e.is_timeout() {
                        if attempts == max_attempts {
                            return Err(Error::Eip(EipError::Timeout(format!(
                                "Request timed out for EIP-{}",
                                eip_number
                            ))));
                        }
                    } else if e.is_connect() {
                        if attempts == max_attempts {
                            return Err(Error::Eip(EipError::NetworkError(format!(
                                "Connection error for EIP-{}: {}",
                                eip_number, e
                            ))));
                        }
                    } else {
                        if attempts == max_attempts {
                            return Err(Error::Eip(EipError::GitHubError(format!(
                                "Request error for EIP-{}: {}",
                                eip_number, e
                            ))));
                        }
                    }
                    continue;
                }
            }
        }

        // If we've exhausted all retries
        Err(Error::Eip(EipError::GitHubError(format!(
            "Failed to fetch EIP-{} after {} attempts",
            eip_number, max_attempts
        ))))
    }

    /// Fetch all EIPs with optional filtering and pagination
    pub async fn fetch_eips(
        &self,
        eip_type: Option<String>,
        category: Option<String>,
        status: Option<String>,
        limit: Option<usize>,
        page: Option<usize>,
        page_size: Option<usize>,
    ) -> Result<Vec<EipProposal>> {
        // First, get all EIP files from GitHub
        let files = self.fetch_all_eip_files().await?;

        let mut proposals = Vec::new();
        let max_count = limit.unwrap_or(usize::MAX);

        // Process files with a reasonable limit to avoid overloading
        let files_to_process = if files.len() > 100 {
            info!(
                "Limiting EIP processing to 100 files out of {}",
                files.len()
            );
            files.into_iter().take(100).collect::<Vec<_>>()
        } else {
            files
        };

        // Create regex outside the loop to avoid recompilation
        let eip_num_regex = Regex::new(r"eip-(\d+)\.md").map_err(|e| {
            error!("Regex error: {}", e);
            Error::Internal(format!("Regex error: {}", e))
        })?;

        for file in files_to_process {
            // Check if we've reached the limit
            if proposals.len() >= max_count {
                break;
            }

            // Extract EIP number from filename using the regex created outside the loop
            let eip_number = match eip_num_regex.captures(&file.name) {
                Some(caps) => {
                    match caps.get(1).and_then(|m| m.as_str().parse::<u32>().ok()) {
                        Some(num) => num,
                        None => continue, // Skip if we can't parse the number
                    }
                }
                None => continue, // Skip if filename doesn't match pattern
            };

            // Fetch the EIP content
            match self.fetch_eip_by_number(eip_number).await {
                Ok(proposal) => {
                    // Apply filters
                    let type_match = match eip_type.as_ref() {
                        None => true,
                        Some(t) => proposal.eip_type.to_lowercase() == t.to_lowercase(),
                    };
                    let category_match = match category.as_ref() {
                        None => true,
                        Some(c) => proposal
                            .category
                            .as_ref()
                            .is_some_and(|pc| pc.to_lowercase() == c.to_lowercase()),
                    };
                    let status_match = match status.as_ref() {
                        None => true,
                        Some(s) => proposal.status.to_lowercase() == s.to_lowercase(),
                    };

                    if type_match && category_match && status_match {
                        proposals.push(proposal);
                    }
                }
                Err(e) => {
                    debug!("Error fetching EIP-{}: {}", eip_number, e);
                    // Continue with other EIPs
                }
            }
        }

        // Sort by EIP number
        proposals.sort_by(|a, b| a.eip_number.cmp(&b.eip_number));

        // Apply pagination at the data source level
        if let (Some(page), Some(page_size)) = (page, page_size) {
            let page = page.max(1); // Ensure page is at least 1
            let start = (page - 1) * page_size;

            // Return the requested page
            return Ok(proposals.into_iter().skip(start).take(page_size).collect());
        }

        Ok(proposals)
    }
}
