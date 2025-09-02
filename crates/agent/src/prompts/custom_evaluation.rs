use crate::models::custom_evaluation::CustomEvaluationRequest;

/// Generate a custom evaluation prompt based on the user's custom criteria
pub fn generate_custom_evaluation_prompt(request: &CustomEvaluationRequest) -> String {
    // Create the prompt using format! for consistency
    let custom_prompt = format!(
        "Here is the proposal to evaluate:\n\n\
        {}\n\n\
        The user has provided the following custom evaluation criteria:\n\
        {}\n\n",
        request.content, request.custom_criteria
    );

    // Instructions for evaluation based on custom criteria
    let instructions = "You are an expert governance analyst. Please evaluate this proposal focusing ONLY on the user's custom criteria above. \
        Ignore any standard evaluation criteria and focus exclusively on what the user has asked for. \
        Your evaluation should directly address the user's specific request.\n\n".to_string();

    let custom_prompt = custom_prompt + &instructions;

    // Request for output format - must match the expected response structure
    let output_format = "Your response MUST be in the following JSON format to be compatible with the backend:\n\n\
        ```json\n\
        {\n\
          \"summary\": \"A brief summary of the overall evaluation based on the user's criteria\",\n\
          \"response_map\": {\n\
            \"criterion_name_1\": {\n\
              \"status\": \"pass\",\n\
              \"justification\": \"Detailed explanation of why this criterion passed or failed\",\n\
              \"suggestions\": [\"Suggestion 1\", \"Suggestion 2\"]\n\
            },\n\
            \"criterion_name_2\": {\n\
              \"status\": \"fail\",\n\
              \"justification\": \"Detailed explanation of why this criterion failed\",\n\
              \"suggestions\": [\"Suggestion 1\", \"Suggestion 2\"]\n\
            }\n\
          }\n\
        }\n\
        ```\n\n".to_string();

    let custom_prompt = custom_prompt + &output_format;
    // Instructions for criteria structure
    let criteria_instructions = "IMPORTANT: You MUST use this exact structure with 'summary' and 'response_map' fields.\n\n\
        For each criterion in the response_map:\n\
        1. Create a key based on the user's criteria (use snake_case)\n\
        2. Each value must be an object with 'status', 'justification', and 'suggestions' fields\n\
        3. Status must be one of: 'pass', 'fail', or 'n/a'\n\n".to_string();

    // Emphasize focusing on user's criteria and JSON format
    let focus_instructions = "IMPORTANT: Your entire evaluation should be based solely on the user's custom criteria. \
        For example, if they want to focus on budget justification, your analysis should primarily address budget aspects. \
        If they want to check for clear milestones, focus your evaluation on identifying and assessing milestones in the proposal.\n\n".to_string();

    let custom_prompt = custom_prompt + &criteria_instructions + &focus_instructions;

    // Add strict JSON formatting rules
    let json_rules = "CRITICAL JSON FORMATTING RULES:\n\
        1. Your response MUST be valid JSON that can be parsed by standard JSON parsers\n\
        2. Do not include any text outside of the JSON structure\n\
        3. Do not include the ```json and ``` markers in your actual response\n\
        4. Ensure all JSON keys and values are properly quoted with double quotes\n\
        5. Arrays must be properly formatted with square brackets and comma-separated values\n\
        6. Do not use trailing commas in arrays or objects\n\
        7. Ensure all special characters are properly escaped in strings\n\n".to_string();

    let custom_prompt = custom_prompt + &json_rules;

    // Add more explicit instructions about valid status values
    let important_instructions = "EXTREMELY IMPORTANT INSTRUCTIONS:\n\
        1. The 'status' field for each criterion MUST be one of these exact values: 'pass', 'fail', or 'n/a'\n\
        2. For 'pass' status: Include a justification explaining why it passed\n\
        3. For 'fail' status: Include a justification explaining why it failed and provide helpful suggestions\n\
        4. For 'n/a' status: Explain why this criterion couldn't be evaluated\n\
        5. Create criterion keys in the response_map based on the user's custom criteria\n\
        6. Use snake_case for all criterion keys (e.g., 'budget_justification', 'team_experience')\n\n".to_string();

    let custom_prompt = custom_prompt + &important_instructions;

    // Add examples of good criterion keys
    let examples = "EXAMPLES OF GOOD CRITERION KEYS (based on different user criteria):\n\
        - If user asks about budget: use 'budget_analysis' or 'cost_effectiveness'\n\
        - If user asks about team: use 'team_experience' or 'team_qualifications'\n\
        - If user asks about milestones: use 'milestone_clarity' or 'timeline_feasibility'\n\
        - If user asks about technical aspects: use 'technical_feasibility' or 'implementation_approach'\n\n".to_string();

    // Final reminder
    let reminder = "Remember: Each criterion in the response_map must have the exact fields 'status', 'justification', and 'suggestions'\n\n";

    // Return the complete prompt
    custom_prompt + &examples + reminder
}
