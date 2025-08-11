// Proposal model for analysis - only includes description as requested
export interface Proposal {
  description: string;
}

// Analysis response from the backend
export interface AnalysisResponse {
  id: string;
  title: string;
  description: string;
  protocol_id: string;
  author: string;
  analysis: string;
}

// Local analysis result for fallback
export interface LocalAnalysisResult {
  summary: string;
  risks: string[];
  score: number; // 0..100
}
