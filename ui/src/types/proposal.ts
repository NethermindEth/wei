// Proposal model for analysis - only includes description as requested
export interface Proposal {
  description: string;
}

// Analysis response from the backend
export interface AnalysisResponse {
  id?: string;
  title?: string;
  description?: string;
  protocol_id?: string;
  author?: string;
  verdict: 'good' | 'bad';
  conclusion: string;
  proposal_quality: {
    clarity_of_goals: string;
    completeness_of_sections: string;
    level_of_detail: string;
    assumptions_made: string[];
    missing_elements: string[];
    community_adaptability: string;
  };
  submitter_intentions: {
    submitter_identity: string;
    inferred_interests: string[];
    social_activity: string[];
    strategic_positioning: string[];
  };
}

// Local analysis result for fallback
export interface LocalAnalysisResult {
  summary: string;
  risks: string[];
  score: number; // 0..100
}
