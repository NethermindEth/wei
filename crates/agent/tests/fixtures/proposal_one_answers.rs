use crate::fixtures::proposals_questions::{
    BinaryQuestions, ProposalQuestions, ReasoningQuestions,
};

pub fn get_proposal_one_answers() -> ProposalQuestions {
    ProposalQuestions {
        binary_questions: BinaryQuestions {
            proposal: vec![
                "yes",
                "yes",
                "yes",
                "time-sensitive",
                "yes",
                "no",
                "yes",
                "no",
                "yes",
                "yes",
                "yes",
                "yes",
                "no",
                "yes",
                "no",
                "yes",
                "no",
                "yes",
                "yes",
            ],
        },
        reasoning_questions: ReasoningQuestions {
            proposal: vec![
                "The Hackathon Continuation Program (HCP) is underfunded by $89,980 USD due to token price drops and delays in fund conversion, leaving Phase 2 without sufficient resources.",
                "Authorize the use of leftover funds from the Domain Allocator Season 1 program to: Cover the $89,980 shortfall in the HCP. Decide whether the remaining funds should go back to the DAO Treasury or be allocated to the Treasury Management Committee (TMC).",
                "Leftover funds from Domain Allocator Season 1, which were originally due to be returned to the DAO.",
                "$89,980 USD for the HCP top-up, plus allocation of the remaining ~$200k leftover funds (distribution depends on vote outcome).",
                "HCP projects may fail or migrate to other ecosystems.Loss of momentum in DAO-funded hackathon initiatives. Reduced trust from service providers due to unstable funding.",
                "The shortfall was caused by market conditions (token price drop). The funds were already allocated to ecosystem support (Domain Allocator).The proposal is time-sensitive to avoid project disruption.Establishes a precedent for improved fund management systems.",
                "Projects are waiting for funding to progress, and further delays risk failure or migration to other ecosystems.",
                "Hackathon Continuation Program (DAO-approved).Domain Allocator Season 1 leftover funds.Treasury Management Committee (TMC v1.2 proposal).Coordination with Arbitrum Foundation (AF)",
                "A. Only top-up the HCP → Use $89,980 to fund HCP; send remaining funds back to DAO.B. Yes to both → Fund HCP and allocate leftover funds to TMC.C. Against → No top-up for HCP; all funds returned to DAO.D. Abstain → No preference.",
                "Hackathon Continuation Program (direct funding).Projects participating in HCP (builders).Treasury Management Committee (if option B passes).DAO Treasury (depending on outcome).",
            ],
        },
    }
}
