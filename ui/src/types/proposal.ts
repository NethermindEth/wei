// Proposal model for analysis - only includes description as requested
export interface Proposal {
  description: string;
}

// Arguments for and against a proposal
export interface ProposalArguments {
  for_proposal: string[];
  against: string[];
}

// Analysis response from the backend
export interface AnalysisResponse {
  id?: string;
  title?: string;
  description?: string;
  protocol_id?: string;
  author?: string;
  goals_and_motivation: {
    status: 'pass' | 'fail' | 'n/a';
    justification: string;
    suggestions: string[];
  };
  measurable_outcomes: {
    status: 'pass' | 'fail' | 'n/a';
    justification: string;
    suggestions: string[];
  };
  budget: {
    status: 'pass' | 'fail' | 'n/a';
    justification: string;
    suggestions: string[];
  };
  technical_specifications: {
    status: 'pass' | 'fail' | 'n/a';
    justification: string;
    suggestions: string[];
  };
  language_quality: {
    status: 'pass' | 'fail' | 'n/a';
    justification: string;
    suggestions: string[];
  };
  // Arguments for and against the proposal
  arguments?: ProposalArguments;
  // Cache metadata
  from_cache: boolean;
  cache_key: string;
}

// Local analysis result for fallback
export interface LocalAnalysisResult {
  summary: string;
  risks: string[];
  score: number; // 0..100
}
