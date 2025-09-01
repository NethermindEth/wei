use crate::models::custom_evaluation::CustomEvaluationRequest;

/// Generate a custom evaluation prompt based on the user's custom criteria
pub fn generate_custom_evaluation_prompt(request: &CustomEvaluationRequest) -> String {
    // Create a prompt that uses the proposal content and focuses on the user's custom criteria
    let mut custom_prompt = String::new();

    // Add the proposal content to be evaluated
    custom_prompt.push_str("Here is the proposal to evaluate:\n\n");
    custom_prompt.push_str(&request.content);
    custom_prompt.push_str("\n\n");

    // Add the user's custom evaluation criteria
    custom_prompt.push_str("The user has provided the following custom evaluation criteria:\n");
    custom_prompt.push_str(&request.custom_criteria);
    custom_prompt.push_str("\n\n");

    // Instructions for evaluation based on custom criteria
    custom_prompt.push_str("You are an expert governance analyst. Please evaluate this proposal focusing ONLY on the user's custom criteria above. ");
    custom_prompt.push_str("Ignore any standard evaluation criteria and focus exclusively on what the user has asked for. ");
    custom_prompt
        .push_str("Your evaluation should directly address the user's specific request.\n\n");

    // Request for output format - must match the expected response structure
    custom_prompt.push_str(
        "Your response MUST be in the following JSON format to be compatible with the backend:\n\n",
    );
    custom_prompt.push_str("```json\n{\n");
    custom_prompt.push_str("  \"summary\": \"A brief summary of the overall evaluation based on the user's criteria\",\n");
    custom_prompt.push_str("  \"response_map\": {\n");
    custom_prompt.push_str("    \"criterion_name_1\": {\n");
    custom_prompt.push_str("      \"status\": \"pass\",\n");
    custom_prompt.push_str("      \"justification\": \"Detailed explanation of why this criterion passed or failed\",\n");
    custom_prompt.push_str("      \"suggestions\": [\"Suggestion 1\", \"Suggestion 2\"]\n");
    custom_prompt.push_str("    },\n");
    custom_prompt.push_str("    \"criterion_name_2\": {\n");
    custom_prompt.push_str("      \"status\": \"fail\",\n");
    custom_prompt.push_str(
        "      \"justification\": \"Detailed explanation of why this criterion failed\",\n",
    );
    custom_prompt.push_str("      \"suggestions\": [\"Suggestion 1\", \"Suggestion 2\"]\n");
    custom_prompt.push_str("    }\n");
    custom_prompt.push_str("  }\n");
    custom_prompt.push_str("}\n```\n\n");
    custom_prompt.push_str("IMPORTANT: You MUST use this exact structure with 'summary' and 'response_map' fields.\n\n");
    custom_prompt.push_str("For each criterion in the response_map:\n");
    custom_prompt.push_str("1. Create a key based on the user's criteria (use snake_case)\n");
    custom_prompt.push_str("2. Each value must be an object with 'status', 'justification', and 'suggestions' fields\n");
    custom_prompt.push_str("3. Status must be one of: 'pass', 'fail', or 'n/a'\n\n");

    // Emphasize focusing on user's criteria and JSON format
    custom_prompt.push_str(
        "IMPORTANT: Your entire evaluation should be based solely on the user's custom criteria. ",
    );
    custom_prompt.push_str("For example, if they want to focus on budget justification, your analysis should primarily address budget aspects. ");
    custom_prompt.push_str("If they want to check for clear milestones, focus your evaluation on identifying and assessing milestones in the proposal.\n\n");

    // Add strict JSON formatting rules
    custom_prompt.push_str("CRITICAL JSON FORMATTING RULES:\n");
    custom_prompt.push_str(
        "1. Your response MUST be valid JSON that can be parsed by standard JSON parsers\n",
    );
    custom_prompt.push_str("2. Do not include any text outside of the JSON structure\n");
    custom_prompt
        .push_str("3. Do not include the ```json and ``` markers in your actual response\n");
    custom_prompt
        .push_str("4. Ensure all JSON keys and values are properly quoted with double quotes\n");
    custom_prompt.push_str(
        "5. Arrays must be properly formatted with square brackets and comma-separated values\n",
    );
    custom_prompt.push_str("6. Do not use trailing commas in arrays or objects\n");
    custom_prompt.push_str("7. Ensure all special characters are properly escaped in strings\n\n");

    // Add more explicit instructions about valid status values
    custom_prompt.push_str("EXTREMELY IMPORTANT INSTRUCTIONS:\n");
    custom_prompt.push_str("1. The 'status' field for each criterion MUST be one of these exact values: 'pass', 'fail', or 'n/a'\n");
    custom_prompt
        .push_str("2. For 'pass' status: Include a justification explaining why it passed\n");
    custom_prompt.push_str("3. For 'fail' status: Include a justification explaining why it failed and provide helpful suggestions\n");
    custom_prompt
        .push_str("4. For 'n/a' status: Explain why this criterion couldn't be evaluated\n");
    custom_prompt.push_str(
        "5. Create criterion keys in the response_map based on the user's custom criteria\n",
    );
    custom_prompt.push_str("6. Use snake_case for all criterion keys (e.g., 'budget_justification', 'team_experience')\n\n");

    // Add examples of good criterion keys
    custom_prompt.push_str("EXAMPLES OF GOOD CRITERION KEYS (based on different user criteria):\n");
    custom_prompt
        .push_str("- If user asks about budget: use 'budget_analysis' or 'cost_effectiveness'\n");
    custom_prompt
        .push_str("- If user asks about team: use 'team_experience' or 'team_qualifications'\n");
    custom_prompt.push_str(
        "- If user asks about milestones: use 'milestone_clarity' or 'timeline_feasibility'\n",
    );
    custom_prompt.push_str("- If user asks about technical aspects: use 'technical_feasibility' or 'implementation_approach'\n\n");

    custom_prompt.push_str("Remember: Each criterion in the response_map must have the exact fields 'status', 'justification', and 'suggestions'\n\n");

    // Return the complete prompt
    custom_prompt
}
