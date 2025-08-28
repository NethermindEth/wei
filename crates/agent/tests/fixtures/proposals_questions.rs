pub struct ProposalQuestions {
    pub binary_questions: BinaryQuestions,
    pub reasoning_questions: ReasoningQuestions,
}

pub struct BinaryQuestions {
    pub proposal: Vec<&'static str>,
    pub submitter_identity: Vec<&'static str>,
    pub submitter_motivation: Vec<&'static str>,
}

pub struct ReasoningQuestions {
    pub proposal: Vec<&'static str>,
    pub submitter_identity: Vec<&'static str>,
    pub submitter_motivation: Vec<&'static str>,
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
            submitter_identity: vec![
                "Is the proposal submitter identified? (yes/no)",
                "Does the submitter have an official or recognized role in the DAO (e.g., delegate, core contributor, grantee)? (yes/no)",
                "Has the submitter contributed to previous proposals or DAO initiatives? (yes/no)",
                "Is this the submitter's first proposal to the DAO? (yes/no)",
                "Is the submitter affiliated with an organization mentioned in the proposal? (yes/no)",
            ],
            submitter_motivation: vec![
                "Does the proposal describe how the submitter is impacted by the problem being addressed? (yes/no)",
                "Is the submitter asking for compensation or reimbursement? (yes/no)",
                "Does the submitter reference community needs, ecosystem growth, or long-term impact as justification? (yes/no)",
                "Was the proposal updated or improved after community input? (yes/no)",
                "Is the proposer's past performance discussed in the current proposal? (yes/no)",
                "Is there independent verification or endorsement of the submitter's work or claims? (yes/no)",
                "Is the proposal's success dependent on the submitter's execution or leadership? (yes/no)",
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
            submitter_identity: vec![
                "Who is the submitter of this proposal?",
                "What is the submitter's relationship to the DAO (e.g., delegate, core team, external contributor)?",
                "Is the submitter affiliated with any organization or team mentioned in the proposal?",
                "What previous contributions has the submitter made to the DAO or ecosystem?",
                "What responsibilities (if any) does the submitter claim in the implementation of this proposal?",
                "Does the submitter reference any relevant expertise or qualifications?",
                "How visible or active is the submitter in public DAO discussions or governance forums?",
            ],
            submitter_motivation: vec![
                "What is the submitter's stated or implied motivation for this proposal?",
                "How might the submitter or their affiliates benefit if the proposal passes?",
                "Does the submitter explain how the proposal aligns with broader DAO goals?",
                "Has the submitter acknowledged any risks or trade-offs in the proposal?",
                "Did the submitter commit to any follow-up, delivery, or accountability steps?",
                "What tone does the submitter use in the proposal (e.g., neutral, persuasive, defensive)?",
                "How has the submitter responded to questions or feedback from the community, if at all?",
            ],
        },
    }
}