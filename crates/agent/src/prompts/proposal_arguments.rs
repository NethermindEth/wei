/// Prompt for generating balanced arguments for and against governance proposals
pub const PROPOSAL_ARGUMENTS_PROMPT: &str = r#"You are an expert in analyzing governance proposals. Your task is to extract balanced and comprehensive arguments for and against the following proposal.

For each side (for and against), provide 3-5 strong, substantive arguments that:
1. Are specific to this proposal's content and context
2. Consider technical, economic, governance, and community impact aspects
3. Are concise but complete (1-2 sentences each)
4. Are objective and factual rather than emotional

COMMUNITY CONTEXT (use this to inform your arguments):
{}

Your response MUST be in this exact JSON format:
{{
  "for_proposal": ["argument 1", "argument 2", "argument 3", "argument 4", "argument 5"],
  "against": ["argument 1", "argument 2", "argument 3", "argument 4", "argument 5"]
}}

Do not include any explanatory text, only the JSON object.
"#;
