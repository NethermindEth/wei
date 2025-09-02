pub struct ProposalQuestions {
    pub binary_questions: BinaryQuestions,
    pub reasoning_questions: ReasoningQuestions,
}

pub struct BinaryQuestions {
    pub proposal: Vec<&'static str>,
}

pub struct ReasoningQuestions {
    pub proposal: Vec<&'static str>,
}

pub fn get_proposal_questions() -> ProposalQuestions {
    ProposalQuestions {
        binary_questions: BinaryQuestions {
            proposal: vec![
                "Does the proposal involve transferring assets or tokens? (yes/no)",
                "Does the proposal address a funding gap or financial shortfall? (yes/no)",
                "Does the proposal request the use of existing, previously allocated resources? (yes/no)",
                "Is the proposal described as time-sensitive or urgent? (time-sensitive/urgent)",
                "Does the proposal reference previous DAO-approved initiatives or programs? (DAO-approved initiatives/programs)",
                "Does the proposal include any suggested changes to DAO rules or governance processes? (DAO rules/governance processes)",
                "Is the proposal submitted by a party directly affected by its outcome? (yes/no)",
                "Would the proposer or affiliated entities receive funding or benefits if approved? (yes/no)",
                "Does the proposal include a justification for the request (e.g., cause of shortfall, expected outcome)? (yes/no)",
                "Does the proposer explain the risks or consequences of not approving the proposal? (yes/no)",
                "Does the proposal mention compliance, legal constraints, or routing mechanisms? (yes/no)",
                "Does the proposal reference any DAO committee, working group, or delegate authority? (yes/no)",
                "Is the proposal requesting additional funding beyond what was previously allocated? (yes/no)",
                "Does the proposal specify a clear financial ask? (yes/no)",
                "Does the proposal specify a team? (yes/no)",
                "Does the proposal specify a budget breakdown of expenditures, if the proposal is asking for funding (yes/no)",
                "Does the proposal specify clear success metrics (yes/no)",
                "Does the proposal indicate future work or unlocks after the proposal is completed (yes/no)",
                "Does the proposal relate to building a community (yes/no)",
            ],
        },
        reasoning_questions: ReasoningQuestions {
            proposal: vec![
                "What is the main problem the proposal is solving?",
                "What is the main action or decision the proposal is requesting?",
                "What is the source of the funds or resources being proposed for use?",
                "What is the total amount involved in the proposal (if any)?",
                "What are the consequences if the proposal is not approved?",
                "What is the rationale provided to justify this proposal?",
                "How urgent is the proposal according to the submitter, and why?",
                "What past events or decisions does this proposal reference or build on?",
                "What are the voting options and what does each one mean?",
                "What part of the DAO or ecosystem will be affected by this proposal?",
            ],
        },
    }
}
